from flask import Blueprint, request, jsonify
from config import reports_collection, db
search_collection = db["search_logs"]
from models.report_model import create_report
from services.ocr_service import extract_text
from services.storage_service import save_file
from services.ai_service import generate_summary
from flask import send_from_directory
from utils.auth import admin_required

import os
from datetime import datetime


# Blueprint
report_bp = Blueprint("report", __name__, url_prefix="/api")

UPLOAD_FOLDER = "uploads/reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dropdown collection
dropdowns_collection = db["dropdowns"]


# --------------------------------------------------
# Dropdown helper
# --------------------------------------------------
def update_dropdown(field, value):
    if not value:
        return

    existing = dropdowns_collection.find_one({"field": field})

    if existing:
        if value not in existing["values"]:
            dropdowns_collection.update_one(
                {"field": field},
                {"$push": {"values": value}}
            )
    else:
        dropdowns_collection.insert_one({
            "field": field,
            "values": [value]
        })

# file path

@report_bp.route("/uploads/<path:filepath>")
def serve_file(filepath):
    full_path = os.path.join("uploads", filepath)

    if not os.path.exists(full_path):
        print("FILE NOT FOUND:", full_path)
        return "File not found", 404

    return send_from_directory("uploads", filepath)

# --------------------------------------------------
# GET DROPDOWNS
# --------------------------------------------------
@report_bp.route("/dropdowns", methods=["GET"])
def get_dropdowns():

    data = list(dropdowns_collection.find({}, {"_id": 0}))

    result = {}
    for item in data:
        result[item["field"]] = item["values"]

    return jsonify(result)


# --------------------------------------------------
# ADD DROPDOWN VALUE (ADMIN)
# --------------------------------------------------
@report_bp.route("/add-dropdown/<field>", methods=["POST"])
@admin_required
def add_dropdown(field):

    value = request.json.get("value")

    if not value:
        return jsonify({"error": "Value required"}), 400

    existing = dropdowns_collection.find_one({"field": field})

    if existing:
        if value not in existing["values"]:
            dropdowns_collection.update_one(
                {"field": field},
                {"$push": {"values": value}}
            )
    else:
        dropdowns_collection.insert_one({
            "field": field,
            "values": [value]
        })

    return jsonify({"message": "Added"})


