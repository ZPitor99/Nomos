import ctypes
import dearpygui.dearpygui as dpg
import os
import datetime
from typing import Union

ctypes.windll.shcore.SetProcessDpiAwareness(2)


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
                    dpg.add_menu_item(label="Statistique")
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


class AccueilWindow(BebeWindow):
    """
    Class de la fenêtre d'accueil de l'interface.
    """

    def __init__(self, krono_instance) -> None:
        """
        Création de l'instance
        """
        super().__init__("Accueil", krono_instance)
        return

    def _naissance(self) -> None:
        """
        Définit les éléments de la fenêtre AccueilWindow.
            - Actions rapides
            - Résumer des sessions déjà présentes
        Returns:
            None
        """
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Bienvenue dans Nomos !")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=200):
                    dpg.add_text("Actions rapides")
                    dpg.add_separator()
                    dpg.add_button(label="Faire une écoute", width=-1,
                                   callback=lambda: self.get_main_window().gestionnaire_windows.afficher_window(
                                       "Ecoute"))
                    dpg.add_button(label="Voir statistiques", width=-1)
                    dpg.add_button(label="Configuration", width=-1)

                dpg.add_spacer(width=20)

                with dpg.child_window(width=-1, height=200):
                    dpg.add_text("Informations")
                    dpg.add_separator()
                    dpg.add_text("Dernière écoute : Aucune")
                    dpg.add_text("Sessions totales : 0")
                    dpg.add_text("Temps total : 0h 0m")
        return

    def get_main_window(self):
        """Méthode helper pour accéder à la fenêtre principale"""
        return dpg.get_item_user_data("main_win") if dpg.does_item_exist("main_win") else None


