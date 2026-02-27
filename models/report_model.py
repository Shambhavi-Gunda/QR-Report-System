def create_report(data):
    return {
        "document_id": data["document_id"],
        "report_name": data["report_name"],
        "report_type": data["report_type"],
        "division": "QR",
        "prepared_by": data["prepared_by"],
        "report_date": data["report_date"],
        "summary": "",
        "file_path": data["file_path"],
        "ocr_text": data.get("ocr_text", ""),
        "uploaded_by": data.get("uploaded_by", "system"),
        "access_role": data.get("access_role", "viewer")
    }
