import os
import tkinter as tk
from typing import TYPE_CHECKING

from PIL import Image, ImageTk

if TYPE_CHECKING:
    from main import PhotomatonApp


class GalleryScreen(tk.Frame):
    """
    Un widget qui affiche une galerie des photos prises,
    permettant la navigation, l'impression et la suppression.
    """
    def __init__(self, master: tk.Frame, app_ref: "PhotomatonApp"):
        super().__init__(master, bg=app_ref.COLOR_BG)
        self.app = app_ref

        self.image_paths: list[str] = []
        self.current_index: int = 0
        self.tk_photo: ImageTk.PhotoImage | None = None
        self._last_width: int = 0
        self._last_height: int = 0
        self._resize_timer: str | None = None
        self.fixed_display_w: int = 0
        self.fixed_display_h: int = 0

        # Configuration de la grille principale de GalleryScreen
        self.rowconfigure(0, weight=1) # photo_label prend tout l'espace vertical disponible
        self.rowconfigure(1, weight=0) # info_label
        self.rowconfigure(2, weight=0) # nav_frame
        self.columnconfigure(0, weight=1)

        # --- Widgets de la galerie ---
        self.photo_label = tk.Label(self, bg=self.app.COLOR_BG)
        self.photo_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.bind("<Configure>", self.on_resize)

        self.info_label = tk.Label(self, text="", font=("Arial", 16), bg=self.app.COLOR_BG, fg=self.app.COLOR_TEXT)
        self.info_label.grid(row=1, column=0, sticky="ew", pady=5)

        self.nav_frame = tk.Frame(self, bg=self.app.COLOR_BG)
        self.nav_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)

        self.create_widgets()
        self.after(100, self.load_photos) # Délai pour permettre à la fenêtre de se dessiner

    def create_widgets(self):
        """Crée les boutons de navigation et d'action de la galerie."""
        button_font = ("Arial", 18, "bold")
        button_padding = {"pady": 20, "padx": 25}
        icon_size = (40, 40)

        icon_back = self.app.load_icon("home.png", icon_size)
        back_button = tk.Button(self.nav_frame, text="Retour", image=icon_back, compound="left", command=self.close_gallery, font=button_font, bg=self.app.COLOR_GREY, fg="white", activebackground=self.app.ACTIVE_GREY, relief="flat", **button_padding)
        back_button.image = icon_back # Garde une référence
        back_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.app.apply_hover_effect(back_button, self.app.HOVER_GREY, self.app.COLOR_GREY)

        icon_prev = self.app.load_icon("arrow-left.png", icon_size)
        prev_button = tk.Button(self.nav_frame, text="Précédent", image=icon_prev, compound="left", command=self.prev_photo, font=button_font, bg=self.app.COLOR_BG_LIGHT, fg="white", activebackground=self.app.COLOR_BG, relief="flat", **button_padding)
        prev_button.image = icon_prev # Garde une référence
        prev_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.app.apply_hover_effect(prev_button, self.app.HOVER_BG_LIGHT, self.app.COLOR_BG_LIGHT)

        if self.app.config.get('enable_printing', False):
            icon_print = self.app.load_icon("printer.png", icon_size)
            print_button = tk.Button(self.nav_frame, text="Imprimer", image=icon_print, compound="left", command=self.print_current_photo, font=button_font, bg=self.app.COLOR_PRIMARY, fg="white", activebackground=self.app.ACTIVE_PRIMARY, relief="flat", **button_padding)
            print_button.image = icon_print # Garde une référence
            print_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
            self.app.apply_hover_effect(print_button, self.app.HOVER_PRIMARY, self.app.COLOR_PRIMARY)

        icon_next = self.app.load_icon("arrow-right.png", icon_size)
        next_button = tk.Button(self.nav_frame, text="Suivant", image=icon_next, compound="right", command=self.next_photo, font=button_font, bg=self.app.COLOR_BG_LIGHT, fg="white", activebackground=self.app.COLOR_BG, relief="flat", **button_padding)
        next_button.image = icon_next # Garde une référence
        next_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.app.apply_hover_effect(next_button, self.app.HOVER_BG_LIGHT, self.app.COLOR_BG_LIGHT)

    def load_photos(self):
        """Charge la liste des photos depuis le dossier 'photos'."""
        self.image_paths = []
        base_photo_dir = 'photos'
        try:
            if not os.path.exists(base_photo_dir):
                self.info_label.config(text="Aucune photo trouvée.")
                self.show_current_photo()
                return

            for root, _, files in os.walk(base_photo_dir):
                for file in files:
                    if file.lower().endswith('.jpg'):
                        self.image_paths.append(os.path.join(root, file))

            self.image_paths.sort(key=lambda f: os.path.getmtime(f), reverse=True)

            self.current_index = 0
            self.show_current_photo()
        except Exception as e:
            self.info_label.config(text=f"Erreur lors du chargement de la galerie: {e}")
            self.show_current_photo()

    def show_current_photo(self):
        """Affiche l'image à l'index actuel."""
        if not self.image_paths:
            self.info_label.config(text="La galerie est vide.")
            self.photo_label.config(image=None)
            self.tk_photo = None
            return

        container_w = self.winfo_width()
        container_h = self.winfo_height()
        if container_w <= 1 or container_h <= 1:
            self.after(20, self.show_current_photo)
            return

        if self.fixed_display_w <= 0 or self.fixed_display_h <= 0:
            info_h = self.info_label.winfo_height() or 40
            nav_h = self.nav_frame.winfo_height() or 80
            self.fixed_display_w = max(100, container_w - 40)
            self.fixed_display_h = max(100, container_h - info_h - nav_h - 40)

        self.info_label.config(text=f"Photo {self.current_index + 1} sur {len(self.image_paths)}")
        
        path = self.image_paths[self.current_index]
        try:
            img = Image.open(path)
            img.thumbnail((self.fixed_display_w, self.fixed_display_h), Image.LANCZOS)
            self.tk_photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.tk_photo)
        except Exception as e:
            self.info_label.config(text=f"Erreur au chargement de l'image: {e}")
            self.photo_label.config(image=None)
            self.tk_photo = None

    def on_resize(self, event):
        """Gère le redimensionnement de l'image lors du changement de taille du widget."""
        if event.width > 1 and event.height > 1:
            if abs(event.width - self._last_width) > 15 or abs(event.height - self._last_height) > 15:
                self._last_width = event.width
                self._last_height = event.height
                info_h = self.info_label.winfo_height() or 40
                nav_h = self.nav_frame.winfo_height() or 80
                self.fixed_display_w = max(100, event.width - 40)
                self.fixed_display_h = max(100, event.height - info_h - nav_h - 40)

                if self.image_paths:
                    if self._resize_timer is not None:
                        try:
                            self.after_cancel(self._resize_timer)
                        except Exception:
                            pass
                    self._resize_timer = self.after(150, self.show_current_photo)

    def next_photo(self):
        """Passe à la photo suivante."""
        if not self.image_paths: return
        self.current_index = (self.current_index + 1) % len(self.image_paths)
        self.show_current_photo()

    def prev_photo(self):
        """Passe à la photo précédente."""
        if not self.image_paths: return
        self.current_index = (self.current_index - 1 + len(self.image_paths)) % len(self.image_paths)
        self.show_current_photo()

    def print_current_photo(self):
        """Prépare et imprime la photo actuelle."""
        if not self.image_paths: return
        current_path = self.image_paths[self.current_index]
        self.app.current_photo_path = current_path
        self.app.processed_photo = Image.open(current_path)
        self.app.print_photo()

    def close_gallery(self):
        """Ferme la galerie et retourne à l'écran d'accueil."""
        self.destroy()
        # On ré-affiche le label principal avant de retourner à l'accueil
        self.app.photo_label.pack(fill=tk.BOTH, expand=True)
        self.app.show_home_screen()
