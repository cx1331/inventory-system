import sqlite3

DATABASE = 'inventory.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            category TEXT DEFAULT '未分类'
        )
    ''')
    conn.commit()
    conn.close()

def load_products():
    conn = get_db()
    rows = conn.execute('SELECT * FROM products ORDER BY id').fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_product(name, quantity, price, category="未分类"):
    conn = get_db()
    conn.execute(
        'INSERT INTO products (name, quantity, price, category) VALUES (?, ?, ?, ?)',
        (name, quantity, price, category)
    )
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db()
    conn.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def search_products_by_name(keyword):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM products WHERE name LIKE ? ORDER BY id',
        (f'%{keyword}%',)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def search_products_by_category(category):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM products WHERE category = ? ORDER BY id',
        (category,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_stock(product_id, new_quantity):
    conn = get_db()
    conn.execute(
        'UPDATE products SET quantity = ? WHERE id = ?',
        (new_quantity, product_id)
    )
    conn.commit()
    conn.close()

# 程序启动时建表
init_db()