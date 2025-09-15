"""
Cross-platform file monitor for Splunk Enterprise
Uses Linux inotify when available, falls back to polling on Windows/other platforms
"""

import os
import sys
import time
import threading
import struct
import select

def create_file_monitor(watch_dir, callback, recursive=False):
    """Factory function to create appropriate monitor for the platform"""
    if sys.platform.startswith('linux'):
        try:
            return LinuxInotifyMonitor(watch_dir, callback, recursive)
        except Exception as e:
            print(f"Failed to create inotify monitor, falling back to polling: {e}")
            return PollingFileMonitor(watch_dir, callback, recursive)
    else:
        return PollingFileMonitor(watch_dir, callback, recursive)

class LinuxInotifyMonitor:
    """Linux-specific file monitor using inotify via ctypes"""
    
    # inotify event constants
    IN_CREATE = 0x00000100
    IN_MOVED_TO = 0x00000080
    IN_CLOSE_WRITE = 0x00000008
    IN_ISDIR = 0x40000000
    
    def __init__(self, watch_dir, callback, recursive=False):
        self.watch_dir = os.path.abspath(watch_dir)
        self.callback = callback
        self.recursive = recursive
        self.running = False
        self.watches = {}  # watch_descriptor -> path mapping
        self.pending_files = {}  # Track files being written
        
        # Validate directory exists
        if not os.path.isdir(self.watch_dir):
            raise ValueError(f"Directory does not exist: {self.watch_dir}")
        
        # Load libc and set up inotify
        self._setup_inotify()
        
    def _setup_inotify(self):
        """Initialize inotify system calls"""
        import ctypes
        import ctypes.util
        
        libc = ctypes.CDLL(ctypes.util.find_library('c'))
        
        # inotify_init
        self.inotify_init = libc.inotify_init
        self.inotify_init.restype = ctypes.c_int
        
        # inotify_add_watch
        self.inotify_add_watch = libc.inotify_add_watch
        self.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        self.inotify_add_watch.restype = ctypes.c_int
        
        # inotify_rm_watch
        self.inotify_rm_watch = libc.inotify_rm_watch
        self.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
        self.inotify_rm_watch.restype = ctypes.c_int
        
        # Initialize inotify file descriptor
        self.fd = self.inotify_init()
        if self.fd < 0:
            raise OSError("Failed to initialize inotify")
    
    def start(self):
        """Start monitoring for file changes"""
        # Add initial watches
        self._add_watch(self.watch_dir)
        
        if self.recursive:
            self._add_recursive_watches(self.watch_dir)
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.cleanup_thread = threading.Thread(target=self._cleanup_pending_files, daemon=True)
        
        self.monitor_thread.start()
        self.cleanup_thread.start()
        
        print(f"Started inotify monitoring on: {self.watch_dir}")
        return self.monitor_thread
    
    def _add_watch(self, path):
        """Add inotify watch to a directory"""
        mask = self.IN_CREATE | self.IN_MOVED_TO | self.IN_CLOSE_WRITE
        if self.recursive:
            mask |= self.IN_ISDIR
            
        try:
            wd = self.inotify_add_watch(self.fd, path.encode('utf-8'), mask)
            if wd < 0:
                print(f"Warning: Failed to add watch for {path}")
                return None
            self.watches[wd] = path
            return wd
        except Exception as e:
            print(f"Error adding watch for {path}: {e}")
            return None
    
    def _add_recursive_watches(self, root_path):
        """Recursively add watches to all subdirectories"""
        for dirpath, dirnames, filenames in os.walk(root_path):
            if dirpath != root_path:  # Already added root
                self._add_watch(dirpath)
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Use select with timeout for graceful shutdown
                ready, _, _ = select.select([self.fd], [], [], 1.0)
                
                if ready and self.fd in ready:
                    data = os.read(self.fd, 4096)
                    self._process_events(data)
                    
            except OSError as e:
                if self.running:  # Only print error if we're supposed to be running
                    print(f"Error in monitor loop: {e}")
                break
    
    def _process_events(self, data):
        """Parse and process inotify events"""
        offset = 0
        while offset < len(data):
            if len(data) - offset < 16:
                break
                
            # Parse inotify_event structure
            wd, mask, cookie, name_len = struct.unpack('iIII', data[offset:offset+16])
            offset += 16
            
            name = ""
            if name_len > 0:
                name = data[offset:offset+name_len].rstrip(b'\0').decode('utf-8', errors='replace')
                offset += name_len
            
            if wd in self.watches:
                self._handle_event(self.watches[wd], name, mask)
    
    def _handle_event(self, watch_path, filename, mask):
        """Handle individual inotify events"""
        if not filename:
            return
            
        full_path = os.path.join(watch_path, filename)
        
        # Handle directory creation for recursive monitoring
        if (mask & self.IN_ISDIR) and (mask & (self.IN_CREATE | self.IN_MOVED_TO)) and self.recursive:
            self._add_watch(full_path)
            return
        
        # Handle file events
        if mask & self.IN_CREATE:
            # File created but might still be writing
            self.pending_files[full_path] = time.time()
            
        elif mask & self.IN_MOVED_TO:
            # File moved into directory - treat as creation
            self.pending_files[full_path] = time.time()
            
        elif mask & self.IN_CLOSE_WRITE:
            # File finished writing. Delete from list of pending files.
            if full_path in self.pending_files:
                del self.pending_files[full_path]
            self._safe_callback(full_path)
    
    def _cleanup_pending_files(self):
        """Clean up files that have been pending for too long"""
        while self.running:
            current_time = time.time()
            timeout_files = []
            
            for file_path, create_time in self.pending_files.items():
                if current_time - create_time > 5.0:  # 5 second timeout
                    if os.path.exists(file_path):
                        timeout_files.append(file_path)
            
            for file_path in timeout_files:
                if file_path in self.pending_files:
                    del self.pending_files[file_path]
                self._safe_callback(file_path)
            
            time.sleep(1.0)
    
    def _safe_callback(self, file_path):
        """Safely call the user callback"""
        try:
            # Verify file still exists and is readable
            if os.path.isfile(file_path):
                self.callback(file_path)
        except Exception as e:
            print(f"Error in callback for {file_path}: {e}")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        
        # Clean up watches
        for wd in list(self.watches.keys()):
            self.inotify_rm_watch(self.fd, wd)
        
        # Close file descriptor
        if hasattr(self, 'fd') and self.fd >= 0:
            os.close(self.fd)
        
        print("Stopped inotify monitoring")


