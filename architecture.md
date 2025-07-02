Structure
```
projet/
├── main.py                    # Script principal
├── scripts_sql/                    # Dossier des scripts SQL
│   ├── create_table.sql           # Création de table
│   ├── insert_keystroke.sql       # Insertion des frappes
│   ├── total_keystrokes.sql       # Total global
│   ├── top_keys.sql              # Top des touches
│   ├── keystrokes_per_minute.sql # Frappes par minute
│   ├── statistiques_avancees.sql # Tes analyses personnalisées
│   └── ...                       # Autres scripts custom
└── logger.log                  # Fichier de log
```

```
start()
│
├─> Démarre un thread qui insère toutes les 2s en base
│
├─> Lance l'écoute des touches (keyboard.hook)
│
├─> Attend ESC (keyboard.wait)
│
├─> Quand ESC pressé :
│     ├─> Arrête la boucle de commit
│     ├─> Envoie les frappes restantes en base
│     └─> Ferme la connexion BD
```

````
         [Logger]
            |
    -------------------
    |                 |
[StreamHandler]   [FileHandler]
    |                 |
[Console]         [Fichier log]

````