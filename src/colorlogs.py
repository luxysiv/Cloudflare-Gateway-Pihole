import logging

class ColoredLevelFormatter(logging.Formatter):
    COLOR_CODE = {
        'DEBUG':    "\x1b[36m",
        'INFO':     "\x1b[32m",
        'WARNING':  "\x1b[33m",
        'ERROR':    "\x1b[31m",
        'CRITICAL': "\x1b[31;1m"
    }

    def format(self, record):
        levelname = record.levelname
        levelname_color = self.COLOR_CODE.get(levelname, "")
        reset_color = "\x1b[0m"
        record.levelname = f"{levelname_color}{levelname}{reset_color}"
        return super().format(record)
