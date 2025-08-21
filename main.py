from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
    WebDriverException
)
from dotenv import load_dotenv
import os

load_dotenv()

PROMISED_DOWN = 300
PROMISED_UP = 30
CHROME_DRIVER_PATH = "/Users/petarmacbook/Web Development Projects/chromedriver-mac-x64/chromedriver"
CHROME_BINARY_PATH = ("/Users/petarmacbook/Web Development Projects/chrome-mac-x64/Google Chrome for "
                      "Testing.app/Contents/MacOS/Google Chrome for Testing")

TWITTER_EMAIL = os.getenv("TWITTER_EMAIL")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
NAME = os.getenv("NAME")


class InternetSpeedTwitterBot:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = CHROME_BINARY_PATH
        chrome_options.add_experimental_option("detach", True)
        service = Service(CHROME_DRIVER_PATH)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 40)
        self.speed_down = None
        self.speed_up = None

    def get_internet_speed(self):
        try:
            self.driver.get("https://www.speedtest.net/")
            go_button = self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'span.start-text')))
            go_button.click()
            back_to_results = self.wait.until(
                ec.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div[1]/div[3]/div/div/div/div['
                                                      '2]/div[2]/div/div[4]/div/div[8]/div/div/div[2]/a')))
            back_to_results.click()
            self.speed_down = self.driver.find_element(By.XPATH,
                                                       '//*[@id="container"]/div[1]/div[3]/div/div/div/div[2]/div['
                                                       '2]/div/div[4]/div/div[3]/div/div/div[2]/div[1]/div['
                                                       '1]/div/div[2]/span').text
            self.speed_up = self.driver.find_element(By.XPATH, '//*[@id="container"]/div[1]/div[3]/div/div/div/div['
                                                               '2]/div['
                                                               '2]/div/div[4]/div/div[3]/div/div/div[2]/div[1]/div['
                                                               '2]/div/div['
                                                               '2]/span').text

            print(f"down: {self.speed_down}")
            print(f"up: {self.speed_up}")
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"Failed to measure internet speed: {e}")

    def tweet_at_provider(self):
        try:
            self.driver.get("https://x.com/i/flow/login")
            email = self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocapitalize="sentences"]')))
            email.click()
            email.send_keys(TWITTER_EMAIL, Keys.ENTER)
            safe_bar = self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[inputmode ="text"]')))
            safe_bar.click()
            safe_bar.send_keys(NAME, Keys.ENTER)
            password = self.wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[autocomplete="current-password"]')))
            password.send_keys(TWITTER_PASSWORD, Keys.ENTER)
            text_place_holder = self.wait.until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="public-DraftStyleDefault-block '
                                                             'public-DraftStyleDefault-ltr"]')))
            text_place_holder.click()
            text_place_holder.send_keys(
                f"Why is my internet speed {self.speed_down}/{self.speed_up} Mbs, when provider says it should be "
                f"300/30?")
            post_button = self.wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/div/div/div['
                                                                                '2]/main/div/div/div/div/div/div['
                                                                                '3]/div/div[2]/div['
                                                                                '1]/div/div/div/div[2]/div[2]/div['
                                                                                '2]/div/div/div/button/div/span/span')))
            post_button.click()

        except (NoSuchElementException, TimeoutException, ElementClickInterceptedException, WebDriverException) as e:
            print(f"Failed to tweet: {e}.")

    def close(self):
        self.driver.quit()


twitter_bot = InternetSpeedTwitterBot()

try:
    twitter_bot.get_internet_speed()

    if twitter_bot.speed_down and twitter_bot.speed_up:
        try:
            down_speed = float(twitter_bot.speed_down)
            up_speed = float(twitter_bot.speed_up)
            if down_speed < PROMISED_DOWN or up_speed < PROMISED_UP:
                twitter_bot.tweet_at_provider()
            else:
                print("Internet speed is within promised range. No tweet needed.")
        except ValueError:
            print("Could not convert speed values to float.")
    else:
        print("Speed test did not return valid results.")
finally:
    twitter_bot.close()
