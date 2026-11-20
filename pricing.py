
from database import get_connection
 
def calculate_price(items):
    conn = get_connection()
    cursor = conn.cursor()

    results = []
    total = 0

    for item in items:
        name = item.get("name")
        quantity = item.get("quantity", 1)

        if not isinstance(name, str) or not name.strip():
            conn.close()
            raise ValueError("Nama makanan tidak valid")

        if type(quantity) is not int or quantity < 1:
            conn.close()
            raise ValueError("Jumlah makanan harus bilangan bulat positif")

        cursor.execute(
            "SELECT id, name, price FROM menu WHERE name = ?",
            (name.strip(),)
        )

        food = cursor.fetchone()

        if food is None:
            conn.close()
            raise ValueError(f"Makanan {name} tidak ditemukan")

        subtotal = food["price"] * quantity
        total += subtotal

        results.append({
            "menu_id": food["id"],
            "name": food["name"],
            "price": food["price"],
            "quantity": quantity,
            "subtotal": subtotal
        })

    conn.close()

    return {
        "items": results,
        "total": total
    }
