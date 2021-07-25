class ExceptionWithInfo(Exception):
    """Stocklab generic exception."""
    def __init__(self, message, info):
        super().__init__(message)
        self.info = info

    def __str__(self):
        return f'{super().__str__()} {str(self.info)}'

class NoLongerAvailable(Exception):
    """
    The requested data is no longer available.  It may be not accessible
    from the website temporarily or permenently.
    """
    pass

class ParserError(ExceptionWithInfo):
    """Indicating there's something wrong during the data parsing."""
    pass
