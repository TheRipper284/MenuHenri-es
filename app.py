import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGO_URI, DB_NAME, UPLOAD_FOLDER

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Crear carpeta de imágenes si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
menu_collection = db["menu_items"]

# Crear datos por defecto si la colección está vacía
if menu_collection.count_documents({}) == 0:
    menu_collection.insert_many([
        {
            "name": "Pizza Pepperoni",
            "price": 150,
            "category": "Pizzas",
            "description": "Clásica pizza con pepperoni fresco",
            "image": None
        },
        {
            "name": "Pizza Hawaiana",
            "price": 160,
            "category": "Pizzas",
            "description": "Jamón y piña dulce",
            "image": None
        }
    ])

# -----------------------------
#      RUTA PRINCIPAL
# -----------------------------
@app.route("/")
def index():
    pizzas = list(menu_collection.find({"category": "Pizzas"}))
    complementos = list(menu_collection.find({"category": "Complementos"}))
    bebidas = list(menu_collection.find({"category": "Bebidas"}))
    return render_template("index.html",
                           pizzas=pizzas,
                           complementos=complementos,
                           bebidas=bebidas)

# -----------------------------
#         ADMIN
# -----------------------------
@app.route("/admin")
def admin():
    menu_items = list(menu_collection.find())
    return render_template("admin.html", menu_items=menu_items)

# -----------------------------
#     AGREGAR ITEM
# -----------------------------
@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form["name"]
    price = float(request.form["price"])
    category = request.form["category"]
    description = request.form["description"]

    image_file = request.files["image"]
    filename = None

    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    menu_collection.insert_one({
        "name": name,
        "price": price,
        "category": category,
        "description": description,
        "image": filename
    })

    return redirect(url_for("admin"))

# -----------------------------
#     EDITAR ITEM
# -----------------------------
@app.route("/edit/<id>")
def edit(id):
    item = menu_collection.find_one({"_id": ObjectId(id)})
    return render_template("edit_item.html", item=item)

# -----------------------------
#      ACTUALIZAR ITEM
# -----------------------------
@app.route("/update/<id>", methods=["POST"])
def update(id):

    name = request.form["name"]
    price = float(request.form["price"])
    category = request.form["category"]
    description = request.form["description"]
    image_file = request.files["image"]

    update_data = {
        "name": name,
        "price": price,
        "category": category,
        "description": description
    }

    # Si se subió una imagen nueva
    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        update_data["image"] = filename

    menu_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )

    return redirect(url_for("admin"))

# -----------------------------
#      ELIMINAR ITEM
# -----------------------------
@app.route("/delete/<id>")
def delete(id):
    menu_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
