import os
import shutil
import socket
import select
import sys
import zipfile

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5007
LOCAL_DIR = './local_drive'

def sync_with_server(client_socket):
    try:
        if os.path.exists(LOCAL_DIR):
            shutil.rmtree(LOCAL_DIR)
        os.makedirs(LOCAL_DIR)
        # S-a sters directorul local

        client_socket.send('SYNC'.encode('utf-8'))
        print("S-a trimis comanda SYNC la server.")

        file_size_data = b''
        while b'PK' not in file_size_data:      # Primeste date pana gaseste semnatura PK 
            data = client_socket.recv(1024)
            file_size_data += data

        file_size_index = file_size_data.find(b'PK')
        file_size = int(file_size_data[:file_size_index])

        with open('NEWshared_drive.zip', 'wb') as f:
            received_size = len(file_size_data) - file_size_index
            f.write(file_size_data[file_size_index:])
            while received_size < file_size:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                received_size += len(data)
        # S-a primit arhiva de la server
        
        with zipfile.ZipFile('NEWshared_drive.zip', 'r') as zipf:
            zipf.extractall(LOCAL_DIR)
        # S-au extras componentele arhivei

        os.remove('NEWshared_drive.zip')
        # S-a sters arhiva
        print(f"Directorul local a fost sincronizat cu directorul remote.\nScrieti comanda: ", end='', flush=True)
    
    except Exception as e:
        print(f"Eroare in comanda sync_with_server: {e}")

def notify_server_of_change(client_socket):
    try:
        client_socket.send('CHANGE'.encode('utf-8'))
        print("S-a trimis comanda CHANGE la server.")

        with zipfile.ZipFile('local_drive.zip', 'w') as zipf:
            for root, _, files in os.walk(LOCAL_DIR):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), LOCAL_DIR))
        print("Directorul local a fost trimis la server.\nScrieti comanda: ", end='', flush=True)

        file_size = os.path.getsize('local_drive.zip')
        client_socket.sendall(str(file_size).encode())
        with open('local_drive.zip', 'rb') as f:
            data = f.read()
            client_socket.sendall(data)
        os.remove('local_drive.zip')
    except Exception as e:
        print(f"Eroare in notify_server_of_change: {e}")

def handle_server_messages(client_socket):
    try:
        message = client_socket.recv(1024).decode('utf-8')
        if message:
            print(f"\n{message}")
            print('Scrieti comanda: ', end='', flush=True)
    except Exception as e:
        print(f"Eroare in handle_server_messages: {e}")

def print_help():
    help_message = """Comenzi disponibile:
SYNC - Sincronizeaza directorul local cu serverul. Salvati intr-un alt director orice modificari locale vreti sa pastrati.
CHANGE - Actualizeaza directorul remote cu modificarile locale.
HELP - Afiseaza acest mesaj de ajutor.
QUIT - Inchide clientul.
Scrieti comanda: """
    print(help_message, end='', flush=True)

def main():
    try:
        if not os.path.exists(LOCAL_DIR):
            os.makedirs(LOCAL_DIR)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f'Bine ati venit!\nConectat la serverul: {SERVER_HOST}:{SERVER_PORT}\nScrieti HELP pentru ajutor.')

        sync_with_server(client_socket)

        while True:
            
            readable, _, _ = select.select([client_socket, sys.stdin], [], [])

            if client_socket in readable:
                handle_server_messages(client_socket)
            
            if sys.stdin in readable:
                command = input()
                if command == 'SYNC':
                    sync_with_server(client_socket)
                elif command == 'CHANGE':
                    notify_server_of_change(client_socket)
                elif command == 'HELP':
                    print_help()
                elif command == 'QUIT':
                    print("Conexiune incheiata. La revedere!")
                    client_socket.close()
                    break
                else:
                    print("Comanda inexistenta. Scrieti HELP pentru o lista de comenzi valide.\nScrieti comanda: ", end='', flush=True)

    except Exception as e:
        print(f"Eroare in main: {e}")

if __name__ == "__main__":
    main()

