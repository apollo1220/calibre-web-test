#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from selenium.webdriver.common.by import By
from helper_ui import ui_class, RESTRICT_TAG_ME
from config_test import TEST_DB, BOOT_TIME
import requests
from helper_func import startup, debug_startup
import time
from helper_func import save_logfiles
'''
opds feed tests
'''


class TestOPDSFeed(unittest.TestCase, ui_class):
    p=None
    driver = None

    @classmethod
    def setUpClass(cls):
        startup(cls, cls.py_version, {'config_calibre_dir':TEST_DB}, login=False)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.login('admin','admin123')
        except:
            pass
        cls.stop_calibre_web()
        # close the browser window and stop calibre-web
        cls.driver.quit()
        cls.p.terminate()
        save_logfiles(cls, cls.__name__)

    def tearDown(self):
        if self.check_user_logged_in('admin'):
            self.logout()
            time.sleep(2)

    def test_opds(self):
        r = requests.get('http://127.0.0.1:8083/opds')
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', '123'))
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Authors']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Top Rated Books']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Categories']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Hot Books']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Shelves']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Publishers']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Random Books']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Series']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Unread Books']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Read Books']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Languages']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['File formats']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Ratings']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)

    def test_opds_guest_user(self):
        self.login("admin", "admin123")
        self.fill_basic_config({'config_anonbrowse': 1})
        time.sleep(BOOT_TIME)
        self.edit_user('Guest', {'download_role': 1})
        self.edit_user('admin', {'download_role': 0})
        time.sleep(3)
        self.logout()
        r = requests.get('http://127.0.0.1:8083/opds')
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Authors']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Top Rated Books']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Categories']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Hot Books']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Shelves']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Publishers']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Random Books']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Series']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Languages']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['File formats']['link'])
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['Ratings']['link'])
        self.assertEqual(200, r.status_code)
        self.assertFalse('Read Books' in elements)
        self.assertFalse('Unread Books' in elements)
        # check download from guest account is possible
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'])
        entries = self.get_opds_feed(r.text)
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        self.assertEqual(200, r.status_code)
        self.assertEqual(len(r.content), 28590)
        self.assertEqual(r.headers['Content-Type'], 'application/pdf')
        # create cookies by logging in to admin account and try to download book again
        req_session = requests.session()
        payload = {'username': 'admin', 'password': 'admin123', 'submit': "", 'next': "/", "remember_me": "on"}
        req_session.post('http://127.0.0.1:8083/login', data=payload)
        r = req_session.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        # logged in via cookies from admin account -> admin is not allowed to download
        self.assertEqual(403, r.status_code)
        # logout admin account, cookies now invalid,
        # now login is done via basic header, means no login, guest account can download
        req_session.get('http://127.0.0.1:8083/logout')
        r = req_session.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        self.assertEqual(200, r.status_code)
        # Close session, delete cookies
        req_session.close()
        # Remove download role from guest account
        self.login("admin", "admin123")
        self.edit_user('Guest', {'download_role': 0})
        time.sleep(3)
        self.logout()
        # try download from guest account, fails
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        self.assertEqual(403, r.status_code)
        # create cookies by logging in to admin account and try to download book again
        req_session = requests.session()
        payload = {'username': 'admin', 'password': 'admin123', 'submit': "", 'next': "/", "remember_me": "on"}
        req_session.post('http://127.0.0.1:8083/login', data=payload)
        # user is logged in via cookies, admin is not allowed to download
        r = req_session.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        self.assertEqual(403, r.status_code)
        # logout admin account, cookies now invalid,
        # now login is done via not existing basic header, means no login, guest account also not allowed to download
        req_session.get('http://127.0.0.1:8083/logout')
        r = req_session.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        self.assertEqual(403, r.status_code)
        # Close session, delete cookies
        req_session.close()
        # reset everything back to default
        self.login("admin", "admin123")
        self.edit_user('Guest', {'download_role': 1})
        self.edit_user('admin', {'download_role': 1})
        time.sleep(3)
        self.logout()
        # try download with invalid credentials, using anonymous browsing
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin131'))
        self.assertEqual(200, r.status_code)
        # try download with invalid credentials, using anonymous browsing
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('hudo', 'admin123'))
        self.assertEqual(200, r.status_code)
        self.login("admin", "admin123")
        self.fill_basic_config({'config_anonbrowse': 0})
        time.sleep(BOOT_TIME)
        self.logout()
        # try download from guest account, fails
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['download'])
        self.assertEqual(401, r.status_code)
        # try download with invalid credentials
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin131'))
        self.assertEqual(401, r.status_code)
        # try download with invalid credentials
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('hudo', 'admin123'))
        self.assertEqual(401, r.status_code)



    def test_opds_random(self):
        self.login("admin", "admin123")
        self.fill_view_config({'config_books_per_page': 10})
        self.logout()
        time.sleep(3)
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Random Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),10)
        self.assertEqual(len(entries['links']), 4)   # no next, prev section
        self.login("admin", "admin123")
        self.fill_view_config({'config_books_per_page': 30})
        self.logout()
        time.sleep(3)

    def test_opds_hot(self):
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Hot Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 1)
        self.assertEqual(len(entries['links']), 4)   # no next, prev section

    def test_opds_language(self):
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Languages']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),2)
        self.assertEqual(len(entries['links']), 4)
        self.assertEqual(entries['elements'][0]['title'], 'English')
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),4)
        r = requests.get('http://127.0.0.1:8083' + elements['Languages']['link']+'/3', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)
        self.login("admin", "admin123")
        self.edit_user('admin',{'default_language': 'English'})
        r = requests.get('http://127.0.0.1:8083' + elements['Languages']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),1)
        self.assertEqual(entries['elements'][0]['title'], 'English')
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),4)
        self.edit_user('admin',{'default_language': 'Show All'})
        self.logout()
        time.sleep(3)

    def test_opds_series(self):
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Series']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 2)
        self.assertEqual(len(entries['links']), 4)
        self.assertEqual(entries['elements'][0]['title'], 'Djüngel')
        r = requests.get('http://127.0.0.1:8083'+entries['elements'][1]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 1)
        r = requests.get('http://127.0.0.1:8083' + elements['Series']['link']+'/3', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 0)


    def test_opds_publisher(self):
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Publishers']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 1)
        self.assertEqual(len(entries['links']), 4)
        self.assertEqual(entries['elements'][0]['title'], 'Randomhäus')
        r = requests.get('http://127.0.0.1:8083'+entries['elements'][0]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 1)
        r = requests.get('http://127.0.0.1:8083' + elements['Publishers']['link']+'/3', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 0)

    def test_opds_tags(self):
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Categories']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),1)
        self.assertEqual(len(entries['links']), 4)
        self.assertEqual(entries['elements'][0]['title'], 'Gênot')
        r = requests.get('http://127.0.0.1:8083'+entries['elements'][0]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),4)
        r = requests.get('http://127.0.0.1:8083' + elements['Categories']['link']+'/3', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)

    def test_opds_formats(self):
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['File formats']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),5)
        self.assertEqual(len(entries['links']), 4)
        self.assertEqual(entries['elements'][2]['title'], 'MOBI')
        r = requests.get('http://127.0.0.1:8083'+entries['elements'][1]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),4)
        r = requests.get('http://127.0.0.1:8083' + elements['File formats']['link']+'/8', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)

    def test_opds_author(self):
        self.login("admin", "admin123")
        self.fill_view_config({'config_books_per_page': 6})
        self.logout()
        time.sleep(3)
        r = requests.get('http://127.0.0.1:8083/opds/', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Authors']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),6)
        self.assertEqual(len(entries['links']), 5)
        self.assertEqual(entries['links'][3].attrib['href'], '/opds/author?offset=6')
        self.assertEqual(entries['links'][3].attrib['title'], 'Next')
        r = requests.get('http://127.0.0.1:8083'+entries['links'][3].attrib['href'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),5)
        self.assertEqual(len(entries['links']), 6)
        self.assertEqual(entries['links'][4].attrib['href'], '/opds/author?offset=0')
        self.assertEqual(entries['links'][4].attrib['rel'], 'previous')
        self.assertEqual(entries['links'][3].attrib['rel'], 'first')
        r = requests.get('http://127.0.0.1:8083'+entries['elements'][2]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),2)
        self.assertEqual(entries['elements'][1]['author'][0], 'Peter Parker')
        r = requests.get('http://127.0.0.1:8083' + elements['Authors']['link']+'/77', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)
        self.login("admin", "admin123")
        self.fill_view_config({'config_books_per_page': 30})
        self.logout()
        time.sleep(3)

    def test_opds_non_admin(self):
        self.login("admin", "admin123")
        self.create_user('opds', {'email': 'a5@b.com', 'password':'123'})
        self.logout()
        r = requests.get('http://127.0.0.1:8083/opds', auth=('opds', '122'))
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083/opds', auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Authors']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Top Rated Books']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Categories']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Hot Books']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Recently added Books']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Shelves']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Publishers']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Random Books']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Series']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Languages']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['File formats']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)
        r = requests.get('http://127.0.0.1:8083'+elements['Ratings']['link'], auth=('opds', '123'))
        self.assertEqual(200, r.status_code)

    def test_opds_read_unread(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Read Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)
        self.assertEqual(len(entries['links']), 4)
        r = requests.get('http://127.0.0.1:8083'+elements['Unread Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),11)
        self.assertEqual(len(entries['links']), 4)

    def test_opds_top_rated(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Top Rated Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),1)
        self.assertEqual(len(entries['links']), 4)

    def test_opds_ratings(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Ratings']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),2)
        self.assertEqual(len(entries['links']), 4)
        r = requests.get('http://127.0.0.1:8083'+entries['elements'][1]['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),1)
        r = requests.get('http://127.0.0.1:8083' + elements['Ratings']['link']+'/22', auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)

    def test_recently_added(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 11)
        self.assertEqual(len(entries['links']), 4)
        self.login("admin", "admin123")
        self.fill_view_config({'config_books_per_page': 4})
        self.logout()
        time.sleep(3)
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 4)
        self.assertEqual(len(entries['links']), 5)
        self.assertEqual(entries['links'][3].attrib['href'], '/opds/new?offset=4')
        self.assertEqual(entries['links'][3].attrib['rel'], 'next')
        r = requests.get('http://127.0.0.1:8083'+entries['links'][3].attrib['href'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 4)
        self.assertEqual(len(entries['links']), 7)
        self.assertEqual(entries['links'][5].attrib['href'], '/opds/new?offset=0')
        self.assertEqual(entries['links'][5].attrib['rel'], 'previous')
        self.assertEqual(entries['links'][3].attrib['rel'], 'first')
        self.assertEqual(entries['links'][4].attrib['rel'], 'next')
        self.assertEqual(entries['links'][4].attrib['href'], '/opds/new?offset=8')
        r = requests.get('http://127.0.0.1:8083' + entries['links'][4].attrib['href'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 3)
        self.assertEqual(len(entries['links']), 6)
        self.assertEqual(entries['links'][3].attrib['rel'], 'first')
        self.assertEqual(entries['links'][4].attrib['rel'], 'previous')
        self.assertEqual(entries['links'][4].attrib['href'], '/opds/new?offset=4')
        self.login("admin", "admin123")
        self.fill_view_config({'config_books_per_page': 30})

    def test_opds_unicode_user(self):
        self.login("admin", "admin123")
        self.create_user('一执', {'email': 'a8@b.com', 'password':'1234'})
        self.logout()
        r = requests.get('http://127.0.0.1:8083/opds', auth=('一执'.encode('utf-8'), '1234'))
        self.assertEqual(200, r.status_code)
        self.login("admin", "admin123")
        self.edit_user('admin', {'delete': 1})
        self.logout()

    def test_opds_cover(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['link'])
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['link'], auth=('admin', 'admin123'))
        self.assertEqual(len(r.content),37952)
        self.assertEqual(r.headers['Content-Type'], 'image/jpeg')

    def test_opds_download_book(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['Recently added Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['download'], auth=('admin', 'admin123'))
        self.assertEqual(len(r.content), 28590)
        self.assertEqual(r.headers['Content-Type'], 'application/pdf')
        self.login("admin", "admin123")
        self.create_user('opdsdown', {'email': 'a7@b.com', 'password':'1234', 'download_role':0})
        self.logout()
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['download'], auth=('opdsdown', '1234'))
        self.assertEqual(403, r.status_code)

    def test_opds_calibre_companion(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Recently added Books']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        r = requests.get('http://127.0.0.1:8083/ajax/book/' + entries['elements'][1]['id'][9:], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements=r.json()
        self.assertEqual(elements['title'], 'book10')
        self.assertEqual(elements['main_format']['pdf'], '/opds/download/12/pdf/')
        self.assertEqual(elements['formats'][0], 'PDF')
        r = requests.get('http://127.0.0.1:8083/ajax/book/' + entries['elements'][1]['id'][9:] +"/lulu",
                         auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)

    def test_opds_search(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083' + elements['links'][2].attrib['href'])
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + elements['links'][2].attrib['href'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        searches = self.get_opds_search(r.text)
        self.assertEqual(searches['longname'],'Calibre-Web')
        term = (searches['search'][1].attrib['template']).format(searchTerms='Parker')
        r = requests.get('http://127.0.0.1:8083' + term)
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + term, auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),2)
        self.assertEqual(entries['elements'][0]['author'][0], 'Peter Parker')
        self.assertEqual(entries['elements'][1]['author'][0], 'Peter Parker')
        term = (searches['search'][0].attrib['template']).format(searchTerms='Genot')
        r = requests.get('http://127.0.0.1:8083' + term)
        self.assertEqual(401, r.status_code)
        r = requests.get('http://127.0.0.1:8083' + term, auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),4)
        term = (searches['search'][0].attrib['template']).format(searchTerms='Djüng')
        r = requests.get('http://127.0.0.1:8083' + term, auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),2)
        self.login("admin", "admin123")
        self.edit_user('admin',{'default_language': 'English'})
        time.sleep(2)
        term = (searches['search'][0].attrib['template']).format(searchTerms='book')
        r = requests.get('http://127.0.0.1:8083' + term, auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 3)
        self.edit_user('admin', {'default_language': 'Show All'})
        restricts = self.list_restrictions(RESTRICT_TAG_ME)
        self.assertEqual(len(restricts), 0)
        self.add_restrictions('Gênot',allow=False)
        close = self.check_element_on_page((By.ID, "restrict_close"))
        self.assertTrue(close)
        close.click()
        time.sleep(2)
        term = (searches['search'][0].attrib['template']).format(searchTerms='book')
        r = requests.get('http://127.0.0.1:8083' + term, auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']), 4)
        restricts = self.list_restrictions(RESTRICT_TAG_ME)
        self.assertEqual(len(restricts), 1)
        self.delete_restrictions('d0')
        close = self.check_element_on_page((By.ID, "restrict_close"))
        self.assertTrue(close)
        close.click()
        time.sleep(2)
        self.logout()
        time.sleep(2)

    def test_opds_shelf_access(self):
        r = requests.get('http://127.0.0.1:8083/opds', auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        elements = self.get_opds_index(r.text)
        r = requests.get('http://127.0.0.1:8083'+elements['Shelves']['link'], auth=('admin', 'admin123'))
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),0)
        self.login('admin', 'admin123')
        self.goto_page('create_shelf')
        self.create_shelf('Pü 执',False)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        r = requests.get('http://127.0.0.1:8083'+elements['Shelves']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),1)
        self.assertEqual(entries['elements'][0]['title'], 'Pü 执')
        self.goto_page('nav_new')
        books = self.get_books_displayed()
        self.get_book_details(int(books[1][0]['id']))
        self.check_element_on_page((By.ID, "add-to-shelf")).click()
        self.check_element_on_page((By.XPATH, "//ul[@id='add-to-shelves']/li/a[contains(.,'P')]")).click()
        self.assertTrue(self.check_element_on_page((By.XPATH, "//*[@id='remove-from-shelves']//a")))
        r = requests.get('http://127.0.0.1:8083'+elements['Shelves']['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(len(entries['elements']),1)
        r = requests.get('http://127.0.0.1:8083' + entries['elements'][0]['link'], auth=('admin', 'admin123'))
        self.assertEqual(200, r.status_code)
        entries = self.get_opds_feed(r.text)
        self.assertEqual(entries['elements'][0]['title'], 'book11')
        self.list_shelfs(u'Pü 执')['ele'].click()
        self.check_element_on_page((By.ID, "delete_shelf")).click()
        self.check_element_on_page((By.ID, "delete_confirm")).click()
        self.logout()
        time.sleep(2)
