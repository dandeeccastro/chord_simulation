import socket 
import sys 
import select 
from multiprocessing import Process 
import hashlib
import random

# Import temporário
import time

locations = dict()
N = None

def lookup_finger_table(target_id, node_id, finger_table):
    print('[lookup_finger_table] finger table to be checked: {0}'.format(list(finger_table.values())))
    node_values = list(finger_table.values())
    i = len(node_values) -1
    while i != 0:
        print('[lookup_finger_table] {0} <= {1} < {2}'.format(node_id,node_values[i],target_id))
        if node_id <= node_values[i] and node_values[i] < target_id:
            return node_values[i]
        i -= 1
    return node_values[0]

def string_to_address(x):
    x = x.split()
    return (x[0],int(x[1]))

def generate_sucessor(node_id):
    for node in list(sorted(locations.keys())):
        if node > node_id:
            return node
    return list(sorted(locations.keys()))[0]

def generate_predecessor(node_id):
    candidate = list(sorted(locations.keys()))[-1]
    for node in list(sorted(locations.keys())):
        if node < node_id:
            candidate = node
        elif node > node_id:
            break
    return candidate


def chord_node(identifier,location,NN):
    # Gerando as informações importantes para o nó
    hash_table = dict() # Tabela onde ficam as informações armazenadas nesse nó
    finger_table = dict() # Tabela onde fica a referência para os outros nós 
    sucessor = generate_sucessor(int(identifier))
    predecessor = generate_predecessor(int(identifier))

    for i in range(0,NN):
        node_id = identifier + 2**i
        node_id %= 2**NN
        finger_table[node_id] = generate_sucessor(node_id)

    sock = socket.socket()
    sock.bind(('localhost',location))
    sock.listen(1)
        
    print("[Node {0}] Sucessor is {1}".format(identifier,sucessor))

    while True:
        r,w,x = select.select([sock],[],[])
        for command in r:
            if command == sock:
                new_sock, addr = sock.accept()
                msg_blob = new_sock.recv(1024)
                msg_blob = str(msg_blob,encoding='utf-8')
                msg = msg_blob.split()

                if msg[0] == 'insert':
                    value = ' '.join(msg[2:])
                    sha1 = hashlib.sha1()
                    sha1.update(bytes(value,encoding='utf-8'))
                    hash_value = sha1.hexdigest()
                    hash_value = int(hash_value,16) % 2**NN

                    if predecessor <= hash_value and hash_value < identifier:
                        hash_table[hash_value] = value
                        new_sock.send(b"INSERTED")
                        print('[Node {0}] updated hash_table: {1}'.format(identifier,hash_table))

                    else:
                        # Aqui a gente seguiria com a busca, mas n rola por enquanto
                        forward_sock = socket.socket()
                        dest_node = lookup_finger_table(hash_value,identifier,finger_table)
                        print('[Node {0}] forwarding insert to {1}'.format(identifier,dest_node))
                        dest_info = string_to_address(locations[int(dest_node)])
                        forward_sock.connect(dest_info)
                        forward_sock.send(bytes('insert ' + str(dest_node) + ' ' + value,encoding='utf-8'))
                        response = forward_sock.recv(1024)
                        new_sock.send(response)
                        forward_sock.close()

                elif msg[0] == 'query':
                    if msg[2] == 'values':
                        result = ""
                        for item in hash_table:
                            result += str(item) + '\t' + str(hash_table[item]) + '\n'
                        new_sock.send(result.encode('utf-8'))

                    elif msg[2] == 'value':
                        value = ' '.join(msg[3:])
                        sha1 = hashlib.sha1()
                        sha1.update(bytes(value,encoding='utf-8'))
                        hash_value = sha1.hexdigest()
                        hash_value = int(hash_value,16) % 2**NN

                        if predecessor <= hash_value and hash_value < identifier:
                            response = hash_table[hash_value] 
                            new_sock.send(response.encode('utf-8'))

                        else:
                            # Aqui a gente seguiria com a busca, mas n rola por enquanto
                            forward_sock = socket.socket()
                            dest_node = lookup_finger_table(hash_value,identifier,finger_table)
                            print('[Node {0}] forwarding query to {1}'.format(identifier,dest_node))
                            dest_info = string_to_address(locations[int(dest_node)])
                            forward_sock.connect(dest_info)
                            forward_sock.send(bytes('query ' + str(dest_node) + ' value ' + value,encoding='utf-8'))
                            response = forward_sock.recv(1024)
                            new_sock.send(response)
                            forward_sock.close()

                new_sock.close()

