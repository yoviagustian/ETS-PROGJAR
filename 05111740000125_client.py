import socket
import select
import sys
import msvcrt
import os
import math
from ftplib import FTP

#  menerima input user dan pas
ip = input('IP Server: ')
username = input('username: ')
password = input('password: ')

# fungsi untuk menerima file
def terima(sock):
    # menerima nama file
    namaFile = sock.recv(1024).decode()
    # menerima banyak chunk yg akan dikirim
    sz = int(sock.recv(1024).decode())

    # menrima setiap chunk
    f = open(namaFile, 'wb')
    for i in range (sz):
        isi = sock.recv(1024)
        f.write(isi)
    f.close()

# flag untuk menandakan status login yg dilakukan
login_flag = 0

#  mencoba lakukan koneksi dan login ke ftp server
try:
    f = FTP(str(ip))
    f.login(str(username), str(password))
    login_flag = 1
except:
    print('Login Fail')
    login_flag = 0

# jika login ftp berhasil lakukan koneksi ke server
if(login_flag):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 8081
    server.connect((ip, port))

    while True:
        socket_list = [server]
        read_socket, write_socket, error_socket = select.select(socket_list, [], [], 1)

        for socks in read_socket + [sys.stdin]:
        
            if socks == server:
                message = socks.recv(1024).decode()
                
                #  mendapatkan perintah dengan melakukan split
                try :
                    choice, nama = message.split()
                except:
                    choice = message

                # client diinta untuk menyiapkan
                # akan dikirim file
                if (choice == 'SENDALL') or (choice == 'DOWNZIP'):
                    # menerima file
                    namaFile = socks.recv(1024).decode()
                    sz = int(socks.recv(1024).decode())

                    f = open(namaFile, 'wb')
                    for i in range (sz):
                        isi = socks.recv(1024)
                        f.write(isi)
                    f.close()
                    # 
                else:
                    # jika bukan perintah/chat biasa
                    # print saja
                    print(message)

            # jika keyboard ditekan
            elif msvcrt.kbhit():
                message = sys.stdin.readline()
                message = str(message[:-1])
                sys.stdout.flush()

                # Cek Apakah perintah atau pesan biasa
                try :
                    choice, nama = message.split()
                except:
                    choice = message

                # lakukan koneksi ulang 
                # menghindari time limit
                f = FTP(str(ip))
                f.login(str(username), str(password))

                # list file
                if (choice == 'LIST'):
                    names = f.nlst()
                    print (names, "\n")
                # cek current directory
                elif (choice == 'PWD'):
                    print (f.pwd(), "\n")
                # pindah folder
                elif (choice == 'CD'):
                    f.cwd(nama)
                # membuat folder
                elif (choice == 'MKDIR'):
                    f.mkd(str(nama))
                # broadcast file
                elif (choice == 'SENDALL'):
                    # simpan current directory
                    tmp = f.pwd()

                    fp = open(str(nama), 'rb')
                    # pindah ke base directory
                    f.cwd('/')
                    # upload file dengan file zilla
                    f.storbinary('STOR ' + str(nama), fp, 1024)
                    fp.close()

                    # kembali ke directory semula
                    f.cwd(tmp)

                    server.send(message.encode())
                # download directory
                elif (choice == 'DOWNZIP'):
                    # mengirim pesan ke server 
                    # untuk melakukan zip dan kirim folder
                    server.send(message.encode())
                else:
                    server.send(message.encode())
                    
    server.close()
    f.quit()