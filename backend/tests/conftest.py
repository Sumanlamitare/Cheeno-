import datetime as dt
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kundali.config import DEFAULT_SETTINGS  # noqa: E402

UTC = dt.timezone.utc


@pytest.fixture
def settings():
    return DEFAULT_SETTINGS


def utc(*args):
    return dt.datetime(*args, tzinfo=UTC)
