# EasyMP3

EasyMP3 is a Python library designed for individuals with limited Python experience to easily manipulate and tag their MP3 files programmatically. This library is a simplified wrapper around the mutagen library, providing simpler functions and expanded functionality.

## Installation and Usage
### Prerequisites
- Python 3.x

### Installation
```bash
pip install easymp3
```

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

String templates can be created using f strings and passing constants from the `Tag` class.
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
then the title will be set to Fast, and the artist will be set to Juice WRLD.
```python
from easymp3 import EasyMP3, Tag

songs_directory = r"path\to\songs"
tagger = EasyMP3(songs_directory, search_subfolders=True)

file_name_template = f"{Tag.TITLE} - {Tag.ARTIST}"
tagger.set_tags_from_filename(file_name_template)
```

### Copying Tags To Other MP3 Files
For all MP3 files in the tagger object, their tags will be extracted to existing MP3
files (of the same filename) in a specified directory. Ex. for all MP3 files in `songs_directory`,
their tags will be copied to a file of the same name in `copy_directory`.

```python
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
copy_directory = r"path\to\other\directory"

tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.copy_tags(copy_directory)
```

### Setting Cover Arts

#### From Filename

By specifying a directory for cover art images, cover art can be set for each MP3 file
in the tagger object.

This will set the cover art for every MP3 file in the tagger object if
it is found. For example, if an MP3 is titled `Fast.mp3` and there is a file
in `covers_path` titled `Fast.png,` that image will be set as the front
cover art for `Fast.mp3`.
```python
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
covers_path = r"path\to\covers"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.set_cover_art(covers_path)
```
#### From A Template

Cover art can also be set by using a string template that represents
how the cover images are named.

This will set the cover for all images that match the template.
For example, if an MP3 file is tagged such that the title is Fast
and the artist is Juice WRLD, then if an image file exists with
the name `Fast - Juice WRLD,` that image will be set as the 
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

#### From Filename
This will extract the cover art for all MP3 files in the tagger object
and name them using the filename of the original MP3 file. For example, if an
MP3 file is named `Fast - Juice WRLD.mp3`, then the cover image will be named
`Fast - Juice WRLD.png` (the extension can vary)

```python
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
extracted_covers_path = r"path\to\covers"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.extract_cover_arts(extracted_covers_path)
```

#### From A Template
The filenames for extracted cover art can also be set using a string template.

This will set all the extracted cover images as the template. For example, if MP3
file is tagged such that the title is Fast and the artist is Juice WRLD, then the
the extracted cover image will be named `Fast - Juice WRLD.png` (the extension can vary)

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
from easymp3 import EasyMP3

songs_directory = r"path\to\songs"
tagger = EasyMP3(songs_directory, search_subfolders=True)

tagger.remove_all_tags()
```

## Key Features
- **String Templates**: Use string templates to set filenames from tags, set tags from filenames, export cover arts, and set cover arts from files.
- **Simplicity**: EasyMP3 simplifies the MP3 tagging and manipulation process, making it accessible to users with little Python experience.
- **Expanded Functionality**: Built on top of mutagen, EasyMP3 extends its capabilities with more user-friendly functions.

## Libraries Used
- **Mutagen**: For MP3 file manipulation.
- **re (Regular Expressions)**: For implementing string templates.

## Challenges Overcome
- **Reusable Code**: Faced difficulties in writing reusable code, which led to frequent refactoring. Overcame this by creating a util module with general-purpose functions, some of which accept other functions as parameters for versatility.
- **String Templates**: Implementing string templates with regular expressions was challenging. Solved this by studying the python regex library (re) documentation and using regex templates like `f'(?P<{attribute}>.+)`.
- **Feature-Rich Yet Simple**: Balancing a feature-rich library with simplicity was tough. Introduced multiple default parameters for functions and rigorously documented them to maintain simplicity while offering expanded functionality.
- **Documentation**: Initially struggled with professional documentation. Researched and adopted the reStructuredText style, replicating its format for EasyMP3's documentation.

## Overall Impact and Significance
EasyMP3 allows users to quickly create powerful scripts utilizing its features without needing to delve into the complexities of the mutagen library. This significantly lowers the barrier for users looking to manage their MP3 collections programmatically.


## Contribution
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License.
