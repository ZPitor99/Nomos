import sqlite3
import yaml


class GestionSqlite:

    def __init__(self) -> None:
        self.connection = sqlite3.connect("mesures.db")
        self.cursor = self.connection.cursor()

        with open("info_sql/insertion.yaml", "r") as file:
            self.commande_insert = yaml.safe_load(file)

        with open("info_sql/selection.yaml", "r") as file:
            self.commande_select = yaml.safe_load(file)

        with open("info_sql/modification.yaml", "r") as file:
            self.commande_update = yaml.safe_load(file)

        with open("info_sql/suppression.yaml", "r") as file:
            self.commande_delete = yaml.safe_load(file)

        tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = tables.fetchall()
        print(tables)

    def ajout_jeu(self, nom: str, description: str, favori: bool, touche1: str, touche2: str, touche3: str,
                  touche4: str) -> None:
        if description == "" or description is None:
            self.cursor.execute(
                self.commande_insert["insertions_jeu_sans_descr"],
                (nom, favori, touche1, touche2, touche3, touche4))
        else:
            self.cursor.execute(
                self.commande_insert["insertions_jeu_descr"],
                (nom, description, favori, touche1, touche2, touche3, touche4))
        return

    def select_all(self, nom: str) -> None:
        self.cursor.execute(
            self.commande_select[f"selection_{nom}"]
        )
        self.connection.commit()
        print(self.cursor.fetchall())

    def delete_all(self, nom: str) -> None:
        self.cursor.execute(
            self.commande_delete[f"suppression_{nom}"]
        )
        self.connection.commit()

gestSQL = GestionSqlite()
gestSQL.ajout_jeu("lol", "", True, "a", "z", "e", "r")
gestSQL.select_all("jeu")
gestSQL.delete_all("jeu")
gestSQL.select_all("jeu")