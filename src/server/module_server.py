# -*- coding: utf-8 -*-

import os
import sys
import socket as sk
import threading

SEPARATOR = '.!.'
BUFFER_SIZE = 1024


def select_port():
    possible_port = input('Select a port: ')
    if possible_port.isdecimal() and int(possible_port) > 1024:
        return int(possible_port)
    else:
        return 8080
  
def handle_request(server_socket, address, request):
    request_list = request.split(SEPARATOR, 2)
    operation = request_list[0]
    arg = []
    if len(request_list) > 1:
        arg = request_list[1]

    print('Command recived: ' + operation.lower())
    if operation == 'LIST':
        return list_files(server_socket, address, arg)          
    elif operation == 'GET':
        return send_file(server_socket, address, arg)      
    elif operation == 'PUT':
        return save_file(server_socket, address, arg)     
    else:
        error = 'Invalid command, ' + operation.lower() + ' doesn\'t exist.'
        server_socket.sendto(error.encode(), address)    

def start(port, ip_address='localhost'):
    server_socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    server_address = (ip_address, port)
    server_socket.bind(server_address)
    
    print('starting up on %s port %s' % server_address)
    
    while True:
        print('Waiting for command...')
        data, address = server_socket.recvfrom(BUFFER_SIZE)
        request = data.decode('utf8')
        if request == 'QUIT':
            close_all(server_socket, address)
        
        thread = threading.Thread(target=handle_request, args=(server_socket, address, request))
        thread.start()
        thread.join()

def close_all(server_socket, address):
    server_socket.sendto('Closing all... Goodbye!'.encode(), address)
    server_socket.close()
    sys.exit()

def save_file(server_socket, address, name):
    with open(name, 'wb') as file_writer:
        while True:
            data, address = server_socket.recvfrom(BUFFER_SIZE)
            # End of file
            if data == SEPARATOR.encode():
                break
            file_writer.write(data)
        file_writer.close()
    put_answer = 'DONE' + SEPARATOR + name
    
    server_socket.sendto(put_answer.encode(), address)
        
def send_file(server_socket, address, name):
    if os.path.isfile(name):
        confirm = 'DONE' + SEPARATOR
        server_socket.sendto(confirm.encode(), address)
        with open(name, 'rb') as file_reader:
            while True:
                data_piece = file_reader.read(BUFFER_SIZE)
                if not data_piece:
                    server_socket.sendto(SEPARATOR.encode(), address)
                    break
                server_socket.sendto(data_piece, address)
            file_reader.close()
    else:
        error = 'NOTDONE' + SEPARATOR + name + ' doesn\'t exist or it\'s not a file.'    
        server_socket.sendto(error.encode(), address)
    
def list_files(server_socket, address, args):
    if len(args) != 0:
        res = 'NOTDONE' + SEPARATOR + 'no such arguments for command list.'
    else:
        file_list = os.listdir(os.getcwd())
        res = 'DONE' + SEPARATOR
        for name in file_list:
            res = res + name + '\n'
    server_socket.sendto(res.encode(), address)
