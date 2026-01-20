import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name='marketplace.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                shop_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')

        # Product images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                image_path TEXT NOT NULL,
                display_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    # Category methods
    def add_category(self, name, description=''):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)',
                      (name, description))
        conn.commit()
        category_id = cursor.lastrowid
        conn.close()
        return category_id

    def get_categories(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY name')
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories

    def get_category(self, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories WHERE id = ?', (category_id,))
        category = cursor.fetchone()
        conn.close()
        return dict(category) if category else None

    def update_category(self, category_id, name, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE categories SET name = ?, description = ? WHERE id = ?',
                      (name, description, category_id))
        conn.commit()
        conn.close()

    def delete_category(self, category_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        conn.commit()
        conn.close()

    # Product methods
    def add_product(self, category_id, name, description, price, shop_link):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO products
                         (category_id, name, description, price, shop_link)
                         VALUES (?, ?, ?, ?, ?)''',
                      (category_id, name, description, price, shop_link))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id

    def get_products(self, category_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if category_id:
            cursor.execute('SELECT * FROM products WHERE category_id = ? ORDER BY created_at DESC',
                          (category_id,))
        else:
            cursor.execute('SELECT * FROM products ORDER BY created_at DESC')
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return products

    def get_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        conn.close()
        return dict(product) if product else None

    def update_product(self, product_id, category_id, name, description, price, shop_link):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''UPDATE products
                         SET category_id = ?, name = ?, description = ?,
                             price = ?, shop_link = ?
                         WHERE id = ?''',
                      (category_id, name, description, price, shop_link, product_id))
        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()

    # Product image methods
    def add_product_image(self, product_id, image_path, display_order=0):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO product_images
                         (product_id, image_path, display_order)
                         VALUES (?, ?, ?)''',
                      (product_id, image_path, display_order))
        conn.commit()
        image_id = cursor.lastrowid
        conn.close()
        return image_id

    def get_product_images(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM product_images
                         WHERE product_id = ?
                         ORDER BY display_order, created_at''',
                      (product_id,))
        images = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return images

    def delete_product_image(self, image_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM product_images WHERE id = ?', (image_id,))
        conn.commit()
        conn.close()

    def get_products_with_images(self, category_id=None):
        """Get products with their first image"""
        products = self.get_products(category_id)
        for product in products:
            images = self.get_product_images(product['id'])
            product['images'] = images
            product['main_image'] = images[0]['image_path'] if images else None
        return products
