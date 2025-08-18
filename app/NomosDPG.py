import ctypes
import time
import threading
import dearpygui.dearpygui as dpg
import os
import datetime
from typing import Union

import keyboard


class NomosDPG:
    """
    Classe principale de l'interface graphique Nomos utilisant DearPyGUI.
    """

    def __init__(self, krono_instance, project_root=None):
        """
        Initialise l'application avec une instance de AppKrono.

        Args:
            krono_instance: Instance de la classe AppKrono
            project_root: Chemin vers la racine du projet (optionnel)
        """
        self.krono = krono_instance
        self.main_win = None
        self.project_root = project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def run(self):
        """
        Lance l'application graphique.
        """
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass
        dpg.create_context()

        try:
            from Theme_NeoDark import theme
            dpg.bind_theme(theme)
        except Exception as e:
            print(f"Theme_NeoDark non trouvé, utilisation du thème par défaut {e}")

        self.main_win = MainWin(self.krono)

        dpg.create_viewport(title='Nomos', width=1280, height=720)

        # Chemin vers l'icône (relatif à la racine du projet)
        icon_path = os.path.join(self.project_root, "ressources", "Nomos.ico")
        if os.path.exists(icon_path):
            dpg.set_viewport_small_icon(icon_path)
            dpg.set_viewport_large_icon(icon_path)

        dpg.setup_dearpygui()
        dpg.set_primary_window(self.main_win.winID, True)

        self.main_win.gestionnaire_windows.afficher_window("Accueil")

        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


class MainWin:
    def __init__(self, krono_instance):
        self.krono = krono_instance
        self.winID = "main_win"
        self.zone_contenu = "Contenue_main_win"

        self.gestionnaire_windows = GestionWindow(self.zone_contenu)
        self.gestionnaire_windows.nouvelle_window("Accueil", AccueilWindow(self.krono))
        self.gestionnaire_windows.nouvelle_window("Ecoute", EcouteWindow(self.krono))
        self.gestionnaire_windows.nouvelle_window("Conf", Configuration(self.krono))
        self.gestionnaire_windows.nouvelle_window("Clavier2D", Clavier2DWindow(self.krono))
        self.gestionnaire_windows.nouvelle_window("Statistique", Statistiques(self.krono))

        self.fait_naitre_main_window()
        return

    def fait_naitre_main_window(self):
        with dpg.window(tag=self.winID) as win_main:
            with dpg.menu_bar():
                with dpg.menu(label="Fichier"):
                    dpg.add_menu_item(label="Accueil",
                                      callback=lambda: self.gestionnaire_windows.afficher_window("Accueil"))
                    dpg.add_menu_item(label="Exporter données")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Plein écran", callback=lambda: dpg.toggle_viewport_fullscreen())
                    dpg.add_menu_item(label="Paramètres")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Quitter", callback=lambda: dpg.stop_dearpygui())

                with dpg.menu(label="Ecoute"):
                    dpg.add_menu_item(label="Enregistrer",
                                      callback=lambda: self.gestionnaire_windows.afficher_window("Ecoute"))
                    dpg.add_menu_item(label="Configurer",
                                      callback=lambda: self.gestionnaire_windows.afficher_window("Conf"))

                with dpg.menu(label="Stats"):
                    dpg.add_menu_item(label="Statistique",
                                      callback=lambda: self.gestionnaire_windows.afficher_window("Statistique"))
                    dpg.add_menu_item(label="Clavier 2D",
                                      callback=lambda: self.gestionnaire_windows.afficher_window("Clavier2D"))

                with dpg.menu(label="Aide"):
                    dpg.add_menu_item(label="Mode d'emploi")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Github")
                    dpg.add_menu_item(label="Contact")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Dear PyGUI", callback=lambda: dpg.show_tool(dpg.mvTool_About))
                    dpg.add_menu_item(label="A propos")
                # DEV
                with dpg.menu(label="Tools"):
                    dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
                    dpg.add_menu_item(label="Show Font Manager", callback=lambda: dpg.show_tool(dpg.mvTool_Font))
                    dpg.add_menu_item(label="Show Item Registry",
                                      callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))
                    dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
                    dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())

            with dpg.child_window(tag=self.zone_contenu, border=False):
                pass

            # Ajustement theme
            with dpg.theme() as mainwin_theme:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 25, 255))
            dpg.bind_item_theme(win_main, mainwin_theme)
        return


