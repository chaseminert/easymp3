class EasyMP3Error(Exception):
    pass


class InvalidTemplateStringError(EasyMP3Error):
    pass


class InvalidTemplateDictError(EasyMP3Error):
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

class InvalidCoverArtDataError(EasyMP3Error):
    pass
