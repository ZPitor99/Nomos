# Nomos

Nomos est une application en développement conçue pour capturer les appuis clavier pendant des sessions de jeu et produire, en fin de partie, des statistiques détaillées à destination de l'utilisateur. Les données sont stockées dans une base SQLite et une interface graphique est prévue via DearPyGui.

## Objectifs du projet

- Suivi des frappes clavier en temps réel durant une session de jeu.
- Génération de statistiques de performance à la fin d’une session.
- Stockage des données dans une base de données SQLite.
- Interface graphique simple et interactive.
- Architecture modulaire orientée objet.

## Fonctionnalités en cours de développement

- Capture des événements clavier.
- Enregistrement des événements dans une base SQLite.
- Calcul de statistiques simples (nombre total d'appuis, fréquence par touche).
- Configuration d’un logger pour le suivi des événements.
- Intégration d’une interface avec DearPyGui.

## Technologies

- Python (keyboard, dearpygui, logging ...)
- SQLite3 (SQL)
- Yaml

## Classes

- `AppKrono.py` : Modèle et controlleur général
- `GestionSQL.py` : Gérer les transactions avec la base de données
- `NomosDPG.py` : Interface graphique
