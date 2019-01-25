#!/usr/bin/env python3.6

import logging
from sys import exit
from pathlib import Path
from collections import Counter


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger()


class squidcheck():
    def __init__(self, folder="."):
        self.folder = folder
        
        # Read in the blacklist file, shove it into a list
        self.blfile = open('blacklist', 'r')
        self.blacklist = self.blfile.read().lower().splitlines()

    def check(self):
        logger.info('Checking folders')
        p = Path(self.folder)

        try:
            for x in p.iterdir():
                if x.is_dir():
                    # ignore the these folders
                    if x.name in ['.git', 'test_data', '.pytest_cache', '__pycache__', 'foldercheck', '.idea']:
                        pass
                    else:
                        logger.info(f'Checking : {x}')
                        d = Path(f'./{x}')
                        for i in d.iterdir():
                            if i.name in ['prod', 'nonprod']:

                                # Check the files in the folder
                                np = Path(f'./{i}')
                                for j in np.iterdir():
                                    if j.name in['domains-whitelist', 'ips-whitelist']:
                                        self.checkdups(x,i,j)
                                    else:
                                        logger.error(f'File {j} is invalid')
                                        raise FileExistsError

                            else:
                                # If its not in the list, raise an error
                                logger.error(f'Folder {i} is invalid')
                                raise FileExistsError
        except FileExistsError:
            exit(1)

    def check_blacklist(self, value):
        if value.lower() in self.blacklist:
            logger.error(f'{value} is blacklisted')
            raise ValueError(f'{value} found in blacklist file')

    def checkdups(self, platform, folder, fh):
        logger.info(f'checking for duplicates in {platform} {folder.name} {fh.name}')
        cnt = Counter()

        with fh.open() as f:
            for line in f:
                if line.startswith('#') or line == '\n':
                    pass
                else:
                    self.check_blacklist(line.strip())
                    cnt[line.strip()] += 1
        
        for item in cnt.items():
            name, value = item
            if value > 1:
                raise ValueError(f'Duplicate record found {name} count {value} in {platform} {folder.name} {fh.name}')


if __name__ == '__main__':
    test = squidcheck()
    test.check()
