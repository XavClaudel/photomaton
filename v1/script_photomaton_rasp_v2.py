import os
import time
import pygame
import threading
import subprocess
import json
import qrcode
import RPi.GPIO as GPIO
import gphoto2 as gp
from http.server import BaseHTTPRequestHandler, HTTPServer

# ----------------------------
# CONFIGURATION
# ----------------------------
WIDTH, HEIGHT = 800, 480
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,200,0)
RED = (200,0,0)
GRAY = (180,180,180)
DARK_GRAY = (50,50,50)

BUTTON_PIN = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

SETTINGS_FILE = "settings.json"
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
pygame.display.set_caption("Photomaton")

font = pygame.font.SysFont(None, 50)
font_small = pygame.font.SysFont(None, 40)
PORT = 8000  # port serveur QR code

# ----------------------------
# SETTINGS UTILITIES
# ----------------------------
def load_settings():
    default = {"IMPRIMER": True,"CLES_USB": False,"DOWNLOAD": False,"RETOUR_IMAGE": False}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        default.update(data)
    return default

def save_settings(settings):
    with open(SETTINGS_FILE,"w") as f:
        json.dump(settings,f,indent=4)

# ----------------------------
# UI ELEMENTS
# ----------------------------
class Toggle:
    WIDTH, HEIGHT = 90, 44
    def __init__(self,label,x,y,state):
        self.label = label
        self.state = state
        self.rect = pygame.Rect(x,y,self.WIDTH,self.HEIGHT)
        self.label_pos = (x-260,y+5)
    def draw(self,screen):
        text = font_small.render(self.label,True,WHITE)
        screen.blit(text,self.label_pos)
        color = GREEN if self.state else DARK_GRAY
        pygame.draw.rect(screen,color,self.rect,border_radius=30)
        cx = self.rect.right-22 if self.state else self.rect.left+22
        pygame.draw.circle(screen,WHITE,(cx,self.rect.centery),18)
    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state

