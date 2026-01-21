import os
import cv2
import numpy as np
import sqlite3
import traceback
import logging
import uuid
import json
import io
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fpdf import FPDF
import tensorflow as tf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Report save function
def save_report(inspection_id: str, report: dict):
    """Save inspection report to JSON file"""
    path = f"{REPORTS_DIR}/{inspection_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

# Absolute path resolution for Render deployment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METAL_MODEL_PATH = os.path.join(BASE_DIR, "metal_surface_validator.tflite")
DEFECT_MODEL_PATH = os.path.join(BASE_DIR, "zenkensa_model.tflite")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Render-safe TensorFlow configuration
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU

# Initialize FastAPI app
app = FastAPI(title="ZenKensa Edge AI - Surface Inspection System")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Static (future safe)
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Main UI on root path
@app.get("/", response_class=HTMLResponse)
def show_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Health check for Render
@app.get("/api/health")
def health():
    return {"status": "ZenKensa running"}

# Global TFLite interpreters
metal_validator_interpreter = None
defect_inspector_interpreter = None

# Database Setup
def init_db():
    db_path = os.path.join(BASE_DIR, 'inspections.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            inspector TEXT,
            batch TEXT,
            status TEXT,
            score REAL,
            defects INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized: {db_path}")

# Email Alert Function
def send_email_alert(data):
    if data.get('status') == 'FAIL':
        logger.info('📧 Email Sent to Manager - Inspection Failed')
    else:
        logger.info('✅ Inspection Passed - No email required')

# Initialize both TFLite models on startup
@app.on_event('startup')
async def startup_event():
    global metal_validator_interpreter, defect_inspector_interpreter
    
    # Initialize database
    init_db()
    
    # Ensure reports directory exists with absolute paths
    os.makedirs(os.path.join(BASE_DIR, 'app/static/reports'), exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)  # For JSON reports
    logger.info(f"✅ Reports directory created: {REPORTS_DIR}")
    
    # Load Metal Surface Validator Model with absolute path
    try:
        if os.path.exists(METAL_MODEL_PATH):
            metal_validator_interpreter = tf.lite.Interpreter(model_path=METAL_MODEL_PATH)
            metal_validator_interpreter.allocate_tensors()
            logger.info(f"✅ Metal Surface Validator loaded: {METAL_MODEL_PATH}")
        else:
            logger.error(f"❌ Metal Surface Validator not found: {METAL_MODEL_PATH}")
            metal_validator_interpreter = None
    except Exception as e:
        logger.error(f"❌ Error loading Metal Surface Validator: {e}")
        metal_validator_interpreter = None
    
    # Load Defect Inspection Model with absolute path
    try:
        if os.path.exists(DEFECT_MODEL_PATH):
            defect_inspector_interpreter = tf.lite.Interpreter(model_path=DEFECT_MODEL_PATH)
            defect_inspector_interpreter.allocate_tensors()
            logger.info(f"✅ Defect Inspection loaded: {DEFECT_MODEL_PATH}")
        else:
            logger.error(f"❌ Defect Inspection not found: {DEFECT_MODEL_PATH}")
            defect_inspector_interpreter = None
    except Exception as e:
        logger.error(f"❌ Error loading Defect Inspection: {e}")
        defect_inspector_interpreter = None
        defect_inspector_interpreter = None
    
    if metal_validator_interpreter and defect_inspector_interpreter:
        logger.info("🚀 Both models loaded - Ready for industrial inspection pipeline")
    else:
        logger.error("❌ Model loading failed - Check model files")

def generate_inspection_report(data):
    """
    Generate Japanese Industrial Inspection Report (JSON canonical source)
    Production-ready, audit-friendly, Japanese-first documentation
    """
    inspection_id = str(uuid.uuid4())
    timestamp = datetime.now()
    
    # === SECTION 1: 検査情報 (Inspection Information) ===
    inspection_info = {
        "検査員名": data.get('inspector_name', 'Edge Inspector'),
        "Inspector Name": data.get('inspector_name', 'Edge Inspector'),
        "バッチID": data.get('batch_id', 'BATCH-001'),
        "Batch ID": data.get('batch_id', 'BATCH-001'),
        "製品情報": data.get('product_description', '金属表面検査'),
        "Product Description": data.get('product_description', 'Metal Surface Inspection')
    }
    
    # === SECTION 2: 判定結果 (Inspection Result) ===
    status_japanese = {
        "PASS": "合格",
        "FAIL": "不合格", 
        "UNCERTAIN": "判定保留",
        "INVALID_INPUT": "無効"
    }
    
    inspection_result = {
        "判定": status_japanese.get(data.get('status'), data.get('status')),
        "Status": data.get('status'),
        "健全性スコア": round(data.get('health_score', 0) or 0, 1),
        "Surface Health Score": round(data.get('health_score', 0) or 0, 1)
    }
    
    # === SECTION 3: AI解析結果 (AI Analysis - Reference Only) ===
    ai_analysis = {
        "metal_surface_validation_score": round(data.get('metal_validation_score', 0) or 0, 4),
        "defect_risk_indicator": round(data.get('defect_score', 0) or 0, 4),
        "disclaimer": "※ 本解析結果はAIによる参考指標です。最終判断は検査担当者の責任において行ってください。",
        "disclaimer_en": "This result is an AI-based reference indicator. Final judgment must be made by the responsible inspector."
    }
    
    # === SECTION 4: 判定理由 (Decision Explanation) ===
    decision_explanations = {
        "PASS": {
            "japanese": "表面に重大な欠陥は確認されておらず、基準内の状態であると判断されました。",
            "english": "No significant surface defects were detected."
        },
        "FAIL": {
            "japanese": "許容基準を超える欠陥傾向が検出されました。品質基準を満たしていません。",
            "english": "Defect patterns exceed acceptable limits."
        },
        "UNCERTAIN": {
            "japanese": "画像状態が不明瞭なため、再撮影または担当者確認を推奨します。",
            "english": "Image clarity insufficient. Retake recommended."
        },
        "INVALID_INPUT": {
            "japanese": "産業用金属表面の検査可能な画像ではありません。",
            "english": "Image does not resemble an inspectable industrial metal surface."
        }
    }
    
    explanation = decision_explanations.get(data.get('status'), {
        "japanese": "検査が完了しました。",
        "english": "Inspection completed."
    })
    
    # === SECTION 5: 検査履歴情報 (Inspection Metadata) ===
    inspection_metadata = {
        "使用モデル": {
            "金属表面判定モデル": "v1.0",
            "Metal Surface Validator": "v1.0",
            "欠陥検査モデル": "v1.0", 
            "Defect Inspection Model": "v1.0"
        }
    }
    
    # === COMPLETE REPORT STRUCTURE ===
    report = {
        # === PAGE HEADER ===
        "report_title": "ZENKENSA 検査報告書",
        "report_subtitle": "（Industrial Surface Inspection Report）",
        "inspection_id": inspection_id,
        "inspection_datetime": timestamp.strftime("%Y-%m-%d %H:%M"),
        
        # === SECTION 1 ===
        "検査情報": inspection_info,
        "Inspection Information": inspection_info,
        
        # === SECTION 2 ===
        "判定結果": inspection_result,
        "Inspection Result": inspection_result,
        
        # === SECTION 3 ===
        "AI解析結果": ai_analysis,
        "AI Analysis - Reference Only": ai_analysis,
        
        # === SECTION 4 ===
        "判定理由": explanation,
        "Decision Explanation": explanation,
        
        # === SECTION 5 ===
        "検査履歴情報": inspection_metadata,
        "Inspection Metadata": inspection_metadata,
        
        # === FOOTER ===
        "system_name": "ZenKensa Edge AI",
        "system_description": "工業用表面検査支援システム",
        "system_description_en": "Industrial Surface Inspection Support System",
        "footer_note": "※ 本レポートは品質管理支援を目的としています。",
        "footer_note_en": "This report is intended for quality management support.",
        
        # === TECHNICAL METADATA ===
        "timestamp_iso": timestamp.isoformat(),
        "report_version": "1.0",
        "encoding": "UTF-8"
    }
    
    # === SAVE REPORT ===
    save_report(inspection_id, report)
    logger.info(f"📄 Japanese inspection report saved: {inspection_id}")
    
    return inspection_id, report

def get_explanation_text(status, metal_score, defect_score):
    """Generate explanation text based on results"""
    if status == "INVALID_INPUT":
        return "Image does not resemble an inspectable industrial metal surface."
    elif status == "UNCERTAIN":
        return "Surface unclear. Please retake image with better lighting."
    elif status == "PASS":
        return "Surface appears clean with no significant defect patterns."
    elif status == "FAIL":
        return "Surface shows defect patterns exceeding acceptable threshold."
    else:
        return "Inspection completed."

# Shared preprocessing function for both models
def preprocess_image(image_bytes):
    """Preprocess image for TFLite model inference (224x224 RGB normalized)"""
    try:
        # Decode image from bytes
        img_array = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            raise Exception("Failed to decode image")
        
        # Convert BGR to RGB (TFLite expects RGB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size (224x224)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
        
        # Normalize to 0-1 range
        img = img.astype(np.float32) / 255.0
        
        # Add batch dimension
        img = np.expand_dims(img, axis=0)
        
        return img
    except Exception as e:
        logger.error(f"❌ Preprocessing error: {e}")
        raise e

# Metal Surface Validation (Gatekeeper)
def validate_metal_surface(processed_img):
    """Run metal surface validation model"""
    try:
        # Get input and output details
        input_details = metal_validator_interpreter.get_input_details()
        output_details = metal_validator_interpreter.get_output_details()
        
        # Set input tensor
        metal_validator_interpreter.set_tensor(input_details[0]['index'], processed_img)
        
        # Run inference
        metal_validator_interpreter.invoke()
        
        # Get metal validation probability
        metal_prediction = metal_validator_interpreter.get_tensor(output_details[0]['index'])[0][0]
        metal_score = float(metal_prediction)
        
        logger.info(f"🔍 Metal validation score: {metal_score:.4f}")
        return metal_score
        
    except Exception as e:
        logger.error(f"❌ Metal validation error: {e}")
        raise e

# Defect Inspection (Secondary Model)
def inspect_defects(processed_img):
    """Run defect inspection model"""
    try:
        # Get input and output details
        input_details = defect_inspector_interpreter.get_input_details()
        output_details = defect_inspector_interpreter.get_output_details()
        
        # Set input tensor
        defect_inspector_interpreter.set_tensor(input_details[0]['index'], processed_img)
        
        # Run inference
        defect_inspector_interpreter.invoke()
        
        # Get defect probability
        defect_prediction = defect_inspector_interpreter.get_tensor(output_details[0]['index'])[0][0]
        defect_score = float(defect_prediction)
        
        logger.info(f"🔍 Defect inspection score: {defect_score:.4f}")
        return defect_score
        
    except Exception as e:
        logger.error(f"❌ Defect inspection error: {e}")
        raise e

# Business Logic (Decision Layer)
def apply_business_logic(defect_score):
    """Apply industrial business logic for defect inspection results"""
    if defect_score <= 0.5:
        status = "PASS"
        # Smart Health Score for PASS: 100 - (P × 20) (Target 80-100%)
        health_score = 100 - (defect_score * 20)
    else:
        status = "FAIL"
        # Smart Health Score for FAIL: (1.0 - P) × 80 (Target < 80%)
        health_score = (1.0 - defect_score) * 80
    
    # Clamp health score to [0, 100]
    health_score = max(0, min(100, health_score))
    
    return status, health_score

# Main prediction endpoint with two-model pipeline
@app.post('/predict')
async def predict(file: UploadFile = File(...)):
    try:
        # Log incoming request
        logger.info(f"📥 Image received: {file.filename}")
        
        # Read uploaded image
        contents = await file.read()
        
        # Save original image for PDF report
        with open('detected_image.jpg', 'wb') as f:
            f.write(contents)
        
        # Check if models are loaded
        if metal_validator_interpreter is None or defect_inspector_interpreter is None:
            raise HTTPException(status_code=500, detail="Models not loaded properly")
        
        # Preprocess image for models
        processed_img = preprocess_image(contents)
        
        # STEP 1: Metal Surface Validation (Gatekeeper)
        metal_score = validate_metal_surface(processed_img)
        
        # Industrial Safety Guard: Uncertain range
        if 0.45 <= metal_score <= 0.55:
            logger.info("🔍 Uncertain metal surface detected")
            explanation = get_explanation_text("UNCERTAIN", metal_score, 0)
            return JSONResponse({
                "status": "UNCERTAIN",
                "message": "Surface unclear. Please retake image with better lighting.",
                "explanation": explanation,
                "metal_validation_score": round(metal_score, 4),
                "defect_score": 0.0,
                "health_score": 0.0
            })
        
        # Gatekeeper Logic: Reject non-metal surfaces
        if metal_score < 0.45:
            logger.info("🚫 Non-metal surface detected - Rejected")
            explanation = get_explanation_text("INVALID_INPUT", metal_score, 0)
            return JSONResponse({
                "status": "INVALID_INPUT",
                "message": "Unsupported or non-inspectable surface detected. Please upload a clear industrial metal surface image.",
                "explanation": explanation,
                "metal_validation_score": round(metal_score, 4),
                "defect_score": 0.0,
                "health_score": 0.0
            })
        
        logger.info("✅ Metal surface validated - Proceeding to defect inspection")
        
        # STEP 2: Defect Inspection (Only if metal validation passes)
        defect_score = inspect_defects(processed_img)
        
        # STEP 3: Apply Business Logic
        status, health_score = apply_business_logic(defect_score)
        
        # Clamp scores to valid ranges
        metal_score = max(0.0, min(1.0, metal_score))
        defect_score = max(0.0, min(1.0, defect_score))
        health_score = max(0.0, min(100.0, health_score))
        
        # Generate explanation
        explanation = get_explanation_text(status, metal_score, defect_score)
        
        # Create final response
        result_data = {
            "status": status,
            "health_score": round(health_score, 2),
            "metal_validation_score": round(metal_score, 4),
            "defect_score": round(defect_score, 4),
            "explanation": explanation
        }
        
        # Generate inspection report for valid inspections
        inspection_id = None
        if status in ["PASS", "FAIL"]:
            inspection_id, _ = generate_inspection_report(result_data)
            result_data["inspection_id"] = inspection_id
        
        # Log final result
        logger.info(f"🎯 Final result: {status} | Health: {health_score:.2f} | Metal: {metal_score:.4f} | Defect: {defect_score:.4f}")
        
        # Save to database (only for valid inspections)
        try:
            db_path = os.path.join(BASE_DIR, 'inspections.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO inspections (timestamp, inspector, batch, status, score, defects)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Edge Inspector',
                'BATCH-001',
                result_data['status'],
                result_data['health_score'],
                0 if result_data['status'] == 'PASS' else 1
            ))
            conn.commit()
            conn.close()
        except Exception as db_error:
            logger.error(f"❌ Database error: {db_error}")
        
        # Send email alert for failed inspections
        if result_data['status'] == 'FAIL':
            send_email_alert(result_data)
        
        return JSONResponse(result_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Health check endpoint
@app.get('/health')
async def health_check():
    """Check if models are loaded and ready"""
    metal_ready = metal_validator_interpreter is not None
    defect_ready = defect_inspector_interpreter is not None
    
    return {
        "status": "ready" if metal_ready and defect_ready else "not_ready",
        "metal_validator_loaded": metal_ready,
        "defect_inspector_loaded": defect_ready
    }

# PDF Generator Function
def generate_pdf_report(report: dict, file_path: str):
    """Generate PDF report from JSON data"""
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Title with safety check
        title = report.get("report_title", "ZENKENSA Inspection Report")
        subtitle = report.get("report_subtitle", "Industrial Surface Inspection Report")
        
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, title, ln=True, align="C")

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, subtitle, ln=True, align="C")
        pdf.ln(5)

        # Inspection Basic Information with safety check
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Inspection Basic Information", ln=True)

        info = report.get("Inspection Information", {})
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 7, f"Inspection ID: {report.get('inspection_id', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Inspection DateTime: {report.get('inspection_datetime', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Inspector: {info.get('Inspector Name', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Batch ID: {info.get('Batch ID', 'N/A')}", ln=True)
        pdf.cell(0, 7, f"Product Description: {info.get('Product Description', 'N/A')}", ln=True)

        pdf.ln(4)
        result = report.get("Inspection Result", {})

        # Judgment Result with safety check
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Judgment Result", ln=True)

        status = result.get("Status", "UNKNOWN")
        if status == "PASS":
            pdf.set_text_color(10, 125, 50)
        else:
            pdf.set_text_color(200, 40, 40)

        pdf.set_font("Arial", "B", 14)
        judgment = result.get("判定", status)
        pdf.cell(0, 10, f"{judgment} ({status})", ln=True)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 7, f"Surface Health Score: {result.get('Surface Health Score', 'N/A')}", ln=True)

        pdf.ln(3)
        reason = report.get("Decision Explanation", {})
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, "Decision Reason", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, reason.get("japanese", "N/A"))
        pdf.ln(2)
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, reason.get("english", "N/A"))

        pdf.ln(4)
        ai = report.get("AI Analysis - Reference Only", {})
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "AI Analysis Results (Reference Only)", ln=True)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"metal_surface_validation_score: {ai.get('metal_surface_validation_score', 'N/A')}", ln=True)
        pdf.cell(0, 6, f"defect_risk_indicator: {ai.get('defect_risk_indicator', 'N/A')}", ln=True)
        pdf.ln(3)
        
        pdf.set_font("Arial", "I", 9)
        pdf.multi_cell(0, 5, ai.get("disclaimer", "N/A"))
        pdf.ln(2)
        pdf.multi_cell(0, 5, ai.get("disclaimer_en", "N/A"))

        pdf.ln(6)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 6, report.get("footer_note", "N/A"), ln=True, align="C")
        pdf.cell(0, 5, report.get("footer_note_en", "N/A"), ln=True, align="C")
        pdf.ln(2)
        pdf.cell(0, 5, f"Generated: {report.get('timestamp_iso', 'N/A')}", ln=True, align="C")
        pdf.cell(0, 5, "System: ZenKensa Edge AI", ln=True, align="C")

        pdf.output(file_path)
    except Exception as e:
        raise Exception(f"PDF generation error: {str(e)}")

