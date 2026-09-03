"""Reader for Bulánci ``.eap`` map files.

Container
---------
The file is a chunked-zlib archive.

======  =========  ==================================================
offset  type       meaning
======  =========  ==================================================
0x00    char[4]    ``GZIP``
0x04    uint32     offset of the trailing seek index (= end of chunks)
0x08    uint32     0
0x0c    ...        payload split into 32 KiB chunks, each one its own
                   zlib stream, or stored raw when deflate did not
                   shrink it
end+0   uint32     total uncompressed size
end+4   uint32     0
end+8   uint32     compressed size of the seek index
end+12  ...        zlib stream of uint64 file offsets, one per chunk
                   plus a terminator
======  =========  ==================================================

Payload
-------
The decompressed payload opens with a resource table::

    uint32 resource_count
    uint32 8                        (constant)
    resource_count * {
        uint32 flags                (always 90)
        uint32 id                   (always 100000 + index)
        uint32 type
        uint32 offset               (relative to 8 + count*24 + 4)
        uint32 0
        uint32 size
    }

Resource types: See ResourceType enum.
"""
import io
import struct
import sys
import warnings
import zlib
from contextlib import suppress
from dataclasses import dataclass, field
from enum import Flag, IntEnum, auto
from itertools import pairwise
from pathlib import Path
from typing import TYPE_CHECKING

from mutagen.mp3 import MP3
from PIL import Image

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

CHUNK = 32768


class ResourceType(IntEnum):
    """The resource types this format is known to use.

    These six are the only codes present across the whole collection, but
    the format itself is undocumented, so `resources` passes any other
    value through as a plain int rather than rejecting the map.
    """
    JPEG = 21
    BMP = 22
    SPRITE = 28
    MUSIC = 48
    INFO = 94
    SCRIPT = 2026


IMAGE_TYPES = (ResourceType.JPEG, ResourceType.BMP)


class Damage(Flag):
    """What a map file turned out to be missing, if anything.

    Maps in this collection have been sourced from the internet and some
    come broken.
    """
    NONE = 0
    CONTAINER = auto()
    '''the trailing seek index is gone: the file is cut off'''
    RESOURCE = auto()
    '''a resource's declared size runs past the payload'''
    UNPARSED = auto()
    '''a resource was too short to parse'''
    UNKNOWN = auto()
    '''a resource of a type this reader does not know'''

    def __str__(self) -> str:
        """List the set flags, lowercased: ``'container, unparsed'``."""
        return ', '.join(flag.name.lower() for flag in self if flag.name)


def _inflate(d: bytes) -> tuple[bytes, Damage]:
    """Decompress a container's payload, and say what the file is missing."""
    if d[:4] != b'GZIP':
        raise ValueError(f'not an .eap container: {d[:8]!r}')
    end = int.from_bytes(d[4:8], 'little')
    if end + 12 > len(d):
        # Truncated file: the index is gone, but chunk 0 still starts at 0x0c
        # and that is where the map info lives.  It holds one chunk at most.
        spans, unc_size, damage = [(12, len(d))], CHUNK, Damage.CONTAINER
    else:
        unc_size = int.from_bytes(d[end:end + 4], 'little')
        index = zlib.decompress(d[end + 12:])
        offs = [int.from_bytes(index[i:i + 8], 'little')
                for i in range(0, len(index), 8)]
        spans, damage = list(pairwise(offs)), Damage.NONE  # last entry terminates
    # A chunk deflate did not shrink was stored raw, at its full length.
    return b''.join(blob if len(blob) == min(CHUNK, unc_size - i * CHUNK)
                    else zlib.decompressobj().decompress(blob)
                    for i, blob in enumerate(d[a:b] for a, b in spans)), damage


@dataclass(frozen=True)
class Resource:
    type: ResourceType
    id: int
    '''always 100000 plus the entry's index'''
    data: bytes
    truncated: bool = False
    '''the table promised more bytes than the payload holds'''


def resources(payload: bytes) -> Iterator[Resource]:
    """Yield every `Resource` in a payload, in table order."""
    count = int.from_bytes(payload[:4], 'little')
    base = 8 + count * 24 + 4
    for i in range(count):
        _, rid, rtype, off, _, size = struct.unpack(
            '<6I', payload[8 + i * 24:32 + i * 24])
        with suppress(ValueError):  # an unknown code stays a raw number
            rtype = ResourceType(rtype)
        data = payload[base + off:base + off + size]
        yield Resource(rtype, rid, data, truncated=len(data) < size)


def _wstr(buf: bytes, p: int) -> tuple[str, int]:
    """Read a uint32-length-prefixed UTF-16LE string; return (text, next_pos).

    Raises ValueError if the string runs past the end of ``buf`` or declares
    an implausible length, both of which mean the resource is damaged.
    """
    n = int.from_bytes(buf[p:p + 4], 'little')
    if n > 4096:
        raise ValueError(f'implausible string length {n}')
    end = p + 4 + n * 2
    if end > len(buf):
        raise ValueError(f'resource ended {end - len(buf)} bytes early')
    return buf[p + 4:end].decode('utf-16-le'), end


