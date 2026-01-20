let categoryModal, productModal;
let categories = [];
let currentProductId = null;

document.addEventListener('DOMContentLoaded', function() {
    categoryModal = new bootstrap.Modal(document.getElementById('categoryModal'));
    productModal = new bootstrap.Modal(document.getElementById('productModal'));

    loadCategories();
    loadProducts();
});

// Categories
async function loadCategories() {
    try {
        const response = await fetch('/api/categories');
        categories = await response.json();
        displayCategories();
        updateCategorySelect();
    } catch (error) {
        console.error('Error loading categories:', error);
        alert('שגיאה בטעינת קטגוריות');
    }
}

function displayCategories() {
    const container = document.getElementById('categoriesList');
    if (categories.length === 0) {
        container.innerHTML = '<p class="text-muted">אין קטגוריות עדיין</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>שם</th>
                        <th>תיאור</th>
                        <th>פעולות</th>
                    </tr>
                </thead>
                <tbody>
                    ${categories.map(cat => `
                        <tr>
                            <td>${cat.name}</td>
                            <td>${cat.description || '-'}</td>
                            <td>
                                <button class="btn btn-sm btn-warning" onclick="editCategory(${cat.id})">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteCategory(${cat.id})">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function showCategoryModal(categoryId = null) {
    document.getElementById('categoryForm').reset();
    document.getElementById('categoryId').value = '';

    if (categoryId) {
        const category = categories.find(c => c.id === categoryId);
        if (category) {
            document.getElementById('categoryId').value = category.id;
            document.getElementById('categoryName').value = category.name;
            document.getElementById('categoryDescription').value = category.description || '';
        }
    }

    categoryModal.show();
}

function editCategory(id) {
    showCategoryModal(id);
}

async function saveCategory() {
    const id = document.getElementById('categoryId').value;
    const name = document.getElementById('categoryName').value;
    const description = document.getElementById('categoryDescription').value;

    if (!name) {
        alert('נא למלא שם קטגוריה');
        return;
    }

    const data = { name, description };

    try {
        let response;
        if (id) {
            response = await fetch(`/api/categories/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch('/api/categories', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        }

        if (response.ok) {
            categoryModal.hide();
            loadCategories();
            alert('הקטגוריה נשמרה בהצלחה');
        } else {
            alert('שגיאה בשמירת קטגוריה');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        alert('שגיאה בשמירת קטגוריה');
    }
}

async function deleteCategory(id) {
    if (!confirm('האם אתה בטוח שברצונך למחוק קטגוריה זו?')) {
        return;
    }

    try {
        const response = await fetch(`/api/categories/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadCategories();
            alert('הקטגוריה נמחקה בהצלחה');
        } else {
            alert('שגיאה במחיקת קטגוריה');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
        alert('שגיאה במחיקת קטגוריה');
    }
}

// Products
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error('Error loading products:', error);
        alert('שגיאה בטעינת מוצרים');
    }
}

function displayProducts(products) {
    const container = document.getElementById('productsList');
    if (products.length === 0) {
        container.innerHTML = '<p class="text-muted">אין מוצרים עדיין</p>';
        return;
    }

    container.innerHTML = `
        <div class="row">
            ${products.map(product => `
                <div class="col-md-4 mb-3">
                    <div class="card h-100">
                        ${product.main_image ? `
                            <img src="/static/${product.main_image}" class="card-img-top" style="height: 200px; object-fit: cover;">
                        ` : `
                            <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 200px;">
                                <i class="bi bi-image" style="font-size: 3rem; color: #ccc;"></i>
                            </div>
                        `}
                        <div class="card-body">
                            <h5 class="card-title">${product.name}</h5>
                            <p class="card-text text-muted small">${product.description || ''}</p>
                            ${product.price ? `<p class="text-primary fw-bold">₪${product.price}</p>` : ''}
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-warning flex-fill" onclick="editProduct(${product.id})">
                                    <i class="bi bi-pencil"></i> ערוך
                                </button>
                                <button class="btn btn-sm btn-danger flex-fill" onclick="deleteProduct(${product.id})">
                                    <i class="bi bi-trash"></i> מחק
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function updateCategorySelect() {
    const select = document.getElementById('productCategory');
    select.innerHTML = '<option value="">בחר קטגוריה</option>' +
        categories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('');
}

function showProductModal(productId = null) {
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.getElementById('existingImages').innerHTML = '';
    currentProductId = null;

    if (productId) {
        loadProductDetails(productId);
    }

    productModal.show();
}

async function loadProductDetails(productId) {
    try {
        const response = await fetch(`/api/products/${productId}`);
        const product = await response.json();

        currentProductId = productId;
        document.getElementById('productId').value = product.id;
        document.getElementById('productCategory').value = product.category_id;
        document.getElementById('productName').value = product.name;
        document.getElementById('productDescription').value = product.description || '';
        document.getElementById('productPrice').value = product.price || '';
        document.getElementById('productShopLink').value = product.shop_link || '';

        displayExistingImages(product.images || []);
    } catch (error) {
        console.error('Error loading product details:', error);
        alert('שגיאה בטעינת פרטי מוצר');
    }
}

function displayExistingImages(images) {
    const container = document.getElementById('existingImages');
    if (images.length === 0) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = `
        <label class="form-label">תמונות קיימות</label>
        <div>
            ${images.map(img => `
                <div class="image-container">
                    <img src="/static/${img.image_path}" class="product-image-preview">
                    <button type="button" class="delete-image-btn" onclick="deleteImage(${img.id})">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            `).join('')}
        </div>
    `;
}

function editProduct(id) {
    showProductModal(id);
}

async function saveProduct() {
    const id = document.getElementById('productId').value;
    const categoryId = document.getElementById('productCategory').value;
    const name = document.getElementById('productName').value;
    const description = document.getElementById('productDescription').value;
    const price = document.getElementById('productPrice').value;
    const shopLink = document.getElementById('productShopLink').value;

    if (!categoryId || !name) {
        alert('נא למלא קטגוריה ושם מוצר');
        return;
    }

    const data = {
        category_id: parseInt(categoryId),
        name,
        description,
        price: parseFloat(price) || 0,
        shop_link: shopLink
    };

    try {
        let response;
        let productId = id;

        if (id) {
            response = await fetch(`/api/products/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            response = await fetch('/api/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            productId = result.id;
        }

        if (!response.ok) {
            throw new Error('Failed to save product');
        }

        // Upload images if any
        const imageFiles = document.getElementById('productImages').files;
        if (imageFiles.length > 0) {
            await uploadImages(productId, imageFiles);
        }

        productModal.hide();
        loadProducts();
        alert('המוצר נשמר בהצלחה');
    } catch (error) {
        console.error('Error saving product:', error);
        alert('שגיאה בשמירת מוצר');
    }
}

async function uploadImages(productId, files) {
    const formData = new FormData();
    for (let file of files) {
        formData.append('images', file);
    }

    const response = await fetch(`/api/products/${productId}/images`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error('Failed to upload images');
    }
}

async function deleteImage(imageId) {
    if (!confirm('האם אתה בטוח שברצונך למחוק תמונה זו?')) {
        return;
    }

    try {
        const response = await fetch(`/api/images/${imageId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            if (currentProductId) {
                loadProductDetails(currentProductId);
            }
            alert('התמונה נמחקה בהצלחה');
        } else {
            alert('שגיאה במחיקת תמונה');
        }
    } catch (error) {
        console.error('Error deleting image:', error);
        alert('שגיאה במחיקת תמונה');
    }
}

async function deleteProduct(id) {
    if (!confirm('האם אתה בטוח שברצונך למחוק מוצר זה? כל התמונות שלו יימחקו גם כן.')) {
        return;
    }

    try {
        const response = await fetch(`/api/products/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadProducts();
            alert('המוצר נמחק בהצלחה');
        } else {
            alert('שגיאה במחיקת מוצר');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        alert('שגיאה במחיקת מוצר');
    }
}
