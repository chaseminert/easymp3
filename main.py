from easymp3 import EasyMP3

def main():
    mp3_path = r"mp3s"
    covers_path = r"mp3s/Cover Art"

    artist = "Juice WRLD"
    album = "Unreleased - Mastered"

    easy_mp3 = EasyMP3(mp3_path)
    easy_mp3.set_title_from_file_all()
    easy_mp3.set_artist_all(artist)
    easy_mp3.set_album_artist_all(artist)
    easy_mp3.set_album_all(album)
    easy_mp3.set_cover_art_from_file_all(covers_path)


if __name__ == "__main__":
    main()