def _wstrz(buf: bytes, p: int) -> tuple[str, int]:
    """Read a NUL-terminated UTF-16LE string; return (text, next_pos)."""
    end = p
    while end + 1 < len(buf) and buf[end:end + 2] != b'\x00\x00':
        end += 2
    return buf[p:end].decode('utf-16-le'), end + 2


@dataclass(frozen=True)
class MapInfo:
    """The name and author the map's creator typed into the editor.
    """
    name: str
    author: str
    unknown: int
    '''uint32 whose meaning is not established.  It is not a
    checksum (unrelated maps share values) and it rises monotonically
    with the map's age, so it behaves like an editor build or revision
    counter.  Maps by one author made around the same time share it.
    '''


def parse_info(blob: bytes) -> MapInfo:
    """Parse a type 94 resource into `MapInfo`.
    """
    if len(blob) < 4:
        raise ValueError('info resource is too short')
    name, p = _wstr(blob, 4)
    author, _ = _wstr(blob, p)
    return MapInfo(
        name=name,
        author=author,
        unknown=int.from_bytes(blob[:4], 'little')
    )


@dataclass(frozen=True)
class Script:
    """The properties held in the type 2026 stream.

    The stream is a graph of tagged records holding the map's script and
    its placed objects, and only its property records are decoded here.
    Every intact map in the collection carries exactly these three, always
    in the order 1, 2, 0.
    """
    name: str | None = None
    '''Same as what `MapInfo` holds'''
    guid: str | None = None
    '''stable map identity: re-saving or re-downloading a map
    keeps it, so it identifies the same map across copies whose bytes
    differ.'''
    unk1: int | None = None
    '''1000 in every known map'''
    extra: dict[int, str | int] = field(default_factory=dict)

_PROP = 0x0b                    # opens a property record: 0b <id> <type>
_PROP_U32, _PROP_WSTR = 0x00, 0x1b
_PROPS = bytes([_PROP, 1, _PROP_U32])  # property 1 opens the block

def parse_script(blob: bytes) -> Script:
    """Parse the property records out of a type 2026 resource.

    The record format is only partly known.  Maps come in two shapes,
    one of which opens with a record this reader cannot measure, so the
    properties are found by scanning for the block that starts with
    property 1 rather than by walking the stream from the beginning.
    """
    props: dict[int, str | int] = {}
    i = blob.find(_PROPS)
    while 0 <= i < len(blob) - 3 and blob[i] == _PROP:
        pid, ptype = blob[i + 1], blob[i + 2]
        if ptype == _PROP_U32:
            props[pid] = int.from_bytes(blob[i + 3:i + 7], 'little')
            i += 7
        elif ptype == _PROP_WSTR:
            props[pid], i = _wstrz(blob, i + 3)
        else:
            break  # a property type this reader does not know: stop here
    name, guid, unk1 = props.pop(0, None), props.pop(2, None), props.pop(1, None)
    return Script(
        name=name.strip() if isinstance(name, str) else None,
        guid=guid if isinstance(guid, str) else None,
        unk1=unk1 if isinstance(unk1, int) else None,
        extra=props
    )


def parse_sprite(blob: bytes) -> Image.Image | None:
    """Decode a type 28 resource into an RGB image, or None if it is damaged.

    Layout: uint32 width, height, 5, stride, then a 3-byte BGR colour key,
    a byte, ``ff 00 00 00``, ``01 00``, then bottom-up 24-bit BGR rows
    padded to a 4-byte stride.  Pillow's raw decoder handles this in one pass.

    The colour key the game draws as transparent is kept in the image's
    ``info['transparency']``, which is Pillow's own convention: saving as
    PNG writes it out as a tRNS chunk, and `Image.convert` to RGBA turns
    those pixels transparent.
    """
    if len(blob) < 26:
        return None
    width, height, _, stride = struct.unpack('<4I', blob[:16])
    try:
        image = Image.frombytes('RGB', (width, height), blob[26:],
                                'raw', 'BGR', stride, -1)  # -1: bottom row first
    except ValueError:
        return None
    image.info['transparency'] = (blob[18], blob[17], blob[16])  # stored BGR
    return image


@dataclass(frozen=True)
class Tags:
    """The ID3 fields recovered from a track; any of them may be missing."""
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    bitrate: int | None = None

    @property
    def track(self) -> str | None:
        """``"artist / title"``, or whichever half is known, or None."""
        return ' / '.join(p for p in (self.artist, self.title) if p) or None


@dataclass(frozen=True)
class Music:
    """The map's background music: the MP3 itself plus its declared format.

    The format fields come from the engine's own header rather than from
    the MP3. 35 maps in this collection hold audio mutagen cannot read at all.

    ``seconds`` is derived from the header's PCM size; mutagen estimates the
    length from the bitrate instead and drifts on VBR tracks, by over five
    seconds for eleven maps here.
    """
    channels: int
    bits: int
    sample_rate: int
    pcm_bytes: int
    seconds: float
    tags: Tags
    audio: bytes


