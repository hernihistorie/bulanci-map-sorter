"""Tests for the .eap reader, run against maps from the collection."""
from pathlib import Path

import eap

MAPS = Path(__file__).parent.parent / '_MAPS_'


def test_read_info() -> None:
    info = eap.MapData.from_file(MAPS / '-PSP-.eap').info
    assert info.name == '-PSP-'
    assert info.author == 'Pavel Švec'
