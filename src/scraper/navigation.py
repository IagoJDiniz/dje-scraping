import logging
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from scraper.extraction import (
    extract_paragraphs_from_page,
    extract_structured_data_from_paragraphs,
    fetch_previous_paragraph_if_incomplete,
    complete_last_paragraph_if_needed,
)
from scraper.utils import go_to_next_page, has_next_page


def run_scraper(driver, data_inicio, data_fim):
    logging.info("Acessando página inicial...")
    driver.get("https://dje.tjsp.jus.br/cdje/index.do")
    time.sleep(2)

    campo_data_inicio = driver.find_element(By.NAME, "dadosConsulta.dtInicio")
    campo_data_fim = driver.find_element(By.NAME, "dadosConsulta.dtFim")
    campo_palavras_chave = driver.find_element(By.NAME, "dadosConsulta.pesquisaLivre")

    campo_caderno = Select(driver.find_element(By.NAME, "dadosConsulta.cdCaderno"))
    campo_caderno.select_by_value("12")

    driver.execute_script(
        "arguments[0].setAttribute('value', arguments[1])",
        campo_data_inicio,
        data_inicio,
    )
    driver.execute_script(
        "arguments[0].setAttribute('value', arguments[1])", campo_data_fim, data_fim
    )
    campo_palavras_chave.send_keys('"RPV" E "pagamento pelo INSS"')

    driver.find_element(
        By.XPATH, '//input[@type="submit" and @value="Pesquisar"]'
    ).click()
    time.sleep(3)
    logging.info("Busca realizada com sucesso.")

    aba_original = driver.current_window_handle
    all_structured_data = []

    def process_current_page():
        links = driver.find_elements(
            By.XPATH, "//a[span[contains(text(), 'ocorrência')]]"
        )

        for index, a in enumerate(links):
            try:
                a.click()
                time.sleep(2)
                abas = driver.window_handles
                nova_aba = [aba for aba in abas if aba != aba_original][0]
                driver.switch_to.window(nova_aba)

                time.sleep(3)
                logging.info("Extraindo parágrafos do PDF aberto...")
                paragraphs = extract_paragraphs_from_page(driver)

                fetch_previous_paragraph_if_incomplete(
                    driver, paragraphs, all_structured_data
                )
                complete_last_paragraph_if_needed(driver, paragraphs)

                structured = extract_structured_data_from_paragraphs(
                    paragraphs, data_inicio
                )
                all_structured_data.extend(structured)

                driver.close()
                driver.switch_to.window(aba_original)
                time.sleep(1)

            except Exception as e:
                logging.error(f"Erro ao processar PDF: {e}")
                driver.switch_to.window(aba_original)

    process_current_page()

    while has_next_page(driver):
        go_to_next_page(driver)
        time.sleep(3)
        process_current_page()

    return all_structured_data
