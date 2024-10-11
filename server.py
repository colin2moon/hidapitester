import subprocess
import socket
import time
import platform
import threading

def read_hid_data(command):
    """Lance hidapitester et lit les données."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except FileNotFoundError:
        print("Erreur : hidapitester introuvable. Vérifiez le chemin.")
        raise
    except Exception as e:
        print(f"Erreur lors de l'exécution de hidapitester : {e}")
        raise

def send_data_to_server(conn, data):
    """Envoie les données au serveur via une connexion socket existante."""
    try:
        conn.sendall(data)
    except Exception as e:
        print(f"Erreur lors de l'envoi des données : {e}")
        raise

def handle_device(command, host, port):
    """Gère la communication pour un périphérique spécifique."""
    process = read_hid_data(command)
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                conn.connect((host, port))
                print(f"Connecté au serveur {host}:{port}")
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    send_data_to_server(conn, line)
        except (ConnectionResetError, ConnectionRefusedError, BrokenPipeError) as e:
            print(f"Connexion perdue, tentative de reconnexion dans 5 secondes : {e}")
            time.sleep(5)  # Attendre avant de réessayer
        except Exception as e:
            print(f"Erreur de lecture des données HID ou de connexion : {e}")
            break
    if process:
        process.terminate()

def main():
    host = "10.0.1.52"  # Utilisez localhost pour les tests locaux
    port = 5000

    # Détection du système d'exploitation et ajustement de la commande
    if platform.system() == "Windows":
        command = ["hidapitester.exe", "--vidpid", "17CC/1220", "--open", "--timeout", "0", "--quiet", "--length", "32", "--read-input-forever"]
    elif platform.system() == "Darwin":  # macOS
        command = ["./hidapitester", "--vidpid", "17CC/1220", "--open", "--timeout", "0", "--quiet", "--length", "32", "--read-input-forever"]
    else:
        raise OSError("Unsupported operating system")

    # Créer et démarrer un thread pour gérer le périphérique
    thread = threading.Thread(target=handle_device, args=(command, host, port))
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()