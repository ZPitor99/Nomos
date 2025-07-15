import sqlite3
import threading
from logging.handlers import RotatingFileHandler
from typing import Optional
import yaml
import logging
import os
from datetime import datetime

from AnalyseEnregistrement import Enregistrement
from Flushhandler import FlushableRotatingFileHandler


class GestionSqlite:
    """
    Class GestionSqlite permet de gérer les transactions avec la base de données en paramètre (path de la base) lors de sa création.
    Dois être de schéma spécifié dans `__init__'.\n
    Etablie une connection sécurisée, travail de logging et fermeture propre avec nettoyage.\n
    Utilise les instructions sql présent dans le répertoire `info_sql` qui sont en adéquation avec le schéma de la base.
    """

    def __init__(self, nom_db: str, logger: Optional[logging.Logger] = None) -> None:
        """
        Constructeur de la classe GestionSqlite. Utilise la base de donnée en paramètre, mais doit être de schéma
        tel que spécifier dans bd1.pdf de type sqlite3.db.\n
        Args:
            nom_db (str): Nom de la base de donnée à laquelle se connecter
            logger (logging.Logger): Non du logger si logger partagé est souhaité
        """
        self.nom_db = nom_db
        self.connection = None
        self.cursor = None
        self.lock = threading.Lock()
        self.ouvert = False

        # Initialiser la connexion
        try:
            self.connection = sqlite3.connect(nom_db, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise Exception(f"Erreur lors de la connexion à la base de données : {e}")

        # Logger
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "loggerdb.log")

        if logger:
            self.logger = logger
            self.logger.info("=== GestionSqlite initialisée avec logger partagé. ===")
        else:
            # Logger par défaut si aucun n'est fourni
            self.logger = logging.getLogger("GestionSqlite")
            self.logger.setLevel(logging.INFO)
            if not self.logger.handlers:
                file_handler = FlushableRotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
                file_handler.setFormatter(logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(file_handler)
            self.logger.info("=== === === GestionSqlite initialisée avec logger par défaut. === === ===")

        # Chargement des scriptes avec gestion d'erreurs
        try:
            with open("info_sql/insertion.yaml", "r") as file:
                self.commande_insert = yaml.safe_load(file)

            with open("info_sql/selection.yaml", "r") as file:
                self.commande_select = yaml.safe_load(file)

            with open("info_sql/modification.yaml", "r") as file:
                self.commande_update = yaml.safe_load(file)

            with open("info_sql/suppression.yaml", "r") as file:
                self.commande_delete = yaml.safe_load(file)

            with open("info_sql/setup.yaml", "r") as file:
                self.setup = yaml.safe_load(file)
            self.logger.info("Chargement des scriptes SQL fait.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des scripts SQL : {e}")
            self.fin()
            raise

        # Etablissement de la connection
        try:
            with self.lock:
                self.cursor.execute(self.setup["pragma_secure"])
                self.connection.commit()
                result = self.cursor.execute("PRAGMA secure_delete").fetchone()
                if not result or result[0] != 1:
                    self.logger.warning("La suppression sécurisée n'est pas activée")
                self.ouvert = True
                self.logger.info("Connection faite et ouverte avec secure applique.")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'établissement de la connexion : {e}")
            self.fin()
            raise

    def __str__(self) -> str:
        """
        Donne la liste des elements de la base de données : tables, index…
        Returns:
            str: La représentation en chaine de character de la liste des éléments de la bd
        """
        if not self.est_ouvert():
            return "Connexion fermée"

        try:
            with self.lock:
                tables = self.cursor.execute(self.setup["gestionSQL_string"])
                tables = tables.fetchall()
                return str(tables) + f"\n Base de données: {self.nom_db}"
        except Exception as e:
            self.logger.error(f"Erreur lors de l'affichage des tables : {e}")
            return f"Erreur : {e}"

    def __del__(self):
        self.fin()
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fin()
        return False

    def est_ouvert(self) -> bool:
        """
        Renvoie true si la connection est ouverte, false sinon
        Returns:
            bool: L'état du champ self.ouvert
        """
        return self.ouvert

    def ajout_jeu(self, nom: str, description: str, favori: bool, touche1: str, touche2: str, touche3: str,
                  touche4: str) -> None:
        """
        Ajoute le jeu dans la table jeu.\n
        Notifications dans le logger.
        Args:
            nom (str): Nom du jeu
            description (str): Description du jeu
            favori (bool): si le jeu est favori ou non favori
            touche1 (str): Nom du touche1
            touche2 (str): Nom du touche2
            touche3 (str): Nom du touche3
            touche4 (str): Nom du touche4

        Returns:
            None
        """
        if not self.est_ouvert():
            self.logger.error("Tentative d'ajout sur une connexion fermée")
            return

        with self.lock:
            try:
                if description == "" or description is None:
                    self.cursor.execute(
                        self.commande_insert["insertions_jeu_sans_descr"],
                        (nom, favori, touche1, touche2, touche3, touche4))
                else:
                    self.cursor.execute(
                        self.commande_insert["insertions_jeu_descr"],
                        (nom, description, favori, touche1, touche2, touche3, touche4))
                self.connection.commit()
                self.logger.info("Insertion d'un nouveau jeu faite.")
            except Exception as e:
                self.logger.error(f"Erreur {e} pour un nouveau jeu")
                self.connection.rollback()
        return

    def select_all(self, nom: str) -> Optional[list]:
        """
        Selection de tous les éléments de la table donnée en paramètre et la renvoie.\n
        Notifications dans le logger.
        Args:
            nom (str) : Le nom de la table

        Returns:
            Optional[list] : Une liste si la table n'est pas vide, None sinon
        """
        if not self.est_ouvert():
            self.logger.error("Tentative de sélection sur une connexion fermée")
            return None

        with self.lock:
            try:
                self.cursor.execute(
                    self.commande_select[f"selection_{nom}"]
                )
                res = self.cursor.fetchall()
                return res
            except Exception as e:
                self.logger.error(f"Erreur {e} pour la selection dans la table {nom}")
        return None

    def delete_all(self, nom: str) -> None:
        """
        Vide la table donnée en paramètre.\n
        Notifications dans le logger.
        Args:
            nom (str): Le nom de la table

        Returns:
            None
        """
        if not self.est_ouvert():
            self.logger.error("Tentative de suppression sur une connexion fermée")
            return

        with self.lock:
            try:
                self.cursor.execute(
                    self.commande_delete[f"suppression_{nom}"]
                )
                self.connection.commit()
                self.logger.info(f"Suppression de tout tuples de {nom}")
            except Exception as e:
                self.logger.error(f"Erreur {e} pour la suppression")
                self.connection.rollback()
        return

    def nettoyage(self) -> None:
        """
        Fait le nettoyage de la base de donnée.
        À faire avant la fermeture.\n
        Notifications dans le logger.
        Returns:
            None
        """
        if not self.est_ouvert():
            return

        try:
            if self.cursor and self.connection:
                self.logger.info("Début du nettoyage de la base de données.")
                #self.delete_all("frappe")
                self.cursor.execute(self.setup["nettoyage"])
                self.connection.commit()
                self.logger.info("Nettoyage terminé avec succès.")
        except Exception as e:
            self.logger.warning(f"Erreur lors du nettoyage : {e}")
            try:
                if self.connection:
                    self.connection.rollback()
            except Exception as rollback_error:
                self.logger.warning(f"Erreur lors du rollback : {rollback_error}")
        return

    def fin(self):
        """
        Applique le nettoyage de la bd et met fin a la connection.\n
        Notifications dans le logger.
        Returns:
            None
        """
        if not self.est_ouvert():
            return

        try:
            self.logger.info("Début de la fermeture de la connexion BD.")

            # Nettoyage seulement si la connexion est encore active
            if self.connection:
                try:
                    self.nettoyage()
                except Exception as e:
                    self.logger.warning(f"Erreur lors du nettoyage pendant la fermeture : {e}")

            # Fermeture du cursor
            if self.cursor:
                try:
                    self.cursor.close()
                    self.logger.info("Cursor fermé.")
                except Exception as e:
                    self.logger.warning(f"Erreur lors de la fermeture du cursor : {e}")
                finally:
                    self.cursor = None

            # Fermeture de la connexion
            if self.connection:
                try:
                    self.connection.close()
                    self.logger.info("Connexion fermée.")
                except Exception as e:
                    self.logger.warning(f"Erreur lors de la fermeture de la connexion : {e}")
                finally:
                    self.connection = None

            self.logger.info("Fermeture BD terminée avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de la connexion : {e}")
        finally:
            self.ouvert = False
            self.cursor = None
            self.connection = None

        # Fermeture propre des handlers de log
        try:
            for handler in self.logger.handlers[:]:
                if isinstance(handler, FlushableRotatingFileHandler) or isinstance(handler, RotatingFileHandler):
                    handler.close()
                    self.logger.removeHandler(handler)
        except Exception as e:
            pass
        return

    def insertion_touche(self, liste_touches: list[tuple[int, str, int, int]]) -> None:
        """
        Prends une liste de touche dont les éléments sont [int, str, int, int] et insert les éléments dans la table
        touche, gère l'identifiant des touches.\n
        Notifications dans le logger.
        Args:
            liste_touches (list): Une liste de touche(`tuple`) que l'on insère dans la table touche

        Returns:
            None
        """
        if not self.est_ouvert():
            self.logger.error("Tentative d'insertion sur une connexion fermée")
            return

        with self.lock:
            try:
                self.cursor.executemany(
                    self.commande_insert["insertion_touche"],
                    liste_touches,
                )
                self.connection.commit()
                self.logger.info("Insertion dans la table touche du liste des touches.")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'initialisation de touche : {e}")
                self.connection.rollback()
        return

    def insertion_frappe(self, frappes: list[tuple[int, int, int]]) -> None:
        """
        Insert les paramètre comme un tuple dans la table frappe.
        Notifications dans le logger.\n
        Args:
            frappes (list): List de tuple contenant les frappes à insérer

        Returns:
            None
        """
        if not self.est_ouvert():
            self.logger.error("Tentative d'insertion sur une connexion fermée")
            return

        if not frappes:
            return

        with self.lock:
            try:
                self.cursor.executemany(
                    self.commande_insert["insertion_frappe"],
                    frappes,
                )
                self.connection.commit()
                self.logger.info(f"Insertion de {len(frappes)} frappes réussie.")
                for handler in self.logger.handlers:
                    handler.flush()
            except Exception as e:
                self.logger.error(f"Erreur lors d'un enregistrement de frappe : {e}")
                self.connection.rollback()
        return

    def insertion_session(self, id_session: int, info_session:str, jeu:str ) -> None:
        if not self.est_ouvert():
            self.logger.error("Tentative d'insertion sur une connexion fermée")
            return

        with self.lock:
            try:
                self.cursor.execute(
                    self.commande_insert["insertion_sessions_vierge"],
                    (id_session, info_session, jeu),
                )
                self.connection.commit()
                self.logger.info(f"Insertion de la session")
            except Exception as e:
                self.logger.error(f"Erreur lors de l'insertion de la session: {e}")
                self.connection.rollback()
        return

    def enregistrement_mapping(self, mapping:dict[int:list]) -> None:
        if not self.est_ouvert():
            self.logger.error("Tentative d'insertion sur une connexion fermée")
            return

        data = [(k, *v) for k, v in mapping.items()]

        with self.lock:
            try:
                self.cursor.executemany(
                    self.commande_insert["insertion_touche"],
                    data,
                )
                self.connection.commit()
                self.logger.info(f"Insertion de {len(data)} touches.")
                for handler in self.logger.handlers[:]:
                    handler.flush()
            except Exception as e:
                self.logger.error(f"Erreur d'insertion de touche : {e}")
                self.connection.rollback()
        return

    def data_enregistrement(self, id_session:int) -> list[Enregistrement]:
        if not self.est_ouvert():
            self.logger.error("Tentative de selection sur une connexion fermée")
            return []

        with self.lock:
            try:
                self.cursor.execute(
                    self.commande_select["selection_data_enregistrement"],
                    (id_session,),
                )

                liste_enregistrement = [
                    Enregistrement(timestamp=row[0], key_code=row[1], key_repr=row[2])
                    for row in self.cursor.fetchall()
                ]

                self.logger.info(f"Chargé {len(liste_enregistrement)} frappes")
                return liste_enregistrement
            except Exception as e:
                self.logger.error(f"Erreur lors de la selection de data_enregistrement : {e}")
        return []

    def test(self):
        """
        Méthode de test pour vérifier la connexion
        """
        if not self.est_ouvert():
            self.logger.error("Tentative de test sur une connexion fermée")
            return None

        with self.lock:
            try:
                self.logger.info("Test de la connexion BD.")
                self.cursor.execute(
                    "SELECT * FROM frappe, touche WHERE frappe.code = touche.code ORDER BY id_frappe")
                res = self.cursor.fetchall()
                return res
            except Exception as e:
                self.logger.error(f"Erreur lors du test : {e}")
                return None


if __name__ == "__main__":
    gestSQL = None
    try:
        gestSQL = GestionSqlite("mesures.db")
        print(gestSQL)

        print("=== Test jeu")
        gestSQL.ajout_jeu("lol", "", True, "a", "z", "e", "r")
        print(gestSQL.select_all("jeu"))
        gestSQL.delete_all("jeu")
        print(gestSQL.select_all("jeu"))

        print("=== Test touche")
        gestSQL.insertion_touche([(10, "a", 1, 1), (20, "b", 2, 2), (30, "c", 3, 3)])
        print(gestSQL.select_all("touche"))

        print("=== Test frappe")
        gestSQL.insertion_frappe([(int(datetime.now().timestamp()), 25, 10), (int(datetime.now().timestamp()), 25, 10),
                                  (int(datetime.now().timestamp()), 25, 30)])
        gestSQL.insertion_frappe([(int(datetime.now().timestamp()), 26, 50), (int(datetime.now().timestamp()), 26, 10),
                                  (int(datetime.now().timestamp()), 26, 10)])

        print(gestSQL.test())

        print(gestSQL.select_all("frappe"))
        gestSQL.delete_all("frappe")
        print(gestSQL.select_all("frappe"))
        gestSQL.delete_all("touche")
        print(gestSQL.select_all("touche"))
        gestSQL.fin()

    except Exception as e:
        print(f"Erreur dans le programme principal : {e}")
    finally:
        if gestSQL:
            gestSQL.fin()