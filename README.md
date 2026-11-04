# Sistema Especialista em Logística de Envio

Trabalho de Inteligência Artificial voltado ao desenvolvimento de um Sistema Especialista para tomada de decisão no envio de pedidos (Frota Própria vs. Terceirizada).

## Alunos
- Pedro Miotto Mujica
- Vinicius Castaman Giongo
- Gabriel Costa
- Pedro Moraes

---

## Configuração do Ambiente

### 1. Criar e ativar o ambiente virtual (venv)

* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate

* **Windows (PowerShell):**


  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1

  ```

---

### 2. Instalar as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt

```

---

## 3. Como Executar

Para iniciar o sistema especialista:

* **Menu Interativo (modo completo):**
```bash
python main.py

```

* **Rodar Pedidos de Exemplo (modo demonstração):**
```bash
python main.py --demo

```
