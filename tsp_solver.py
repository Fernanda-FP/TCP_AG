import sys
import math
import random 
import time
import signal

#aumentando limite de recursão para lidar com grafos grandoes
sys.setrecursionlimit(2000)

#lendo dados de entrada no formato TSPLIB
def ler_instancia_tsp():
    entrada = sys.stdin.read().strip().splitlines()

    nome = "Desconhecido"
    dimensao = 0
    coordenadas = []
    lendo_coordenadas = False

    for linha in entrada:
        linha = linha.strip()
        if not linha or linha == "EOF":
            continue

        if linha.startswith("NAME"):
            nome = linha.split(":")[1].strip()
        elif linha.startswith("DIMENSION"):
            dimensao = int(linha.split(":")[1].strip())
        elif linha.startswith("NODE_COORD_SECTION"):
            lendo_coordenadas = True
            continue
    
        if lendo_coordenadas:
            partes = linha.split()
            if len(partes) >= 3:
                x = float(partes[1])
                y = float(partes[2])
                coordenadas.append((x, y))

    return nome, dimensao, coordenadas

#calculando matriz de distâncias usando distância euclidiana arredondada para o inteiro mais próximo
def calcular_matriz_distancias(n_cidades, coordenadas):

    dist_matrix = [[0] * n_cidades for _ in range(n_cidades)]

    for i in range(n_cidades):

        for j in range(i + 1, n_cidades):
            xd = coordenadas[i][0] - coordenadas[j][0]
            yd = coordenadas[i][1] - coordenadas[j][1]
            rij = math.sqrt(xd*xd + yd*yd)
            dij = int(math.floor(rij + 0.5))
            
            dist_matrix[i][j] = dij
            dist_matrix[j][i] = dij
            
    return dist_matrix

#classe representando uma formiga na metaheuristica ACO
class Ant: 

    def __init__(self, n_cidades, alfa, beta):
        self.n_cidades = n_cidades
        self.alfa = alfa #peso do feromonio
        self.beta = beta #peso da distnacia
        self.rota = []
        self.distancia_total = 0.0
    
    def percorrer_rota (self, matriz_dist, matriz_feromonio):
        self.rota = [0] # comecam na cidade 0
        self.distancia_total = 0
        nao_visitadas = set(range(1, self.n_cidades))
        atual = 0

        #construindo a rota da formiga passo a passo
        while nao_visitadas:

            candidatos = list(nao_visitadas)
            pesos = []
            #avalia a probabilidade de escolher cada cidade candidata com base no feromonio e na distancia
            for proxima in candidatos:
                f = matriz_feromonio[atual][proxima]
                #evitando divisão por zero, adicionando um pequeno valor a distancia
                d = 1.0 / (matriz_dist[atual][proxima] + 1e-9) 
                #calculando o peso da escolha usando a formula do ACO
                pesos.append((f ** self.alfa) * (d ** self.beta))
            
            soma = sum(pesos)
            if soma == 0:
                proxima = random.choice(candidatos)
            else:
                #escolhendo a proxima cidade com base na probabilidade calculada
                r = random.uniform(0, soma)
                acumulado = 0
                for i, p in enumerate(pesos):
                    acumulado += p
                    if acumulado >= r:
                        proxima = candidatos[i]
                        break
            self.distancia_total += matriz_dist[atual][proxima]
            self.rota.append(proxima)
            nao_visitadas.remove(proxima)
            atual = proxima
            
        #fechando o ciclo de volta para a cidade inicial
        self.distancia_total += matriz_dist[self.rota[-1]][self.rota[0]]

def imprimir_solucao(nome, custo, rota):
    print(f"NAME: {nome}")
    print("COMMENT: Equipe Nos trupica mas nao cai - Algoritmo ACO")
    print("TYPE: TOUR")
    print(f"DIMENSION: {len(rota)}")
    print(f"TOTAL WEIGHT: {custo}")
    print("TOUR_SECTION")
    for cidade in rota:
        print(cidade + 1) 
    print("EOF")

#variaveis globais para armazenar a melhor solucao encontrada, permitindo que seja salva em caso de interrupcao
melhor_distancia = float('inf')
melhor_rota = []
nome_instancia  = "Desconecido"

#funcao para salvar a melhor solucao encontrada em caso de interrupcao do programa
def salva_vidas(sig, frame):
    if melhor_rota:
        imprimir_solucao(nome_instancia, int(melhor_distancia), melhor_rota)
    sys.exit(0)


if __name__ == "__main__":
    #registrando o handler para sinais de interrupcao, permitindo salvar a melhor solucao encontrada antes de sair
    signal.signal(signal.SIGINT, salva_vidas) 
    signal.signal(signal.SIGTERM, salva_vidas)
    
    #passo 1: leitura da instancia e processamento dos dados de entrada
    nome_instancia, n_cidades, coordenadas = ler_instancia_tsp()

    if n_cidades == 0:
        sys.exit(1)
    
    matriz_dist = calcular_matriz_distancias(n_cidades, coordenadas)

    #passo 2: configuracao dos parametros do algoritmo ACO e inicializacao da matriz de feromonio
    matriz_feromonio = [[1.0] * n_cidades for _ in range(n_cidades)]

    alfa = 1.0
    beta = 3.0
    rho = 0.1

    tempo_inicial = time.time()
    tempo_maximo = 14.5 

    #passo 3: loop principal do algoritmo ACO, onde as formigas constroem suas rotas, o feromonio eh atualizado, 
    # e a melhor solucao encontrada eh armazenada
    while time.time() - tempo_inicial < tempo_maximo:
        #criando um grupo de formigas para explorar o espaco de solucoes
        formigas = [Ant(n_cidades, alfa, beta) for _ in range(10)]
        
        #cada formiga constoi sua rota
        for formiga in formigas:
            formiga.percorrer_rota(matriz_dist, matriz_feromonio)
            #atualizando a melhor solucao encontrada se a formiga atual tiver uma rota melhor
            if formiga.distancia_total < melhor_distancia:
                melhor_distancia = formiga.distancia_total
                melhor_rota = formiga.rota.copy()
        
        #atualizando a matriz de feromonio com base nas rotas construidas pelas formigas
        #  evaporando o feromonio antigo e depositando novo feromonio nas rotas melhores
        for i in range(n_cidades):
            for j in range(n_cidades):
                matriz_feromonio[i][j] *= (1.0 - rho)

        #depositando feromonio nas rotas construidas pelas formigas
        for formiga in formigas:
            deposito = 100.0 / formiga.distancia_total
            rota_f = formiga.rota

            #marcando o caminho de ida e volta
            for k in range(n_cidades - 1):
                u, v = rota_f[k], rota_f[k+1]
                matriz_feromonio[u][v] += deposito
                matriz_feromonio[v][u] += deposito
            #fechando o ciclo de volta para a cidade inicial
            u, v = rota_f[-1], rota_f[0]
            matriz_feromonio[u][v] += deposito
            matriz_feromonio[v][u] += deposito
            
    #passo 4: impressao da melhor solucao encontrada no formato exigido 
    imprimir_solucao(nome_instancia, int(melhor_distancia), melhor_rota)#