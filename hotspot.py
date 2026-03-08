import subprocess

# def create_hotspot(ssid:str, password:str):
#     # Créer un hotspot Wi-Fi
#     try:
#         # Créer un nouveau point d'accès
#         subprocess.run([
#             'nmcli', 'device', 'wifi', 'hotspot',
#             'ifname', 'wlan0', 'con-name', ssid,
#             'ssid', ssid, 'band', 'bg', 'password', password
#         ], check=True)
#         print(f'Hotspot "{ssid}" créé avec succès.')
#     except subprocess.CalledProcessError as e:
#         print(f'Erreur lors de la création du hotspot : {e}')

import subprocess


def create_hotspot(ssid: str, password: str, interface: str | None = None):

    if len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caractères")

    if interface is None:
        interface = get_wifi_interface()

    if interface is None:
        print("Aucune interface Wi-Fi détectée")
        return False

    cmd = [
        "nmcli",
        "device",
        "wifi",
        "hotspot",
        "ifname",
        interface,
        "con-name",
        ssid,
        "ssid",
        ssid,
        "password",
        password
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Hotspot '{ssid}' créé sur {interface}")
        return True

    except subprocess.CalledProcessError as e:
        print("Erreur lors de la création du hotspot :", e)
        return False
    
def get_wifi_interface() -> str | None:
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE", "device"],
            capture_output=True,
            text=True,
            check=True
        )

        for line in result.stdout.splitlines():
            device, dtype, state = line.split(":")

            if dtype == "wifi" and state != "unavailable":
                return device

        return None

    except subprocess.CalledProcessError:
        return None