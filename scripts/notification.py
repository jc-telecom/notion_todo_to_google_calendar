import tkinter as tk


def show_notification(nb_new_events, nb_updated_events, nb_deleted_events):
    message = f"{nb_new_events} new events\n{nb_updated_events} updated events\n {nb_deleted_events} deleted events"
    # Créer une nouvelle fenêtre
    window = tk.Tk()
    window.title("Synchronisation succeeded")
    # Supprimer la bordure de la fenêtre
    # window.overrideredirect(True)
    frame = tk.Frame(window, bg="white")
    frame.pack(fill="both", expand=True)
    # Positionner la fenêtre en haut à droite de l'écran
    window.geometry(f"+{window.winfo_screenwidth() - 200}+30")

    # Charger l'image
    # Remplacez par le chemin vers votre image
    image = tk.PhotoImage(file="assets/icon.png")

    # Redimensionner l'image
    # Remplacez 2 par le facteur de sous-échantillonnage que vous souhaitez utiliser
    image = image.subsample(20, 20)

    # Ajouter l'image à la fenêtre
    image_label = tk.Label(window, image=image,
                           bg="white", width=50, height=65)
    image_label.pack(side="left")

    # Ajouter un message à la fenêtre
    label = tk.Label(window, text=message, bg="white",
                     fg="black", width=15, height=4, anchor="w")
    label.pack(side="right")

    # Fermer la fenêtre après 3 secondes
    label.after(5000, window.destroy)

    window.mainloop()
