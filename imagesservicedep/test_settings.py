import os
import sys
from .settings import *  # noqa: F403


if 'test' in sys.argv or 'pytest' in sys.argv[0]:
    TEST_MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')  # noqa: F405
    MEDIA_ROOT = TEST_MEDIA_ROOT
