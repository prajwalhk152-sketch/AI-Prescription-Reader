import streamlit as st
import os
import pandas as pd
import json

UPLOAD_DIR = "outputs/module_03_upload"
PREPROCESS_DIR = "outputs/module_04_preprocessed"
OCR_DIR = "outputs/module_05_ocr"
MEDICINE_DIR = "outputs/module_06_medicines"
DOSAGE_DIR = "outputs/module_07_dosage"
BENEFITS_DIR = "outputs/module_08_benefits"
INTERACTION_DIR = "outputs/module_09_interactions"
RECOMMENDATION_DIR = "outputs/module_10_recommendations"


def get_latest_file(folder, extensions):
    if not os.path.exists(folder):
        return None

    files = [
        os.path.join(folder, file)
        for file in os.listdir(folder)
        if file.lower().endswith(tuple(extensions))
    ]

    if not files:
        return None

    return max(files, key=os.path.getctime)


def read_text_file(path):
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    return ""


def read_json_file(path):
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


def show_csv_section(title, folder):
    latest_csv = get_latest_file(folder, [".csv"])

    st.subheader(title)

    if latest_csv:
        df = pd.read_csv(latest_csv)
        st.dataframe(df, use_container_width=True)
        st.caption(f"Loaded file: {latest_csv}")
        return df
    else:
        st.warning(f"No output found for {title}")
        return None


