import mimetypes

from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4, MP4Cover, AtomDataType

import tag
import util
from easymp3 import EasyMP3
from mutagen.mp3 import MP3

from tag import Tag


def main():
    template = f"{Tag.ARTIST} - {Tag.TITLE}"
    song = "Black and White - Juice WRLD"


    song_info = util.extract_info(template, song)
    print(song_info)



if __name__ == "__main__":
    main()
