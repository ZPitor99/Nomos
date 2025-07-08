import tkinter as tk

def create_indicator():
    root = tk.Tk()
    root.overrideredirect(True)  # Supprime la bordure/fenêtre
    root.attributes("-topmost", True)  # Toujours au-dessus

    # Taille du carré
    square_size = 20

    # Obtenir dimensions écran
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Position : coin supérieur droit
    x = 10
    y = screen_height - square_size - 10

    # Appliquer position et taille
    root.geometry(f"{square_size}x{square_size}+{x}+{y}")
    root.configure(bg="blue")
    root.attributes("-disabled", True)  # Non interactif

    root.mainloop()

create_indicator()
