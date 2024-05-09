import sys
from enum import Enum


class Tag(Enum):
    ALBUM = 'album'
    BPM = 'bpm'
    COMPILATION = 'compilation'
    COMPOSER = 'composer'
    COPYRIGHT = 'copyright'
    ENCODEDBY = 'encodedby'
    LYRICIST = 'lyricist'
    LENGTH = 'length'
    MEDIA = 'media'
    MOOD = 'mood'
    GROUPING = 'grouping'
    TITLE = 'title'
    VERSION = 'version'
    ARTIST = 'artist'
    ALBUMARTIST = 'albumartist'
    CONDUCTOR = 'conductor'
    ARRANGER = 'arranger'
    DISCNUMBER = 'discnumber'
    ORGANIZATION = 'organization'
    TRACKNUMBER = 'tracknumber'
    AUTHOR = 'author'
    ALBUMARTISTSORT = 'albumartistsort'
    ALBUMSORT = 'albumsort'
    COMPOSERSORT = 'composersort'
    ARTISTSORT = 'artistsort'
    TITLESORT = 'titlesort'
    ISRC = 'isrc'
    DISCSUBTITLE = 'discsubtitle'
    LANGUAGE = 'language'
    GENRE = 'genre'
    DATE = 'date'
    ORIGINALDATE = 'originaldate'
    PERFORMER = 'performer:*'
    MUSICBRAINZ_TRACKID = 'musicbrainz_trackid'
    WEBSITE = 'website'
    REPLAYGAIN_TRACK_GAIN = 'replaygain_track_gain'
    REPLAYGAIN_TRACK_PEAK = 'replaygain_track_peak'
    MUSICBRAINZ_ARTISTID = 'musicbrainz_artistid'
    MUSICBRAINZ_ALBUMID = 'musicbrainz_albumid'
    MUSICBRAINZ_ALBUMARTISTID = 'musicbrainz_albumartistid'
    MUSICBRAINZ_TRMID = 'musicbrainz_trmid'
    MUSICIP_PUID = 'musicip_puid'
    MUSICIP_FINGERPRINT = 'musicip_fingerprint'
    MUSICBRAINZ_ALBUMSTATUS = 'musicbrainz_albumstatus'
    MUSICBRAINZ_ALBUMTYPE = 'musicbrainz_albumtype'
    RELEASECOUNTRY = 'releasecountry'
    MUSICBRAINZ_DISCID = 'musicbrainz_discid'
    ASIN = 'asin'
    BARCODE = 'barcode'
    CATALOGNUMBER = 'catalognumber'
    MUSICBRAINZ_RELEASETRACKID = 'musicbrainz_releasetrackid'
    MUSICBRAINZ_RELEASEGROUPID = 'musicbrainz_releasegroupid'
    MUSICBRAINZ_WORKID = 'musicbrainz_workid'
    ACOUSTID_FINGERPRINT = 'acoustid_fingerprint'
    ACOUSTID_ID = 'acoustid_id'

    # Custom

    COVER_ART = "cover_art"


def check_tag_key(tag_key: Tag | str):
    try:
        Tag(tag_key)
        if isinstance(tag_key, str):
            return tag_key
        else:
            return tag_key.value

    except ValueError:
        print(f"Invalid mp3 metadata field: {tag_key}", file=sys.stderr)
        return None