class PollingFileMonitor:
    """Cross-platform file monitor using polling (fallback for Windows/other platforms)"""
    
    def __init__(self, watch_dir, callback, recursive=False):
        self.watch_dir = os.path.abspath(watch_dir)
        self.callback = callback
        self.recursive = recursive
        self.running = False
        self.known_files = {}  # path -> (size, mtime)
        self.poll_interval = 0.5  # Seconds between polls
        
        if not os.path.isdir(self.watch_dir):
            raise ValueError(f"Directory does not exist: {self.watch_dir}")
        
        # Initialize known files
        self._scan_directory()
    
    def start(self):
        """Start monitoring for file changes"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"Started polling file monitor on: {self.watch_dir} (interval: {self.poll_interval}s)")
        return self.monitor_thread
    
    def _scan_directory(self):
        """Scan directory and update known files"""
        new_files = {}
        
        if self.recursive:
            for root, dirs, files in os.walk(self.watch_dir):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    new_files[file_path] = self._get_file_info(file_path)
        else:
            try:
                for filename in os.listdir(self.watch_dir):
                    file_path = os.path.join(self.watch_dir, filename)
                    if os.path.isfile(file_path):
                        new_files[file_path] = self._get_file_info(file_path)
            except OSError:
                pass  # Directory might have been deleted
        
        return new_files
    
    def _get_file_info(self, file_path):
        """Get file size and modification time"""
        try:
            stat_info = os.stat(file_path)
            return (stat_info.st_size, stat_info.st_mtime)
        except OSError:
            return None
    
    def _monitor_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                current_files = self._scan_directory()
                
                # Check for new files
                for file_path in current_files:
                    if file_path not in self.known_files:
                        # New file detected
                        if self._wait_for_stable_file(file_path):
                            self._safe_callback(file_path)
                
                self.known_files = current_files
                
            except Exception as e:
                print(f"Error in polling loop: {e}")
            
            time.sleep(self.poll_interval)
    
    def _wait_for_stable_file(self, file_path):
        """Wait for file to stabilize (stop growing)"""
        stable_checks = 3
        check_interval = 0.1
        
        prev_info = self._get_file_info(file_path)
        if not prev_info:
            return False
        
        for _ in range(stable_checks):
            time.sleep(check_interval)
            current_info = self._get_file_info(file_path)
            
            if not current_info:
                return False
                
            if current_info != prev_info:
                # File is still changing
                prev_info = current_info
                stable_checks = 3  # Reset counter
            else:
                stable_checks -= 1
        
        return True
    
    def _safe_callback(self, file_path):
        """Safely call the user callback"""
        try:
            if os.path.isfile(file_path):
                self.callback(file_path)
        except Exception as e:
            print(f"Error in callback for {file_path}: {e}")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        print("Stopped polling file monitor")
