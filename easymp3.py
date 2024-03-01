import enum
import mimetypes
import os
from enum import Enum

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover

from keys import MP3Keys, M4AKeys


class AudioType(Enum):
    MP3 = enum.auto()
    M4A = enum.auto()


class EasyMP3:

    def __init__(self, directory):
        self._list: list[str] = []
        self._get_list(directory)


    def _get_list(self, directory):
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            audio_type = EasyMP3._get_audio_type(path)
            if audio_type != AudioType.MP3 and audio_type != AudioType.M4A:
                continue
            self._list.append(path)

    def _set_tag(self, keys, new_val_func):
        mp3key, m4akey = keys
        for path in self._list:
            audio_type = EasyMP3._get_audio_type(path)
            audio: EasyID3 | MP4 = EasyMP3._construct_audio_obj(audio_type, path)
            if audio_type == AudioType.MP3:
                key = mp3key
            else:
                key = m4akey
            new_val = new_val_func(path)
            audio[key] = new_val
            audio.save()

    def set_artist_all(self, new_artist):
        keys = (MP3Keys.ARTIST, M4AKeys.ARTIST)
        self._set_tag(keys, lambda path: new_artist)

    def set_album_artist_all(self, new_album_artist):
        keys = (MP3Keys.ALBUMARTIST, M4AKeys.ALBUMARTIST)
        self._set_tag(keys, lambda path: new_album_artist)

    def set_album_all(self, new_album):
        keys = (MP3Keys.ALBUM, M4AKeys.ALBUM)
        self._set_tag(keys, lambda path: new_album)

    def set_title_all(self, new_title):
        keys = (MP3Keys.TITLE, M4AKeys.TITLE)
        self._set_tag(keys, lambda path: new_title)

    def set_title_from_name_all(self):
        keys = [MP3Keys.TITLE, M4AKeys.TITLE]
        self._set_tag(keys, lambda path: self._get_filename(path, extension=False))

    def set_cover_art_from_file_all(self, covers_dir):
        for path in self._list:
            cover_path = EasyMP3._find_cover_from_file(path, covers_dir)
            if cover_path is None:
                print(f"Cover Not Found for: {path}")
                continue
            EasyMP3._set_art_from_file(path, cover_path)

    @staticmethod
    def _set_mp3_art_from_file(mp3_path: str, cover_path: str):
        mp3_obj: MP3 = MP3(mp3_path, ID3=ID3)
        if mp3_obj.tags is None:
            mp3_obj.add_tags()
        mp3_obj.tags.delall("APIC")
        mp3_obj.save()

        mime_type, _ = mimetypes.guess_type(cover_path)
        if mime_type is None:
            raise ValueError(f"Invalid mime type for path: {cover_path}")
        with open(cover_path, 'rb') as img:
            cover_data = img.read()

        apic = APIC(encoding=3, mime=mime_type, type=3, desc='Cover', data=cover_data)
        mp3_obj.tags.add(apic)
        mp3_obj.save()

    @staticmethod
    def _set_m4a_art_from_file(m4a_path: str, cover_path: str):
        mime_type, _ = mimetypes.guess_type(cover_path)
        if mime_type is None:
            raise ValueError(f"Invalid mime type for path: {cover_path}")
        if mime_type == 'image/jpeg':
            image_format = MP4Cover.FORMAT_JPEG
        elif mime_type == 'image/png':
            image_format = MP4Cover.FORMAT_PNG
        else:
            raise ValueError(f"Unsupported image format for: {cover_path}")
        m4a_obj = MP4(m4a_path)
        with open(cover_path, 'rb') as f:
            cover_data = f.read()
        new_cover = MP4Cover(cover_data, imageformat=image_format)
        m4a_obj.tags[M4AKeys.COVER_ART] = [new_cover]
        m4a_obj.save()

    @staticmethod
    def _set_art_from_file(audio_path: str, cover_path: str):
        audio_type = EasyMP3._get_audio_type(audio_path)
        if audio_type == AudioType.MP3:
            EasyMP3._set_mp3_art_from_file(audio_path, cover_path)
        elif audio_type == AudioType.M4A:
            EasyMP3._set_m4a_art_from_file(audio_path, cover_path)
        else:
            raise ValueError(f"File path: {audio_path} is invalid. Audio can only be mp3 or m4a")

    @staticmethod
    def _get_filename(path: str, extension=True):
        base_name = os.path.basename(path)
        if extension:
            return base_name
        name_without_extension, _ = os.path.splitext(base_name)
        return name_without_extension

    @staticmethod
    def _get_audio_type(path: str):
        if path.lower().endswith("mp3"):
            return AudioType.MP3
        elif path.lower().endswith("m4a"):
            return AudioType.M4A

    @staticmethod
    def _construct_audio_obj(audio_type: AudioType, path):
        if audio_type == AudioType.MP3:
            return EasyID3(path)
        else:
            return MP4(path)

    @staticmethod
    def _find_cover_from_file(song_path: str, covers_dir: str):
        song_name = EasyMP3._get_filename(song_path, extension=False)
        for file in os.listdir(covers_dir):
            file_no_extension = EasyMP3._get_filename(file, extension=False)
            if file_no_extension.lower() == song_name.lower():
                file_path = os.path.join(covers_dir, file)
                return file_path
        return None
