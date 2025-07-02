import keyboard
import time
from datetime import datetime
import threading
import queue
import logging
import os
from logging.handlers import RotatingFileHandler



class AppKrono:

    def __init__(self) -> None:
        self.identifiant_session = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.en_enregistrement = True
        self.appui_touche_queue = queue.Queue()

        # Configuration du répertoire des logs
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "logger.log")

        # Création du logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Évite les doublons si plusieurs loggers

        # Handler fichier avec rotation
        file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Handler console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # Ajout des handlers au logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        self.logger.info("Logger initialisé.")

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
            timestamp = datetime.now()
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
            print((identifiant_session, timestamp, touche_name, touche_code))

    def start(self) -> None:
        self.logger.info("Start de AppKrono.")
        ecoute_thread = threading.Thread(target=self.faire_commit_periodique)
        ecoute_thread.daemon = True
        ecoute_thread.start()

        self.logger.info("Debut enregistrement de touche.")
        keyboard.hook(self.ecoute)
        keyboard.wait('esc')
        self.logger.info("Fin enregistrement de touche.")

        self.logger.info("Fermeture.")
        self.en_enregistrement = False
        self.enregistre_dans_bd()
        self.logger.info("Fin.")


# if __name__ == "__main__":
#     logger = AppKrono()
#     logger.start()
