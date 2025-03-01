#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from selenium.webdriver.common.by import By
from helper_ui import ui_class
from config_test import TEST_DB
from helper_func import startup
from helper_func import save_logfiles


class TestAnonymous(unittest.TestCase, ui_class):
    p = None
    driver = None

    @classmethod
    def setUpClass(cls):
        try:
            startup(cls, cls.py_version, {'config_calibre_dir': TEST_DB, 'config_anonbrowse': 1}, env={"APP_MODE": "test"})
        except Exception as e:
            print(e)

    @classmethod
    def tearDownClass(cls):
        cls.driver.get("http://127.0.0.1:8083")
        cls.stop_calibre_web()
        # close the browser window and stop calibre-web
        cls.driver.quit()
        cls.p.terminate()
        save_logfiles(cls, cls.__name__)

    def tearDown(self):
        if not self.check_user_logged_in('admin'):
            try:
                self.logout()
            except:
                self.driver.get("http://127.0.0.1:8083")
                self.logout()
            self.check_element_on_page((By.ID, "top_user")).click()
            self.login('admin', 'admin123')


    def test_guest_about(self):
        self.logout()
        self.assertFalse(self.goto_page('nav_about'))

    # Checks if random book section is available in all sidebar menus
    def test_guest_random_books_available(self):
        self.edit_user('Guest', {'show_128': 1, 'show_2': 1, 'show_64': 1, 'show_8192': 1, 'show_16384': 1,
                                 'show_16': 1, 'show_4': 1, 'show_4096': 1, 'show_8': 1, 'show_32': 1})
        self.logout()
        # check random books shown in new section
        self.goto_page('nav_new')
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books not shown in random section
        self.assertTrue(self.goto_page('nav_rand'))
        self.assertFalse(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in category section
        list_element = self.goto_page('nav_cat')
        self.assertIsNotNone(list_element)
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in series section
        self.goto_page('nav_serie')
        # check if we are seeing list view
        # if len(list_element == 0):
        list_element = self.get_list_books_displayed()
        self.assertIsNotNone(list_element)
        list_element[0]['ele'].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books NOT shown in author section
        list_element = self.goto_page('nav_author')
        self.assertIsNotNone(list_element)
        list_element[0].click()
        self.driver.implicitly_wait(5)
        self.assertFalse(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in language section
        list_element = self.goto_page('nav_lang')
        self.assertIsNotNone(list_element)
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in hot section
        list_element = self.goto_page('nav_author')
        self.assertIsNotNone(list_element)
        self.goto_page('nav_hot')
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in publisher section
        list_element = self.goto_page('nav_publisher')
        self.assertIsNotNone(list_element)
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in rating section
        list_element = self.goto_page('nav_rate')
        self.assertIsNotNone(list_element)
        list_element[1].find_element(By.XPATH, '..').click()
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # check random books shown in format section
        list_element = self.goto_page('nav_format')
        self.assertIsNotNone(list_element)
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))

        # Check random menu is in sidebar
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_32': 0, 'show_128': 0, 'show_2': 0, 'show_8192': 0, 'show_16384': 0,
                                 'show_16': 0, 'show_4': 0, 'show_4096': 0, 'show_8': 0, 'show_64': 0})
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_read")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_download")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_list")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_unread")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_archived")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rate")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_format")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_publisher")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_new")))
        # login as admin again
        self.login('admin', 'admin123')

    # checks if admin can configure sidebar for random view
    def test_guest_visibility_sidebar(self):
        self.edit_user('Guest', {'show_32': 0, 'show_128': 1, 'show_2': 1,
                                 'show_16': 1, 'show_4': 1, 'show_4096': 1, 'show_8': 1, 'show_64': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        self.goto_page("nav_new")
        books = self.get_books_displayed()
        self.assertEqual(books[1][0]['id'],'13')
        self.assertEqual(books[1][3]['id'], '10')
        self.assertEqual(books[1][7]['id'], '5')
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in category section
        list_element = self.goto_page("nav_cat")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books shown in series section
        self.goto_page("nav_serie")
        list_element = self.get_list_books_displayed()
        self.assertIsNotNone(list_element)
        list_element[0]['ele'].click()

        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in author section
        list_element = self.goto_page("nav_author")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in publisher section
        list_element = self.goto_page("nav_publisher")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in language section
        list_element = self.goto_page("nav_lang")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in hot section
        self.goto_page("nav_hot")
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in best rated section
        self.goto_page("nav_rated")
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rand")))
        # Go to admin section and re enable show random view
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_32': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        list_element = self.goto_page("nav_cat")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books shown in series section
        self.goto_page("nav_serie")
        list_element = self.get_list_books_displayed()
        self.assertIsNotNone(list_element)
        list_element[0]['ele'].click()

        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in author section
        list_element = self.goto_page("nav_author")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in publisher section
        list_element = self.goto_page("nav_publisher")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in language section
        list_element = self.goto_page("nav_lang")
        list_element[0].click()
        self.assertTrue(self.check_element_on_page((By.ID, "books")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in hot section
        self.goto_page("nav_hot")
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        # check random books not shown in best rated section
        self.goto_page("nav_rated")
        self.assertTrue(self.check_element_on_page((By.ID, "books_rand")))
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rand")))
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_32': 0, 'show_128': 0, 'show_2': 0,
                                 'show_16': 0, 'show_4': 0, 'show_4096': 0, 'show_8': 0, 'show_64': 0})

    # Test if user can change visibility of sidebar view best rated books
    def test_guest_change_visibility_rated(self):
        self.edit_user('Guest', {'show_128': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rated")))
        self.goto_page("nav_rated")
        books = self.get_books_displayed()
        self.assertEqual(books[1][0]['id'], '10')
        self.check_element_on_page((By.ID, "old")).click()
        books = self.get_books_displayed()
        self.assertEqual(books[1][0]['id'], '10')
        self.check_element_on_page((By.ID, "new")).click()
        books = self.get_books_displayed()
        self.assertEqual(books[1][0]['id'], '10')
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_128': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rated")))

    # checks if admin can change user language
    def test_guest_change_visibility_language(self):
        self.edit_user('Guest', {'show_2': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_lang")))
        self.goto_page("nav_lang")
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['id'], 'eng')
        self.check_element_on_page((By.ID, "desc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[2]['id'], 'eng')
        self.goto_page("nav_new")
        self.goto_page("nav_lang")
        self.assertEqual(books[2]['id'], 'eng')
        self.check_element_on_page((By.ID, "asc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['id'], 'eng')
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_2': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_lang")))

    # checks if admin can change hot books
    def test_guest_change_visibility_hot(self):
        self.edit_user('Guest', {'show_16': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_hot")))
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_16': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_hot")))

    # checks if admin can change series
    def test_guest_change_visibility_series(self):
        self.edit_user('Guest', {'show_4': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_serie")))
        self.goto_page("nav_serie")
        books = self.get_list_books_displayed()
        self.assertEqual(books[1]['id'], '2')
        self.check_element_on_page((By.ID, "desc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['id'], '2')
        self.goto_page("nav_new")
        self.goto_page("nav_serie")
        self.assertEqual(books[0]['id'], '2')
        self.check_element_on_page((By.ID, "asc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[1]['id'], '2')
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_4': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_serie")))

    # checks if admin can change publisher
    def test_guest_change_visibility_publisher(self):
        self.edit_user('Guest', {'show_4096': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_publisher")))
        self.goto_page("nav_publisher")
        books = self.get_list_books_displayed()
        self.assertEqual(books[1]['title'], 'Randomhäus')
        self.check_element_on_page((By.ID, "desc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['title'], 'Randomhäus')
        self.check_element_on_page((By.ID, "asc")).click()
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_4096': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_publisher")))

    # checks if admin can change format
    def test_guest_change_visibility_format(self):
        self.edit_user('Guest', {'show_16384': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_format")))
        self.goto_page("nav_format")
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['id'], 'CBR')
        self.check_element_on_page((By.ID, "desc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[4]['id'], 'CBR')
        self.goto_page("nav_new")
        self.goto_page("nav_format")
        self.assertEqual(books[4]['id'], 'CBR')
        self.check_element_on_page((By.ID, "asc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['id'], 'CBR')
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_16384': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_format")))

    # checks if admin can change ratings
    def test_guest_change_visibility_rating(self):
        self.edit_user('Guest', {'show_8192': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_rate")))
        self.goto_page("nav_rate")
        books = self.get_list_books_displayed()
        self.assertEqual(books[2]['id'], '2')
        self.check_element_on_page((By.ID, "desc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['id'], '2')
        self.assertEqual(books[2]['id'], '-1')
        self.goto_page("nav_new")
        self.goto_page("nav_rate")
        self.assertEqual(books[0]['id'], '2')
        self.check_element_on_page((By.ID, "asc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[2]['id'], '2')
        self.assertEqual(books[0]['id'], '-1')
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_8192': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_rate")))

    # checks if admin can't change read and archive visibility, name, locale can't be changed and isn't visible
    def test_guest_restricted_settings_visibility(self):
        rights = self.get_user_settings('Guest')
        self.assertIsNone(rights['show_512'])
        self.assertIsNone(rights['name'])
        self.assertIsNone(rights['show_256'])
        self.assertIsNone(rights['show_32768'])
        self.assertIsNone(rights['show_65536'])
        self.assertIsNone(rights['show_131072'])
        self.assertIsNone(rights['locale'])
        self.assertIsNone(rights['edit_shelf_role'])
        self.assertIsNone(rights['admin_role'])

    # checks if admin can change categories
    def test_guest_change_visibility_category(self):
        self.edit_user('Guest', {'show_8': 1})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.logout()
        self.assertTrue(self.check_element_on_page((By.ID, "nav_cat")))
        self.goto_page("nav_cat")
        books = self.get_list_books_displayed()
        self.assertEqual(books[0]['title'], 'Gênot')
        self.check_element_on_page((By.ID, "desc")).click()
        books = self.get_list_books_displayed()
        self.assertEqual(books[1]['title'], 'Gênot')
        self.check_element_on_page((By.ID, "asc")).click()
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'show_8': 0})
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        # Category not visible
        self.logout()
        self.assertFalse(self.check_element_on_page((By.ID, "nav_cat")))

    def test_check_locale_guest(self):
        self.goto_page('admin_setup')
        user = self.driver.find_elements(By.XPATH, "//table[@id='table_user']/tbody/tr/td/a")
        for ele in user:
            if ele.text == 'Guest':
                ele.click()
                self.assertTrue(self.check_element_on_page((By.ID, "email")))
                self.assertFalse(self.check_element_on_page((By.ID, "locale")))
                return
        self.assertTrue(False, "User account not found")