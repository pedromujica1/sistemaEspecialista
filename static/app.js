const form = document.querySelector("#form-pedido");
const listaTransportadoras = document.querySelector("#transportadoras");
const modeloTransportadora = document.querySelector("#linha-transportadora");
const resultado = document.querySelector("#resultado");

const reais = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
const porcento = new Intl.NumberFormat("pt-BR", { style: "percent", maximumFractionDigits: 1 });

// Mesmos pedidos do "python main.py --demo"
const exemplos = {
  P1: {
    preco: 10000, custo_produto: 6000, quantidade: 200, distancia_km: 300, prazo_dias: 3,
    prioridade: "media", atraso_obra_dias: 0, distancia_alt_km: 0, variacao_mercado: 12,
    transportadoras: [{ nome: "TransRapida", frete: 900, prazo: 2 }, { nome: "LogBarato", frete: 700, prazo: 5 }],
  },
  P2: {
    preco: 5000, custo_produto: 3800, quantidade: 20, distancia_km: 900, prazo_dias: 2,
    prioridade: "alta", atraso_obra_dias: 0, distancia_alt_km: 0, variacao_mercado: 12,
    transportadoras: [{ nome: "TransRapida", frete: 600, prazo: 1 }],
  },
  P3: {
    preco: 12000, custo_produto: 6000, quantidade: 300, distancia_km: 450, prazo_dias: 2,
    prioridade: "media", atraso_obra_dias: 3, distancia_alt_km: 700, variacao_mercado: 12,
    transportadoras: [{ nome: "LogBarato", frete: 1500, prazo: 4 }],
  },
};

function el(tag, classe, texto) {
  const elemento = document.createElement(tag);
  if (classe) elemento.className = classe;
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}

function adicionarTransportadora(dados = {}) {
  const linha = modeloTransportadora.content.firstElementChild.cloneNode(true);
  for (const campo of linha.querySelectorAll("[data-campo]")) {
    campo.value = dados[campo.dataset.campo] ?? "";
  }
  linha.querySelector(".remover").addEventListener("click", () => linha.remove());
  listaTransportadoras.append(linha);
}

function preencher(pedido) {
  for (const [nome, valor] of Object.entries(pedido)) {
    if (form.elements[nome]) form.elements[nome].value = valor;
  }
  listaTransportadoras.replaceChildren();
  pedido.transportadoras.forEach(adicionarTransportadora);
}

function lerPedido() {
  const campos = Object.fromEntries(new FormData(form));
  const pedido = {};
  for (const [nome, valor] of Object.entries(campos)) {
    pedido[nome] = nome === "prioridade" ? valor : Number(valor);
  }
  pedido.variacao_mercado /= 100;
  pedido.transportadoras = [...listaTransportadoras.querySelectorAll(".transportadora")].map((linha) => ({
    nome: linha.querySelector('[data-campo="nome"]').value,
    frete: Number(linha.querySelector('[data-campo="frete"]').value),
    prazo: Number(linha.querySelector('[data-campo="prazo"]').value),
  }));
  return pedido;
}

function mostrarRecomendacao(r) {
  const bloco = el("div", "mt-3");
  if (!r.recomendacao) {
    bloco.append(el("p", "rounded border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900",
      "Nenhuma opção preserva a margem mínima e o prazo prometido. " +
      "Renegociar preço/frete ou consolidar a carga."));
    return bloco;
  }
  const { modal, frete, prazo, margem } = r.recomendacao;
  bloco.append(
    el("p", "text-xl font-semibold text-blue-800", modal),
    el("p", "mt-1 text-sm", `Frete ${reais.format(frete)} · ${prazo} dia(s) · margem ${porcento.format(margem)}`),
    el("p", "mt-1 text-xs text-slate-500", r.criterio === "velocidade"
      ? "Critério: mais rápida (cliente prioritário com prazo apertado)."
      : "Critério: menor custo entre as opções válidas."),
  );
  return bloco;
}

function mostrarRegras(regras) {
  const bloco = el("div", "mt-5");
  bloco.append(el("h3", "text-sm font-semibold", "Regras disparadas"));
  if (!regras.length) {
    bloco.append(el("p", "mt-1 text-sm text-slate-500", "Nenhuma restrição disparada."));
    return bloco;
  }
  const lista = el("ul", "mt-2 space-y-1.5 text-sm");
  for (const { codigo, texto } of regras) {
    const item = el("li", "flex gap-2");
    item.append(
      el("span", "shrink-0 rounded bg-slate-100 px-1.5 font-mono text-xs leading-5 text-slate-600", codigo),
      el("span", "", texto.replaceAll("->", "→")),
    );
    lista.append(item);
  }
  bloco.append(lista);
  return bloco;
}

function mostrarOpcoes(opcoes) {
  const bloco = el("div", "mt-5");
  bloco.append(el("h3", "text-sm font-semibold", "Opções válidas"));
  if (!opcoes.length) {
    bloco.append(el("p", "mt-1 text-sm text-slate-500", "Nenhuma opção respeita margem e prazo."));
    return bloco;
  }
  const tabela = el("table", "mt-2 w-full text-left text-sm");
  const cabecalho = el("tr", "border-b border-slate-200 text-slate-500");
  for (const titulo of ["Modal", "Frete", "Prazo", "Margem"]) cabecalho.append(el("th", "py-1 font-normal", titulo));
  tabela.append(cabecalho);
  for (const o of opcoes) {
    const linha = el("tr", o.escolhida ? "bg-blue-50 font-medium" : "border-b border-slate-100");
    linha.append(
      el("td", "py-1 pl-1", o.modal),
      el("td", "py-1", reais.format(o.frete)),
      el("td", "py-1", `${o.prazo} dia(s)`),
      el("td", "py-1", porcento.format(o.margem)),
    );
    tabela.append(linha);
  }
  bloco.append(tabela);
  return bloco;
}

function mostrarResultado(r) {
  resultado.replaceChildren(el("h2", "font-semibold", "Recomendação"));
  if (r.reavaliar_rotas) {
    resultado.append(el("p", "mt-2 rounded bg-slate-100 px-3 py-2 text-sm text-slate-700",
      "R6: alta de combustível/frete acima do limite. Reavaliar as rotas."));
  }
  resultado.append(mostrarRecomendacao(r), mostrarRegras(r.regras), mostrarOpcoes(r.opcoes));
}

function mostrarErro(mensagem) {
  resultado.replaceChildren(
    el("h2", "font-semibold", "Recomendação"),
    el("p", "mt-2 text-sm text-red-700", mensagem),
  );
}

async function avaliar(evento) {
  evento.preventDefault();
  try {
    const resposta = await fetch("/api/avaliar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lerPedido()),
    });
    const dados = await resposta.json();
    if (resposta.ok) mostrarResultado(dados);
    else mostrarErro(dados.erro);
  } catch {
    mostrarErro("Não foi possível falar com o servidor. Ele está rodando?");
  }
}

document.querySelector("#adicionar-transportadora").addEventListener("click", () => adicionarTransportadora());
document.querySelector("#exemplo").addEventListener("change", (e) => {
  if (e.target.value) preencher(exemplos[e.target.value]);
});
form.addEventListener("submit", avaliar);
