from flask import Blueprint, request, jsonify
from config import reports_collection
from models.report_model import create_report
from services.ocr_service import extract_text
from services.storage_service import save_file
from services.ai_service import generate_summary
import os

report_bp = Blueprint("report", __name__)

UPLOAD_FOLDER = "uploads/reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------------------------
# Upload Report API
# -------------------------
@report_bp.route("/upload-report", methods=["POST"])
def upload_report():

    # Validate file
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    data = request.form

    # Validate mandatory fields
    required_fields = [
        "document_id",
        "report_name",
        "report_type",
        "prepared_by",
        "report_date"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    # Prevent duplicate document_id
    if reports_collection.find_one({"document_id": data["document_id"]}):
        return jsonify({"error": "Document ID already exists"}), 409

    # Save file securely
    try:
        file_path = save_file(file, UPLOAD_FOLDER)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # OCR extraction (safe)
    try:
        ocr_text = extract_text(file_path)
    except Exception:
        ocr_text = ""
    # AI summary generation (safe)
    try:
        ai_summary = generate_summary(ocr_text) if ocr_text else ""
    except Exception:
        ai_summary = ""

    # Create DB document using model
    report = create_report({
        **data,
        "file_path": file_path,
        "ocr_text": ocr_text,
        "ai_summary": ai_summary
    })

    reports_collection.insert_one(report)

    return jsonify({"message": "Report uploaded successfully"}), 201


# -------------------------
# Search Report API
# -------------------------
@report_bp.route("/search", methods=["GET"])
def search_reports():
    keyword = request.args.get("q")

    if not keyword:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    regex_query = {"$regex": keyword, "$options": "i"}

    results = reports_collection.find(
        {
            "$or": [
                {"report_name": regex_query},
                {"ocr_text": regex_query}
            ]
        },
        {"_id": 0, "report_name": 1}
    )

    return jsonify([r["report_name"] for r in results]), 200
