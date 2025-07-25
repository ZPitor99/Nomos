from logging.handlers import RotatingFileHandler

class FlushableRotatingFileHandler(RotatingFileHandler):
    """
    Class FlushableRotatingFileHandler hérite de RotatingFileHandler et pousse le flush de l'Handler.
    """
    def emit(self, record):
        super().emit(record)
        self.flush()