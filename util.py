import mimetypes
import os


def is_mp3(file_path: str):
    """
    Checks if a given file path points to an existing MP3 file.

    :param file_path: Path to the file to check.
    :return: True if the file is an MP3 file, otherwise False.
    """
    return os.path.isfile(file_path) and file_path.endswith(".mp3")


def is_image(file_path: str) -> bool:
    """
    Determines if the file at the given path is an image file.

    :param file_path: Path to the file to check.
    :return: True if the file is an image and exists, otherwise False.
    """
    return os.path.isfile(file_path) and "image" in get_mime_type(file_path)


def no_filter(_):
    """
    A no-op filter function that always returns True. Useful as a default filter.

    :param _: An unused parameter.
    :return: Always True.
    """
    return True


def get_all_mp3s(directory: str, search_subfolders):
    """
    Retrieves a list of MP3 files from a directory, optionally searching subfolders.

    :param directory: Path to the root directory or an individual MP3 file.
    :param search_subfolders: Whether to include subdirectories in the search.
    :return: List of MP3 files found.
    :raises TypeError: If the given path is not an MP3 file or directory.
    """
    if is_mp3(directory):
        return [directory]
    elif os.path.isdir(directory):
        return get_all_files(directory, search_subfolders, is_mp3)
    else:
        raise TypeError(f"\"{directory}\" is neither an MP3 file nor a directory")


def get_all_files(directory: str, search_subfolders, filter_func=no_filter):
    """
    Retrieves a list of files from a directory based on a filter function.

    :param directory: Path to the root directory to search for files.
    :param search_subfolders: Whether to include subdirectories in the search.
    :param filter_func: A function that filters which files to include.
    :return: List of files meeting the filter criteria.
    """
    files = []

    if search_subfolders:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                path = os.path.join(root, filename)
                if filter_func(path):
                    files.append(path)
    else:
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            if filter_func(path):
                files.append(path)

    return files


def filename_no_extension(file_path: str):
    """
    Extracts the base filename from a given file path, excluding the extension.

    :param file_path: Path to the file.
    :return: The filename without the extension.
    """
    base_filename = os.path.basename(file_path)
    # Split the filename from its extension
    filename_without_ext, _ = os.path.splitext(base_filename)
    return filename_without_ext


def get_mime_type(path):
    """
    Determines the MIME type of the file at the given path.

    :param path: Path to the file to identify.
    :return: The MIME type of the file.
    :raises TypeError: If the MIME type cannot be determined.
    """
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        raise TypeError(f"Invalid mime type for path: {path}")
    else:
        return mime_type
