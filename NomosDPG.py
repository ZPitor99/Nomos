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
        with dpg.window(tag=self.winID) as win_main:
            with dpg.menu_bar():
                with dpg.menu(label="Fichier"):
                    dpg.add_menu_item(label="Accueil")
                    dpg.add_menu_item(label="Exporter données")
                    dpg.add_menu_item(label="Plein écran", callback=lambda: dpg.toggle_viewport_fullscreen())
                    dpg.add_menu_item(label="Paramètres")
                    dpg.add_menu_item(label="Quitter", callback=lambda: dpg.stop_dearpygui())

                with dpg.menu(label="Ecoute"):
                    dpg.add_menu_item(label="Faire une écoute")

                with dpg.menu(label="Stats"):
                    dpg.add_menu_item(label="Statistique")
                    dpg.add_menu_item(label="Clavier 2D")

                with dpg.menu(label="Aide"):
                    dpg.add_menu_item(label="Mode d'emploi")
                    dpg.add_menu_item(label="Github")
                    dpg.add_menu_item(label="Contact")
                    dpg.add_menu_item(label="Dear PyGUI", callback=lambda: dpg.show_tool(dpg.mvTool_About))
                    dpg.add_menu_item(label="A propos")
                # DEV
                with dpg.menu(label="Tools"):
                    dpg.add_menu_item(label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug))
                    dpg.add_menu_item(label="Show Font Manager", callback=lambda: dpg.show_tool(dpg.mvTool_Font))
                    dpg.add_menu_item(label="Show Item Registry",callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry))
                    dpg.add_menu_item(label="Show Metrics", callback=lambda: dpg.show_tool(dpg.mvTool_Metrics))
                    dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda: dpg.toggle_viewport_fullscreen())
                    dpg.add_menu_item(label="Reopen all windows", callback=self.reopen_all_win)

            # Ajustement theme
            with dpg.theme() as mainwin_theme:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (20, 20, 25, 255))
            dpg.bind_item_theme(win_main, mainwin_theme)




    @staticmethod
    def reopen_all_win():
        all_items = dpg.get_all_items()

        for item in all_items:
            if dpg.get_item_type(item) == "mvAppItemType::mvWindowAppItem":
                dpg.configure_item(item, show=True)


main_win = MainWin()


# class HelloWorld:
#     def __init__(self, name=""):
#         self.winID = "Hello_World_win_" + str(dpg.generate_uuid())
#         with dpg.window(tag=self.winID, pos=(50, 50), width=-1, label="Hello World window " + str(name)):
#             dpg.add_text("Hello, World!")
#             dpg.add_button(label="Kill window", width=-1, callback=lambda: dpg.delete_item(self.winID))
#
#
# hello_world_win = HelloWorld("1")
# hello_world_win2 = HelloWorld("2")

# dpg.set_viewport_vsync(True)
dpg.setup_dearpygui()
dpg.set_primary_window("main_win", True)
dpg.show_viewport()

while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()