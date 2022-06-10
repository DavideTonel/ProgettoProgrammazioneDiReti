# -*- coding: utf-8 -*-

import sys
import os

SEPARATOR = '.!.'
BUFFER_SIZE = 1024

def select_port():
    possible_port = input('Select a port: ')
    if possible_port.isdecimal() and int(possible_port) > 1024:
        return int(possible_port)
    else:
        return 8080

def is_valid(request):
    if len(request) < 1:
        return False
    return True

def make_request(client_socket, server_address):
    layout_instructions = 'Command layout: COMMAND ARG1, ARG2, ..., ARGn'
    print(layout_instructions)
    request = input('Write command here: ')
    while not is_valid(request):
        print('Invalid command, try again.')
        print(layout_instructions)
        request = input('Write command here: ')
            
    normalized_request = normalize_request(request)
    analize_request(client_socket, server_address, normalized_request)
   
def normalize_request(request):
    # Layout of a normalized request: command_uppercaseSEPARETORarg1,...,argn
    command = request.split(' ', 1)
    operation = command[0]
        
    normalized_request = operation.upper() + SEPARATOR
    if len(command) > 1:
        args = command[1].split(', ')
        
        for name in args:
            normalized_request = normalized_request + name + ','
        # Remove the last ','
        normalized_request = normalized_request[:-1]       
        
    return normalized_request

def analize_request(client_socket, server_address, normalized_request):
    request = normalized_request.split(SEPARATOR)
    operation = request[0]
    args = request[1].split(',')
                
    if operation == 'QUIT':
        return close(client_socket, server_address, args)
    elif operation == 'PUT':
        return send_files(client_socket, server_address, args)
    elif operation == 'GET':
        return get_files(client_socket, server_address, args)   #PARE PERFETTO
    elif operation == 'LIST':
        return list_files(client_socket, server_address, normalized_request) #PARE PERFETTO
    else:
        client_socket.sendto(normalized_request.encode() , server_address)
        data, server = client_socket.recvfrom(BUFFER_SIZE)
        print(data.decode('utf8'))

def close(client_socket, server_address, args):
    if args[0] == '':
        print('Quitting... Goodbye!')
        client_socket.close()
        sys.exit()
    elif args[0] == 'all':
        client_socket.sendto('QUIT'.encode(), server_address)
        data, address = client_socket.recvfrom(BUFFER_SIZE)
        print(data.decode('utf8'))
        client_socket.close()
        sys.exit()
    else:
        print('ERROR: ' + args[0] + ' invalid arguments')
    
def list_files(client_socket, server_address, normalized_request):
    client_socket.sendto(normalized_request.encode(), server_address)
    data, address = client_socket.recvfrom(BUFFER_SIZE)
    answer = data.decode('utf8').split(SEPARATOR)
    
    outcome = answer[0]
    
    if outcome == 'DONE':
        print(answer[1])
    else:
        print('Error: ' + answer[1])
        
def get_single_file(client_socket, server_address, name):
    single_get_request_template = 'GET' + SEPARATOR
    single_get_request = single_get_request_template + name

    client_socket.sendto(single_get_request.encode(), server_address)
    
    data, address = client_socket.recvfrom(BUFFER_SIZE)
    answer = data.decode('utf8').split(SEPARATOR)
    outcome = answer[0]
    
    if outcome == 'DONE':
        with open(name, 'wb') as file_writer:
            while True:
                data, address = client_socket.recvfrom(BUFFER_SIZE)
                # End of file
                if data == SEPARATOR.encode():
                    break
                file_writer.write(data)
            file_writer.close()
        print(name + ' downloaded successfully')
    elif outcome == 'NOTDONE':
        message_error = answer[1]
        print('ERROR: ' + message_error)
    
def get_files(client_socket, server_address, args):
    if args[0] == '':
        print('ERROR: get needs at least an argument.')
    else:
        for name in args:
            get_single_file(client_socket, server_address, name)
            
def send_files(client_socket, server_address, args):
    if args[0] == '':
        print('ERROR: put needs at least an argument.')
    else:
        for name in args:
            send_single_file(client_socket, server_address, name)
            
def send_single_file(client_socket, server_address, name):
    single_put_request_template = 'PUT' + SEPARATOR
    single_put_request = single_put_request_template + name
        
    if os.path.isfile(name):
        client_socket.sendto(single_put_request.encode(), server_address)

        with open(name, 'rb') as file_reader:
            while True:
                data_piece = file_reader.read(BUFFER_SIZE)
                if not data_piece:
                    client_socket.sendto(SEPARATOR.encode(), server_address)
                    break
                client_socket.sendto(data_piece, server_address)
            file_reader.close()
            
        data, address = client_socket.recvfrom(BUFFER_SIZE)
        outcome = data.decode('utf8').split(SEPARATOR)[0]
        if outcome == 'DONE':
            print(name + ' saved on server!')
    else:
        print('ERROR: ' + name + ' doesn\'t exist or it\'s not a file.')
    