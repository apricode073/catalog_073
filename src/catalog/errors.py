class CatalogError(Exception):
    pass


class InvalidItemError(CatalogError):
    pass


class DuplicateIdError(CatalogError):
    pass


class ItemNotFoundError(CatalogError):
    pass


class UnsupportedVersionError(CatalogError):
    pass


class CorruptedFileError(CatalogError):
    pass

class NothingToUndoError(CatalogError):
    pass

class InvalidVersionError(CatalogError):
    pass
