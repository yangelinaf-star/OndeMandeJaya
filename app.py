from flask import Flask, request, jsonify
from flask_cors import CORS

from database import get_connection, initialize_database
from pricing import calculate_price

app = Flask(__name__)
CORS(app)


# Halaman utama untuk mengecek backend
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "PadangScan AI Backend is running!"
    })


# Mengambil semua menu aktif
@app.route("/api/menu", methods=["GET"])
def get_menu():
    connection = get_connection()

    menus = connection.execute("""
        SELECT id, name, price
        FROM menu
        WHERE is_active = 1
        ORDER BY price, name
    """).fetchall()

    connection.close()

    return jsonify([
        dict(menu) for menu in menus
    ])


# Menghitung harga pesanan
@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Format JSON tidak valid."}), 400

    items = data.get("items")

    try:
        result = calculate_price(items)
        return jsonify(result)

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# Menyimpan transaksi
@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Format JSON tidak valid."}), 400

    try:
        result = calculate_price(data.get("items"))

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO transactions (total_price)
            VALUES (?)
        """, (result["total_price"],))

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

        connection.commit()
        connection.close()

        return jsonify({
            "message": "Transaksi berhasil disimpan.",
            "transaction_id": transaction_id,
            "items": result["items"],
            "total_price": result["total_price"]
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# Melihat riwayat transaksi
@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    connection = get_connection()

    transactions = connection.execute("""
        SELECT id, total_price, created_at
        FROM transactions
        ORDER BY id DESC
    """).fetchall()

    connection.close()

    return jsonify([
        dict(transaction) for transaction in transactions
    ])


if __name__ == "__main__":
    initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=True)
