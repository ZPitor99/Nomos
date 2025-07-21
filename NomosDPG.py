import ctypes
import dearpygui.dearpygui as dpg
import os
import datetime

from AppKrono import AppKrono

ctypes.windll.shcore.SetProcessDpiAwareness(2)


class MainWin:
    def __init__(self):
        self.winID = "main_win"
        self.zone_contenu = "Contenue_main_win"

        self.gestionnaire_windows = GestionWindow(self.zone_contenu)
        self.gestionnaire_windows.nouvelle_window("Accueil", AccueilWindow())
        self.gestionnaire_windows.nouvelle_window("Ecoute", EcouteWindow())

        self.gestionnaire_windows.nouvelle_window("Clavier2D", Clavier2DWindow())

        self.fait_naitre_main_window()
        return

    def fait_naitre_main_window(self):
        with dpg.window(tag=self.winID) as win_main:
            with dpg.menu_bar():
                with dpg.menu(label="Fichier"):
                    dpg.add_menu_item(label="Accueil", callback=lambda: self.gestionnaire_windows.afficher_window("Accueil"))
                    dpg.add_menu_item(label="Exporter données")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Plein écran", callback=lambda: dpg.toggle_viewport_fullscreen())
                    dpg.add_menu_item(label="Paramètres")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Quitter", callback=lambda: dpg.stop_dearpygui())

                with dpg.menu(label="Ecoute"):
                    dpg.add_menu_item(label="Enregistrer", callback=lambda: self.gestionnaire_windows.afficher_window("Ecoute"))
                    dpg.add_menu_item(label="Configurer")

                with dpg.menu(label="Stats"):
                    dpg.add_menu_item(label="Statistique")
                    dpg.add_menu_item(label="Clavier 2D", callback=lambda: self.gestionnaire_windows.afficher_window("Clavier2D"))

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
                    dpg.add_menu_item(label="Show Item Registry",callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))
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

    def nouvelle_window(self, nom:str, window):
        window.parent_id = self.parent
        self.windows[nom] = window

    def afficher_window(self, nom:str):
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
    def __init__(self, window_id):
        self.winID = window_id
        self.vivante = False
        self.parent_id = None
        self.data = {}
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
    def __init__(self):
        super().__init__("Accueil")
        return

    def _naissance(self):
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Bienvenue dans Nomos !")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=200):
                    dpg.add_text("Actions rapides")
                    dpg.add_separator()
                    dpg.add_button(label="Faire une écoute", width=-1,
                                   callback=lambda: main_win.gestionnaire_windows.afficher_window("Ecoute"))
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

