from threading import Thread
import requests, tempfile, time, logging
from pathlib import Path
from typing import Optional


_thr: Optional[Thread] = None
latest_version = None


def thr_target():
    global latest_version

    try:
        check_interval_d = 3
        tmp_file = Path(tempfile.gettempdir()).joinpath('genin2_tmp')

        if tmp_file.exists():
            last_check_delta_d = (time.time() - tmp_file.stat().st_mtime) // 24 // 60 // 60
            logging.debug("check_update(): Last checked for updates %d days ago", last_check_delta_d)
            
            if last_check_delta_d <= check_interval_d:
                latest_version = str(open(tmp_file).readline()).strip()
                logging.debug("check_update(): Retrieved from temp file: %s", latest_version)
        else:
            logging.debug("check_update(): Checking for updates...")
            res = requests.get(f'https://pypi.org/pypi/genin2/json', timeout=4)
            latest_version = res.json()['info']['version']
            latest_version = str(latest_version).strip()
            open(tmp_file, 'w').write(latest_version + '\n')
            logging.debug("check_update(): fetched and saved latest version from PyPi: %s", latest_version)
    except Exception as e:
        logging.warning("Could not check for updates. %s: %s", type(e).__name__, str(e))


def start_check():
    global _thr
    _thr = Thread(None, thr_target)
    _thr.start()


def get_result():
    if _thr is None:
        logging.error("The checker thread has never been started.")
        raise Exception("The checker thread has never been started.")
    
    _thr.join()
    return latest_version
