import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

INPUT_DIR = "outputs/module_06_medicines"
OUTPUT_DIR = "outputs/module_10_recommendations"

os.makedirs(OUTPUT_DIR, exist_ok=True)

RECOMMENDATION_DATABASE = {
    "Paracetamol": ["Crocin", "Calpol", "Dolo 650"],
    "Crocin": ["Paracetamol", "Calpol", "Dolo 650"],
    "Calpol": ["Paracetamol", "Crocin", "Dolo 650"],
    "Dolo": ["Paracetamol", "Crocin", "Calpol"],

    "Ibuprofen": ["Combiflam", "Brufen"],
    "Aspirin": ["Ecosprin"],

    "Amoxicillin": ["Augmentin", "Moxikind"],
    "Azithromycin": ["Azee", "Azithral"],
    "Cefixime": ["Taxim-O", "Cefspan"],
    "Ciprofloxacin": ["Cifran", "Ciplox"],

    "Cetirizine": ["Levocetirizine", "Allegra", "Fexofenadine"],
    "Levocetirizine": ["Cetirizine", "Allegra"],
    "Fexofenadine": ["Allegra", "Cetirizine"],

    "Metformin": ["Glycomet", "Glucophage"],
    "Glimepiride": ["Amaryl", "Glimestar"],

    "Amlodipine": ["Amlong", "Stamlo"],
    "Losartan": ["Losar", "Repace"],
    "Telmisartan": ["Telma", "Telsartan"],

    "Atorvastatin": ["Atorlip", "Lipicure"],
    "Rosuvastatin": ["Rozavel", "Rosuvas"],

    "Pantoprazole": ["Pan-D", "Pantocid"],
    "Omeprazole": ["Omez", "Ocid"],
    "Rabeprazole": ["Razo", "Rabicip"],

    "Warfarin": ["Doctor consultation required"],
    "Clopidogrel": ["Doctor consultation required"],
    "Ecosprin": ["Doctor consultation required"],

    "Becosules": ["Supradyn", "Neurobion"],
    "Supradyn": ["Becosules", "Neurobion"],
    "Shelcal": ["Calcium + Vitamin D3"]
}


@st.cache_data(show_spinner=False)
def get_medicine_files():
    if not os.path.exists(INPUT_DIR):
        return []

    return sorted(
        [file for file in os.listdir(INPUT_DIR) if file.endswith(".csv")],
        reverse=True
    )


def get_recommendations(medicine_name, category):
    medicine_name = str(medicine_name).strip()

    if medicine_name in RECOMMENDATION_DATABASE:
        return RECOMMENDATION_DATABASE[medicine_name]

    category_lower = str(category).lower()

    if "fever" in category_lower or "pain" in category_lower:
        return ["Paracetamol", "Crocin", "Calpol"]

    if "antibiotic" in category_lower:
        return ["Doctor consultation required"]

    if "allergy" in category_lower:
        return ["Cetirizine", "Levocetirizine", "Fexofenadine"]

    if "acidity" in category_lower:
        return ["Pantoprazole", "Omeprazole", "Rabeprazole"]

    if "diabetes" in category_lower:
        return ["Doctor consultation required"]

    if "blood pressure" in category_lower:
        return ["Doctor consultation required"]

    return ["No alternative available in local database"]


def show_module_10_recommendations():
    st.title("Medicine Recommendation Engine")

    st.write(
        "This step suggests alternative/common medicines based on detected medicine names and categories."
    )

    medicine_files = get_medicine_files()

    if not medicine_files:
        st.warning("No medicine detection output found. Please complete Medicine Detection first.")
        return

    selected_file = st.selectbox(
        "Select detected medicine CSV",
        medicine_files
    )

    csv_path = os.path.join(INPUT_DIR, selected_file)
    df = pd.read_csv(csv_path)

    st.subheader("Detected Medicines Input")
    st.dataframe(df, use_container_width=True)

    if st.button("Generate Recommendations"):
        recommendation_output = []

        for _, row in df.iterrows():
            medicine_name = str(row["medicine_name"])
            category = str(row["category"])

            recommendations = get_recommendations(medicine_name, category)

            recommendation_output.append({
                "medicine_name": medicine_name,
                "category": category,
                "recommendations": ", ".join(recommendations),
                "note": "Use alternatives only after doctor consultation."
            })

        recommendation_df = pd.DataFrame(recommendation_output)

        st.success("Medicine recommendations generated successfully.")

        st.subheader("Medicine Recommendation Output")
        st.dataframe(recommendation_df, use_container_width=True)

        st.subheader("Recommendation Cards")

        for item in recommendation_output:
            with st.expander(item["medicine_name"]):
                st.write("**Category:**", item["category"])
                st.write("**Recommended Alternatives:**")
                for rec in item["recommendations"].split(", "):
                    st.write("-", rec)
                st.warning(item["note"])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_file = f"medicine_recommendations_{timestamp}.csv"
        json_file = f"medicine_recommendations_{timestamp}.json"

        csv_output_path = os.path.join(OUTPUT_DIR, csv_file)
        json_output_path = os.path.join(OUTPUT_DIR, json_file)

        recommendation_df.to_csv(csv_output_path, index=False)

        result_data = {
            "input_file": selected_file,
            "input_path": csv_path,
            "recommendations": recommendation_output,
            "total_medicines": len(recommendation_output),
            "created_at": str(datetime.now())
        }

        with open(json_output_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, indent=4)

        st.subheader("Saved Output")
        st.write("**CSV File:**", csv_output_path)
        st.write("**JSON File:**", json_output_path)

        st.download_button(
            "Download Recommendations CSV",
            data=recommendation_df.to_csv(index=False),
            file_name="medicine_recommendations.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download Recommendations JSON",
            data=json.dumps(result_data, indent=4),
            file_name="medicine_recommendations.json",
            mime="application/json"
        )

        st.info("This output is ready for the Interactive Dashboard.")

        st.warning(
            "Medical Disclaimer: These recommendations are for internship project demonstration only. "
            "Do not replace prescribed medicines without doctor consultation."
        )
