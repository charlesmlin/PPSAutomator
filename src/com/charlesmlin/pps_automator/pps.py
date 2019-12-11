import os
import random
from pathlib import Path
from typing import List, Callable

from src.com.charlesmlin.pps_automator.driver import BrowserDriver
from src.com.charlesmlin.pps_automator.gui_input import TkInput
from src.com.charlesmlin.pps_automator.page_processor import PageProcessor
from src.com.charlesmlin.pps_automator.util import Utils

PPS_WEBLINK = 'https://www.ppshk.com/pps/pps2/revamp2/template/pc/login_c.jsp'
MIN_CENTS = 0
MAX_CENTS = 4
EPSILON = 1e-6
MAX_RETRY_COUNT = 5
DEFAULT_DRIVER = BrowserDriver.CHROME


def add_driver_to_path(driver: BrowserDriver) -> None:
    print(f'checking if {driver.name.lower()} driver installation is needed')
    func: Callable = driver.value[0]
    if func is not None:
        driver_path: Path = func()
        if driver_path is not None:
            os.environ['PATH'] += os.pathsep + str(driver_path.parent)
    print(f'{driver.name.lower()} driver is installed and added to PATH')


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
        final_payment = round(remaining_amount / 2, 2)
        while abs(payment - final_payment) < EPSILON or abs(remaining_amount - final_payment * 2) < EPSILON:
            final_payment -= 0.01
        payment_list.append(round(final_payment, 2))
        payment_list.append(round(remaining_amount - final_payment, 2))
    elif remaining_amount >= 1:
        payment_list.append(round(remaining_amount, 2))
    return payment_list


def main(weblink: str, user_input: TkInput, browser_driver: BrowserDriver) -> None:
    total_amount: float = user_input.get_payment_amount()
    payment_list: List[float] = get_payment_list(total_amount)
    remaining_amount = total_amount
    print(f'Amount to pay = {"{:.2f}".format(sum(payment_list))}, payment times = {len(payment_list)}')
    print(f'Payment breakdown: {", ".join(map(lambda x: "{:.2f}".format(x), payment_list))}')

    remote_driver = browser_driver.value[1]
    with remote_driver() as driver:
        driver.get(weblink)
        processor = PageProcessor(driver)
        try:
            success = Utils.run_with_retry(processor.process_login_page,
                                           [user_input.get_username(), user_input.get_password()], MAX_RETRY_COUNT)
            if not success:
                print(f'Login failure after {MAX_RETRY_COUNT} attempt(s)')
            else:
                for payment in payment_list:
                    print(f'Paying merchant with code {user_input.get_merchant_code()}. '
                          f'Remaining amount = {"{:.2f}".format(remaining_amount)}. '
                          f'Next payment = {"{:.2f}".format(payment)}')
                    processor.process_merchant_list_page(user_input.get_merchant_code())
                    Utils.run_with_retry(processor.process_payment_page, [payment], MAX_RETRY_COUNT)
                    processor.process_confirm_payment_page()
                    remaining_amount = round(remaining_amount - payment, 2)
                    processor.process_pay_another_page()
        except Exception:
            pass
        if remaining_amount > 0:
            print(f'Not all is done. Paid amount = {"{:.2f}".format(total_amount - remaining_amount)}. '
                  f'Remaining amount = {"{:.2f}".format(remaining_amount)}')
        else:
            print('All Done')


if __name__ == '__main__':
    path: Path = Utils.get_project_path()
    if path is not None:
        os.environ['PATH'] += os.pathsep + str(path.joinpath('libs'))
    add_driver_to_path(DEFAULT_DRIVER)
    tk_input = TkInput()
    tk_input.show_front_end()
    main(PPS_WEBLINK, tk_input, DEFAULT_DRIVER)
