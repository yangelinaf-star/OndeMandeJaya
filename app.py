
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

from database import (
    initialize_database,
    get_connection
)

from pricing import calculate_price


app = Flask(__name__)
CORS(app)


# =========================
# HOME / TEST BACKEND
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "PadangScan AI Backend is Running!",
        "status": "success"
    })


# =========================
# GET ALL MENU
# =========================

@app.route("/api/menu", methods=["GET"])
def get_menu():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM menu ORDER BY name")

    menus = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(menus)


# =========================
# ADD NEW MENU
# =========================

@app.route("/api/menu", methods=["POST"])
def add_menu():
    data = request.get_json(silent=True) or {}

    name = data.get("name")
    price = data.get("price")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Nama makanan wajib diisi"}), 400

    if type(price) is not int or price < 0:
        return jsonify({"error": "Harga harus berupa angka positif"}), 400

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO menu (name, price)
            VALUES (?, ?)
        """, (name.strip(), price))

        conn.commit()

        return jsonify({
            "message": "Menu berhasil ditambahkan"
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({
            "error": "Nama makanan sudah tersedia"
        }), 409

    finally:
        conn.close()


# =========================
# UPDATE FOOD PRICE
# =========================

@app.route("/api/menu/<int:menu_id>", methods=["PUT"])
def update_menu(menu_id):
    data = request.get_json(silent=True) or {}

    price = data.get("price")

    if type(price) is not int or price < 0:
        return jsonify({"error": "Harga tidak valid"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE menu
        SET price = ?
        WHERE id = ?
    """, (price, menu_id))

    conn.commit()

    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return jsonify({"error": "Menu tidak ditemukan"}), 404

    return jsonify({
        "message": "Harga berhasil diperbarui"
    })


# =========================
# CALCULATE FOOD PRICE
# =========================

@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True) or {}
    items = data.get("items")

    if not isinstance(items, list) or not items:
        return jsonify({
            "error": "Daftar makanan tidak boleh kosong"
        }), 400

    try:
        result = calculate_price(items)

        return jsonify({
            "message": "Harga berhasil dihitung",
            **result
        })

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


# =========================
# CHECKOUT AND SAVE TRANSACTION
# =========================

@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json(silent=True) or {}
    items = data.get("items")

    if not isinstance(items, list) or not items:
        return jsonify({
            "error": "Tidak ada makanan untuk checkout"
        }), 400

    try:
        result = calculate_price(items)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transactions (total_price)
            VALUES (?)
        """, (result["total"],))

        transaction_id = cursor.lastrowid

        for item in result["items"]:
            cursor.execute("""
                INSERT INTO transaction_items
                (transaction_id, menu_id, quantity, subtotal)
                VALUES (?, ?, ?, ?)
            """, (
                transaction_id,
                item["menu_id"],
                item["quantity"],
                item["subtotal"]
            ))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Transaksi berhasil disimpan",
            "transaction_id": transaction_id,
            "items": result["items"],
            "total": result["total"]
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# =========================
# GET TRANSACTION HISTORY
# =========================

@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM transactions
        ORDER BY created_at DESC
    """)

    transactions = [
        dict(row) for row in cursor.fetchall()
    ]

    conn.close()

    return jsonify(transactions)


# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(debug=False)
