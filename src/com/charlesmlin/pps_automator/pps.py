import os
import random
from pathlib import Path
from typing import List

from selenium import webdriver

from com.charlesmlin.pps_automator.page_processor import PageProcessor
from com.charlesmlin.pps_automator.util import Utils

PPS_WEBLINK = 'https://www.ppshk.com/pps/pps2/revamp2/template/pc/login_c.jsp'
MIN_CENTS = 0
MAX_CENTS = 4
EPSILON = 1e-6

MERCHANT_CODE = 24
AMOUNT_TO_PAY = 100.00


def get_payment_list(amount: float) -> List[float]:
    payment_list = []
    remaining_amount = amount
    payment = -1
    if amount > 3:
        last_random_value = 0
        while remaining_amount > 3:
            random_value = random.randint(MIN_CENTS, MAX_CENTS)
            while random_value == last_random_value:
                random_value = random.randint(MIN_CENTS, MAX_CENTS)
            payment = 1 + random_value / 100
            payment_list.append(round(payment, 2))
            remaining_amount -= payment
            last_random_value = random_value
    if remaining_amount > 2:
        final_payment = remaining_amount / 2
        while abs(payment - final_payment) < EPSILON or abs(remaining_amount - final_payment * 2) < EPSILON:
            final_payment -= 0.01
        payment_list.append(round(final_payment, 2))
        payment_list.append(round(remaining_amount - final_payment, 2))
    elif remaining_amount > 1:
        payment_list.append(round(remaining_amount, 2))
    return payment_list


def main(weblink: str, merchant_code: int, amount: float) -> None:
    payment_list: List[float] = get_payment_list(amount)
    print(f'Amount to pay = {"{:.2f}".format(sum(payment_list))}, payment times = {payment_list.__len__()}')
    print(f'Payment breakdown: {", ".join(map(lambda x: "{:.2f}".format(x), payment_list))}')

    with webdriver.Chrome() as driver:
        driver.get(weblink)
        processor = PageProcessor(driver)
        processor.process_login_page()
        for payment in payment_list:
            print(f'Paying Merchant with code {merchant_code} and amount {payment}')
            processor.process_merchant_list_page(merchant_code)
            processor.process_payment_page(payment)
            processor.process_confirm_payment_page()
            processor.process_pay_another_page()
    print('All Done')


if __name__ == '__main__':
    path: Path = Utils.get_path(Path(__file__), 'src')
    os.environ['PATH'] += os.pathsep + str(Path.joinpath(path.parent, 'libs'))
    main(PPS_WEBLINK, MERCHANT_CODE, AMOUNT_TO_PAY)
