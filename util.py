import mimetypes
import os
import re

import tag
from tag import Tag

import exception


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


def no_change(item):
    return item


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
        raise exception.InvalidMP3DirectoryError(f"\"{directory}\" is neither an MP3 file nor a directory")


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


def get_mime_type(path, verify_image=False):
    """
    Determines the MIME type of the file at the given path.

    :param verify_image: Whether to verify that the file is an image or not
    :param path: Path to the file to identify.
    :return: The MIME type of the file.
    :raises TypeError: If the MIME type cannot be determined.
    """
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        raise TypeError(f"Invalid mime type for path: {path}")
    elif verify_image and "image" not in mime_type:
        raise TypeError(f"The following path is not an image: {path}\nMime Type: {mime_type}")
    else:
        return mime_type


def _replace_attribute(attribute: str) -> str:
    return f'(?P<{attribute}>.+)'


def list_to_str(_list: list):
    return ", ".join(_list)


def extract_info(template: str, input_string: str):
    # Escape special regex characters in the template
    # Replace placeholders with named capture groups
    og_template = template  # save original template

    template = re.escape(template)

    template_vals = tag.get_tag_list()

    for tag_val in template_vals:
        template = template.replace(tag_val, _replace_attribute(tag_val))

    # Compile the regex pattern
    pattern = re.compile(template)

    # Match the pattern to the input string
    match = pattern.match(input_string)

    # If there's a match, return the group dictionary
    if match:
        result_dict = match.groupdict()
        return {getattr(Tag, key): value for key, value in result_dict.items()}
    else:
        raise exception.InvalidFilenameError(f"String '{input_string}' is invalid for template '{og_template}'")


def check_template(template: str):
    if template.endswith(".mp3"):
        raise exception.InvalidStringTemplateError(
            f"Invalid string template '{template}'. A string template should not end in .mp3")


def parse_cover_art_tuple(covers_info: tuple[str, str, bool]):
    tuple_len = len(covers_info)
    if not (tuple_len == 3 or tuple_len == 2):
        raise exception.InvalidCoversTupleError(f"Tuple {covers_info} is invalid. Must be of length 2 or 3")

    covers_dir = cover_template = include_subfolders = None
    if tuple_len == 2:
        cover_template, covers_dir = covers_info
        include_subfolders = True
    elif tuple_len == 3:
        cover_template, covers_dir, include_subfolders = covers_info

    if not (isinstance(covers_dir, str) and isinstance(cover_template, str) and isinstance(include_subfolders, bool)):
        raise exception.InvalidCoversTupleError(f"Tuple {covers_info} in invalid. The correct type is tuple[str, str, bool] or tuple[str, str]")
    if not os.path.isdir(covers_dir):
        raise exception.InvalidCoversDirectoryError(f"The specified covers directory is not a directory: {covers_dir}")

    return cover_template, covers_dir, include_subfolders


