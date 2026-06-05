import streamlit as st
import os
import re
import json
import pandas as pd
from datetime import datetime
try:
    import spacy
except ImportError:
    spacy = None

from modules.module_06_medicine_detection import MEDICINE_DATABASE, detect_medicines

INPUT_DIR = "outputs/module_05_ocr"
OUTPUT_DIR = "outputs/module_07_dosage"

os.makedirs(OUTPUT_DIR, exist_ok=True)

NLP = None


def get_ocr_text_files():
    if not os.path.exists(INPUT_DIR):
        return []

    files = []
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".txt"):
            files.append(file)

    return sorted(files, reverse=True)


def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def get_nlp_pipeline():
    global NLP

    if spacy is None:
        return None

    if NLP is not None:
        return NLP

    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = [
        {
            "label": "MEDICINE",
            "pattern": [{"LOWER": token} for token in medicine_name.split()]
        }
        for medicine_name in sorted(MEDICINE_DATABASE.keys(), key=len, reverse=True)
    ]
    ruler.add_patterns(patterns)
    nlp.add_pipe("sentencizer")
    NLP = nlp
    return NLP


def normalize_medicine_name(name):
    normalized = re.sub(r"\s+", " ", name.strip().lower())
    return normalized.title()


def extract_medicine_entities(text):
    nlp = get_nlp_pipeline()
    if nlp is None:
        detected_medicines = detect_medicines(text)
        return [
            {
                "medicine_name": medicine["medicine_name"],
                "category": medicine["category"],
                "start_char": -1,
                "end_char": -1,
                "source_text": text.strip(),
                "extraction_method": "Medicine detector fallback"
            }
            for medicine in detected_medicines
        ]

    doc = nlp(text)
    entities = {}

    for ent in doc.ents:
        if ent.label_ != "MEDICINE":
            continue

        key = ent.text.lower().strip()
        category = MEDICINE_DATABASE.get(key, "Unknown")
        display_name = normalize_medicine_name(ent.text)

        entities[key] = {
            "medicine_name": display_name,
            "category": category,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
            "source_text": ent.sent.text.strip() if ent.sent else ent.text,
            "extraction_method": "spaCy EntityRuler"
        }

    return list(entities.values())


def extract_dosage(text):
    dosage_patterns = [
        r"\b\d+\s?mg\b",
        r"\b\d+\s?ml\b",
        r"\b\d+\s?g\b",
        r"\b\d+\s?mcg\b",
        r"\b\d+\s?tablet\b",
        r"\b\d+\s?tablets\b",
        r"\b\d+\s?tab\b",
        r"\b\d+\s?capsule\b",
        r"\b\d+\s?capsules\b",
        r"\b\d+\s?cap\b",
        r"\b\d+\s?drops\b",
        r"\b\d+\s?spoon\b"
    ]

    found_dosages = []

    for pattern in dosage_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        found_dosages.extend(matches)

    return list(set(found_dosages))


def extract_timing(text):
    timing_keywords = [
        "once daily",
        "twice daily",
        "three times daily",
        "morning",
        "afternoon",
        "evening",
        "night",
        "before food",
        "after food",
        "before meal",
        "after meal",
        "before breakfast",
        "after breakfast",
        "before lunch",
        "after lunch",
        "before dinner",
        "after dinner",
        "before sleep",
        "at bedtime",
        "daily",
        "weekly",
        "sos",
        "as needed"
    ]

    found_timings = []

    text_lower = text.lower()

    for timing in timing_keywords:
        if timing in text_lower:
            found_timings.append(timing.title())

    return list(set(found_timings))


def extract_frequency(text):
    frequency_patterns = [
        r"\bOD\b",
        r"\bBD\b",
        r"\bBID\b",
        r"\bTID\b",
        r"\bQID\b",
        r"\bSOS\b",
        r"\bHS\b",
        r"\b1-0-0\b",
        r"\b0-1-0\b",
        r"\b0-0-1\b",
        r"\b1-1-0\b",
        r"\b1-0-1\b",
        r"\b0-1-1\b",
        r"\b1-1-1\b"
    ]

    found_frequency = []

    for pattern in frequency_patterns:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        found_frequency.extend(matches)

    return list(set(found_frequency))


def split_prescription_segments(text):
    segments = []
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            segments.append(cleaned)

    if not segments:
        segments = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", text) if sentence.strip()]

    return segments


