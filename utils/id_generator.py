import re
from db import db

ID_PREFIXES = {
    'product': ('PROD-', 'products', 'product_id'),
    'material': ('MAT-', 'materials', 'material_id'),
    'production_order': ('ORD-', 'production_orders', 'order_id'),
    'batch': ('BAT-', 'batches', 'batch_id'),
    'customer': ('CUS-', 'customers', 'customer_id'),
    'supplier': ('SUP-', 'suppliers', 'supplier_id'),
    'shipment': ('SHP-', 'shipments', 'shipment_id'),
    'inventory_transaction': ('INV-TXN-', 'inventory_transactions', 'transaction_id'),
    'quality_inspection': ('QC-', 'quality_inspections', 'inspection_id'),
    'user': ('USR-', 'users', 'user_id')
}

def generate_next_id(entity_type):
    """
    Generates automatic sequential unique formatted IDs:
    Products -> PROD-0001
    Materials -> MAT-0001
    Production Orders -> ORD-0001
    Batches -> BAT-0001
    Customers -> CUS-0001
    Suppliers -> SUP-0001
    Shipments -> SHP-0001
    Inventory Transactions -> INV-TXN-0001
    Quality Inspections -> QC-0001
    Users -> USR-0001
    """
    if entity_type not in ID_PREFIXES:
        raise ValueError(f"Unknown entity type for ID generation: {entity_type}")

    prefix, table_name, column_name = ID_PREFIXES[entity_type]
    
    # Query all existing IDs with that prefix
    query = f"SELECT {column_name} FROM {table_name} WHERE {column_name} LIKE '{prefix}%'"
    result = db.session.execute(db.text(query)).fetchall()
    
    max_num = 0
    for row in result:
        val = row[0]
        match = re.search(r'(\d+)$', val)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
                
    next_num = max_num + 1
    return f"{prefix}{next_num:04d}"
