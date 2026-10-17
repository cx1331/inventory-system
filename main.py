from flask import Flask, render_template, request, redirect, url_for
from res_db import load_products, add_product, search_products_by_name, search_products_by_category, update_stock, delete_product

app = Flask(__name__)

@app.route('/')
def home():
    return "<a href='/inventory'>进入库存管理</a>"

@app.route('/inventory')
def show_inventory():
    products = load_products()
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

    if not name or not quantity_str or not price_str:
        return "名称、数量、价格不能为空", 400

    try:
        quantity = int(quantity_str)
        price = float(price_str)
    except ValueError:
        return "数量和价格必须是数字", 400

    add_product(name, quantity, price, category)
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

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)