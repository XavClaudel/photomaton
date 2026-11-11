from __future__ import annotations

import os
import time
import threading
import qrcode
import tkinter as tk
from tkinter import messagebox, PhotoImage
from PIL import Image, ImageTk, ImageOps, ImageDraw, ImageFilter
from typing import Any

# Importation des modules personnalisés
import camera_manager
import image_processor
import printer_manager
import usb_manager
import web_server_manager
import config_manager
import gpio_manager
from ui_config_screen import ConfigScreen
from ui_gallery_screen import GalleryScreen

class PhotomatonApp:
    """
    Classe principale de l'application Photomaton.
    Gère l'interface graphique, le flux de l'application et l'orchestration des différents modules.
    """
    def __init__(self, master: tk.Tk) -> None:
        # --- Modern UI Color Palette ---
        self.COLOR_BG = "#2C3E50"
        self.COLOR_BG_LIGHT = "#34495E"
        self.COLOR_TEXT = "#ECF0F1"
        self.COLOR_PRIMARY = "#3498DB"
        self.COLOR_SUCCESS = "#2ECC71"
        self.COLOR_WARNING = "#F39C12"
        self.COLOR_DANGER = "#E74C3C"
        self.COLOR_GREY = "#7F8C8D"
        self.COLOR_PURPLE = "#9B59B6"
        self.COLOR_GREEN_ALT = "#16A085"

        # --- Active/Pressed Colors (darker) ---
        self.ACTIVE_PRIMARY = "#2980B9"
        self.ACTIVE_SUCCESS = "#27AE60"
        self.ACTIVE_WARNING = "#D35400"
        self.ACTIVE_DANGER = "#C0392B"
        self.ACTIVE_GREY = "#6c7a7b"
        self.ACTIVE_PURPLE = "#8E44AD"
        self.ACTIVE_GREEN_ALT = "#117A65"

        # --- Hover Colors (lighter) ---
        self.HOVER_PRIMARY = "#5DADE2"
        self.HOVER_SUCCESS = "#58D68D"
        self.HOVER_WARNING = "#F5B041"
        self.HOVER_DANGER = "#EC7063"
        self.HOVER_GREY = "#99A3A4"
        self.HOVER_PURPLE = "#AF7AC5"
        self.HOVER_GREEN_ALT = "#48C9B0"
        self.HOVER_BG_LIGHT = "#415B76"

        self.master: tk.Tk = master
        master.title("Photomaton")
        self.is_fullscreen = True
        master.geometry("1024x768")
        master.minsize(800, 600)
        master.attributes('-fullscreen', self.is_fullscreen)  # Lancement en plein écran
        master.bind("<Escape>", self.toggle_fullscreen)
        master.bind("<F11>", self.toggle_fullscreen)
        master.configure(bg=self.COLOR_BG)

        self.config: dict[str, Any] = config_manager.load_config()

        self.current_photo_path: str | None = None
        self.tk_photo: ImageTk.PhotoImage | None = None
        self.tk_processed_photo: ImageTk.PhotoImage | None = None
        self.is_camera_active: bool = True
        self.processed_photo: Image.Image | None = None # Image en cours de traitement (avec effets)
        self.original_photo: Image.Image | None = None # Image originale, sans effets
        self.photo_strip_paths: list[str] = [] # Chemins des photos pour le mode montage
        self.print_count: int = 0

        if not os.path.exists('photos'):
            os.makedirs('photos')

        # Cadre principal
        self.main_frame: tk.Frame = tk.Frame(master, bg=self.COLOR_BG)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Notification Widget ---
        # Ce label sera utilisé pour afficher des notifications non-bloquantes.
        self.notification_label = tk.Label(self.main_frame, text="", font=("Arial", 18, "bold"), fg="white", pady=15)
        self.notification_job: str | None = None

        self.photo_label: tk.Label = tk.Label(self.main_frame, bg=self.COLOR_BG)
        self.photo_label.pack(fill=tk.BOTH, expand=True)

        self.button_frame: tk.Frame = tk.Frame(self.main_frame, bg="black")
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        close_button: tk.Button = tk.Button(master, text="X", command=master.destroy, 
                                 font=("Arial", 16, "bold"), bg="red", fg="white", 
                                 activebackground="#9B0000", relief="flat")
        close_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

        # Déclaration des widgets pour l'autocomplétion et l'analyse statique
        self.take_photo_button: tk.Button
        self.montage_button: tk.Button
        self.montage_menu_window: tk.Toplevel | None = None
        self.gallery_button: tk.Button
        self.retake_button: tk.Button
        self.print_button: tk.Button
        self.effects_toggle_button: tk.Button
        self.bw_button: tk.Button
        self.sepia_button: tk.Button
        self.vignette_button: tk.Button
        self.sharpen_button: tk.Button
        self.blur_button: tk.Button
        self.contour_button: tk.Button
        self.overlay_button: tk.Button
        self.reset_button: tk.Button
        self.countdown_label: tk.Label
        self.qr_code_label: tk.Label
        self.side_effects_panel: tk.Frame
        self.config_frame: tk.Frame
        self.tk_qr_code: ImageTk.PhotoImage
        self.icon_cache: dict[str, ImageTk.PhotoImage] = {}

        self.show_config_screen() # Affiche l'écran de configuration au lieu de l'accueil

    def toggle_fullscreen(self, event=None) -> None:
        """Bascule entre le mode plein écran et le mode fenêtré."""
        self.is_fullscreen = not self.is_fullscreen
        self.master.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def gpio_trigger_photo(self, channel: int) -> None:
        """
        Fonction de callback appelée par l'appui sur le bouton GPIO.
        Elle doit être exécutée dans le thread principal de Tkinter pour éviter les conflits.
        """
        if self.is_camera_active:
            print(f"Déclenchement par GPIO (broche {channel}) détecté (Nouvelle photo) !")
            self.master.after(0, self.countdown_and_capture)
        elif self.retake_button.winfo_ismapped():
            print(f"Déclenchement par GPIO (broche {channel}) détecté (Reprendre la photo) !")
            self.master.after(0, self.show_home_screen)

    def create_widgets(self) -> None:
        """Crée tous les widgets (boutons, labels) de l'interface."""
        # Style commun pour les boutons tactiles
        button_font = ("Arial", 22, "bold")
        button_padding = {"pady": 20, "padx": 30}
        icon_size = (48, 48) # Taille commune pour les icônes des boutons principaux

        # --- Écran d'accueil ---
        icon_camera = self.load_icon("camera.png", icon_size)
        self.take_photo_button = tk.Button(self.button_frame, text="Prendre une photo", image=icon_camera, compound="left", command=self.countdown_and_capture, font=button_font, 
                                           bg=self.COLOR_SUCCESS, fg="white", activebackground=self.ACTIVE_SUCCESS, relief="flat", **button_padding)
        self.take_photo_button.image = icon_camera # Garde une référence
        self.apply_hover_effect(self.take_photo_button, self.HOVER_SUCCESS, self.COLOR_SUCCESS)

        icon_montage = self.load_icon("grid.png", icon_size)
        self.montage_button = tk.Button(self.button_frame, text="Mode Montage", image=icon_montage, compound="left", command=self.show_montage_menu, font=button_font, 
                                        bg=self.COLOR_PRIMARY, fg="white", activebackground=self.ACTIVE_PRIMARY, relief="flat", **button_padding)
        self.montage_button.image = icon_montage # Garde une référence
        self.apply_hover_effect(self.montage_button, self.HOVER_PRIMARY, self.COLOR_PRIMARY)
        
        icon_gallery = self.load_icon("images.png", icon_size)
        self.gallery_button = tk.Button(self.button_frame, text="Galerie", image=icon_gallery, compound="left", command=self.show_gallery_screen, font=button_font, 
                                        bg=self.COLOR_PURPLE, fg="white", activebackground=self.ACTIVE_PURPLE, relief="flat", **button_padding)
        self.gallery_button.image = icon_gallery # Garde une référence
        self.apply_hover_effect(self.gallery_button, self.HOVER_PURPLE, self.COLOR_PURPLE)

        # --- Écran de prévisualisation ---
        icon_retake = self.load_icon("undo.png", icon_size)
        self.retake_button = tk.Button(self.button_frame, text="Reprendre", image=icon_retake, compound="left", command=self.show_home_screen, font=button_font, 
                                       bg=self.COLOR_WARNING, fg="white", activebackground=self.ACTIVE_WARNING, relief="flat", **button_padding)
        self.retake_button.image = icon_retake # Garde une référence
        self.apply_hover_effect(self.retake_button, self.HOVER_WARNING, self.COLOR_WARNING)

        icon_print = self.load_icon("printer.png", icon_size)
        self.print_button = tk.Button(self.button_frame, text="Imprimer", image=icon_print, compound="left", command=self.print_photo, font=button_font, 
                                      bg=self.COLOR_PRIMARY, fg="white", activebackground=self.ACTIVE_PRIMARY, relief="flat", **button_padding)
        self.print_button.image = icon_print # Garde une référence
        self.apply_hover_effect(self.print_button, self.HOVER_PRIMARY, self.COLOR_PRIMARY)

        icon_effects = self.load_icon("stars.png", icon_size)
        self.effects_toggle_button = tk.Button(self.button_frame, text="Effets", image=icon_effects, compound="left", command=self.toggle_effects_panel, font=button_font, 
                                               bg=self.COLOR_GREEN_ALT, fg="white", activebackground=self.ACTIVE_GREEN_ALT, relief="flat", **button_padding)
        self.effects_toggle_button.image = icon_effects # Garde une référence
        self.apply_hover_effect(self.effects_toggle_button, self.HOVER_GREEN_ALT, self.COLOR_GREEN_ALT)
        
        # --- Panneau d'effets latéral (initialement caché) ---
        self.side_effects_panel = tk.Frame(self.main_frame, bg=self.COLOR_BG, bd=2, relief="raised")
        effect_font = ("Arial", 18)
        effect_icon_size = (32, 32)
        side_effect_padding = {"pady": 15, "padx": 25}
        side_effect_button_kwargs = {
            "font": effect_font, "relief": "flat", "bg": self.COLOR_BG_LIGHT, "fg": self.COLOR_TEXT, "compound": "left", "anchor": "w",
            "activebackground": self.COLOR_BG, "activeforeground": self.COLOR_TEXT, **side_effect_padding
        }

        icon_bw = self.load_icon("contrast.png", effect_icon_size)
        self.bw_button = tk.Button(self.side_effects_panel, text=" Noir & Blanc", image=icon_bw, command=self.apply_bw_filter, **side_effect_button_kwargs)
        self.bw_button.image = icon_bw # Garde une référence
        self.apply_hover_effect(self.bw_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)
        icon_sepia = self.load_icon("filter.png", effect_icon_size)
        self.sepia_button = tk.Button(self.side_effects_panel, text=" Sépia", image=icon_sepia, command=self.apply_sepia_filter, **side_effect_button_kwargs)
        self.sepia_button.image = icon_sepia # Garde une référence
        self.apply_hover_effect(self.sepia_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)
        icon_vignette = self.load_icon("focus.png", effect_icon_size)
        self.vignette_button = tk.Button(self.side_effects_panel, text=" Vignette", image=icon_vignette, command=self.apply_vignette_effect, **side_effect_button_kwargs)
        self.vignette_button.image = icon_vignette # Garde une référence
        self.apply_hover_effect(self.vignette_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)
        icon_sharpen = self.load_icon("triangle.png", effect_icon_size)
        self.sharpen_button = tk.Button(self.side_effects_panel, text=" Netteté", image=icon_sharpen, command=self.apply_sharpen_effect, **side_effect_button_kwargs)
        self.sharpen_button.image = icon_sharpen # Garde une référence
        self.apply_hover_effect(self.sharpen_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)
        icon_blur = self.load_icon("droplet.png", effect_icon_size)
        self.blur_button = tk.Button(self.side_effects_panel, text=" Flou", image=icon_blur, command=self.apply_blur_effect, **side_effect_button_kwargs)
        self.blur_button.image = icon_blur # Garde une référence
        self.apply_hover_effect(self.blur_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)
        icon_contour = self.load_icon("edit.png", effect_icon_size)
        self.contour_button = tk.Button(self.side_effects_panel, text=" Contour", image=icon_contour, command=self.apply_contour_effect, **side_effect_button_kwargs)
        self.contour_button.image = icon_contour # Garde une référence
        self.apply_hover_effect(self.contour_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)
        icon_overlay = self.load_icon("border-all.png", effect_icon_size)
        self.overlay_button = tk.Button(self.side_effects_panel, text=" Cadre", image=icon_overlay, command=self.apply_overlay, **side_effect_button_kwargs)
        self.overlay_button.image = icon_overlay # Garde une référence
        self.apply_hover_effect(self.overlay_button, self.HOVER_BG_LIGHT, self.COLOR_BG_LIGHT)

        icon_reset = self.load_icon("undo.png", effect_icon_size)
        self.reset_button = tk.Button(self.side_effects_panel, text=" Reset", image=icon_reset, compound="left", anchor="w", command=self.reset_effects, font=effect_font, bg=self.COLOR_DANGER, fg="white", activebackground=self.ACTIVE_DANGER, relief="flat", **side_effect_padding)
        self.reset_button.image = icon_reset # Garde une référence
        self.apply_hover_effect(self.reset_button, self.HOVER_DANGER, self.COLOR_DANGER)

        # Empile les boutons d'effets dans le panneau latéral
        self.bw_button.pack(fill='x', expand=True)
        self.sepia_button.pack(fill='x', expand=True)
        self.vignette_button.pack(fill='x', expand=True)
        self.sharpen_button.pack(fill='x', expand=True)
        self.blur_button.pack(fill='x', expand=True)
        self.contour_button.pack(fill='x', expand=True)
        self.overlay_button.pack(fill='x', expand=True)
        self.reset_button.pack(fill='x', expand=True, pady=(20, 0))
        # --- Label pour le décompte ---
        self.countdown_label = tk.Label(self.photo_label, text="", font=("Arial", 120, "bold"), bg=self.COLOR_BG, fg="white")
        self.qr_code_label = tk.Label(self.main_frame, bg=self.COLOR_BG)

    def show_config_screen(self) -> None:
        """Affiche l'écran de configuration."""
        self.clear_buttons()
        self.config_frame = ConfigScreen(self.main_frame, self, self.start_from_config)
        self.config_frame.pack(fill=tk.BOTH, expand=True)

    def start_from_config(self, updated_config: dict[str, Any]) -> None:
        """Callback appelé par l'écran de configuration pour démarrer l'application."""
        self.config = updated_config
        config_manager.save_config(self.config)

        if self.config.get('enable_web_server', False):
            threading.Thread(target=web_server_manager.start_server, args=('photos',), daemon=True).start()

        if gpio_manager.IS_RASPBERRY_PI:
            button_pin = self.config.get('gpio_button_pin', 2)
            gpio_manager.setup_button(button_pin, self.gpio_trigger_photo)

        # On détruit l'écran de configuration pour laisser place à l'interface principale
        self.config_frame.destroy()
        # Le photo_label créé dans __init__ est maintenant visible.
        self.create_widgets()
        self.show_home_screen()

    def clear_buttons(self) -> None:
        """Nettoie la zone des boutons."""
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()

    def show_home_screen(self) -> None:
        """Affiche l'écran d'accueil avec le flux de la caméra."""
        self.clear_buttons()
        self.qr_code_label.place_forget()
        self.side_effects_panel.place_forget()
        self.is_camera_active = True
        self.take_photo_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=5)
        self.montage_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.gallery_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        if camera_manager.IS_WEBCAM_AVAILABLE:
            self.update_camera_feed()
        else:
            self.show_no_webcam_message()

    def get_daily_photo_dir(self) -> str:
        """Retourne le chemin du dossier de photos pour la date actuelle et le crée si nécessaire."""
        today_str = time.strftime("%Y-%m-%d")
        daily_dir = os.path.join('photos', today_str)
        if not os.path.exists(daily_dir):
            os.makedirs(daily_dir)
        return daily_dir

    def create_montage_menu_window(self):
        """Crée et configure la fenêtre (Toplevel) personnalisée pour le menu de montage."""
        if self.montage_menu_window and self.montage_menu_window.winfo_exists():
            self.montage_menu_window.destroy()

        self.montage_menu_window = tk.Toplevel(self.master)
        self.montage_menu_window.geometry("+9999+9999") # On la crée hors de l'écran pour éviter le flash
        self.montage_menu_window.overrideredirect(True)
        self.montage_menu_window.configure(bg=self.COLOR_BG_LIGHT, relief="solid", bd=1)
        self.montage_menu_window.transient(self.master)

        # --- Fonctions de rappel pour le menu ---
        def close_menu(event=None):
            """Fonction utilitaire pour fermer proprement le menu."""
            if self.montage_menu_window and self.montage_menu_window.winfo_exists():
                self.montage_menu_window.destroy()
                self.montage_menu_window = None

        def on_choice(format_choice: str):
            """Gère le choix d'un format et lance le montage."""
            close_menu()
            self.start_photo_strip(format_choice)

        menu_icon_size = (32, 32)
        btn_font = ("Arial", 16)
        btn_kwargs = {
            "font": btn_font, "bg": self.COLOR_BG_LIGHT, "fg": self.COLOR_TEXT, "activebackground": self.ACTIVE_PRIMARY, "compound": "left",
            "activeforeground": "white",
            "relief": "flat", "pady": 10, "padx": 20, "anchor": "w"
        }

        icon_grid = self.load_icon("grid.png", menu_icon_size)
        grid_btn = tk.Button(self.montage_menu_window, text=" Grille 2x2", image=icon_grid, command=lambda: on_choice('Grille 2x2'), **btn_kwargs)
        grid_btn.image = icon_grid # Garde une référence
        grid_btn.pack(fill="x", expand=True)
        self.apply_hover_effect(grid_btn, self.COLOR_PRIMARY, self.COLOR_BG_LIGHT)
        
        icon_strip = self.load_icon("filmstrip.png", menu_icon_size)
        strip_btn = tk.Button(self.montage_menu_window, text=" Bande 1x4", image=icon_strip, command=lambda: on_choice('Bande 1x4'), **btn_kwargs)
        strip_btn.image = icon_strip # Garde une référence
        strip_btn.pack(fill="x", expand=True)
        self.apply_hover_effect(strip_btn, self.COLOR_PRIMARY, self.COLOR_BG_LIGHT)

        # --- Liaisons d'événements pour fermer le menu ---
        self.montage_menu_window.bind("<FocusOut>", close_menu) # Se ferme si on clique ailleurs
        self.montage_menu_window.bind("<Escape>", close_menu)   # Se ferme avec la touche Echap

    def animate_montage_menu(self, current_y: int, target_y: int, x: int):
        """Anime le déplacement vertical du menu de montage."""
        if not self.montage_menu_window or not self.montage_menu_window.winfo_exists():
            return
        step = 15
        new_y = current_y - step
        if new_y <= target_y:
            self.montage_menu_window.geometry(f"+{x}+{target_y}")
        else:
            self.montage_menu_window.geometry(f"+{x}+{new_y}")
            self.master.after(10, lambda: self.animate_montage_menu(new_y, target_y, x))

    def show_gallery_screen(self):
        """Affiche l'écran de la galerie de photos."""
        # On ne détruit pas tout, on cache juste les éléments de l'accueil
        self.clear_buttons()
        self.photo_label.pack_forget()
        self.is_camera_active = False
        gallery = GalleryScreen(self.main_frame, self) # La galerie est maintenant un enfant de main_frame
        gallery.pack(fill=tk.BOTH, expand=True)

    def apply_hover_effect(self, button: tk.Button, hover_color: str, original_color: str):
        """Applique un effet de survol à un bouton."""
        button.bind("<Enter>", lambda e: button.config(bg=hover_color))
        button.bind("<Leave>", lambda e: button.config(bg=original_color))

    def load_icon(self, name: str, size: tuple[int, int]) -> ImageTk.PhotoImage | None:
        """Charge une icône PNG depuis le dossier assets, la redimensionne et la met en cache."""
        cache_key = f"{name}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        path = os.path.join("assets", name)
        if not os.path.exists(path):
            print(f"AVERTISSEMENT: Icône introuvable. Le fichier '{name}' n'a pas été trouvé dans le dossier '{os.path.abspath('assets')}'.")
            return None

        try:
            img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img, master=self.master)
            self.icon_cache[cache_key] = tk_img
            return tk_img
        except Exception as e:
            print(f"Erreur lors du chargement de l'icône '{name}': {e}")
            return None


    def update_camera_feed(self) -> None:
        """Met à jour l'image de la caméra en continu."""
        if not self.is_camera_active or not camera_manager.IS_WEBCAM_AVAILABLE:
            return

        frame = camera_manager.get_frame()
        if frame is not None:
            display_h = self.photo_label.winfo_height()
            display_w = self.photo_label.winfo_width()
            
            # Si le widget n'est pas encore dessiné, sa taille est 1. On attend un peu.
            if display_w <= 1 or display_h <= 1:
                self.master.after(20, self.update_camera_feed)
                return

            h, w, _ = frame.shape
            scale = min(display_w / w, display_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
            # La vérification ci-dessus garantit que new_w et new_h ne seront pas nuls.
            
            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.LANCZOS)

            self.tk_photo = ImageTk.PhotoImage(image=img)
            self.photo_label.config(image=self.tk_photo, text="")
        
        self.master.after(20, self.update_camera_feed)

    def show_no_webcam_message(self):
        """Affiche un message statique si aucune webcam n'est disponible."""
        self.photo_label.config(image=None, text="Pas de retour vidéo.\nL'appareil photo est prêt.", 
                                font=("Arial", 30, "bold"), 
                                bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                                compound="center")
        self.tk_photo = None
        
        icon = self.load_icon("camera.png", (200, 200))
        if icon:
            self.photo_label.config(image=icon)
            self.tk_photo = icon # Garder une référence

    def countdown_and_capture(self) -> None:
        """Gère le décompte avant de prendre la photo."""
        self.is_camera_active = False
        self.clear_buttons()
        self.capture_single_photo()

    def do_countdown(self, message: str = "") -> None:
        """Effectue un décompte visuel."""
        # Efface l'arrière-plan pour ne pas voir la dernière image de la caméra pendant le décompte
        self.photo_label.config(image=None, text="")
        self.tk_photo = None # Libère la référence à l'ancienne image

        # Affiche le label de décompte au centre de la zone photo
        self.countdown_label.place(in_=self.photo_label, anchor="center", relx=.5, rely=.5)

        if message:
            self.countdown_label.config(text=message, font=("Arial", 60, "bold"))
            self.master.update()
            time.sleep(2)

        self.countdown_label.config(font=("Arial", 120, "bold"))
        for i in range(self.config.get('countdown_seconds', 5), 0, -1):
            self.countdown_label.config(text=str(i))
            self.master.update()
            time.sleep(1)
        
        self.countdown_label.config(text="")
        self.master.update()
        time.sleep(0.2) # Petite pause pour simuler un flash
        self.countdown_label.place_forget()

    def capture_single_photo(self) -> None:
        """Capture une seule photo."""
        self.do_countdown()
        self.capture_photo()

    def show_montage_menu(self) -> None:
        """Affiche un menu personnalisé avec une animation pour choisir le format du montage."""
        # Si la fenêtre existe déjà, on la détruit et on s'arrête là (comportement de bascule).
        if self.montage_menu_window and self.montage_menu_window.winfo_exists():
            self.montage_menu_window.destroy()
            self.montage_menu_window = None
            return

        self.create_montage_menu_window()
        self.montage_menu_window.update_idletasks()
        
        menu_width = self.montage_menu_window.winfo_reqwidth()
        menu_height = self.montage_menu_window.winfo_reqheight()

        btn_x = self.montage_button.winfo_rootx()
        btn_y = self.montage_button.winfo_rooty()
        btn_width = self.montage_button.winfo_width()

        popup_x = btn_x + (btn_width - menu_width) // 2
        final_y = btn_y - menu_height - 5
        start_y = btn_y

        self.montage_menu_window.geometry(f"+{popup_x}+{start_y}")
        self.animate_montage_menu(start_y, final_y, popup_x)
        self.montage_menu_window.focus_set()

    def start_photo_strip(self, montage_format: str) -> None:
        """Capture une série de 4 photos pour le montage avec le format spécifié."""
        self.is_camera_active = False
        self.clear_buttons()

        if not montage_format:
            self.show_home_screen()
            return

        save_dir = self.get_daily_photo_dir()
        self.photo_strip_paths = []
        for i in range(4):
            self.do_countdown(f"Photo {i+1} sur 4")
            photo_path = camera_manager.take_picture(save_dir)
            if photo_path:
                self.photo_strip_paths.append(photo_path)
            else:
                self.show_notification(f"La photo {i+1} a échoué. Montage annulé.", 'error')
                self.show_home_screen()
                return
        
        # Crée le montage à partir des 4 photos capturées.
        self.current_photo_path = image_processor.create_photo_strip(
            self.photo_strip_paths, output_folder=save_dir, strip_format=montage_format
        )
        if self.current_photo_path:
            self.original_photo = Image.open(self.current_photo_path)
            self.process_and_display_photo()
        else:
            self.show_notification("La création du montage a échoué.", 'error')
            self.show_home_screen()

    def capture_photo(self) -> None:
        """Capture une photo, la sauvegarde automatiquement sur USB si activé, et l'affiche."""
        save_dir = self.get_daily_photo_dir()
        self.current_photo_path = camera_manager.take_picture(save_dir)
        if self.current_photo_path:
            if self.config.get('enable_usb_save', False):
                print("Option de sauvegarde USB activée, tentative de sauvegarde automatique...")
                # La sauvegarde est silencieuse pour ne pas interrompre l'utilisateur
                self.save_to_usb(show_success_message=False)
            self.original_photo = Image.open(self.current_photo_path)
            self.process_and_display_photo()
        else:
            self.show_notification("Impossible de prendre la photo. Veuillez réessayer.", 'error')
            self.show_home_screen()

    def process_and_display_photo(self) -> None:
        """Applique les modifications permanentes (marquage) et affiche l'aperçu."""
        if self.config.get('enable_text_marking', False) and self.config.get('marking_text', ''):
            print("Application du texte de marquage...")
            self.original_photo = image_processor.add_text_to_image(
                self.original_photo,
                self.config['marking_text'],
                position=self.config.get('marking_text_position'),
                color=self.config.get('marking_text_color'),
                font_name=self.config.get('marking_text_font'),
                font_size=self.config.get('marking_text_size')
            )
            # Écrase le fichier original sur le disque avec la version incluant le texte
            self.original_photo.convert("RGB").save(self.current_photo_path)
        self.show_preview_screen()

    def show_preview_screen(self) -> None:
        """Affiche l'écran de prévisualisation avec les options."""
        self.is_camera_active = False
        self.clear_buttons()
        self.print_count = 0
        self.side_effects_panel.place_forget()
        
        if self.original_photo is None:
            self.show_notification("Aucune photo à afficher.", 'error')
            return self.show_home_screen()
        self.processed_photo = self.original_photo.copy()

        self.display_image(self.processed_photo)

        self.retake_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=5)

        if self.config.get('enable_personalization', False):
            self.effects_toggle_button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

        if self.config.get('enable_printing', False):
            self.print_button.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0, 10), pady=5)

        if self.config.get('enable_web_server', False):
            self.show_qr_code()

    def display_image(self, img_object: Image.Image) -> None:
        """Affiche une image dans le label principal."""
        try:
            display_h = self.photo_label.winfo_height()
            display_w = self.photo_label.winfo_width()
            img = img_object.copy() # On travaille sur une copie pour ne pas altérer l'original
            img.thumbnail((display_w, display_h), Image.LANCZOS)

            self.tk_processed_photo = ImageTk.PhotoImage(img)
            self.photo_label.config(image=self.tk_processed_photo, text="")
        except Exception as e:
            self.show_notification(f"Impossible d'afficher l'image: {e}", 'error')
            self.show_home_screen()

    def toggle_effects_panel(self) -> None:
        """Affiche ou cache le panneau latéral des effets."""
        if self.side_effects_panel.winfo_viewable():
            self.side_effects_panel.place_forget()
        else:
            overlay_path = self.config.get('overlay_path', 'assets/overlay.png')
            if not os.path.exists(overlay_path):
                self.overlay_button.pack_forget()
            else:
                self.overlay_button.pack(fill='x', expand=True, before=self.reset_button)
            self.side_effects_panel.place(in_=self.photo_label, anchor='w', relx=0.0, rely=0.5, x=20)

    def _apply_effect(self, effect_function, error_message: str = "Impossible d'appliquer l'effet"):
        """Méthode générique pour appliquer un effet à l'image en cours de traitement."""
        if self.processed_photo:
            try:
                self.processed_photo = effect_function(self.processed_photo)
                self.display_image(self.processed_photo)
            except Exception as e:
                self.show_notification(f"{error_message} : {e}", 'error')

    def apply_bw_filter(self) -> None:
        """Applique un filtre noir et blanc."""
        self._apply_effect(lambda img: ImageOps.grayscale(img).convert("RGB"), "Filtre N&B échoué")

    def apply_sepia_filter(self) -> None:
        """Applique un filtre sépia."""
        def effect(img: Image.Image) -> Image.Image:
            grayscale = ImageOps.grayscale(img)
            return ImageOps.colorize(grayscale, black="#4A2E04", white="#F3EAD3")
        self._apply_effect(effect, "Filtre sépia échoué")

    def apply_overlay(self) -> None:
        """Applique une image de cadre/logo en superposition."""
        def effect(img: Image.Image) -> Image.Image:
            overlay_path = self.config.get('overlay_path', 'assets/overlay.png')
            processed_rgba = img.copy().convert("RGBA")
            overlay = Image.open(overlay_path).convert("RGBA")
            overlay = overlay.resize(processed_rgba.size, Image.LANCZOS)
            processed_rgba.paste(overlay, (0, 0), overlay)
            return processed_rgba
        self._apply_effect(effect, "Application du cadre échouée")

    def apply_vignette_effect(self) -> None:
        """Applique un effet de vignettage."""
        def effect(img: Image.Image) -> Image.Image:
            img_rgb = img.copy().convert("RGB")
            vignette_layer = Image.new('RGB', img_rgb.size, 'black')
            mask = Image.new('L', img_rgb.size, 0)
            draw = ImageDraw.Draw(mask)
            x0, y0 = img_rgb.width * 0.1, img_rgb.height * 0.1
            x1, y1 = img_rgb.width * 0.9, img_rgb.height * 0.9
            draw.ellipse((x0, y0, x1, y1), fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(min(img_rgb.size) / 5))
            return Image.composite(img_rgb, vignette_layer, mask)
        self._apply_effect(effect, "Effet vignette échoué")

    def apply_sharpen_effect(self) -> None:
        """Applique un filtre de netteté."""
        self._apply_effect(lambda img: img.filter(ImageFilter.SHARPEN), "Filtre netteté échoué")

    def apply_blur_effect(self) -> None:
        """Applique un filtre de flou gaussien."""
        self._apply_effect(lambda img: img.filter(ImageFilter.GaussianBlur(radius=2)), "Filtre flou échoué")

    def apply_contour_effect(self) -> None:
        """Applique un filtre de contour."""
        self._apply_effect(lambda img: img.filter(ImageFilter.CONTOUR), "Filtre contour échoué")

    def reset_effects(self) -> None:
        """Annule tous les effets et revient à la photo originale."""
        self.processed_photo = self.original_photo.copy()
        self.display_image(self.processed_photo)

    def print_photo(self) -> None:
        """Gère la logique d'impression."""
        # Sauvegarde la photo avec les effets actuels dans un fichier temporaire pour l'impression
        try:
            base, ext = os.path.splitext(self.current_photo_path)
            photo_to_print_path = f"{base}_print_{int(time.time())}{ext}"
            self.processed_photo.convert("RGB").save(photo_to_print_path)
            print(f"Préparation pour impression : {photo_to_print_path}")
        except Exception as e:
            self.show_notification(f"Impossible de préparer l'image pour l'impression: {e}", 'error')
            return

        max_prints = self.config.get('max_prints_per_photo', 1)
        if self.print_count >= max_prints:
            self.show_notification(f"Nombre maximum d'impressions atteint ({max_prints}).", 'info')
            return

        fit_method = self.config.get('print_fit_method', 'pad')
        photo_to_print = image_processor.prepare_for_print(
            photo_to_print_path,
            target_ratio=3.0/2.0,
            method=fit_method
        )

        printer_name = self.config.get('printer_name')
        printing_options = self.config.get('printing_options')
        success = printer_manager.print_image(photo_to_print, printer_name, printing_options)
        if success:
            self.print_count += 1
            self.show_notification(f"Impression lancée ! Restant : {max_prints - self.print_count}", 'success')
        else:
            self.show_notification("L'impression a échoué.", 'error')

    def save_to_usb(self, show_success_message: bool = True) -> None:
        """Sauvegarde la photo sur une clé USB. Peut être silencieux."""
        is_temp_file: bool = False
        photo_to_save_path: str
        if show_success_message:
            # Appel MANUEL depuis l'écran de prévisualisation : on sauvegarde l'image avec effets.
            try:
                base, ext = os.path.splitext(self.current_photo_path)
                photo_to_save_path = f"{base}_usb_{int(time.time())}{ext}"
                self.processed_photo.convert("RGB").save(photo_to_save_path)
                print(f"Préparation pour sauvegarde USB (avec effets) : {photo_to_save_path}")
                is_temp_file = True
            except Exception as e:
                self.show_notification(f"Impossible de préparer l'image pour la sauvegarde: {e}", 'error')
                return
        else:
            # Appel AUTOMATIQUE juste après la capture : on sauvegarde le fichier original.
            photo_to_save_path = self.current_photo_path
            print(f"Préparation pour sauvegarde USB (auto) : {photo_to_save_path}")

        usb_path = usb_manager.find_usb_drive()
        if not usb_path:
            if show_success_message: # On n'affiche la notification que si l'action est manuelle
                self.show_notification("Aucune clé USB n'a été trouvée.", 'warning')
            else:
                print("Sauvegarde automatique sur USB : clé non trouvée.")
            return

        try:
            usb_manager.save_photo_to_usb(photo_to_save_path, usb_path)
            if show_success_message:
                self.show_notification("Photo sauvegardée sur la clé USB.", 'success')
            if is_temp_file:
                os.remove(photo_to_save_path)
        except Exception as e:
            if show_success_message:
                self.show_notification(f"Impossible de sauvegarder sur la clé USB: {e}", 'error')
            else:
                print(f"Erreur lors de la sauvegarde automatique sur USB : {e}")

    def show_qr_code(self) -> None:
        """Génère et affiche le QR code pour le téléchargement."""
        try:
            forced_ip = self.config.get('web_server_ip')
            ip = forced_ip if forced_ip else web_server_manager.get_local_ip()

            # Si l'IP est 127.0.0.1, il n'y a pas de réseau externe, le QR code est inutile.
            if ip == '127.0.0.1':
                print("INFO: Aucune connexion réseau externe détectée. Le QR code ne sera pas affiché.")
                self.qr_code_label.place_forget()
                return

            # Construit une URL relative au dossier 'photos' qui est servi par le serveur web
            relative_path = os.path.relpath(self.current_photo_path, 'photos').replace(os.sep, '/')
            url = f"http://{ip}:8000/{relative_path}"
            
            qr_img = qrcode.make(url)
            qr_img = qr_img.resize((150, 150), Image.LANCZOS)
            
            self.tk_qr_code = ImageTk.PhotoImage(qr_img)
            self.qr_code_label.config(image=self.tk_qr_code)
            
            self.qr_code_label.place(in_=self.photo_label, anchor="se", relx=1.0, rely=1.0, x=-10, y=-10)

        except Exception as e:
            print(f"Erreur lors de la génération du QR code: {e}")

    def show_notification(self, message: str, msg_type: str = 'info', duration: int = 3000):
        """Affiche une notification non-bloquante en haut de l'écran."""
        if self.notification_job:
            self.master.after_cancel(self.notification_job)

        color_map = {
            'info': self.COLOR_PRIMARY,
            'success': self.COLOR_SUCCESS,
            'warning': self.COLOR_WARNING,
            'error': self.COLOR_DANGER
        }
        self.notification_label.config(text=message, bg=color_map.get(msg_type, self.COLOR_BG_LIGHT))
        
        # Place la notification en haut, centrée horizontalement
        self.notification_label.place(in_=self.main_frame, anchor='n', relx=0.5, rely=0.0, relwidth=1.0)
        self.notification_label.lift() # Assure que la notification est au-dessus des autres widgets
        
        self.notification_job = self.master.after(duration, self.hide_notification)

    def hide_notification(self):
        """Cache la notification."""
        if self.notification_label.winfo_ismapped():
            self.notification_label.place_forget()
        self.notification_job = None


if __name__ == "__main__":
    if not camera_manager.init_camera():
        messagebox.showerror("Erreur Caméra", "Aucune caméra (Webcam ou Reflex) n'a été détectée. L'application va se fermer.")
        exit()

    root: tk.Tk = tk.Tk()
    app: PhotomatonApp = PhotomatonApp(root)
    root.mainloop()

    camera_manager.release_camera()
    gpio_manager.cleanup()