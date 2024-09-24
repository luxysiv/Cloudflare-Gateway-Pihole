import logging
from datetime import datetime
import os

class ColoredLevelFormatter(logging.Formatter):
    """
    A custom logging formatter that adds colors to log levels and formats the output.
    """

    # Color codes for log levels
    COLOR_CODE = {
        'DEBUG':    "\x1b[36m",
        'INFO':     "\x1b[0m",
        'WARNING':  "\x1b[33m",
        'ERROR':    "\x1b[31m",
        'CRITICAL': "\x1b[31;1m",
        'RESET':    "\x1b[0m",
        'DATE':     "\x1b[32m",
        'CALLER':   "\x1b[36m"
    }

    def format(self, record):
        """
        Formats the log record.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted log record.
        """
        levelname = record.levelname
        levelname_color = self.COLOR_CODE.get(levelname, "")
        reset_color = self.COLOR_CODE['RESET']
        date_color = self.COLOR_CODE['DATE']
        caller_color = self.COLOR_CODE['CALLER']

        # Get the current time
        current_time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        # Get caller information
        if os.path.basename(record.pathname) == "__init__.py":
            caller_info = f"{os.path.basename(os.path.dirname(record.pathname))}:{record.funcName}:{record.lineno}"
        else:
            caller_info = f"{record.filename}:{record.funcName}:{record.lineno}"

        original_message = record.getMessage()

        # Create the formatted log message
        formatted_message = (
            f"{date_color}{current_time}{reset_color} | "
            f"{levelname_color}{levelname:<8}{reset_color} | "
            f"{caller_color}{caller_info}{reset_color} - "
            f"{levelname_color}{original_message}{reset_color}"
        )

        record.msg = formatted_message
        formatted_record = super().format(record)

        return formatted_record


# Configure logger
logging.getLogger().setLevel(logging.INFO)
formatter = ColoredLevelFormatter()
console = logging.StreamHandler()
console.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(console)
