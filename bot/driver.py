from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def setup_browser():
    options = Options()
    options.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(options=options)
    driver.get("https://web.whatsapp.com")
    input("🔒 QR scan kar len, phir Enter press karein... ")
    return driver