def create_dosage_summary(text):
    medicine_entities = extract_medicine_entities(text)
    all_dosages = extract_dosage(text)
    all_timings = extract_timing(text)
    all_frequencies = extract_frequency(text)
    rows = []

    for segment in split_prescription_segments(text):
        segment_medicines = extract_medicine_entities(segment)
        if not segment_medicines:
            continue

        segment_dosages = extract_dosage(segment)
        segment_timings = extract_timing(segment)
        segment_frequencies = extract_frequency(segment)

        for medicine in segment_medicines:
            rows.append({
                "medicine_name": medicine["medicine_name"],
                "category": medicine["category"],
                "dosage": ", ".join(segment_dosages) if segment_dosages else "Not detected",
                "timing": ", ".join(segment_timings) if segment_timings else "Not detected",
                "frequency": ", ".join(segment_frequencies) if segment_frequencies else "Not detected",
                "source_text": segment,
                "extraction_method": medicine["extraction_method"]
            })

    if not rows:
        max_len = max(len(all_dosages), len(all_timings), len(all_frequencies), 1)
        for i in range(max_len):
            rows.append({
                "medicine_name": "Not detected",
                "category": "Unknown",
                "dosage": all_dosages[i] if i < len(all_dosages) else "Not detected",
                "timing": all_timings[i] if i < len(all_timings) else "Not detected",
                "frequency": all_frequencies[i] if i < len(all_frequencies) else "Not detected",
                "source_text": "No medicine entity detected",
                "extraction_method": "Dosage pattern fallback"
            })

    return rows, medicine_entities, all_dosages, all_timings, all_frequencies


def explain_frequency(freq):
    meanings = {
        "OD": "Once daily",
        "BD": "Twice daily",
        "BID": "Twice daily",
        "TID": "Three times daily",
        "QID": "Four times daily",
        "SOS": "Use only when needed",
        "HS": "At bedtime",
        "1-0-0": "Morning only",
        "0-1-0": "Afternoon only",
        "0-0-1": "Night only",
        "1-1-0": "Morning and afternoon",
        "1-0-1": "Morning and night",
        "0-1-1": "Afternoon and night",
        "1-1-1": "Morning, afternoon, and night"
    }

    return meanings.get(freq.upper(), "Meaning not available")


def show_module_07_dosage_extraction():
    st.title("Dosage & Timing Extraction")

    st.write(
        "This step extracts dosage, timing, and frequency instructions from OCR text."
    )

    text_files = get_ocr_text_files()

    if not text_files:
        st.warning("No OCR text found. Please complete OCR Text Extraction first.")
        return

    selected_file = st.selectbox("Select OCR text file", text_files)

    text_path = os.path.join(INPUT_DIR, selected_file)
    ocr_text = read_text_file(text_path)

    st.subheader("OCR Text Input")
    st.text_area("Extracted OCR Text", ocr_text, height=220)

    if st.button("Extract Dosage & Timing"):
        rows, medicines, dosages, timings, frequencies = create_dosage_summary(ocr_text)

        df = pd.DataFrame(rows)

        st.success("Dosage and timing extraction completed.")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Medicines Found", len(medicines))

        with col2:
            st.metric("Dosages Found", len(dosages))

        with col3:
            st.metric("Timings Found", len(timings))

        with col4:
            st.metric("Frequencies Found", len(frequencies))

        st.subheader("Dosage & Timing Output")
        st.dataframe(df, use_container_width=True)

        if frequencies:
            st.subheader("Frequency Meaning")
            for freq in frequencies:
                st.write(f"**{freq}:** {explain_frequency(freq)}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_file = f"dosage_timing_{timestamp}.csv"
        json_file = f"dosage_timing_{timestamp}.json"

        csv_path = os.path.join(OUTPUT_DIR, csv_file)
        json_path = os.path.join(OUTPUT_DIR, json_file)

        df.to_csv(csv_path, index=False)

        result_data = {
            "input_file": selected_file,
            "input_path": text_path,
            "medicines": medicines,
            "dosages": dosages,
            "timings": timings,
            "frequencies": frequencies,
            "table": rows,
            "created_at": str(datetime.now())
        }

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, indent=4)

        st.subheader("Saved Output")
        st.write("**CSV File:**", csv_path)
        st.write("**JSON File:**", json_path)

        st.download_button(
            "Download Dosage CSV",
            data=df.to_csv(index=False),
            file_name="dosage_timing.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download Dosage JSON",
            data=json.dumps(result_data, indent=4),
            file_name="dosage_timing.json",
            mime="application/json"
        )

        st.info("This output is ready for Medicine Benefits Explanation.")