def show_module_11_dashboard():
    st.title("Interactive Prescription Intelligence Dashboard")

    st.write(
        "This dashboard combines all previous step outputs into one final view."
    )

    st.divider()

    uploaded_image = get_latest_file(UPLOAD_DIR, [".jpg", ".jpeg", ".png"])
    preprocessed_image = get_latest_file(PREPROCESS_DIR, [".jpg", ".jpeg", ".png"])
    ocr_text_file = get_latest_file(OCR_DIR, [".txt"])

    medicine_csv = get_latest_file(MEDICINE_DIR, [".csv"])
    dosage_csv = get_latest_file(DOSAGE_DIR, [".csv"])
    benefits_csv = get_latest_file(BENEFITS_DIR, [".csv"])
    interactions_csv = get_latest_file(INTERACTION_DIR, [".csv"])
    recommendations_csv = get_latest_file(RECOMMENDATION_DIR, [".csv"])

    total_outputs = sum([
        uploaded_image is not None,
        preprocessed_image is not None,
        ocr_text_file is not None,
        medicine_csv is not None,
        dosage_csv is not None,
        benefits_csv is not None,
        interactions_csv is not None,
        recommendations_csv is not None
    ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Steps Completed", f"{total_outputs}/8")

    with col2:
        st.metric("Prescription Uploaded", "Yes" if uploaded_image else "No")

    with col3:
        st.metric("OCR Available", "Yes" if ocr_text_file else "No")

    with col4:
        st.metric("Medicine Data", "Yes" if medicine_csv else "No")

    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Prescription Images",
        "OCR Text",
        "Medicines",
        "Dosage",
        "Benefits",
        "Interactions",
        "Recommendations"
    ])

    with tab1:
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Uploaded Prescription")
            if uploaded_image:
                st.image(uploaded_image, width=320)
                st.caption(uploaded_image)
            else:
                st.warning("No uploaded image found. Complete Upload.")

        with col_b:
            st.subheader("Preprocessed Image")
            if preprocessed_image:
                st.image(preprocessed_image, width=320)
                st.caption(preprocessed_image)
            else:
                st.warning("No preprocessed image found. Complete Preprocessing.")

    with tab2:
        st.subheader("OCR Extracted Text")
        if ocr_text_file:
            ocr_text = read_text_file(ocr_text_file)
            st.text_area("OCR Output", ocr_text, height=350)
            st.caption(f"Loaded file: {ocr_text_file}")
        else:
            st.warning("No OCR text found. Complete OCR.")

    with tab3:
        medicine_df = show_csv_section(
            "Detected Medicines",
            MEDICINE_DIR
        )

        if medicine_df is not None:
            st.success(f"Total medicines detected: {len(medicine_df)}")

    with tab4:
        dosage_df = show_csv_section(
            "Dosage & Timing",
            DOSAGE_DIR
        )

        if dosage_df is not None:
            st.success(f"Total dosage rows: {len(dosage_df)}")

    with tab5:
        benefits_df = show_csv_section(
            "Medicine Benefits",
            BENEFITS_DIR
        )

        if benefits_df is not None:
            for _, row in benefits_df.iterrows():
                with st.expander(row.get("medicine_name", "Medicine")):
                    st.write("**Category:**", row.get("category", "N/A"))
                    st.write("**Benefit:**", row.get("benefit_explanation", "N/A"))
                    st.warning(row.get("patient_note", "Follow doctor advice."))

    with tab6:
        interactions_df = show_csv_section(
            "Drug Interaction Warnings",
            INTERACTION_DIR
        )

        if interactions_df is not None:
            high_risk = len(interactions_df[interactions_df["risk_level"] == "High"]) if "risk_level" in interactions_df.columns else 0
            moderate_risk = len(interactions_df[interactions_df["risk_level"] == "Moderate"]) if "risk_level" in interactions_df.columns else 0

            col_x, col_y = st.columns(2)
            with col_x:
                st.metric("High Risk Interactions", high_risk)
            with col_y:
                st.metric("Moderate Risk Interactions", moderate_risk)

            for _, row in interactions_df.iterrows():
                level = row.get("risk_level", "No Known Risk")
                msg = (
                    f"{row.get('medicine_1', '')} + {row.get('medicine_2', '')} "
                    f"({row.get('risk_percent', 0)}%) - {row.get('warning', '')}"
                )

                if level == "High":
                    st.error(msg)
                elif level == "Moderate":
                    st.warning(msg)
                elif level == "Low":
                    st.info(msg)
                else:
                    st.success(msg)

    with tab7:
        recommendations_df = show_csv_section(
            "Medicine Recommendations",
            RECOMMENDATION_DIR
        )

        if recommendations_df is not None:
            for _, row in recommendations_df.iterrows():
                with st.expander(row.get("medicine_name", "Medicine")):
                    st.write("**Category:**", row.get("category", "N/A"))
                    st.write("**Recommendations:**", row.get("recommendations", "N/A"))
                    st.warning(row.get("note", "Use alternatives only after doctor consultation."))

    st.divider()

    st.subheader("Final Patient-Friendly Summary")

    if medicine_csv and dosage_csv and benefits_csv:
        st.success("Summary can be generated from available step outputs.")

        if st.button("Generate Final Summary"):
            medicine_df = pd.read_csv(medicine_csv)
            dosage_df = pd.read_csv(dosage_csv)
            benefits_df = pd.read_csv(benefits_csv)

            st.markdown("## Prescription Summary")

            st.markdown("### Detected Medicines")
            for _, row in medicine_df.iterrows():
                st.write(f"- **{row.get('medicine_name', 'Medicine')}**: {row.get('category', 'N/A')}")

            st.markdown("### Dosage & Timing")
            for _, row in dosage_df.iterrows():
                st.write(
                    f"- Dosage: **{row.get('dosage', 'Not detected')}**, "
                    f"Timing: **{row.get('timing', 'Not detected')}**, "
                    f"Frequency: **{row.get('frequency', 'Not detected')}**"
                )

            st.markdown("### Medicine Benefits")
            for _, row in benefits_df.iterrows():
                st.write(
                    f"- **{row.get('medicine_name', 'Medicine')}**: "
                    f"{row.get('benefit_explanation', 'N/A')}"
                )

            st.warning(
                "Medical Disclaimer: This project is for internship and educational use only. "
                "Always consult a qualified doctor before taking or changing medicines."
            )
    else:
        st.warning(
            "Complete Medicine Detection, Dosage, and Benefits first to generate final patient summary."
        )
