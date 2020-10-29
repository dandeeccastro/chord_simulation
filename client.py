import socket 
import sys 
import select 
from multiprocessing import Process 
import hashlib

# Import temporário
import time

def string_to_address(x):
    x = x.split()
    return (x[0],int(x[1]))

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

    sock = socket.socket()
    sock.bind(('localhost',location))
    sock.listen(1)
        
    print("[Node {0}] Sucessor is {1}".format(identifier,sucessor))
    print("[Node {0}] Predecessor is {1}".format(identifier,predecessor))

    r,w,x = select.select([sock],[],[])
    for command in r:
        if command == sock:
            new_sock, addr = sock.accept()

            msg = new_sock.recv(1024)
            msg = str(msg,encoding='utf-8')
            print(msg)

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

    while True:
        sock = socket.socket()
        command = input()
        command = command.split()
        address = string_to_address(addresses[int(command[1])]) if len(command) > 1 else None
        if command[0] == "query":
            sock.connect(address)
            sock.send(b"salve")
            print("this should query the network")
        elif command[0] == "insert":
            print("this should add to the network")
        elif command[0] == "close" or command == "quit":
            for address in addresses.values():
                sock.connect(string_to_address(address))
                sock.send(b"QUIT")
                msg = sock.recv(1024)
                msg = str(msg,encoding='utf-8')
                print(msg)
                sock = socket.socket()
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
