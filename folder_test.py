#!/usr/bin/env python3.6

import sys

from foldercheck import foldertest


if __name__ == "__main__":  # pragma: no cover
    test = foldertest.squidcheck(sys.argv[1] or ".")
    test.check()