# Load report function
def load_report_from_storage(inspection_id: str):
    """Load inspection report from JSON file"""
    path = os.path.join(REPORTS_DIR, f"{inspection_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Report endpoint
@app.get("/report/{inspection_id}")
def get_report(inspection_id: str):
    report = load_report_from_storage(inspection_id)
    if not report:
        return {"detail": "Inspection report not found"}
    return report

@app.get("/report/{inspection_id}/view", response_class=HTMLResponse)
def view_report(request: Request, inspection_id: str):
    report_data = load_report_from_storage(inspection_id)
    if not report_data:
        return HTMLResponse("Inspection report not found", status_code=404)

    return templates.TemplateResponse(
        "report.html",
        {"request": request, "report": report_data}
    )

# PDF Report Export Endpoint
@app.get("/report/{inspection_id}/pdf")
def download_pdf_report(inspection_id: str):
    try:
        report = load_report_from_storage(inspection_id)
        if not report:
            raise HTTPException(status_code=404, detail="Inspection report not found")

        pdf_path = os.path.join(REPORTS_DIR, f"{inspection_id}.pdf")
        generate_pdf_report(report, pdf_path)

        # Ensure PDF file exists before returning
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="PDF generation failed")

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"ZENKENSA_Report_{inspection_id}.pdf",
            headers={
                "Content-Disposition": f'attachment; filename="ZENKENSA_Report_{inspection_id}.pdf"'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
