# TODO List do Projeto de Implementação do CHORD

## Requerimentos do Sistema

- Tabela hash de sistema imutável
- Anel de nós com $2^n$ nós
- Cada nó i sabe seu sucessor e a tabela finger

- Execução da tabela hash distribuída em uma máquina
	- O processo cliente recebe como entrada o valor de n
	- Abre portas distintas para cada nó
	- Dispara um processo filho pra simular cada nó

- Inserção de pares chave/valor
	- Tem que ser inserido no primeiro nó com ID maior ou igual ao valor hash gerado a partir da chave 
	- Operação insere(nóOrigem, chave, valor) deve ser implementada, onde o nó origem é o nó para o qual o cliente está fazendo a solicitação
	- O nó origem que receber o par chave valor vai hashear a chave e rotear ela para o nó que merece recebê-la

- Busca por chaves  
	- Operação tem padrão busca(idBusca, nóOrigem, chave)
		- idBusca: tipo de busca
		- nóOrigem: o nó que o cliente tá mandando requisição
		- chave: a chave a ser procurada

- Interface de interação com a rede chord será feita via aplicação cliente principal
	- Ou seja, quem insere e consulta é a aplicação principal

- ATENÇÃO: eu não entendi essa frase do doc
	- "As inserções e consultas deverão ser encaminhadas diretamente para o nó de origem (sem passar pelo programa principal)."
