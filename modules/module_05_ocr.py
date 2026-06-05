import streamlit as st
import os
import json
import shutil
import re
import cv2
import numpy as np
import pytesseract
from PIL import Image
from datetime import datetime

INPUT_DIR = "outputs/module_04_preprocessed"
OUTPUT_DIR = "outputs/module_05_ocr"

TESSERACT_POSSIBLE_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

EASYOCR_READER = None


def configure_tesseract_path():
    existing_cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "")

    if existing_cmd and os.path.exists(existing_cmd):
        return existing_cmd

    for path in TESSERACT_POSSIBLE_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return path

    found_cmd = shutil.which("tesseract")
    if found_cmd:
        pytesseract.pytesseract.tesseract_cmd = found_cmd
        return found_cmd

    return ""


TESSERACT_CMD = configure_tesseract_path()


def get_easyocr_reader():
    global EASYOCR_READER

    if EASYOCR_READER is None:
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "EasyOCR is not installed in this deployment. Use Tesseract OCR, "
                "or add easyocr to requirements.txt if you need it."
            ) from exc
        EASYOCR_READER = easyocr.Reader(["en"], gpu=False)

    return EASYOCR_READER


def get_preprocessed_images():
    if not os.path.exists(INPUT_DIR):
        return []

    allowed_extensions = [".jpg", ".jpeg", ".png"]
    images = []

    for file in os.listdir(INPUT_DIR):
        file_path = os.path.join(INPUT_DIR, file)

        if os.path.isfile(file_path):
            if os.path.splitext(file)[1].lower() in allowed_extensions:
                images.append(file)

    return sorted(images, reverse=True)


def resize_for_ocr(image):
    height, width = image.shape[:2]
    target_width = 1200

    # Only downscale very large images for faster OCR.
    # Upscaling smaller images adds time without improving OCR quality.
    if width <= target_width:
        return image

    scale = target_width / width
    return cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)