class EcouteWindow(BebeWindow):
    """
    Class de la fenêtre dearpygui pour gérer les écoutes.
    """

    def __init__(self, krono_instance):
        """
        Création de l'instance.
        """
        super().__init__("Ecoute", krono_instance)
        self.item_activation = ["bnt_ecoute", "btn_creer"]
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
                with dpg.child_window(width=300, height=250):
                    dpg.add_text("Lancer une écoute")
                    dpg.add_separator()
                    dpg.add_button(label="Nouvelle écoute", width=-1, callback=lambda: self.start_ecoute(),
                                   tag="bnt_ecoute")
                    dpg.add_text("Nom session")
                    dpg.add_input_text(width=-1, tag="champ_nom")
                    dpg.add_text("Jeu")
                    dpg.add_combo(width=-1, items=self.data["liste_jeu"], tag="champ_jeu")

                dpg.add_spacer(width=20)
                with dpg.group():
                    with dpg.child_window(width=-1, height=200):
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
                                                      items=sorted(list(self.data["dict_rep_code"].keys())))
                                    else:
                                        dpg.add_input_text(width=200, tag=elem[2])
                        dpg.add_spacer(height=15)
                        dpg.add_button(label="Créer", callback=lambda: self.valider_nouveau_jeu(), tag="btn_creer")

                    dpg.add_text("Enregistrement en cour", tag="enregistrement", color=(21, 20, 25))

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
        self.data["dict_rep_code"] = {v: k for k, v in
                                      {cle: valeur[0] for cle, valeur in self.krono.mapping.items()}.items()}
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
        Méthode pour valider la création d'un nouveau jeu. Récupère les données des champs dpg necessaire pour la création
        et envoie les données pour faire l'ajout. Puis actualise la fenêtre.
        Returns:
            None
        """
        val1 = dpg.get_value("champ_jeu1")
        val2 = dpg.get_value("champ_jeu2")
        val3 = self.data["dict_rep_code"][dpg.get_value("champ_jeu3")]
        val4 = self.data["dict_rep_code"][dpg.get_value("champ_jeu4")]
        val5 = self.data["dict_rep_code"][dpg.get_value("champ_jeu5")]
        val6 = self.data["dict_rep_code"][dpg.get_value("champ_jeu6")]
        ajout = self.krono.bd.ajout_jeu(val1, val2, val3, val4, val5, val6)
        if ajout:
            with dpg.window(label="Information", modal=True, no_close=True, width=300, height=150, tag="popup_success",
                            pos=(dpg.get_viewport_client_width() // 2 - 150,
                                 dpg.get_viewport_client_height() // 2 - 75)):
                dpg.add_text("Jeu ajouté avec succès")
                dpg.add_spacer(height=10)
                dpg.add_button(label="OK", width=100, callback=lambda: dpg.delete_item("popup_success"))

        self.actualiser_donnees()
        return

    def start_ecoute(self) -> None:
        """
        Lance l'écoute des frappes pour l'enregistrement. Affiche un message de fin pour informer de la fin de l'enregistrement.
        Returns:
            None
        """
        for elem in self.item_activation:
            dpg.configure_item(elem, enabled=False)
        dpg.configure_item("enregistrement", color=(63,234,21))

        valjeu = dpg.get_value("champ_jeu")
        valnom = dpg.get_value("champ_nom")
        self.krono.start(valnom, valjeu)

        with dpg.window(label="Information", modal=True, no_close=True, width=300, height=150, tag="popup_ecoute",
                        pos=(dpg.get_viewport_client_width() // 2 - 150, dpg.get_viewport_client_height() // 2 - 75),
                        no_title_bar=True):
            from Theme_NeoDark import theme
            dpg.bind_item_theme("popup_ecoute", theme)
            dpg.add_text("Fin de la session", indent=50)
            dpg.add_spacer(height=10)
            dpg.add_button(label="OK", width=-1, callback=lambda: dpg.delete_item("popup_ecoute"))

        for elem in self.item_activation:
            dpg.configure_item(elem, enabled=True)
        dpg.configure_item("enregistrement", color=(21, 20, 25))

        self.actualiser_donnees()
        return


class Configuration(BebeWindow):

    def __init__(self, krono_instance) -> None:
        super().__init__("Conf", krono_instance)
        return

    def _naissance(self) -> None:
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            # get_colormap_color(colormap_id, index)
            dpg.add_text("Configuration des touches")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=500, height=-1):
                    dpg.add_text("Instructions")
                    dpg.add_separator()
                    dpg.add_spacer(height=10)
                    dpg.add_text("La configuration des touches est nécessaire pour que l'application associe"
                                 " correctement la touche présser et le caractère de la touche.",
                                 bullet=True, wrap=475)
                    dpg.add_spacer(height=10)
                    dpg.add_text("Appuyer sur la touche correspondante au caractère affiché.",
                                 bullet=True, wrap=475)
                    dpg.add_spacer(height=10)
                    dpg.add_text("Appuyer sur Passer si la touche n'est pas présente sur votre clavier.",
                                 bullet=True, wrap=475)
                    dpg.add_spacer(height=10)
                    dpg.add_text("La configuration est faite sur la base d'un clavier azerty standardisé."
                                 "La configuration se fera de gauche à droite, de bas en haut",
                                 bullet=True, wrap=475)


class Clavier2DWindow(BebeWindow):
    """
    Class pour visualiser sur un clavier généré le nombre d'appuis par touche par coloration de ce dernier.
    """

    def __init__(self, krono_instance) -> None:
        """
        Création de l'instance.
        """
        super().__init__("Clavier2D", krono_instance)
        return

    def _naissance(self) -> None:
        """
        Définit les éléments de la fenêtre Clavier2DWindow.\n
            - Légende du nombre d'appuis mit en correspondance de la couleur.
            - Clavier 2D coloré en fonction du nombre d'appuis de la session choisie.
            - Choix de la session dont on veut visualiser les nombres d'appuis.
        Returns:
            None
        """
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            # get_colormap_color(colormap_id, index)
            dpg.add_text("Clavier 2D des appuis")
            dpg.add_separator()

            dpg.add_spacer(height=10)
            dpg.add_colormap_scale(label="Répartition", min_scale=0, max_scale=100)
            dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Hot)


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


def unix_to_date(horaire: int = 0, retour: bool = True) -> Union[str, datetime]:
    """
    Transforme un horaire au format Unix au format Jour/Mois/Année Heure:Minutes:Seconde en chaine de character ou
    au format datetime.
    Args :
        horaire (int) : L'horodatage au format Unix.
        retour (bool) : True pour la chaine de character, False pour le format datetime.

    Returns :
        L'horodatage sous le format en fonction du paramètre retour.
    """
    if retour:
        return datetime.datetime.fromtimestamp(horaire).strftime("%d/%m/%Y %H:%M:%S")
    else:
        return datetime.time
