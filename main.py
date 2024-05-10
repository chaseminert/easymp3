from easymp3 import EasyMP3
from tag import Tag


def main():
    songs_path = "mp3s"
    covers_path = "mp3s/Cover Art"
    test_cover_path = "mp3s/Cover Art/Fenty Edit.mp3"
    artist = "Juice WRLD"
    album = "Unreleased (Mastered)"

    template = {
        Tag.TITLE: EasyMP3.TITLE_FROM_FILE,
        Tag.ARTIST: artist,
        Tag.ALBUMARTIST: artist,
        Tag.ALBUM: album,
        Tag.COVER_ART: (covers_path, "your mom")
    }

    easy_mp3 = EasyMP3(songs_path, search_subfolders=True)
    easy_mp3.set_tags(template)
    # easy_mp3.remove_all_tags()
    # easy_mp3.set_tags(template)
    #
    # easy_mp3.set_tag(Tag.COVER_ART, test_cover_path)
    # easy_mp3.set_cover_art_from_file(covers_path)
    # easy_mp3.set_tag(Tag.COVER_ART, test_cover_path)


if __name__ == "__main__":
    main()
