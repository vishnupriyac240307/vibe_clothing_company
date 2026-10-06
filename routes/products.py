from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.product import Product, ProductBOM
from models.material import Material
from services.image_service import ImageService
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity, format_inr

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
@login_required
def index():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    view_mode = request.args.get('view', 'grid').strip() # grid or table

    query = Product.query

    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.product_id.ilike(f"%{search}%")) |
            (Product.color.ilike(f"%{search}%")) |
            (Product.size.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)

    products = query.order_by(Product.created_at.desc()).all()

    categories = db.session.query(Product.category).distinct().all()
    category_list = [c[0] for c in categories if c[0]]

    materials = Material.query.order_by(Material.name.asc()).all()

    # Formatted prices for UI display
    product_list = []
    for p in products:
        p_dict = p.to_dict()
        p_dict['formatted_selling_price'] = format_inr(p.selling_price)
        p_dict['formatted_cost_price'] = format_inr(p.cost_price)
        p_dict['formatted_total_stock_value'] = format_inr(p.available_stock * p.cost_price)
        product_list.append(p_dict)

    return render_template(
        'products/index.html',
        products=product_list,
        materials=materials,
        categories=category_list,
        view_mode=view_mode,
        search=search,
        selected_category=category,
        selected_status=status
    )

@products_bp.route('/products/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def add_product():
    try:
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'T-Shirts').strip()
        description = request.form.get('description', '').strip()
        size = request.form.get('size', 'M').strip()
        color = request.form.get('color', '').strip()
        selling_price = float(request.form.get('selling_price', 0.0))
        cost_price = float(request.form.get('cost_price', 0.0))
        target_quantity = int(request.form.get('target_quantity', 100))
        custom_image_url = request.form.get('image_url', '').strip()

        if not name:
            flash('Product name is required.', 'danger')
            return redirect(url_for('products.index'))

        product_id = generate_next_id('product')

        # Auto-fetch image if custom URL not provided
        if custom_image_url:
            image_url = custom_image_url
        else:
            image_url = ImageService.get_product_image(name, category)

        product = Product(
            product_id=product_id,
            name=name,
            category=category,
            description=description,
            image_url=image_url,
            size=size,
            color=color,
            selling_price=selling_price,
            cost_price=cost_price,
            target_quantity=target_quantity,
            available_stock=0,
            status='Active'
        )

        db.session.add(product)
        db.session.flush() # Flush to associate BOM items

        # Process BOM items from form arrays (material_ids[], quantity_required[])
        material_ids = request.form.getlist('material_id[]')
        quantities = request.form.getlist('quantity_required[]')

        for mat_id, qty in zip(material_ids, quantities):
            if mat_id and qty:
                try:
                    bom_qty = float(qty)
                    if bom_qty > 0:
                        bom_item = ProductBOM(
                            product_id=product_id,
                            material_id=mat_id,
                            quantity_required=bom_qty
                        )
                        db.session.add(bom_item)
                except ValueError:
                    continue

        db.session.commit()

        log_activity('Add Product', 'Products', f"Created product {name} with Product ID {product_id} and prices Selling: {format_inr(selling_price)}, Cost: {format_inr(cost_price)}.", record_id=product_id)
        flash(f"Product {name} ({product_id}) created successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating product: {str(e)}", 'danger')

    return redirect(url_for('products.index'))

@products_bp.route('/products/edit/<product_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def edit_product(product_id):
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    try:
        product.name = request.form.get('name', product.name).strip()
        product.category = request.form.get('category', product.category).strip()
        product.description = request.form.get('description', product.description).strip()
        product.size = request.form.get('size', product.size).strip()
        product.color = request.form.get('color', product.color).strip()
        product.selling_price = float(request.form.get('selling_price', product.selling_price))
        product.cost_price = float(request.form.get('cost_price', product.cost_price))
        product.target_quantity = int(request.form.get('target_quantity', product.target_quantity))
        product.status = request.form.get('status', product.status)

        custom_image_url = request.form.get('image_url', '').strip()
        if custom_image_url:
            product.image_url = custom_image_url

        # Update BOM
        ProductBOM.query.filter_by(product_id=product_id).delete()

        material_ids = request.form.getlist('material_id[]')
        quantities = request.form.getlist('quantity_required[]')

        for mat_id, qty in zip(material_ids, quantities):
            if mat_id and qty:
                try:
                    bom_qty = float(qty)
                    if bom_qty > 0:
                        bom_item = ProductBOM(
                            product_id=product_id,
                            material_id=mat_id,
                            quantity_required=bom_qty
                        )
                        db.session.add(bom_item)
                except ValueError:
                    continue

        db.session.commit()
        log_activity('Edit Product', 'Products', f"Updated product details and BOM for {product.name} ({product_id}).", record_id=product_id)
        flash(f"Product {product.name} updated successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating product: {str(e)}", 'danger')

    return redirect(url_for('products.index'))

@products_bp.route('/products/delete/<product_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def delete_product(product_id):
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    p_name = product.name
    try:
        # Check production orders referencing this product
        related_orders = ProductionOrder.query.filter_by(product_id=product_id).count()
        if related_orders > 0:
            flash(f"Cannot delete product '{p_name}' ({product_id}) because it is referenced in {related_orders} production order(s). Delete or disassociate related orders first.", 'warning')
            return redirect(url_for('products.index'))

        # Delete associated BOM items
        ProductBOM.query.filter_by(product_id=product_id).delete()

        db.session.delete(product)
        db.session.commit()
        user_id = session.get('username', 'System')
        log_activity('Delete Product', 'Products', f"Deleted product {p_name} ({product_id}).", record_id=product_id, user_id=user_id)
        flash(f"Product '{p_name}' ({product_id}) deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting product: {str(e)}", 'danger')

    return redirect(url_for('products.index'))



@products_bp.route('/api/products/<product_id>/bom')
@login_required
def get_product_bom(product_id):
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    return jsonify({
        'success': True,
        'product_id': product.product_id,
        'product_name': product.name,
        'bom': [item.to_dict() for item in product.bom_items]
    })
