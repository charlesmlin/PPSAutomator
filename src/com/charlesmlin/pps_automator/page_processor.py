import os
import time
from pathlib import Path
from typing import List

from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from src.com.charlesmlin.captcha_fetcher.util import CaptchaUtils


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

    def process_login_page(self, username: str, password: str) -> bool:
        username_element: WebElement = self._driver.find_element_by_name('PMA')
        username_element.send_keys(username)
        password_element: WebElement = self._driver.find_element_by_name('PIN')
        password_element.send_keys(password)
        image_element: WebElement = self._driver.find_element_by_id('exampleCaptchaTag_CaptchaImage')
        reload_element: WebElement = self._driver.find_element_by_id('exampleCaptchaTag_ReloadLink')
        captcha_text = self.get_captcha_text(image_element, reload_element)
        captcha_element: WebElement = self._driver.find_element_by_name('captchaCode')
        captcha_element.send_keys(captcha_text)
        go_button: WebElement = self._driver.find_element_by_name('go')
        go_button.click()
        try:
            alert: Alert = self._driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            return True
        else:
            return False

    @staticmethod
    def get_captcha_text(image_element: WebElement, reload_element: WebElement) -> str:
        captcha_text = ''
        while len(captcha_text) != 4:
            img_path = Path(os.getenv('TEMP')).joinpath('captcha.png')
            image_element.screenshot(str(img_path))
            time.sleep(1)
            captcha_text = CaptchaUtils.predict(img_path)
            if len(captcha_text) != 4:
                reload_element.click()
        return captcha_text

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
        if len(captcha_list) > 0:
            image_element: WebElement = self._driver.find_element_by_id('exampleCaptchaTag_CaptchaImage')
            reload_element: WebElement = self._driver.find_element_by_id('exampleCaptchaTag_ReloadLink')
            captcha_text = self.get_captcha_text(image_element, reload_element)
            captcha_list[0].send_keys(captcha_text)
        # if len(captcha_list) > 0:
        #     text = ''
        #     while text is None or text is '' or len(text) != 4:
        #         time.sleep(1)
        #         input_box: WebElement = self._driver.find_element_by_name('captchaCode')
        #         text = input_box.get_attribute('value')
        #     time.sleep(3)
        proceed_button.click()
        try:
            alert: Alert = self._driver.switch_to.alert
            alert.accept()
        except NoAlertPresentException:
            return True
        else:
            return False

    def process_confirm_payment_page(self) -> bool:
        images: List[WebElement] = self._driver.find_elements_by_tag_name('img')
        confirm_button: List[WebElement] = list(filter(lambda x: x.get_attribute('alt') == '繳款', images))
        if len(confirm_button) > 0:
            confirm_button[0].click()
            return True
        print('confirm button not found')
        return False

    def process_pay_another_page(self) -> bool:
        images: List[WebElement] = self._driver.find_elements_by_tag_name('img')
        pay_another_button: List[WebElement] = list(filter(lambda x: x.get_attribute('alt') == '繳付另一張賬單', images))
        if len(pay_another_button) > 0:
            pay_another_button[0].click()
            return True
        print('confirm button not found')
        return False
