import mimetypes
import os

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover

from keys import MP3Keys, M4AKeys


class EasyMP3:

    def __init__(self, directory):
        self._mp3_list: list[EasyID3] = []
        self._m4a_list: list[MP4] = []
        self._get_list(directory)

    def _get_list(self, directory):
        for file in os.listdir(directory):
            path = os.path.join(directory, file)
            is_mp3 = file.endswith("mp3")
            is_m4a = file.endswith("m4a")
            if not is_mp3 and not is_m4a:
                continue
            if is_mp3:
                self._mp3_list.append(EasyID3(path))
            elif is_m4a:
                self._m4a_list.append(MP4(path))
        self._combo_list = [self._mp3_list, self._m4a_list]

    def _set_tag(self, keys, new_val_func):
        for _list, key in zip(self._combo_list, keys):
            for item in _list:
                new_val = new_val_func(item)
                item[key] = new_val
                item: EasyID3
                item.save()

    def set_artist(self, new_artist):
        keys = [MP3Keys.ARTIST, M4AKeys.ARTIST]
        self._set_tag(keys, lambda: new_artist)

    def set_album_artist(self, new_album_artist):
        keys = [MP3Keys.ALBUMARTIST, M4AKeys.ALBUMARTIST]
        self._set_tag(keys, lambda item: new_album_artist)

    def set_album(self, new_album):
        keys = [MP3Keys.ALBUM, M4AKeys.ALBUM]
        self._set_tag(keys, lambda item: new_album)

    def set_title(self, new_title):
        keys = [MP3Keys.TITLE, M4AKeys.TITLE]
        self._set_tag(keys, lambda item: new_title)

    def set_title_from_name(self):
        keys = [MP3Keys.TITLE, M4AKeys.TITLE]
        self._set_tag(keys, lambda item: self._get_filename(item.filename, extension=False))

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
    def _get_filename(path: str, extension=True):
        base_name = os.path.basename(path)
        if extension:
            return base_name
        name_without_extension, _ = os.path.splitext(base_name)
        return name_without_extension