class GestionWindow:
    def __init__(self, parent_id):
        self.parent = parent_id
        self.window_courante = None
        self.windows = {}
        return

    def nouvelle_window(self, nom: str, window):
        window.parent_id = self.parent
        self.windows[nom] = window

    def afficher_window(self, nom: str):
        if self.window_courante:
            dpg.hide_item(self.window_courante)

        if nom not in self.windows:
            return

        actuel = self.windows[nom]

        if not dpg.does_item_exist(actuel.winID):
            actuel.cree()
        else:
            actuel.actualiser_donnees()

        dpg.show_item(actuel.winID)
        self.window_courante = actuel.winID
        return


class BebeWindow:
    def __init__(self, window_id, krono_instance):
        self.winID = window_id
        self.vivante = False
        self.parent_id = None
        self.data = {}
        self.krono = krono_instance
        return

    def cree(self):
        if not self.vivante:
            self._naissance()
            self.vivante = True
        return

    def _naissance(self):
        pass

    def actualiser_donnees(self):
        pass


def get_main_window():
    """Méthode helper pour accéder à la fenêtre principale"""
    return dpg.get_item_user_data("main_win") if dpg.does_item_exist("main_win") else None


class AccueilWindow(BebeWindow):
    """
    Class de la fenêtre d'accueil de l'interface.
    """

    def __init__(self, krono_instance) -> None:
        """
        Création de l'instance
        """
        super().__init__("Accueil", krono_instance)
        self.info_acc = {
            "nombre_session" : 0,
            "temps_total" : 0,
            "session_recente" : ""
        }
        return

    def _naissance(self) -> None:
        """
        Définit les éléments de la fenêtre AccueilWindow.
            - Actions rapides
            - Résumer des sessions déjà présentes
        Returns:
            None
        """
        self.set_donnees()
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Bienvenue dans Nomos !")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=200):
                    dpg.add_text("Actions rapides")
                    dpg.add_separator()
                    dpg.add_button(label="Faire une écoute", width=-1,
                                   callback=lambda: get_main_window().gestionnaire_windows.afficher_window(
                                       "Ecoute"))
                    dpg.add_button(label="Voir statistiques", width=-1)
                    dpg.add_button(label="Configuration", width=-1)

                dpg.add_spacer(width=20)

                with dpg.child_window(width=-1, height=200):
                    dpg.add_text("Informations")
                    dpg.add_separator()
                    dpg.add_text(f"Nom de la dernière écoute : {self.info_acc['session_recente']}")
                    dpg.add_text(f"Nombre de sessions totales : {self.info_acc['nombre_session']}")
                    dpg.add_text(f"Temps total en enregistrement: {unix_to_time(self.info_acc['temps_total'], True)}")
        return

    def actualiser_donnees(self):
        self.set_donnees()
        if dpg.does_item_exist(self.winID):
            dpg.delete_item(self.winID)

        self.vivante = False
        self.cree()
        return

    def set_donnees(self):
        self.info_acc = self.krono.info_accueil()
        self.info_acc['session_recente'] = self.tuple_net(self.info_acc['session_recente'])
        self.info_acc['temps_total'] = self.info_acc['temps_total'] if self.info_acc['temps_total'] else 0
        return

    @staticmethod
    def tuple_net(t: tuple):
        while (isinstance(t, tuple) or isinstance(t, list)) and len(t) == 1:
            t = t[0]
        return t

