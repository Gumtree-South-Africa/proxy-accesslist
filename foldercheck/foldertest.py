#!/usr/bin/env python3.6

import ipaddress
import logging
import re
from collections import Counter
from pathlib import Path
from sys import exit


logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)
logger = logging.getLogger()


class squidcheck:
    IP_REGEX = re.compile(r"\d{1,3}\.\d{1,3}.")

    def __init__(self, folder="."):
        self.folder = folder

        # Read in the denylist file, shove it into a list
        with open(Path.joinpath(Path(self.folder), "denylist"), "r") as dlfile:
            self.denylist = dlfile.read().lower().splitlines()

    @staticmethod
    def uncomment(value):
        if value.startswith("#") or value == "\n":
            return
        else:
            data = value.split("#", 1)[0].strip()
            return data

    def check(self):
        logger.info("Checking folders")
        p = Path(self.folder)
        try:
            for x in p.iterdir():
                if x.is_dir():
                    # ignore the these folders
                    if x.name not in [
                        ".git",
                        ".github",
                        "tests",
                        ".pytest_cache",
                        "__pycache__",
                        "foldercheck",
                        ".idea",
                    ]:

                        logger.info(f"Checking: {x}")
                        d = Path(f"{x}")
                        for i in d.iterdir():
                            if i.name in ["prod", "nonprod"]:

                                # Check the files in the folder
                                np = Path(f"{i}")
                                for j in np.iterdir():
                                    if j.name in ["domains-allowlist", "ips-allowlist"]:
                                        self.checkdups(x, i, j)
                                        if j.name == "domains-allowlist":
                                            self.checkdomaindata(x, i, j)
                                        if j.name == "ips-allowlist":
                                            self.checkipdata(x, i, j)
                                    else:
                                        logger.error(f"File {j} is invalid")
                                        raise FileExistsError

                            else:
                                # If its not in the list, raise an error
                                logger.error(f"Folder {i} is invalid")
                                raise FileExistsError
        except FileExistsError:
            exit(1)

    def check_denylist(self, value):
        if value.lower() in self.denylist:
            logger.error(f"{value} is not allowed")
            raise ValueError(f"{value} found in denylist file")

    def checkdups(self, platform, folder, fh):
        logger.info(f"checking for duplicates in {platform} {folder.name} {fh.name}")
        cnt = Counter()

        with fh.open() as f:
            for line in f:
                data = self.uncomment(line)
                if data:
                    self.check_denylist(data)
                    cnt.update([data])

        for item in cnt.items():
            name, value = item
            if value > 1:
                raise ValueError(
                    f"Duplicate record found {name} count {value} in {platform} {folder.name} {fh.name}"
                )

    def checkdomaindata(self, platform, folder, fh):
        logger.info(f"checking for bad values in {platform} {folder.name} {fh.name}")

        with fh.open() as f:
            for line in f:
                data = self.uncomment(line)
                if data:
                    # Check if the line has a port number
                    if ":" in data:
                        raise ValueError(
                            f"Port values found {data} in {platform} {folder.name} {fh.name}"
                        )

                    if self.IP_REGEX.match(data):
                        raise ValueError(
                            f"IP address/prefix record found {data} in {platform} {folder.name} {fh.name}"
                        )

    def checkipdata(self, platform, folder, fh):
        logger.info(f"checking for bad IP values in {platform} {folder.name} {fh.name}")
        with fh.open() as f:
            for line in f:
                data = self.uncomment(line)
                if data:
                    if not self.IP_REGEX.match(data):
                        raise ValueError(
                            f"Not an IP {data} in {platform} {folder.name} {fh.name}"
                        )
                    if "/" in data:
                        if not ipaddress.ip_network(data):
                            raise ValueError(
                                f"IP prefix invalid {data} in {platform} {folder.name} {fh.name}"
                            )
                    else:
                        if not ipaddress.ip_address(data):
                            raise ValueError(
                                f"IP address invalid {data} in {platform} {folder.name} {fh.name}"
                            )
                        if ipaddress.ip_address(data).is_private:
                            raise ValueError(
                                f"IP in private ranges record found {data} in {platform} {folder.name} {fh.name}"
                            )


if __name__ == "__main__":  # pragma: no cover
    test = squidcheck()
    test.check()
