from easymp3 import EasyMP3

def main():
    mp3_path = r"C:\Users\Chase Minert\Documents\Side Projects\Learning Python\mp3-tag\mp3s"
    easy_mp3 = EasyMP3(mp3_path)
    easy_mp3.set_album("Test")



if __name__ == "__main__":
    main()
