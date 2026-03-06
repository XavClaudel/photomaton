import os, time, pygame, threading, subprocess, pyudev, qrcode
import RPi.GPIO as GPIO
import gphoto2 as gp
from http.server import BaseHTTPRequestHandler, HTTPServer

# -------------------------
# CONFIG PYGAME
# -------------------------
pygame.init()
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
pygame.display.set_caption("Photomaton")

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,200,0)
RED = (200,0,0)
GRAY = (180,180,180)
DARK_GRAY = (50,50,50)

font = pygame.font.SysFont(None, 50)
font_small = pygame.font.SysFont(None, 40)
font_large = pygame.font.SysFont(None, 74)

# -------------------------
# GPIO
# -------------------------
BUTTON_PIN = 2
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# -------------------------
# SERVER HTTP
# -------------------------
PORT = 8000
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

# -------------------------
# QR CODE
# -------------------------
def generate_qr_code(url,filename="qr_code.png"):
    qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black",back_color="white")
    img.save(filename)
    return filename

# -------------------------
# UI COMPONENTS
# -------------------------
class Toggle:
    def __init__(self, x, y, w=60, h=30, state=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.state = state
        self.circle_radius = h//2 - 2
        self.circle_pos = x + (w-15 if state else 15)
        self.target_pos = self.circle_pos
        self.speed = 5

    def draw(self, screen):
        if self.circle_pos < self.target_pos:
            self.circle_pos = min(self.circle_pos + self.speed, self.target_pos)
        elif self.circle_pos > self.target_pos:
            self.circle_pos = max(self.circle_pos - self.speed, self.target_pos)
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=self.rect.height//2)
        color = GREEN if self.state else RED
        pygame.draw.circle(screen, color, (int(self.circle_pos), self.rect.y+self.rect.height//2), self.circle_radius)

    def toggle(self):
        self.state = not self.state
        self.target_pos = self.rect.x + (self.rect.width-15 if self.state else 15)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.hover = False
        self.clicked = False

    def draw(self, screen, font):
        color = GRAY
        if self.hover: color = WHITE
        if self.clicked: color = GREEN
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

    def click(self):
        self.clicked = True

    def reset(self):
        self.clicked = False

# -------------------------
# USB MONITOR
# -------------------------
class USBMonitor:
    def __init__(self,dest_folder):
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem="block", device_type="partition")
        self.dest_folder = dest_folder
        os.makedirs(dest_folder,exist_ok=True)
    def check_usb(self):
        for device in iter(self.monitor.poll, None):
            if device.action=="add":
                device_node = device.device_node
                mount_point = f"/media/{os.getlogin()}/{device_node.split('/')[-1]}"
                os.makedirs(mount_point,exist_ok=True)
                subprocess.run(["pmount",device_node],check=False)
                print(f"USB mounted at {mount_point}")
                return mount_point
        return None

# -------------------------
# CAMERA
# -------------------------
class Camera:
    def __init__(self):
        self.context = gp.Context()
        self.cam = gp.Camera()
        self.cam.init(self.context)
    def capture_preview(self):
        camera_file = self.cam.capture_preview()
        data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        return data

# -------------------------
# PHOTOBOOTH
# -------------------------
class PhotoBooth:
    def __init__(self,screen,font,font_small,font_large):
        self.screen = screen
        self.font = font
        self.font_small = font_small
        self.font_large = font_large
        self.home = os.environ.get("HOME")
        self.tmp_folder = os.path.join(self.home,"tmp")
        os.makedirs(self.tmp_folder,exist_ok=True)
        start_server()
        self.usb_monitor = USBMonitor(dest_folder=os.path.join(self.home,"USB_PHOTOS"))
        self.camera = Camera()
        self.env_vars = ["IMPRIMER","CLES_USB","DOWNLOAD"]
        self.toggles_ui = [Toggle(400, 100+i*70) for i in range(len(self.env_vars))]
        self.validate_btn = Button(WIDTH-200, HEIGHT-100, 150, 60, "Valider")
        self.in_settings = True

    # -------------------------
    # FADE EFFECT
    # -------------------------
    def fade_in(self, surface, speed=5):
        overlay = pygame.Surface((WIDTH,HEIGHT))
        overlay.fill(BLACK)
        for alpha in range(255,0,-speed):
            self.screen.blit(surface,(0,0))
            overlay.set_alpha(alpha)
            self.screen.blit(overlay,(0,0))
            pygame.display.flip()
            pygame.time.delay(10)

    def fade_out(self, surface, speed=5):
        overlay = pygame.Surface((WIDTH,HEIGHT))
        overlay.fill(BLACK)
        for alpha in range(0,256,speed):
            self.screen.blit(surface,(0,0))
            overlay.set_alpha(alpha)
            self.screen.blit(overlay,(0,0))
            pygame.display.flip()
            pygame.time.delay(10)

    # -------------------------
    # DRAW UI
    # -------------------------
    def draw_settings(self):
        self.screen.fill(DARK_GRAY)
        for i,var in enumerate(self.env_vars):
            text = self.font_small.render(var,True,WHITE)
            self.screen.blit(text,(100,100+i*70))
            self.toggles_ui[i].draw(self.screen)
        self.validate_btn.draw(self.screen,self.font_small)
        pygame.display.flip()

    def handle_settings_click(self,pos):
        for t in self.toggles_ui:
            if t.is_clicked(pos):
                t.toggle()
        if self.validate_btn.is_hover(pos):
            self.validate_btn.click()
            self.in_settings = False
            print("Paramètres validés:",[t.state for t in self.toggles_ui])

    def draw_welcome(self):
        frame_data = self.camera.capture_preview()
        with open("/tmp/liveview.jpg","wb") as f:
            f.write(frame_data)
        img = pygame.image.load("/tmp/liveview.jpg").convert()
        img = pygame.transform.scale(img,(WIDTH,HEIGHT))
        self.fade_in(img)
        self.screen.blit(img,(0,0))
        self.draw_text_center("Appuyez sur le bouton pour prendre une photo",HEIGHT-50,self.font_small)
        pygame.display.flip()

    def draw_text_center(self,text,y,font,color=WHITE):
        txt = font.render(text,True,color)
        rect = txt.get_rect(center=(WIDTH//2,y))
        self.screen.blit(txt,rect)

    # -------------------------
    # COUNTDOWN
    # -------------------------
    def countdown_liveview(self,seconds=5):
        overlay = pygame.Surface((WIDTH,HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        for i in range(seconds,0,-1):
            frame_data = self.camera.capture_preview()
            with open("/tmp/liveview.jpg","wb") as f:
                f.write(frame_data)
            img = pygame.image.load("/tmp/liveview.jpg").convert()
            img = pygame.transform.scale(img,(WIDTH,HEIGHT))
            self.screen.blit(img,(0,0))
            self.screen.blit(overlay,(0,0))
            self.draw_text_center(str(i),HEIGHT//2,self.font_large)
            pygame.display.flip()
            time.sleep(1)

    # -------------------------
    # CAPTURE PHOTO
    # -------------------------
    def capture_photo(self):
        filename = os.path.join(self.tmp_folder,f"capt_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
        os.system(f"gphoto2 --capture-image-and-download --filename {filename}")
        if self.toggles_ui[1].state: # USB
            usb_path = self.usb_monitor.check_usb()
            if usb_path:
                os.system(f"cp {filename} {usb_path}")
        return filename

    # -------------------------
    # PRINT PHOTO
    # -------------------------
    def print_photo(self,path):
        if self.toggles_ui[0].state:
            os.system(f"lp {path}")

    # -------------------------
    # SHOW QR
    # -------------------------
    def show_qr(self,path):
        if self.toggles_ui[2].state:
            ip = subprocess.getoutput("hostname -I").split()[0]
            url = f"http://{ip}:{PORT}/{os.path.basename(path)}"
            qr_file = generate_qr_code(url)
            img = pygame.image.load(qr_file).convert()
            img = pygame.transform.scale(img,(300,300))
            self.screen.blit(img,(WIDTH-350,HEIGHT-350))
            self.draw_text_center("Scannez le QR code",HEIGHT-50,self.font_small)
            pygame.display.flip()
            time.sleep(5)
            os.remove(qr_file)

    # -------------------------
    # MAIN LOOP
    # -------------------------
    def run(self):
        clock = pygame.time.Clock()
        running=True
        while running:
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                elif event.type==pygame.MOUSEBUTTONDOWN:
                    if self.in_settings:
                        self.handle_settings_click(pos)
            if self.in_settings:
                self.draw_settings()
            else:
                self.draw_welcome()
                if GPIO.input(BUTTON_PIN)==GPIO.LOW:
                    self.countdown_liveview(5)
                    path = self.capture_photo()
                    self.fade_in(pygame.image.load(path).convert())
                    self.print_photo(path)
                    self.show_qr(path)
                    self.fade_out(pygame.image.load(path).convert())
            self.validate_btn.reset()
            clock.tick(30)
        pygame.quit()

if __name__=="__main__":
    photobooth = PhotoBooth(screen,font,font_small,font_large)
    photobooth.run()