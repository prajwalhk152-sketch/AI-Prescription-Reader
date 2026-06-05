import json
import os
import re
import html
from datetime import datetime
from io import BytesIO

import streamlit as st
from PIL import Image

UPLOAD_DIR = "outputs/module_03_upload"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _safe_filename(file_name):
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", file_name.strip())
    return cleaned.strip("_") or "prescription_upload"


def _format_file_size(size_bytes):
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    return f"{size_bytes / 1024:.2f} KB"


def _render_upload_styles():
    st.markdown(
        """
        <style>
            .upload-hero {
                background:
                    linear-gradient(135deg, rgba(16, 54, 69, 0.92), rgba(40, 91, 116, 0.72)),
                    radial-gradient(circle at 12% 20%, rgba(255, 255, 255, 0.18), transparent 26%),
                    linear-gradient(90deg, rgba(217, 244, 244, 0.22), rgba(255, 255, 255, 0));
                color: white;
                padding: 1.8rem 2rem;
                border-radius: 8px;
                margin-bottom: 1.25rem;
                box-shadow: 0 12px 30px rgba(16, 54, 69, 0.18);
            }

            .upload-hero h2 {
                font-size: 1.9rem;
                margin: 0 0 0.35rem 0;
                letter-spacing: 0;
            }

            .upload-hero p {
                margin: 0;
                max-width: 760px;
                color: rgba(255, 255, 255, 0.9);
            }

            .upload-panel {
                background: #ffffff;
                border: 1px solid rgba(31, 92, 112, 0.16);
                border-radius: 8px;
                padding: 1.2rem;
                box-shadow: 0 6px 18px rgba(20, 39, 54, 0.08);
                min-height: 180px;
            }

            .upload-panel-title {
                color: #24576d;
                font-weight: 750;
                font-size: 1.05rem;
                margin: 0 0 0.55rem 0;
            }

            .upload-chip-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-top: 0.9rem;
            }

            .upload-chip {
                background: #e9f6f4;
                color: #1f5f61;
                border: 1px solid rgba(31, 95, 97, 0.14);
                border-radius: 999px;
                padding: 0.35rem 0.7rem;
                font-size: 0.84rem;
                font-weight: 650;
            }

            .upload-detail-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.75rem;
                margin-top: 0.8rem;
            }

            .upload-detail {
                background: #f7fbfc;
                border-left: 4px solid #2f8f93;
                border-radius: 7px;
                padding: 0.75rem;
            }

            .upload-detail-label {
                color: #667985;
                font-size: 0.78rem;
                font-weight: 700;
                text-transform: uppercase;
            }

            .upload-detail-value {
                color: #203847;
                font-weight: 750;
                margin-top: 0.2rem;
                overflow-wrap: anywhere;
            }

            .upload-empty {
                border: 1px dashed rgba(36, 87, 109, 0.3);
                border-radius: 8px;
                padding: 2rem;
                text-align: center;
                background: linear-gradient(180deg, #fbfefe, #f2faf9);
                color: #496270;
            }

            div[data-testid="stFileUploader"] {
                margin-bottom: 1rem;
            }

            div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] {
                min-height: 178px;
                border: 1px solid rgba(22, 127, 142, 0.34);
                border-radius: 12px;
                background:
                    linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(229, 248, 249, 0.88)),
                    radial-gradient(circle at 18% 22%, rgba(20, 151, 163, 0.16), transparent 28%),
                    radial-gradient(circle at 82% 80%, rgba(39, 93, 115, 0.12), transparent 26%);
                box-shadow:
                    0 14px 30px rgba(20, 70, 88, 0.13),
                    inset 0 1px 0 rgba(255, 255, 255, 0.95);
                overflow: hidden;
                position: relative;
            }

            div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]::before {
                content: "";
                position: absolute;
                left: 1.15rem;
                top: 1rem;
                width: 58px;
                height: 74px;
                border-radius: 8px;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(237, 249, 250, 0.94));
                border: 1px solid rgba(22, 127, 142, 0.24);
                box-shadow: 0 10px 18px rgba(21, 91, 109, 0.12);
                transform: rotate(-5deg);
            }

            div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]::after {
                content: "";
                position: absolute;
                left: 2rem;
                top: 2.15rem;
                width: 29px;
                height: 29px;
                border-radius: 50%;
                background: linear-gradient(#1ba8b1, #12758b);
                box-shadow:
                    0 0 0 8px rgba(27, 168, 177, 0.12),
                    0 8px 14px rgba(18, 117, 139, 0.22);
            }

            div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"]:hover {
                border-color: rgba(18, 117, 139, 0.58);
                box-shadow:
                    0 18px 38px rgba(20, 70, 88, 0.18),
                    inset 0 1px 0 rgba(255, 255, 255, 1);
                transform: translateY(-1px);
            }

            div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] > div {
                padding-left: 5.6rem;
                position: relative;
                z-index: 1;
            }

            div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] small {
                color: #607784;
            }

            div[data-testid="stFileUploader"] button {
                min-height: 42px;
                padding: 0.55rem 1.1rem;
                border-radius: 8px;
                border: 1px solid rgba(18, 117, 139, 0.46);
                background: linear-gradient(180deg, #ffffff, #e8f8f9);
                color: #145f72;
                font-weight: 750;
                box-shadow:
                    0 8px 16px rgba(20, 70, 88, 0.12),
                    inset 0 1px 0 rgba(255, 255, 255, 0.92);
            }

            div[data-testid="stFileUploader"] button:hover {
                border-color: rgba(18, 117, 139, 0.68);
                color: #0f5364;
                background: linear-gradient(180deg, #ffffff, #d9f5f6);
            }

            .st-key-upload_submit_button button {
                min-height: 50px;
                border-radius: 10px;
                border: 1px solid rgba(12, 91, 107, 0.42);
                background: linear-gradient(180deg, #1db3bd 0%, #13889c 52%, #0c6478 100%);
                color: white;
                font-weight: 800;
                letter-spacing: 0;
                box-shadow:
                    0 14px 24px rgba(13, 105, 126, 0.24),
                    inset 0 1px 0 rgba(255, 255, 255, 0.28);
            }

            .st-key-upload_submit_button button:hover:not(:disabled) {
                border-color: rgba(255, 255, 255, 0.44);
                background: linear-gradient(180deg, #26c2cb 0%, #1595a7 52%, #0d6f84 100%);
                transform: translateY(-1px);
                box-shadow:
                    0 18px 30px rgba(13, 105, 126, 0.28),
                    inset 0 1px 0 rgba(255, 255, 255, 0.34);
            }

            .st-key-upload_submit_button button:disabled {
                background: linear-gradient(180deg, #cbd9dd, #aebec4);
                color: rgba(255, 255, 255, 0.84);
                border-color: rgba(130, 152, 160, 0.35);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.24);
            }

            @media (max-width: 700px) {
                div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] > div {
                    padding-left: 0;
                    padding-top: 5rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _save_upload(uploaded_file, file_bytes):
    file_name = uploaded_file.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_file_name = _safe_filename(file_name)
    saved_file_name = f"{timestamp}_{safe_file_name}"
    saved_path = os.path.join(UPLOAD_DIR, saved_file_name)

    with open(saved_path, "wb") as file:
        file.write(file_bytes)

    metadata = {
        "original_file_name": file_name,
        "saved_file_name": saved_file_name,
        "file_type": uploaded_file.type,
        "file_size_kb": round(uploaded_file.size / 1024, 2),
        "saved_path": saved_path,
        "upload_time": str(datetime.now()),
    }

    metadata_path = os.path.join(UPLOAD_DIR, f"{timestamp}_metadata.json")
    with open(metadata_path, "w") as json_file:
        json.dump(metadata, json_file, indent=4)

    return metadata, metadata_path


def show_module_03_upload():
    _render_upload_styles()

    st.markdown(
        """
        <div class="upload-hero">
            <h2>Prescription Intake Desk</h2>
            <p>Upload a clear prescription image or PDF, review the preview, then submit it for preprocessing and OCR.</p>
            <div class="upload-chip-row">
                <span class="upload-chip">JPG</span>
                <span class="upload-chip">JPEG</span>
                <span class="upload-chip">PNG</span>
                <span class="upload-chip">PDF</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_col, preview_col = st.columns([1.05, 1], gap="large")

    with upload_col:
        st.markdown('<div class="upload-panel-title">Upload Prescription</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Prescription file",
            type=["jpg", "jpeg", "png", "pdf"],
            label_visibility="collapsed",
            help="Upload JPG, JPEG, PNG, or PDF files.",
        )

        patient_reference = st.text_input(
            "Patient Reference",
            placeholder="Optional: patient name or visit ID",
            help="Optional label for your local record.",
        )

        intake_note = st.text_area(
            "Intake Note",
            placeholder="Optional: add a short note before submission",
            height=90,
        )

        submit_disabled = uploaded_file is None
        submit_label = "Submit Prescription" if uploaded_file is not None else "Choose File To Submit"
        submit_clicked = st.button(
            submit_label,
            type="primary",
            use_container_width=True,
            disabled=submit_disabled,
            key="upload_submit_button",
        )
        if uploaded_file is None:
            st.caption("Select a prescription file to enable the submit button.")
        else:
            st.caption("Ready. Click Submit Prescription to save this upload.")

    with preview_col:
        if uploaded_file is None:
            st.markdown(
                """
                <div class="upload-empty">
                    <strong>No prescription selected</strong><br>
                    Choose a file to preview the prescription before submitting.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            file_bytes = uploaded_file.getvalue()
            file_type = uploaded_file.type

            st.markdown('<div class="upload-panel-title">Review Before Submit</div>', unsafe_allow_html=True)

            if file_type in ["image/jpeg", "image/png", "image/jpg"]:
                image = Image.open(BytesIO(file_bytes))
                st.image(image, caption="Prescription preview", width=340)
            else:
                st.info("PDF selected. The file will be saved and handled in later steps.")

            st.markdown(
                f"""
                <div class="upload-detail-grid">
                    <div class="upload-detail">
                        <div class="upload-detail-label">File Name</div>
                        <div class="upload-detail-value">{html.escape(uploaded_file.name)}</div>
                    </div>
                    <div class="upload-detail">
                        <div class="upload-detail-label">File Size</div>
                        <div class="upload-detail-value">{_format_file_size(uploaded_file.size)}</div>
                    </div>
                    <div class="upload-detail">
                        <div class="upload-detail-label">File Type</div>
                        <div class="upload-detail-value">{html.escape(file_type or "Unknown")}</div>
                    </div>
                    <div class="upload-detail">
                        <div class="upload-detail-label">Status</div>
                        <div class="upload-detail-value">Ready to submit</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if submit_clicked:
        metadata, metadata_path = _save_upload(uploaded_file, uploaded_file.getvalue())

        if patient_reference.strip():
            metadata["patient_reference"] = patient_reference.strip()
        if intake_note.strip():
            metadata["intake_note"] = intake_note.strip()

        with open(metadata_path, "w") as json_file:
            json.dump(metadata, json_file, indent=4)

        st.session_state["latest_upload_metadata"] = metadata
        st.success("Prescription submitted successfully.")

    if "latest_upload_metadata" in st.session_state:
        st.markdown("#### Latest Submitted Prescription")
        st.json(st.session_state["latest_upload_metadata"])
        st.info("This upload is ready for Image Preprocessing.")
