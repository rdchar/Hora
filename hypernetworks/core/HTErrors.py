
class HnErrors(BaseException):
    """Base class"""
    pass


class HnSearchError(HnErrors):
    """Search Error"""
    pass


class HnInsertError(HnErrors):
    """Add to Hn Error"""
    pass


class HnUnknownHsType(HnErrors):
    """The Hs Type is unknown"""
    pass


class HnVertexNoFound(HnErrors):
    """The vertex cannot be found in the Hn"""
    pass


class HnImmutableType(HnErrors):
    """ This type is immutable """
    pass
