"""
Vocabulário lógico do sistema: variáveis, fatos e regras (predicados).
Todos os módulos de regras fazem:  from ...variaveis_e_predicados import *
"""
from pyDatalog import pyDatalog

# Variáveis (maiúsculas)
pyDatalog.create_terms("P, T, V, CT, CP, CTT, DT, DD, DP, M, Q, KM, QL, KL, X, LIM, F, A, D, DA, CA")

# Fatos (preenchidos por config_dados.py)
pyDatalog.create_terms(
    "pedido, preco, custo_produto, custo_proprio, prazo_proprio, "
    "prazo_prometido, prioridade, quantidade, distancia, "
    "custo_terc, prazo_terc, margem_minima, folga_minima, "
    "qtd_pequena, dist_longa, variacao_mercado, limite_variacao, "
    "atraso_obra, custo_rota_alt, prazo_rota_alt"
)

# Regras (definidas em subcampos/)
pyDatalog.create_terms(
    "inviavel_proprio, propria_margem_ok, terceira_margem_ok, "
    "propria_no_prazo, terceira_no_prazo, prazo_estourado, avaliar_expressa, "
    "prazo_apertado, priorizar_velocidade, consolidar, reavaliar_rotas, "
    "propria_ok, terceira_ok, recomendar_terceirizar, tem_opcao_ok, alerta_margem, "
    "prazo_efetivo, tem_obra, obra_estoura_prazo, alternativa_mais_rapida, "
    "alternativa_margem_ok, alternativa_no_prazo, rota_alt_ok, "
    "recomendar_rota_alternativa"
)
