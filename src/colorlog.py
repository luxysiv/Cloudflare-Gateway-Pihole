import logging
from datetime import datetime
import os

class ColoredLevelFormatter(logging.Formatter):
    COLOR_CODE = {
        'DEBUG':    "\x1b[36m",   # Cyan
        'INFO':     "\x1b[0m",    # White
        'WARNING':  "\x1b[33m",   # Yellow
        'ERROR':    "\x1b[31m",   # Red
        'CRITICAL': "\x1b[31;1m", # Bold Red
        'RESET':    "\x1b[0m",    # Reset color
        'DATE':     "\x1b[32m",   # Green for date
        'CALLER':   "\x1b[36m"    # Cyan for caller info
    }

    def format(self, record):
        levelname = record.levelname
        levelname_color = self.COLOR_CODE.get(levelname, "")
        reset_color = self.COLOR_CODE['RESET']
        date_color = self.COLOR_CODE['DATE']
        caller_color = self.COLOR_CODE['CALLER']

        # Format current time with milliseconds
        current_time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Check if the record is from __init__.py
        if os.path.basename(record.pathname) == "__init__.py":
            caller_info = f"{os.path.basename(os.path.dirname(record.pathname))}:{record.funcName}:{record.lineno}"
        else:
            caller_info = f"{record.filename}:{record.funcName}:{record.lineno}"

        # Store original message
        original_message = record.getMessage()

        # Format the log message with timestamp, levelname, caller info, and original message
        formatted_message = (
            f"{date_color}{current_time}{reset_color} | "
            f"{levelname_color}{levelname:<8}{reset_color} | "
            f"{caller_color}{caller_info}{reset_color} - "
            f"{levelname_color}{original_message}{reset_color}"
        )

        # Assign formatted message back to record
        record.msg = formatted_message

        # Call the base formatter to format the entire log record
        formatted_record = super().format(record)

        return formatted_record
        

# Configure logging
logging.getLogger().setLevel(logging.INFO)  # Set the logging level
formatter = ColoredLevelFormatter()  # Create an instance of ColoredLevelFormatter
console = logging.StreamHandler()  # Create a console handler
console.setFormatter(formatter)  # Set the formatter for the console handler
logger = logging.getLogger()  # Get the root logger
logger.addHandler(console)  # Add console handler to the root logger
