import socket 
import sys 
import select 
from multiprocessing import Process 
import hashlib

# Import temporário
import time

def find_sucessor(node_id,nodes):
    sucessor = None
    for node in sorted(nodes):
        print(nodes.get(node))
        if int(node) > node_id: 
            sucessor = node
            break
    return sucessor

def find_predecessor(node_id, nodes):
    predecessor = None
    for node in sorted(nodes):
        if int(node) < node_id:
            predecessor = node
    return predecessor

def chord_node(identifier,location,nodes):
    hash_table = dict() # Tabela onde ficam as informações armazenadas nesse nó
    finger_table = dict() # Tabela onde fica a referência para os outros nós 

    sucessor = find_sucessor(int(identifier), nodes)
    predecessor = find_predecessor(int(identifier), nodes)
        
    print("[Node {0}] Sucessor is {1}".format(identifier,sucessor))
    print("[Node {0}] Predecessor is {1}".format(identifier,predecessor))

    # Espera ocupada
    a = -50
    for i in range(0,100000):
        a += 1 

def spawn_chord_nodes(n):

    # Variáveis que serão retornadas no fim da função mais outras de uso no loop
    spawn_array = []
    locations = dict()
    port = 4200 
    sha1 = hashlib.sha1()

    for i in range(0,n):
        # Gerando informações do nó que será gerado
        node_location = "localhost " + str(port)
        sha1.update(bytes(node_location,encoding='utf-8'))
        node_key = sha1.hexdigest()
        node_key = int(node_key,16) % 2**n
        
        # Gerando o nó com as informações geradas
        proc = Process(target=chord_node,args=(node_key,port,locations,))
        proc.start()

        # Atualizamos as informaçoes das estruturas de retorno 
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
