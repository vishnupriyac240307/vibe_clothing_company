from flask import Blueprint, request, make_response, flash, redirect, url_for
from models.material import Material
from models.product import Product
from models.production import ProductionOrder
from models.batch import Batch
from models.quality import QualityInspection
from models.shipment import Shipment
from models.customer import Customer
from models.supplier import Supplier
from db import db
from services.export_service import ExportService
from utils.decorators import login_required
from utils.helpers import format_inr

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/export/<module>')
@login_required
def export(module):
    fmt = request.args.get('format', 'pdf').lower()
    charts_flowables = None

    if module == 'inventory':
        title = "Inventory Materials Report"
        headers = ["Material ID", "Material Name", "Category", "Quantity", "Unit", "Unit Cost (₹)", "Total Value (₹)", "Status"]
        materials = Material.query.all()
        rows = [
            [m.material_id, m.name, m.category, f"{m.quantity:.2f}", m.unit, format_inr(m.unit_cost), format_inr(m.total_value), m.status]
            for m in materials
        ]
    elif module == 'analytics':
        title = "Factory Analytics & Executive Intelligence Report"
        headers = ["Metric Category", "Indicator / Entity Description", "Volume / Count", "Financial Value (₹)", "Operational Status"]
        rows = []
        
        # 1. Production Status Breakdown
        orders_status = db.session.query(
            ProductionOrder.status, db.func.count(ProductionOrder.id)
        ).group_by(ProductionOrder.status).all()
        for status, count in orders_status:
            rows.append(["Production Status", f"Orders in {status}", f"{count} Orders", "-", "Active System Record"])
            
        # 2. Inventory Category Valuations
        cat_values = db.session.query(
            Material.category,
            db.func.sum(Material.quantity * Material.unit_cost),
            db.func.count(Material.id)
        ).group_by(Material.category).all()
        for cat, val, count in cat_values:
            if cat:
                rows.append(["Inventory Valuation", f"Category: {cat}", f"{count} Material Types", format_inr(val or 0), "Stock Asset Valuation"])

        # 3. Top Products Target & Stock
        top_products = Product.query.order_by(Product.target_quantity.desc()).limit(5).all()
        for p in top_products:
            total_val = p.selling_price * p.available_stock
            rows.append(["Top Products", f"{p.name} ({p.product_id})", f"{p.available_stock} Stock / {p.target_quantity} Target", format_inr(total_val), p.status])

        # 4. Customer Order Volume & Spend
        customers = Customer.query.all()
        for c in customers:
            c_orders = ProductionOrder.query.filter_by(customer_id=c.customer_id).all()
            if len(c_orders) > 0:
                spend = sum((o.product.selling_price * o.quantity) for o in c_orders if o.product)
                rows.append(["Customer Spend", f"{c.company_name} ({c.customer_id})", f"{len(c_orders)} Orders", format_inr(spend), c.status])

        # 5. Quality Defect Summary
        defects = db.session.query(
            QualityInspection.defect_type,
            db.func.sum(QualityInspection.defective_units)
        ).group_by(QualityInspection.defect_type).all()
        for dtype, dcount in defects:
            if dtype:
                rows.append(["Quality Defects", f"Defect Type: {dtype}", f"{int(dcount or 0)} Defective Units", "-", "Quality Inspection Log"])

        # Prepare chart data arrays for ReportLab visual charts
        analytics_chart_data = {
            'status_labels': [s[0] for s in orders_status],
            'status_values': [s[1] for s in orders_status],
            'cat_labels': [c[0] for c in cat_values if c[0]],
            'cat_values': [round(float(c[1] or 0), 2) for c in cat_values if c[0]],
            'prod_names': [p.name for p in top_products],
            'prod_targets': [p.target_quantity for p in top_products],
            'prod_stocks': [p.available_stock for p in top_products],
            'qc_labels': [d[0] for d in defects if d[0]],
            'qc_values': [int(d[1] or 0) for d in defects if d[0]]
        }
        charts_flowables = ExportService.generate_analytics_charts_flowables(analytics_chart_data)
    elif module == 'products':
        title = "Products Master Report"
        headers = ["Product ID", "Product Name", "Category", "Size", "Color", "Selling Price (₹)", "Cost Price (₹)", "Stock", "Status"]
        products = Product.query.all()
        rows = [
            [p.product_id, p.name, p.category, p.size, p.color or 'N/A', format_inr(p.selling_price), format_inr(p.cost_price), p.available_stock, p.status]
            for p in products
        ]
    elif module == 'production':
        title = "Production Orders Report"
        headers = ["Order ID", "Product ID", "Product Name", "Quantity", "Customer", "Priority", "Readiness %", "Status"]
        orders = ProductionOrder.query.all()
        rows = [
            [o.order_id, o.product_id, o.product.name if o.product else 'N/A', o.quantity, o.customer.company_name if o.customer else 'Internal', o.priority, f"{o.readiness_score:.1f}%", o.status]
            for o in orders
        ]
    elif module == 'batches':
        title = "Production Batches Report"
        headers = ["Batch ID", "Order ID", "Product ID", "Target Qty", "Produced Qty", "Stage", "Supervisor", "Status"]
        batches = Batch.query.all()
        rows = [
            [b.batch_id, b.production_order_id, b.product_id, b.target_quantity, b.produced_quantity, b.current_stage, b.supervisor or 'N/A', b.status]
            for b in batches
        ]
    elif module == 'quality':
        title = "Quality Control Inspections Report"
        headers = ["Inspection ID", "Batch ID", "Product ID", "Evaluated", "Defects", "Passed", "Pass Rate %", "Status"]
        inspections = QualityInspection.query.all()
        rows = [
            [q.inspection_id, q.batch_id, q.product_id, q.total_evaluated, q.defective_units, q.passed_units, f"{q.pass_rate:.1f}%", q.qa_status]
            for q in inspections
        ]
    elif module == 'shipments':
        title = "Outbound Shipments Report"
        headers = ["Shipment ID", "Product ID", "Customer", "Quantity", "Carrier", "Tracking No", "Status"]
        shipments = Shipment.query.all()
        rows = [
            [s.shipment_id, s.product_id, s.customer.company_name if s.customer else 'N/A', s.quantity, s.carrier, s.tracking_number or 'N/A', s.status]
            for s in shipments
        ]
    else:
        flash("Invalid report module requested.", "danger")
        return redirect(url_for('dashboard.index'))

    if fmt == 'pdf':
        content = ExportService.export_pdf(title, headers, rows, charts_flowables=charts_flowables)
        response = make_response(content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=vibe_clothing_{module}_report.pdf'
        return response
    elif fmt == 'excel':
        content = ExportService.export_excel(title, headers, rows)
        response = make_response(content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=vibe_clothing_{module}_report.xlsx'
        return response
    elif fmt == 'csv':
        content = ExportService.export_csv(headers, rows)
        response = make_response(content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=vibe_clothing_{module}_report.csv'
        return response
    else:
        flash("Invalid report format requested.", "danger")
        return redirect(url_for('dashboard.index'))
