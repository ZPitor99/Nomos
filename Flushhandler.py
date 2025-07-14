from logging.handlers import RotatingFileHandler

class FlushableRotatingFileHandler(RotatingFileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()