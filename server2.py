import hid
import socket
import time
import threading

def read_hid_data(device):
    """Lit les données du périphérique HID."""
    try:
        while True:
            data = device.read(32)
            if data:
                yield data
    except Exception as e:
        print(f"Erreur lors de la lecture des données HID : {e}")
        raise

def send_data_to_server(conn, data):
    """Envoie les données au serveur via une connexion socket existante."""
    try:
        conn.sendall(data)
    except Exception as e:
        print(f"Erreur lors de l'envoi des données : {e}")
        raise

def handle_device(vendor_id, product_id, host, port):
    """Gère la communication pour un périphérique spécifique."""
    try:
        device = hid.device()
        device.open(vendor_id, product_id)
        print(f"Périphérique HID ouvert : VID={vendor_id:04x}, PID={product_id:04x}")
        
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                    conn.connect((host, port))
                    print(f"Connecté au serveur {host}:{port}")
                    for data in read_hid_data(device):
                        send_data_to_server(conn, bytes(data))
            except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError) as e:
                print(f"Connexion perdue, tentative de reconnexion dans 5 secondes : {e}")
                time.sleep(5)  # Attendre avant de réessayer
            except Exception as e:
                print(f"Erreur de lecture des données HID ou de connexion : {e}")
                break
    finally:
        device.close()
        print("Périphérique HID fermé")

def main():
    host = "10.0.1.52"  # Utilisez localhost pour les tests locaux
    port = 5000
    vendor_id = 0x17CC  # Remplacez par votre Vendor ID
    product_id = 0x1220  # Remplacez par votre Product ID

    # Créer et démarrer un thread pour gérer le périphérique
    thread = threading.Thread(target=handle_device, args=(vendor_id, product_id, host, port))
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
