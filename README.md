# SmartStoke

Controle de estoque local, simples e gratuito para pequenos negócios. Feito em Python com Tkinter e SQLite.

## O que já funciona

- Cadastro, edição, pesquisa e exclusão de produtos.
- Registro de entradas e saídas, com validação para impedir estoque negativo.
- Histórico de movimentações (preservado mesmo quando um produto é excluído).
- Painel com quantidade de produtos, unidades e valor estimado em estoque.
- Lista de produtos no limite ou abaixo do estoque mínimo.
- Gráfico dos produtos com mais unidades vendidas.
- Banco SQLite criado automaticamente no computador: `~/.smartstoke/smartstoke.db`.

## Requisitos

- Python 3.10 ou superior.
- Tkinter (normalmente já acompanha Python; em algumas distribuições Linux é instalado separadamente).

## Como executar

```bash
git clone https://github.com/HubertRamos/SmartStoke.git
cd SmartStoke
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# No Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

No Linux baseado em Debian/Ubuntu, caso o Tkinter não esteja disponível:

```bash
sudo apt install python3-tk
```

## Testes

```bash
python -m unittest discover -s tests -v
```

Os dados ficam no próprio computador. Para fazer backup, feche o SmartStoke e copie o arquivo `~/.smartstoke/smartstoke.db`.
