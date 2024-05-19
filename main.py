from easymp3 import EasyMP3
from tag import Tag


def main():
    songs_dir = "mp3s"
    covers_dir = songs_dir

    artist = "Juice WRLD"
    album = "Unreleased (Mastered)"

    tagger = EasyMP3(songs_dir, search_subfolders=False)

    template = f"{Tag.TITLE} - {Tag.ARTIST} - {Tag.ALBUM}"
    tagger.set_filename_from_tags(template)


    # tagger.remove_all_tags()


if __name__ == "__main__":
    main()
