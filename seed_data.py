"""
Expanded Real Garment Manufacturing Seed Data Generator for Vibe Clothing Company ERP.
Populates 25+ Materials, 30+ Products, 25+ Customers, 25+ Suppliers, 45+ Production Orders,
50+ Batches, 70+ Inventory Transactions, 45+ Quality Control Inspections, 45+ Shipments,
ProductBOM mappings, Activity Logs, and System Notifications across a 5-month historical timeline.
"""

from datetime import datetime, timedelta, timezone
from db import db
from models.user import User
from models.supplier import Supplier
from models.customer import Customer
from models.material import Material
from models.product import Product, ProductBOM
from models.production import ProductionOrder
from models.batch import Batch
from models.quality import QualityInspection
from models.shipment import Shipment
from models.transaction import InventoryTransaction
from models.activity import ActivityLog
from models.notification import Notification

def populate_database():
    """Populates the database with massive, interconnected manufacturing ERP dataset."""
    
    # 0. Clear existing data if needed or ensure fresh baseline
    db.session.query(Notification).delete()
    db.session.query(ActivityLog).delete()
    db.session.query(InventoryTransaction).delete()
    db.session.query(Shipment).delete()
    db.session.query(QualityInspection).delete()
    db.session.query(Batch).delete()
    db.session.query(ProductionOrder).delete()
    db.session.query(ProductBOM).delete()
    db.session.query(Product).delete()
    db.session.query(Material).delete()
    db.session.query(Customer).delete()
    db.session.query(Supplier).delete()
    db.session.query(User).delete()
    db.session.commit()

    print("Generating expanded garment manufacturing seed dataset...")

    # Base date reference (Current date: Oct 2026)
    base_date = datetime.now(timezone.utc).date()

    # ---------------------------------------------------------
    # 1. USERS
    # ---------------------------------------------------------
    admin = User(user_id='USR-0001', username='admin', email='admin@vibeclothing.com', phone='+91 98765 43210', role='admin', is_active=True)
    admin.set_password('admin123')

    manager = User(user_id='USR-0002', username='manager', email='manager@vibeclothing.com', phone='+91 98765 43211', role='manager', is_active=True)
    manager.set_password('manager123')

    staff = User(user_id='USR-0003', username='staff', email='staff@vibeclothing.com', phone='+91 98765 43212', role='staff', is_active=True)
    staff.set_password('staff123')

    db.session.add_all([admin, manager, staff])
    db.session.flush()

    # ---------------------------------------------------------
    # 2. SUPPLIERS (25 Realistic Vendors)
    # ---------------------------------------------------------
    suppliers_data = [
        ('SUP-0001', 'Southern Textile Mills', 'Rajesh Sharma', 'sales@southerntextiles.in', '+91 44 2345 6789', '33AAACA1234A1Z5', '12 Industrial Estate, Guindy', 'Chennai', 'Tamil Nadu', 'Fabrics', 'Net 30', 4.8),
        ('SUP-0002', 'Chennai Fabric Suppliers', 'Suresh Kumar', 'info@chennaifabrics.com', '+91 44 8765 4321', '33BBBBA5678B1Z2', '45 Textile Hub', 'Tirupur', 'Tamil Nadu', 'Knitted Fabrics', 'Net 15', 4.5),
        ('SUP-0003', 'Premium Threads Pvt Ltd', 'Anita Roy', 'orders@premiumthreads.in', '+91 80 4123 9988', '29CCCCA9988C1Z9', '88 Garment Zone, Peenya', 'Bengaluru', 'Karnataka', 'Threads & Yarns', 'Advance', 4.9),
        ('SUP-0004', 'DenimCraft Mills Ltd', 'Vikram Patel', 'contact@denimcraft.in', '+91 79 2654 1122', '24DDDDD1122D1Z3', '101 GIDC Industrial Area', 'Ahmedabad', 'Gujarat', 'Denim Fabrics', 'Net 45', 4.7),
        ('SUP-0005', 'National Trims & Fasteners', 'Manish Gupta', 'sales@nationaltrims.com', '+91 22 2850 4455', '27EEEEE4455E1Z7', '34 MIDC Andheri East', 'Mumbai', 'Maharashtra', 'Buttons & Zippers', 'Net 30', 4.6),
        ('SUP-0006', 'Apex Packaging Solutions', 'Kavita Menon', 'support@apexpack.in', '+91 422 2541 8899', '33FFFFF8899F1Z1', '67 Hope College Road', 'Coimbatore', 'Tamil Nadu', 'Packaging', 'Net 15', 4.4),
        ('SUP-0007', 'EcoDye & Chemical Processing', 'Dr. Arul Nathan', 'orders@ecodye.in', '+91 421 2478 3344', '33GGGGG3344G1Z8', '89 SIPCOT Complex', 'Perundurai', 'Tamil Nadu', 'Dyes & Chemicals', 'Net 30', 4.8),
        ('SUP-0008', 'Royal Interlining Corp', 'Siddharth Rao', 'info@royalinterlining.com', '+91 80 2334 7711', '29HHHHH7711H1Z4', '12 Rajajinagar Ind Area', 'Bengaluru', 'Karnataka', 'Interlining', 'Net 30', 4.3),
        ('SUP-0009', 'Silk & Rayon Weavers', 'Meenakshi Sundaram', 'sales@silkrayon.in', '+91 452 2301 6655', '33IIIII6655I1Z0', '56 Ring Road', 'Madurai', 'Tamil Nadu', 'Rayon & Linen', 'Net 30', 4.5),
        ('SUP-0010', 'Tirupur Elastic & Tape Mills', 'K. Balakrishnan', 'orders@tirupurelastic.com', '+91 421 2234 5566', '33JJJJJ5566J1Z6', '23 PN Road', 'Tirupur', 'Tamil Nadu', 'Elastic & Tapes', 'Net 15', 4.6),
        ('SUP-0011', 'Global Label Printers', 'Pooja Verma', 'sales@globallabels.in', '+91 11 4152 8800', '07KKKKK8800K1Z2', '78 Okhla Industrial Area', 'New Delhi', 'Delhi', 'Labels & Tags', 'Advance', 4.9),
        ('SUP-0012', 'Spandex Global India', 'David Miller', 'india@spandexglobal.com', '+91 22 6123 9900', '27LLLLL9900L1Z9', '90 BKC Commercial Hub', 'Mumbai', 'Maharashtra', 'Synthetic Fabrics', 'Net 30', 4.7),
        ('SUP-0013', 'Modern Printing Inks Ltd', 'Alok Chatterjee', 'orders@moderninks.in', '+91 33 2400 1122', '19MMMMM1122M1Z5', '45 Salt Lake Sector V', 'Kolkata', 'West Bengal', 'Printing Inks', 'Net 30', 4.4),
        ('SUP-0014', 'Heritage Woolen Spinners', 'Gurpreet Singh', 'sales@heritagewool.in', '+91 161 2500 3344', '03NNNNN3344N1Z1', '12 Focal Point', 'Ludhiana', 'Punjab', 'Wool Fabrics', 'Net 45', 4.8),
        ('SUP-0015', 'Precision Fasteners Ltd', 'Ramesh Iyer', 'info@precisionfasteners.in', '+91 44 2625 7788', '33OOOOO7788O1Z7', '89 Ambattur Ind Estate', 'Chennai', 'Tamil Nadu', 'Zippers & Pins', 'Net 30', 4.5),
        ('SUP-0016', 'GreenCotton Organic Fibers', 'Sunita Reddy', 'organic@greencotton.in', '+91 40 2311 4455', '36PPPPP4455P1Z3', '56 Gachibowli Tech Park', 'Hyderabad', 'Telangana', 'Organic Cotton', 'Advance', 4.9),
        ('SUP-0017', 'Smart Packaging Box Ind', 'Nitin Shah', 'orders@smartpackbox.com', '+91 79 2589 2233', '24QQQQQ2233Q1Z8', '34 Changodar Ind Zone', 'Ahmedabad', 'Gujarat', 'Corrugated Boxes', 'Net 15', 4.3),
        ('SUP-0018', 'Vibrant Colors Chemical Co', 'Dr. S. K. Bose', 'sales@vibrantcolors.in', '+91 265 2334 6677', '24RRRRR6677R1Z4', '12 Nandesari Ind Area', 'Vadodara', 'Gujarat', 'Washing Chemicals', 'Net 30', 4.6),
        ('SUP-0019', 'Zenith Ribbon & Trim Co', 'Priya Joshi', 'info@zenithribbon.com', '+91 80 2839 5511', '29SSSSS5511S1Z0', '67 Peenya 3rd Stage', 'Bengaluru', 'Karnataka', 'Ribbons & Piping', 'Net 30', 4.5),
        ('SUP-0020', 'Coast Thread India', 'Antony Cruz', 'sales@coastthread.in', '+91 484 2390 1122', '32TTTTT1122T1Z6', '45 Kalamassery Ind Estate', 'Kochi', 'Kerala', 'Sewing Threads', 'Net 30', 4.7),
        ('SUP-0021', 'Metro Buttons & Rivets', 'Harish Chawla', 'orders@metrobuttons.in', '+91 11 2541 3344', '07UUUUU3344U1Z2', '23 Mayapuri Ind Area', 'New Delhi', 'Delhi', 'Buttons & Rivets', 'Net 15', 4.4),
        ('SUP-0022', 'Sunweave Knits Tirupur', 'M. Shanmugam', 'info@sunweaveknits.com', '+91 421 2489 7788', '33VVVVV7788V1Z9', '78 College Road', 'Tirupur', 'Tamil Nadu', 'Terry & Knits', 'Net 30', 4.8),
        ('SUP-0023', 'Apex Accessories India', 'Deepak Tandon', 'sales@apexaccessories.in', '+91 22 2834 9900', '27WWWWW9900W1Z5', '12 Marol Naka', 'Mumbai', 'Maharashtra', 'Garment Accessories', 'Net 30', 4.3),
        ('SUP-0024', 'Pioneer Woven Labels', 'Geetha Nair', 'orders@pioneerlabels.com', '+91 44 2250 1122', '33XXXXX1122X1Z1', '45 Thiruvanmiyur', 'Chennai', 'Tamil Nadu', 'Woven Labels', 'Advance', 4.7),
        ('SUP-0025', 'Frontier Logistics Supplies', 'Ajay Deshmukh', 'sales@frontierlogistics.in', '+91 20 2712 4455', '27YYYYY4455Y1Z8', '89 Bhosari Ind Area', 'Pune', 'Maharashtra', 'Packaging Tapes', 'Net 15', 4.4)
    ]

    suppliers_list = []
    for sid, sname, cperson, email, phone, gst, addr, city, state, cat, pterms, rat in suppliers_data:
        logo = f"https://ui-avatars.com/api/?name={sname.replace(' ', '+')}&background=0f172a&color=38bdf8"
        s = Supplier(supplier_id=sid, supplier_name=sname, logo_url=logo, contact_person=cperson, email=email, phone=phone, gst_id=gst, address=addr, city=city, state=state, supplier_category=cat, payment_terms=pterms, rating=rat)
        suppliers_list.append(s)

    db.session.add_all(suppliers_list)
    db.session.flush()

    # ---------------------------------------------------------
    # 3. MATERIALS / INVENTORY (30 Items with Varied Stock States)
    # ---------------------------------------------------------
    materials_data = [
        # (ID, Name, Code, Category, Description, Qty, Unit, Color, Min, Reorder, Crit, UnitCost, SupID, Location, Lot)
        ('MAT-0001', 'Cotton Fabric', 'MAT-COT-01', 'Fabric', '100% Organic Combed Cotton 180 GSM', 650.0, 'Meter', 'Super White', 100.0, 150.0, 50.0, 250.00, 'SUP-0001', 'Rack A-12', 'LOT-COT-2026-01'), # OK
        ('MAT-0002', 'Merino Wool Fabric', 'MAT-WOL-01', 'Fabric', 'Premium Australian Merino Wool Blend', 85.0, 'Meter', 'Navy Blue', 100.0, 150.0, 30.0, 550.00, 'SUP-0014', 'Rack A-14', 'LOT-WOL-2026-02'), # LOW
        ('MAT-0003', 'Polyester Sewing Thread', 'MAT-TRD-01', 'Trims', 'High-Tenacity Polyester Thread 40/2', 12000.0, 'Meter', 'White & Black', 2000.0, 3000.0, 800.0, 2.50, 'SUP-0003', 'Bin T-04', 'LOT-TRD-2026-05'), # OK
        ('MAT-0004', 'Resin Shirt Buttons', 'MAT-BTN-01', 'Accessories', 'Resin 4-Hole Shirt Buttons 18L', 8500.0, 'PCS', 'Matte Black', 1500.0, 2000.0, 500.0, 4.50, 'SUP-0005', 'Bin B-02', 'LOT-BTN-2026-09'), # OK
        ('MAT-0005', 'Stainless Steel Pins', 'MAT-PIN-01', 'Accessories', 'Stainless Steel Garment Folding Pins', 180.0, 'PCS', 'Silver', 800.0, 1000.0, 200.0, 1.50, 'SUP-0015', 'Bin B-05', 'LOT-PIN-2026-01'), # CRITICAL
        ('MAT-0006', 'Reactive Dye Liquid', 'MAT-DYE-01', 'Chemicals', 'Eco-Friendly Reactive Royal Blue Dye', 45.0, 'Liter', 'Royal Blue', 50.0, 75.0, 15.0, 360.00, 'SUP-0007', 'Drum C-01', 'LOT-DYE-2026-03'), # LOW
        ('MAT-0007', 'Indigo Denim Fabric', 'MAT-DEN-01', 'Fabric', 'Heavyweight 14oz Slub Denim Fabric', 1200.0, 'Meter', 'Dark Indigo', 300.0, 450.0, 100.0, 380.00, 'SUP-0004', 'Rack D-01', 'LOT-DEN-2026-08'), # OK
        ('MAT-0008', 'Single Jersey Knit Fabric', 'MAT-JRS-01', 'Fabric', '100% Combed Cotton Jersey 160 GSM', 800.0, 'Meter', 'Heather Grey', 200.0, 300.0, 50.0, 220.00, 'SUP-0002', 'Rack J-03', 'LOT-JRS-2026-04'), # OK
        ('MAT-0009', 'Cotton Rib Knit Fabric', 'MAT-RIB-01', 'Fabric', '2x2 Stretch Cotton Rib Collar Material', 160.0, 'Meter', 'Charcoal', 150.0, 220.0, 40.0, 240.00, 'SUP-0002', 'Rack J-05', 'LOT-RIB-2026-02'), # NEAR REORDER
        ('MAT-0010', 'French Terry Fabric', 'MAT-TRY-01', 'Fabric', '320 GSM Loopback Cotton Terry Knit', 950.0, 'Meter', 'Black', 250.0, 350.0, 80.0, 310.00, 'SUP-0022', 'Rack T-02', 'LOT-TRY-2026-11'), # OK
        ('MAT-0011', 'Spandex Stretch Fabric', 'MAT-SPX-01', 'Fabric', '4-Way Stretch Nylon Spandex 220 GSM', 90.0, 'Meter', 'Crimson Red', 100.0, 150.0, 25.0, 420.00, 'SUP-0012', 'Rack S-01', 'LOT-SPX-2026-06'), # LOW
        ('MAT-0012', 'Nylon Zipper 7-inch', 'MAT-ZIP-01', 'Trims', '7-Inch Nylon Concealed Zipper', 120.0, 'PCS', 'Navy', 1000.0, 1500.0, 300.0, 12.00, 'SUP-0005', 'Bin Z-01', 'LOT-ZIP-2026-07'), # CRITICAL
        ('MAT-0013', 'Garment Packaging Poly Bags', 'MAT-PKG-01', 'Packaging', 'Transparent Polyethylene Poly Bags', 15000.0, 'PCS', 'Clear', 3000.0, 4500.0, 1000.0, 1.80, 'SUP-0006', 'Pallet P-01', 'LOT-PKG-2026-12'), # OK
        ('MAT-0014', 'Heavy Corrugated Cartons', 'MAT-CTN-01', 'Packaging', '5-Ply Shipping Outer Cartons', 2200.0, 'PCS', 'Kraft Brown', 500.0, 800.0, 150.0, 45.00, 'SUP-0017', 'Pallet P-04', 'LOT-CTN-2026-03'), # OK
        ('MAT-0015', 'Printed Wash Care Labels', 'MAT-LBL-01', 'Labels', 'Satin Printed Wash Care Instruction Labels', 5200.0, 'PCS', 'White/Black', 5000.0, 7500.0, 1000.0, 1.20, 'SUP-0011', 'Bin L-02', 'LOT-LBL-2026-09'), # NEAR REORDER
        ('MAT-0016', 'Brand Woven Neck Labels', 'MAT-LBL-02', 'Labels', 'High-Density Woven Vibe Brand Labels', 25000.0, 'PCS', 'Red/White', 5000.0, 8000.0, 1500.0, 2.20, 'SUP-0024', 'Bin L-01', 'LOT-LBL-2026-10'), # OK
        ('MAT-0017', 'Cardstock Garment Hang Tags', 'MAT-TAG-01', 'Labels', '350 GSM Matte Cardstock Brand Hang Tags', 50000.0, 'PCS', 'Vibe Red', 5000.0, 8000.0, 1000.0, 3.50, 'SUP-0011', 'Bin L-05', 'LOT-TAG-2026-01'), # OVERSTOCKED
        ('MAT-0018', 'Non-Woven Fusible Interlining', 'MAT-ITL-01', 'Interlining', 'Polyester Fusible Collar/Cuff Interlining', 110.0, 'Meter', 'White', 120.0, 180.0, 40.0, 85.00, 'SUP-0008', 'Rack I-01', 'LOT-ITL-2026-05'), # LOW
        ('MAT-0019', 'Collar Canvas Canvas', 'MAT-ITL-02', 'Interlining', 'Heavy Woven Cotton Canvas Interlining', 35.0, 'Meter', 'Off-White', 150.0, 220.0, 50.0, 95.00, 'SUP-0008', 'Rack I-02', 'LOT-ITL-2026-06'), # CRITICAL
        ('MAT-0020', 'Braided Cotton Drawstrings', 'MAT-DST-01', 'Trims', 'Flat Braided Hooded Drawstring Cords', 850.0, 'Meter', 'White', 800.0, 1200.0, 200.0, 14.00, 'SUP-0010', 'Bin D-01', 'LOT-DST-2026-03'), # NEAR REORDER
        ('MAT-0021', 'Knitted Elastic Tape 1.5"', 'MAT-ELT-01', 'Trims', 'High-Resilience Waistband Elastic Tape', 450.0, 'Meter', 'White', 500.0, 750.0, 100.0, 18.00, 'SUP-0010', 'Bin E-02', 'LOT-ELT-2026-04'), # LOW
        ('MAT-0022', 'Heavy Duty Packing Tape', 'MAT-TAP-01', 'Packaging', 'Self-Adhesive Branded Packing Tape', 800.0, 'Roll', 'Transparent', 100.0, 200.0, 20.0, 65.00, 'SUP-0025', 'Pallet P-05', 'LOT-TAP-2026-08'), # OVERSTOCKED
        ('MAT-0023', 'Open-End Plastic Zipper 24"', 'MAT-ZIP-02', 'Trims', 'Heavy Duty Plastic Molded Zipper 24"', 650.0, 'PCS', 'Black', 600.0, 900.0, 150.0, 22.00, 'SUP-0005', 'Bin Z-03', 'LOT-ZIP-2026-11'), # NEAR REORDER
        ('MAT-0024', 'Plastisol Screen Printing Ink', 'MAT-INK-01', 'Printing', 'High-Opacity White Plastisol Printing Ink', 18.0, 'Liter', 'Pure White', 20.0, 30.0, 5.0, 550.00, 'SUP-0013', 'Shelf C-04', 'LOT-INK-2026-02'), # LOW
        ('MAT-0025', 'Biowash Enzyme Compound', 'MAT-CHM-01', 'Chemicals', 'Concentrated Textile Bio-Polishing Enzyme', 800.0, 'Liter', 'Clear Liquid', 100.0, 200.0, 20.0, 180.00, 'SUP-0018', 'Drum C-08', 'LOT-CHM-2026-09'), # OVERSTOCKED
        ('MAT-0026', 'Metal Jeans Buttons 24L', 'MAT-BTN-02', 'Accessories', 'Antique Brass Tack Metal Jeans Buttons', 150.0, 'PCS', 'Antique Brass', 1200.0, 1800.0, 300.0, 8.50, 'SUP-0021', 'Bin B-08', 'LOT-BTN-2026-14'), # CRITICAL
        ('MAT-0027', 'Organic Cotton GOTS Fabric', 'MAT-ORG-01', 'Fabric', 'GOTS Certified Organic Jersey 180 GSM', 0.0, 'Meter', 'Natural Beige', 200.0, 300.0, 50.0, 320.00, 'SUP-0016', 'Rack A-20', 'LOT-ORG-2026-01'), # OUT OF STOCK
        ('MAT-0028', 'Brass Metal Zipper 8-inch', 'MAT-ZIP-03', 'Trims', 'Brass Tooth Heavy Metal Zipper for Denim', 0.0, 'PCS', 'Antique Brass', 500.0, 800.0, 100.0, 35.00, 'SUP-0015', 'Bin Z-09', 'LOT-ZIP-2026-04'), # OUT OF STOCK
        ('MAT-0029', 'Slub Rayon Fabric', 'MAT-RAY-01', 'Fabric', 'Soft Breathable Slub Rayon Woven 140 GSM', 0.0, 'Meter', 'Olive Green', 150.0, 250.0, 40.0, 270.00, 'SUP-0009', 'Rack R-01', 'LOT-RAY-2026-03'), # OUT OF STOCK
        ('MAT-0030', 'Linen Blend Fabric', 'MAT-LIN-01', 'Fabric', '55/45 Linen Cotton Blend Fabric 200 GSM', 0.0, 'Meter', 'Sand Khaki', 180.0, 280.0, 45.0, 390.00, 'SUP-0009', 'Rack L-04', 'LOT-LIN-2026-05')  # OUT OF STOCK
    ]

    materials_dict = {}
    for mid, mname, code, cat, desc, qty, unit, col, minl, reord, crit, ucost, supid, loc, lot in materials_data:
        m = Material(material_id=mid, name=mname, code=code, category=cat, description=desc, quantity=qty, unit=unit, color=col, minimum_level=minl, reorder_level=reord, critical_level=crit, unit_cost=ucost, supplier_id=supid, storage_location=loc, batch_number=lot)
        materials_dict[mid] = m

    db.session.add_all(list(materials_dict.values()))
    db.session.flush()

    # ---------------------------------------------------------
    # 4. CUSTOMERS (25 Retail & Wholesaler Clients)
    # ---------------------------------------------------------
    customers_data = [
        ('CUS-0001', 'Flipkart India Pvt Ltd', 'Vikram Sethi', 'vendor@flipkart.com', '+91 80 4900 0000', '29AABCF1234F1Z1', 'Outer Ring Road', 'Bengaluru', 'Karnataka', 'E-Commerce'),
        ('CUS-0002', 'Amazon Retail India', 'Priya Menon', 'retail-in@amazon.com', '+91 80 4000 1111', '29AABCA9999A1Z3', 'World Trade Centre', 'Bengaluru', 'Karnataka', 'E-Commerce'),
        ('CUS-0003', 'Nykaa Fashion Retail', 'Rohan Gupta', 'fashion-sourcing@nykaa.com', '+91 22 6600 8800', '27AAACN5555N1Z8', 'Lower Parel', 'Mumbai', 'Maharashtra', 'Retail Chain'),
        ('CUS-0004', 'Myntra Designs Pvt Ltd', 'Ananya Sharma', 'vendors@myntra.com', '+91 80 6156 1900', '29AABCM8899M1Z2', 'Koramangala Ind Layout', 'Bengaluru', 'Karnataka', 'E-Commerce'),
        ('CUS-0005', 'Reliance Trends Ltd', 'Sanjay Dutt', 'sourcing@reliancetrends.com', '+91 22 4477 0000', '27AABCR1122R1Z5', 'Reliance Corporate Park', 'Navi Mumbai', 'Maharashtra', 'Retail Chain'),
        ('CUS-0006', 'Tata CLIQ Luxury', 'Kavita Iyer', 'luxury@tatacliq.com', '+91 22 6757 8899', '27AAACT9900T1Z4', 'Army & Navy Building', 'Mumbai', 'Maharashtra', 'E-Commerce'),
        ('CUS-0007', 'Lifestyle International', 'Manish Verma', 'sourcing@lifestylestores.com', '+91 80 4119 7000', '29AABCL3344L1Z9', 'Yelahanka Tech Zone', 'Bengaluru', 'Karnataka', 'Retail Chain'),
        ('CUS-0008', 'Shoppers Stop Ltd', 'Deepak Parekh', 'vendors@shoppersstop.com', '+91 22 4249 7000', '27AAACS4455S1Z1', 'Malad West', 'Mumbai', 'Maharashtra', 'Retail Chain'),
        ('CUS-0009', 'Westside Trent Ltd', 'Neha Kapur', 'apparel@trent-tata.com', '+91 22 6700 9000', '27AAACT1234T1Z6', 'Taj Building, Fort', 'Mumbai', 'Maharashtra', 'Retail Chain'),
        ('CUS-0010', 'Pantaloons Fashion', 'Rajiv Nair', 'buying@pantaloons.com', '+91 22 6750 0000', '27AABCP5566P1Z3', 'Aditya Birla Centre', 'Mumbai', 'Maharashtra', 'Retail Chain'),
        ('CUS-0011', 'Max Fashion India', 'Sunil Thomas', 'orders@maxfashion.in', '+91 80 4012 3344', '29AABCM2233M1Z8', 'Banaswadi Main Road', 'Bengaluru', 'Karnataka', 'Wholesale'),
        ('CUS-0012', 'FabIndia Overseas Pvt Ltd', 'Aarti Mehra', 'sourcing@fabindia.net', '+91 11 4051 2000', '07AAACF6677F1Z0', 'Okhla Phase 3', 'New Delhi', 'Delhi', 'Boutique Chain'),
        ('CUS-0013', 'Ajio Digital Retail', 'Varun Malhotra', 'vendor-support@ajio.com', '+91 22 3555 1122', '27AABCA7788A1Z7', 'Ghansoli', 'Navi Mumbai', 'Maharashtra', 'E-Commerce'),
        ('CUS-0014', 'Beyoung Apparel Ltd', 'Shivam Soni', 'b2b@beyoung.in', '+91 294 2411 9900', '08AAACB9900B1Z4', 'Udaipur Ind Area', 'Udaipur', 'Rajasthan', 'Clothing Brand'),
        ('CUS-0015', 'Snitch Menswear Brands', 'Siddharth Dungarwal', 'wholesale@snitch.co.in', '+91 80 4567 8900', '29AAACS1122S1Z9', 'HSR Layout', 'Bengaluru', 'Karnataka', 'Clothing Brand'),
        ('CUS-0016', 'Rare Rabbit House of Rare', 'Manish Poddar', 'b2b@thehouseofrare.com', '+91 80 4112 3456', '29AAACR3344R1Z5', 'Whitefield Ind Area', 'Bengaluru', 'Karnataka', 'Clothing Brand'),
        ('CUS-0017', 'Decathlon Sports India', 'Jean Pascal', 'supply@decathlon.in', '+91 80 6813 0000', '29AAACD5566D1Z2', 'Chikkajala', 'Bengaluru', 'Karnataka', 'Sportswear Brand'),
        ('CUS-0018', 'Zudio Retail Trent', 'Pooja Agarwal', 'zudio-buying@trent-tata.com', '+91 22 6700 9500', '27AAACZ7788Z1Z8', 'Bandra Kurla Complex', 'Mumbai', 'Maharashtra', 'Retail Chain'),
        ('CUS-0019', 'Monte Carlo Fashions', 'Rishabh Oswal', 'orders@montecarlo.in', '+91 161 5040 100', '03AAACM9900M1Z3', 'GT Road, Miller Ganj', 'Ludhiana', 'Punjab', 'Clothing Brand'),
        ('CUS-0020', 'Peter England Outlets', 'Vishal Mirchandani', 'b2b@peterengland.com', '+91 80 4049 8000', '29AAACP1122P1Z7', 'Mission Road', 'Bengaluru', 'Karnataka', 'Corporate Uniform'),
        ('CUS-0021', 'Allen Solly Retail', 'Kalyan Ram', 'allensolly@adityabirla.com', '+91 80 4049 8500', '29AAACA3344A1Z1', 'MG Road', 'Bengaluru', 'Karnataka', 'Retail Chain'),
        ('CUS-0022', 'Van Heusen India', 'Gaurav Chakravarty', 'b2b@vanheusenindia.com', '+91 80 4049 9000', '29AAACV5566V1Z6', 'Ulsoor', 'Bengaluru', 'Karnataka', 'Corporate Uniform'),
        ('CUS-0023', 'Raymond Apparel Ltd', 'Gautam Singhania', 'orders@raymond.in', '+91 22 4036 7000', '27AAACR7788R1Z2', 'Pokhran Road', 'Thane', 'Maharashtra', 'Wholesale'),
        ('CUS-0024', 'Flying Machine Denim', 'Alok Kumar', 'fm-orders@arvind.in', '+91 79 6828 8000', '24AAACF9900F1Z8', 'Naroda Road', 'Ahmedabad', 'Gujarat', 'Clothing Brand'),
        ('CUS-0025', 'Urban Style Retailers', 'Karan Johar', 'orders@urbanstyle.in', '+91 11 2641 5566', '07AAACU1122U1Z4', 'Connaught Place', 'New Delhi', 'Delhi', 'Fashion Store')
    ]

    customers_dict = {}
    for cid, ccomp, cperson, email, phone, gst, addr, city, state, ctype in customers_data:
        logo = f"https://ui-avatars.com/api/?name={ccomp.replace(' ', '+')}&background=0f172a&color=38bdf8"
        c = Customer(customer_id=cid, company_name=ccomp, logo_url=logo, contact_person=cperson, email=email, phone=phone, gst_id=gst, address=addr, city=city, state=state, customer_type=ctype)
        customers_dict[cid] = c

    db.session.add_all(list(customers_dict.values()))
    db.session.flush()

    # ---------------------------------------------------------
    # 5. PRODUCTS (30 Garment Products)
    # ---------------------------------------------------------
    products_data = [
        # (ID, Name, Cat, Desc, Img, Size, Color, SellingPrice, CostPrice, TargetQty, AvailableStock, Status)
        ('PROD-0001', 'Classic Cotton Crew T-Shirt', 'T-Shirts', 'Premium 100% Combed Cotton Crew Neck T-Shirt', 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80', 'M', 'Super White', 799.00, 350.00, 500, 240, 'Active'),
        ('PROD-0002', 'Slim Fit Stretch Denim Jeans', 'Jeans', 'Slim Fit Heavyweight Stretch Denim Jeans', 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop&q=80', '32', 'Dark Indigo', 1899.00, 850.00, 300, 115, 'Active'),
        ('PROD-0003', 'Urban Denim Trucker Jacket', 'Jackets', 'Classic Heavyweight Denim Trucker Jacket', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop&q=80', 'L', 'Indigo Wash', 2499.00, 1150.00, 200, 45, 'In Production'),
        ('PROD-0004', 'Comfort Fleece Pullover Hoodie', 'Hoodies', 'Fleece Lined Heavyweight Pullover Hoodie', 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&auto=format&fit=crop&q=80', 'XL', 'Heather Grey', 1499.00, 650.00, 250, 180, 'Active'),
        ('PROD-0005', 'Premium Pique Polo Shirt', 'Polo Shirts', 'Classic Cotton Pique Polo Shirt with Rib Collar', 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=500&auto=format&fit=crop&q=80', 'L', 'Navy Blue', 999.00, 420.00, 400, 130, 'Active'),
        ('PROD-0006', 'Oxford Formal Button-Down Shirt', 'Formal Shirts', '100% Cotton Premium Oxford Formal Shirt', 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&auto=format&fit=crop&q=80', '40', 'Sky Blue', 1299.00, 580.00, 350, 95, 'Active'),
        ('PROD-0007', 'Casual Linen Blend Summer Shirt', 'Casual Shirts', 'Lightweight Breathable Linen Blend Shirt', 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&auto=format&fit=crop&q=80', 'M', 'Sand Beige', 1399.00, 620.00, 200, 60, 'Active'),
        ('PROD-0008', 'Athletic Performance Sweatshirt', 'Sweatshirts', 'Loopback Fleece Athletic Sweatshirt', 'https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=500&auto=format&fit=crop&q=80', 'L', 'Charcoal', 1249.00, 540.00, 300, 140, 'Active'),
        ('PROD-0009', 'Chino Slim Fit Trousers', 'Trousers', 'Stretch Cotton Chino Trousers', 'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=500&auto=format&fit=crop&q=80', '34', 'Olive Khaki', 1599.00, 720.00, 250, 85, 'Active'),
        ('PROD-0010', 'Casual Denim Shorts', 'Shorts', 'Washed Denim Casual Shorts', 'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500&auto=format&fit=crop&q=80', '32', 'Light Blue', 999.00, 450.00, 200, 70, 'Active'),
        ('PROD-0011', 'Athletic Fleece Track Pants', 'Track Pants', 'Cotton Fleece Slim Fit Jogger Track Pants', 'https://images.unsplash.com/photo-1552902865-b72c031ac5ea?w=500&auto=format&fit=crop&q=80', 'L', 'Black', 1199.00, 520.00, 300, 110, 'Active'),
        ('PROD-0012', 'High-Waist Stretch Leggings', 'Leggings', '4-Way Stretch Ankle Length Leggings', 'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500&auto=format&fit=crop&q=80', 'M', 'Jet Black', 799.00, 320.00, 400, 210, 'Active'),
        ('PROD-0013', 'Women Floral Print Summer Dress', 'Dresses', 'Rayon Printed Casual Summer Dress', 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=500&auto=format&fit=crop&q=80', 'S', 'Floral Red', 1799.00, 780.00, 150, 35, 'In Production'),
        ('PROD-0014', 'A-Line Casual Cotton Skirt', 'Skirts', 'Cotton Knee-Length A-Line Skirt', 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=500&auto=format&fit=crop&q=80', 'M', 'Mustard Yellow', 1099.00, 480.00, 180, 50, 'Active'),
        ('PROD-0015', 'Kids Graphic Printed T-Shirt', 'Kids Wear', 'Soft Organic Cotton Printed Kids Tee', 'https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=500&auto=format&fit=crop&q=80', '6-7Y', 'Bright Yellow', 499.00, 210.00, 500, 280, 'Active'),
        ('PROD-0016', 'Kids Fleece Hooded Sweatshirt', 'Kids Wear', 'Cozy Fleece Lined Kids Hoodie', 'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=500&auto=format&fit=crop&q=80', '8-9Y', 'Royal Blue', 899.00, 380.00, 300, 125, 'Active'),
        ('PROD-0017', 'Dry-Fit Sports Training Tee', 'Sports Wear', 'Moisture-Wicking Polyester Sports Tee', 'https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=500&auto=format&fit=crop&q=80', 'L', 'Neon Green', 699.00, 290.00, 450, 230, 'Active'),
        ('PROD-0018', 'Performance Running Shorts', 'Sports Wear', 'Lightweight Quick-Dry Athletic Shorts', 'https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&auto=format&fit=crop&q=80', 'M', 'Steel Grey', 799.00, 340.00, 350, 160, 'Active'),
        ('PROD-0019', 'Corporate Cotton Polo Uniform', 'Uniforms', 'Heavy Duty Pique Uniform Polo Shirt', 'https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=500&auto=format&fit=crop&q=80', 'L', 'Corporate Blue', 899.00, 390.00, 600, 340, 'Active'),
        ('PROD-0020', 'Industrial Work Coverall', 'Work Wear', 'Heavy Duty Cotton Twill Work Suit', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=500&auto=format&fit=crop&q=80', 'XL', 'Safety Orange', 2199.00, 980.00, 150, 40, 'Active'),
        ('PROD-0021', 'Compression Activewear Top', 'Activewear', 'High Elasticity Compression Workout Top', 'https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=500&auto=format&fit=crop&q=80', 'M', 'Graphite', 999.00, 410.00, 250, 90, 'Active'),
        ('PROD-0022', 'Active Yoga Stretch Tights', 'Activewear', 'High-Waisted Non-See-Through Yoga Pants', 'https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=500&auto=format&fit=crop&q=80', 'S', 'Plum Purple', 1199.00, 490.00, 300, 115, 'Active'),
        ('PROD-0023', 'Organic Cotton V-Neck Tee', 'T-Shirts', 'Certified GOTS Organic V-Neck T-Shirt', 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80', 'L', 'Olive', 899.00, 390.00, 350, 150, 'Active'),
        ('PROD-0024', 'Lightweight Windbreaker Jacket', 'Jackets', 'Water-Resistant Nylon Outer Shell Jacket', 'https://images.unsplash.com/photo-1544441893-675973e31985?w=500&auto=format&fit=crop&q=80', 'XL', 'Maroon', 1999.00, 890.00, 200, 55, 'Active'),
        ('PROD-0025', 'Formal Pleated Dress Trousers', 'Formal Wear', 'Poly-Viscose Premium Formal Trousers', 'https://images.unsplash.com/photo-1479064555552-3ef4979f8908?w=500&auto=format&fit=crop&q=80', '32', 'Dark Grey', 1799.00, 790.00, 200, 70, 'Active'),
        ('PROD-0026', 'Women Denim Trucker Vest', 'Casual Wear', 'Sleeveless Washed Denim Vest', 'https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=500&auto=format&fit=crop&q=80', 'M', 'Vintage Blue', 1599.00, 680.00, 150, 45, 'Active'),
        ('PROD-0027', 'Kids Denim Overall Dungarees', 'Kids Wear', 'Adjustable Strap Denim Kids Dungarees', 'https://images.unsplash.com/photo-1519457431-44ccd64a579b?w=500&auto=format&fit=crop&q=80', '4-5Y', 'Medium Blue', 1199.00, 510.00, 200, 80, 'Active'),
        ('PROD-0028', 'School Uniform White Shirt', 'Uniforms', 'Easy Care Polyester Cotton School Shirt', 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&auto=format&fit=crop&q=80', '34', 'Pure White', 599.00, 240.00, 800, 420, 'Active'),
        ('PROD-0029', 'Hospitality Staff Blazer', 'Uniforms', 'Tailored Single-Breasted Uniform Blazer', 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=500&auto=format&fit=crop&q=80', '42', 'Midnight Navy', 2899.00, 1290.00, 120, 30, 'Active'),
        ('PROD-0030', 'Thermal Base Layer Top', 'Activewear', 'Brushed Poly Thermal Insulation Shirt', 'https://images.unsplash.com/photo-1506152983158-b4a74a01c721?w=500&auto=format&fit=crop&q=80', 'L', 'Charcoal Grey', 1099.00, 460.00, 250, 95, 'Active')
    ]

    products_dict = {}
    for pid, pname, pcat, pdesc, pimg, psize, pcol, psell, pcost, ptarg, pavail, pstat in products_data:
        p = Product(product_id=pid, name=pname, category=pcat, description=pdesc, image_url=pimg, size=psize, color=pcol, selling_price=psell, cost_price=pcost, target_quantity=ptarg, available_stock=pavail, status=pstat)
        products_dict[pid] = p

    db.session.add_all(list(products_dict.values()))
    db.session.flush()

    # ---------------------------------------------------------
    # 6. PRODUCT BOM (Bill of Materials Mappings)
    # ---------------------------------------------------------
    bom_recipes = [
        # PROD-0001 (Classic Cotton Tee)
        ('PROD-0001', 'MAT-0001', 1.4), # Cotton Fabric 1.4m
        ('PROD-0001', 'MAT-0003', 45.0), # Thread 45m
        ('PROD-0001', 'MAT-0009', 0.15), # Rib Fabric 0.15m
        ('PROD-0001', 'MAT-0015', 1.0), # Care Label
        ('PROD-0001', 'MAT-0016', 1.0), # Neck Label
        ('PROD-0001', 'MAT-0013', 1.0), # Poly bag
        # PROD-0002 (Denim Jeans)
        ('PROD-0002', 'MAT-0007', 1.8), # Denim 1.8m
        ('PROD-0002', 'MAT-0003', 85.0), # Thread 85m
        ('PROD-0002', 'MAT-0026', 1.0), # Metal Button
        ('PROD-0002', 'MAT-0012', 1.0), # Zipper
        ('PROD-0002', 'MAT-0016', 1.0), # Label
        ('PROD-0002', 'MAT-0013', 1.0), # Poly bag
        # PROD-0003 (Denim Jacket)
        ('PROD-0003', 'MAT-0007', 2.6), # Denim 2.6m
        ('PROD-0003', 'MAT-0003', 120.0), # Thread
        ('PROD-0003', 'MAT-0026', 6.0), # Buttons
        ('PROD-0003', 'MAT-0016', 1.0), # Label
        ('PROD-0003', 'MAT-0017', 1.0), # Hang tag
        # PROD-0004 (Fleece Hoodie)
        ('PROD-0004', 'MAT-0010', 2.2), # Terry/Fleece 2.2m
        ('PROD-0004', 'MAT-0003', 75.0), # Thread
        ('PROD-0004', 'MAT-0020', 1.2), # Drawstring 1.2m
        ('PROD-0004', 'MAT-0009', 0.3), # Rib
        ('PROD-0004', 'MAT-0016', 1.0), # Label
        # PROD-0005 (Polo Shirt)
        ('PROD-0005', 'MAT-0008', 1.5), # Jersey 1.5m
        ('PROD-0005', 'MAT-0009', 0.2), # Rib collar
        ('PROD-0005', 'MAT-0004', 3.0), # Resin buttons
        ('PROD-0005', 'MAT-0003', 50.0), # Thread
        ('PROD-0005', 'MAT-0016', 1.0), # Label
        # PROD-0006 (Oxford Shirt)
        ('PROD-0006', 'MAT-0001', 1.9), # Cotton Fabric
        ('PROD-0006', 'MAT-0018', 0.4), # Fusible Interlining
        ('PROD-0006', 'MAT-0004', 7.0), # Buttons
        ('PROD-0006', 'MAT-0003', 60.0), # Thread
        # PROD-0011 (Track Pants)
        ('PROD-0011', 'MAT-0010', 1.6), # Terry fabric
        ('PROD-0011', 'MAT-0021', 0.9), # Elastic tape
        ('PROD-0011', 'MAT-0020', 1.1), # Drawstring
        ('PROD-0011', 'MAT-0003', 45.0)  # Thread
    ]

    bom_list = []
    for pid, mid, qreq in bom_recipes:
        b = ProductBOM(product_id=pid, material_id=mid, quantity_required=qreq)
        bom_list.append(b)

    db.session.add_all(bom_list)
    db.session.flush()

    # ---------------------------------------------------------
    # 7. PRODUCTION ORDERS (45 Orders Spanning 5 Months)
    # ---------------------------------------------------------
    supervisors = ['Ramesh Pal', 'Suresh Kumar', 'Anita Roy', 'DeepakQA', 'Kavita Sharma', 'Vikram Sethi']
    priorities = ['High', 'Medium', 'Low', 'Urgent']

    production_orders = []
    batches_list = []
    quality_list = []
    shipments_list = []
    txns_list = []
    logs_list = []
    notifs_list = []

    # Generate historical production data across 5 months (150 days)
    for i in range(1, 46):
        oid = f"ORD-{i:04d}"
        pid = f"PROD-{(i % 30) + 1:04d}" # Cycle products
        cid = f"CUS-{(i % 25) + 1:04d}" # Cycle customers
        sup = supervisors[i % len(supervisors)]
        prio = priorities[i % len(priorities)]
        qty = 100 + (i * 15) % 400

        # Spread dates backwards from current date
        days_ago = 150 - (i * 3) # 147 days ago to 15 days ago
        start_dt = base_date - timedelta(days=days_ago)
        end_dt = start_dt + timedelta(days=7 + (i % 5))

        # Status distribution: Completed (early ones), In Progress (middle), Planned (recent)
        if i <= 28:
            status = 'COMPLETED'
            avail_pct = 100.0
            r_score = 100.0
            r_stat = 'READY'
        elif i <= 38:
            status = 'IN_PROGRESS'
            avail_pct = 100.0
            r_score = 100.0
            r_stat = 'READY'
        else:
            status = 'PLANNED'
            avail_pct = 75.0 if i % 2 == 0 else 100.0
            r_score = 75.0 if i % 2 == 0 else 100.0
            r_stat = 'PARTIALLY_READY' if i % 2 == 0 else 'READY'

        order = ProductionOrder(
            order_id=oid,
            product_id=pid,
            quantity=qty,
            customer_id=cid,
            priority=prio,
            start_date=start_dt,
            expected_completion=end_dt,
            assigned_supervisor=sup,
            status=status,
            material_availability_pct=avail_pct,
            readiness_score=r_score,
            readiness_status=r_stat,
            notes=f"Order {oid} for customer {cid} targeting {qty} units of {pid}."
        )
        production_orders.append(order)

        # Activity Log for Order Creation
        logs_list.append(ActivityLog(
            user_id='admin' if i % 2 == 0 else 'manager',
            action='Create Order',
            module='Production',
            record_id=oid,
            description=f"Created Production Order {oid} for {qty} units of Product {pid} for customer {cid}.",
            timestamp=datetime.now(timezone.utc) - timedelta(days=days_ago)
        ))

        # ---------------------------------------------------------
        # 8. BATCHES (45 Batches at Different Stages)
        # ---------------------------------------------------------
        if status in ['IN_PROGRESS', 'COMPLETED']:
            bid = f"BAT-{i:04d}"
            bcode = f"BAT-{oid}"
            stages = ['Cutting', 'Dyeing', 'Stitching', 'Finishing', 'Packing', 'Completed']

            if status == 'COMPLETED':
                stage = 'Completed'
                bstatus = 'Completed'
                produced_qty = qty - (i % 8) # Minor defective units subtracted
            else:
                stage = stages[(i % 5)] # Cutting, Dyeing, Stitching, Finishing, Packing
                bstatus = 'In Progress'
                produced_qty = int(qty * ((i % 4 + 1) * 0.2)) # Partial production progress

            batch = Batch(
                batch_id=bid,
                batch_code=bcode,
                production_order_id=oid,
                product_id=pid,
                target_quantity=qty,
                produced_quantity=produced_qty,
                supervisor=sup,
                customer_id=cid,
                start_date=start_dt,
                expected_completion=end_dt,
                current_stage=stage,
                status=bstatus
            )
            batches_list.append(batch)

            # ---------------------------------------------------------
            # 9. QUALITY CONTROL INSPECTIONS (For Active & Completed Batches)
            # ---------------------------------------------------------
            qcid = f"QC-{i:04d}"
            total_eval = min(qty, produced_qty if produced_qty > 0 else qty)
            defects = (i * 3) % 12 if i % 7 != 0 else 18 # Occasional higher defects
            passed = max(0, total_eval - defects)
            pass_rate = round((passed / total_eval * 100.0), 1) if total_eval > 0 else 100.0
            qa_status = 'PASS' if pass_rate >= 90.0 else 'FAIL'

            qc = QualityInspection(
                inspection_id=qcid,
                batch_id=bid,
                product_id=pid,
                inspector=sup,
                inspection_date=datetime.now(timezone.utc) - timedelta(days=max(1, days_ago - 5)),
                total_evaluated=total_eval,
                defective_units=defects,
                passed_units=passed,
                pass_rate=pass_rate,
                defect_type='Minor Loose Stitching' if defects <= 5 else ('Fabric Dye Variance' if defects <= 10 else 'Button Attachment Defect'),
                remarks=f"QA Inspection {qcid} completed. Pass rate: {pass_rate}%. Status: {qa_status}.",
                qa_status=qa_status
            )
            quality_list.append(qc)

            if qa_status == 'FAIL':
                notifs_list.append(Notification(
                    title=f"Quality Alert: QC Fail on {bid}",
                    message=f"Batch {bid} failed QA inspection with {defects} defects ({pass_rate}% Pass Rate).",
                    type='danger',
                    link='/quality',
                    created_at=datetime.now(timezone.utc) - timedelta(days=max(1, days_ago - 5))
                ))

            # ---------------------------------------------------------
            # 10. SHIPMENTS (For Completed & Advanced Batches)
            # ---------------------------------------------------------
            if status == 'COMPLETED' or stage in ['Packing', 'Completed']:
                shpid = f"SHP-{i:04d}"
                carriers = ['Blue Dart Logistics', 'DHL Express Air', 'FedEx Commercial', 'Delhivery Surface', 'DTDC Express']
                carr = carriers[i % len(carriers)]
                trk = f"TRK-{i:04d}-{carr[:3].upper()}"

                ship_status = 'DELIVERED' if status == 'COMPLETED' else ('IN_TRANSIT' if i % 2 == 0 else 'READY')
                actual_del = end_dt + timedelta(days=2) if ship_status == 'DELIVERED' else None

                shipment = Shipment(
                    shipment_id=shpid,
                    batch_id=bid,
                    production_order_id=oid,
                    product_id=pid,
                    customer_id=cid,
                    quantity=passed,
                    carrier=carr,
                    tracking_number=trk,
                    shipment_date=end_dt,
                    expected_delivery=end_dt + timedelta(days=3),
                    actual_delivery=actual_del,
                    status=ship_status,
                    notes=f"Shipment {shpid} dispatched via {carr} to customer {cid}."
                )
                shipments_list.append(shipment)

                if ship_status == 'DELIVERED':
                    notifs_list.append(Notification(
                        title=f"Delivery Confirmed: {shpid}",
                        message=f"Shipment {shpid} ({passed} units) delivered to customer {cid}.",
                        type='success',
                        link='/shipments',
                        created_at=datetime.now(timezone.utc) - timedelta(days=max(1, days_ago - 8))
                    ))

        # ---------------------------------------------------------
        # 11. INVENTORY TRANSACTIONS (Stock Receipts & Production Consumption)
        # ---------------------------------------------------------
        txid1 = f"INV-TXN-IN-{i:04d}"
        mat1_id = f"MAT-{(i % 30) + 1:04d}"
        txns_list.append(InventoryTransaction(
            transaction_id=txid1,
            material_id=mat1_id,
            transaction_type='Stock In',
            quantity=500.0 + (i * 20),
            previous_quantity=100.0,
            new_quantity=600.0 + (i * 20),
            reference=f"PO-SUP-{(i % 25) + 1:04d}",
            user_id='admin',
            remarks=f"Received raw material shipment from Supplier SUP-{(i % 25) + 1:04d}.",
            created_at=datetime.now(timezone.utc) - timedelta(days=days_ago + 2)
        ))

        if status in ['IN_PROGRESS', 'COMPLETED']:
            txid2 = f"INV-TXN-OUT-{i:04d}"
            txns_list.append(InventoryTransaction(
                transaction_id=txid2,
                material_id=mat1_id,
                transaction_type='Production Consumption',
                quantity=150.0 + (i * 5),
                previous_quantity=600.0 + (i * 20),
                new_quantity=450.0 + (i * 15),
                reference=oid,
                user_id='manager',
                remarks=f"Consumed material for Production Order {oid}.",
                created_at=datetime.now(timezone.utc) - timedelta(days=days_ago)
            ))

    db.session.add_all(production_orders)
    db.session.add_all(batches_list)
    db.session.add_all(quality_list)
    db.session.add_all(shipments_list)
    db.session.add_all(txns_list)
    db.session.add_all(logs_list)
    db.session.add_all(notifs_list)

    # 12. Add Notifications for Low / Critical Stock Items
    for m in materials_dict.values():
        if m.quantity <= m.critical_level:
            db.session.add(Notification(
                title=f"CRITICAL Stock Alert: {m.name}",
                message=f"Material {m.name} ({m.material_id}) is down to {m.quantity} {m.unit} (Critical Threshold: {m.critical_level}). Immediate PO required!",
                type='danger',
                link='/inventory'
            ))
        elif m.quantity <= m.minimum_level:
            db.session.add(Notification(
                title=f"LOW Stock Alert: {m.name}",
                message=f"Material {m.name} ({m.material_id}) is at {m.quantity} {m.unit} (Min Threshold: {m.minimum_level}). Reorder recommended.",
                type='warning',
                link='/inventory'
            ))

    db.session.commit()
    print("Vibe Clothing ERP Expanded Seed Dataset Generated & Committed Successfully!")
