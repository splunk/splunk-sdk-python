
import sys
import os
import csv
import atexit
from typing import Any, Dict, Union
from logging import LoggerAdapter
from .internals import CsvDialect
from .monitor_fs import create_file_monitor, PollingFileMonitor, LinuxInotifyMonitor

class DispatchMonitor:
    """ Monitor the dispatch directory for file creations and update the job state 
    based on the created files. Prevents the need to repeatedly poll the job. """
    def __init__(self, search_command_instance):
        self.command = search_command_instance
        self.logger = LoggerAdapter(search_command_instance.logger, {'component': 'DispatchMonitor'})
        self.dispatch_dir: str = search_command_instance.metadata.searchinfo.dispatch_dir

        self.fs_monitor: Union[LinuxInotifyMonitor, PollingFileMonitor] = \
                create_file_monitor(
                    self.dispatch_dir,
                    self.on_create,
                    False
                )
        self._atexit_registered = False

    def on_create(self, filepath):
        """ Handle file creation events in the dispatch directory """
        filename = os.path.basename(filepath)
        self.logger.debug(f"File created in dispatch directory: {filename}")

        # Handle creation of the finalize file
        if filename == 'finalize':
            self.logger.warning(f"Finalize file created; stopping search: {filepath}")
            self.command._finalizing = True

        # Handle status.csv file creation
        elif filename == 'status.csv':
            self.logger.debug(f"Status file created: {filepath}")

            # Process the status.csv file
            self.command.status = read_csv_to_dict(filepath)
            print("Updated job status:", self.command.status, file=sys.stderr)

            # TODO: Do something with this output data
            # Read the status string from the updated job state (status.csv)
            job_status_updated = self.command.status.get('state', None)
            self.logger.debug("Job state read: %s", self.command.status)

        # Handle info.csv file creation if needed
        elif filename == 'info.csv':
            self.logger.debug(f"Info file created: {filepath}")
            #self.dispatch_info_result = read_csv_to_dict(filepath)
            # Refresh the info from the job
            self.command._search_results_info_refresh()

    def start(self):
        """
        Monitor the dispatch directory for file creations using watchdog.
        
        Sets the _finalize_file_exists flag when the finalize file is created.
        """
        # Check if a monitoring observer is already running
        if self.fs_monitor is not None and self.fs_monitor.running:
           return

        # Start the observer in a daemon thread
        self.fs_monitor.start()

        # Register atexit handler to stop the observer cleanly
        self.register()
        

        print(f"Started filesystem observer for dispatch directory: {self.dispatch_dir}", file=sys.stderr)
        return self.fs_monitor

    def stop(self):
        """ Stop the dispatch directory observer """
        try:
            if self.fs_monitor is not None and self.fs_monitor.running:
                self.fs_monitor.stop()
            print("Dispatch directory observer stopped cleanly at exit.", file=sys.stderr)
        except Exception as e:
            print(f"Error stopping dispatch directory observer: {e}", file=sys.stderr)

    def register(self):
        """
        Register a function to be called at exit.
        This is used to ensure that all observers are stopped gracefully.
        """
        if not self._atexit_registered:
            atexit.register(self.stop)
            self._atexit_registered = True


def read_csv_to_dict(csv_path) -> Dict[str, Any]:
    """
    Read a CSV file and return a dictionary. Merge row data.
    """
    result = {}
    with open(csv_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, dialect=CsvDialect)
        for row in reader:
            result = {**result, **{k.lstrip('_'): v for k, v in row.items()}}
    return result

__all__ = ['DispatchMonitor']