def deskew_image(gray):
    inverted = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(inverted > 0))

    if len(coords) < 50:
        return gray

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) > 12:
        return gray

    height, width = gray.shape[:2]
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray,
        matrix,
        (width, height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


def build_handwriting_variants(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return []

    image = resize_for_ocr(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = deskew_image(gray)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)
    denoised = cv2.fastNlMeansDenoising(contrast, None, 18, 7, 21)
    sharpened = cv2.addWeighted(denoised, 1.55, cv2.GaussianBlur(denoised, (0, 0), 1.2), -0.55, 0)

    adaptive = cv2.adaptiveThreshold(
        sharpened,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        9
    )
    inverse = cv2.bitwise_not(adaptive)
    closed = cv2.morphologyEx(
        inverse,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
        iterations=1
    )
    closed = cv2.bitwise_not(closed)

    return [
        ("contrast", contrast),
        ("denoised", denoised),
        ("sharpened", sharpened),
        ("adaptive_threshold", adaptive),
        ("stroke_repaired", closed),
    ]


def merge_ocr_texts(*texts):
    unique_lines = []
    seen = set()

    for text in texts:
        if not text:
            continue
        if " Error:" in text or "executable not found" in text:
            unique_lines.append(text.strip())
            continue

        for line in text.splitlines():
            cleaned = re.sub(r"\s+", " ", line).strip()
            if not cleaned:
                continue

            key = re.sub(r"[^a-zA-Z0-9]+", "", cleaned).lower()
            if len(key) < 2 or key in seen:
                continue

            seen.add(key)
            unique_lines.append(cleaned)

    return "\n".join(unique_lines).strip()


def extract_text_tesseract(image_path, handwriting_mode=False):
    if not TESSERACT_CMD:
        return (
            "Tesseract OCR executable not found. "
            "Please restart your terminal or ensure Tesseract is installed and on PATH."
        )

    try:
        if handwriting_mode:
            texts = []
            configs = [
                r"--oem 3 --psm 6",
                r"--oem 3 --psm 11",
                r"--oem 3 --psm 12",
            ]
            for _, variant in build_handwriting_variants(image_path):
                for config in configs:
                    texts.append(pytesseract.image_to_string(variant, config=config))
            return merge_ocr_texts(*texts)

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return ""

        custom_config = r"--oem 1 --psm 6 -l eng"
        return pytesseract.image_to_string(image, config=custom_config).strip()
    except Exception as e:
        return f"Tesseract OCR Error: {str(e)}"


def extract_text_easyocr(image_path, handwriting_mode=False):
    try:
        reader = get_easyocr_reader()

        if handwriting_mode:
            texts = []
            for _, variant in build_handwriting_variants(image_path):
                result = reader.readtext(
                    variant,
                    detail=0,
                    paragraph=False,
                    decoder="beamsearch",
                    width_ths=0.8,
                    contrast_ths=0.05,
                    adjust_contrast=0.7
                )
                texts.append("\n".join(result))
            return merge_ocr_texts(*texts)

        result = reader.readtext(image_path, detail=0)

        text = "\n".join(result)
        return text.strip()

    except Exception as e:
        return f"EasyOCR Error: {str(e)}"


def get_medicine_rescue_matches(text):
    if not text:
        return []

    try:
        from modules.module_06_medicine_detection import detect_medicines
        return detect_medicines(text)
    except Exception:
        return []


def calculate_basic_confidence(text):
    if not text:
        return 0

    characters = len(text)
    words = len(text.split())

    if characters < 10:
        return 20
    elif words < 3:
        return 35
    elif words < 8:
        return 60
    else:
        return 80


def show_module_05_ocr():
    st.title("OCR Text Extraction")

    st.write(
        "It extracts text from the preprocessed prescription image. "
        "The extracted text will be used in the next steps for medicine detection "
        "and dosage extraction."
    )

    images = get_preprocessed_images()

    if not images:
        st.warning(
            "No preprocessed image found. please process the image first"
        )
        return

    selected_image = st.selectbox(
        "Select preprocessed image from above image preprocessing dashboard",
        images
    )

    image_path = os.path.join(INPUT_DIR, selected_image)

    st.subheader("Selected Preprocessed Image")
    st.image(image_path, caption=selected_image, width=320)

    st.subheader("Choose OCR Engine")

    ocr_engine = st.radio(
        "OCR Engine",
        [
            "Tesseract OCR",
            "EasyOCR",
            "Both"
        ],
        horizontal=True
    )

    handwriting_mode = st.checkbox(
        "Difficult handwriting mode",
        value=False,
        help="Runs OCR on multiple enhanced image versions for hard-to-read prescriptions. This is slower, so enable it only when needed."
    )

    if st.button("Extract Text"):
        with st.spinner("Extracting text from prescription image..."):
            tesseract_text = ""
            easyocr_text = ""

            if ocr_engine in ["Tesseract OCR", "Both"]:
                tesseract_text = extract_text_tesseract(image_path, handwriting_mode)

            if ocr_engine in ["EasyOCR", "Both"]:
                easyocr_text = extract_text_easyocr(image_path, handwriting_mode)

            combined_text = merge_ocr_texts(easyocr_text, tesseract_text)
            rescue_matches = get_medicine_rescue_matches(combined_text)

            confidence = calculate_basic_confidence(combined_text)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            text_file_name = f"ocr_text_{timestamp}.txt"
            json_file_name = f"ocr_result_{timestamp}.json"

            text_path = os.path.join(OUTPUT_DIR, text_file_name)
            json_path = os.path.join(OUTPUT_DIR, json_file_name)

            with open(text_path, "w", encoding="utf-8") as file:
                file.write(combined_text)

            result_data = {
                "input_image": selected_image,
                "input_path": image_path,
                "ocr_engine": ocr_engine,
                "handwriting_mode": handwriting_mode,
                "tesseract_text": tesseract_text,
                "easyocr_text": easyocr_text,
                "combined_text": combined_text,
                "medicine_rescue_matches": rescue_matches,
                "basic_confidence_percent": confidence,
                "text_file_path": text_path,
                "created_at": str(datetime.now())
            }

            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, indent=4)

        st.success("OCR text extraction completed successfully.")

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Tesseract Output",
                "EasyOCR Output",
                "Final Combined Text",
                "Medicine Rescue"
            ]
        )

        with tab1:
            if tesseract_text:
                st.text_area(
                    "Tesseract OCR Text",
                    tesseract_text,
                    height=250
                )
            else:
                st.info("Tesseract OCR was not selected.")

        with tab2:
            if easyocr_text:
                st.text_area(
                    "EasyOCR Text",
                    easyocr_text,
                    height=250
                )
            else:
                st.info("EasyOCR was not selected.")

        with tab3:
            st.text_area(
                "Final OCR Text",
                combined_text,
                height=300
            )

        with tab4:
            if rescue_matches:
                st.dataframe(rescue_matches, use_container_width=True)
            else:
                st.info("No medicine names were confidently rescued from OCR text.")

        st.subheader("OCR Confidence")

        st.progress(confidence / 100)
        st.write(f"Estimated OCR Confidence: **{confidence}%**")

        st.subheader("OCR Output")

        st.success("OCR text saved successfully.")
        st.write("**Text File:**", text_file_name)
        st.write("**JSON File:**", json_file_name)
        st.write("**Output Folder:**", OUTPUT_DIR)

        st.download_button(
            label="Download OCR Text",
            data=combined_text,
            file_name="ocr_extracted_text.txt",
            mime="text/plain"
        )

        st.download_button(
            label="Download OCR JSON",
            data=json.dumps(result_data, indent=4),
            file_name="ocr_result.json",
            mime="application/json"
        )

        st.info(
            "This OCR text is ready for Medicine detection: Medicine Name Detection using NLP."
        )

