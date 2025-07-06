import keyboard
from collections import defaultdict
import pyodbc
import time
from datetime import datetime
import threading
import queue
import logging
import signal
import sys
import os
import glob
from logging.handlers import RotatingFileHandler


class AppKrono:

    def __init__(self) -> None:
        self.identifiant_session = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.en_enregistrement = True
        self.appui_touche_queue = queue.Queue()

        self.connection = pyodbc.connect("DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=database_touches.accdb")
        self.cursor = self.connection.cursor()

        # Configuration du logging
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "logger.log")
        logging.FileHandler(log_file)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logger.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Rotation des logs
        RotatingFileHandler('logger.log', maxBytes=1000000, backupCount=3)

    def ecoute(self, event) -> None:
        """
        Methode lancé à l'appui d'une touche. Ajoute les informations de la touche appuyée à appui_touche_queue.\n
        Enregistre :\n
        - id de session
        - l'horodatage de la touche -> nullification de second et microsecond
        - le nom de la touche
        - le code de la touche
        Args:
            event: Évènement de déclenchement de pressions sur touche

        Returns:
            None
        """
        if event.event_type == "down":
            timestamp = datetime.now().replace(second=0, microsecond=0)
            touche_name = event.name.lower()
            touche_code = event.scan_code

            self.appui_touche_queue.put((self.identifiant_session, timestamp, touche_name, touche_code))

        return

    def faire_commit_periodique(self) -> None:
        while self.en_enregistrement:
            time.sleep(2)
            self.enregistre_dans_bd()

    def enregistre_dans_bd(self) -> None:
        while not self.appui_touche_queue.empty():
            identifiant_session, timestamp, touche_name, touche_code = self.appui_touche_queue.get()
            self.cursor.execute("INSERT INTO pressions (identifiant, horodatage, touche, code_touche) VALUES (?,?,?,?)",
                                (identifiant_session, timestamp, touche_name, touche_code))
            self.connection.commit()

    def start(self) -> None:
        ecoute_thread = threading.Thread(target=self.faire_commit_periodique)
        ecoute_thread.daemon = True
        ecoute_thread.start()

        keyboard.hook(self.ecoute)
        keyboard.wait('esc')
        self.en_enregistrement = False
        self.enregistre_dans_bd()
        self.connection.close()


if __name__ == "__main__":
    logger = AppKrono()
    logger.start()
