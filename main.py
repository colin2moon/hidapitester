import socket
from pythonosc import udp_client

# Remappage personnalisé pour 32 octets (256 bits)
# Ajustez ce tableau selon le schéma de remappage des bits que vous souhaitez
bit_mapping = [
    20, 21, 22, 23, 8, 9, 10, 11,
    12, 255, 255, 255, 255, 255, 255, 255,
    36, 37, 38, 39, 24, 25, 26, 27,
    28, 255, 255, 255, 255, 255, 255, 255,
    
    52, 53, 54, 55, 40, 41, 42, 43,
    44, 255, 255, 255, 255, 255, 255, 255,
    68, 69, 70, 71, 56, 57, 58, 59,
    60, 255, 255, 255, 255, 255, 255, 255,

    84, 85, 86, 87, 72, 73, 74, 75,
    76, 255, 255, 255, 255, 255, 255, 255,
    100, 101, 102, 103, 88, 89, 90, 91,
    92, 255, 255, 255, 255, 255, 255, 255,

    116, 117, 118, 119, 104, 105, 106, 107,
    108, 255, 255, 255, 255, 255, 255, 255,
    132, 133, 134, 135, 120, 121, 122, 123,
    124, 255, 255, 255, 255, 255, 255, 255,

    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,

    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,

    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,

    255, 255, 255, 255, 255, 255, 255, 255,
    7, 6, 5, 4, 0, 1, 2, 3, 
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
]

def hex_to_bin(hex_str):
    return ''.join(format(int(byte, 16), '08b') for byte in hex_str)

def is_hex(s):
    """Vérifie si la chaîne est un hexadécimal valide."""
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def map_bits(bits, mapping):
    """Remappage des bits selon le tableau de remappage."""
    mapped_bits = ['0'] * len(mapping)  # La longueur de mapped_bits doit correspondre à celle de mapping
    for i, mapped_index in enumerate(mapping):
        if mapped_index < len(bits):  # Vérifier que l'index est valide et non égal à 255
            mapped_bits[i] = bits[mapped_index]
    return ''.join(mapped_bits)

def extract_bits(mapped_binary_data, start_bit, end_bit):
    return mapped_binary_data[start_bit:end_bit]

def parse_data(data, binary_mode=True):

    if binary_mode:
        # Convertir les données binaires en une chaîne binaire
        binary_data = ''.join(format(byte, '08b') for byte in data)
    else:
        """Convertir les données ASCII en valeurs binaires, puis les remapper et extraire des segments de 12 bits."""
        # Nettoyer les données pour enlever les espaces et les retours à la ligne
        cleaned_data = data.replace(' ', '').replace('\n', '')
    
        # Filtrer les segments non valides (en supposant que les segments sont des hexadécimaux valides)
        valid_segments = [cleaned_data[i:i+2] for i in range(0, len(cleaned_data), 2) if is_hex(cleaned_data[i:i+2])]
    
        # Convertir la chaîne hexadécimale en une chaîne binaire
        #binary_data = ''.join(format(int(segment, 16), '08b') for segment in valid_segments)

        # Convertir le message reçu en binaire
        binary_data = hex_to_bin(valid_segments)

    # Afficher la variable binary_data avec espace tous les 8 bits
    formatted_binary_data = ' '.join([binary_data[i:i+8] for i in range(0, len(binary_data), 8)])
    print(f"Binary data: {formatted_binary_data}")

    # Appliquer le bit mapping
    mapped_binary_data = map_bits(binary_data, bit_mapping)

    # Afficher la variable binary_data avec espace tous les 8 bits
    formatted_mapped_binary_data = ' '.join([mapped_binary_data[i:i+8] for i in range(0, len(mapped_binary_data), 8)])
    print(f"Binary mapped data: {formatted_mapped_binary_data}")

    if len(binary_data) != 256:
        print('Attention: les données ne contiennent pas 256 bits (32 octets) count:' + str(len(binary_data)))
        return []
    
    # Itérer 8 fois, chaque itération sur une fenêtre de 32 octets
    results = []

    for i in range(0, 256, 16):
        extracted_bits = extract_bits(mapped_binary_data, i, i + 9)
        results.append(int(extracted_bits, 2))
        print(f"Extracted bits: {extracted_bits}")
        if len(results) >= 8:
            break

    # Convertir les bits extraits en décimal
    # decimal_value = int(extracted_bits, 2)
    # print(f"Decimal value: {decimal_value}")
    
    return results

# Fonction principale du serveur pour recevoir et traiter les données des sliders
def start_server(host='0.0.0.0', port=5000, osc_host='127.0.0.1', osc_port=9000):  # Utilisez localhost pour les tests locaux
    # Créer un client OSC
    osc_client = udp_client.SimpleUDPClient(osc_host, osc_port)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f'Server listening on {host}:{port}')
        try:
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f'Connected by {addr}')
                    buffer = b""
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            print("No data received, closing connection.")
                            break

                        # print(f'Received message: {data}')
                        buffer += data
                        # buffer += data.decode('ascii')
                        # buffer += data.decode('utf-8', errors='ignore')  # Decode bytes to string using UTF-8
                        while b"\r\n" in buffer:
                            message, buffer = buffer.split(b"\r\n", 1)
                            print(f'Received message: {message}')
                            
                            try:
                                # Check if the message contains exactly 32 bytes (256 bits)
                                if len(message) != 32:
                                    print(f"Attention: les données ne contiennent pas 256 bits (32 octets) count: {len(message)}")
                                    continue

                                # Parse les données et itérer 8 fois sur 32 octets
                                results = parse_data(message)
                                
                                for iteration, parsed_values in enumerate(results):
                                    print(f'Iteration {iteration + 1}:')
                                    print(f'Parsed slider values (32 chars): {parsed_values}')
                                    # Envoyer les valeurs analysées via OSC
                                    osc_client.send_message(f"/rot{iteration + 1}", parsed_values)
                            except Exception as e:
                                print(f"Error parsing data: {e}")

        except KeyboardInterrupt:
            print("Server interrupted by user")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            print("Closing server socket.")
            s.close()

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"An error occurred in the main function: {e}")