class EcouteWindow(BebeWindow):
    def __init__(self):
        super().__init__("Ecoute")
        return
    
    def _naissance(self):
        self.set_donnees()
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            dpg.add_text("Enregistrement des touches")
            dpg.add_separator()

            with dpg.group(horizontal=True):
                with dpg.child_window(width=300, height=250):
                    dpg.add_text("Démarer une écoute")
                    dpg.add_separator()
                    dpg.add_button(label="Nouvelle écoute", width=-1, callback=lambda: self.start_ecoute())
                    dpg.add_text("Nom session")
                    dpg.add_input_text(width=-1, tag="champ_nom")
                    dpg.add_text("Jeu")
                    dpg.add_combo(width=-1, items=self.data["liste_jeu"], tag="champ_jeu")

                dpg.add_spacer(width=20)

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
                    dpg.add_button(label="Créer", callback=lambda: self.valider_nouveau_jeu())

            dpg.add_spacer(height=10)
            dpg.add_text(f"Nombre total d'écoute faite:  {len(self.data["ecoute_session_table"])}")
            dpg.add_separator()
            with dpg.table(header_row=True, no_host_extendX=True, context_menu_in_body=True,
                           row_background=True, policy=dpg.mvTable_SizingStretchSame,scrollY=True,
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
                        dpg.add_text(unix_to_time(i[2]-i[1]))
                        dpg.add_text(f"{i[3]}")

    def set_donnees(self):
        self.data["ecoute_session_table"] = krono.bd.select_ecoute_session()
        self.data["dict_rep_code"] = {v: k for k, v in {cle: valeur[0] for cle, valeur in krono.mapping.items()}.items()}
        self.data["liste_jeu"] = [s[0] for s in krono.bd.select_list_jeu()]
        return

    def actualiser_donnees(self):
        self.set_donnees()
        if dpg.does_item_exist(self.winID):
            dpg.delete_item(self.winID)

        self.vivante = False
        self.cree()

        return

    def valider_nouveau_jeu(self):
        val1 = dpg.get_value("champ_jeu1")
        val2 = dpg.get_value("champ_jeu2")
        val3 = self.data["dict_rep_code"][dpg.get_value("champ_jeu3")]
        val4 = self.data["dict_rep_code"][dpg.get_value("champ_jeu4")]
        val5 = self.data["dict_rep_code"][dpg.get_value("champ_jeu5")]
        val6 = self.data["dict_rep_code"][dpg.get_value("champ_jeu6")]
        ajout = krono.bd.ajout_jeu(val1, val2, val3, val4, val5, val6)
        if ajout:
            with dpg.window(label="Information", modal=True, no_close=True, width=300, height=150, tag="popup_success",
                            pos=(dpg.get_viewport_client_width()//2-150, dpg.get_viewport_client_height()//2-75)):
                dpg.add_text("Jeu ajouté avec succès")
                dpg.add_spacer(height=10)
                dpg.add_button(label="OK", width=100, callback=lambda: dpg.delete_item("popup_success"))

        self.actualiser_donnees()
        return

    def start_ecoute(self):
        valjeu = dpg.get_value("champ_jeu")
        valnom = dpg.get_value("champ_nom")
        krono.start(valnom, valjeu)

        with dpg.window(label="Information", modal=True, no_close=True, width=300, height=150, tag="popup_ecoute",
                        pos=(dpg.get_viewport_client_width() // 2 - 150, dpg.get_viewport_client_height() // 2 - 75)):
            dpg.add_text("Fin de la session")
            dpg.add_spacer(height=10)
            dpg.add_button(label="OK", width=100, callback=lambda: dpg.delete_item("popup_ecoute"))

        self.actualiser_donnees()
        return
    
class Clavier2DWindow(BebeWindow):
    def __init__(self):
        super().__init__("Clavier2D")
        return
    
    def _naissance(self):
        with dpg.child_window(tag=self.winID, parent=self.parent_id, border=False):
            #get_colormap_color(colormap_id, index)
            dpg.add_text("Clavier 2D des appuis")
            dpg.add_separator()

            dpg.add_spacer(height=10)
            dpg.add_colormap_scale(label="Répartition", min_scale=0, max_scale=100)
            dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Hot)


def unix_to_time(horaire:int = 0, retour: bool = True) -> str | tuple[int, int, int]:
    """
    Transforme une durée au format unix en chaine de character ou en un tuple d’entier correspondant aux heures, minutes
    secondes de l’horaire
    Args :
        horaire (int) : Une durée au format unix
        retour (bool) : True pour une chaine de character, false pour un tuple d’entier

    Returns :
        La durée sous le format en fonction du paramètre retour

    """
    heure = horaire // 3600
    mini = (horaire % 60) // 60
    sec = horaire % 60

    if retour:
        heure = str(heure)
        mini = str(mini)
        if len(mini) == 1 :
            mini = "0" + mini
        sec = str(sec)
        if len(sec) == 1 :
            sec = "0" + sec
        return f"{heure}:{mini}:{sec}"
    else:
        return heure, mini, sec


def unix_to_date(horaire:int = 0, retour: bool = True) -> str | datetime:
    if retour:
        return datetime.datetime.fromtimestamp(horaire).strftime("%d/%m/%Y %H:%M:%S")
    else:
        return datetime.time


def main():
    dpg.create_context()

    try:
        from Theme_NeoDark import theme
        dpg.bind_theme(theme)
    except Exception as e:
        print(f"Theme_NeoDark non trouvé, utilisation du thème par défaut {e}")

    global main_win
    main_win = MainWin()

    dpg.create_viewport(title='Nomos', width=1280, height=720)

    icon_path = "ressources/Nomos.ico"
    if os.path.exists(icon_path):
        dpg.set_viewport_small_icon(icon_path)
        dpg.set_viewport_large_icon(icon_path)

    dpg.setup_dearpygui()
    dpg.set_primary_window(main_win.winID, True)

    main_win.gestionnaire_windows.afficher_window("Accueil")

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    global krono
    krono = AppKrono()
    main()