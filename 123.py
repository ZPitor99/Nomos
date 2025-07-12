import keyboard
import time

# Layout AZERTY brut (ligne/colonne = position physique sur clavier)
azerty_layout = [
    ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'],
    ['²', '&', 'é', '"', "'", '(', '-', 'è', '_', 'ç', 'à', ')', '=', 'Backspace'],
    ['Tab', 'a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '^', '$', 'Enter'],
    ['CapsLock', 'q', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'ù', '*'],
    ['Shift', '<', 'w', 'x', 'c', 'v', 'b', 'n', ',', ';', ':', '!', 'Shift'],
    ['Ctrl', 'Win', 'Alt', 'Space', 'AltGr', 'Menu', 'Ctrl'],
    ['Up', 'Down', 'Left', 'Right']
]


mapping = {}

print("Touche par touche, appuie sur les touches suivantes dans l'ordre affiché.")
print("S'il y a des doublons (ex: Shift), appuie toujours sur celui de gauche.")
time.sleep(3)

for row_idx, row in enumerate(azerty_layout):
    for col_idx, label in enumerate(row):
        while True:
            print(f"Appuie sur : {label} (ligne {row_idx}, col {col_idx})")
            event = keyboard.read_event()
            if event.event_type == 'down':
                mapping[event.scan_code] = {
                    "symbol": label,
                    "position": (row_idx, col_idx),
                    "valeur": event.name
                }
                print(f"✔ Capturé : scan_code={event.scan_code}, symbole={label}, position=({row_idx}, {col_idx})\n")
                break

print("\nMapping terminé ! Voici le dictionnaire :\n")
print(mapping)
time.sleep(3)
#
# import keyboard
#
#
# def on_key_event(event):
#     print(f"Name: {event.name}, Scan code: {event.scan_code}")
#
#
# keyboard.hook(on_key_event)
# keyboard.wait('esc')  # Quit with Escape
