import os
import re
import subprocess
import urllib
from enum import Enum
from pathlib import Path
from urllib.error import HTTPError

from selenium import webdriver
from webdrivermanager import ChromeDriverManager

from src.com.charlesmlin.pps_automator.util import Utils


def download_chrome_driver() -> Path or None:
    path: Path = Utils.get_project_path()
    output = subprocess.Popen(['cmd', '/C', str(path.joinpath('chrome_version.bat'))],
                              stdout=subprocess.PIPE).communicate()[0]
    output.decode('utf-8').split(os.linesep)
    match_versions = list(map(lambda x: x.split(' ')[-1],
                              filter(lambda x: re.match('^[ ]*pv[ ]*REG_SZ[ ]*[0-9.]+', x) is not None,
                                     output.decode('utf-8').split(os.linesep))))
    if len(match_versions) > 0:
        # As per description, only stable and beta build will have corresponding chromedriver
        # https://chromedriver.chromium.org/downloads/version-selection
        chrome_version = '.'.join(match_versions[0].split('.')[0:-1])
        print(f'browser version is {chrome_version}')
        driver_check_link = f'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{chrome_version}'
        driver_version: str
        try:
            with urllib.request.urlopen(driver_check_link) as response:
                driver_version = response.read().decode('utf-8')
        except HTTPError:
            driver_version = 'latest'
        print(f'driver version should be {driver_version}')
        driver = ChromeDriverManager()
        (exe_path, exe_sym_link) = driver.download_and_install(driver_version)
        return Path(exe_sym_link)
    return None


class BrowserDriver(Enum):
    CHROME = (download_chrome_driver, webdriver.Chrome)
    FIREFOX = (None, webdriver.Firefox)
    OPERA = (None, webdriver.Opera)
    EDGE = (None, webdriver.Edge)
    IE = (None, webdriver.Ie)
