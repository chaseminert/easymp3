from easymp3 import EasyMP3

def main():
    songs_path = "mp3s"
    covers_path = r"C:\Users\Chase Minert\Documents\Music Backup\New Songs\New Cover Art"

    artist = "Your Mom"
    album = "Unreleased (Mastered)"

    easy_mp3 = EasyMP3(songs_path, search_subfolders=False)

    easy_mp3.set_artist(artist)


if __name__ == "__main__":
    main()

