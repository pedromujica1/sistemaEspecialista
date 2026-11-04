#Alunos: Pedro Miotto Mujica, Vinicius Castaman Giongo, Gabriel Costa, Pedro Moraes
"""
Base de regras do Sistema Especialista (pyDatalog).

Seções: viabilidade/margem (R1) · prazo e prioridade (R3, R4) ·
consolidação (R5) · mercado (R6) · obra e rota alternativa (R7) ·
recomendação final (R2 + alerta de margem)
"""
from base_conhecimento.variaveis_e_predicados import *


#VIABILIDADE / MARGEM — Regra 1
#R1: rota inviável com meios próprios (custo próprio + produto > preço × (1 − margem))
inviavel_proprio(P) <= (custo_proprio(P, CT) & custo_produto(P, CP) & preco(P, V) & margem_minima(M) & (CT + CP > V * (1 - M)))# type: ignore

propria_margem_ok(P) <= (custo_proprio(P, CT) & custo_produto(P, CP) & preco(P, V) & margem_minima(M) & (CT + CP <= V * (1 - M))) # type: ignore

terceira_margem_ok(P, T) <= (custo_terc(P, T, CTT) & custo_produto(P, CP) & preco(P, V) & margem_minima(M) & (CTT + CP <= V * (1 - M))) # type: ignore

#PRAZO E PRIORIDADE — Regras 3 e 4
#Prazo da rota principal = deslocamento + atraso de obra (0 se não há)
prazo_efetivo(P, D) <= (prazo_proprio(P, DD) & atraso_obra(P, A) & (D == DD + A)) # type: ignore

propria_no_prazo(P) <= (prazo_efetivo(P, DD) & prazo_prometido(P, DP) & (DD <= DP)) # type: ignore

terceira_no_prazo(P, T) <= (prazo_terc(P, T, DT) & prazo_prometido(P, DP) & (DT <= DP)) # type: ignore

#R3: deslocamento > prazo prometido => avaliar expressa/terceirizada
prazo_estourado(P) <= (prazo_efetivo(P, DD) & prazo_prometido(P, DP) & (DD > DP)) # type: ignore
avaliar_expressa(P) <= prazo_estourado(P) # type: ignore

#R4: prioridade alta + prazo apertado => priorizar velocidade
prazo_apertado(P) <= (prazo_efetivo(P, DD) & prazo_prometido(P, DP) & folga_minima(F) & (DP - DD <= F)) # type: ignore
priorizar_velocidade(P) <= prioridade(P, 'alta') & prazo_apertado(P) # type: ignore

#CONSOLIDAÇÃO DE CARGA — Regra 5
consolidar(P) <= (quantidade(P, Q) & distancia(P, KM) & qtd_pequena(QL) & dist_longa(KL) & (Q < QL) & (KM > KL)) # type: ignore

#MERCADO (combustível/frete) — Regra 6
reavaliar_rotas(X) <= variacao_mercado(X) & limite_variacao(LIM) & (X > LIM) # type: ignore

#OBRA NA PISTA E ROTA ALTERNATIVA — Regra 7
#SE tem obra ENTÃO calcula o atraso e compara com outra rota
tem_obra(P) <= atraso_obra(P, A) & (A > 0) # type: ignore

obra_estoura_prazo(P) <= (tem_obra(P) & prazo_efetivo(P, D) & prazo_prometido(P, DP) & (D > DP)) # type: ignore

alternativa_mais_rapida(P) <= prazo_efetivo(P, D) & prazo_rota_alt(P, DA) & (DA < D) # type: ignore

alternativa_margem_ok(P) <= (custo_rota_alt(P, CA) & custo_produto(P, CP) & preco(P, V) & margem_minima(M) & (CA + CP <= V * (1 - M))) # type: ignore
alternativa_no_prazo(P) <= prazo_rota_alt(P, DA) & prazo_prometido(P, DP) & (DA <= DP) # type: ignore
rota_alt_ok(P) <= alternativa_margem_ok(P) & alternativa_no_prazo(P) # type: ignore

recomendar_rota_alternativa(P) <= (tem_obra(P) & alternativa_mais_rapida(P) & rota_alt_ok(P)) # type: ignore

#RECOMENDAÇÃO FINAL — Regra 2 + alerta de margem
#Opção válida = respeita margem mínima E prazo prometido
propria_ok(P) <= propria_margem_ok(P) & propria_no_prazo(P) # type: ignore
terceira_ok(P, T) <= terceira_margem_ok(P, T) & terceira_no_prazo(P, T) # type: ignore

#R2: própria inviável + parceira que cabe no prazo => terceirizar
recomendar_terceirizar(P, T) <= inviavel_proprio(P) & terceira_ok(P, T) # type: ignore

#Alerta: nenhuma opção preserva a margem mínima
tem_opcao_ok(P) <= propria_ok(P) # type: ignore
tem_opcao_ok(P) <= terceira_ok(P, T) # type: ignore
tem_opcao_ok(P) <= tem_obra(P) & rota_alt_ok(P) # type: ignore
alerta_margem(P) <= pedido(P) & ~tem_opcao_ok(P) # type: ignore
