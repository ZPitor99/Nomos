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

        # Etablissement de la connection
        self.cursor.execute(self.setup["pragma_secure"])
        self.connection.commit()
        assert self.cursor.execute("PRAGMA secure_delete").fetchone()[0] == 1, "La suppression n'est pas sécurisé"
        self.ouvert = True
        self.logger.info("Connection faite et ouverte avec secure applique.")

    def __str__(self) -> str:
        tables = self.cursor.execute(self.setup["gestionSQL_string"])
        tables = tables.fetchall()
        return str(tables)

    def __del__(self) -> None:
        self.fin()
        return

    def est_ferme(self) -> bool:
        return not self.ouvert

    def ajout_jeu(self, nom: str, description: str, favori: bool, touche1: str, touche2: str, touche3: str,
                  touche4: str) -> None:
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

    def select_all(self, nom: str) -> None:
        try:
            self.cursor.execute(
                self.commande_select[f"selection_{nom}"]
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error("Erreur" + str(e) + "pour la selection dans la table" + nom)
        return

    def delete_all(self, nom: str) -> None:
        try:
            self.cursor.execute(
                self.commande_delete[f"suppression_{nom}"]
            )
            self.connection.commit()
        except Exception as e:
            self.logger.error("Erreur" + str(e) + "pour la suppression")
        return

    def nettoyage(self):
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


gestSQL = GestionSqlite("mesures.db")
print(gestSQL)
gestSQL.ajout_jeu("lol", "", True, "a", "z", "e", "r")
gestSQL.select_all("jeu")
gestSQL.delete_all("jeu")
gestSQL.select_all("jeu")
