from pyDatalog import pyDatalog

#ROTEIRO DO VIDEO
#PARTE 1: COMO OPERAR E MANIPULAR VALORES

#cria os termos lógicos
#LETRAS MAISCULAS PARA NAO DAR ERRO
pyDatalog.create_terms('X, Y, double')

print("Declaração de valores no Pytdatalog: ")
print((X == 1) & (Y == 6))

#PARTE 2: COMO OPERAR E MANIPULAR FUNÇOES
print("funções no Pytdatalog: ")
def double(a):
    return a*2

print((X ==2) & (Y == double(33)))

#PARTE3: COMO EXECUTAR LOOPS
print("Loop no Pytdatalog: ")
print(X.in_(range(6)))

#PARTE4: COMO USAR A PARTE LOGICA PARA FAZER UM SISTEMA ESPECIALISTA
#Exemplo: Escolhendo Roupas

# Definir predicados e variáveis
pyDatalog.create_terms('recomendacao, oque_vestir, Clima, Roupa')

#base de conhecimento)

#usar fato e remover o fato para garantir que operação realize corretamente
#fato temporario pois pydatalog pode crachar
+ recomendacao('dummy','dummy')
- recomendacao('dummy','dummy')

+ recomendacao('frio', 'casaco')
+ recomendacao('calor', 'camiseta')
+ recomendacao('chuva', 'capa_de_chuva')
#da pra usar - para remover fatos já definidos, como no comentario abaixo
#- recomendacao('frio', 'casaco')

#regra de inferência
oque_vestir(Clima, Roupa) <= recomendacao(Clima, Roupa)

#testes de consulta
print()
print("RESULTADOS Sistema Especialista simples: ")
print("No Frio:", oque_vestir('frio', Roupa), "\n\n")
print("No Calor:", oque_vestir('calor', Roupa), "\n\n")
print("Na Chuva:", oque_vestir('chuva', Roupa), "\n")

#PARTE5: FUNCOES NO PYDATALOG
#criando termos
pyDatalog.create_terms('cidade, X')

# Atribuindo a cidade de cada time
cidade['arsenal'] = 'londres'
cidade['chelsea'] = 'londres'
cidade['liverpool'] = 'liverpool'
cidade['manchester_city'] = 'manchester'

# Consultando a cidade do Arsenal
print(cidade['arsenal'] == X)

