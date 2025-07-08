import logging
from datetime import datetime, timedelta
from scraper.browser import init_browser
from scraper.navigation import run_scraper
from services.sender import send_data_to_api

# Estabelendo um sistema de logging para identificar as etapas quando em headless mode
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def main():

    start = datetime.strptime("01/10/2024", "%d/%m/%Y")
    end = datetime.strptime("29/11/2024", "%d/%m/%Y")

    current = start
    while current <= end:
        date_str = current.strftime("%d/%m/%Y")
        logging.info(f"Executando scraping para a data: {date_str}")

        driver = init_browser()

        try:
            # Executa o scraper sempre de um dia apenas, para reduzir a carga da requisição
            # Isso também me permite burlar o sistema de sessão do DJE antes que ele expire
            # Futuramente pretendo liberar para que a data seja preenchida pela automação
            data = run_scraper(driver, date_str, date_str)
            send_data_to_api(data)

        finally:
            # Fecho o navegador pois assim ele é forçado a renovar a sessão no DJE e não
            # Corro o risco de não achar publicações porque expirou
            driver.quit()

        current += timedelta(days=1)


if __name__ == "__main__":
    main()
