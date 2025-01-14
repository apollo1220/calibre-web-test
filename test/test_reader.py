#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from helper_ui import ui_class
from config_test import TEST_DB, base_path
from helper_func import startup, debug_startup, add_dependency, remove_dependency
from selenium.webdriver.common.by import By
from helper_func import save_logfiles, createcbz
import time
import os
from diffimg import diff
from io import BytesIO
import rarfile
from PIL import Image

class TestReader(unittest.TestCase, ui_class):

    p = None
    driver = None

    @classmethod
    def setUpClass(cls):

        try:
            startup(cls, cls.py_version, {'config_calibre_dir':TEST_DB}, env={"APP_MODE": "test"})
            cls.current_handle = cls.driver.current_window_handle

        except Exception:
            cls.driver.quit()
            cls.p.terminate()
            cls.p.poll()

    @classmethod
    def tearDown(cls):
        new_handle = cls.driver.current_window_handle
        if new_handle != cls.current_handle:
            cls.driver.close()
            cls.driver.switch_to.window(cls.current_handle)

    @classmethod
    def tearDownClass(cls):
        cls.driver.switch_to.window(cls.current_handle)
        cls.driver.get("http://127.0.0.1:8083")
        cls.stop_calibre_web()
        cls.driver.quit()
        cls.p.terminate()
        # close the browser window and stop calibre-web
        # remove_dependency(cls.dependency)
        save_logfiles(cls, cls.__name__)


    def test_txt_reader(self):
        self.get_book_details(1)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("txt" in read_button.text)
        read_button.click()
        #self.check_element_on_page((By.ID, "read-in-browser")).click()
        #current_handles = self.driver.window_handles
        #self.check_element_on_page((By.XPATH, "//ul[@aria-labelledby='read-in-browser']/li/a[contains(.,'txt')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        time.sleep(3)
        content = self.check_element_on_page((By.ID, "content"))
        self.assertTrue(content)
        self.assertTrue('hörte' in content.text, 'Encoding of textfile viewer is not respected properly')

    def test_epub_reader(self):
        self.get_book_details(8)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("epub" in read_button.text)
        read_button.click()
        #self.check_element_on_page((By.ID, "read-in-browser")).click()
        #current_handles = self.driver.window_handles
        #self.check_element_on_page((By.XPATH, "//ul[@aria-labelledby='read-in-browser']/li/a[contains(.,'epub')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        self.driver.switch_to.frame(self.check_element_on_page((By.XPATH,"//iframe[starts-with(@id, 'epubjs-view')]")))
        content = self.driver.find_elements(By.CLASS_NAME, "calibre1")
        # content = self.check_element_on_page((By.XPATH, "//@id=viewer/")) # "//div[@id='viewer']/div" [starts-with(@id, 'serie_')]"
        self.assertTrue(content)
        self.assertTrue('Überall dieselbe alte Leier.' in content[1].text)
        self.driver.switch_to.default_content()
        self.driver.close()
        self.driver.switch_to.window(self.current_handle)
        # remove viewer rights
        self.edit_user('admin', {'viewer_role': 0})
        self.get_book_details(8)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        self.assertFalse(self.check_element_on_page((By.ID, "readbtn")))
        self.edit_user('admin', {'viewer_role': 1})


    def test_pdf_reader(self):
        self.get_book_details(13)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("pdf" in read_button.text)
        read_button.click()
        #self.check_element_on_page((By.ID, "read-in-browser")).click()
        #current_handles = self.driver.window_handles
        #self.check_element_on_page((By.XPATH, "//ul[@aria-labelledby='read-in-browser']/li/a[contains(.,'pdf')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        time.sleep(3)
        content = self.driver.find_elements(By.XPATH, "//div[@class='textLayer']/span")
        self.assertTrue(content)
        self.assertTrue('Lorem ipsum dolor sit amet, consectetuer adipiscing elit' in content[0].text)
        self.driver.close()
        self.driver.switch_to.window(self.current_handle)
        self.fill_basic_config({'config_anonbrowse': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.edit_user('Guest', {'viewer_role': 1})
        self.logout()
        self.get_book_details(13)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("pdf" in read_button.text)
        read_button.click()
        #self.check_element_on_page((By.ID, "read-in-browser")).click()
        #current_handles = self.driver.window_handles
        #self.check_element_on_page((By.XPATH, "//ul[@aria-labelledby='read-in-browser']/li/a[contains(.,'pdf')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        time.sleep(3)
        self.assertFalse(self.check_element_on_page((By.ID, "print")))
        self.assertFalse(self.check_element_on_page((By.ID, "download")))
        self.driver.close()
        self.driver.switch_to.window(self.current_handle)
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.edit_user('Guest', {'download_role': 1})
        self.logout()
        self.get_book_details(13)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("pdf" in read_button.text)
        read_button.click()
        #self.check_element_on_page((By.ID, "read-in-browser")).click()
        #self.check_element_on_page((By.XPATH, "//ul[@aria-labelledby='read-in-browser']/li/a[contains(.,'pdf')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "print")))
        self.assertTrue(self.check_element_on_page((By.ID, "download")))
        self.driver.close()
        self.driver.switch_to.window(self.current_handle)
        self.check_element_on_page((By.ID, "top_user")).click()
        self.login('admin', 'admin123')
        self.fill_basic_config({'config_anonbrowse': 0})

    def test_comic_reader(self):
        self.get_book_details(3)
        self.assertFalse(self.check_element_on_page((By.ID, "read-in-browser")))
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("cbr" in read_button.text)
        read_button.click()
        # self.check_element_on_page((By.XPATH, "//ul[@aria-labelledby='read-in-browser']/li/a[contains(.,'cbr')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        self.assertTrue(self.check_element_on_page((By.ID, "mainContent")))
        with rarfile.RarFile(os.path.join(TEST_DB,"Asterix Lionherd", "comicdemo (3)",
                                          "comicdemo - Asterix Lionherd.cbr")) as rf:
            pic1 = rf.read("comic0.jpg")
            pic2 = rf.read("comic1.jpg")
            pic3 = rf.read("comic2.jpg")
        img1 = Image.open(BytesIO(pic1)).convert(mode="RGBA")
        img2 = Image.open(BytesIO(pic2)).convert(mode="RGBA")
        img3 = Image.open(BytesIO(pic3)).convert(mode="RGBA")
        with BytesIO() as output:
            img1.save(output, format="PNG")
            pic1 = output.getvalue()
        with BytesIO() as output:
            img2.save(output, format="PNG")
            pic2 = output.getvalue()
        with BytesIO() as output:
            img3.save(output, format="PNG")
            pic3 = output.getvalue()
        # ToDO: Check displayed content
        first_page = self.check_element_on_page((By.ID, "mainContent"))
        self.assertTrue(first_page)
        pic = first_page.screenshot_as_png
        self.assertLessEqual(diff(BytesIO(pic1), BytesIO(pic), delete_diff_file=True), 0.02)
        self.assertFalse(self.check_element_on_page((By.ID, "left")).is_displayed())
        right = self.check_element_on_page((By.ID, "right"))
        self.assertTrue(right.is_displayed())
        right.click()
        second_page = self.check_element_on_page((By.ID, "mainContent"))
        self.assertTrue(second_page)
        pic_2 = second_page.screenshot_as_png
        self.assertLessEqual(diff(BytesIO(pic2), BytesIO(pic_2), delete_diff_file=True), 0.04)
        time.sleep(0.5)
        self.assertTrue(right.is_displayed())
        self.assertTrue(self.check_element_on_page((By.ID, "left")).is_displayed())
        right.click()
        third_page = self.check_element_on_page((By.ID, "mainContent"))
        self.assertTrue(third_page)
        pic_3 = third_page.screenshot_as_png
        self.assertLessEqual(diff(BytesIO(pic2), BytesIO(pic_3), delete_diff_file=True), 0.04)
        # Last page arrow not visible
        self.assertFalse(right.is_displayed())
        self.assertTrue(self.check_element_on_page((By.ID, "left")).is_displayed())
        setting = self.check_element_on_page((By.ID, "setting"))
        window_size = self.driver.get_window_size()
        self.assertTrue(setting)
        setting.click()
        setting = self.check_element_on_page((By.ID, "fitWidth"))
        self.assertTrue(setting)
        setting.click()
        self.check_element_on_page((By.CLASS_NAME, "closer")).click()
        '''Scale auf width einstellen
            Bild muss viel größer erscheinen

        Bild muss größer als Ansicht sein (scale width):
            Scrollbar rechts in Hauptanzeige sichtbar
            umstellen hide scrollbar rechts in Hauptanzeige nicht sichtbar
        Scrollbar auf sichtbar einstellen'''
        horizontal_scroll_status = self.driver.execute_script(
            "return document.documentElement.scrollWidth>document.documentElement.clientWidth;")

    def test_single_file_comic(self):
        upload_file = os.path.join(base_path, 'files', 'book_test.cbz')
        # upload webp book
        zipdata = [os.path.join(base_path, 'files', 'cover.jpg')]
        names = ['cover1.jpg']
        createcbz(upload_file, zipdata, names)
        self.fill_basic_config({'config_uploading': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.goto_page('nav_new')
        upload = self.check_element_on_page((By.ID, 'btn-upload'))
        upload.send_keys(upload_file)
        time.sleep(2)
        self.check_element_on_page((By.ID, 'edit_cancel')).click()
        time.sleep(2)
        details = self.get_book_details()
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("cbz" in read_button.text)
        read_button.click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        self.assertFalse(self.check_element_on_page((By.ID, "left")).is_displayed())
        self.assertFalse(self.check_element_on_page((By.ID, "right")).is_displayed())
        self.driver.close()
        self.driver.switch_to.window(current_handles[0])
        self.delete_book(details['id'])
        os.remove(upload_file)

        self.fill_basic_config({'config_uploading': 0})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        
        # Comic file mit einer Datei

    def test_cb7_reader(self):
        self.fill_basic_config({'config_uploading': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.goto_page('nav_new')
        upload_file = os.path.join(base_path, 'files', 'book.cb7')
        upload = self.check_element_on_page((By.ID, 'btn-upload'))
        upload.send_keys(upload_file)
        time.sleep(3)
        self.check_element_on_page((By.ID, 'edit_cancel')).click()
        time.sleep(2)
        details = self.get_book_details()
        self.assertEqual('Test 执 to', details['title'])
        self.assertEqual('Author Nameless', details['author'][0])
        self.assertEqual('2', details['series_index'])
        self.assertEqual('No S', details['series'])
        self.delete_book(int(self.driver.current_url.split('/')[-1]))
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.fill_basic_config({'config_uploading': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        

    def test_comic_MACOS_files(self):
        upload_file = os.path.join(base_path, 'files', 'book1.cbz')
        # upload webp book
        zipdata = [os.path.join(base_path, 'files', 'cover.webp'),
                   os.path.join(base_path, 'files', 'cover.webp'),
                   os.path.join(base_path, 'files', 'cover.jpg')]
        names = ['cover1.weBp', 'cover2.weBp', "/__MACOSX/cover.jpg"]
        createcbz(upload_file, zipdata, names)
        self.fill_basic_config({'config_uploading': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        createcbz(upload_file, zipdata, names)
        self.goto_page('nav_new')
        upload = self.check_element_on_page((By.ID, 'btn-upload'))
        upload.send_keys(upload_file)
        time.sleep(2)
        self.check_element_on_page((By.ID, 'edit_cancel')).click()
        time.sleep(2)
        details = self.get_book_details()
        current_handles = self.driver.window_handles
        read_button = self.check_element_on_page((By.ID, "readbtn"))
        self.assertTrue("cbz" in read_button.text)
        read_button.click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        self.assertTrue(self.check_element_on_page((By.ID, "mainContent")))
        page = self.check_element_on_page((By.CLASS_NAME, "mainImage")).screenshot_as_png
        right = self.check_element_on_page((By.ID, "right"))
        self.assertTrue(right)
        right.click()
        right_page = self.driver.find_elements(By.CLASS_NAME, "mainImage")[1].screenshot_as_png
        self.assertAlmostEqual(diff(BytesIO(page), BytesIO(right_page), delete_diff_file=True), 0.0, delta=0.0001)
        left = self.check_element_on_page((By.ID, "left"))
        self.assertTrue(left)
        left.click()
        left_page = self.driver.find_elements(By.CLASS_NAME, "mainImage")[0].screenshot_as_png
        self.assertAlmostEqual(diff(BytesIO(page), BytesIO(left_page), delete_diff_file=True), 0.0, delta=0.0001)
        self.driver.close()
        self.driver.switch_to.window(current_handles[0])
        self.delete_book(details['id'])
        os.remove(upload_file)
        self.fill_basic_config({'config_uploading': 0})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        

    def sound_test(self, file_name, title, duration):
        self.goto_page('nav_new')
        upload_file = os.path.join(base_path, 'files', file_name)
        upload = self.check_element_on_page((By.ID, 'btn-upload'))
        upload.send_keys(upload_file)
        time.sleep(2)
        self.check_element_on_page((By.ID, 'edit_cancel')).click()
        details = self.get_book_details()
        self.assertFalse(self.check_element_on_page((By.ID, "listen-in-browser")))
        #self.check_element_on_page((By.ID, "listen-in-browser")).click()
        current_handles = self.driver.window_handles
        listen_button = self.check_element_on_page((By.ID, "listenbtn"))
        self.assertTrue(os.path.splitext(file_name)[1][1:] in listen_button.text)
        listen_button.click()
        #self.check_element_on_page((By.XPATH,
        #                            "//ul[@aria-labelledby='listen-in-browser']/li/a[contains(.,'" + os.path.splitext(file_name)[1][1:] + "')]")).click()
        new_handle = [x for x in self.driver.window_handles if x not in current_handles]
        if len(new_handle) != 1:
            self.assertFalse('Not exactly one new tab was opened')
        self.driver.switch_to.window(new_handle[0])
        time.sleep(2)
        play_button = self.check_element_on_page((By.CLASS_NAME, "sm2-icon-play-pause"))
        self.assertTrue(play_button)
        play_button.click()
        time.sleep(2)
        title_item = self.check_element_on_page((By.XPATH, "//ul[@class='sm2-playlist-bd']/li"))
        self.assertTrue(title_item)
        if title_item.text.startswith("✖ ✖") and os.name == 'nt':
            self.assertEqual(title, title_item.text,
                             "May fail due to inactive sound output on Windows Remotedesktop connection")
        else:
            self.assertEqual(title, title_item.text)
        duration_item = self.check_element_on_page((By.CLASS_NAME, "sm2-inline-duration"))
        self.assertTrue(duration_item)
        self.assertEqual(duration, duration_item.text)
        self.driver.close()
        self.driver.switch_to.window(self.current_handle)
        self.delete_book(int(details['id']))


    def test_sound_listener(self):
        self.fill_basic_config({'config_uploading': 1})
        time.sleep(3)
        self.assertTrue(self.check_element_on_page((By.ID, "flash_success")))
        self.edit_user('admin', {'upload_role': 1})
        self.sound_test('music.flac', 'Unknown - music', '0:02')
        self.sound_test('music.mp3', 'Unknown - music', '0:02')
        self.sound_test('music.ogg', 'Unknown - music', '0:02')
        self.sound_test('music.opus', 'Unknown - music', '0:02')
        self.sound_test('music.wav', 'Unknown - music', '0:02')
        self.sound_test('music.mp4', 'Unknown - music', '0:02')
        self.fill_basic_config({'config_uploading': 0})
        time.sleep(3)

