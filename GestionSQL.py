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

        print(self.commande_insert)

        tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = tables.fetchall()
        print(tables)

    def ajout_jeu(self, nom: str, description: str, favori: bool, touche1: str, touche2: str, touche3: str,
                  touche4: str) -> None:
        if description:
            self.cursor.execute(
                self.commande_insert["insertions_jeu_descr"],
                (nom, description, favori, touche1, touche2, touche3, touche4))
        else:
            self.cursor.execute(
                self.commande_insert["insertions_jeu_sans_descr"],
                (nom, description, favori, touche1, touche2, touche3, touche4))
        return

    def select(self):
        self.cursor.execute(
            self.commande_select["selection_jeu"]
        )
        print(self.cursor.fetchall())

    def delete(self, nom: str) -> None:
        self.cursor.execute(
            self.commande_delete[f"suppression_{nom}"]
        )

gestSQL = GestionSqlite()
gestSQL.ajout_jeu("lol", "Jeu lol", True, "a", "z", "e", "r")
gestSQL.select()
gestSQL.delete("jeu")
gestSQL.select()