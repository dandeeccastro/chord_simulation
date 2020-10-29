import socket 
import sys 
import select 
from multiprocessing import Process 
import hashlib
import random

# Import temporário
import time

locations = dict()
sha1 = hashlib.sha1()

def string_to_address(x):
    x = x.split()
    return (x[0],int(x[1]))

def find_sucessor(node_id):
    sucessor = None
    for node in sorted(locations):
        if int(node) > node_id: 
            sucessor = node
            break
    if sucessor is None:
        sucessor = sorted(locations)[0]
    return sucessor

def chord_node(identifier,location):
    hash_table = dict() # Tabela onde ficam as informações armazenadas nesse nó
    finger_table = dict() # Tabela onde fica a referência para os outros nós 

    sucessor = find_sucessor(int(identifier))

    sock = socket.socket()
    sock.bind(('localhost',location))
    sock.listen(1)

    for i in range(0,len(locations.values())):
        node_id = identifier + 2**i
        node_id %= 2**len(locations.values())
        finger_table[node_id] = find_sucessor(node_id)
        
    print("[Node {0}] Sucessor is {1}".format(identifier,sucessor))
    print("[Node {0}] {1}".format(identifier,finger_table))

    r,w,x = select.select([sock],[],[])
    for command in r:
        if command == sock:
            new_sock, addr = sock.accept()
            msg_blob = new_sock.recv(1024)
            msg_blob = str(msg_blob,encoding='utf-8')
            msg = msg_blob.split()
            if msg[0] == 'insert':
                value = ' '.join(msg[2:])
                sha1.update(bytes(value,encoding='utf-8'))
                hash_value = sha1.hexdigest()
                hash_value = int(hash_value,16) % 2**len(locations.values())
                dest_node = find_sucessor(hash_value)
                print(dest_node)
                if dest_node == identifier:
                    hash_table[hash_value] = value
                    new_sock.send(b"INSERTED")
                    print(hash_table)
                else:
                    # Aqui a gente seguiria com a busca, mas n rola por enquanto
                    forward_sock = socket.socket()
                    dest_info = string_to_address(locations[dest_node])
                    forward_sock.connect(dest_info)
                    forward_sock.send(bytes('insert ' + str(dest_node) + ' ' + value,encoding='utf-8'))
                    response = forward_sock.recv(1024)
                    new_sock.send(response)


def spawn_chord_nodes(n):

    # Variáveis que serão retornadas no fim da função mais outras de uso no loop
    spawn_array = []
    port = random.randint(4201,5000) 
    sha1 = hashlib.sha1()
    ports = [port]

    for i in range(0,n):
        # Gerando informações do nó que será gerado
        node_location = "localhost " + str(port)
        sha1.update(bytes(node_location,encoding='utf-8'))
        node_key = sha1.hexdigest()
        node_key = int(node_key,16) % 2**n
        locations[node_key] = node_location
        while port in ports:
            port = random.randint(4201,5000)
        ports.append(port)
        
    for node_key in locations:
        # Gerando o nó com as informações geradas
        port = int(locations[node_key].split()[1])
        proc = Process(target=chord_node,args=(node_key,port,))
        proc.start()

        # Atualizamos as informaçoes das estruturas de retorno 
        spawn_array.append(proc)

    return spawn_array

def run_client_interface():

    while True:
        sock = socket.socket()
        command_blob = input()
        command = command_blob.split()
        address = string_to_address(locations[int(command[1])]) if len(command) > 1 else None
        if command[0] == "query":
            sock.connect(address)
            sock.send(b"salve")
            print("this should query the network")
        elif command[0] == "insert":
            sock.connect(address)
            sock.send(bytes(command_blob,encoding='utf-8'))
            response = sock.recv(1024)
            response = str(response, encoding='utf-8')
            print(response)
        elif command[0] == "close" or command == "quit":
            for address in locations.values():
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
    nodes = spawn_chord_nodes( n )

    run_client_interface()

    # Espero os processos terminarem (necessário?)
    for node in nodes:
        print(node.pid)
        node.join()
