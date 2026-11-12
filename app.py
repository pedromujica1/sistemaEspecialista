#Alunos: Pedro Miotto Mujica, Vinicius Castaman Giongo, Gabriel Costa, Pedro Moraes
#python app.py  -> abre a interface em http://localhost:5000

from flask import Flask, jsonify, render_template, request
from base_conhecimento.config_dados import (
    Pedido, MARGEM_MINIMA, FOLGA_MINIMA_DIAS, QTD_PEQUENA, DIST_LONGA_KM,
    LIMITE_VARIACAO, CUSTO_KM_PROPRIO, VELOCIDADE_MEDIA_KM_DIA,
    carregar_parametros, trocar_variacao_mercado, carregar_pedido, descarregar_pedido)
from main import decidir, margem_pct, vale

ID_PEDIDO = "WEB"
PRIORIDADES = ("alta", "media", "baixa")

PARAMETROS = [
    ("Margem mínima", f"{MARGEM_MINIMA:.0%}"),
    ("Frota própria", f"R$ {CUSTO_KM_PROPRIO:.2f}/km".replace(".", ",")),
    ("Velocidade média", f"{VELOCIDADE_MEDIA_KM_DIA} km/dia"),
    ("Prazo apertado", f"folga ≤ {FOLGA_MINIMA_DIAS} dia"),
    ("Carga pequena", f"< {QTD_PEQUENA} unidades"),
    ("Distância longa", f"> {DIST_LONGA_KM} km"),
    ("Limite de variação", f"{LIMITE_VARIACAO:.0%}"),
]

app = Flask(__name__)
carregar_parametros()


def numero(dados, campo, nome, tipo=float):
    try:
        valor = tipo(dados.get(campo, 0))
    except (TypeError, ValueError):
        raise ValueError(f"{nome}: valor inválido")
    if valor < 0:
        raise ValueError(f"{nome} não pode ser negativo")
    return valor


def ler_pedido(dados):
    preco = numero(dados, "preco", "Preço de venda")
    if preco == 0:
        raise ValueError("Preço de venda deve ser maior que zero")

    prioridade = dados.get("prioridade")
    if prioridade not in PRIORIDADES:
        raise ValueError("Prioridade inválida")

    transportadoras = {}
    for t in dados.get("transportadoras", []):
        nome = str(t.get("nome", "")).strip()
        if not nome:
            raise ValueError("Toda transportadora precisa de um nome")
        if nome in transportadoras:
            raise ValueError(f"Transportadora repetida: {nome}")
        transportadoras[nome] = (numero(t, "frete", f"Frete de {nome}"),
                                 numero(t, "prazo", f"Prazo de {nome}", int))

    return Pedido(ID_PEDIDO, preco,
                  numero(dados, "custo_produto", "Custo dos produtos"),
                  numero(dados, "quantidade", "Quantidade", int),
                  numero(dados, "distancia_km", "Distância"),
                  numero(dados, "prazo_dias", "Prazo prometido", int),
                  prioridade, transportadoras,
                  numero(dados, "atraso_obra_dias", "Atraso por obra", int),
                  numero(dados, "distancia_alt_km", "Distância da rota alternativa"))


def opcao_json(p, opcao):
    modal, frete, prazo = opcao
    return {"modal": modal, "frete": frete, "prazo": prazo, "margem": margem_pct(p, frete)}


@app.get("/")
def index():
    return render_template("index.html", parametros=PARAMETROS)


@app.post("/api/avaliar")
def avaliar():
    dados = request.get_json(silent=True) or {}
    try:
        p = ler_pedido(dados)
        variacao = numero(dados, "variacao_mercado", "Variação de mercado")
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400

    trocar_variacao_mercado(variacao)
    custos = carregar_pedido(p)
    try:
        escolha, opcoes, log = decidir(p, *custos)
        regras = [dict(zip(("codigo", "texto"), linha.split(": ", 1))) for linha in log]
        resposta = {
            "recomendacao": opcao_json(p, escolha) if escolha else None,
            "opcoes": [opcao_json(p, o) | {"escolhida": o == escolha} for o in opcoes],
            "criterio": "velocidade" if vale(f"priorizar_velocidade('{p.id}')") else "custo",
            "regras": regras,
            "reavaliar_rotas": vale("reavaliar_rotas(X)"),
            "alerta_margem": vale(f"alerta_margem('{p.id}')"),
        }
    finally:
        descarregar_pedido(p)
    return jsonify(resposta)


if __name__ == "__main__":
    # threaded=False: o pyDatalog guarda as regras por thread, então todas
    # as requisições precisam rodar na mesma thread em que as regras foram carregadas
    app.run(threaded=False)
