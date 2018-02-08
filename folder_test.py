#!/usr/bin/env python3.6

import logging
from sys import exit
from pathlib import Path

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger()


def main():
    logger.info('Checking folders')
    p = Path('.')

    try:
        for x in p.iterdir():
            if x.is_dir():
                if x.name == '.git':
                    # ignore the .git folder
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
                                    # ignore the file name in the list
                                    pass
                                else:
                                    logger.error(f'File {j} is invalid')
                                    raise FileExistsError

                        else:
                            # If its not in the list, raise an error
                            logger.error(f'Folder {i} is invalid')
                            raise FileExistsError
    except FileExistsError as e:
        exit(1)


if __name__ == '__main__':
    main()