class EcouteWindow(BebeWindow):
    """
    Class de la fenêtre dearpygui pour gérer les écoutes.
    """

    def __init__(self, krono_instance):
        """
        Création de l'instance.
        """
        super().__init__("Ecoute", krono_instance)
        self.item_activation = [f"{self.winID}_bnt_ecoute", f"{self.winID}_btn_creer"]
        return

    def _naissance(self) -> None:
        """
        Définit les élements de la fenêtre EcouteWindow.\n
            - Lancer une écoute avec paramétrage.
            - Ajouter un nouveau jeu
            - Visualizer les sessions faites.

        Returns:
            None
        """
        self.set_donnees()
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Enregistrement des touches")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=300):
                    dpg.add_text("Lancer une écoute")
                    dpg.add_separator()
                    dpg.add_button(label="Nouvelle écoute", width=-1, callback=lambda: self.start_ecoute(),
                                   tag=f"{self.winID}_bnt_ecoute")
                    dpg.add_text("Nom session")
                    dpg.add_input_text(width=-1, tag="champ_nom")
                    dpg.add_text("Jeu")
                    dpg.add_combo(width=-1, items=self.data["liste_jeu"], tag="champ_jeu")

                dpg.add_spacer(width=20)
                with dpg.group():
                    with dpg.child_window(width=-1, height=250):
                        dpg.add_text("Créer un nouveau jeu")
                        dpg.add_separator()
                        with dpg.group(horizontal=True):
                            for elem in [("Nom", False, "champ_jeu1"), ("Description", False, "champ_jeu2"),
                                         ("T1", True, "champ_jeu3"), ("T2", True, "champ_jeu4"),
                                         ("T3", True, "champ_jeu5"), ("T4", True, "champ_jeu6")]:
                                with dpg.group():
                                    dpg.add_text(elem[0])
                                    if elem[1]:
                                        dpg.add_combo(fit_width=True, tag=elem[2],
                                                      items=self.data["list_nom_touches"])
                                    else:
                                        dpg.add_input_text(width=200, tag=elem[2])
                        dpg.add_spacer(height=15)
                        dpg.add_button(label="Créer", callback=lambda: self.valider_nouveau_jeu(),
                                       tag=f"{self.winID}_btn_creer")

                    dpg.add_text("Enregistrement en cour", tag=f"{self.winID}_enregistrement", color=(21, 20, 25))

            dpg.add_spacer(height=10)
            dpg.add_text(f"Nombre total d'écoute faite:  {len(self.data["ecoute_session_table"])}")
            dpg.add_separator()
            with dpg.table(header_row=True, no_host_extendX=True, context_menu_in_body=True,
                           row_background=True, policy=dpg.mvTable_SizingStretchSame, scrollY=True,
                           clipper=True, height=-1, resizable=True, delay_search=True, borders_outerH=True,
                           borders_innerV=True, borders_outerV=True):

                dpg.add_table_column(label="Nom")
                dpg.add_table_column(label="Date")
                dpg.add_table_column(label="Durée")
                dpg.add_table_column(label="Jeu")

                for i in self.data["ecoute_session_table"]:
                    with dpg.table_row():
                        dpg.add_text(f"{i[0]}")
                        dpg.add_text(f"{unix_to_date(i[1])}")
                        dpg.add_text(unix_to_time(i[2] - i[1]))
                        dpg.add_text(f"{i[3]}")

    def set_donnees(self) -> None:
        """
        Applique au champ `self.data` les données que la fenêtre doit afficher.
        Appeler la méthode quand un changement de données est fait pour mettre à jour les données en mémoire.
        Returns:
            None
        """
        self.data["ecoute_session_table"] = self.krono.bd.select_ecoute_session()
        self.data["list_nom_touches"] = self.krono.bd.select_touche_mappe()
        self.data["liste_jeu"] = [s[0] for s in self.krono.bd.select_list_jeu()]
        return

    def actualiser_donnees(self) -> None:
        """
        Fait l'actualisation des données visuellement, c'est-à-dire détruit la fenêtre et l'affiche de nouveau avec
        les données en mémoire.
        Returns:
            None
        """
        self.set_donnees()
        if dpg.does_item_exist(self.winID):
            dpg.delete_item(self.winID)

        self.vivante = False
        self.cree()

        return

    def valider_nouveau_jeu(self) -> None:
        """
        Méthode pour valider la création d’un nouveau jeu. Récupère les données des champs dpg necessaire pour la création
        et envoie les données pour faire l'ajout. Puis actualise la fenêtre.
        Returns:
            None
        """
        try:
            val1 = dpg.get_value("champ_jeu1")
            val2 = dpg.get_value("champ_jeu2")
            val3 = dpg.get_value("champ_jeu3")
            val4 = dpg.get_value("champ_jeu4")
            val5 = dpg.get_value("champ_jeu5")
            val6 = dpg.get_value("champ_jeu6")
            if any([v is None or v == "" for v in [val1, val2, val3, val4, val5, val6]]):
                self.popup_creer(3)
            else:
                ajout = self.krono.bd.ajout_jeu(val1, val2, val3, val4, val5, val6)
                if ajout:
                    self.popup_creer(2)
        except Exception as e:
            print(e)
        self.actualiser_donnees()
        return

    def start_ecoute(self) -> None:
        """
        Lance l'écoute des frappes pour l'enregistrement. Affiche un message de fin pour informer de la fin de l'enregistrement.
        Returns:
            None
        """
        try:
            valjeu = dpg.get_value("champ_jeu")
            valnom = dpg.get_value("champ_nom")

            if not valjeu or not valnom or valnom == "" or valjeu == "":
                self.popup_creer(3)
            else:
                for elem in self.item_activation:
                    dpg.configure_item(elem, enabled=False)
                dpg.configure_item(f"{self.winID}_enregistrement", color=(63, 234, 21))

                self.krono.start(valnom, valjeu)
                self.popup_creer(1)
        except Exception as e:
            print(e)

        for elem in self.item_activation:
            dpg.configure_item(elem, enabled=True)
        dpg.configure_item(f"{self.winID}_enregistrement", color=(21, 20, 25))

        self.actualiser_donnees()
        return

    def popup_creer(self, type_err: int = 0) -> None:

        if type_err == 1:
            information = "Fin de la session"
            x = 280
        elif type_err == 2:
            information = "Jeu ajouté avec succès"
            x = 350
        elif type_err == 3:
            information = "Champ incorrect"
            x = 300
        else:
            information = "Une erreur est survenue"
            x = 400

        with dpg.window(label="Information", modal=True, no_close=True, width=x, height=150,
                        tag=f"{self.winID}_popup",
                        pos=(dpg.get_viewport_client_width() // 2 - (x//2), dpg.get_viewport_client_height() // 2 - 75),
                        no_title_bar=True):
            from Theme_NeoDark import theme
            dpg.bind_item_theme(f"{self.winID}_popup", theme)
            dpg.add_text(f"{information}", indent=(x//5))
            dpg.add_spacer(height=10)
            dpg.add_button(label="OK", width=-1, callback=lambda: dpg.delete_item(f"{self.winID}_popup"))
        return


class Configuration(BebeWindow):

    def __init__(self, krono_instance) -> None:
        super().__init__("Conf", krono_instance)
        self.azerty_layout_legacy = [
            ["Echap", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
            ["²", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ")", "=", "Retour"],
            ["Tab", "A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P", "^", "$", "Entrée"],
            ["Verr.Maj", "Q", "S", "D", "F", "G", "H", "J", "K", "L", "M", "%", "*"],
            ["Shift", "<", "W", "X", "C", "V", "B", "N", ",", ";", ":", "!", "ShiftG"],
            ["Ctrl", "Win", "Alt", "Espace", "AltGr", "Menu"],
            ["Haut", "Bas", "Gauche", "Droite"]
        ]
        self.azerty_layout_standard = [
            ["Echap", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
            ["@", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "'", "^", "Retour"],
            ["Tab", "A", "Z", "E", "R", "T", "Y", "U", "I", "O", "P", "-", "+", "Enter"],
            ["Verr.Maj", "Q", "S", "D", "F", "G", "H", "J", "K", "L", "M", "/", "*"],
            ["Shift", "<", "W", "X", "C", "V", "B", "N", ",", ":", ";", "ShiftG"],
            ["Ctrl", "Win", "Alt", "Espace", "AltGr", "Menu"],
            ["Haut", "Bas", "Gauche", "Droite"]
        ]
        self.qwerty_layout_standard = [
            ["Echap", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
            ["²", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
            ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]"],
            ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"],
            ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "ShiftG"],
            ["Ctrl", "Win", "Alt", "Espace", "AltGr", "Menu"],
            ["Top", "Bot", "Left", "Right"]
        ]
        self.krono = krono_instance
        self.mapping_data = {}  # {scan_code: [représentation, x, y]}
        self.ligne_courante = 0
        self.colonne_courante = 0
        self.is_mapping = False
        self.mapping_thread = None
        self.demande_skip = False  # Flag pour gérer le skip
        self.touche_appuye = None  # Stocke la dernière touche pressée
        self.keyboard_hook = None  # Hook clavier
        return

    def _naissance(self) -> None:
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Configuration des touches")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                # Panel d'instructions (gauche)
                with dpg.child_window(width=500, height=-1, tag=f"{self.winID}_instructions", no_scrollbar=True):
                    dpg.add_text("Instructions")
                    dpg.add_separator()
                    dpg.add_spacer(height=5)
                    dpg.add_text("La configuration des touches est nécessaire pour que l'application associe"
                                 " correctement la touche pressée et le caractère de la touche.",
                                 bullet=True, wrap=475)
                    dpg.add_text("Appuyer sur la touche correspondante au caractère affiché.",
                                 bullet=True, wrap=475)
                    dpg.add_text("Appuyer sur Passer si la touche n'est pas présente sur votre clavier.",
                                 bullet=True, wrap=475)
                    dpg.add_text("La configuration est faite sur la base d'un clavier azerty standardisé. "
                                 "La configuration se fera de gauche à droite, de haut en bas.",
                                 bullet=True, wrap=475)

                    dpg.add_spacer(height=20)
                    dpg.add_separator()

                    dpg.add_text("Statut:", tag=f"{self.winID}_status_label")
                    dpg.add_text("Prêt à commencer", tag=f"{self.winID}_status", color=(100, 200, 100))

                    dpg.add_spacer(height=10)
                    dpg.add_text("Progression:", tag=f"{self.winID}_progression_label")
                    dpg.add_progress_bar(default_value=0.0, tag=f"{self.winID}_progression", width=-1)
                    dpg.add_text("0/0", tag=f"{self.winID}_progression_text")

                # Panel de configuration
                with dpg.child_window(width=-1, height=-1, tag=f"{self.winID}_config"):
                    dpg.add_text("Configuration", tag=f"{self.winID}_config_title")
                    dpg.add_separator()

                    with dpg.group(horizontal=False, tag=f"{self.winID}_touche_courante_group"):
                        dpg.add_spacer(height=20)
                        dpg.add_text("Touche à configurer:", tag=f"{self.winID}_current_label")
                        dpg.add_text("", tag=f"{self.winID}_touche_courante",
                                     color=(255, 255, 0),
                                     wrap=400)
                        dpg.add_spacer(height=10)
                        dpg.add_text("Position: ", tag=f"{self.winID}_position")

                    dpg.add_spacer(height=30)

                    # Boutons de contrôle
                    with dpg.group(horizontal=True, tag=f"{self.winID}_controls"):
                        dpg.add_button(label="Commencer",
                                       callback=self._debut_mapping,
                                       tag=f"{self.winID}_start_btn",
                                       width=130, height=40)
                        dpg.add_button(label="Passer",
                                       callback=self._skip_key,
                                       tag=f"{self.winID}_skip_btn",
                                       width=100, height=40,
                                       enabled=False)
                        dpg.add_button(label="Arrêter",
                                       callback=self._stop_mapping,
                                       tag=f"{self.winID}_stop_btn",
                                       width=100, height=40,
                                       enabled=False)

                    dpg.add_spacer(height=20)

                    # Zone de logs
                    dpg.add_text("Journal:")
                    with dpg.child_window(height=-1, tag=f"{self.winID}_logs"):
                        dpg.add_text("En attente de configuration...\n", tag=f"{self.winID}_log_contenu")
        return

    def _keyboard_callback(self, event):
        """Callback appelé à chaque appui de touche"""
        if self.is_mapping and event.event_type == keyboard.KEY_DOWN:
            self.touche_appuye = event.scan_code

    def _debut_mapping(self) -> None:
        """Lance le processus de mapping"""
        if not self.is_mapping:
            self.is_mapping = True
            self.ligne_courante = 0
            self.colonne_courante = 0
            self.mapping_data.clear()
            self.touche_appuye = None

            # Installer le hook clavier
            self.keyboard_hook = keyboard.hook(self._keyboard_callback)

            # Mise à jour de l'interface
            dpg.set_value(f"{self.winID}_start_btn", "En cours...")
            dpg.configure_item(f"{self.winID}_start_btn", enabled=False)
            dpg.configure_item(f"{self.winID}_skip_btn", enabled=True)
            dpg.configure_item(f"{self.winID}_stop_btn", enabled=True)
            dpg.set_value(f"{self.winID}_status", "Mapping en cours")
            dpg.configure_item(f"{self.winID}_status", color=(255, 165, 0))

            # Démarrer le thread de mapping
            self.mapping_thread = threading.Thread(target=self._boucle_capture, daemon=True)
            self.mapping_thread.start()

    def _boucle_capture(self) -> None:
        """Boucle principale du mapping dans un thread séparé"""
        total_keys = sum(len(row) for row in self.azerty_layout_legacy)
        touche_mapper = 0

        self._log_message("Début du mapping des touches...")

        for row_idx, row in enumerate(self.azerty_layout_legacy):
            if not self.is_mapping:
                break

            for col_idx, key_label in enumerate(row):
                if not self.is_mapping:
                    break

                self.ligne_courante = row_idx
                self.colonne_courante = col_idx
                self.demande_skip = False

                # Mise à jour de l'interface depuis le thread principal
                dpg.set_value(f"{self.winID}_touche_courante", f"{key_label}")
                dpg.set_value(f"{self.winID}_position", f"Position: Ligne {row_idx + 1}, Colonne {col_idx + 1}")

                progression = touche_mapper / total_keys
                dpg.set_value(f"{self.winID}_progression", progression)
                dpg.set_value(f"{self.winID}_progression_text", f"{touche_mapper}/{total_keys}")

                self._log_message(f"En attente de la touche: {key_label}")

                # Attendre l'appui de touche ou le skip
                key_captured = False
                while not key_captured and self.is_mapping:
                    if self.demande_skip:
                        self._log_message(f"Touche '{key_label}' passée")
                        touche_mapper += 1
                        self.demande_skip = False
                        break

                    if self.touche_appuye is not None:
                        scan_code = self.touche_appuye
                        self.touche_appuye = None

                        if scan_code in self.mapping_data:
                            self._log_message(f"Scan code {scan_code} déjà utilisé, passer automatiquement")
                            touche_mapper += 1
                            break

                        self.mapping_data[scan_code] = [key_label, col_idx, row_idx]
                        self._log_message(f"{key_label}: scan_code: {scan_code}, position: ({col_idx}, {row_idx})")

                        touche_mapper += 1
                        key_captured = True

                    time.sleep(0.05)

                time.sleep(0.2)

        if self.is_mapping:
            self._fin_mapping(touche_mapper, total_keys)
        return

    def _skip_key(self) -> None:
        """Passe la touche courante"""
        if self.is_mapping:
            self.demande_skip = True
        return

    def _stop_mapping(self) -> None:
        """Arrête le processus de mapping"""
        self.is_mapping = False

        if self.keyboard_hook:
            keyboard.unhook(self.keyboard_hook)
            self.keyboard_hook = None

        if self.mapping_thread and self.mapping_thread.is_alive():
            self.mapping_thread.join(timeout=1.0)

        dpg.set_value(f"{self.winID}_start_btn", "Commencer")
        dpg.configure_item(f"{self.winID}_start_btn", enabled=True)
        dpg.configure_item(f"{self.winID}_skip_btn", enabled=False)
        dpg.configure_item(f"{self.winID}_stop_btn", enabled=False)
        dpg.set_value(f"{self.winID}_status", "Arrêté")
        dpg.configure_item(f"{self.winID}_status", color=(255, 100, 100))
        dpg.set_value(f"{self.winID}_touche_courante", "")
        dpg.set_value(f"{self.winID}_position", "")

        self._log_message("Mapping arrêté par l'utilisateur")
        return

    def _fin_mapping(self, mapped_keys, total_keys):
        """Termine le processus de mapping"""
        self.is_mapping = False

        if self.keyboard_hook:
            keyboard.unhook(self.keyboard_hook)
            self.keyboard_hook = None

        dpg.set_value(f"{self.winID}_progression", 1.0)
        dpg.set_value(f"{self.winID}_progression_text", f"{mapped_keys}/{total_keys}")
        dpg.set_value(f"{self.winID}_status", "Terminé")
        dpg.configure_item(f"{self.winID}_status", color=(100, 255, 100))

        dpg.set_value(f"{self.winID}_start_btn", "Recommencer")
        dpg.configure_item(f"{self.winID}_start_btn", enabled=True)
        dpg.configure_item(f"{self.winID}_skip_btn", enabled=False)
        dpg.configure_item(f"{self.winID}_stop_btn", enabled=False)

        dpg.set_value(f"{self.winID}_touche_courante", "Configuration terminée!")
        dpg.set_value(f"{self.winID}_position", "")

        self._log_message(f"Mapping terminé! {mapped_keys} touches configurées sur {total_keys}")
        self._log_message("Données prêtes pour sauvegarde en base de données")
        self.krono.setup_mapping(self.mapping_data)
        return

    def _log_message(self, message) -> None:
        """Ajoute un message au journal"""
        timestamp = time.strftime("%H:%M:%S")
        log_text = f"[{timestamp}] {message}\n"

        current_log = dpg.get_value(f"{self.winID}_log_contenu")
        new_log = log_text + current_log

        # 50 derniers msg uniquement
        lines = new_log.split('\n')
        if len(lines) > 50:
            lines = lines[:50]
            new_log = '\n'.join(lines)

        dpg.set_value(f"{self.winID}_log_contenu", new_log)
        return

    def get_mapping_data(self) -> dict:
        """Retourne les données de mapping sous forme de dictionnaire"""
        return self.mapping_data.copy()


class Statistiques(BebeWindow):
    """
    Class pour afficher les statistiques d'une session qui sera sélectionnée
    """

    def __init__(self, krono_instance) -> None:
        super().__init__("Statistiques", krono_instance)
        self.krono = krono_instance
        self.data_apm = []
        self.data_session = {}
        self.data_session_list = []
        self.correspondance_session_affichage = {}
        self.combo_val = ""
        return

    def _naissance(self) -> None:
        self.set_donnees()
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Statistiques")
            dpg.add_separator()
            with dpg.group(horizontal=False):
                with dpg.group(horizontal=True):
                    with dpg.group():
                        dpg.add_text("Session")
                        dpg.add_combo(
                            tag="choix_session",
                            items=self.data_session_list,
                            width=400,
                            callback=self.selectionne_session,
                            default_value=self.combo_val
                        )
                        dpg.add_spacer()
                        dpg.add_text("Stats générales")

                    with dpg.group():
                        dpg.add_text("Touches du jeu")

                    with dpg.group():
                        dpg.add_text("Latences des appuis")

                with dpg.plot(label="Action Clavier par Minute", width=-1, height=500, crosshairs=True):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Temps (minutes)", auto_fit=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="Nombre d'appuis (u.a)") as y_axis:
                        dpg.add_line_series([x[0] for x in self.data_apm], [y[1] for y in self.data_apm], label="APM brut", parent=y_axis)
                        dpg.add_line_series([x[0] for x in self.data_apm], [y[2] for y in self.data_apm], label="APM mobile", parent=y_axis)


    def selectionne_session(self, sender, app_data, user_data) -> None:
        self.data_apm = self.krono.bd.select_apm_graphique(self.correspondance_session_affichage[app_data])
        self.combo_val = app_data
        self.actualiser_donnees()

    def set_donnees(self) -> None:
        """
        Applique au champ `self.data` les données que la fenêtre doit afficher.
        Appeler la méthode quand un changement de données est fait pour mettre à jour les données en mémoire.
        Returns:
            None
        """
        temp = self.krono.bd.select_session_choix()
        self.data_session = {cle: valeur for cle, valeur in temp}
        self.data_session_list = []
        for a,b in self.data_session.items():
            self.data_session_list.append(unix_to_date(a) + "\t" + b)
            self.correspondance_session_affichage[(unix_to_date(a)) + "\t" + b] = a
        self.data_session_list.reverse()
        return

    def actualiser_donnees(self) -> None:
        self.set_donnees()
        if dpg.does_item_exist(self.winID):
            dpg.delete_item(self.winID)

        self.vivante = False
        self.cree()
        return

class Clavier2DWindow(BebeWindow):
    """
    Class pour visualiser sur un clavier généré le nombre d’appuis par touche par coloration de ce dernier.
    """

    def __init__(self, krono_instance) -> None:
        """
        Création de l'instance.
        """
        super().__init__("Clavier2D", krono_instance)
        self.krono = krono_instance
        self.data_session = {}
        self.data_session_list = []
        self.correspondance_session_affichage = {}
        return

    def _naissance(self) -> None:
        """
        Définit les éléments de la fenêtre Clavier2DWindow.\n
            - Légende du nombre d’appuis mit en correspondance de la couleur.
            - Clavier 2D coloré en fonction du nombre d’appuis de la session choisie.
            - Choix de la session dont on veut visualiser les nombres d’appuis.
        Returns:
            None
        """
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            self.set_donnees()
            # get_colormap_color(colormap_id, index)
            dpg.add_text("Clavier 2D des appuis")
            dpg.add_separator()

            dpg.add_spacer(height=10)
            dpg.add_colormap_scale(label="Répartition", min_scale=0, max_scale=100)
            dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Hot)

            with dpg.group():
                dpg.add_listbox(
                    tag="choix_session_clavier",
                    items=self.data_session_list,
                    width=300,
                    num_items=5
                )

                dpg.add_text("Date: Aucune sélection", tag="date_session_clavier")



    def set_donnees(self) -> None:
        """
        Applique au champ `self.data` les données que la fenêtre doit afficher.
        Appeler la méthode quand un changement de données est fait pour mettre à jour les données en mémoire.
        Returns:
            None
        """
        temp = self.krono.bd.select_session_choix()
        self.data_session = {cle: valeur for cle, valeur in temp}
        self.data_session_list = []
        for a,b in self.data_session.items():
            self.data_session_list.append(unix_to_date(a) + "\t" + b)
            self.correspondance_session_affichage[(unix_to_date()) + "\t" + b] = a

        print(self.data_session_list)
        print(self.correspondance_session_affichage)
        return

    def actualiser_donnees(self) -> None:
        self.set_donnees()
        if dpg.does_item_exist(self.winID):
            dpg.delete_item(self.winID)

        self.vivante = False
        self.cree()
        return


def unix_to_time(horaire: int = 0, retour: bool = True) -> Union[str, tuple[int, int, int]]:
    """
    Transforme une durée au format Unix en chaine de character ou en un tuple d'entier correspondant aux heures, minutes
    secondes de l'horaire.
    Args :
        horaire (int) : Une durée au format Unix.
        retour (bool) : True pour une chaine de character, false pour un tuple d'entier.

    Returns :
        La durée sous le format en fonction du paramètre retour.

    """
    heure = horaire // 3600
    mini = (horaire % 60) // 60
    sec = horaire % 60

    if retour:
        heure = str(heure)
        mini = str(mini)
        if len(mini) == 1:
            mini = "0" + mini
        sec = str(sec)
        if len(sec) == 1:
            sec = "0" + sec
        return f"{heure}:{mini}:{sec}"
    else:
        return heure, mini, sec


def unix_to_date(horaire: int = 0, type_retour: int = 0) -> Union[str, datetime]:
    """
    Transforme un horaire au format Unix au format Jour/Mois/Année Heure:Minutes:Seconde en chaine de character ou
    au format datetime.
    Args :
        horaire (int) : L'horodatage au format Unix.
        type_retour (int) : 0 pour Jour/Mois/Année Heure:Minutes:Second, 1 sans seconde et sinon sous forme de datetime

    Returns :
        L'horodatage sous le format en fonction du paramètre retour.
    """
    if type_retour == 0:
        return datetime.datetime.fromtimestamp(horaire).strftime("%d/%m/%Y %H:%M:%S")
    elif type_retour == 1:
        return datetime.datetime.fromtimestamp(horaire).strftime("%d/%m/%Y %H:%M")
    else:
        return datetime.time
