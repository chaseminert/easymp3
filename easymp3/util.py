import mimetypes
import os
import re
import sys
from typing import Any, Type, Union

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, ID3NoHeaderError, APIC
from mutagen.mp3 import MP3

from . import exception
from . import tag
from .tag import Tag

INVALID_CHAR_MAP = {
    ":": "-",
    "\\": "-",
    "/": "-",
    "*": " ",
    "?": " ",
    "\"": "'",
    "<": " ",
    ">": " ",
    "|": " "
}

INVALID_CHAR_TRANS = str.maketrans(INVALID_CHAR_MAP)


def is_mp3(file_path: str) -> bool:
    """
    Checks if a given file path points to an existing MP3 file.

    :param file_path: Path to the file to check.
    :returns: True if the file is an MP3 file, otherwise False.
    """
    return os.path.isfile(file_path) and file_path.endswith(".mp3")


def is_image(file_path: str) -> bool:
    """
    Determines if the file at the given path is an image file.

    :param file_path: Path to the file to check.
    :returns: True if the file is an image and exists, otherwise False.
    """
    return os.path.isfile(file_path) and "image" in get_mime_type(file_path)


def no_filter(_: Any) -> bool:
    """
    A no-op filter function that always returns True. Useful as a default filter.

    :param _: An unused parameter.
    :returns: Always True.
    """
    return True


def get_all_mp3s(directory: str, search_subfolders: bool) -> list[str]:
    """
    Retrieves a list of MP3 files from a directory

    :param directory: Path to a directory containing MP3 files or an individual MP3 file
    :param search_subfolders: Whether to include subdirectories in the search.
    :return: List of MP3 files found
    :raises TypeError: If the given path is not an MP3 file or directory.
    """
    if is_mp3(directory):
        return [directory]
    elif os.path.isdir(directory):
        return get_all_files(directory, search_subfolders, is_mp3)
    else:
        raise exception.InvalidMP3DirectoryError(f"\"{directory}\" is neither an MP3 file nor a directory")


def get_all_files(directory: str, search_subfolders: bool, filter_func=no_filter) -> list[str]:
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


def filename_no_extension(file_path: str) -> str:
    """
    Extracts the base filename from a given file path, excluding the extension.

    :param file_path: Path to the file.
    :return: The filename without the extension.
    """
    base_filename = os.path.basename(file_path)
    # Split the filename from its extension
    filename_without_ext, _ = os.path.splitext(base_filename)
    return filename_without_ext


def get_mime_type(path, verify_image=False) -> str:
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
    """
    An internal method used for replacing template strings with actual values using regex
    :param attribute: a string which should be a member of Tag
    :return: The new regex string
    """
    return f'(?P<{attribute}>.+)'


def list_to_str(_list: list) -> str:
    """
    Converts a list to a string. Useful when a tag has a list of strings instead of
    simply a string
    :param _list: The list to be converted
    :return: A string representation of the list
    """
    return ", ".join(_list)


def construct_mp3_obj(path: str, cls: Type[Union[EasyID3, ID3]] = EasyID3) -> EasyID3 | ID3:
    """
    Constructs an object for the given file path, creating new tags if necessary.
    :param path: Path to the MP3 file.
    :param cls: The class to create. Either EasyID3 or MP3
    :return: An object for the file.
    """

    try:
        return cls(path)
    except ID3NoHeaderError:
        audio_tags = cls()
        audio_tags.save(path)
        return cls(path)


def extract_info(template: str, input_string: str) -> dict[Tag, str] | None:
    # Escape special regex characters in the template
    # Replace placeholders with named capture groups
    """
    Parses the information from a template string
    :param template: A traditional string template.
                     ex. f"{Tag.TITLE} - {Tag.ARTIST}"
    :param input_string: The non-templated string.
                     ex. "Black And White - Juice WRLD"
    :return: A dictionary with tags and values
    """

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
        return None


def copy_tags(source_file: str, dest_file: str, tag_set: set[str] | None, complement: bool):
    """
    Copy the tags from one MP3 file to another
    :param source_file: The file that will have its tags copied
    :param dest_file: The file that will receive the tags
    :param tag_set: A set of tags. Should be a set of values from the Tag class
    :param complement: Whether to check if something is in the set, or check
        if it is not in the set
    """

    # Load the source MP3 file and read its tags
    source_audio = MP3(source_file, ID3=EasyID3)
    all_tags = source_audio.tags.items()

    # Load the destination MP3 file and initialize it for ID3 tags if not already present
    dest_audio = MP3(dest_file, ID3=EasyID3)

    # Clear existing tags in the destination file

    # Copy each tag from the source to the destination

    if tag_set is None:
        verified_tag_set = set()
    else:
        verified_tag_set = tag_set

    for tag_key, tag_value in all_tags:
        _test = tag_key in verified_tag_set
        if complement:
            _test = not _test  # If it's not in the set

        if (tag_set is not None and _test) or tag_set is None:
            dest_audio[tag_key] = tag_value
    # Save the destination file with the new tags
    dest_audio.save()


    ca_in_set = Tag.COVER_ART.value in verified_tag_set
    if complement:
        ca_in_set = not ca_in_set

    if tag_set is not None and (not ca_in_set):
        return


    src_id3 = construct_mp3_obj(source_file, cls=ID3)
    dest_id3 = construct_mp3_obj(dest_file, cls=ID3)
    for _tag in src_id3.values():
        if isinstance(_tag, APIC):
            dest_id3.add(_tag)
    dest_audio.save()
    dest_id3.save(dest_file)





