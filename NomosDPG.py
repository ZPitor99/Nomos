import ctypes
import dearpygui.dearpygui as dpg
import os

ctypes.windll.shcore.SetProcessDpiAwareness(2)

dpg.create_context()
dpg.create_viewport(title='Nomos', width=1280, height=720)
icon_path = "ressources/Nomos.ico"
if os.path.exists(icon_path):
    dpg.set_viewport_small_icon(icon_path)
    dpg.set_viewport_large_icon(icon_path)

from Theme_NeoDark import theme
dpg.bind_theme(theme)

class MainWin:
    def __init__(self):
        self.winID = "main_win"

        self.gestionnaire_windows = GestionWindow()
        self.gestionnaire_windows.nouvelle_window("Accueil", AccueilWindow())

        self.fait_naitre_main_window()

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

            # Ajustement theme
            with dpg.theme() as mainwin_theme:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 25, 255))
            dpg.bind_item_theme(win_main, mainwin_theme)


class GestionWindow:
    def __init__(self):
        self.window_courante = None
        self.windows = {}

    def nouvelle_window(self, nom:str, window):
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

class BebeWindow:
    def __init__(self, window_id):
        self.winID = window_id
        self.vivante = False

        def cree(self):
            if not self.vivante:
                self.naissance()
                self.vivante = True

        def _naissance(self):
            pass

class AccueilWindow(BebeWindow):
    def __init__(self):
        super().__init__("Accueil")

    def _naissance(self):
        with dpg.window(tag=self.winID, label="Accueil"):
            dpg.add_text("Accueil")


def main():
    dpg.create_context()

    main_win = MainWin()

    dpg.create_viewport(title='Nomos', width=1280, height=720)
    dpg.setup_dearpygui()
    dpg.set_primary_window(main_win.winID, True)

    main_win.gestionnaire_windows.afficher_window("Accueil")

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()