import sqlite3
from typing import Optional
import yaml
import logging
import os


class GestionSqlite:

    def __init__(self, nom_db: str, logger: Optional[logging.Logger] = None) -> None:
        self.nom_db = nom_db
        self.connection = sqlite3.connect(nom_db)
        self.cursor = self.connection.cursor()

        # Logger
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "loggerdb.log")

        if logger:
            self.logger = logger
            self.logger.info("GestionSqlite initialisée avec logger partagé.")
        else:
            # Logger par défaut si aucun n'est fourni
            self.logger = logging.getLogger("GestionSqlite")
            self.logger.setLevel(logging.INFO)
            if not self.logger.handlers:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(file_handler)
            self.logger.info("GestionSqlite initialisée avec logger par défaut.")

        # Chargement des scriptes
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

        # Etablissement de la connection
        self.cursor.execute(self.setup["pragma_secure"])
        self.connection.commit()
        assert self.cursor.execute("PRAGMA secure_delete").fetchone()[0] == 1, "La suppression n'est pas sécurisé"
        self.ouvert = True
        self.logger.info("Connection faite et ouverte avec secure applique.")
        return

    def __str__(self) -> str:
        """
        Donne la liste des elements de la base de données : tables, index…
        Returns:
            str: La représentation en chaine de character de la liste des éléments de la bd
        """
        tables = self.cursor.execute(self.setup["gestionSQL_string"])
        tables = tables.fetchall()
        return str(tables)

    def __del__(self) -> None:
        """
        Met fin à la connection avec la bd à la suppression de le l'instance de la classe
        Returns:
            None
        """
        self.fin()
        return

    def est_ferme(self) -> bool:
        """
        Renvoie thrue si la connection est fermé, false sinon
        Returns:
            bool: La négation du champs self.ouvert
        """
        return not self.ouvert

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
        except Exception as e:
            self.logger.error("Erreur" + str(e) + "pour un nouveau jeu")
        return

    def select_all(self, nom: str) -> Optional[list]:
        """
        Selection de tous les éléments de la table donnée en paramètre et la renvoie.\n
        Notifications dans le logger.
        Args:
            nom (str) : Le nom de la table

        Returns:
            Optional[list] : Une liste si la table n’est pas vide
        """
        try:
            self.cursor.execute(
                self.commande_select[f"selection_{nom}"]
            )
            res = self.cursor.fetchall()
        except Exception as e:
            self.logger.error("Erreur" + str(e) + "pour la selection dans la table" + nom)
        return

    def delete_all(self, nom: str) -> None:
        """
        Vide la table donnée en paramètre.\n
        Notifications dans le logger.
        Args:
            nom (str): Le nom de la table

        Returns:
            None
        """
        try:
            self.cursor.execute(
                self.commande_delete[f"suppression_{nom}"]
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error("Erreur" + str(e) + "pour la suppression")
        return

    def nettoyage(self) -> None:
        """
        Fait le nettoyage de la base de donnée.
        À faire avant la fermeture.\n
        Notifications dans le logger.
        Returns:
            None
        """
        if self.est_ferme():
            return

        try:
            if self.cursor and not self.est_ferme():
                self.logger.info("Début du nettoyage de la base de données.")
                self.cursor.execute(
                    self.setup["nettoyage"]
                )
                self.connection.commit()
                self.logger.info("Nettoyage terminé avec succès.")
        except Exception as e:
            self.logger.warning(f"Erreur lors du nettoyage : {e}.")
        return

    def fin(self):
        """
        Applique le nettoyage de la bd et met fin a la connection.\n
        Notifications dans le logger.
        Returns:
            None
        """
        if self.est_ferme():
            self.logger.debug("Tentative de fermeture d'une connexion déjà fermée.")
            return
        try:
            self.logger.info("Début de la fermeture de la connexion BD.")
            self.nettoyage()

            if self.cursor and not self.est_ferme():
                self.cursor.close()
                self.logger.debug("Cursor fermée.")

            if self.connection and not self.est_ferme():
                self.connection.close()
                self.logger.debug("Connexion fermée.")

            self.logger.info("Fermeture BD terminée avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors du connexion : {e}")
        finally:
            self.ouvert = False
        return

    def insertion_touche(self, liste_touche: list[list]) -> None:
        """
        Prends une liste de touche dont les éléments sont [str, int, int, int] et insert les éléments dans la table
        touche, gère l’identifiant des touches.\n
        Notifications dans le logger.
        Args:
            liste_touche (list): Une liste de touche(`list`) que l’on insère dans la table touche

        Returns:
            None
        """
        id_t = 0
        try:
            self.logger.info("Insertion dans la table touche du dictionnaire des touches.")
            for info_touche in liste_touche:
                self.cursor.execute(
                    self.commande_insert["insertion_touche"],
                    (id_t, info_touche[0], info_touche[1], info_touche[2], info_touche[3])
                )
                id_t += 1
            self.connection.commit()
            self.logger.info("Insertion faite avec success.")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de touche : {e}")
        return

    def insertion_frappe(self, temps: int, session: int, touche: int) -> None:
        """
        Insert les paramètre comme un tuple dans la table frappe.
        Notifications dans le logger.\n
        Args:
            temps (int): l'horodatage de la frappe au format UNIX
            session (int): identifiant du session
            touche (int): identifiant de la touche

        Returns:
            None
        """
        try:
            self.cursor.execute(
                self.commande_insert["insertion_frappe"],
                (temps, session, touche)
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error(f"Erreur lors d'une enregistrement de frappe : {e}")


gestSQL = GestionSqlite("mesures.db")
print(gestSQL)
gestSQL.ajout_jeu("lol", "", True, "a", "z", "e", "r")
gestSQL.select_all("jeu")
gestSQL.delete_all("jeu")
gestSQL.select_all("jeu")
