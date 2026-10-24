# def add(a, b):
#     return a + b
#
# print(add(1, 2))==3

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

driver.get("https://fon.bet/")

buttons = driver.find_elements(By.TAG_NAME, "button")

for i, button in enumerate(buttons):
    print(f"\n========== BUTTON {i} ==========")
    print(button.get_attribute("outerHTML"))

# input("\nНажми Enter для закрытия...")
#
# driver.quit()

