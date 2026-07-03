import asyncio
import time
import os
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

class BurpTrafficCapture:
    def __init__(self, proxy_host="127.0.0.1", proxy_port=8080):
        self.proxy = f"{proxy_host}:{proxy_port}"

    async def capture(self, url, duration=30):
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, self._capture_sync, url, duration)
            return {"status": "captured", "proxy": self.proxy}
        except WebDriverException as e:
            return {"status": "failed", "error": str(e), "suggestion": "Install firefox and geckodriver, or use Chrome."}

    def _capture_sync(self, url, duration):
        # Try Firefox first, fallback to Chrome if not available
        options = webdriver.FirefoxOptions()
        options.add_argument(f'--proxy-server={self.proxy}')
        options.add_argument('--headless')
        try:
            driver = webdriver.Firefox(options=options)
        except:
            # Fallback to Chrome
            from selenium.webdriver.chrome.options import Options
            chrome_options = Options()
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
            chrome_options.add_argument('--headless')
            driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(duration)
        driver.quit()
