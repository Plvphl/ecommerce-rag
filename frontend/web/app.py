from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 模拟商品数据
products = [
    {
        'id': 1,
        'name': '商品1',
        'price': 100,
        'description': '这是商品1的描述',
        'category': '电子产品',
        'image': 'https://via.placeholder.com/300x200?text=商品1',
        'stock': 10,
        'rating': 4.5
    },
    {
        'id': 2,
        'name': '商品2',
        'price': 200,
        'description': '这是商品2的描述',
        'category': '家用电器',
        'image': 'https://via.placeholder.com/300x200?text=商品2',
        'stock': 5,
        'rating': 4.2
    }
]

cart = []

# 用户信息
user_info = {
    'username': '用户1',
    'email': 'user1@example.com',
    'gender': '男',
    'age': 25,
    'phone': '13800000000',
    'address': '北京市',
    'orders': []
}

# 登录保护装饰器
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_logged_in' not in session and 'merchant_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        if user_type == 'user':
            session['user_logged_in'] = True
            return redirect(url_for('index'))
        elif user_type == 'merchant':
            session['merchant_logged_in'] = True
            return redirect(url_for('management'))
    return render_template('login.html')

# 首页
@app.route('/')
@login_required
def index():
    return render_template('index.html', products=products)

#搜索
@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').lower()
    results = [p for p in products if query in p['name'].lower()]
    return render_template('search_results.html', products=results, query=query)


# 商品详情页
@app.route('/product/<int:product_id>')
@login_required
def product_detail(product_id):
    product = next(p for p in products if p['id'] == product_id)
    return render_template('product_detail.html', product=product)

# 加入购物车
from flask import flash

# 修改后的加入购物车逻辑
@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = next(p for p in products if p['id'] == product_id)
    # 判断购物车中是否已有该商品（根据商品 id）
    if any(item['id'] == product_id for item in cart):
        flash('该商品已在购物车中，无需重复添加！')
    else:
        cart.append(product)
        flash('商品已成功加入购物车！')
    return redirect(request.referrer or url_for('index'))

# 购物车页面
@app.route('/cart')
@login_required
def shopping_cart():
    return render_template('cart.html', cart=cart)

#移出购物车
@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    global cart
    cart = [item for item in cart if item['id'] != product_id]
    flash('商品已从购物车移除。')
    return redirect(url_for('shopping_cart'))

# 我的页面
@app.route('/my')
@login_required
def my_page():
    status_filter = request.args.get('status')
    orders = user_info['orders']
    if status_filter:
        orders = [o for o in orders if o['status'] == status_filter]
    return render_template('mypage.html', user={**user_info, 'orders': orders})

# 修改用户信息
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user_info['username'] = request.form['username']
    user_info['gender'] = request.form['gender']
    user_info['age'] = int(request.form['age'])
    user_info['phone'] = request.form['phone']
    user_info['address'] = request.form['address']
    return redirect(url_for('my_page'))

# 下单页面
@app.route('/order/<int:product_id>')
@login_required
def order_page(product_id):
    product = next(p for p in products if p['id'] == product_id)
    return render_template('order_form.html', product=product)

# 提交订单
@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    product_id = int(request.form['product_id'])
    product = next(p for p in products if p['id'] == product_id)
    recipient = request.form['recipient']
    phone = request.form['phone']
    address = request.form['address']

    new_order = {
        'id': len(user_info['orders']) + 1,
        'status': '已付款',
        'total': product['price'],
        'delivery_address': f"{recipient}, {phone}, {address}",
        'product_name': product['name']
    }
    user_info['orders'].append(new_order)

    # 自动从购物车中移除该商品（如果存在）
    global cart
    cart = [item for item in cart if item['id'] != product_id]

    flash('订单提交成功，商品已从购物车移除！')
    return redirect(url_for('my_page'))

# 商家管理页
@app.route('/management')

def management():
    if 'merchant_logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('management.html', products=products, orders=user_info['orders'])

# 添加商品
@app.route('/add_product', methods=['POST'])

def add_product():
    if 'merchant_logged_in' not in session:
        return redirect(url_for('login'))
    new_id = max([p['id'] for p in products] + [0]) + 1
    new_product = {
        'id': new_id,
        'name': request.form['name'],
        'description': request.form['description'],
        'category': request.form['category'],
        'image': request.form['image'],
        'price': float(request.form['price']),
        'stock': int(request.form['stock']),
        'rating': float(request.form['rating'])
    }
    products.append(new_product)
    return redirect(url_for('management'))

# 修改商品
@app.route('/update_product/<int:product_id>', methods=['POST'])

def update_product(product_id):
    if 'merchant_logged_in' not in session:
        return redirect(url_for('login'))
    for product in products:
        if product['id'] == product_id:
            product['name'] = request.form['name']
            product['description'] = request.form['description']
            product['category'] = request.form['category']
            product['image'] = request.form['image']
            product['price'] = float(request.form['price'])
            product['stock'] = int(request.form['stock'])
            product['rating'] = float(request.form['rating'])
            break
    return redirect(url_for('management'))

# 删除商品
@app.route('/delete_product/<int:product_id>', methods=['POST'])

def delete_product(product_id):
    if 'merchant_logged_in' not in session:
        return redirect(url_for('login'))
    global products
    products = [p for p in products if p['id'] != product_id]
    return redirect(url_for('management'))

# 修改订单状态
@app.route('/update_order_status/<int:order_id>', methods=['POST'])

def update_order_status(order_id):
    if 'merchant_logged_in' not in session:
        return redirect(url_for('login'))
    new_status = request.form['status']
    for order in user_info['orders']:
        if order['id'] == order_id:
            order['status'] = new_status
            break
    return redirect(url_for('management'))

# 退出登录
@app.route('/logout')
def logout():
    session.pop('user_logged_in', None)
    session.pop('merchant_logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
