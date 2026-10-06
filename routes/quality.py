from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.quality import QualityInspection
from models.batch import Batch
from models.product import Product
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity, create_notification

quality_bp = Blueprint('quality', __name__)

@quality_bp.route('/quality')
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()

    query = QualityInspection.query

    if search:
        query = query.filter(
            (QualityInspection.inspection_id.ilike(f"%{search}%")) |
            (QualityInspection.batch_id.ilike(f"%{search}%")) |
            (QualityInspection.product_id.ilike(f"%{search}%")) |
            (QualityInspection.inspector.ilike(f"%{search}%"))
        )

    if status_filter:
        query = query.filter(QualityInspection.qa_status == status_filter.upper())

    inspections = query.order_by(QualityInspection.inspection_date.desc()).all()

    batches = Batch.query.filter(Batch.status != 'Cancelled').all()
    products = Product.query.filter_by(status='Active').all()

    # Calculate overall metrics
    total_inspections = len(inspections)
    total_eval = sum(q.total_evaluated for q in inspections)
    total_defects = sum(q.defective_units for q in inspections)
    total_passed = sum(q.passed_units for q in inspections)
    overall_pass_rate = round((total_passed / total_eval * 100.0), 1) if total_eval > 0 else 100.0

    return render_template(
        'quality/index.html',
        inspections=[q.to_dict() for q in inspections],
        batches=batches,
        products=products,
        total_inspections=total_inspections,
        total_eval=total_eval,
        total_defects=total_defects,
        overall_pass_rate=overall_pass_rate,
        search=search,
        selected_status=status_filter
    )

@quality_bp.route('/quality/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager', 'staff'])
def add_inspection():
    try:
        batch_id = request.form.get('batch_id', '').strip()
        product_id = request.form.get('product_id', '').strip()
        inspector = request.form.get('inspector', '').strip() or session.get('username', 'QA Lead')
        total_evaluated = int(request.form.get('total_evaluated', 100))
        defective_units = int(request.form.get('defective_units', 0))
        defect_type = request.form.get('defect_type', '').strip()
        remarks = request.form.get('remarks', '').strip()

        if not batch_id:
            flash('Batch ID is required for Quality Inspection.', 'danger')
            return redirect(url_for('quality.index'))

        if total_evaluated <= 0:
            flash('Total evaluated garments must be greater than zero.', 'danger')
            return redirect(url_for('quality.index'))

        if defective_units < 0 or defective_units > total_evaluated:
            flash('Defective units cannot be negative or exceed total evaluated garments.', 'danger')
            return redirect(url_for('quality.index'))

        batch = Batch.query.filter_by(batch_id=batch_id).first()
        if not batch:
            flash('Selected Batch not found.', 'danger')
            return redirect(url_for('quality.index'))

        target_product_id = product_id or batch.product_id

        inspection_id = generate_next_id('quality_inspection')

        inspection = QualityInspection(
            inspection_id=inspection_id,
            batch_id=batch_id,
            product_id=target_product_id,
            inspector=inspector,
            inspection_date=datetime.now(timezone.utc),
            total_evaluated=total_evaluated,
            defective_units=defective_units,
            defect_type=defect_type or 'None',
            remarks=remarks
        )

        inspection.calculate_metrics(pass_threshold=90.0)

        # Update batch produced quantity to reflect usable QC passed units
        batch.produced_quantity = inspection.passed_units

        db.session.add(inspection)
        db.session.commit()

        if inspection.qa_status == 'FAIL':
            create_notification(
                title=f"Quality Alert: QC Fail on {batch_id}",
                message=f"QC Inspection {inspection_id} failed with {defective_units} defects ({inspection.pass_rate}% Pass Rate). Defect: {defect_type}.",
                ntype='danger',
                link='/quality'
            )

        user_id = session.get('username', 'System')
        log_activity('QC Inspection Recorded', 'Quality', f"Recorded QC Inspection {inspection_id} for batch {batch_id}. Status: {inspection.qa_status} ({inspection.pass_rate}% pass rate). Usable passed output: {inspection.passed_units} units.", record_id=inspection_id, user_id=user_id)
        flash(f"QC Inspection {inspection_id} recorded! Status: {inspection.qa_status} ({inspection.pass_rate}% Pass Rate). Usable batch output set to {inspection.passed_units} units.", 'success' if inspection.qa_status == 'PASS' else 'warning')

    except Exception as e:
        db.session.rollback()
        flash(f"Error recording quality inspection: {str(e)}", 'danger')

    return redirect(url_for('quality.index'))
