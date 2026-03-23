import logging

class Logger:
    def __init__(self):
        """
        Initialize the Logger instance with a default logger.
        """
        self.logger = logging.getLogger()

    def setup_logger(self, log_file: str):
        """
        Set up the logger configuration to write logs to the specified file.
        Removes existing handlers and sets log format and level.
        Args:
            log_file (str): Path to the log file.
        """
        # Remove all handlers associated with the root logger object
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    def write_log(self, message: str, level: str = "info"):
        """
        Write a log message with the specified level.
        Args:
            message (str): The log message to write.
            level (str): The log level ('info', 'warning', 'error', 'debug'). Defaults to 'info'.
        """
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.debug(message)