# Easy MP3

Easy MP3 is a python library that allows people with little python experience to manipulate 
their MP3 files and tag them in a programmatic way. This library is essentially a wrapper around 
mutagen which has much simpler functions and expanded functionality.

## Usage Examples

### Creating A Tagger Object

```python
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
tagger = EasyMP3(songs_directory, search_subfolders=True)
```
This will create a tagger object that contains the paths to all MP3 files in the given directory
including MP3 files in subfolders of the directory.

### Using String Templates

String templates can be created by using f strings and passing constants from the `Tag` class.
For example:
```python
from easymp3 import Tag

file_name_template = f"{Tag.TITLE} - {Tag.ARTIST}"
```
### Setting Tags From Filenames
String templates can be used to set tags from the filename.

This will set the filename for all MP3 files in the tagger object.
Ex. `Fast - Juice WRLD.mp3`.

```python
from easymp3 import EasyMP3, Tag

songs_directory = r"path\to\songs"
tagger = EasyMP3(songs_directory, search_subfolders=True)

file_name_template = f"{Tag.TITLE} - {Tag.ARTIST}"
tagger.set_filename_from_tags(file_name_template)
```

### Setting Filenames From Tags
String templates can also be used to set the filenames from the tags.

For all MP3 files in the tagger object that are correctly formatted, their title
and artist will be set accordingly. Ex. If the file is named `Fast - Juice WRLD.mp3`
then the title will be set to Fast and the artist will be set to Juice WRLD.
```python
from easymp3 import EasyMP3, Tag

songs_directory = r"path\to\songs"
tagger = EasyMP3(songs_directory, search_subfolders=True)

file_name_template = f"{Tag.TITLE} - {Tag.ARTIST}"
tagger.set_tags_from_filename(file_name_template)
```

### Setting Cover Arts

By specifying a directory for cover art images, cover arts can be set for each MP3 file
in the tagger object.

This will set the cover arts for every MP3 file in the tagger object if
it is found. For example, if an MP3 is titled `Fast.mp3` and there is a file
in `covers_path` titled `Fast.png`, then that image will be set as the front
cover art for `Fast.mp3`.
```python
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
covers_path = r"path\to\covers"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.set_cover_art(covers_path)
```
<br>
Cover arts can also be set by using a string template that represents
how the cover images are named.

This will set the cover for all images that match the template.
For example, if an MP3 file is tagged such that the title is Fast
and the artist is Juice WRLD, then if an image file exists with
the name `Fast - Juice WRLD`, then that image will be set as the 
front cover image.
```python
from easymp3 import EasyMP3, Tag

songs_directory = r"path\to\songs"
covers_path = r"path\to\covers"
template_str = f"{Tag.TITLE} - {Tag.ARTIST}"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.set_cover_art(covers_path, template_str)
```
### Extracting Cover Arts
This will extract the cover arts for all MP3 files in the tagger object
and name them by the filename of the original MP3 file. For example, if an
MP3 file is named `Fast - Juice WRLD.mp3`, then the cover image will be named
`Fast - Juice WRLD.png` (the extension can vary)

```python
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
extracted_covers_path = r"path\to\covers"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.extract_cover_arts(extracted_covers_path)
```

The filenames for extracted cover arts can also be set by using a string template.

This will set all the extracted cover images as the template. For example, if MP3
file is tagged such that the title is Fast and the artist is Juice WRLD, then the
extracted cover image will be named `Fast - Juice WRLD.png` (the extension can vary)

```python
from easymp3 import EasyMP3, Tag

songs_directory = r"path\to\songs"
extracted_covers_path = r"path\to\covers"
template_str = f"{Tag.TITLE} - {Tag.ARTIST}"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.extract_cover_arts(extracted_covers_path, template_str)
```

### Removing All Tags

This will remove all tags from all MP3 files in the tagger object.

```python
from easymp3 import EasyMP3, Tag

songs_directory = r"path\to\songs"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.remove_all_tags()
```


