class TraceNotFoundError(Exception):
    """Raised when a trace is not found"""
    pass

class TraceCollectionError(Exception):
    """Raised when trace collection fails"""
    pass

class TraceExportError(Exception):
    """Raised when trace export fails"""
    pass
