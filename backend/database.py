import sqlite3

DATABASE_NAME = "padang.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Tabel menu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            price INTEGER NOT NULL
        )
    """)

    # Menambahkan kolom is_active untuk database lama
    columns = [
        row["name"]
        for row in cursor.execute("PRAGMA table_info(menu)").fetchall()
    ]

    if "is_active" not in columns:
        cursor.execute("""
            ALTER TABLE menu
            ADD COLUMN is_active INTEGER DEFAULT 1
        """)

    # Tabel transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_price INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Detail transaksi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            menu_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            subtotal INTEGER NOT NULL,
            FOREIGN KEY (transaction_id) REFERENCES transactions(id),
            FOREIGN KEY (menu_id) REFERENCES menu(id)
        )
    """)

    # Nonaktifkan menu lama agar tidak muncul sebagai pilihan
    cursor.execute("UPDATE menu SET is_active = 0")

    # Daftar menu dan harga paket
    sample_menu = [
        ("Ayam Bakar (Potong 8)", 13000),
        ("Ayam Goreng (Potong 8)", 13000),
        ("Ayam Gulai (Potong 8)", 13000),
        ("Telur Barendo", 13000),
        ("Telur Rebus Gulai", 13000),
        ("Telur Ceplok", 13000),
        ("Ati Ampela", 13000),

        ("Ikan Nila Goreng", 17000),
        ("Ikan Nila Bakar", 17000),
        ("Ikan Kembung Goreng", 17000),
        ("Ikan Kembung Bakar", 17000),
        ("Ikan Lele Goreng", 17000),
        ("Ikan Bawal Goreng", 17000),
        ("Ikan Bawal Bakar", 17000),

        ("Ayam Bakar (Potong 4)", 22000),
        ("Ayam Goreng (Potong 4)", 22000),
        ("Ayam Gulai (Potong 4)", 22000),
        ("Rendang Daging Sapi", 22000),

        ("Gulai Cincang (Isi 5)", 23000),
        ("Tunjang", 30000),

        ("Ayam Geprek", 15000),
        ("Udang (Isi 3)", 20000)
    ]

    # Tambahkan menu baru atau perbarui harga menu lama
    cursor.executemany("""
        INSERT INTO menu (name, price, is_active)
        VALUES (?, ?, 1)
        ON CONFLICT(name)
        DO UPDATE SET
            price = excluded.price,
            is_active = 1
    """, sample_menu)

    connection.commit()
    connection.close()

    print("Database berhasil diinisialisasi!")