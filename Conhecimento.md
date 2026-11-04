# Regras de Decisão de Envio: Frota Própria vs. Terceirizada

Problema: Dado um pedido (produtos, quantidade, destino, prazo prometido, prioridade do cliente), o sistema recomenda a melhor forma de entrega e avisa quando a margem de lucro fica abaixo do mínimo. 

## 1. Viabilidade de Frota Própria por Margem

Avalia se o custo de entrega com veículos próprios mantém a margem de lucro mínima desejada.

* **Regra:** SE `custo_transporte_proprio + custo_produto > preco * (1 - margem_minima)` ENTÃO a rota própria é inviável.
* **Pseudocódigo:**

```text
SE (custo_transporte_proprio + custo_produto) > (preco * (1 - margem_minima)) ENTAO
    marcar rota_propria como INVIÁVEL
FIM_SE

```

---

## 2. Recomendação de Terceirização por Margem

Recomenda a contratação de transportadora parceira caso a opção própria seja financeiramente inviável.

* **Regra:** SE a rota própria é inviável E existe transportadora parceira que cumpre o prazo ENTÃO recomendar terceirizar.
* **Pseudocódigo:**

```text
SE rota_propria eh INVIÁVEL E prazo_transportadora_terceira <= prazo_prometido ENTAO
    recomendar TERCEIRIZAR
FIM_SE

```

---

## 3. Avaliação de Prazo de Deslocamento

Identifica a necessidade de rotas expressas ou parceiros terceirizados quando o tempo de transporte próprio excede a promessa de entrega.

* **Regra:** SE `prazo_deslocamento > prazo_prometido` ENTÃO avaliar entrega expressa ou terceirizada.
* **Pseudocódigo:**

```text
SE prazo_deslocamento_proprio > prazo_prometido ENTAO
    AVALIAR entrega_expressa OU terceirizacao
FIM_SE

```

---

## 4. Priorização por Perfil do Cliente

Garante velocidade na entrega para clientes de alta prioridade sem descumprir o teto de margem mínima.

* **Regra:** SE `prioridade == 'alta'` E `prazo == 'apertado'` ENTÃO priorizar velocidade (aceitando menor margem desde que `>= margem_minima`).
* **Pseudocódigo:**

```text
SE cliente_prioridade == 'ALTA' E prazo == 'APERTADO' ENTAO
    SE margem_estimada >= margem_minima ENTAO
        priorizar MODAL_MAIS_RAPIDO
    FIM_SE
FIM_SE

```

---

## 5. Consolidação de Carga

Sugere juntar cargas para economizar frete quando o volume é reduzido e o percurso é longo.

* **Regra:** SE `quantidade == pequena` E `distancia == grande` ENTÃO sugerir consolidar a carga.
* **Pseudocódigo:**

```text
SE quantidade_pedido < LIMITE_QUANTIDADE E distancia_destino > LIMITE_DISTANCIA ENTAO
    sugerir CONSOLIDAR_CARGA
FIM_SE

```

---

## 6. Reavaliação de Custos de Mercado

Identifica a necessidade de recalcular rotas devido à variação dos custos de insumos (combustível/frete).

* **Regra:** SE `aumento_custo > variacao_maxima_percentual` ENTÃO reavaliar as rotas.
* **Pseudocódigo:**

```text
SE aumento_custo_combustivel_ou_frete > LIMITE_VARIACAO_PERCENTUAL ENTAO
    solicitar REAVALIACAO_DE_ROTAS
FIM_SE

```

---

## 7. Impacto de Obras na Pista e Comparativo de Rota

Calcula o atraso provocado por obras em um trecho para comparar com rotas alternativas.

* **Regra:** SE `tem_obra(Trecho)` ENTÃO calcular o atraso gerado e somar ao tempo total da Rota A para comparar com a Rota B.
* **Pseudocódigo:**

```text
SE rota_A contem OBRA ENTAO
    tempo_total_rota_A = tempo_base_rota_A + tempo_atraso_obra
    
    SE tempo_total_rota_A > tempo_base_rota_B ENTAO
        selecionar ROTA_B
    SENAO
        manter ROTA_A
    FIM_SE
FIM_SE

```