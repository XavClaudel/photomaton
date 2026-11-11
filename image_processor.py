from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
import time

def apply_black_and_white(image_path: str) -> str:
    """
    Applique un filtre noir et blanc à une image.
    Crée un nouveau fichier avec le suffixe '_bw' et retourne son chemin.
    """
    try:
        img = Image.open(image_path)
        bw_img = ImageOps.grayscale(img)
        base, ext = os.path.splitext(image_path)
        new_path = f"{base}_bw{ext}"
        bw_img.save(new_path)
        print(f"Filtre N&B appliqué : {new_path}")
        return new_path
    except Exception as e:
        print(f"Erreur lors de l'application du filtre N&B: {e}")
        return image_path

def apply_sepia_filter(image_path: str) -> str:
    """
    Applique un filtre sépia à une image pour un look vintage.
    Crée un nouveau fichier avec le suffixe '_sepia'.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        grayscale = ImageOps.grayscale(img)
        sepia_img = ImageOps.colorize(grayscale, black="#4A2E04", white="#F3EAD3")
        
        base, ext = os.path.splitext(image_path)
        new_path = f"{base}_sepia{ext}"
        sepia_img.save(new_path)
        print(f"Filtre Sépia appliqué : {new_path}")
        return new_path
    except Exception as e:
        print(f"Erreur lors de l'application du filtre sépia: {e}")
        return image_path

def add_overlay(image_path: str, overlay_path: str, position: tuple[int, int] = (0, 0)) -> str:
    """
    Superpose une image (un cadre, un logo...) sur la photo principale.
    L'image de superposition doit être en PNG avec transparence pour un meilleur effet.
    """
    try:
        background = Image.open(image_path).convert("RGBA")
        overlay = Image.open(overlay_path).convert("RGBA")

        overlay = overlay.resize(background.size, Image.LANCZOS)

        background.paste(overlay, position, overlay)
        base, ext = os.path.splitext(image_path)
        new_path = f"{base}_overlay{ext}"
        background.convert("RGB").save(new_path)
        print(f"Cadre ajouté : {new_path}")
        return new_path
    except Exception as e:
        print(f"Erreur lors de l'ajout du cadre: {e}")
        return image_path

def add_text_to_image(image: Image.Image, text: str, position: str = "En bas à droite", font_size: int = 50, color: str = "Blanc", font_name: str = "font.ttf") -> Image.Image:
    """Dessine un texte sur un objet Image de Pillow."""
    try:
        img_with_text = image.copy().convert("RGBA")
        draw = ImageDraw.Draw(img_with_text)

        try:
            font_path: str = os.path.join("assets", font_name)
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"ERREUR: La police '{font_path}' est introuvable.")
            print("Le texte ne sera pas ajouté. Veuillez vérifier que le fichier de police existe bien dans le dossier 'assets'.")
            return image

        COLOR_MAP = {
            "Blanc": (255, 255, 255),
            "Noir": (0, 0, 0),
            "Rouge": (220, 50, 50),
            "Jaune": (255, 220, 0)
        }
        final_color: tuple[int, int, int] = COLOR_MAP.get(color, (255, 255, 255))

        # font.getbbox() est la méthode la plus fiable pour obtenir les dimensions précises du texte
        left, top, right, bottom = font.getbbox(text)
        text_width = right - left
        text_height = bottom - top

        margin: int = int(font_size * 0.05)

        if "gauche" in position:
            x = margin
        else: # droite
            x = img_with_text.width - text_width - margin

        if "bas" in position:
            y = img_with_text.height - text_height - margin
        else: # haut
            y = margin

        # On dessine le texte en compensant la position 'top' de la police pour un alignement vertical correct
        draw.text((x, y - top), text, font=font, fill=final_color)

        return img_with_text
    except Exception as e:
        print(f"Erreur lors de l'ajout du texte : {e}")
        return image

def prepare_for_print(image_path: str, target_ratio: float = 3.0/2.0, method: str = 'pad') -> str:
    """
    Prépare une image pour l'impression en ajustant son ratio.
    - 'pad': ajoute des bandes noires pour atteindre le ratio cible sans déformer.
    - 'crop': rogne l'image au centre pour atteindre le ratio cible.
    """
    try:
        img = Image.open(image_path)
        original_width, original_height = img.size
        original_ratio = original_width / original_height
        processed_img: Image.Image
        suffix: str
        if abs(original_ratio - target_ratio) < 0.01:
            return image_path

        if method == 'pad':
            if original_ratio > target_ratio:
                new_width = original_width
                new_height = int(new_width / target_ratio)
                processed_img = Image.new("RGB", (new_width, new_height), "black")
                paste_y = (new_height - original_height) // 2
                processed_img.paste(img, (0, paste_y))
            else:
                new_height = original_height
                new_width = int(new_height * target_ratio)
                processed_img = Image.new("RGB", (new_width, new_height), "black")
                paste_x = (new_width - original_width) // 2
                processed_img.paste(img, (paste_x, 0))
            suffix = '_padded'
        elif method == 'crop':
            if original_ratio > target_ratio:
                new_width = int(original_height * target_ratio)
                left = (original_width - new_width) // 2
                processed_img = img.crop((left, 0, left + new_width, original_height))
            else:
                new_height = int(original_width / target_ratio)
                top = (original_height - new_height) // 2
                processed_img = img.crop((0, top, original_width, top + new_height))
            suffix = '_cropped'
        else:
            print(f"Méthode de préparation '{method}' invalide. L'image originale sera utilisée.")
            return image_path

        base, ext = os.path.splitext(image_path)
        new_path = f"{base}{suffix}{ext}"
        processed_img.save(new_path)
        print(f"Image préparée pour l'impression (méthode: {method}) : {new_path}")
        return new_path
    except Exception as e:
        print(f"Erreur lors de la préparation de l'image pour l'impression : {e}")
        return image_path

def create_photo_strip(image_paths: list[str], output_folder: str = 'photos', strip_format: str = 'Grille 2x2') -> str | None:
    """
    Crée un montage photo à partir d'une liste d'images.
    Prend en charge un format 2x2 ou une bande verticale 1x4.
    """
    if len(image_paths) != 4:
        print("Erreur: Le montage nécessite exactement 4 photos.")
        return None

    try:
        images = [Image.open(p) for p in image_paths]
        strip_img: Image.Image
        base_width, base_height = images[0].size
        images = [img.resize((base_width, base_height), Image.LANCZOS) for img in images]

        if strip_format == 'Grille 2x2':
            strip_img = Image.new('RGB', (base_width * 2, base_height * 2))
            strip_img.paste(images[0], (0, 0))
            strip_img.paste(images[1], (base_width, 0))
            strip_img.paste(images[2], (0, base_height))
            strip_img.paste(images[3], (base_width, base_height))
        else: # Par défaut, format "Bande 1x4"
            strip_img = Image.new('RGB', (base_width, base_height * 4))
            for i, img in enumerate(images):
                strip_img.paste(img, (0, base_height * i))

        timestamp: str = time.strftime("%Y%m%d-%H%M%S")
        new_path = os.path.join(output_folder, f"photomaton_strip_{timestamp}.jpg")
        strip_img.save(new_path)
        print(f"Montage photo créé : {new_path}")
        return new_path
    except Exception as e:
        print(f"Erreur lors de la création du montage: {e}")
        return None