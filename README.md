# Nomos

Nomos est une application en développement conçue pour capturer les appuis clavier pendant des sessions de jeu et produire, en fin de partie, des statistiques détaillées à destination de l'utilisateur. Les données sont stockées dans une base SQLite et une interface graphique est prévue via DearPyGui.

## Objectifs du projet

- Suivi des frappes clavier en temps réel durant une session de jeu.
- Génération de statistiques de performance à la fin d’une session.
- Stockage des données dans une base de données SQLite.
- Interface graphique simple et interactive.
- Architecture modulaire orientée objet.

## Fonctionnalités faites

- Capture des événements clavier.
- Enregistrement des événements dans une base SQLite.
- Configuration d’un logger pour le suivi des événements.
- Intégration d’une interface avec DearPyGui. (Partiellement)


## Fonctionnalités en cours de développement

- Calcul de statistiques simples (nombre total d'appuis, fréquence par touche).
- Intégration d’une interface avec DearPyGui.
- Tester l'ensemble des classes
- Exporter en application utilisable par tous

## Technologies

- Python (keyboard, dearpygui, logging, datetime, ...)
- SQLite3 (SQL)
- Yaml

## Classes Principales

- `AppKrono.py` : Modèle et controlleur général
- `GestionSQL.py` : Gérer les transactions avec la base de données
- `NomosDPG.py` : Interface graphique

## Licence
Ce projet est sous licence **Creative Commons BY-NC-SA 4.0**  
[Consulter la licence](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---

### Ressources tierces :

- **Police Open Sans** – Copyright 2020 The Open Sans Project Authors  
  Sous licence **SIL Open Font License 1.1**  
  Le fichier de licence est disponible dans le dossier `ressources/OFL_OpenSans_Licence.txt`.

- **Bibliothèques Python utilisées** (standard & tierces, non-exhaustive) :
  - `ctypes`, `time`, `threading`, `os`, `datetime`, `queue`, `sys`, `logging`, `typing`, `sqlite3` (Python standard)
  - `keyboard`  
  - `dearpygui`  
  - `pytest`  
  - `yaml`  
  - `filelock`
  
  Les bibliothèques tierces sont sous leurs propres licences respectives (MIT, BSD, etc.). Consulte leurs dépôts pour plus de détails.

### Outils de développement utilisés

- **Visual Studio Code**
- **PyCharm**
- **Git**
- **DB Browser for SQLite**
