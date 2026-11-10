"""
Backend REST API - Facility Issue Reporting System
Telkom University - Cloud Computing UTS
Studi Kasus 8: Laporan Kerusakan Fasilitas Kampus
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import json
import os
import threading

DATA_DIR = "/var/lib/backend_data"
DATA_FILE = os.path.join(DATA_DIR, "facility_reports.json")
lock = threading.Lock()


def load_data():
    """Load facility reports from JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_data(data):
    """Save facility reports to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    # Tulis ke file sementara lalu rename, supaya file data tidak pernah
    # setengah tertulis kalau kontainer dimatikan paksa di tengah proses.
    tmp_file = DATA_FILE + ".tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_file, DATA_FILE)


class FacilityReportHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Facility Issue Reports."""

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, data, status=200):
        self._set_headers(status)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _route(self):
        """Return the request path without query string and trailing slash."""
        return urlparse(self.path).path.rstrip("/") or "/"

    def _method_not_allowed(self):
        self._send_json({"status": "error", "message": "Method not allowed"}, 405)

    do_PUT = _method_not_allowed
    do_PATCH = _method_not_allowed

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self._set_headers(204)

    def do_GET(self):
        """GET /reports - Retrieve all facility issue reports."""
        route = self._route()
        if route == "/reports":
            with lock:
                reports = load_data()
            self._send_json({
                "status": "success",
                "count": len(reports),
                "data": reports
            })
        elif route == "/health":
            self._send_json({"status": "healthy", "service": "facility-report-api"})
        else:
            self._send_json({"status": "error", "message": "Endpoint not found"}, 404)

    def do_POST(self):
        """POST /reports - Submit a new facility issue report."""
        if self._route() == "/reports":
            try:
                try:
                    content_length = int(self.headers.get("Content-Length", 0))
                except ValueError:
                    content_length = 0
                if content_length <= 0:
                    self._send_json({"status": "error", "message": "Request body is empty"}, 400)
                    return

                body = self.rfile.read(content_length)
                new_report = json.loads(body.decode("utf-8"))

                if not isinstance(new_report, dict):
                    self._send_json({"status": "error", "message": "Request body must be a JSON object"}, 400)
                    return

                # Validate required fields
                required_fields = ["location", "category", "description", "reporter"]
                missing = [f for f in required_fields if f not in new_report or not str(new_report[f]).strip()]
                if missing:
                    self._send_json({
                        "status": "error",
                        "message": f"Missing required fields: {', '.join(missing)}"
                    }, 400)
                    return

                not_text = [f for f in required_fields if not isinstance(new_report[f], str)]
                if not_text:
                    self._send_json({
                        "status": "error",
                        "message": f"Fields must be text: {', '.join(not_text)}"
                    }, 400)
                    return

                # Build report entry
                report_entry = {
                    "location": new_report["location"].strip(),
                    "category": new_report["category"].strip(),
                    "description": new_report["description"].strip(),
                    "reporter": new_report["reporter"].strip(),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Pending"
                }

                with lock:
                    reports = load_data()
                    reports.append(report_entry)
                    save_data(reports)

                self._send_json({
                    "status": "success",
                    "message": "Report submitted successfully",
                    "data": report_entry
                }, 201)

            except (json.JSONDecodeError, UnicodeDecodeError):
                self._send_json({"status": "error", "message": "Invalid JSON format"}, 400)
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        else:
            self._send_json({"status": "error", "message": "Endpoint not found"}, 404)

    def do_DELETE(self):
        """DELETE /reports?index=X - Delete a specific facility issue report by index."""
        if self._route() == "/reports":
            try:
                # Parse index from query string
                params = parse_qs(urlparse(self.path).query)

                if "index" not in params:
                    self._send_json({"status": "error", "message": "Missing 'index' query parameter"}, 400)
                    return

                index = int(params["index"][0])

                with lock:
                    reports = load_data()
                    if index < 0 or index >= len(reports):
                        self._send_json({
                            "status": "error",
                            "message": f"Index {index} out of range. Total reports: {len(reports)}"
                        }, 404)
                        return

                    deleted = reports.pop(index)
                    save_data(reports)

                self._send_json({
                    "status": "success",
                    "message": "Report deleted successfully",
                    "data": deleted
                })

            except ValueError:
                self._send_json({"status": "error", "message": "Invalid index value, must be integer"}, 400)
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, 500)
        else:
            self._send_json({"status": "error", "message": "Endpoint not found"}, 404)

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[API] {self.client_address[0]} - {format % args}")


def run_server(host="0.0.0.0", port=5000):
    """Start the HTTP server."""
    server = HTTPServer((host, port), FacilityReportHandler)
    print(f"🚀 Facility Report API Server running on http://{host}:{port}")
    print(f"📂 Data stored in: {DATA_FILE}")
    print(f"📋 Endpoints:")
    print(f"   GET    /reports           - List all reports")
    print(f"   POST   /reports           - Submit new report")
    print(f"   DELETE /reports?index=X   - Delete report by index")
    print(f"   GET    /health            - Health check")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        server.server_close()


if __name__ == "__main__":
    run_server()
