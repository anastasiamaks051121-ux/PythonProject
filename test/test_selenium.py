from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_search_events():
    driver = webdriver.Chrome()

    try:
        driver.get("https://fon.bet/")

        wait = WebDriverWait(driver, 15)

        search = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "span[resource-name='searchThick']")
            )
        )

        search.click()

        text_box = driver.find_element(
            By.CSS_SELECTOR,
            "input[placeholder='Enter name of team or competition']"
        )

        text_box.send_keys("Capitals")

        message = wait.until(
            EC.visibility_of_element_located(
                (By.CLASS_NAME, "text--JsVbp")
            )
        )

        assert message.text == "EVENTS"

    finally:
        driver.quit()