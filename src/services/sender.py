import os
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv()
headers = {
    "Content-Type": "application/json",
    "x-api-key": "290755df-40f9-4fbd-8bbe-dedfe0133564",
}

API_KEY = os.getenv("SCRAPER_API_KEY")
API_URL = os.getenv("API_URL", "http://localhost:3333/register-posts")


def send_data_to_api(data):
    try:
        if data is None or len(data) == 0:
            logging.warning("Nenhum dado para enviar.")
            return

        logging.info(f"Enviando {len(data)} registros para a API...")
        res = requests.post(API_URL, json={"posts": data}, headers=headers)
        res.raise_for_status()
        logging.info("Posts enviados com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao enviar dados para API: {e}")
        with open("backup.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info("Backup salvo localmente.")
