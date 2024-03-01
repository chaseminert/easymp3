import mimetypes

from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4, MP4Cover, AtomDataType

from easymp3 import EasyMP3
from mutagen.mp3 import MP3

def main():
    cover_path = "mp3s/Cover Art/Already.png"
    m4a_path = "mp3s/Already.m4a"
    EasyMP3._set_m4a_art_from_file(m4a_path, cover_path)




if __name__ == "__main__":
    main()