def check_template(template: str) -> None:
    """
    A method to ensure that a template string does not end with .mp3
    :param template: A traditional string template
    :raises InvalidStringTemplateError: If the template ends with .mp3
    """
    if template.endswith(".mp3"):
        raise exception.InvalidTemplateStringError(
            f"Invalid string template '{template}'. A string template should not end in .mp3")


def extract_cover_art(mp3_path: str, dest_path_no_extension: str, show_output: bool) -> None:
    """
    Extracts the first cover art from an MP3 file and saves it to the destination folder.
    :param mp3_path: Path to the MP3 file.
    :param dest_path_no_extension: Path to the destination folder and file (with no extension) where
    the cover art will be saved.
    :param show_output: Whether to include the console output
    """

    audio = MP3(mp3_path, ID3=ID3)

    apic_frame = audio.tags.getall('APIC')

    if not apic_frame:
        print(f"No cover art found for file: {mp3_path}", file=sys.stderr)
        return

    apic_frame = apic_frame[0]

    mime: str = apic_frame.mime.lower()
    if not mime.startswith("image"):
        raise exception.InvalidCoverArtDataError(f"The cover art from mp3 '{mp3_path}' has invalid data\n"
                                                 f"Mime type is '{mime}'")
    extension = get_extension_from_mime(mime)
    dest_path_full = dest_path_no_extension + extension

    base_dir = os.path.dirname(dest_path_full)
    os.makedirs(base_dir, exist_ok=True)

    with open(dest_path_full, 'wb') as img_file:
        img_file.write(apic_frame.data)
    if show_output:
        print(f"Successfully extracted cover art from MP3 with path '{mp3_path}' to file '{dest_path_full}'")

def apply_cover_art(mp3_path: str, cover_path: str):
    """
    Internal wrapper method that applies a cover art to a file
    :param mp3_path: The path to an MP3 file
    :param cover_path: The path to the cover art image
    """
    with open(cover_path, 'rb') as img:
        cover_data = img.read()
        mime_type = get_mime_type(cover_path, verify_image=True)

    apply_cover_art_data(mp3_path, cover_data, mime_type)


def apply_cover_art_data(mp3_path: str, cover_data, mime_type: str):
    """
    An internal method that adds cover art to a single MP3 file
    :param mp3_path: Path to the MP3 file.
    :param cover_data: The binary data for the cover art.
    """

    apic = APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=cover_data)

    mp3_audio = MP3(mp3_path, ID3=ID3)

    if mp3_audio.tags is None:
        mp3_audio.add_tags()

    mp3_audio.tags.add(apic)
    mp3_audio.save()

def get_extension_from_mime(mime: str) -> str:
    """
    Gets the file extension of a file
    :param mime: A string representing the mime type
    :return: The extension or 'bin' if the mimetype cannot be guessed
    """
    extension = mimetypes.guess_extension(mime)
    if extension:
        return extension
    else:
        return 'bin'  # Default if mimetype is unknown


def is_valid_sub_file_name(name: str) -> bool:
    """
    Returns if a string has any characters that can't be in a filename path
    :param name: The path to be tested
    :return: True if `name` can be a valid path, False otherwise
    """
    return name == name.translate(INVALID_CHAR_TRANS)


def get_valid_replacement(initial_val: str) -> str:
    """
    Repeatedly prompts the user for a replacement string that does
    not have invalid path characters.

    :param initial_val: The initial string the user entered
    :return: The new (user entered) value with no invalid path characters
    """
    invalid_chars = get_invalid_filename_chars(initial_val)
    print(f"'{initial_val}' contains invalid path characters: {invalid_chars}")
    while True:
        new_val = input(f"Enter new name: ")
        if new_val == new_val.translate(INVALID_CHAR_TRANS):
            return new_val
        invalid_chars = get_invalid_filename_chars(new_val)
        print(f"The entered name contains invalid path characters: {invalid_chars}")


def get_invalid_filename_chars(name: str, string=True) -> str | tuple[str]:
    """
    Gets the specific invalid characters that were used to help
    show the user which characters were invalid

    :param name: The string to be tested for invalid characters
    :param string: A boolean for whether to return the result as
        a string or as a tuple of the characters
    :return: Either a tuple of characters or one string
        representing the tuple
    """
    invalid_chars = set()
    for char in name:
        if char in INVALID_CHAR_MAP:
            invalid_chars.add(char)

    invalid_tuple = tuple(sorted(invalid_chars))
    if string:
        wrapped_tuple = (f"'{char}'" for char in invalid_tuple)
        return ", ".join(wrapped_tuple)
    else:
        return invalid_tuple
