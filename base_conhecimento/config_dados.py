#Alunos: Pedro Miotto Mujica, Vinicius Castaman Giongo, Gabriel Costa, Pedro Moraes
#Dados de entrada: parâmetros de negócio, modelo de Pedido e carga de fatos.

from dataclasses import dataclass, field
from base_conhecimento.variaveis_e_predicados import *

#Parametros do Negocio
MARGEM_MINIMA = 0.15 #15 % sobre o preço
FOLGA_MINIMA_DIAS = 1 #prazo "apertado" se sobrar <= 1 dia
QTD_PEQUENA = 50 #unidades
DIST_LONGA_KM = 400 #km
LIMITE_VARIACAO = 0.10 # X% de alta em combustível/frete
CUSTO_KM_PROPRIO = 3.20 #R$/km (frota própria)
VELOCIDADE_MEDIA_KM_DIA = 500 #km/dia (frota própria)


@dataclass
class Pedido:
    id: str
    preco: float                 #preço de venda total
    custo_produto: float         #custo total dos produtos
    quantidade: int
    distancia_km: float
    prazo_dias: int              # prazo prometido ao cliente
    prioridade: str              # 'alta' | 'media' | 'baixa'
    transportadoras: dict = field(default_factory=dict)  # {nome: (frete, prazo)}
    atraso_obra_dias: int = 0      # atraso por obra na pista (0 = sem obra)
    distancia_alt_km: float = 0.0  # rota alternativa (0 = não existe)


def carregar_parametros(variacao_mercado_atual: float = 0.0):
    + margem_minima(MARGEM_MINIMA) #type: ignore
    + folga_minima(FOLGA_MINIMA_DIAS) #type: ignore
    + qtd_pequena(QTD_PEQUENA) #type: ignore
    + dist_longa(DIST_LONGA_KM) #type: ignore
    + limite_variacao(LIMITE_VARIACAO) #type: ignore
    + variacao_mercado(variacao_mercado_atual) #type: ignore


def carregar_pedido(p: Pedido):
    custo_prop = p.distancia_km * CUSTO_KM_PROPRIO
    prazo_prop = int(-(-p.distancia_km // VELOCIDADE_MEDIA_KM_DIA))  #type: ignore
    + pedido(p.id) #type: ignore
    + preco(p.id, p.preco) #type: ignore
    + custo_produto(p.id, p.custo_produto) #type: ignore
    + custo_proprio(p.id, custo_prop) #type: ignore
    + prazo_proprio(p.id, prazo_prop) #type: ignore
    + prazo_prometido(p.id, p.prazo_dias) #type: ignore
    + prioridade(p.id, p.prioridade) #type: ignore
    + quantidade(p.id, p.quantidade) #type: ignore
    + distancia(p.id, p.distancia_km) #type: ignore
    for nome, (frete, prazo) in p.transportadoras.items():
        + custo_terc(p.id, nome, frete) #type: ignore
        + prazo_terc(p.id, nome, prazo) #type: ignore
    # Obra na pista (R7): atraso sempre registrado (0 = sem obra)
    + atraso_obra(p.id, p.atraso_obra_dias) #type: ignore
    prazo_efetivo_ = prazo_prop + p.atraso_obra_dias

    # Rota alternativa; sem alternativa => valores proibitivos (nunca é escolhida)
    if p.distancia_alt_km > 0:
        custo_alt = p.distancia_alt_km * CUSTO_KM_PROPRIO
        prazo_alt = int(-(-p.distancia_alt_km // VELOCIDADE_MEDIA_KM_DIA))
    else:
        custo_alt, prazo_alt = 1e12, 10**6
    + custo_rota_alt(p.id, custo_alt) # type: ignore
    + prazo_rota_alt(p.id, prazo_alt) #type: ignore
    return custo_prop, prazo_efetivo_, custo_alt, prazo_alt
