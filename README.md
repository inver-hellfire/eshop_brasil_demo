# E-Shop Brasil — Demo (MongoDB + Streamlit)

## Introdução
Projeto demonstrativo para aplicação prática de bancos de dados e Big Data em e-commerce.

## Tecnologias
- Docker / docker-compose
- MongoDB
- Streamlit (app)
- Python (pymongo, pandas, faker)

## Como executar
1. `docker compose up --build`
2. Acesse `http://localhost:8501`
3. Popular dados: `python scripts/data_generator.py`

## Funcionalidades
- Inserção, edição e exclusão de dados
- Consultas agregadas (vendas por mês)
- Exportação de CSV
- Demonstrações em `examples/`

## Notas de segurança e LGPD
- Recomendamos ativar TLS no MongoDB e usar KMS para chaves.
- Implementar endpoints para solicitações de titulares (exclusão/exportação).
