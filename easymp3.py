import os.path
import sys
from typing import Callable

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3NoHeaderError, ID3
from mutagen.mp3 import MP3

import exception
import tag
import util
from tag import Tag

FROM_FILENAME = "from_filename"

class EasyMP3:
    def __init__(self, directory: str, search_subfolders=True):
        """
        Initializes the EasyMP3 object with a list of paths to MP3 files.
        :param directory: Path to the directory to search for MP3 files or a path
                          to a single MP3 file.
        :param search_subfolders: Whether to include subfolders in the search.
        """
        self._list: list[str] = util.get_all_mp3s(directory, search_subfolders)
        self._directory = directory

    def remove_all_tags(self):
        """
        Removes all ID3 tags from the MP3 files in the directory.
        """
        for mp3_path in self._list:
            audio = ID3(mp3_path)
            audio.delete()
            audio.save()



    def set_cover_art(self, covers_dir=None, template=FROM_FILENAME, search_subfolders=True):
        """
        Adds cover art to MP3 files based on matching image files in the specified directory.
        Matches are found by filename not by tags
        :param covers_dir: Directory containing cover images
        :param search_subfolders: Whether to include subfolders in the search
        :return: None
        """

        if covers_dir is None:
            covers_dir = self._directory
        if not isinstance(template, str):
            raise exception.InvalidStringTemplateError(f"Template must be a string. Invalid template: {template}")
        tag_list = tag.get_tag_list(string=False)
        for mp3_path in self._list:
            if template == FROM_FILENAME:
                cover_file = util.filename_no_extension(mp3_path)
            else:
                cover_file = self._new_name_from_template(mp3_path, template, tag_list)
            cover_path: str = EasyMP3._find_cover_from_file(cover_file, covers_dir, search_subfolders)
            if cover_path is None:
                print(f"Cover Not Found for: {mp3_path}", file=sys.stderr)
            else:
                EasyMP3._apply_cover_art(mp3_path, cover_path)

    def set_filename_from_tags(self, template: str):
        util.check_template(template)
        tag_list = tag.get_tag_list(string=False)
        for mp3_path in self._list:
            parent_path = os.path.dirname(mp3_path)
            new_name = self._new_name_from_template(mp3_path, template, tag_list)
            new_mp3_path = os.path.join(parent_path, new_name) + ".mp3"
            os.rename(mp3_path, new_mp3_path)

    def set_tags_from_filename(self, template: str):
        util.check_template(template)
        for mp3_path in self._list:
            file_name_no_extension = util.filename_no_extension(mp3_path)
            template_dict = util.extract_info(template, file_name_no_extension)
            audio = self._construct_easy_id3(mp3_path)
            for key, value in template_dict.items():
                checked_key = tag.check_tag_key(key)
                audio[checked_key] = value
            audio.save()

    def set_tags_from_template(self, template: dict[Tag, str | Callable]):
        """
        Sets multiple tags for mp3 files based on a template. If a key is invalid, it will be
        skipped and printed to stderr.
        :param template: A dictionary that contains Tags from the class Tag and values
                         of type str
        :raises KeyError: If no valid tags are in the template
        :return: None
        """

        if Tag.COVER_ART in template:
            covers_info = template.pop(Tag.COVER_ART)
            if isinstance(covers_info, str):
                cover_art = covers_info  #  Since covers_info is a path to an image
                if util.is_image(covers_info):
                    #  put same image for all
                    for mp3_path in self._list:
                        self._apply_cover_art(mp3_path, cover_art)
                elif os.path.isdir(covers_info):
                    #  put cover art from filename for all
                    self.set_cover_art(covers_info)
                else:
                    raise exception.InvalidCoversDirectoryError("Covers directory must be either a path to an image or a directory")
            elif isinstance(covers_info, tuple):
                util.check_cover_art_tuple(covers_info)
                covers_template, covers_dir, include_sub = covers_info
                self.set_cover_art(covers_dir, covers_template, include_sub)

        valid_tags_dict: dict[Tag, str] = dict()

        for key, value in template.items():
            checked_key = tag.check_tag_key(key)
            if checked_key is not None:
                valid_tags_dict[checked_key] = value
        if not valid_tags_dict:
            raise exception.NoValidKeysError(f"All keys invalid for dictionary: {template}")

        for mp3_path in self._list:
            audio = self._construct_easy_id3(mp3_path)
            for key, value in valid_tags_dict.items():
                audio[key] = value
            audio.save()


    def _new_name_from_template(self, mp3_path: str, template: str, tag_list: list[Tag]):
        audio = self._construct_easy_id3(mp3_path)
        parent_path = os.path.dirname(mp3_path)
        new_name = template
        for _tag in tag_list:
            new_val = audio.get(_tag.value, f"NO{_tag.name}")
            if isinstance(new_val, list):
                new_val = util.list_to_str(new_val)
            new_name = new_name.replace(_tag.name, new_val)
        return new_name

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

        mime_type = util.get_mime_type(cover_path, verify_image=True)

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
            if file_no_extension.lower().strip() == song_name.lower().strip() and util.is_image(file):
                return file
        return None

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
