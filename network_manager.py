"""
Gestion du point d'accès Wi-Fi (hotspot) du photomaton via NetworkManager (nmcli).

Utilisé notamment pour l'impression : l'imprimante Wi-Fi est connectée au hotspot
« photomaton », il faut donc que le Raspberry Pi l'émette, même s'il était connecté
à un autre réseau Wi-Fi.
"""
import shutil
import subprocess
import time

# Nom du profil NetworkManager créé par l'application si aucun profil hotspot n'existe
HOTSPOT_CONNECTION_NAME = "photomaton-hotspot"


def _nmcli(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(["nmcli", *args], capture_output=True, text=True, timeout=timeout)


def is_available() -> bool:
    """Indique si NetworkManager (nmcli) est disponible."""
    return shutil.which("nmcli") is not None


def get_wifi_interface() -> str | None:
    """Retourne le nom de la première interface Wi-Fi (ex: 'wlan0')."""
    result = _nmcli("-t", "-f", "DEVICE,TYPE", "dev")
    for line in result.stdout.splitlines():
        device, _, dev_type = line.rpartition(":")
        if dev_type == "wifi" and device:
            return device
    return None


def _get_connection_wifi_settings(connection: str) -> tuple[str, str]:
    """Retourne (mode, ssid) d'un profil Wi-Fi NetworkManager."""
    result = _nmcli("-g", "802-11-wireless.mode,802-11-wireless.ssid", "con", "show", connection)
    lines = result.stdout.splitlines()
    mode = lines[0].strip() if len(lines) > 0 else ""
    ssid = lines[1].strip() if len(lines) > 1 else ""
    return mode, ssid


def get_active_connection(iface: str) -> str | None:
    """Retourne le nom du profil actif sur l'interface, ou None."""
    result = _nmcli("-g", "GENERAL.CONNECTION", "dev", "show", iface)
    name = result.stdout.strip()
    return name or None


def is_hotspot_active(iface: str, ssid: str) -> bool:
    """Vérifie si l'interface émet déjà le hotspot avec le SSID demandé."""
    connection = get_active_connection(iface)
    if not connection:
        return False
    mode, active_ssid = _get_connection_wifi_settings(connection)
    return mode == "ap" and active_ssid == ssid


def _find_hotspot_profile(ssid: str) -> str | None:
    """Cherche un profil NetworkManager existant en mode point d'accès pour ce SSID."""
    result = _nmcli("-t", "-f", "NAME,TYPE", "con", "show")
    for line in result.stdout.splitlines():
        name, _, con_type = line.rpartition(":")
        if con_type != "802-11-wireless" or not name:
            continue
        name = name.replace("\\:", ":")
        mode, profile_ssid = _get_connection_wifi_settings(name)
        if mode == "ap" and profile_ssid == ssid:
            return name
    return None


def get_interface_ip(iface: str) -> str | None:
    """Retourne l'adresse IPv4 de l'interface (sans le masque)."""
    for _ in range(10):
        result = _nmcli("-g", "IP4.ADDRESS", "dev", "show", iface)
        address = result.stdout.strip().split("|")[0].strip()
        if address:
            return address.split("/")[0]
        time.sleep(0.5)
    return None


def start_hotspot(ssid: str, password: str = "") -> tuple[bool, str | None, str]:
    """
    Active le hotspot sur l'interface Wi-Fi (en quittant le réseau actuel si besoin).
    Réutilise le profil existant s'il y en a un, pour que l'imprimante retrouve
    exactement le même réseau (SSID / mot de passe).

    Retourne (succès, ip_du_hotspot, message).
    """
    if not is_available():
        return False, None, "NetworkManager (nmcli) n'est pas installé."

    iface = get_wifi_interface()
    if not iface:
        return False, None, "Aucune interface Wi-Fi trouvée."

    if is_hotspot_active(iface, ssid):
        return True, get_interface_ip(iface), f"Le hotspot '{ssid}' est déjà actif."

    profile = _find_hotspot_profile(ssid)
    if profile:
        print(f"INFO: Activation du profil hotspot existant '{profile}' sur {iface}...")
        result = _nmcli("con", "up", profile, "ifname", iface)
    elif password:
        print(f"INFO: Création du hotspot sécurisé '{ssid}' sur {iface}...")
        result = _nmcli("dev", "wifi", "hotspot", "ifname", iface, "con-name", HOTSPOT_CONNECTION_NAME,
                        "ssid", ssid, "password", password)
    else:
        # 'nmcli dev wifi hotspot' sans mot de passe en génère un aléatoire :
        # on crée donc explicitement un point d'accès ouvert.
        print(f"INFO: Création du hotspot ouvert '{ssid}' sur {iface}...")
        result = _nmcli("con", "add", "type", "wifi", "ifname", iface, "con-name", HOTSPOT_CONNECTION_NAME,
                        "autoconnect", "no", "ssid", ssid,
                        "802-11-wireless.mode", "ap", "802-11-wireless.band", "bg",
                        "ipv4.method", "shared", "ipv6.method", "ignore")
        if result.returncode == 0:
            result = _nmcli("con", "up", HOTSPOT_CONNECTION_NAME, "ifname", iface)

    if result.returncode != 0:
        error = (result.stderr or result.stdout).strip()
        return False, None, f"Échec de l'activation du hotspot : {error}"

    ip = get_interface_ip(iface)
    return True, ip, f"Hotspot '{ssid}' actif" + (f" (IP {ip})." if ip else ".")
