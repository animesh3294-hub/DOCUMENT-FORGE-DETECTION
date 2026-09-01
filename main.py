from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image, ImageChops, ExifTags
import io
import re
import numpy as np
import cv2
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image_for_ocr(image_bytes: bytes) -> Image.Image:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    height, width = img.shape[:2]
    new_width = 1500
    new_height = int((new_width / width) * height)
    img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)

# --- NEW: METADATA / EXIF FORENSICS ---
def analyze_metadata(image: Image.Image) -> dict:
    suspicious_software = ['photoshop', 'gimp', 'canva', 'illustrator', 'paint']
    software_found = None
    is_tampered = False
    
    try:
        exif_data = image.getexif()
        if exif_data:
            # Tag 305 usually holds the "Software" signature in EXIF data
            software_found = exif_data.get(305)
            if software_found:
                if any(sus in str(software_found).lower() for sus in suspicious_software):
                    is_tampered = True
    except Exception:
        pass

    return {
        "metadata_present": image.getexif() is not None,
        "editing_software_detected": software_found if software_found else "None (Clean)",
        "tampering_suspected": is_tampered
    }

def perform_ela(image_bytes: bytes, quality=90) -> dict:
    original = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    buffer = io.BytesIO()
    original.save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer).convert('RGB')
    
    ela_image = ImageChops.difference(original, resaved)
    extrema = ela_image.getextrema()
    max_diff = max([ex[1] for ex in extrema]) if extrema else 1
    if max_diff == 0: max_diff = 1
        
    scale = 255.0 / max_diff
    ela_image = Image.eval(ela_image, lambda x: min(int(x * scale), 255))
    
    ela_arr = np.array(ela_image)
    mean_error = float(np.mean(ela_arr))
    
    return {
        "mean_error_score": round(mean_error, 2),
        "tampering_suspected": mean_error > 45.0
    }

def validate_mrz(raw_ocr_text: str) -> dict:
    text = raw_ocr_text.upper().replace(" ", "").replace("§", "8").replace("O", "0") 
    lines = text.split('\n')
    line2 = None
    
    for line in lines:
        clean_line = re.sub(r'[^A-Z0-9<]', '', line)
        if len(clean_line) >= 30 and any(c.isdigit() for c in clean_line) and not clean_line.startswith("P"):
            line2 = clean_line
            break

    if not line2:
        return {"found": False} # Not a passport, just a regular document

    try:
        printed_check_digit = int(line2[9])
        calculated_digit = sum((int(c) if c.isdigit() else (ord(c)-55 if c.isalpha() else 0)) * w for c, w in zip(line2[0:9], [7,3,1]*3)) % 10
        is_valid = (printed_check_digit == calculated_digit)
        return {"found": True, "valid": is_valid, "error": None if is_valid else "Checksum mismatch"}
    except Exception:
        return {"found": True, "valid": False, "error": "Invalid MRZ format"}

@app.post("/api/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    content = await file.read()
    raw_img = Image.open(io.BytesIO(content))
    cleaned_image = preprocess_image_for_ocr(content)
    
    # Run all 3 Forensic Modules
    extracted_text_raw = pytesseract.image_to_string(cleaned_image)
    metadata_results = analyze_metadata(raw_img)
    ela_results = perform_ela(content)
    mrz_results = validate_mrz(extracted_text_raw)
    
    # Universal Dynamic Risk Scoring
    risk_score = 5 # Baseline
    
    # 1. Pixel Tampering Penalty
    if ela_results.get("tampering_suspected"):
        risk_score += 45
        
    # 2. Metadata Penalty
    if metadata_results.get("tampering_suspected"):
        risk_score += 40
        
    # 3. Document-Specific Logic
    if mrz_results.get("found"):
        if not mrz_results.get("valid"):
            risk_score += 50 # Massive penalty for fake passports
    else:
        # If no MRZ is found, rely heavily on ELA and EXIF
        pass 

    risk_score = min(risk_score, 100)

    return {
        "filename": file.filename,
        "risk_score": risk_score,
        "document_type": "Passport" if mrz_results.get("found") else "General Document",
        "forensics": {
            "metadata": metadata_results,
            "ela": ela_results,
            "mrz": mrz_results,
            "ocr_preview": extracted_text_raw.strip()[:200] + "..." # Just show a snippet
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)