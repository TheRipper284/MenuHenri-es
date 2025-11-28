from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from bson.objectid import ObjectId


app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
menu_collection = db['menu_items']

if menu_collection.count_documents({}) == 0:
    menu_collection.insert_many([
        {"name": "Pizza Pepperoni", "price": 150, "category": "Pizzas"},
        {"name": "Pizza Hawaiana", "price": 160, "category": "Pizzas"},
        {"name": "Papas a la Francesa", "price": 50, "category": "Complementos"},
        {"name": "Alitas BBQ", "price": 120, "category": "Complementos"},
        {"name": "Coca-Cola 600ml", "price": 25, "category": "Bebidas"}
    ])

@app.route('/')
def index():
    pizzas = list(menu_collection.find({"category": "Pizzas"}))
    complementos = list(menu_collection.find({"category": "Complementos"}))
    bebidas = list(menu_collection.find({"category": "Bebidas"}))

    return render_template("index.html",
                           pizzas=pizzas,
                           complementos=complementos,
                           bebidas=bebidas)

@app.route("/admin")
def admin():
    menu_items = list(menu_collection.find())
    return render_template("admin.html", menu_items=menu_items)

@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form["name"]
    price = float(request.form["price"])
    category = request.form["category"]

    menu_collection.insert_one({"name": name, "price": price, "category": category})
    return redirect(url_for("admin"))

@app.route("/edit/<id>")
def edit(id):
    item = menu_collection.find_one({"_id": ObjectId(id)})
    return render_template("edit_item.html", item=item)

@app.route("/update/<id>", methods=["POST"])
def update(id):
    name = request.form["name"]
    price = float(request.form["price"])
    category = request.form["category"]

    menu_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"name": name, "price": price, "category": category}}
    )
    return redirect(url_for("admin"))

@app.route("/delete/<id>")
def delete(id):
    menu_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin"))

print("MONGO_URI =", MONGO_URI)
if __name__ == "__main__":
    app.run(debug=True)