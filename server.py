import os
import shutil
import socket
import threading
import zipfile
import select

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5007
SHARED_DIR = './shared_drive'
clients = []
lock = threading.Lock()

def handle_client(client_socket, addr):
    global clients
    try:
        while True:
            # Client valid
            ready_to_read, _, _ = select.select([client_socket], [], [], 0.1)
            if ready_to_read:
                request = client_socket.recv(1024).decode('utf-8')
                if not request:
                    break  # Client disconnected
                if request == 'SYNC':
                    print(f"S-a primit comanda SYNC de la client-ul: {addr}")
                    send_directory(client_socket)
                elif request == 'CHANGE':
                    print(f"S-a primit comanda CHANGE de la client-ul: {addr}")
                    update_from_client(client_socket, addr)
                    notify_clients(client_socket, addr)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        clients.remove(client_socket)
        client_socket.close()
        print(f'Clientul {addr} s-a deconenctat.')

def send_directory(client_socket):
    try:
        with lock:
            with zipfile.ZipFile('shared_drive.zip', 'w') as zipf:
                for root, _, files in os.walk(SHARED_DIR):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), SHARED_DIR))
        print("S-a trimis directorul la client.")
        
        file_size = os.path.getsize('shared_drive.zip')
        client_socket.sendall(str(file_size).encode())
        with open('shared_drive.zip', 'rb') as f:
            data = f.read()
            client_socket.sendall(data)
        os.remove('shared_drive.zip')
    except Exception as e:
        print(f"Eroare in send_directory: {e}")

def update_from_client(client_socket, addr):
    try:
        if os.path.exists(SHARED_DIR):
            shutil.rmtree(SHARED_DIR)
        os.makedirs(SHARED_DIR)
        # S-a sters directorul remote

        file_size_data = b''
        while b'PK' not in file_size_data:      # Primeste date pana gaseste semnatura PK 
            data = client_socket.recv(1024)
            file_size_data += data

        file_size_index = file_size_data.find(b'PK')
        file_size = int(file_size_data[:file_size_index])

        with open('NEWlocal_drive.zip', 'wb') as f:
            received_size = len(file_size_data) - file_size_index
            f.write(file_size_data[file_size_index:])
            while received_size < file_size:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                received_size += len(data)
        # S-a primit directorul local de la client
        
        with zipfile.ZipFile('NEWlocal_drive.zip', 'r') as zipf:
            zipf.extractall(SHARED_DIR)
        # S-au extras componentele arhivei

        os.remove('NEWlocal_drive.zip')
        # S-a sters arhiva
        print(f"Directorul remote a fost modificat de clientul: {addr}")
    
    except Exception as e:
        print(f"Eroare in update_from_client: {e}")


def notify_clients(client_socket, addr):
    global clients
    for client in clients:
        try:
            if (client != client_socket):
                client.send(f'Directorul remote a fost modificat de clientul {addr}.\nFolositi comanda SYNC pentru a va sincroniza directorul local.'.encode('utf-8'))
        except:
            clients.remove(client)
            client.close()
            print(f'Clientul {addr} s-a deconenctat in urma unei erori.')

def main():
    if not os.path.exists(SHARED_DIR):
        os.makedirs(SHARED_DIR)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    print(f'Serverul asculta la: {SERVER_HOST}:{SERVER_PORT}')
    
    while True:
        client_socket, addr = server.accept()
        print(f'Clientul {addr} s-a conectat')
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,addr)).start()

if __name__ == "__main__":
    main()
