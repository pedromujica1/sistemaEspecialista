#Alunos: Pedro Miotto Mujica, Vinicius Castaman Giongo, Gabriel Costa, Pedro Moraes
#python main.py          -> menu interativo
#python main.py --demo   -> roda pedidos de exemplo

import sys
from pyDatalog import pyDatalog
from base_conhecimento.config_dados import (
    Pedido, LIMITE_VARIACAO, carregar_parametros, carregar_pedido)
import base_conhecimento  # noqa: F401  (registra as regras)


#motor de decisção
def vale(consulta: str) -> bool:
    return pyDatalog.ask(consulta) is not None


#calculo da margem de lucro
def margem_pct(p: Pedido, frete: float) -> float:
    return (p.preco - p.custo_produto - frete) / p.preco

#função para decidir
def decidir(p: Pedido, custo_prop, prazo_prop, custo_alt, prazo_alt):
    pid, log, opcoes = p.id, [], []

    if vale(f"propria_ok('{pid}')"):
        opcoes.append(("FROTA PRÓPRIA", custo_prop, prazo_prop))
        
    if vale(f"tem_obra('{pid}')") and vale(f"rota_alt_ok('{pid}')"):
        opcoes.append(("FROTA PRÓPRIA (rota alternativa)", custo_alt, prazo_alt))
    
    r = pyDatalog.ask(f"terceira_ok('{pid}', T)")
    
    if r:
        for (nome,) in r.answers:
            frete, prazo = p.transportadoras[nome]
            opcoes.append((f"TERCEIRA: {nome}", frete, prazo))

    if vale(f"inviavel_proprio('{pid}')"):
        log.append("R1: frota própria inviável (margem mínima violada).")
        r2 = pyDatalog.ask(f"recomendar_terceirizar('{pid}', T)")
        
        if r2:
            log.append("R2: terceirizar possível com: " + ", ".join(t for (t,) in r2.answers) + ".")
    
    if vale(f"tem_obra('{pid}')"):
        log.append(f"R7: obra na pista: atraso de {p.atraso_obra_dias} dia(s) "
                   f"-> prazo da rota principal passa a {prazo_prop} dia(s).")
        
        if vale(f"obra_estoura_prazo('{pid}')"):
            log.append(f"R7: a obra faz estourar o prazo prometido " f"({p.prazo_dias} dia(s)).")
        
        if p.distancia_alt_km > 0:
            if vale(f"recomendar_rota_alternativa('{pid}')"):
                log.append(f"R7: rota alternativa ({p.distancia_alt_km:.0f} km, " f"{prazo_alt} dia(s)) é mais rápida e respeita " f"margem e prazo -> candidata ao desvio.")
            else:
                log.append("R7: rota alternativa comparada, mas não compensa " "(não é mais rápida ou viola margem/prazo).")
        
        else:
            log.append("R7: não há rota alternativa cadastrada para comparar.")
    if vale(f"avaliar_expressa('{pid}')"):
        log.append("R3: prazo de deslocamento > prazo prometido -> " "avaliar expressa/terceirizada.")
    
    if vale(f"priorizar_velocidade('{pid}')"):
        log.append("R4: cliente prioritário + prazo apertado -> " "priorizar velocidade (margem sempre >= mínima).")
    
    if vale(f"consolidar('{pid}')"):
        log.append("R5: quantidade pequena + distância grande -> " "consolidar carga com outros pedidos.")

    if not opcoes:
        return None, log
    
    if vale(f"priorizar_velocidade('{pid}')"):
        return min(opcoes, key=lambda o: (o[2], o[1])), log
    return min(opcoes, key=lambda o: o[1]), log

#funçao de processamento de pedidos
def processar(p: Pedido):
    cp, dp, ca, da = carregar_pedido(p)
    escolha, log = decidir(p, cp, dp, ca, da)
    print(f"\n=== Pedido {p.id} (prioridade {p.prioridade}) ===")
    for linha in log:
        print("  -", linha)
    if escolha:
        nome, frete, prazo = escolha
        print(f"  >> RECOMENDAÇÃO: {nome} | frete R$ {frete:.2f} | "
              f"prazo {prazo} dia(s) | margem {margem_pct(p, frete):.1%}")
    if vale(f"alerta_margem('{p.id}')"):
        print("  !! ALERTA: nenhuma opção preserva a margem mínima. "
              "Renegociar preço/frete ou consolidar carga.")


def avisar_mercado():
    r6 = pyDatalog.ask("reavaliar_rotas(X)")
    if r6:
        print(f"[R6] Variação de mercado {r6.answers[0][0]:.0%} acima do " f"limite {LIMITE_VARIACAO:.0%}: REAVALIAR ROTAS.")


#demonstraçao CLI
def demo():
    carregar_parametros(variacao_mercado_atual=0.12)
    avisar_mercado()
    
    '''id, preco, custo_produto, qtdade, distancia_km prazo_dias, prioridade, transportadores, atraso_obra_dias, distancia_alt_km'''
    processar(Pedido("P1", 10000, 6000, 200, 300, 3, "media", {"TransRapida": (900, 2), "LogBarato": (700, 5)}))
    processar(Pedido("P2", 5000, 3800, 20, 900, 2, "alta",{"TransRapida": (600, 1)}))
    # Obra na pista: +3 dias na rota principal; alternativa de 700 km
    processar(Pedido("P3", 12000, 6000, 300, 450, 2, "media",{"LogBarato": (1500, 4)},atraso_obra_dias=3, distancia_alt_km=700))


def ler(msg, tipo=str):
    while True:
        try:
            return tipo(input(msg).strip())
        except ValueError:
            print("  valor inválido, tente de novo.")


def interativo():
    var = ler("Variação atual de combustível/frete (ex.: 0.12 = 12%): ", float)#type: ignore
    carregar_parametros(var) #type: ignore
    avisar_mercado()
    n = 0
    while True:
        n += 1
        pid = f"P{n}"
        print(f"\n--- Novo pedido {pid} ---")
        transp = {}
        preco_ = ler("Preço de venda (R$): ", float) #type: ignore
        custo = ler("Custo dos produtos (R$): ", float) #type: ignore
        qtd = ler("Quantidade: ", int) #type: ignore
        dist = ler("Distância até o destino (km): ", float) #type: ignore
        prazo = ler("Prazo prometido (dias): ", int) #type: ignore
        prio = ler("Prioridade (alta/media/baixa): ").lower()
        atraso = ler("Atraso por obra na pista, em dias (0 = sem obra): ", int) #type: ignore
        dist_alt = 0.0
        if atraso > 0: #type: ignore
            dist_alt = ler("Distância da rota alternativa em km (0 = não há): ", float) #type: ignore
        while input("Cadastrar transportadora parceira? (s/n): ").lower() == "s":
            nome = ler("  Nome: ")
            transp[nome] = (ler("  Frete (R$): ", float), ler("  Prazo (dias): ", int)) #type: ignore
        processar(Pedido(pid, preco_, custo, qtd, dist, prazo, prio, transp,atraso, dist_alt)) #type: ignore
        if input("\nOutro pedido? (s/n): ").lower() != "s":
            break


if __name__ == "__main__":
    demo() if "--demo" in sys.argv else interativo()
