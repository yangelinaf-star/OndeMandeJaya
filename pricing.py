from database import get_connection


def calculate_price(items):
    if not isinstance(items, list) or len(items) == 0:
        raise ValueError("Daftar menu tidak boleh kosong.")

    connection = get_connection()
    cursor = connection.cursor()

    results = []
    total_price = 0

    try:
        for item in items:
            name = item.get("name")
            quantity = item.get("quantity", 1)

            if not isinstance(name, str) or not name.strip():
                raise ValueError("Nama menu tidak valid.")

            if (
                isinstance(quantity, bool)
                or not isinstance(quantity, int)
                or quantity <= 0
            ):
                raise ValueError("Jumlah menu harus berupa bilangan bulat positif.")

            cursor.execute("""
                SELECT id, name, price
                FROM menu
                WHERE name = ? AND is_active = 1
            """, (name,))

            menu = cursor.fetchone()

            if menu is None:
                raise ValueError(f"Menu '{name}' tidak ditemukan.")

            subtotal = menu["price"] * quantity
            total_price += subtotal

            results.append({
                "menu_id": menu["id"],
                "name": menu["name"],
                "quantity": quantity,
                "price": menu["price"],
                "subtotal": subtotal
            })

        return {
            "items": results,
            "total_price": total_price
        }

    finally:
        connection.close()