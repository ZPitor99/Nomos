import ctypes
import dearpygui.dearpygui as dpg
import os

ctypes.windll.shcore.SetProcessDpiAwareness(2)


class MainWin:
    def __init__(self):
        self.winID = "main_win"
        self.zone_contenu = "Contenue_main_win"

        self.gestionnaire_windows = GestionWindow(self.zone_contenu)
        self.gestionnaire_windows.nouvelle_window("Accueil", AccueilWindow())

        self.fait_naitre_main_window()
        return

    def fait_naitre_main_window(self):
        with dpg.window(tag=self.winID) as win_main:
            with dpg.menu_bar():
                with dpg.menu(label="Fichier"):
                    dpg.add_menu_item(label="Accueil", callback=lambda: self.gestionnaire_windows.afficher_window("Accueil"))
                    dpg.add_menu_item(label="Exporter données")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Configurer")
                    dpg.add_menu_item(label="Plein écran", callback=lambda: dpg.toggle_viewport_fullscreen())
                    dpg.add_menu_item(label="Paramètres")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Quitter", callback=lambda: dpg.stop_dearpygui())

                with dpg.menu(label="Ecoute"):
                    dpg.add_menu_item(label="Faire une écoute")

                with dpg.menu(label="Stats"):
                    dpg.add_menu_item(label="Statistique")
                    dpg.add_menu_item(label="Clavier 2D")

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

        dpg.show_item(actuel.winID)
        self.window_courante = actuel.winID
        return

class BebeWindow:
    def __init__(self, window_id):
        self.winID = window_id
        self.vivante = False
        self.parent_id = None
        return

    def cree(self):
         if not self.vivante:
            self._naissance()
            self.vivante = True
         return

    def _naissance(self):
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
                    dpg.add_button(label="Nouvelle écoute", width=-1)
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


def main():
    dpg.create_context()

    try:
        from Theme_NeoDark import theme
        dpg.bind_theme(theme)
    except Exception as e:
        print(f"Theme_NeoDark non trouvé, utilisation du thème par défaut {e}")

    main_win = MainWin()

    dpg.create_viewport(title='Nomos', width=1280, height=720)

    icon_path = "ressources/Nomos.ico"
    if os.path.exists(icon_path):
        dpg.set_viewport_small_icon(icon_path)
        dpg.set_viewport_large_icon(icon_path)

    dpg.setup_dearpygui()
    dpg.create_viewport(title='Nomos', width=1280, height=720)
    dpg.set_primary_window(main_win.winID, True)

    main_win.gestionnaire_windows.afficher_window("Accueil")

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()