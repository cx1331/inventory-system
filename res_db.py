import os
import sqlite3
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None

def get_db():
    if IS_POSTGRES:
        # 云端使用 PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        # 本地使用 SQLite
        conn = sqlite3.connect('inventory.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 针对不同数据库的自增主键写法
    if IS_POSTGRES:
        create_sql = '''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                category TEXT DEFAULT '未分类',
                remark TEXT
            )
        '''
    else:
        create_sql = '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                category TEXT DEFAULT '未分类',
                remark TEXT
            )
        '''
    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()

def load_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY id')
    rows = cursor.fetchall()
    
    if IS_POSTGRES:
        products = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        products = [dict(row) for row in rows]
        
    cursor.close()
    conn.close()
    return products

def add_product(name, quantity, price, category="未分类", remark=""):
    conn = get_db()
    cursor = conn.cursor()
    
    # 动态判断占位符
    p = "%s" if IS_POSTGRES else "?"
    sql = f'INSERT INTO products (name, quantity, price, category, remark) VALUES ({p}, {p}, {p}, {p}, {p})'
    
    cursor.execute(sql, (name, quantity, price, category, remark))
    conn.commit()
    cursor.close()
    conn.close()

def delete_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'DELETE FROM products WHERE id = {p}', (product_id,))
    conn.commit()
    cursor.close()
    conn.close()

def update_stock(product_id, new_quantity):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'UPDATE products SET quantity = {p} WHERE id = {p}', (new_quantity, product_id))
    conn.commit()
    cursor.close()
    conn.close()

def search_products_by_name(keyword):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM products WHERE name LIKE {p} ORDER BY id', (f'%{keyword}%',))
    rows = cursor.fetchall()
    
    if IS_POSTGRES:
        products = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        products = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return products

def search_products_by_category(category):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM products WHERE category = {p} ORDER BY id', (category,))
    rows = cursor.fetchall()
    
    if IS_POSTGRES:
        products = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    else:
        products = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return products

# 启动时建表
init_db()