def spawn_chord_nodes(n):

    # Variáveis que serão retornadas no fim da função mais outras de uso no loop
    spawn_array = []
    port = random.randint(4201,5000) 
    ports = [port]

    for i in range(0,n):
        # Gerando informações do nó que será gerado
        node_location = "localhost " + str(port)
        sha1 = hashlib.sha1()
        sha1.update(bytes(node_location,encoding='utf-8'))
        node_key = sha1.hexdigest()
        node_key = int(node_key,16) % 2**n
        locations[node_key] = node_location
        while port in ports:
            port = random.randint(4201,5000)
        ports.append(port)

    N = len(locations.values()) 
    for node_key in locations:
        # Gerando o nó com as informações geradas
        port = int(locations[node_key].split()[1])
        proc = Process(target=chord_node,args=(node_key,port,len(locations)))
        proc.start()

        # Atualizamos as informaçoes das estruturas de retorno 
        spawn_array.append(proc)

    return spawn_array

def run_client_interface():

    while True:
        sock = socket.socket()
        command_blob = input()
        command = command_blob.split()

        if command[0] == "query" or command[0] == 'insert':
            address = string_to_address(locations[int(command[1])]) if len(command) > 1 else None
            sock.connect(address)
            sock.send(command_blob.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            print(response)

        elif command[0] == "close" or command == "quit":
            for address in locations.values():
                sock.connect(string_to_address(address))
                sock.send(b"QUIT")
                msg = sock.recv(1024)
                msg = str(msg,encoding='utf-8')
                print(msg)
                sock = socket.socket()
            return 0

        elif command[0] == 'help':
            if len(command) == 1:
                print("Lista de comandos: insert, query, help")
                print("help <comando>: Mostra informações de uso do comando desejado. Se usado sozinho, mostra a lista de comandos disponíveis para uso")
            else:
                if command[1] == 'insert':
                    print("insert <id do nó> <valor a ser inserido>: Insere o valor na rede, iniciando o processo no nó escolhido")
                    print("Ao receber esse comando, o nó faz o hash do valor e roteia o valor até que ele chegue no nó que deve armazená-lo")
                    print("Para saber os ids de nó disponíveis, use o comando list")
                elif command[1] == 'query':
                    print("query <id do nó> <id da busca>: Pesquisa por algo no sistema, começando pelo ID especificado e de acordo com o ID de busca")
                    print("IDs de busca disponíveis: \n\t- values: mostra os valores armazenados em um nó específico")
                    print("\t- value <valor a ser pesquisado>: pesquisa pelo valor nos nós da rede, roteando a requisição se necessário")
                elif command[1] == 'list':
                    print("list: Lista os IDs disponíveis para serem usados")
                else:
                    print("{0}: Comando não reconhecido no sistema".format(command[1]))

        elif command[0] == 'list':
            result = ''
            for node in locations.keys():
                result = result + str(node) + ' '
            print(result)

        del sock

if __name__ == "__main__":
    # Spawno n processos 
    n = int(input("Insira o número de nós que quer na sua rede: "))
    nodes = spawn_chord_nodes( n )

    print('[Client] {0}'.format(list(locations.keys())))
    run_client_interface()

    # Espero os processos terminarem (necessário?)
    for node in nodes:
        print(node.pid)
        node.join()
