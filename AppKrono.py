import keyboard
import time
from datetime import datetime
import threading
import queue
import logging
import os
import sys
from Flushhandler import FlushableRotatingFileHandler
from filelock import FileLock, Timeout

import GestionSQL as gsql


class AppKrono:
    """
    Class AppKrono s’occupe de mettre en place les éléments essentiels de l’application:
        - Initialisation des éléments de base de l’application
        - Ecoute et enregistrement périodique des appuis claviers
    """

    def __init__(self) -> None:
        """
        Constructeur de la classe AppKrono. Initialise les éléments de base de l’application:
            - Session
            - Mapping
            - Base de données (Instance de `GestionSQL`)
            - Logger
        """
        self.identifiant_session = int(datetime.now().timestamp())
        self.en_enregistrement = False
        self.touches_enfoncees = set()
        self.appui_touche_queue = queue.Queue()
        self.mapping = None
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
        file_handler = FlushableRotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s'))
        file_handler.flush = lambda: file_handler.stream.flush() if file_handler.stream else None

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

        self.setup_session("Session test3 game", "")
        self.faire_mapping()
        return

    def __str__(self) -> str:
        return f"AppKrono de session {self.identifiant_session} avec le status d'enregistrement {self.en_enregistrement}"


    def __del__(self):
        self.fin()
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fin()
        return

    def fin(self):
        """
        Gère la fin des différents champs qui ont besoin de traitement de fin:
            - self.logger
            - self.bd
        Returns:
            None
        """
        try:
            self.logger.info("Fermeture de la bd.")
            self.bd = None
            self.logger.info("fermeture du logger.")
            for handler in self.logger.handlers[:]:
                if isinstance(handler, FlushableRotatingFileHandler):
                    handler.close()
                    self.logger.removeHandler(handler)
        except Exception as e:
            pass
        return

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
        try:
            if event.event_type == "down":
                if event.name not in self.touches_enfoncees:
                    self.touches_enfoncees.add(event.name)
                    self.appui_touche_queue.put((float(datetime.now().timestamp()), self.identifiant_session, event.scan_code))
            elif event.event_type == "up":
                self.touches_enfoncees.discard(event.name)
        except Exception as e:
            self.logger.error(f"Erreur dans l'écoute de touche: {e}")
            return

    def faire_commit_periodique(self) -> None:
        """
        Fait l’enregistrement dans la base de données à chaque quatre secondes
        Returns:
            None
        """
        while self.en_enregistrement:
            time.sleep(4)
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

    def setup_mapping(self) -> None:
        """
        Procède au mapping des touches.\n
        Notifications dans le logger.
        Returns:
            None
        """
        azerty_layout = [
            ['Echap', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'],
            ['²', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ')', '=', 'Retour'],
            ['Tab', 'a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '^', '$', 'Entrer'],
            ['Verr.maj', 'q', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'ù', '*'],
            ['Shift', '<', 'w', 'x', 'c', 'v', 'b', 'n', ',', ';', ':', '!', 'Shift'],
            ['Ctrl', 'Win', 'Alt', 'Space', 'AltGr', 'Menu', 'Ctrl'],
            ['Haut', 'Bas', 'Gauche', 'Droite']
        ]

        self.mapping = {}

        print("Touche par touche, appuie sur les touches suivantes dans l'ordre affiché.")
        time.sleep(3)

        for row_idx, row in enumerate(azerty_layout):
            for col_idx, label in enumerate(row):
                while True:
                    print(f"Appuie sur : {label} (ligne {row_idx}, col {col_idx})")
                    event = keyboard.read_event()
                    if event.event_type == 'down':
                        self.mapping[event.scan_code] = [label, row_idx, col_idx]
                        print(
                            f"Capturé : scan_code={event.scan_code}, symbole={label}, position=({row_idx}, {col_idx})\n")
                        break

        print("\nMapping terminé ! \n")
        print(self.mapping)
        self.logger.info("Mapping fait, envoie des données dans la bd.")
        self.bd.enregistrement_mapping(self.mapping)
        time.sleep(3)
        return

    def doit_etre_mapper(self) -> bool:
        """
        Renvoie True si les touches ont besoin d’être mappé, False sinon.\n
        Notifications dans le logger.
        Returns:
            (bool): True ou false en fonction du besoin de mapping
        """
        self.logger.info("Verification si besoin de mapping.")
        result = self.bd.select_all("touche")
        if not result:
            return True
        else:
            return False

    def faire_mapping(self) -> None:
        """
        Gestion du mapping : vérification du besoin de mapping et le fait si besoin.\n
        Notifications dans le logger.
        Returns:
            None
        """
        if self.doit_etre_mapper():
            self.setup_mapping()
            self.logger.info("Mapping terminé.")
            return
        else:
            self.logger.info("Mapping déjà fait.")
            return

    def setup_session(self, info:str, jeu:str) -> None:
        """
        Applique les informations de base de la session dans la bd.\n
        Notifications dans le logger.
        Args:
            info (str): Information sur la session.
            jeu (str): Jeu de la session.

        Returns:
            None
        """
        self.logger.info("Setting up session basique")
        self.bd.insertion_session(self.identifiant_session, info, jeu)
        return

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
        keyboard.wait('+')
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
            en_cour.fin()
except Timeout:
    print("L'application est déjà en cours d'exécution.")
    sys.exit(1)