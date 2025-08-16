#!/usr/bin/env python3
"""
Point d'entrée principal de l'application Nomos.
"""

import sys
import os
from filelock import FileLock, Timeout
import traceback


def setup_paths():
    """
    Configure les chemins pour que l'application fonctionne correctement.
    """
    # Obtenir le répertoire racine du projet
    project_root = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(project_root, 'app')

    # Ajouter les dossiers au chemin Python
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Changer le répertoire de travail vers le dossier app
    # pour que les chemins relatifs dans AppKrono fonctionnent
    if os.path.exists(app_dir):
        os.chdir(app_dir)

    return project_root, app_dir


def main():
    """
    Fonction principale de l'application Nomos.
    """
    # Empêcher plusieurs lancements
    lock_path = os.path.join(os.path.expanduser("~"), ".Nomos.lock")
    print(lock_path)
    lock = FileLock(lock_path)

    try:
        # Tentative d'acquisition du verrou avec un timeout très court
        with lock.acquire(timeout=0.1):
            try:
                # Configuration des chemins
                project_root, app_dir = setup_paths()

                # Import des modules (après configuration des chemins)
                from AppKrono import AppKrono
                from NomosDPG import NomosDPG

                # Initialisation de l'application Krono
                krono = AppKrono()

                # Lancement de l'interface graphique
                app = NomosDPG(krono, project_root)
                app.run()

            except ImportError as e:
                print(f"Erreur d'import: {e}")
                print("Vérifiez que tous les fichiers sont présents dans le dossier 'app'")
                sys.exit(1)
            except FileNotFoundError as e:
                print(f"Fichier non trouvé: {e}")
                print("Vérifiez que tous les fichiers de configuration sont présents")
                sys.exit(1)
            except Exception as e:
                print(f"Erreur lors du lancement de l'application: {e}")
                tb = traceback.extract_tb(e.__traceback__)
                for frame in tb:
                    print(f"Fichier : {frame.filename}, Ligne : {frame.lineno}, Fonction : {frame.name}")
                sys.exit(1)

    except Timeout:
        print("Une instance de Nomos est déjà en cours d'exécution.")
        print("Veuillez fermer l'application existante avant d'en lancer une nouvelle.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors de l'acquisition du verrou: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()