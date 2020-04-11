import socket
import select
import sys
import threading
import math
import os
import zipfile

# membuat socket pada server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ip_address = '127.0.0.1'
port = 8081
server.bind(("localhost", 8081))
server.listen(100)
list_of_clients = []

# menghandle client
def clientthread(conn, addr):
    message = "connected "
    conn.send(message.encode())
    while True:
        try:
            message = conn.recv(1024).decode()
            if message:
                message = str(message)

                # Mendapatkan perintah dengan di split -> choice
                try:
                    choice, nama = message.split()
                except:
                    choice = message

                #  Jika user mengirimkan perintah SENDALL 
                if (choice == 'SENDALL'):
                    broadcastFile(message, nama, conn)
                    # mendapatkan path file di server
                    fnama = os.path.basename(nama)
                    # menghapus file di server
                    os.remove(fnama)
                elif (choice == 'DOWNZIP'):
                    # mengirim pesan dahulu agar client 
                    # mengetahui akan dikirim file
                    conn.send(message.encode())
                    # zip folder secara rekursif 
                    namazip = zipdir(nama)
                    # mengirim hasil zip
                    kirim(namazip, conn)
                    # menghapus zip
                    os.remove(namazip)
                else:
                    message_to_send = '<' + addr[0] + '> ' + message
                    #  Karena bukan perintah maka lakukan broadcast pesan
                    broadcast(message_to_send, conn)
            else:
                remove(conn)
        except:
            continue

# fungsi untuk mengirim pesan ke seluruh client
def broadcast(message, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                clients.send(message.encode())
            except:
                clients.close()
                remove(clients)

# fungsi untuk mengkompres directory
def zipdir(path):
    namazip = str(os.path.basename(path)) + '.zip'
    ziph = zipfile.ZipFile(namazip, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
    ziph.close()

    return namazip

# fungsi untuk mengirim file ke client
def kirim(path, s):
    namaFile = os.path.basename(path)
    sz = math.ceil(os.stat(path).st_size/1024)

    # mengirim nama file
    s.send(namaFile.encode())
    # mengirim banyak chunk
    s.send(str(sz).encode())

    # mengirim setiap chunk
    f = open(namaFile, 'rb')
    for i in range(sz) :
        isi = f.read(1024)
        s.send(isi)
    f.close()

# fungsi untuk mengirim file ke seluruh client
def broadcastFile(message, path, connection):
    for clients in list_of_clients:
        if clients != connection:
            try:
                # mengirim pesan dahulu agar client 
                # mengetahui akan dikirim file
                clients.send(message.encode())
                # mengirim file
                kirim(path, clients)
            except:
                clients.close()
                remove(clients)

def remove(connection):
    if connection in list_of_clients:
        list_of_clients.remove(connection)

while True:
    conn, addr = server.accept()
    list_of_clients.append(conn)
    print(addr[0] + ' connected')
    # masing client akan di handle oleh sebuah thread
    threading.Thread(target = clientthread, args = (conn, addr)).start()

conn.close()