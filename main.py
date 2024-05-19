from easymp3 import EasyMP3
from tag import Tag


def main():
    songs_dir = "mp3s"
    covers_dir = songs_dir

    artist = "Juice WRLD"
    album = "Unreleased (Mastered)"

    template = {
        Tag.ARTIST: artist,
        Tag.ALBUM: album,
        Tag.COVER_ART: (f"{Tag.TITLE} - {Tag.ARTIST}", covers_dir, True)
    }

    tagger = EasyMP3(songs_dir, search_subfolders=False)

    tagger.set_tags_from_template(template)

    # tagger.remove_all_tags()


if __name__ == "__main__":
    main()
