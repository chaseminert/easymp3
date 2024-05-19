class EasyMP3Error(Exception):
    pass


class InvalidStringTemplateError(EasyMP3Error):
    pass


class InvalidDictTemplateError(EasyMP3Error):
    pass


class InvalidFilenameError(EasyMP3Error):
    pass


class InvalidMP3DirectoryError(EasyMP3Error):
    pass


class NoValidKeysError(EasyMP3Error):
    pass


class InvalidTagError(EasyMP3Error):
    pass


class InvalidCoversDirectoryError(EasyMP3Error):
    pass

class InvalidCoversTupleError(EasyMP3Error):
    pass
