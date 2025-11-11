import streamlit as st
from pymongo import MongoClient
import pandas as pd
import os
from bson.json_util import dumps, loads
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/eshop")
client = MongoClient(MONGO_URI)
db = client.get_database()

st.set_page_config(page_title="E-Shop Brasil - Demo", layout="wide")
st.title("E-Shop Brasil — Dashboard Demo (MongoDB + Streamlit)")

menu = ["Visão Geral", "Produtos", "Clientes", "Pedidos", "Inserir Dados", "Consultas"]
choice = st.sidebar.selectbox("Navegação", menu)

if choice == "Visão Geral":
    col1, col2, col3 = st.columns(3)
    total_customers = db.customers.count_documents({})
    total_products = db.products.count_documents({})
    total_orders = db.orders.count_documents({})

    col1.metric("Clientes", total_customers)
    col2.metric("Produtos", total_products)
    col3.metric("Pedidos", total_orders)

    st.subheader("Top 10 produtos por estoque")
    top_stock = list(db.products.find().sort("stock", -1).limit(10))
    st.table(pd.DataFrame(top_stock))

if choice == "Produtos":
    st.subheader("Catálogo de Produtos")
    q = st.text_input("Pesquisar (nome / categoria):")
    query = {}
    if q:
        query = {"$or":[{"name":{"$regex":q,"$options":"i"}},{"category":{"$regex":q,"$options":"i"}}]}
    docs = list(db.products.find(query).limit(200))
    df = pd.DataFrame(docs)
    st.dataframe(df)
    if st.button("Exportar CSV"):
        st.download_button("Download CSV", df.to_csv(index=False), file_name="produtos.csv")

if choice == "Clientes":
    st.subheader("Clientes")
    docs = list(db.customers.find().limit(200))
    st.dataframe(pd.DataFrame(docs))
    cust_id = st.text_input("Buscar por customer_id")
    if cust_id:
        c = db.customers.find_one({"customer_id": cust_id})
        st.json(loads(dumps(c)))

if choice == "Pedidos":
    st.subheader("Pedidos")
    status = st.multiselect("Status", ["processing","shipped","delivered","cancelled"], default=["processing","shipped","delivered"])
    docs = list(db.orders.find({"status": {"$in": status}}).sort("created_at", -1).limit(200))
    st.dataframe(pd.DataFrame(docs))
    oid = st.text_input("Buscar order_id")
    if oid:
        o = db.orders.find_one({"order_id": oid})
        st.json(loads(dumps(o)))
    st.write("---")
    del_id = st.text_input("Excluir pedido (order_id)")
    if st.button("Excluir pedido"):
        res = db.orders.delete_one({"order_id": del_id})
        st.write(f"Removidos: {res.deleted_count}")

if choice == "Inserir Dados":
    st.subheader("Inserir produto manualmente")
    name = st.text_input("Nome do produto")
    cat = st.text_input("Categoria")
    price = st.number_input("Preço", min_value=0.0, value=10.0)
    stock = st.number_input("Estoque", min_value=0, value=10)
    if st.button("Inserir produto"):
        product = {"product_id": f"P{int(datetime.utcnow().timestamp())}", "name": name, "category": cat, "price": price, "stock": int(stock)}
        db.products.insert_one(product)
        st.success("Produto inserido.")

if choice == "Consultas":
    st.subheader("Exemplo de consulta: total vendas por mês")
    pipeline = [
        {"$match": {"status": {"$ne": "cancelled"}}},
        {"$project": {"month": {"$dateToString": {"format": "%Y-%m", "date": "$created_at"}}, "total": "$total"}},
        {"$group": {"_id": "$month", "revenue": {"$sum": "$total"}, "orders": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    res = list(db.orders.aggregate(pipeline))
    df = pd.DataFrame(res)
    df = df.rename(columns={"_id":"month"})
    st.line_chart(df.set_index("month")["revenue"])
    st.dataframe(df)
