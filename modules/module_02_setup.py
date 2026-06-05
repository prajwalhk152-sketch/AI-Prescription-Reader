import streamlit as st
import os
import sys
import platform

def show_module_02_setup():
    st.title("Module 2: Environment Setup")
    st.write("This module verifies that the project environment is ready.")

    st.subheader("Project Objective")
    st.write(
        "The objective of this module is to set up the Streamlit project, "
        "install required libraries, create folders, and verify that the system is ready "
        "for AI prescription processing."
    )

    st.subheader("Technology Stack")

    tech_stack = {
        "Technology": [
            "Python",
            "Streamlit",
            "OpenCV",
            "Pillow",
            "NumPy",
            "Pandas",
            "Pytesseract",
            "EasyOCR",
            "spaCy",
            "Plotly",
            "SQLite"
        ],
        "Purpose": [
            "Main programming language",
            "Interactive dashboard",
            "Image preprocessing",
            "Image handling",
            "Array and image data processing",
            "Data table processing",
            "OCR text extraction",
            "OCR text extraction",
            "NLP medicine detection",
            "Charts and dashboard visuals",
            "Prescription data storage"
        ]
    }

    st.table(tech_stack)

    st.subheader("System Information")

    system_info = {
        "Python Version": sys.version,
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Current Working Directory": os.getcwd()
    }

    st.json(system_info)

    st.subheader("Create Output Folders")

    folders = [
        "outputs/module_03_upload",
        "outputs/module_04_preprocessed",
        "outputs/module_05_ocr",
        "outputs/module_06_medicines",
        "outputs/module_07_dosage",
        "outputs/module_08_benefits",
        "outputs/module_09_interactions",
        "outputs/module_10_recommendations",
        "database",
        "docs"
    ]

    if st.button("Create Required Folders"):
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

        st.success("All required folders created successfully.")

    st.subheader("Folder Checklist")

    for folder in folders:
        if os.path.exists(folder):
            st.success(f"{folder} exists")
        else:
            st.warning(f"{folder} missing")

    st.subheader("Module 2 Output")

    st.info(
        "After completing this module, the project environment is ready. "
        "You can now continue to Module 3: Prescription Upload System."
    )