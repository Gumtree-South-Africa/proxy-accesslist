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
        
    def check(self):
        logger.info('Checking folders')
        p = Path(self.folder)

        try:
            for x in p.iterdir():
                if x.is_dir():
                    # ignore the these folders
                    if x.name in ['.git', 'test_data','.pytest_cache','__pycache__','foldercheck']:
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
                                        #pass
                                    else:
                                        logger.error(f'File {j} is invalid')
                                        raise FileExistsError

                            else:
                                # If its not in the list, raise an error
                                logger.error(f'Folder {i} is invalid')
                                raise FileExistsError
        except FileExistsError as e:
            exit(1)


    def checkdups(self, platform, folder, fh):
        logger.info(f'checking for duplicates in {platform} {folder.name} {fh.name}')
        cnt = Counter()
    
        with fh.open() as f:
            for line in f:
                if line.startswith('#') or line == '\n':
                    pass
                else:
            #print(line.strip())
                    cnt[line.strip()] +=1
        
        #print(cnt)
        for item in cnt.items():
            name, value = item
            if value > 1:
                raise ValueError(f'Duplicate record found {name} count {value} in {platform} {folder.name} {fh.name}')


if __name__ == '__main__':
    test = squidcheck()
    test.check()
