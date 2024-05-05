import mimetypes
import os


def is_mp3(file_path: str):
    return os.path.isfile(file_path) and file_path.endswith(".mp3")

def is_image(file_path: str) -> bool:
    return os.path.isfile(file_path) and "image" in get_mime_type(file_path)

def no_filter(_):
    return True


def get_all_mp3s(directory: str, search_subfolders):
    if is_mp3(directory):
        return [directory]
    elif os.path.isdir(directory):
        return get_all_files(directory, search_subfolders, is_mp3)
    else:
        raise TypeError(f"\"{directory}\" is neither an MP3 file nor a directory")


def get_all_files(directory: str, search_subfolders, filter_func=no_filter):
    files = []

    if search_subfolders:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                path = os.path.join(root, filename)
                if filter_func(path):
                    files.append(path)
    else:
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)
            if filter_func(path):
                files.append(path)

    return files

def filename_no_extension(file_path: str):
    base_filename = os.path.basename(file_path)
    # Split the filename from its extension
    filename_without_ext, _ = os.path.splitext(base_filename)
    return filename_without_ext

def get_mime_type(path):
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        raise TypeError(f"Invalid mime type for path: {path}")
    else:
        return mime_type



