import time
from typing import List, Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class PageProcessor:
    _driver: WebDriver

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def get_pay_button(self, merchant_code: int) -> WebElement or None:
        table_container: WebElement = self._driver.find_element_by_class_name('bgTable')
        rows: List[WebElement] = table_container.find_elements_by_tag_name('tr')
        rows = rows[2:-1]
        # headers = ['', 'Merchant_Code', 'Bill_Name', 'Bill_No', 'Last_Payment', 'Execute']
        for row in rows:
            cells: List[WebElement] = row.find_elements_by_tag_name('td')
            if cells[1].text == str(merchant_code):
                return cells[5].find_element_by_tag_name('img')
        return None

    def process_login_page(self) -> bool:
        all_filled = False
        while not all_filled:
            all_filled = True
            time.sleep(1)
            for element in ['PMA', 'PIN', 'captchaCode']:
                input_box: WebElement = self._driver.find_element_by_name(element)
                text = input_box.get_attribute('value')
                if text is None or text is '':
                    all_filled = False
                if element == 'captchaCode' and text.__len__() != 4:
                    all_filled = False
        print('All required fields on login page are filled')
        time.sleep(3)
        go_button: WebElement = self._driver.find_element_by_name('go')
        go_button.click()
        return True

    def process_merchant_list_page(self, merchant_code: int) -> bool:
        pay_button = self.get_pay_button(merchant_code)
        if pay_button is not None:
            pay_button.click()
            return True
        print(f'{merchant_code} not found')
        return False

    def process_payment_page(self, amount: float) -> bool:
        amount_element: WebElement = self._driver.find_element_by_name('AMOUNT')
        amount_element.send_keys('{:.2f}'.format(amount))
        proceed_button: WebElement = self._driver.find_element_by_name('proceedBut')
        captcha_list: List[WebElement] = self._driver.find_elements_by_name('captchaCode')
        if captcha_list.__len__() > 0:
            text = ''
            while text is None or text is '' or text.__len__() != 4:
                time.sleep(1)
                input_box: WebElement = self._driver.find_element_by_name('captchaCode')
                text = input_box.get_attribute('value')
            time.sleep(3)
        proceed_button.click()
        return True

    def process_confirm_payment_page(self) -> bool:
        images: List[WebElement] = self._driver.find_elements_by_tag_name('img')
        confirm_button: List[WebElement] = list(filter(lambda x: x.get_attribute('alt') == '繳款', images))
        if confirm_button.__len__() > 0:
            confirm_button[0].click()
            return True
        print('confirm button not found')
        return False

    def process_pay_another_page(self) -> bool:
        images: List[WebElement] = self._driver.find_elements_by_tag_name('img')
        pay_another_button: List[WebElement] = list(filter(lambda x: x.get_attribute('alt') == '繳付另一張賬單', images))
        if pay_another_button.__len__() > 0:
            pay_another_button[0].click()
            return True
        print('confirm button not found')
        return False
