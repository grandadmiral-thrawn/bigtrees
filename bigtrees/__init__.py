from __future__ import division
import sys
try:
    import cdecimal
    sys.modules["decimal"] = cdecimal
except:
    pass

__title__      = "bigtrees"
__version__    = "0.1"
__author__     = "Fox Peterson"
__license__    = "MIT"
__maintainer__ = "Fox Peterson"
__email__      = "fox@tinybike.net"

from .biggest_trees import *