# --------------------------------------------------
# Upload Report (UPDATED FOR MULTIPLE FILES)
# --------------------------------------------------
@report_bp.route("/upload-report", methods=["POST"])
def upload_report():

    files = request.files.getlist("files")

    #  FIX: safer validation
    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "Files are required"}), 400

    data = request.form

    required_fields = [
        "document_id",
        "report_name",
        "report_type",
        "prepared_by",
        "report_date",
        "division"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if reports_collection.find_one({"document_id": data["document_id"]}):
        return jsonify({"error": "Document ID already exists"}), 409

    # SAVE MULTIPLE FILES
    file_paths = []

    for file in files:
        if file and file.filename != "":
            path = save_file(file, UPLOAD_FOLDER)
            file_paths.append(path)

    print("DEBUG FILE PATHS:", file_paths)  # debug

    # OCR + AI
    extracted_text = ""
    ai_summary = ""

    try:
        for path in file_paths:
            extracted_text += extract_text(path) + "\n"

        if extracted_text.strip():
            ai_summary = generate_summary(extracted_text[:3000])

    except Exception as e:
        print("OCR error:", e)

    
    report = create_report({
        "document_id": data.get("document_id"),
        "report_name": data.get("report_name"),
        "report_type": data.get("report_type"),
        "division": data.get("division"),
        "equipment": data.get("equipment"),
        "prepared_by": data.get("prepared_by"),
        "report_date": data.get("report_date"),
        "summary": data.get("summary"),
        "files": file_paths,   # changed from file_paths → files
        "ocr_text": extracted_text,
        "ai_summary": ai_summary,
        "uploaded_at": datetime.utcnow()
    })

    reports_collection.insert_one(report)

    return jsonify({"message": "Report uploaded successfully"}), 201

# --------------------------------------------------
# Get All Reports (UPDATED)
# --------------------------------------------------
@report_bp.route("/all-reports", methods=["GET"])
def get_all_reports():

    reports = reports_collection.find(
        {},
        {
            "_id": 0,
            "document_id": 1,
            "report_name": 1,
            "report_type": 1,
            "division": 1,
            "equipment": 1,
            "report_date": 1,
            "files": 1,   # updated
            "ai_summary": 1
        }
    )

    return jsonify(list(reports))


# --------------------------------------------------
# Stats
# --------------------------------------------------
@report_bp.route("/stats", methods=["GET"])
def get_stats():

    total_reports = reports_collection.count_documents({})

    return jsonify({
        "total_reports": total_reports
    })


# --------------------------------------------------
# Delete Report
# --------------------------------------------------
@report_bp.route("/delete-report/<id>", methods=["DELETE"])
@admin_required
def delete_report(id):

    reports_collection.delete_one({"document_id": id})

    return jsonify({"message": "Deleted"})


# --------------------------------------------------
# Update Report
# --------------------------------------------------
@report_bp.route("/update-report/<document_id>", methods=["PUT"])
def update_report(document_id):

    data = request.json

    report = reports_collection.find_one({"document_id": document_id})

    if not report:
        return jsonify({"error": "Report not found"}), 404

    update_fields = {
        "report_name": data.get("report_name"),
        "report_type": data.get("report_type"),
        "division": data.get("division"),
        "equipment": data.get("equipment"),
        "prepared_by": data.get("prepared_by"),
        "report_date": data.get("report_date"),
        "summary": data.get("summary")
    }

    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    reports_collection.update_one(
        {"document_id": document_id},
        {"$set": update_fields}
    )

    return jsonify({"message": "Updated successfully"})
# --------------------------------------------------
# Upload Trend (GRAPH)
# --------------------------------------------------
@report_bp.route("/upload-trend", methods=["GET"])
def upload_trend():

    reports = list(reports_collection.find({}, {"uploaded_at": 1, "_id": 0}))

    trend = {}

    for r in reports:
        if "uploaded_at" in r:
            date = r["uploaded_at"].strftime("%Y-%m-%d")
            trend[date] = trend.get(date, 0) + 1

    labels = sorted(trend.keys())
    values = [trend[d] for d in labels]

    return jsonify({
        "labels": labels,
        "values": values
    })


# --------------------------------------------------
# Recent Uploads
# --------------------------------------------------
@report_bp.route("/recent-uploads", methods=["GET"])
def recent_uploads():

    reports = list(reports_collection.find(
        {},
        {
            "_id": 0,
            "document_id": 1,
            "report_name": 1,
            "report_type": 1,
            "division": 1,
            "report_date": 1,
            "prepared_by": 1,
            "uploaded_at": 1
        }
    ).sort("uploaded_at", -1).limit(5))

    return jsonify(reports)

# --------------------------------------------------
# Recent Searches
# --------------------------------------------------
@report_bp.route("/recent-searches", methods=["GET"])
def recent_searches():

    searches = list(search_collection.find(
        {},
        {
            "_id": 0,
            "document_id": 1,
            "report_name": 1,
            "report_type": 1,
            "division": 1,
            "date": 1,
            "user": 1
        }
    ).sort([("_id", -1)]).limit(5))   # ✅ FIXED SORT

    return jsonify(searches)


# --------------------------------------------------
# OPTIONAL: Log Search (VERY IMPORTANT)
# --------------------------------------------------
@report_bp.route("/log-search", methods=["POST"])
def log_search():

    data = request.json

    # 🔥 If document_id exists → fetch full report
    report = None
    if data.get("document_id"):
        report = reports_collection.find_one(
            {"document_id": data.get("document_id")},
            {"_id": 0}
        )

    search_collection.insert_one({
        "document_id": report.get("document_id") if report else None,
        "report_name": report.get("report_name") if report else data.get("report_name"),
        "report_type": report.get("report_type") if report else None,
        "division": report.get("division") if report else None,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),  # ✅ FIXED FORMAT
        "user": data.get("user", "Admin")
    })

    return jsonify({"message": "Logged"})