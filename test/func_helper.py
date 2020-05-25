#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import re
from testconfig import CALIBRE_WEB_PATH, TEST_DB, BOOT_TIME
from selenium.webdriver.support.ui import WebDriverWait
from subproc_wrapper import process_open
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time

try:
    import pycurl
    from io import BytesIO
    curl_available = True
except ImportError:
    curl_available = False

def is_port_in_use(port):
    import socket, errno
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
    except socket.error as e:
        if e.errno == errno.EADDRINUSE:
            return True
        else:
            return False
    s.close()
    return False


def startup(inst, pyVersion, config, login=True):
    print("\n%s - %s: " % (inst.py_version, inst.__name__))
    try:
        os.remove(os.path.join(CALIBRE_WEB_PATH, 'app.db'))
    except:
        pass
    shutil.rmtree(TEST_DB, ignore_errors=True)
    shutil.copytree('./Calibre_db', TEST_DB)
    inst.p = process_open([pyVersion, os.path.join(CALIBRE_WEB_PATH, u'cps.py')], (1), sout=None)

    # create a new Firefox session
    inst.driver = webdriver.Firefox()
    # time.sleep(15)
    inst.driver.implicitly_wait(BOOT_TIME)

    inst.driver.maximize_window()

    # navigate to the application home page
    inst.driver.get("http://127.0.0.1:8083")

    # Wait for config screen to show up
    inst.fill_initial_config(dict(config_calibre_dir=config['config_calibre_dir']))
    del config['config_calibre_dir']

    # wait for cw to reboot
    time.sleep(BOOT_TIME)

    # Wait for config screen with login button to show up
    WebDriverWait(inst.driver, 5).until(EC.presence_of_element_located((By.NAME, "login")))
    login_button = inst.driver.find_element_by_name("login")
    login_button.click()
    inst.login("admin", "admin123")
    inst.fill_basic_config(config)
    time.sleep(BOOT_TIME)
    # login
    if not login:
        inst.logout()

def wait_Email_received(func):
    i = 0
    while i < 10:
        if func():
            return True
        time.sleep(2)
        i += 1
    return False

def check_response_language_header(url, header, expected_response,search_text):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.HTTPHEADER, header)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    if c.getinfo(c.RESPONSE_CODE) != expected_response:
        return False
    c.close()
    body = buffer.getvalue().decode('utf-8')
    return bool(re.search(search_text, body))