class Button:
    def __init__(self,text,x,y,w,h):
        self.text=text
        self.rect=pygame.Rect(x,y,w,h)
    def draw(self,screen):
        pygame.draw.rect(screen,GRAY,self.rect,border_radius=12)
        txt = font.render(self.text,True,BLACK)
        screen.blit(txt,txt.get_rect(center=self.rect.center))
    def clicked(self,event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# ----------------------------
# ADMIN SECRET ZONE
# ----------------------------
class SecretAdminZone:
    def __init__(self):
        self.rect = pygame.Rect(0,0,120,120)
        self.start_press = None
        self.trigger_time = 3000
    def update(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.start_press = pygame.time.get_ticks()
        if event.type == pygame.MOUSEBUTTONUP:
            self.start_press = None
        if self.start_press:
            elapsed = pygame.time.get_ticks()-self.start_press
            if elapsed>self.trigger_time:
                self.start_press=None
                return True
        return False

# ----------------------------
# SERVEUR HTTP POUR QR CODE
# ----------------------------
class ImageHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.lstrip("/")
        if os.path.exists(path):
            with open(path,"rb") as f:
                self.send_response(200)
                self.send_header("Content-type","image/png")
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404,"File not found")

def start_server():
    server = HTTPServer(("", PORT), ImageHTTPRequestHandler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    print(f"Server running on port {PORT}")

# ----------------------------
# QR CODE
# ----------------------------
def generate_qr_code(url,filename="qr_code.png"):
    qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black",back_color="white")
    img.save(filename)
    return filename

# ----------------------------
# PHOTOMATON LOGIC
# ----------------------------
class PhotoBooth:
    def __init__(self):
        self.settings = load_settings()
        self.toggles = []
        self.validate_button = None
        self.create_ui()
        self.admin_zone = SecretAdminZone()
        self.screen_mode = "PHOTO"
        self.home = os.environ.get("HOME")
        self.tmp_folder = os.path.join(self.home,"tmp")
        os.makedirs(self.tmp_folder,exist_ok=True)
        start_server()
    
    def create_ui(self):
        start_y = 100
        spacing = 80
        self.toggles=[]
        for i,(k,v) in enumerate(self.settings.items()):
            self.toggles.append(Toggle(k,WIDTH-200,start_y+i*spacing,v))
        self.validate_button = Button("VALIDER",WIDTH-220,HEIGHT-100,200,70)
    
    # ----------------------------
    # ECRANS
    # ----------------------------
    def draw_settings_screen(self):
        screen.fill(BLACK)
        title = font.render("PARAMETRES",True,WHITE)
        screen.blit(title,(50,30))
        for t in self.toggles:
            t.draw(screen)
        self.validate_button.draw(screen)
        pygame.display.flip()
    
    def draw_photo_screen(self):
        screen.fill(BLACK)
        text = font.render("APPUIER SUR LE BOUTON POUR PRENDRE UNE PHOTO",True,WHITE)
        screen.blit(text,(50,HEIGHT//2))
        pygame.display.flip()
    
    # ----------------------------
    # COMPTE A REBOURS
    # ----------------------------
    def countdown(self, seconds=5):
        for i in range(seconds,0,-1):
            img_path = f"images/{i}.jpg"
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert()
                img = pygame.transform.scale(img,(WIDTH,HEIGHT))
                screen.blit(img,(0,0))
            else:
                screen.fill(BLACK)
                txt = font.render(str(i),True,WHITE)
                screen.blit(txt,txt.get_rect(center=(WIDTH//2,HEIGHT//2)))
            pygame.display.flip()
            time.sleep(1)
        img_path = "images/0.jpg"
        if os.path.exists(img_path):
            img = pygame.image.load(img_path).convert()
            img = pygame.transform.scale(img,(WIDTH,HEIGHT))
            screen.blit(img,(0,0))
        else:
            screen.fill(BLACK)
            txt = font.render("0",True,WHITE)
            screen.blit(txt,txt.get_rect(center=(WIDTH//2,HEIGHT//2)))
        pygame.display.flip()
        time.sleep(0.5)
    
    # ----------------------------
    # LIVEVIEW
    # ----------------------------
    def display_liveview(self):
        if not self.settings.get("RETOUR_IMAGE"):
            return
        try:
            context = gp.Context()
            camera = gp.Camera()
            camera.init(context)
            camera_file = camera.capture_preview()
            data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
            with open("/tmp/liveview.jpg","wb") as f:
                f.write(data)
            img = pygame.image.load("/tmp/liveview.jpg").convert()
            img = pygame.transform.scale(img,(WIDTH,HEIGHT))
            screen.blit(img,(0,0))
            pygame.display.flip()
        except Exception as e:
            print("Erreur LiveView :", e)
    
    # ----------------------------
    # CAPTURE PHOTO
    # ----------------------------
    def capture_photo(self):
        filename = os.path.join(self.tmp_folder,f"capt_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
        os.system(f"gphoto2 --capture-image-and-download --filename {filename}")
        print("Photo capturée :",filename)
        return filename
    
    def print_photo(self,path):
        if self.settings.get("IMPRIMER"):
            os.system(f"lp {path}")
            print("Photo imprimée")
    
    def export_usb(self,path):
        if self.settings.get("CLES_USB"):
            usb_path = "/media/usb/photos"
            os.makedirs(usb_path,exist_ok=True)
            os.system(f"cp {path} {usb_path}")
            print("Photo copiée sur clé USB")
    
    def download_qr(self,path):
        if self.settings.get("DOWNLOAD"):
            ip = subprocess.getoutput("hostname -I").split()[0]
            url = f"http://{ip}:{PORT}/{os.path.basename(path)}"
            qr_file = generate_qr_code(url)
            print(f"QR code généré : {qr_file}")
            return qr_file
    
    # ----------------------------
    # MAIN LOOP
    # ----------------------------
    def run(self):
        clock = pygame.time.Clock()
        running=True
        while running:
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                # ADMIN MODE
                if self.screen_mode=="PHOTO":
                    if self.admin_zone.update(event):
                        print("ADMIN MODE")
                        self.screen_mode="SETTINGS"
                # SETTINGS EVENTS
                if self.screen_mode=="SETTINGS":
                    for t in self.toggles:
                        t.handle_event(event)
                    if self.validate_button.clicked(event):
                        self.settings={t.label:t.state for t in self.toggles}
                        save_settings(self.settings)
                        print("Paramètres sauvegardés :",self.settings)
                        self.screen_mode="PHOTO"
                # CAPTURE PHOTO
                if self.screen_mode=="PHOTO" and (event.type==pygame.KEYDOWN and event.key==pygame.K_SPACE or GPIO.input(BUTTON_PIN)==GPIO.LOW):
                    self.display_liveview()
                    self.countdown(5)
                    path = self.capture_photo()
                    self.print_photo(path)
                    self.export_usb(path)
                    self.download_qr(path)
            
            if self.screen_mode=="PHOTO":
                self.draw_photo_screen()
            elif self.screen_mode=="SETTINGS":
                self.draw_settings_screen()
            clock.tick(60)
        pygame.quit()

# ----------------------------
# LANCEMENT
# ----------------------------
if __name__=="__main__":
    photobooth=PhotoBooth()
    photobooth.run()