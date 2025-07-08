from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def init_browser():

    # Iniciando o navegador, caso queira ver a "mágica" acontecendo basta remover o argumento --headless

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--width=1280")
    options.add_argument("--height=800")
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)
    return driver
