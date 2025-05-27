# rspy/__init__.py

from .utils import file, log, stopwatch, timer, lsusb
from .hubs import device_hub  # we handle imports to the hubs within device_hub

# tell Python to look in the utils subfolder for top‑level modules
import os
__path__.insert(0, os.path.join(os.path.dirname(__file__), "utils")) # to allow us to do things like `from rspy.timer import Timer`

# — other top‑level modules that still live at this level —
from .devices         import *
from .libci           import *
from .librs           import *
from .repo            import *
from .signals         import *
from .test            import *
from .tests_wrapper   import *

# — your subpackages —
from . import hubs
from . import utils


# # (optional) make __all__ explicit
# __all__ = [
#     # modules
#     "devices", "libci", "librs", "lsusb", "repo",
#     "signals", "test", "tests_wrapper",
#     # re‑exported names
#     "file", "log", "stopwatch", "timer",
#     # packages
#     "hubs", "utils",
# ]
