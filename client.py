import socket 
import sys 
import select 
from multiprocessing import Process 
import hashlib

# Import temporário
import time

def chord_node(identifier,location):
    hash_table = dict()
    finger_table = dict()

    print(identifier, location)

    # Espera ocupada
    a = -50
    for i in range(0,100000):
        a += 1 

def spawn_chord_nodes(n):

    spawn_array = []
    locations = dict()
    port = 4200 # TODO talvez mudar isso aqui depois
    sha1 = hashlib.sha1()

    for i in range(0,n):
        node_location = "localhost " + str(port)
        sha1.update(bytes(node_location,encoding='utf-8'))
        node_key = sha1.hexdigest()
        proc = Process(target=chord_node,args=(node_key,port,))
        proc.start()

        spawn_array.append(proc)
        locations[node_key] = node_location

        port += 1

    return locations, spawn_array

def run_client_interface(addresses):
    sock = socket.socket()

    while True:
        command = input()
        if command == "query":
            print("this should query the network")
        elif command == "insert":
            print("this should add to the network")
        elif command == "close" or command == "quit":
            print("goodbye world")
            return 0

if __name__ == "__main__":
    # Spawno n processos 
    n = int(input("Insira o número de nós que quer na sua rede: "))
    addresses, nodes = spawn_chord_nodes( n )

    print(addresses)
    
    run_client_interface(addresses)

    # Espero os processos terminarem (necessário?)
    for node in nodes:
        print(node.pid)
        node.join()
