import os
import re
import time
from random import randint

import selenium
from dotenv import load_dotenv
from fake_useragent import UserAgent
from kalindro_custom_loguru_logger import default_logger as logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager

from src.pushbullet_client import PushbulletClient

load_dotenv()

logger.set_console_level("INFO")


class EthenaInitNotify:

    def __init__(self):
        self.URL = "https://app.init.capital/pool/0x3282437c436ee6aa9861a6a46ab0822d82581b1c?chain=5000"
        self.headless = True
        self.detach = False

    def main(self):
        driver = self.driver_init()
        driver.get(self.URL)
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//button[contains(@class, 'MuiButton-root')]")))

        button_xpath = "//button[contains(@class, 'MuiButton-root') and contains(text(), 'Continue')]"
        button = driver.find_element(By.XPATH, button_xpath)
        button.click()

        first_element_xpath = "/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/div[1]/div/div[1]/div/p"
        second_element_xpath = "/html/body/div[1]/div/div[3]/div/div[2]/div/div[1]/div[1]/div/div[2]/p"

        WebDriverWait(driver, 30).until(lambda d: re.search(r'\d+', d.find_element(By.XPATH, first_element_xpath).text))
        WebDriverWait(driver, 30).until(lambda d: re.search(r'\d+', d.find_element(By.XPATH, second_element_xpath).text))

        first_element_text = driver.find_element(By.XPATH, first_element_xpath).text
        second_element_text = driver.find_element(By.XPATH, second_element_xpath).text

        current_cap = int(round(float(re.sub(r'[^\d.]', '', first_element_text))))
        max_cap = int(round(float(re.sub(r'[^\d.]', '', second_element_text))))

        logger.info(f"Current cap: {current_cap}")
        logger.info(f"Max cap: {max_cap}")

        driver.quit()

        if max_cap - current_cap > 20_000:
            logger.success("CAP INCREASED")
            self.send_notification()
        else:
            logger.info("Still no cap increase, RIP")

    def driver_init(self) -> selenium.webdriver:
        logger.debug("Initializing chrome driver...")
        user_agent = UserAgent().chrome

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={user_agent}")

        if self.headless:
            options.add_argument('--headless=new')
        if self.detach:
            options.add_experimental_option("detach", True)  # To keep window open after

        service = ChromeService(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd(
            'Network.setUserAgentOverride', {
                "userAgent": user_agent
            }
        )

        logger.debug("Assertion - successfully found chrome driver")
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )
        logger.debug("Finished initializing driver")
        return driver

    @staticmethod
    def send_notification():
        notification_client = PushbulletClient()
        message = "THERE IS CAP ON INIT, GO FAST"
        notification_client.send_message(os.getenv("PUSHBULLET_API_TOKEN"), message)


if __name__ == '__main__':
    interval = randint(40, 50)
    while True:
        EthenaInitNotify().main()
        time.sleep(interval)
