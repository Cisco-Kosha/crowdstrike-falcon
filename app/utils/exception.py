# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class NoSuchBucketExists(Error):
    pass


class NoSuchFileExists(Error):
    pass
