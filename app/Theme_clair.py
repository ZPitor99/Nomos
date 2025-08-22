import dearpygui.dearpygui as dpg

with dpg.theme() as theme:
    with dpg.font_registry():
        fontsize = 40
        default_font = dpg.add_font("../ressources/OpenSans-SemiBold.ttf", fontsize)

    dpg.bind_font(default_font)
    dpg.set_global_font_scale(0.65)

    with dpg.theme_component(dpg.mvAll):
        # Window & Layout
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1.2)  # Bordures un peu plus épaisses
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)  # Supprime la bordure de fenêtre
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)  # Bordures des child windows
        dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 1)  # Bordures des popups

        # Séparateurs et lignes - plus marqués
        dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextPadding, 20, 3)  # espacement autour des séparateurs
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 6)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 5)
        dpg.add_theme_style(dpg.mvStyleVar_IndentSpacing, 20)
        dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 12)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 18)
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_PopupBorderSize, 0)  # Supprime bordure des popups

        # Window Background - Base gris moderne
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (40, 42, 50, 255))  # gris de base moderne
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (40, 42, 50, 255))  # même couleur uniforme
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (42, 44, 52, 255))  # très légèrement plus clair
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (35, 37, 45, 255))  # plus foncé pour différenciation
        dpg.add_theme_color(dpg.mvThemeCol_Border, (65, 70, 80, 255))  # bordures plus visibles
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))  # pas d'ombres

        # Frames & Widgets - nuances de la même famille
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 47, 57, 255))  # légèrement plus clair que base
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (52, 55, 65, 255))  # survol dans la même famille
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (58, 62, 72, 255))  # actif plus clair mais cohérent

        # Buttons - nuances modernes
        dpg.add_theme_color(dpg.mvThemeCol_Button, (47, 50, 60, 255))  # proche du fond mais distinct
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (54, 58, 68, 255))  # survol harmonieux
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (60, 65, 75, 255))  # actif cohérent

        # Combo boxes - plus foncés mais dans la famille
        dpg.add_theme_color(dpg.mvThemeCol_Header, (32, 34, 42, 255))  # plus foncé que base
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (38, 40, 48, 255))  # survol subtil
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (45, 47, 57, 255))  # sélection visible

        # Titles & Headers - cohérents avec la famille
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (37, 39, 47, 255))  # dans la famille, un peu plus foncé
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (42, 44, 52, 255))  # légèrement plus clair
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, (32, 34, 42, 255))

        # Sliders & Grabs - accent moderne
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (65, 70, 85, 255))  # dans la famille mais distinct
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (70, 75, 90, 255))

        # Scrollbars - nuances subtiles
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (35, 37, 45, 255))  # fond discret
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (50, 52, 62, 255))  # poignée dans la famille
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (55, 58, 68, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (60, 65, 75, 255))

        # Checkboxes et Radio buttons
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (65, 70, 85, 255))  # cohérent avec sliders

        # Séparateurs et lignes de division
        dpg.add_theme_color(dpg.mvThemeCol_Separator, (70, 75, 85, 255))  # séparateurs bien visibles
        dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, (80, 85, 95, 255))  # survol des séparateurs
        dpg.add_theme_color(dpg.mvThemeCol_SeparatorActive, (85, 90, 100, 255))  # séparateurs actifs
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (120, 125, 135, 255))  # texte désactivé

        # Sélection de texte
        dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (55, 60, 70, 160))  # sélection dans la famille

        # Tabs - cohérentes avec le design
        dpg.add_theme_color(dpg.mvThemeCol_Tab, (37, 39, 47, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (45, 47, 57, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, (42, 44, 52, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, (32, 34, 42, 255))
        dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, (37, 39, 47, 255))

        # Graphs / Plots - à la fin du thème
        dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight, 2, category=dpg.mvThemeCat_Plots)
        dpg.add_theme_style(dpg.mvPlotStyleVar_FillAlpha, 0.50, category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvPlotCol_Crosshairs, (255, 0, 50, 175), category=dpg.mvThemeCat_Plots)