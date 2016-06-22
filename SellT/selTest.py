#coding: utf8
#from django.shortcuts import redirect
#######################################
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/index/")
        driver.find_element_by_link_text('Боржники').click()
        driver.find_element_by_link_text('Арбітражні керуючі').click()
        driver.find_element_by_link_text('Судді').click()
        driver.find_element_by_link_text('Суди').click()
        driver.find_element_by_xpath("html/body/div[2]/div/div[1]/div/div[1]/div/div[2]/a").click()
        #
        djName = driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div[1]/input")
        djName.clear()
        djName.send_keys("TestName");
        djSname = driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div[2]/input")
        djSname.send_keys("TestName");
        djMname = driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/div[3]/input")
        djMname.send_keys("222");
        driver.find_element_by_xpath("html/body/div[2]/div/div/div/form/button").click()
        # try:
        #     driver.find_element_by_xpath("html/body/div[2]/div/div[1]/div/div[2]")
        # except NoSuchElementException:
        #     return False
        # return True
        driver.get("http://127.0.0.1:8000/index/")
        driver.find_element_by_link_text('Граф').click()
        # self.assertIn("Python", driver.title)
        # elem = driver.find_element_by_name("q")
        # elem.send_keys("pycon")
        # assert "No results found." not in driver.page_source
        # elem.send_keys(Keys.RETURN)

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
