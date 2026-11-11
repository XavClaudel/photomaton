import os
import tkinter as tk
from typing import Any, TYPE_CHECKING

from PIL import Image, ImageTk

import usb_manager
import printer_manager
import web_server_manager

if TYPE_CHECKING:
    from main import PhotomatonApp


class ConfigScreen(tk.Frame):
    """
    Un widget Frame qui encapsule tout l'écran de configuration.
    """
    def __init__(self, master: tk.Frame, app_ref: "PhotomatonApp", on_start_callback: callable):
        super().__init__(master, bg=app_ref.COLOR_BG)
        self.app = app_ref
        self.config = app_ref.config
        self.on_start_callback = on_start_callback

        # --- Widgets internes à l'écran de configuration ---
        self.gear_icon_tk: ImageTk.PhotoImage
        self.config_vars: dict[str, tk.BooleanVar] = {}
        self.toggle_buttons: dict[str, tk.Canvas] = {}
        self.marking_text_var: tk.StringVar
        self.marking_text_entry: tk.Entry
        self.marking_options_frame: tk.Frame
        self.marking_font_frame: tk.Frame
        self.marking_font_var: tk.StringVar
        self.marking_size_choice: tk.StringVar
        self.size_buttons: dict[str, tk.Button]
        self.marking_position_var: tk.StringVar
        self.marking_color_var: tk.StringVar

        self.create_config_widgets()

    def create_config_widgets(self):
        """Crée et positionne tous les widgets de l'écran de configuration."""
        # --- Titre de l'écran ---
        title_frame: tk.Frame = tk.Frame(self, bg=self.app.COLOR_BG)
        title_frame.pack(side="top", pady=(5, 0), anchor="n")

        # On essaie de charger un SVG, sinon un PNG.
        gear_icon = self.app.load_icon("gear_icon.png", (40, 40))
        if gear_icon:
            self.gear_icon_tk = gear_icon # Garde une référence pour éviter la suppression par le garbage collector
            gear_label: tk.Label = tk.Label(title_frame, image=self.gear_icon_tk, bg=self.app.COLOR_BG)
            gear_label.pack(side="left", padx=(0, 15))

        tk.Label(title_frame, text="Options du Photomaton", font=("Arial", 28, "bold"), bg=self.app.COLOR_BG, fg=self.app.COLOR_TEXT).pack(side="left")

        from PIL import Image, ImageTk
        import os
        
        # Pour remonter l'icône, on la charge et on ajoute de l'espace transparent en bas
        icon_path = os.path.join("assets", "play.png")
        if os.path.exists(icon_path):
            img = Image.open(icon_path).convert("RGBA")
            img = img.resize((40, 40), Image.Resampling.LANCZOS)
            padded_img = Image.new("RGBA", (40, 50), (0, 0, 0, 0)) # 10px de vide en bas
            padded_img.paste(img, (0, 0))
            icon_play = ImageTk.PhotoImage(padded_img)
        else:
            icon_play = self.app.load_icon("play.png", (40, 40))

        start_button = tk.Button(self, text="  Lancer le Photomaton", image=icon_play, compound="left", command=self.start_app, 
                                 font=("Arial", 22, "bold"), bg=self.app.COLOR_PRIMARY, fg="white", 
                                 activebackground=self.app.ACTIVE_PRIMARY, activeforeground="white",
                                 relief="flat", bd=0, highlightthickness=0)
        start_button.image = icon_play # Garde une référence pour éviter la suppression
        start_button.config(padx=15) 
        # ipady réduit pour gagner de la place
        start_button.pack(side="bottom", fill="x", padx=30, pady=(5, 10), ipady=10)
        self.app.apply_hover_effect(start_button, self.app.HOVER_PRIMARY, self.app.COLOR_PRIMARY)

        content_frame: tk.Frame = tk.Frame(self, bg=self.app.COLOR_BG)
        content_frame.pack(side="top", pady=10)

        options = {
            "enable_printing": "Activer l'impression",
            "enable_usb_save": "Activer la sauvegarde sur USB",
            "enable_web_server": "Activer le QR Code de téléchargement",
            "enable_personalization": "Personnalisation des photos",
            "enable_text_marking": "Marquage photo"
        }

        # Conteneur pour la liste d'options
        list_frame = tk.Frame(content_frame, bg=self.app.COLOR_BG)
        list_frame.pack(fill='x', padx=40, pady=5)

        for key, text in options.items():
            row_frame = tk.Frame(list_frame, bg=self.app.COLOR_BG)
            row_frame.pack(fill='x', pady=2) # Padding réduit pour gagner de la place verticale
            
            label = tk.Label(row_frame, text=text, font=("Arial", 16), bg=self.app.COLOR_BG, fg=self.app.COLOR_GREY, anchor="w")
            label.pack(side="left", fill='x', expand=True)
            
            var = tk.BooleanVar(value=self.config.get(key, False))
            self.config_vars[key] = var
            
            switch = tk.Canvas(row_frame, width=50, height=25, bg=self.app.COLOR_BG, highlightthickness=0)
            switch.pack(side="right", padx=(20, 0))
            switch.bind("<Button-1>", lambda event, k=key: self.toggle_option(k))
            self.toggle_buttons[key] = switch
            self.update_toggle_appearance(key)
            
            if key == "enable_text_marking":
                self.create_marking_widgets(content_frame)

        if self.config.get("enable_text_marking"):
            self.show_marking_text_entry(True)

    def create_marking_widgets(self, parent: tk.Frame):
        """Crée les widgets spécifiques à l'option de marquage texte."""
        self.marking_text_var = tk.StringVar(value=self.config.get("marking_text", ""))
        self.marking_text_entry = tk.Entry(parent, textvariable=self.marking_text_var, font=("Arial", 14), 
                                           bg=self.app.COLOR_BG_LIGHT, fg=self.app.COLOR_TEXT, relief="flat", 
                                           justify="center", insertbackground=self.app.COLOR_TEXT)

        self.marking_options_frame = tk.Frame(parent, bg=self.app.COLOR_BG)
        self.marking_font_frame = tk.Frame(parent, bg=self.app.COLOR_BG)

        font_files = [f for f in os.listdir("assets") if f.endswith('.ttf')] or ["Lobster-Regular.ttf"]
        self.marking_font_var = tk.StringVar(value=self.config.get("marking_text_font", font_files[0]))
        font_menu = self._create_option_menu(self.marking_font_frame, self.marking_font_var, font_files, command=self.update_marking_preview)
        font_menu.pack(side="left", expand=True, fill="x", padx=(0, 10))

        size_frame = tk.Frame(self.marking_font_frame, bg=self.app.COLOR_BG)
        size_frame.pack(side="left", expand=True, fill="x", padx=(10, 0))

        self.size_buttons = {}
        for size in ["Petit", "Moyen", "Gros"]:
            btn = tk.Button(size_frame, text=size, font=("Arial", 12), relief="flat", command=lambda s=size: self.select_size(s, update_preview=True))
            btn.pack(side="left", expand=True, fill="x", ipady=5)
            self.size_buttons[size] = btn
        
        size_map_inv = {40: "Petit", 60: "Moyen", 80: "Gros"}
        self.marking_size_choice = tk.StringVar(value=size_map_inv.get(self.config.get("marking_text_size", 60), "Moyen"))
        self.update_size_buttons_appearance()

        pos_options = ["En bas à droite", "En bas à gauche", "En haut à droite", "En haut à gauche"]
        self.marking_position_var = tk.StringVar(value=self.config.get("marking_text_position", pos_options[0]))
        pos_menu = self._create_option_menu(self.marking_options_frame, self.marking_position_var, pos_options)
        pos_menu.pack(side="left", expand=True, fill="x", padx=(0, 10))

        color_options = ["Blanc", "Noir", "Rouge", "Jaune"]
        self.marking_color_var = tk.StringVar(value=self.config.get("marking_text_color", color_options[0]))
        color_menu = self._create_option_menu(self.marking_options_frame, self.marking_color_var, color_options, command=self.update_marking_preview)
        color_menu.pack(side="left", expand=True, fill="x", padx=(10, 0))

    def _create_option_menu(self, parent: tk.Frame, var: tk.StringVar, options: list[str], **kwargs) -> tk.OptionMenu:
        """Crée et stylise un menu déroulant standard pour l'application."""
        menu = tk.OptionMenu(parent, var, *options, **kwargs)
        menu.config(font=("Arial", 12), bg=self.app.COLOR_BG_LIGHT, fg=self.app.COLOR_TEXT,
                    activebackground=self.app.COLOR_BG_LIGHT, activeforeground=self.app.COLOR_PRIMARY,
                    relief="flat", highlightthickness=0, bd=0, indicatoron=0)
        menu["menu"].config(font=("Arial", 12), bg=self.app.COLOR_BG_LIGHT, fg=self.app.COLOR_TEXT, activebackground=self.app.COLOR_PRIMARY)
        return menu

    def show_marking_text_entry(self, show: bool):
        """Affiche ou cache les options détaillées pour le marquage texte."""
        if show:
            self.marking_text_entry.pack(fill='x', padx=40, pady=(0, 5))
            self.marking_font_frame.pack(fill='x', padx=40, pady=(0, 5))
            self.marking_options_frame.pack(fill='x', padx=40, pady=(0, 5))
            self.update_marking_preview()
        else:
            self.marking_text_entry.pack_forget()
            self.marking_font_frame.pack_forget()
            self.marking_options_frame.pack_forget()

    def update_marking_preview(self, *args):
        """Met à jour le style du champ de saisie du texte pour prévisualiser la police et la couleur."""
        try:
            font_name = self.marking_font_var.get()
            size_map = {"Petit": 16, "Moyen": 20, "Gros": 24}
            font_size = size_map.get(self.marking_size_choice.get(), 20)
            color_map = {"Blanc": "white", "Noir": "black", "Rouge": "#E74C3C", "Jaune": "#F1C40F"}
            font_color = color_map.get(self.marking_color_var.get(), "white")
            self.marking_text_entry.config(font=(font_name, font_size), fg=font_color)
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'aperçu du marquage : {e}")

    def select_size(self, size: str, update_preview: bool = False):
        """Gère la sélection d'une taille de police."""
        self.marking_size_choice.set(size)
        self.update_size_buttons_appearance()
        if update_preview:
            self.update_marking_preview()

    def update_size_buttons_appearance(self):
        """Met à jour l'apparence des boutons de taille pour indiquer la sélection actuelle."""
        selected_size = self.marking_size_choice.get()
        for size, button in self.size_buttons.items():
            is_selected = size == selected_size
            original_color = self.app.COLOR_PRIMARY if is_selected else self.app.COLOR_BG_LIGHT
            hover_color = self.app.HOVER_PRIMARY if is_selected else self.app.HOVER_BG_LIGHT
            active_color = self.app.ACTIVE_PRIMARY if is_selected else self.app.COLOR_BG
            button.config(
                bg=original_color, fg="white" if is_selected else self.app.COLOR_TEXT,
                activebackground=active_color, activeforeground="white"
            )
            self.app.apply_hover_effect(button, hover_color, original_color)

    def toggle_option(self, key: str):
        """Inverse la valeur d'une option et met à jour l'interface."""
        new_value = not self.config_vars[key].get()

        # Affiche des avertissements non-bloquants si le matériel requis est manquant
        if new_value: # On ne vérifie que lors de l'activation
            if key == "enable_usb_save" and usb_manager.find_usb_drive() is None:
                self.app.show_notification("Avertissement : Aucune clé USB n'est détectée.", 'warning')
            
            if key == "enable_printing" and not printer_manager.check_printers():
                self.app.show_notification("Avertissement : Aucune imprimante n'est détectée.", 'warning')

            if key == "enable_web_server" and web_server_manager.get_local_ip() == '127.0.0.1' and not self.config.get('web_server_ip'):
                self.app.show_notification("Aucune connexion réseau détectée pour le QR code.", 'warning')
                # Pour le QR code, c'est bloquant car inutile sans réseau
                return

        if key == "enable_text_marking":
            self.show_marking_text_entry(new_value)
        
        self.config_vars[key].set(new_value)
        self.update_toggle_appearance(key)

    def update_toggle_appearance(self, key: str):
        """Redessine le widget 'interrupteur' pour refléter son état (activé/désactivé)."""
        switch = self.toggle_buttons[key]
        is_on = self.config_vars[key].get()
        switch.delete("all")
        w, h, padding = 50, 25, 3
        radius = h / 2
        track_color = self.app.COLOR_SUCCESS if is_on else self.app.COLOR_BG_LIGHT
        switch.create_oval(0, 0, h, h, fill=track_color, outline=track_color)
        switch.create_oval(w - h, 0, w, h, fill=track_color, outline=track_color)
        switch.create_rectangle(radius, 0, w - radius, h, fill=track_color, outline=track_color)
        
        # Dessine la poignée
        handle_x = w - h + padding if is_on else padding
        switch.create_oval(handle_x, padding, handle_x + h - 2 * padding, h - padding, fill="#FFFFFF", outline="#FFFFFF")

    def start_app(self):
        """Rassemble les valeurs de configuration de l'interface et appelle le callback pour démarrer l'application."""
        for key, var in self.config_vars.items():
            self.config[key] = var.get()
        if self.config.get("enable_text_marking"):
            self.config["marking_text"] = self.marking_text_var.get()
            self.config["marking_text_position"] = self.marking_position_var.get()
            self.config["marking_text_color"] = self.marking_color_var.get()
            self.config["marking_text_font"] = self.marking_font_var.get()
            size_map = {"Petit": 40, "Moyen": 60, "Gros": 80}
            self.config["marking_text_size"] = size_map.get(self.marking_size_choice.get(), 60)
        
        self.on_start_callback(self.config)
