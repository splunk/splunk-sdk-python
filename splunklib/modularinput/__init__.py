"""The following imports allow these classes to be imported via
the splunklib.modularinput package like so:

from splunklib.modularinput import *
"""
from .argument import Argument
from .decorators import Configuration
from .event import Event
from .event_writer import EventWriter
from .input_definition import InputDefinition
from .scheme import Scheme
from .script import Script
from .validation_definition import ValidationDefinition
