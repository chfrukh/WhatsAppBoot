from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time, os

def setup_browser():
    options = Options()
    driver = webdriver.Firefox(options=options)
    driver.get("https://web.whatsapp.com")
    input("🔒 QR scan kar len, phir Enter press karein... ")
    return driver

def send_message(driver, number, message):
    url = f"https://web.whatsapp.com/send?phone={number}&text={message}"
    driver.get(url)
    try:
        time.sleep(10)
        send_btn = driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
        send_btn.click()
        return "Sent"
    except Exception as e:
        return f"Error: {str(e)}"

def send_all(contacts, message, media_path=None):
    driver = setup_browser()
    count = 0
    log = []

    for contact in contacts:
        result = send_message(driver, contact["number"], message)
        log.append((contact["number"], result))
        count += 1

        if count % 5 == 0:
            time.sleep(150)
        if count % 250 == 0:
            time.sleep(3600)

    driver.quit()
    return log
