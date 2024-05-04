import mimetypes
import os
import sys

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, PictureType, ID3NoHeaderError

import util
from keys import MP3Keys


class EasyMP3:

    def __init__(self, directory: str, instant_save=True, search_subfolders=True):

        self._instant_save = instant_save

        self._list: list[EasyID3] = list()

        mp3_files = util.get_all_mp3s(directory, search_subfolders)

        for file in mp3_files:
            try:
                audio = EasyID3(file)
            except ID3NoHeaderError:
                tags = EasyID3()
                tags.save(file)
                audio = EasyID3(file)

            self._list.append(audio)

    def set_artist(self, new_artist):
        self._set_tag(MP3Keys.ARTIST, lambda audio: new_artist)

    def set_album_artist(self, new_album_artist):
        self._set_tag(MP3Keys.ALBUMARTIST, lambda audio: new_album_artist)

    def set_album(self, new_album):
        self._set_tag(MP3Keys.ALBUM, lambda audio: new_album)

    def set_title_from_file(self):
        self._set_tag(MP3Keys.TITLE, lambda audio: audio.filename)

    def save_all(self):
        if self._instant_save:
            return

        for audio in self._list:
            audio.save()

    def set_cover_art_from_file(self, covers_dir, search_subfolders=True):
        for audio in self._list:
            file_name: str = audio.filename
            cover_path: str = EasyMP3._find_cover_from_file(file_name, covers_dir, search_subfolders)
            if cover_path is None:
                print(f"Cover Not Found for: {file_name}", file=sys.stderr)
            else:
                EasyMP3._apply_cover_art(audio, cover_path)
                if self._instant_save:
                    audio.save()

    def set_tag(self, key: MP3Keys, value: str):
        self._set_tag(key, lambda audio: value)

    def _set_tag(self, key: MP3Keys, new_val_func):
        for audio in self._list:
            audio[key] = new_val_func(audio)
            if self._instant_save:
                audio.save()

    @staticmethod
    def _apply_cover_art(audio: EasyID3, cover_path: str):
        mime_type, _ = mimetypes.guess_type(cover_path)
        if mime_type is None:
            raise TypeError(f"Invalid mime type for path: {cover_path}")
        with open(cover_path, 'rb') as img:
            cover_data = img.read()

        apic = APIC(encoding=3, mime=mime_type, type=PictureType.COVER_FRONT, desc='Cover', data=cover_data)
        audio["APIC"] = apic

    @staticmethod
    def _find_cover_from_file(song_name: str, covers_dir: str, search_subfolders) -> str | None:
        files = util.get_all_files(covers_dir, search_subfolders)

        for file in files:
            file_no_extension = os.path.splitext(file)
            if file_no_extension.lower() == song_name.lower():
                file_path = os.path.join(covers_dir, file)
                return file_path
