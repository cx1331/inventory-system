import os
import sqlite3
import psycopg2
import psycopg2.extras

# 核心：在这里定义变量，电脑就不会报错了
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = DATABASE_URL is not None

def get_db():
    if IS_POSTGRES:
        print("正在使用：云端 PostgreSQL 数据库")
        return psycopg2.connect(DATABASE_URL)
    else:
        print("正在使用：本地 SQLite 数据库")
        # 获取当前文件所在的绝对路径，强制数据库跟代码在同一目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'inventory.db')
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 针对不同数据库的自增主键写法
    if IS_POSTGRES:
        create_products_sql = '''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                category TEXT DEFAULT '未分类',
                remark TEXT
            )
        '''
        # 建用户表 (PostgreSQL版)
        create_users_sql = '''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        '''
    else:
        create_products_sql = '''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                category TEXT DEFAULT '未分类',
                remark TEXT
                )
            '''
        # 建用户表 (SQLite版)
        create_users_sql = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
                )
        '''

    cursor.execute(create_products_sql)
    cursor.execute(create_users_sql)
    conn.commit()
    cursor.close()
    conn.close()

def load_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY id')
    rows = cursor.fetchall()

    columns = [column[0] for column in cursor.description]
    products = [dict(zip(columns, row)) for row in rows]
    
    cursor.close()
    conn.close()
    return products

def add_product(name, quantity, price, category="未分类", remark=""):
    conn = get_db()
    cursor = conn.cursor()

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

# 根据用户名查找用户 (登录时用)
def get_user_by_username(username):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    cursor.execute(f'SELECT * FROM users WHERE username = {p}', (username,))
    row = cursor.fetchone()

    if row:
        columns = [column[0] for column in cursor.description]
        user = dict(zip(columns, row))
    else:
        user = None

    cursor.close()
    conn.close()
    return user

# 创建新用户 (初始化管理员密码时用)
def create_user(username, password_hash):
    conn = get_db()
    cursor = conn.cursor()
    p = "%s" if IS_POSTGRES else "?"
    try:
        cursor.execute(f'INSERT INTO users (username, password_hash) VALUES ({p}, {p})', (username, password_hash))
        conn.commit()
        return True
    except Exception as e:
        # 如果用户名已存在，会报错，直接返回 False
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# 启动时建表
init_db()
