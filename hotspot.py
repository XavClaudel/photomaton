import subprocess

def hotspot_exists(name: str) -> bool:
    result = subprocess.run(
        ["nmcli", "-t", "-f", "NAME", "connection", "show"],
        capture_output=True,
        text=True
    )

    return name in result.stdout.splitlines()

def create_hotspot(ssid: str, password: str, interface: str | None = None):

    if interface is None:
        interface = get_wifi_interface()

    if interface is None:
        print("Aucune interface Wi-Fi détectée")
        return False

    try:

        # vérifier si la connexion existe déjà
        if not hotspot_exists(ssid):

            print("Création du hotspot...")

            subprocess.run([
                "nmcli", "connection", "add",
                "type", "wifi",
                "ifname", interface,
                "mode", "ap",
                "con-name", ssid,
                "ssid", ssid
            ], check=True)

            subprocess.run([
                "nmcli", "connection", "modify", ssid,
                "wifi-sec.key-mgmt", "wpa-psk",
                "wifi-sec.psk", password
            ], check=True)

            subprocess.run([
                "nmcli", "connection", "modify", ssid,
                "ipv4.method", "shared",
                "ipv4.addresses", "192.168.4.1/24"
            ], check=True)

        # activer la connexion
        subprocess.run([
            "nmcli", "connection", "up", ssid
        ], check=True)

        print("Hotspot actif :", ssid)
        HOTSPOT = True
        return True

    except subprocess.CalledProcessError as e:
        print("Erreur hotspot :", e)
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