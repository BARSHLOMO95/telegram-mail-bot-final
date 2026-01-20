import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from database import Database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Force Render to recognize this as the main app file
print("✅ Marketplace app starting...")

db = Database()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Public routes (User Interface)
@app.route('/')
def index():
    """Main page - display all categories and products"""
    categories = db.get_categories()
    category_id = request.args.get('category', type=int)
    products = db.get_products_with_images(category_id)
    return render_template('index.html', categories=categories, products=products, selected_category=category_id)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with all images"""
    product = db.get_product(product_id)
    if not product:
        return "Product not found", 404

    images = db.get_product_images(product_id)
    category = db.get_category(product['category_id'])

    return render_template('product.html', product=product, images=images, category=category)

# Admin routes
@app.route('/admin')
def admin():
    """Admin panel"""
    return render_template('admin.html')

# API endpoints for categories
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = db.get_categories()
    return jsonify(categories)

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category_id = db.add_category(data['name'], data.get('description', ''))
    return jsonify({'id': category_id, 'message': 'Category created successfully'}), 201

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    data = request.get_json()
    db.update_category(category_id, data['name'], data.get('description', ''))
    return jsonify({'message': 'Category updated successfully'})

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    db.delete_category(category_id)
    return jsonify({'message': 'Category deleted successfully'})

# API endpoints for products
@app.route('/api/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id', type=int)
    products = db.get_products_with_images(category_id)
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    product_id = db.add_product(
        data['category_id'],
        data['name'],
        data.get('description', ''),
        data.get('price', 0),
        data.get('shop_link', '')
    )
    return jsonify({'id': product_id, 'message': 'Product created successfully'}), 201

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db.get_product(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    images = db.get_product_images(product_id)
    product['images'] = images
    return jsonify(product)

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    db.update_product(
        product_id,
        data['category_id'],
        data['name'],
        data.get('description', ''),
        data.get('price', 0),
        data.get('shop_link', '')
    )
    return jsonify({'message': 'Product updated successfully'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    # Delete all images first
    images = db.get_product_images(product_id)
    for img in images:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(img['image_path']))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete_product(product_id)
    return jsonify({'message': 'Product deleted successfully'})

# API endpoints for images
@app.route('/api/products/<int:product_id>/images', methods=['POST'])
def upload_product_image(product_id):
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400

    files = request.files.getlist('images')
    uploaded_images = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid filename conflicts
            timestamp = str(int(os.path.getmtime(__file__) * 1000))
            filename = f"{timestamp}_{filename}"

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Save to database
            image_path = f"uploads/{filename}"
            image_id = db.add_product_image(product_id, image_path)
            uploaded_images.append({'id': image_id, 'path': image_path})

    return jsonify({'message': f'{len(uploaded_images)} images uploaded successfully', 'images': uploaded_images}), 201

@app.route('/api/images/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    # Get image info before deleting
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT image_path FROM product_images WHERE id = ?', (image_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(result['image_path']))
        if os.path.exists(image_path):
            os.remove(image_path)

    db.delete_product_image(image_id)
    return jsonify({'message': 'Image deleted successfully'})

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
