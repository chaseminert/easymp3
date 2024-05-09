import sys
from typing import Callable

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3NoHeaderError, ID3
from mutagen.mp3 import MP3

import tag
import util
from tag import Tag


class EasyMP3:

    def __init__(self, directory: str, search_subfolders=True):
        """
        Initializes the EasyMP3 object with a list of paths to MP3 files.
        :param directory: Path to the directory to search for MP3 files or a path
        to a single MP3 file.
        :param search_subfolders: Whether to include subfolders in the search.
        """
        self._list: list[str] = util.get_all_mp3s(directory, search_subfolders)

    def set_title_from_file(self):
        """
        Sets the title tag to the file name (excluding the extension) for all MP3 files in the directory.
        :return: None
        """
        self._set_tag(Tag.TITLE, lambda path: util.filename_no_extension(path))

    def remove_all_tags(self):
        """
        Removes all ID3 tags from the MP3 files in the directory.
        """
        for mp3_path in self._list:
            audio = ID3(mp3_path)
            audio.delete()
            audio.save()

    def set_cover_art_from_file(self, covers_dir, search_subfolders=True):
        """
        Adds cover art to MP3 files based on matching image files in the specified directory.
        :param covers_dir: Directory containing cover images
        :param search_subfolders: Whether to include subfolders in the search
        :return: None
        """
        for mp3_path in self._list:
            song_name = util.filename_no_extension(mp3_path)
            cover_path: str = EasyMP3._find_cover_from_file(song_name, covers_dir, search_subfolders)
            if cover_path is None:
                print(f"Cover Not Found for: {mp3_path}", file=sys.stderr)
            else:
                EasyMP3._apply_cover_art(mp3_path, cover_path)

    def set_tag(self, tag_key: Tag, value: str):
        """
        Sets the specified tag key to a given value for all MP3 files
        in the original directory
        :param tag_key: The tag key to set, from the Tags class
        :param value: The value to assign to the tag
        :return: None
        """
        self._set_tag(tag_key, lambda path: value)

    def set_tags(self, template: dict[Tag, str]):
        """
        Sets multiple tags for mp3 files based on a template. If a key is invalid, it will be
        skipped and printed to stderr.
        :param template: A dictionary that contains Tags from the class Tag and values
                         of type str
        :raises KeyError: If no valid tags are in the template
        :return: None
        """
        valid_tags_dict: dict[Tag, str] = dict()
        for key, value in template.items():
            checked_key = tag.check_tag_key(key)
            if checked_key is not None:
                valid_tags_dict[checked_key] = value
        if not valid_tags_dict:
            raise KeyError(f"All keys invalid for dictionary: {template}")

        for key, value in valid_tags_dict.items():
            self._set_tag(key, lambda path: value, check=False)

    def _set_tag(self, key: Tag, new_val_func: Callable[[str], str], check=True):
        """
        Internal method to update a tag key using a provided function to generate new values.
        :param key: The tag key to set
        :param new_val_func: A function that generates a new tag value given the file path
        :param check: A boolean to decide whether keys should be checked for validity or not
        :return: None
        """
        if check:
            key = tag.check_tag_key(key)
            if key is None:
                raise KeyError(f"Invalid key: {key}")

        for mp3_path in self._list:
            audio = EasyMP3._construct_easy_id3(mp3_path)
            audio[key] = new_val_func(mp3_path)
            audio.save()

    @staticmethod
    def _apply_cover_art(mp3_path: str, cover_path: str):
        """
        An internal method that adds cover art to a single MP3 file
        :param mp3_path: Path to the MP3 file.
        :param cover_path: Path to the cover image.
        :return: None
        """
        with open(cover_path, 'rb') as img:
            cover_data = img.read()

        mime_type = util.get_mime_type(cover_path)
        apic = APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=cover_data)

        mp3_audio = MP3(mp3_path, ID3=ID3)
        mp3_audio.tags.add(apic)
        mp3_audio.save()

    @staticmethod
    def _find_cover_from_file(song_name: str, covers_dir: str, search_subfolders: bool) -> str | None:
        """
        An internal method that searches for a matching cover image for a song name in the specified directory.
        :param song_name: The name of the song to find a cover image for.
        :param covers_dir: The directory containing potential cover images.
        :param search_subfolders: Whether to include subfolders in the search.
        :return:
        """
        files = util.get_all_files(covers_dir, search_subfolders)

        for file in files:
            file_no_extension = util.filename_no_extension(file)
            if file_no_extension.lower() == song_name.lower() and util.is_image(file):
                return file

    @staticmethod
    def _construct_easy_id3(path):
        """
        Constructs an EasyID3 object for the given file path, creating new tags if necessary.
        :param path: Path to the MP3 file.
        :return: AN EasyID3 object for the file.
        """
        try:
            return EasyID3(path)
        except ID3NoHeaderError:
            audio_tags = EasyID3()
            audio_tags.save(path)
            return EasyID3(path)
