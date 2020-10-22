import socket 
import sys 
import select 
from multiprocessing import Process 

# Import temporário
import time

def chord_node():
    a = -50
    for i in range(0,100000):
        a += 1 # Espera ocupada

def spawn_chord_nodes(n):
    spawn_array = []
    locations = []
    port = 4200 # TODO talvez mudar isso aqui depois
    for i in range(0,n):
        proc = Process(target=chord_node)
        proc.start()
        spawn_array.append(proc)
        locations.append(("localhost",port))
        port += 1
    return locations, spawn_array

def run_client_interface(addresses):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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
