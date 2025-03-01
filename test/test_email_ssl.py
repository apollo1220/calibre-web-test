#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import unittest
import socket

from selenium.webdriver.common.by import By
from helper_email_convert import AIOSMTPServer
import helper_email_convert
from helper_ui import ui_class
from config_test import CALIBRE_WEB_PATH, TEST_DB, BOOT_TIME, base_path
# from parameterized import parameterized_class
from helper_func import startup, save_logfiles, wait_Email_received
# from helper_certificate import generate_ssl_testing_files

@unittest.skipIf(helper_email_convert.is_calibre_not_present(),"Skipping convert, calibre not found")
class TestSSL(unittest.TestCase, ui_class):
    p = None
    driver = None
    email_server = None
    LOG_LEVEL = 'DEBUG'

    @classmethod
    def setUpClass(cls):
        # start email server
        # generate_ssl_testing_files()
        cls.email_server = AIOSMTPServer(
            hostname=socket.gethostname(), port=1027,
            only_ssl=True,
            certfile='files/server.crt',
            keyfile='files/server.key',
            timeout=10
        )
        cls.email_server.start()
        startup(cls, cls.py_version, {'config_calibre_dir':TEST_DB,
                                      'config_converterpath':helper_email_convert.calibre_path(),
                                      'config_ebookconverter':'converter2',
                                      'config_log_level':cls.LOG_LEVEL}, env={"APP_MODE": "test"})

        cls.edit_user('admin', {'email': 'a5@b.com','kindle_mail': 'a1@b.com'})
        cls.setup_server(False, {'mail_server':socket.gethostname(), 'mail_port':'1027',
                            'mail_use_ssl':'SSL/TLS','mail_login':'name@host.com','mail_password_e':'10234',
                            'mail_from':'name@host.com'})


    @classmethod
    def tearDownClass(cls):
        cls.driver.get("http://127.0.0.1:8083")
        cls.stop_calibre_web()
        # close the browser window and stop calibre-web
        cls.driver.quit()
        cls.p.terminate()
        cls.email_server.stop()
        time.sleep(2)
        save_logfiles(cls, cls.__name__)

    # start sending e-mail
    # check email received
    def test_SSL_only(self):
        tasks = self.check_tasks()
        self.setup_server(False, {'mail_use_ssl': 'SSL/TLS'})
        details = self.get_book_details(7)
        details['kindlebtn'].click()
        conv = self.check_element_on_page((By.LINK_TEXT, details['kindle'][0].text))
        self.assertTrue(conv)
        conv.click()
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        i = 0
        while i < 10:
            time.sleep(2)
            task_len, ret = self.check_tasks(tasks)
            if task_len == 1:
                if ret[-1]['result'] == 'Finished' or ret[-1]['result'] == 'Failed':
                    break
            i += 1
        self.assertEqual(ret[-1]['result'], 'Finished')


    # check behavior for failed server setup (STARTTLS)
    @unittest.skipIf(sys.version_info < (3, 7), "AsyncIO has no ssl handshake timeout")
    def test_SSL_STARTTLS_setup_error(self):
        tasks = self.check_tasks()
        self.setup_server(False, {'mail_use_ssl':'STARTTLS'})
        details = self.get_book_details(7)
        details['kindlebtn'].click()
        conv = self.check_element_on_page((By.LINK_TEXT, details['kindle'][0].text))
        self.assertTrue(conv)
        conv.click()
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        i = 0
        while i < 10:
            time.sleep(2)
            task_len, ret = self.check_tasks(tasks)
            if task_len == 1:
                if ret[-1]['result'] == 'Finished' or ret[-1]['result'] == 'Failed':
                    break
            i += 1
        self.assertEqual(ret[-1]['result'], 'Failed')

    # check behavior for failed server setup (NonSSL)
    @unittest.skipIf(sys.version_info < (3, 7), "AsyncIO has no ssl handshake timeout")
    def test_SSL_None_setup_error(self):
        tasks = self.check_tasks()
        self.setup_server(False, {'mail_use_ssl':'None'})
        details = self.get_book_details(7)
        details['kindlebtn'].click()
        conv = self.check_element_on_page((By.LINK_TEXT, details['kindle'][0].text))
        self.assertTrue(conv)
        conv.click()
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        i = 0
        while i < 10:
            time.sleep(2)
            task_len, ret = self.check_tasks(tasks)
            if task_len == 1:
                if ret[-1]['result'] == 'Finished' or ret[-1]['result'] == 'Failed':
                    break
            i += 1
        self.assertEqual('Failed', ret[-1]['result'])

    # check if email traffic is logged to logfile
    def test_SSL_logging_email(self):
        self.setup_server(True, {'mail_use_ssl': 'SSL/TLS'})
        time.sleep(5)
        with open(os.path.join(CALIBRE_WEB_PATH,'calibre-web.log'),'r') as logfile:
            data = logfile.read()
        self.assertTrue(len(re.findall('Subject: Calibre-Web Test Email', data)), "Email logging not working")


    def test_email_limit(self):
        # enable upload files
        self.fill_basic_config({'config_uploading': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, 'flash_success')))
        self.edit_user('admin', {'upload_role': 1})
        random_file = os.path.join(base_path, 'files', 'random.mobi')
        # create random .mobi file size >2 mb
        with open(random_file, 'wb') as fout:
            fout.write(os.urandom(2049*1024))
        self.goto_page('nav_new')
        upload = self.check_element_on_page((By.ID, 'btn-upload'))
        upload.send_keys(random_file)
        time.sleep(4)
        self.check_element_on_page((By.ID, 'edit_cancel')).click()
        book_details = self.get_book_details()
        self.assertTrue(book_details['kindlebtn'])
        # set limit to 0 mb
        self.setup_server(False, {'mail_size': ''})
        self.assertFalse(self.check_element_on_page((By.ID, "flash_success")))
        # set limit to 0.5 mb
        self.setup_server(False, {'mail_size': '0.5'})
        self.assertFalse(self.check_element_on_page((By.ID, "flash_success")))
        # set limit to -1 mb
        self.setup_server(False, {'mail_size': '-1'})
        self.assertFalse(self.check_element_on_page((By.ID, "flash_success")))
        # set limit to 601 mb
        self.setup_server(False, {'mail_size': '601'})
        self.assertFalse(self.check_element_on_page((By.ID, "flash_success")))
        # set limit to 2 mb
        self.setup_server(False, {'mail_size': '2'})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))

        # try to send
        details = self.get_book_details(int(book_details['id']))
        # check what happens
        self.assertFalse(details['kindlebtn'])

        self.fill_basic_config({'config_uploading': 0})
        os.unlink(random_file)

    # start sending e-mail
    # check email received
    def test_SSL_non_admin_user(self):
        self.create_user('ssl_email', {'password': '123AbC*!', 'email': 'answer@beta.com', 'kindle_mail': 'answer@beta.com', 'download_role': 1})
        self.setup_server(False, {'mail_use_ssl': 'SSL/TLS'})
        self.logout()
        self.login("ssl_email", "123AbC*!")
        tasks = self.check_tasks()
        details = self.get_book_details(7)
        details['kindlebtn'].click()
        conv = self.check_element_on_page((By.LINK_TEXT, details['kindle'][0].text))
        self.assertTrue(conv)
        conv.click()
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        i = 0
        while i < 10:
            time.sleep(2)
            task_len, ret = self.check_tasks(tasks)
            if task_len == 1:
                if ret[-1]['result'] == 'Finished' or ret[-1]['result'] == 'Failed':
                    break
            i += 1
        self.assertEqual(ret[-1]['result'], 'Finished')
        self.assertTrue(wait_Email_received(self.email_server.handler.check_email_received))
        self.logout()
        self.login("admin", "admin123")
        self.edit_user('ssl_email', {'delete': 1})

    # Navigate to http://localhost:8083/admin/config
    # Unfold "Server Configuration" section
    # Click the filepicker next to the text input under "SSL certfile location (leave it empty for non-SSL Servers)"
    # Navigate to an arbitrary location
    # Confirm selection
    # Click the filepicker next to the text input under "SSL Keyfile location (leave it empty for non-SSL Servers)
    # Navigate to an arbitrary location
    # Confirm selection

    # Expected result:
    # The value of the first text input is set to the result of step 5
    # The value of the second text input is set to the result of step 8
    def test_filepicker_two_file(self):
        self.goto_page('basic_config')
        accordions = self.driver.find_elements(By.CLASS_NAME, "accordion-toggle")
        accordions[0].click()
        filepicker = self.check_element_on_page((By.ID, "certfile_path"))
        self.assertTrue(filepicker)
        # open filepicker
        filepicker.click()
        time.sleep(2)
        found = False
        selections = self.driver.find_elements(By.XPATH, "//tr[@class='tr-clickable']/td[2]")
        for i in selections:
            if i.text == "files":
                i.click()
                found = True
                break
        self.assertTrue(found, "files folder not found")
        found = False
        time.sleep(2)
        file_selections = self.driver.find_elements(By.XPATH, "//tr[@class='tr-clickable']/td[2]")
        time.sleep(2)
        for i in file_selections:
            if i.text == "client.crt":
                i.click()
                found = True
                break
        self.assertTrue(found, "client.crt not found")
        crt_element = self.check_element_on_page((By.ID, "element_selected")).text
        self.check_element_on_page((By.ID, "file_confirm")).click()
        time.sleep(2)

        filepicker2 = self.check_element_on_page((By.ID, "keyfile_path"))
        self.assertTrue(filepicker2)
        found = False
        # open filepicker
        filepicker2.click()
        time.sleep(2)
        selections = self.driver.find_elements(By.XPATH, "//tr[@class='tr-clickable']/td[2]")
        for i in selections:
            if i.text == "files":
                i.click()
                time.sleep(1)
                found = True
                break
        self.assertTrue(found, "files folder not found")
        found = False
        time.sleep(2)
        file_selections = self.driver.find_elements(By.XPATH, "//tr[@class='tr-clickable']/td[2]")
        for i in file_selections:
            if i.text == "client.key":
                i.click()
                found = True
                break
        self.assertTrue(found, "client.key not found")
        key_element = self.check_element_on_page((By.ID, "element_selected")).text
        self.check_element_on_page((By.ID, "file_confirm")).click()
        time.sleep(2)

        self.assertEqual(self.check_element_on_page((By.ID, "config_certfile")).get_attribute('value'), crt_element)
        self.assertEqual(self.check_element_on_page((By.ID, "config_keyfile")).get_attribute('value'), key_element)
