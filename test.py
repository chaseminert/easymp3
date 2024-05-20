import mimetypes

from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4, MP4Cover, AtomDataType

import tag
import util
from easymp3 import EasyMP3
from mutagen.mp3 import MP3

from tag import Tag


def main():
    mp3_path = r"mp3s\6 Kiss.mp3"
    dest_dir = r"mp3s\6 Kiss"
    util.extract_cover_art(mp3_path, dest_dir)


if __name__ == "__main__":
    main()
