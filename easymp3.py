import os.path
import shutil
import sys

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3NoHeaderError, ID3
from mutagen.mp3 import MP3

import exception
import tag
import util
from util import INVALID_CHAR_TRANS
from tag import Tag

COVER_FROM_FILENAME = "cover_from_filename"


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
        self._search_sub = search_subfolders

    def remove_all_tags(self, show_output=True) -> None:
        """
        Removes all ID3 tags from the MP3 files in the directory.
        :param show_output: Whether to show the console output
        """
        for mp3_path in self._list:
            audio = ID3(mp3_path)
            audio.delete()
            audio.save()
            if show_output:
                print(f"All tags removed for '{mp3_path}'")

    def set_cover_art(self, covers_dir=None, template_str: str = COVER_FROM_FILENAME,
                      search_subfolders=True, show_output=True) -> None:
        """
        Adds cover art to MP3 files based on matching image files in the specified directory.
        Matches are found by filename (default) or by using a template string
        :param covers_dir: Directory containing cover images. Default is the directory of the MP3 files
        :param template_str: A string containing a template for the name of the cover art (with the default
                             being to search for matching file names).
                             ex: f"{Tag.TITLE} - {Tag.ARTIST}".
                             Note: Templates should not have a file extension at the end
        :param search_subfolders: Whether to include subfolders in the search
        :param show_output: Whether to show the console output
        """

        if covers_dir is None:
            covers_dir = self._directory
        if not isinstance(template_str, str):
            raise exception.InvalidTemplateStringError(f"Template must be a string. Invalid template: {template_str}")
        tag_list = tag.get_tag_list(string=False)
        for mp3_path in self._list:
            if template_str == COVER_FROM_FILENAME:
                cover_file = util.filename_no_extension(mp3_path)
            else:
                cover_file = self._new_name_from_template(mp3_path, template_str, tag_list, rename_invalid=False)
            cover_path: str = EasyMP3._find_cover_from_file(cover_file, covers_dir, search_subfolders)
            if cover_path is None:
                print(f"Cover Not Found for: {mp3_path}", file=sys.stderr)
            else:
                EasyMP3._apply_cover_art(mp3_path, cover_path)
                if show_output:
                    print(f"Cover Art successfully applied to '{mp3_path}' using file '{cover_path}'")

    def set_filename_from_tags(self, template_str: str, copy=False, rename_invalid=True, show_output=True) -> None:
        """
        Renames all the MP3 filenames with their tags by using a template.
        :param template_str: A string representing how to format the new file name.
                         ex. f"{Tag.TITLE} - {Tag.ARTIST}"
                         Note: A template should never end with .mp3 as this is
                         implied
        :param copy: A boolean variable to control whether the files are moved or copied
        :param rename_invalid: A boolean variable to control whether to automatically
                         rename invalid filenames or have the user rename them as they
                         occur
        :param show_output: Whether to show the console output
        """
        util.check_template(template_str)
        tag_list = tag.get_tag_list(string=False)

        for mp3_path in self._list:
            parent_path = os.path.dirname(mp3_path)
            new_name = self._new_name_from_template(mp3_path, template_str, tag_list, rename_invalid)

            new_mp3_path = os.path.join(parent_path, new_name) + ".mp3"

            base_path = os.path.dirname(new_mp3_path)
            os.makedirs(base_path, exist_ok=True)

            if copy:
                #  copy and keep metadata
                shutil.copy2(mp3_path, new_mp3_path)
                if show_output:
                    print(f"Successfully copied '{mp3_path}' to {new_mp3_path}")
            else:
                shutil.move(mp3_path, new_mp3_path)
                if show_output:
                    print(f"Successfully moved '{mp3_path}' to {new_mp3_path}")

        self._reload_directory()

    def set_tags_from_filename(self, template_str: str, show_output=True) -> None:
        """
        Sets tags for all the MP3s based on their filename by using a provided template
        :param template_str: A string representing how to extract the tags.
                         ex. f"{Tag.TITLE} - {Tag.ARTIST}"
                         Note: A template should never end with .mp3 as this is implied
        :param show_output: Whether to show the console output
        """
        util.check_template(template_str)
        for mp3_path in self._list:
            file_name_no_extension = util.filename_no_extension(mp3_path)
            template_dict = util.extract_info(template_str, file_name_no_extension)
            if template_dict is None:
                if show_output:
                    print(f"MP3 file with path '{mp3_path}' does not match the template string and will be skipped")
                continue
            audio = self._construct_easy_id3(mp3_path)
            for key, value in template_dict.items():
                checked_key = tag.check_tag_key(key)
                audio[checked_key] = value
            audio.save()
            print(f"Tags from template string successfully applied to MP3 file with path '{mp3_path}'")

    def set_tags_from_dict(self, template_dict: dict[Tag, str], show_output=True) -> None:
        """
        Sets the same tags for all MP3 files based on a template dictionary.
        :param template_dict - A dictionary containing `Tag` keys and string values
        :param show_output: Whether to show the console output
        :raise KeyError if no valid tags are found
        :raise InvalidTemplateDictError if the template dictionary has incorrect types or values
        """

        cover_art_key = False  # If cover art was in the template

        if Tag.COVER_ART in template_dict:
            cover_art_key = True
            covers_info = template_dict.pop(Tag.COVER_ART)
            if isinstance(covers_info, str) and util.is_image(covers_info):
                #  put same image for all
                for mp3_path in self._list:
                    self._apply_cover_art(mp3_path, covers_info)
            else:
                raise exception.InvalidTemplateDictError(
                    f"The value for key {Tag.COVER_ART} must be a string representing"
                    f"a path to a cover art image.\nInvalid value: {covers_info}")
        valid_tags_dict = dict()

        for key, value in template_dict.items():

            checked_key = tag.check_tag_key(key)
            if checked_key is not None:
                valid_tags_dict[checked_key] = value
                if not isinstance(value, str):
                    raise exception.InvalidTemplateDictError(f"The value for key {key} must be a string."
                                                             f"\nInvalid value: {value}")
        if not valid_tags_dict and not cover_art_key:
            raise exception.NoValidKeysError(f"No valid keys found for template dictionary: {template_dict}")

        for mp3_path in self._list:
            audio = self._construct_easy_id3(mp3_path)
            for key, value in valid_tags_dict.items():
                audio[key] = value
            audio.save()
            if show_output:
                print(f"Tags from template dictionary successfully applied to MP3 with path '{mp3_path}'")

    def extract_cover_arts(self, folder_path: str, template_str: str = f"{Tag.TITLE}",
                           rename_invalid=True, show_output=True) -> None:
        """
        Extracts the cover arts for all MP3 files
        :param folder_path: A string representing the directory for the extracted cover arts
        :param template_str: A string representing how each extracted cover art should be named.
                            ex. f"{Tag.TITLE} - {Tag.ARTIST}".
                            - Tags can also create new directories used to group cover arts.
                                Ex. f"{Tag.ARTIST}\\{Tag.TITLE}"
                                - This will create a folder for each artist with their cover art images
                                    inside.
                            - the default is the filename of the original mp3
        :param rename_invalid: Whether to automatically rename invalid filenames or to prompt
                            the user for a new name every time an invalid filename is found
        :param show_output: Whether to show the console output
        """
        tag_list = tag.get_tag_list(string=False)
        os.makedirs(folder_path, exist_ok=True)
        for mp3_path in self._list:
            cover_name_no_extension = self._new_name_from_template(mp3_path, template_str, tag_list, rename_invalid)
            dest_path_no_extension = os.path.join(folder_path, cover_name_no_extension)
            util.extract_cover_art(mp3_path, dest_path_no_extension, show_output)

    def _new_name_from_template(self, mp3_path: str, template: str, tag_list: list[Tag], rename_invalid: bool) -> str:
        """
        Internal method that parses template strings based on the tags of an MP3 file
        :param mp3_path: The path to the mp3 file
        :param template: A traditional string template. Ex. f"{Tag.TITLE}"
        :param tag_list: A list of tags from the Tag class
        :param rename_invalid: Whether to rename invalid files automatically or prompt the user
        """
        audio = self._construct_easy_id3(mp3_path)
        new_name = template
        for _tag in tag_list:
            new_val = audio.get(_tag.value, f"NO{_tag.name}")

            if isinstance(new_val, list):
                new_val = util.list_to_str(new_val)
            new_val_translated = new_val.translate(INVALID_CHAR_TRANS)
            if rename_invalid:
                new_val = new_val_translated
            elif not util.is_valid_sub_file_name(new_val) and _tag.name in new_name:
                new_val = util.get_valid_replacement(new_val)
                print()

            if new_val != new_val_translated:
                pass
            new_name = new_name.replace(_tag.name, new_val)
        return new_name

    def _reload_directory(self) -> None:
        """
        Internal method that resets the list of paths to mp3 files. Used after filenames are changed
        """
        self._list = util.get_all_mp3s(self._directory, self._search_sub)

    @staticmethod
    def _apply_cover_art(mp3_path: str, cover_path: str):
        """
        An internal method that adds cover art to a single MP3 file
        :param mp3_path: Path to the MP3 file.
        :param cover_path: Path to the cover image.
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
        :return: The path to the cover art or None if one is not found
        """
        files = util.get_all_files(covers_dir, search_subfolders)

        for file in files:
            file_no_extension = util.filename_no_extension(file)
            if file_no_extension.lower().strip() == song_name.lower().strip() and util.is_image(file):
                return file
        return None

    @staticmethod
    def _construct_easy_id3(path: str) -> EasyID3:
        """
        Constructs an EasyID3 object for the given file path, creating new tags if necessary.
        :param path: Path to the MP3 file.
        :return: An EasyID3 object for the file.
        """

        try:
            return EasyID3(path)
        except ID3NoHeaderError:
            audio_tags = EasyID3()
            audio_tags.save(path)
            return EasyID3(path)

    @property
    def mp3_list(self) -> list[str]:
        return self._list

    @property
    def mp3s_directory(self) -> str:
        return self._directory

    @property
    def include_subfolders(self) -> bool:
        return self._search_sub
