import keyboard
import time
from datetime import datetime
import threading
import queue
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from filelock import FileLock, Timeout

import GestionSQL as gsql


class AppKrono:

    def __init__(self) -> None:
        self.identifiant_session = int(datetime.now().timestamp())
        self.en_enregistrement = False
        self.appui_touche_queue = queue.Queue()
        self.bd = None

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
        file_handler.setFormatter(logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s'))

        # Handler console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s'))

        # Ajout des handlers au logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        self.logger.info("=== === === Logger initialisé. === === ===")

        try:
            self.bd = gsql.GestionSqlite("mesures.db", self.logger)
        except Exception as e:
            self.logger.error(f"Erreur lors de initialisation de la bd : {e}")
        return

    # def initialisation_touches(self) -> None:
    #     pass
    #     return

    def ecoute(self, event) -> None:
        """
        Methode lancé à l’appui d’une touche. Ajoute les informations de la touche appuyée à appui_touche_queue.\n
        Enregistre :\n
        - l’horodatage de la touche au format UNIX
        - id de session
        - le code de la touche
        Args:
            event: Évènement de déclenchement de pressions sur touche

        Returns:
            None
        """
        if event.event_type == "down":
            timestamp = datetime.now().timestamp()
            touche_code = event.scan_code #code
            self.appui_touche_queue.put((timestamp, self.identifiant_session, touche_code))
        return

    def faire_commit_periodique(self) -> None:
        """
        Fait l’enregistrement dans la base de données à chaque deux secondes
        Returns:
            None
        """
        while self.en_enregistrement:
            time.sleep(2)
            self.enregistre_dans_bd()

    def enregistre_dans_bd(self) -> None:
        """
        Vide les éléments de la queue dans une liste et insert les éléments de cette liste and la base de
        donnée via GestionSQL.\n
        Notifications dans le logger.
        Returns:
            None
        """
        if self.appui_touche_queue.empty():
            return
        batch_data = []
        while not self.appui_touche_queue.empty():
            try:
                data = self.appui_touche_queue.get_nowait()
                batch_data.append(data)
            except Exception as e:
                self.logger.error(f"Erreur dans l'enregistrement dans la bd : {e}")

        if batch_data:
            self.bd.insertion_frappe(batch_data)
        return

    def setup_touche(self) -> None:
        pass

    def start(self) -> None:
        """
        Lance un thread pour enregister toutes les deux secondes.
        Lance l’écoute des touches du clavier.\n
        Notifications dans le logger.
        Returns:
            None
        """
        self.logger.info("Start de AppKrono.")
        self.en_enregistrement = True
        ecoute_thread = threading.Thread(target=self.faire_commit_periodique)
        ecoute_thread.daemon = True
        ecoute_thread.start()

        self.logger.info("Debut enregistrement de touche.")
        keyboard.hook(self.ecoute)
        keyboard.wait('esc')
        self.logger.info("Fin enregistrement de touche.")

        self.logger.info("Fermeture.")
        self.enregistre_dans_bd()
        self.logger.info("Fin.")
        self.en_enregistrement = False
        return

# Empecher plusieurs lancements
lock_path = os.path.join(os.path.expanduser("~"), ".Nomos.lock")
lock = FileLock(lock_path)

try:
    with lock:
        if __name__ == "__main__":
            en_cour = AppKrono()
            en_cour.start()
except Timeout:
    print("L'application est déjà en cours d'exécution.")
    sys.exit(1)