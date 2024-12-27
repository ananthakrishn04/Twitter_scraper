# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.keys import Keys
# from pymongo import MongoClient
# import time
# import uuid
# import datetime
# import requests

# def scrape_twitter_trends():
#     # Configure ProxyMesh
#     PROXY = "http://USERNAME:PASSWORD@proxy.proxyMesh.com:port"
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument(f'--proxy-server={PROXY}')
    
#     # Set up WebDriver
#     service = Service('/path/to/chromedriver')  # Update the path to chromedriver
#     driver = webdriver.Chrome(service=service, options=chrome_options)
    
#     # Log in to Twitter
#     driver.get("https://twitter.com/login")
#     time.sleep(5)
    
#     username = driver.find_element(By.NAME, "text")
#     username.send_keys("your_twitter_username")
#     username.send_keys(Keys.RETURN)
#     time.sleep(2)
    
#     password = driver.find_element(By.NAME, "password")
#     password.send_keys("your_twitter_password")
#     password.send_keys(Keys.RETURN)
#     time.sleep(5)

#     # Scrape "What's Happening"
#     trends = driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Timeline: Trending')]//span")[:5]
#     trend_names = [trend.text for trend in trends]
#     driver.quit()
    
#     # MongoDB integration
#     client = MongoClient("mongodb://localhost:27017/")
#     db = client["stir_tech_task"]
#     collection = db["twitter_trends"]
    
#     # Create record
#     record = {
#         "_id": str(uuid.uuid4()),
#         "trend1": trend_names[0],
#         "trend2": trend_names[1],
#         "trend3": trend_names[2],
#         "trend4": trend_names[3],
#         "trend5": trend_names[4],
#         "datetime": datetime.datetime.now(),
#         "ip_address": requests.get("https://api.ipify.org").text
#     }
#     collection.insert_one(record)
#     return record

import requests
from bs4 import BeautifulSoup
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from django.conf import settings
import time
import os
import zipfile
import tempfile

class TwitterTrendsScraper:
    def __init__(self,username,password,email):
        # Setup logging
        self.username = username
        self.email = email
        self.password = password

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Create and load proxy extension
        proxy_extension = self.create_proxy_extension('us-ca.proxymesh.com', '31280', settings.PROXY_USERNAME, settings.PROXY_PASSWORD)
        

        chrome_options = webdriver.ChromeOptions() 
        # chrome_options.add_extension(proxy_extension)

        chrome_options.add_argument("headless")  # Run in headless mode
        chrome_options.add_argument("no-sandbox")  # Bypass OS security model
        chrome_options.add_argument('disable-blink-features=AutomationControlled')

        self.chromeDriver = webdriver.Chrome(options=chrome_options)
        # self.chromeDriver = webdriver.Chrome()

        # self.chromeDriver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        # self.chromeDriver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
        os.remove(proxy_extension)

    def create_proxy_extension(self,proxy_host, proxy_port, proxy_username, proxy_password):
        """
        Create a Chrome extension to handle proxy authentication
        """

        temp_dir = tempfile.gettempdir()
        plugin_path = os.path.join(temp_dir, 'proxy_auth_plugin.zip')

        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: %s
                },
                bypassList: ["localhost"]
            }
        };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """ % (proxy_host, proxy_port, proxy_username, proxy_password)


        with zipfile.ZipFile(plugin_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        
        return plugin_path

    def scrape_twitter_trends(self,email=None, password=None ,username=None):
        driver = self.chromeDriver
        if not email:
            email = self.email        
        if not password:
            password = self.password
        if not username:
            username = self.username
        
        try:
            # Go to Twitter login page
            driver.get("https://x.com/explore")
            time.sleep(3)  # Wait for page to load
            
            # Fill in username
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            email_field.send_keys(email)
                
            # Click Next
            buttons = driver.find_elements(By.CSS_SELECTOR, '[role="button"]')
            buttons[-3].click()
            time.sleep(2)

            try:
                profilename_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="text"]'))
                )
                profilename_field.send_keys(username)

                login_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="ocfEnterTextNextButton"]'))
                )

                login_button.click()
                time.sleep(2)
            except:
                pass
            
            # Fill in password
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
            )
            password_field.send_keys(password)
            
            # Click Login
            login_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="LoginForm_Login_Button"]')
            login_button.click()
            
            # Wait for login to complete and navigate to explore page
            time.sleep(5)
            
            # Wait for trends to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="trend"]'))
            )
            
            # Get all trend elements
            trend_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="trend"]')
            
            trends = []
            for element in trend_elements:
                try:
                    category = element.find_element(By.CSS_SELECTOR, '.r-n6v787').text
                    topic = element.find_element(By.CSS_SELECTOR, '.r-b88u0q').text
                    posts = element.find_elements(By.CSS_SELECTOR, '.r-n6v787')[-1].text
                    
                    trends.append({
                        'category': category,
                        'topic': topic,
                        'posts': posts
                    })
                except Exception as e:
                    print(f"Error parsing trend: {e}")
            
            self.logger.info(f"Successfully scraped {len(trends)} trending topics")

            return trends , self.test_proxy_connection(driver)
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return None
            
        finally:
            driver.quit()

    def test_proxy_connection(self,driver):
        try:
            # Visit a site that shows your IP
            driver.get("https://api.ipify.org")
            time.sleep(2)
            
            # Print the IP address
            ip = driver.find_element(By.TAG_NAME, 'body').text
            
            return ip
    
        except Exception as e:
            print(f"Proxy test failed: {e}")
            return None


    def run_scraper(self, num_attempts=3, delay_between_attempts=5):
        """Run the scraper with multiple attempts and delay between them"""
        for attempt in range(num_attempts):
            self.logger.info(f"Scraping attempt {attempt + 1} of {num_attempts}")
            
            results = self.scrape_twitter_trends()
            if results:
                return results
                
            if attempt < num_attempts - 1:
                time.sleep(delay_between_attempts)
        
        self.logger.error("All scraping attempts failed")
        return None

