from flask import Flask, render_template, request, redirect, url_for, Response
import csv
import io
# 导入 flask-login 和 密码加密工具
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from res_db import (load_products, add_product, search_products_by_name, search_products_by_category, update_stock, delete_product, get_user_by_username, create_user # 导入刚才写的两个用户函数
)

app = Flask(__name__)
app.secret_key = 'super_secret_malaysia_key' # 必须设置一个密钥用于加密Session

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # 如果没登录，自动跳转到名叫 'login' 的路由
login_manager.login_message = "请先登录才能访问库存系统！"

# 定义 User 类 (Flask-login 要求的格式)
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

# 告诉 Flask-login 怎么根据用户ID加载用户
@login_manager.user_loader
def load_user(user_id):
    # 这里为了简单，如果是初始化请求，直接返回一个假用户对象，真实情况建议写个 get_user_by_id 函数
    # 因为我们只有一个管理员，只要 ID 存在就认为已登录
    return User(user_id, "admin", "")

@app.route('/')
def home():
    return "<a href='/inventory'>进入库存管理</a>"

@app.route('/inventory')
@login_required # 加上这一行，没登录的人就进不来了
def show_inventory():
    products = load_products()
    print(f"📦 当前读取到的数据: {products}")  # 加上这行
    return render_template('inventory.html', products=products)

@app.route('/add_form')
def add_form():
    return render_template('add_product.html')

@app.route('/add')
def add():
    name = request.args.get('name', '').strip()
    quantity_str = request.args.get('quantity', '').strip()
    price_str = request.args.get('price', '').strip()
    category = request.args.get('category', '').strip() or '未分类'
    remark = request.args.get('remark', '').strip() # 获取备注！

    if not name or not quantity_str or not price_str:
        return "名称、数量、价格不能为空", 400

    try:
        quantity = int(quantity_str)
        price = float(price_str)
    except ValueError:
        return "数量和价格必须是数字", 400

    add_product(name, quantity, price, category, remark) # 传给数据库
    print(f"✅ 已尝试存入数据: {name}")  # 加上这行
    return redirect(url_for('show_inventory'))

@app.route('/search')
def search_product():
    keyword = request.args.get('q', '').strip()
    if not keyword:
        return redirect(url_for('show_inventory'))
    results = search_products_by_name(keyword)
    return render_template('search_result.html', title=f"搜索 '{keyword}' 的结果", results=results)

@app.route('/filter_category')
def filter_category():
    category = request.args.get('cat', '').strip()
    if not category:
        return redirect(url_for('show_inventory'))
    results = search_products_by_category(category)
    return render_template('search_result.html', title=f"分类 '{category}' 的商品", results=results)

@app.route('/update_stock_form/<int:product_id>')
def update_stock_form(product_id):
    products = load_products()
    # 找到对应的商品
    target = None
    for p in products:
        if p['id'] == product_id:
            target = p
            break
    if not target:
        return "商品不存在", 404
    return render_template('update_stock.html', product=target)

@app.route('/update_stock')
def update_stock_route():
    product_id = request.args.get('id', '').strip()
    new_quantity_str = request.args.get('quantity', '').strip()

    if not product_id or not new_quantity_str:
        return "参数不能为空", 400

    try:
        product_id = int(product_id)
        new_quantity = int(new_quantity_str)
    except ValueError:
        return "数量和编号必须是数字", 400

    if new_quantity < 0:
        return "库存不能为负数", 400

    update_stock(product_id, new_quantity)
    return redirect(url_for('show_inventory'))

@app.route('/delete/<int:product_id>')
def delete(product_id):
    delete_product(product_id)
    return redirect(url_for('show_inventory'))

@app.route('/export')
def export_csv():
    products = load_products()

    # 1. 创建一个虚拟的文本文件 （就像在内存里建了个空 Excel)
    output = io.StringIO()
    writer = csv.writer(output)

    # 2. 写入表头 (第一行)
    writer.writerow(['ID', 'Name', 'Quantity', 'Price', 'Category', 'Remark'])

    # 3. 遍历数据库，把每一行数据写进去
    for p in products:
        writer.writerow([p['id'], p['name'], p['quantity'], p['price'], p['category'], p['remark']])

    # 4. 准备把文件发给浏览器下载
    # 加上 .encode('utf-8-sig') 告诉 Excel 这是带中文的 UTF-8
    response = Response(output.getvalue().encode('utf-8-sig'), mimetype="text/csv")
    # 这里的关键是 attachment, 它告诉浏览器：这不是网页，这是一个要下载的文件！
    response.headers["Content-Disposition"] = "attachment; filename=inventory_export.csv"
    return response

# ---------- 登录与登出路由 ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)

        # 检查用户是否存在，且密码是否匹配
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['password_hash'])
            login_user(user_obj)
            return redirect(url_for('show_inventory'))
        else:
            return render_template('login.html', error="用户名或密码错误， 请重试！")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# 初始化默认管理员账号 （只在第一次启动时生效）
with app.app_context():
    if not get_user_by_username("admin"):
        hashed_pw = generate_password_hash("admin123")
        create_user("admin", hashed_pw)
        print("✅️ 默认管理员账号创建成功：用户名 admin, 密码 admin123")

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
