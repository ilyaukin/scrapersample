import os
import random
import traceback
from os import environ
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from twocaptcha import TwoCaptcha


def gen_name() -> str:
    letters = list('jkasdvlsvlnadsjkvlnjkldsasvdvniwpbvubclvbccuyapiucahihovbnoipyqbduiocdbn')
    random.shuffle(letters)
    namelen = random.randint(10, 15)
    return ''.join(letters[:namelen])


# page object,  like a big boy
class Page(object):
    driver: webdriver.Chrome

    def __init__(self, driver, **kwargs):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, timeout=kwargs.get('timeout', 10))

    def open(self, url: str):
        self.driver.get(url)

    def close(self):
        self.driver.quit()

    def take_screenshot(self, filename: str):
        self.driver.save_screenshot(filename)


class RegisterPage(Page):

    def __init__(self, driver, **kwargs):
        super().__init__(driver, **kwargs)
        self.URL = 'https://www.reddit.com/register/'
        self.solver_api_key = kwargs.get('solver_api_key')

    def newacc(self, name: str):
        self.open(self.URL)
        driver = self.driver
        wait = self.wait
        element = driver.find_element(By.CSS_SELECTOR, '#regEmail')
        element.send_keys(name + "@mailinator.com" + "\n")
        element = driver.find_element(By.CSS_SELECTOR, 'button[data-step="email"]')
        element.click()
        element = driver.find_element(By.CSS_SELECTOR, '#regUsername')
        wait.until(lambda d: element.is_displayed())
        element.send_keys(name)
        element = driver.find_element(By.CSS_SELECTOR, '#regPassword')
        element.send_keys('aboba123')

        # recapctha
        solver = TwoCaptcha(self.solver_api_key)

        result = solver.recaptcha(sitekey='6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC',
                                  url=self.URL)
        element = driver.find_element(By.CSS_SELECTOR, '#g-recaptcha-response')
        driver.execute_script(f'arguments[0]'
                              f'.value = "{result["code"]}"', element)

        element = driver.find_element(By.CSS_SELECTOR, 'button[data-step="username-and-password"]')
        element.click()

        wait.until(lambda d: 'register' not in driver.current_url)


class BrowserFactory(object):
    headless: bool
    proxy_list: Optional[list[str]]
    proxy: Optional[str]

    def __init__(self):
        self.headless = False
        self.proxy = None
        self.proxy_list = None
        self.proxy_number = None

    def with_proxies(self, filename):
        with open(filename, 'r') as f:
            self.proxy_list = f.readlines()
            self.proxy_number = 0
        return self

    def with_headless(self):
        self.headless = True
        return self

    def get(self):
        chrome_options = webdriver.ChromeOptions()
        seleniumwire_options = None

        if self.proxy_list:
            self.proxy = self.proxy_list[self.proxy_number]
            self.proxy_number = (self.proxy_number + 1) % len(self.proxy_list)

        if self.proxy:
            seleniumwire_options = {
                'proxy': {
                    'http': f'http://{self.proxy}',
                    'verify_ssl': False,
                }
            }

        if self.headless:
            chrome_options.add_argument('--headless')

        return webdriver.Chrome(chrome_options=chrome_options,
                                seleniumwire_options=seleniumwire_options)


if __name__ == '__main__':
    solver_api_key = environ.get('SAMPLESCRAPER_2CAPCTHA_API_KEY')
    proxies_filename = environ.get('SAMPLESCRAPER_PROXIES')
    n = environ.get('SAMPLESCRAPER_N', '1')
    is_headless = environ.get('SAMPLESCRAPER_HEADLESS')
    screenshot_folder = environ.get('SAMPLESCRAPER_SCREENSHOT_FOLDER', '.screenshots')

    browser_factory = BrowserFactory()
    if proxies_filename:
        browser_factory.with_proxies(proxies_filename)
    if is_headless:
        browser_factory.with_headless()

    success_count = 0
    for i in range(int(n)):
        page = RegisterPage(browser_factory.get(), solver_api_key=solver_api_key)
        try:
            page.newacc(gen_name())
            success_count += 1
        except:
            print(traceback.format_exc())
        finally:
            os.makedirs(screenshot_folder, exist_ok=True)
            page.take_screenshot(f'{screenshot_folder}/{i}.png')
            page.close()

    print(f'{success_count}/{n} new accounts are registered successfully')
