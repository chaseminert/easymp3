from easymp3 import EasyMP3
from tags import Tags


def main():
    songs_path = "mp3s"
    covers_path = r"mp3s"
    artist = "Test"
    album = "Unreleased (Mastered)"

    easy_mp3 = EasyMP3(songs_path, search_subfolders=True)
    # easy_mp3.set_title_from_file()
    # easy_mp3.remove_all_tags()
    # easy_mp3.set_tag(Tags.ARTIST, "Juice WRLD")
    easy_mp3.set_cover_art_from_file(covers_path)
    # easy_mp3.set_tag(Tags.ARTIST, artist)


if __name__ == "__main__":
    main()
