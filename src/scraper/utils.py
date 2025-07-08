from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def has_next_page(driver):
    # Verificamos se tem a próxima página
    driver.switch_to.default_content()
    try:
        driver.find_element(By.XPATH, "//a[contains(text(), 'Próximo>')]")
        return True
    except NoSuchElementException:
        return False


def go_to_next_page(driver):
    # Navegamos para a próxima pagina
    driver.switch_to.default_content()
    next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Próximo>')]")
    next_button.click()
