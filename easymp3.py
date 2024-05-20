import os.path
import sys

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

    def set_cover_art(self, covers_dir=None, template_str: str = FROM_FILENAME, search_subfolders=True):
        """
        Adds cover art to MP3 files based on matching image files in the specified directory.
        Matches are found by filename or by using a template string
        :param covers_dir: Directory containing cover images. Default is the directory of the MP3 files
        :param template_str: A string containing a template for the name of the cover art (with the default
                             being to search for matching file names).
                             ex: f"{Tag.TITLE} - {Tag.ARTIST}".
                             Note: Templates should not have a file extension at the end
        :param search_subfolders: Whether to include subfolders in the search
        :return: None
        """

        if covers_dir is None:
            covers_dir = self._directory
        if not isinstance(template_str, str):
            raise exception.InvalidStringTemplateError(f"Template must be a string. Invalid template: {template_str}")
        tag_list = tag.get_tag_list(string=False)
        for mp3_path in self._list:
            if template_str == FROM_FILENAME:
                cover_file = util.filename_no_extension(mp3_path)
            else:
                cover_file = self._new_name_from_template(mp3_path, template_str, tag_list)
            cover_path: str = EasyMP3._find_cover_from_file(cover_file, covers_dir, search_subfolders)
            if cover_path is None:
                print(f"Cover Not Found for: {mp3_path}", file=sys.stderr)
            else:
                EasyMP3._apply_cover_art(mp3_path, cover_path)

    def set_filename_from_tags(self, template_str: str):
        """
        Renames all the MP3 filenames with their tags by using a template.
        :param template_str: A string representing how to format the new file name.
                         ex. f"{Tag.TITLE} - {Tag.ARTIST}"
                         Note: A template should never end with .mp3 as this is
                         implied
        :return: None
        """
        util.check_template(template_str)
        tag_list = tag.get_tag_list(string=False)
        for mp3_path in self._list:
            parent_path = os.path.dirname(mp3_path)
            new_name = self._new_name_from_template(mp3_path, template_str, tag_list)
            new_mp3_path = os.path.join(parent_path, new_name) + ".mp3"
            os.rename(mp3_path, new_mp3_path)

    def set_tags_from_filename(self, template_str: str):
        """
        Sets tags for all the MP3s based on their filename by using a provided template
        :param template_str: A string representing how to extract the tags.
                         ex. f"{Tag.TITLE} - {Tag.ARTIST}"
                         Note: A template should never end with .mp3 as this is implied
        :return: None
        """
        util.check_template(template_str)
        for mp3_path in self._list:
            file_name_no_extension = util.filename_no_extension(mp3_path)
            template_dict = util.extract_info(template_str, file_name_no_extension)
            audio = self._construct_easy_id3(mp3_path)
            for key, value in template_dict.items():
                checked_key = tag.check_tag_key(key)
                audio[checked_key] = value
            audio.save()

    def set_tags_from_template(self, template_dict: dict[Tag, str | tuple[str, str, bool] | tuple[str, str]]):
        """
        Sets multiple tags for MP3 files based on a template dictionary.

        This method updates tags for MP3 files using a provided template. Invalid keys are skipped and printed to
        stderr.

        :param: template_dict (dict[Tag, str | tuple[str, str, bool] | tuple[str, str]]): - A dictionary containing
        `Tag` keys and string values. - Special handling for `Tag.COVERART` values: - **Single path** (str): Path to
        a cover art file applied to all MP3 files. - **Directory path** (str): Path to cover art files with matching
        filenames to MP3 files, searching subfolders. - **Template string** (str): Template for cover art filenames,
        searching in the MP3 files' directory and subfolders. - **Tuple** (tuple[str, str, bool] | tuple[str,
        str]): - Template for cover art filenames. - Path to the cover art files. - Boolean indicating whether to
        search subfolders (optional).

        :raise KeyError if no valid tags are found

        :return None
        """

        if Tag.COVER_ART in template_dict:
            covers_info = template_dict.pop(Tag.COVER_ART)
            if isinstance(covers_info, str):
                if util.is_image(covers_info):
                    #  put same image for all
                    for mp3_path in self._list:
                        self._apply_cover_art(mp3_path, covers_info)
                elif os.path.isdir(covers_info):
                    #  put cover art from filename for all
                    self.set_cover_art(covers_info)
                else:
                    #  It must be a template
                    self.set_cover_art(template_str=covers_info)
            elif isinstance(covers_info, tuple):
                covers_template, covers_dir, include_sub = util.parse_cover_art_tuple(covers_info)
                self.set_cover_art(covers_dir, covers_template, include_sub)

        valid_tags_dict: dict[Tag, str] = dict()

        for key, value in template_dict.items():
            checked_key = tag.check_tag_key(key)
            if checked_key is not None:
                valid_tags_dict[checked_key] = value
        if not valid_tags_dict:
            raise exception.NoValidKeysError(f"All keys invalid for dictionary: {template_dict}")

        for mp3_path in self._list:
            audio = self._construct_easy_id3(mp3_path)
            for key, value in valid_tags_dict.items():
                audio[key] = value
            audio.save()

    def extract_cover_arts(self, folder_path: str, template_str: str = FROM_FILENAME):
        tag_list = tag.get_tag_list(string=False)
        os.makedirs(folder_path, exist_ok=True)
        for mp3_path in self._list:
            if template_str == FROM_FILENAME:
                cover_name_no_exten = util.filename_no_extension(mp3_path)
            else:
                cover_name_no_exten = self._new_name_from_template(mp3_path, template_str, tag_list)

            dest_path_no_exten = os.path.join(folder_path, cover_name_no_exten)
            util.extract_cover_art(mp3_path, dest_path_no_exten)

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
