from pymongo import MongoClient
from faker import Faker
import random
import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/eshop")
client = MongoClient(MONGO_URI)
db = client.get_database()

fake = Faker("pt_BR")

def create_products(n=100):
    categories = ["eletrônicos", "moda", "casa", "beleza", "esportes"]
    products = []
    for i in range(n):
        p = {
            "product_id": f"P{i:05d}",
            "name": fake.word().capitalize() + " " + fake.word().capitalize(),
            "category": random.choice(categories),
            "price": round(random.uniform(20, 2000), 2),
            "stock": random.randint(0, 500),
            "attributes": {"color": random.choice(["azul","preto","branco","vermelho","verde"]), "size": random.choice(["P","M","G","ÚNICO"])}
        }
        products.append(p)
    db.products.insert_many(products)
    return products

def create_customers(n=200):
    customers = []
    for i in range(n):
        c = {
            "customer_id": f"C{i:06d}",
            "name": fake.name(),
            "email": fake.email(),
            "address": {"city": fake.city(), "state": fake.state_abbr()},
            "created_at": fake.date_time_between(start_date='-3y', end_date='now')
        }
        customers.append(c)
    db.customers.insert_many(customers)
    return customers

def create_orders(customers, products, n=500):
    orders = []
    for i in range(n):
        cust = random.choice(customers)
        num_items = random.randint(1,4)
        items = []
        total = 0
        for k in range(num_items):
            p = random.choice(products)
            q = random.randint(1,3)
            items.append({"product_id": p["product_id"], "qty": q, "unit_price": p["price"]})
            total += p["price"] * q
        o = {
            "order_id": f"O{i:07d}",
            "customer_id": cust["customer_id"],
            "items": items,
            "total": round(total,2),
            "status": random.choice(["processing","shipped","delivered","cancelled"]),
            "created_at": fake.date_time_between(start_date='-1y', end_date='now')
        }
        orders.append(o)
    db.orders.insert_many(orders)
    return orders

if __name__ == "__main__":
    print("Populando MongoDB...")
    db.products.drop()
    db.customers.drop()
    db.orders.drop()
    products = create_products(200)
    customers = create_customers(500)
    orders = create_orders(customers, products, 1500)
    print("Concluído.")
