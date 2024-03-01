from easymp3 import EasyMP3

def main():
    mp3_path = r"mp3s"
    covers_path = r"mp3s/Cover Art"
    easy_mp3 = EasyMP3(mp3_path)
    easy_mp3.set_cover_art_from_file_all(covers_path)


if __name__ == "__main__":
    main()
