# -*- coding: utf-8 -*-

import socket as sk
import module_client as mc

socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
server_port = mc.select_port()
server_address = ('localhost', server_port)            

while True:
    mc.make_request(socket, server_address )