def parse_music(blob: bytes) -> Music | None:
    """Parse a type 48 resource into `Music`, or None if it is too short.

    Header: uint32 data length, uint32 decoded PCM size, uint16 channels,
    uint16 bits per sample, uint32 sample rate.  The body is an MP3,
    usually with its original ID3 tags still attached.
    """
    if len(blob) < 16:
        return None
    _dlen, pcm, channels, bits, rate = struct.unpack('<IIHHI', blob[:16])
    seconds = pcm / (rate * channels * bits / 8) if rate and channels else 0.0
    audio = blob[16:]
    return Music(channels, bits, rate, pcm, seconds, read_tags(audio), audio)


def read_tags(audio: bytes) -> Tags:
    """Return the `Tags` of an MP3 blob.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            mp3 = MP3(io.BytesIO(audio))
    except Exception:
        return Tags()
    text: dict[str, str] = {}
    for frame, key in (('TIT2', 'title'), ('TPE1', 'artist'), ('TALB', 'album')):
        value = mp3.tags.get(frame) if mp3.tags else None
        if value:
            text[key] = str(value).strip()
    return Tags(bitrate=getattr(mp3.info, 'bitrate', None), **text)


def _decode_images(blobs: Iterable[bytes]) -> list[Image.Image]:
    """Decode JPEG/BMP blobs with Pillow."""
    return [Image.open(io.BytesIO(blob)) for blob in blobs]


@dataclass(frozen=True)
class MapData:
    """Everything one .eap file holds, parsed in a single pass.

    ``sprites`` are decoded, since nothing but this reader can make sense of
    a type 28 resource.  ``images`` keeps the JPEG/BMP ones undecoded, since
    scanning a collection rarely needs the pixels; call `decode_images` for
    those.

    Resources of an unrecognised type are dropped, and so are ones too
    short to parse -- truncated maps are common in this collection, and
    recovering the rest of one beats failing on all of it.  Each such loss
    is recorded in ``damage``; only a missing or unreadable `MapInfo`
    raises.
    """
    info: MapInfo
    script: Script | None
    music: Music | None
    sprites: list[Image.Image]
    images: list[Image.Image]
    path: Path | None = None
    damage: Damage = Damage.NONE

    @property
    def guid(self) -> str | None:
        """The map's stable identity, from its `Script`."""
        return self.script.guid if self.script else None

    @classmethod
    def from_payload(cls, payload: bytes, path: Path | None = None,
                     damage: Damage = Damage.NONE) -> MapData:
        """Parse a decompressed payload, sorting each resource by its type.

        ``damage`` carries in what the container itself was missing, which
        only `from_file` can see.
        """
        info, script, music = None, None, None
        sprites: list[Image.Image] = []
        images: list[Image.Image] = []
        for res in resources(payload):
            if res.truncated:
                damage |= Damage.RESOURCE
            match res.type:
                case ResourceType.INFO:
                    info = parse_info(res.data)
                case ResourceType.SPRITE if (s := parse_sprite(res.data)):
                    sprites.append(s)
                case ResourceType.MUSIC if (m := parse_music(res.data)):
                    music = m
                case ResourceType.JPEG | ResourceType.BMP:
                    images.append(Image.open(io.BytesIO(res.data)))
                case ResourceType.SCRIPT:
                    script = script or parse_script(res.data)
                case ResourceType.SPRITE | ResourceType.MUSIC:
                    damage |= Damage.UNPARSED  # too short for its header
                case _:
                    damage |= Damage.UNKNOWN  # nothing to parse it with
        if info is None:
            raise ValueError('no map info resource found')
        return cls(info, script, music, sprites, images, path, damage)

    @classmethod
    def from_file(cls, path: Path) -> MapData:
        """Read and parse a whole .eap file."""
        payload, damage = _inflate(path.read_bytes())
        return cls.from_payload(payload, path, damage)

    def describe(self) -> str:
        """Return the multi-line summary the command line prints."""
        music = self.music
        track = '' if music is None else music.tags.track or f'{music.seconds:.0f}s'
        return (f'{self.path}\n'
                f'  name   {self.info.name}\n'
                f'  author {self.info.author}\n'
                f'  guid   {self.guid}\n'
                f'  music  {track}\n'
                f'  unknown {self.info.unknown}'
                + (f'\n  damage {self.damage}' if self.damage else ''))


def main(argv: list[str] | None = None) -> None:
    """Print a summary of every .eap file named on the command line."""
    for arg in sys.argv[1:] if argv is None else argv:
        path = Path(arg)
        try:
            print(MapData.from_file(path).describe())
        except Exception as exc:
            print(f'{path}\n  ERROR: {exc}', file=sys.stderr)


if __name__ == '__main__':
    main()
