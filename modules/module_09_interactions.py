import os
import json
import csv
import pandas as pd
from itertools import combinations
from datetime import datetime
from pathlib import Path


class _StreamlitFallback:
    def cache_data(self, **_kwargs):
        def decorator(func):
            return func
        return decorator

    def __getattr__(self, name):
        raise RuntimeError(
            f"Streamlit UI function st.{name} is unavailable. "
            "Run the React/FastAPI app instead."
        )


st = _StreamlitFallback()

INPUT_DIR = "outputs/module_06_medicines"
OUTPUT_DIR = "outputs/module_09_interactions"
DATA_DIR = Path(__file__).parent.parent / "data"
MEDICINE_INTERACTIONS_DATABASE_PATH = DATA_DIR / "medicine_interactions_database.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)

INTERACTION_DATABASE = {
    ("Warfarin", "Aspirin"): {
        "risk": 95,
        "level": "High",
        "warning": "May increase bleeding risk. Immediate doctor consultation recommended."
    },
    ("Aspirin", "Ibuprofen"): {
        "risk": 75,
        "level": "Moderate",
        "warning": "May increase stomach bleeding risk and reduce heart protection effect."
    },
    ("Paracetamol", "Ibuprofen"): {
        "risk": 40,
        "level": "Low",
        "warning": "Usually safe when prescribed, but avoid overdose and follow doctor instructions."
    },
    ("Warfarin", "Ibuprofen"): {
        "risk": 90,
        "level": "High",
        "warning": "May increase serious bleeding risk."
    },
    ("Metformin", "Alcohol"): {
        "risk": 85,
        "level": "High",
        "warning": "May increase risk of lactic acidosis and low blood sugar."
    },
    ("Azithromycin", "Warfarin"): {
        "risk": 80,
        "level": "High",
        "warning": "May increase blood thinning effect and bleeding risk."
    },
    ("Amlodipine", "Simvastatin"): {
        "risk": 70,
        "level": "Moderate",
        "warning": "May increase statin side effects. Doctor monitoring required."
    },
    ("Losartan", "Ibuprofen"): {
        "risk": 65,
        "level": "Moderate",
        "warning": "May reduce blood pressure medicine effect and affect kidney function."
    },
    ("Aspirin", "Clopidogrel"): {
        "risk": 80,
        "level": "High",
        "warning": "May increase bleeding risk. Use only under doctor supervision."
    },
    ("Ecosprin", "Clopidogrel"): {
        "risk": 80,
        "level": "High",
        "warning": "May increase bleeding risk. Doctor supervision required."
    },
    ("Ibuprofen", "Clopidogrel"): {
        "risk": 82,
        "level": "High",
        "warning": "May increase bleeding risk, especially stomach bleeding. Use only with doctor supervision."
    },
    ("Aspirin", "Warfarin"): {
        "risk": 95,
        "level": "High",
        "warning": "May increase bleeding risk. Immediate doctor consultation recommended."
    },
    ("Ibuprofen", "Warfarin"): {
        "risk": 90,
        "level": "High",
        "warning": "May increase serious bleeding risk."
    },
    ("Paracetamol", "Warfarin"): {
        "risk": 60,
        "level": "Moderate",
        "warning": "Repeated or high-dose use may affect blood thinning control. Follow doctor advice."
    },
    ("Azithromycin", "Atorvastatin"): {
        "risk": 55,
        "level": "Moderate",
        "warning": "May increase statin side-effect risk in some patients. Report muscle pain or weakness."
    },
    ("Clarithromycin", "Atorvastatin"): {
        "risk": 88,
        "level": "High",
        "warning": "May strongly increase statin side effects. Doctor review is recommended."
    },
    ("Clarithromycin", "Simvastatin"): {
        "risk": 92,
        "level": "High",
        "warning": "May strongly increase simvastatin toxicity risk. Avoid unless specifically supervised."
    },
    ("Amlodipine", "Atorvastatin"): {
        "risk": 45,
        "level": "Low",
        "warning": "Usually manageable, but monitor for statin side effects if prescribed together."
    },
    ("Amlodipine", "Simvastatin"): {
        "risk": 70,
        "level": "Moderate",
        "warning": "May increase statin side effects. Doctor monitoring required."
    },
    ("Metformin", "Ibuprofen"): {
        "risk": 45,
        "level": "Low",
        "warning": "Kidney function should be considered, especially in dehydration or kidney disease."
    },
    ("Metformin", "Aspirin"): {
        "risk": 35,
        "level": "Low",
        "warning": "Usually safe when prescribed, but monitor blood sugar and follow medical advice."
    },
    ("Losartan", "Aspirin"): {
        "risk": 50,
        "level": "Moderate",
        "warning": "Regular NSAID use may reduce blood pressure control or affect kidneys."
    },
    ("Amlodipine", "Losartan"): {
        "risk": 35,
        "level": "Low",
        "warning": "May lower blood pressure more when used together. Monitor dizziness or weakness."
    },
    ("Cetirizine", "Alcohol"): {
        "risk": 60,
        "level": "Moderate",
        "warning": "May increase drowsiness and reduce alertness."
    },
    ("Levocetirizine", "Alcohol"): {
        "risk": 60,
        "level": "Moderate",
        "warning": "May increase drowsiness and reduce alertness."
    },
    ("Pantoprazole", "Clopidogrel"): {
        "risk": 35,
        "level": "Low",
        "warning": "Usually preferred over some alternatives, but follow doctor advice."
    },
    ("Omeprazole", "Clopidogrel"): {
        "risk": 65,
        "level": "Moderate",
        "warning": "May reduce clopidogrel effect in some patients. Doctor review is recommended."
    },
    ("Insulin", "Metformin"): {
        "risk": 55,
        "level": "Moderate",
        "warning": "May increase low blood sugar risk. Glucose monitoring is important."
    },
    ("Glimepiride", "Metformin"): {
        "risk": 55,
        "level": "Moderate",
        "warning": "May increase low blood sugar risk. Use with monitoring as prescribed."
    },
    ("Salbutamol", "Propranolol"): {
        "risk": 75,
        "level": "Moderate",
        "warning": "Beta blockers may reduce bronchodilator effect. Doctor review is recommended."
    },
    ("Montelukast", "Cetirizine"): {
        "risk": 20,
        "level": "Low",
        "warning": "Often prescribed together for allergy/asthma control, but follow the prescription."
    }
}


def normalize_database_name(name):
    return str(name).strip().title()


def load_external_interaction_database():
    if not MEDICINE_INTERACTIONS_DATABASE_PATH.exists():
        return 0

    loaded_count = 0
    with MEDICINE_INTERACTIONS_DATABASE_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            medicine_1 = normalize_database_name(row.get("medicine_1", ""))
            medicine_2 = normalize_database_name(row.get("medicine_2", ""))
            if not medicine_1 or not medicine_2 or medicine_1 == medicine_2:
                continue

            try:
                risk = int(float(row.get("risk_percent", 0)))
            except (TypeError, ValueError):
                risk = 0

            level = str(row.get("risk_level", "No Known Risk")).strip() or "No Known Risk"
            warning = str(row.get("warning", "")).strip()
            if not warning:
                warning = "Potential interaction listed in the local CSV database. Please confirm with a doctor."

            pair = (medicine_1, medicine_2)
            reverse_pair = (medicine_2, medicine_1)
            if pair in INTERACTION_DATABASE or reverse_pair in INTERACTION_DATABASE:
                continue

            INTERACTION_DATABASE[pair] = {
                "risk": max(0, min(100, risk)),
                "level": level,
                "warning": warning,
            }
            loaded_count += 1

    return loaded_count


EXTERNAL_INTERACTION_COUNT = load_external_interaction_database()


@st.cache_data(show_spinner=False)
def get_medicine_files():
    if not os.path.exists(INPUT_DIR):
        return []

    return sorted(
        [file for file in os.listdir(INPUT_DIR) if file.endswith(".csv")],
        reverse=True
    )


def normalize_name(name):
    return normalize_database_name(name)


def check_interaction(med1, med2):
    pair1 = (med1, med2)
    pair2 = (med2, med1)

    if pair1 in INTERACTION_DATABASE:
        return INTERACTION_DATABASE[pair1]

    if pair2 in INTERACTION_DATABASE:
        return INTERACTION_DATABASE[pair2]

    return {
        "risk": 0,
        "level": "No Known Risk",
        "warning": "No major known interaction found in the local database."
    }


def risk_badge(level):
    if level == "High":
        return "High Risk"
    elif level == "Moderate":
        return "Moderate Risk"
    elif level == "Low":
        return "Low Risk"
    else:
        return "No Known Risk"


def show_module_09_interactions():
    st.title("Drug Interaction Warning System")

    st.write(
        "This step checks detected medicines for possible dangerous drug interactions."
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

    medicines = [normalize_name(med) for med in df["medicine_name"].dropna().tolist()]
    medicines = list(dict.fromkeys(medicines))

    st.write("**Medicines selected for interaction checking:**", medicines)

    if st.button("Check Drug Interactions"):
        interaction_results = []

        if len(medicines) < 2:
            st.warning("At least two medicines are required to check interactions.")
            return

        for med1, med2 in combinations(medicines, 2):
            interaction = check_interaction(med1, med2)

            interaction_results.append({
                "medicine_1": med1,
                "medicine_2": med2,
                "risk_percent": interaction["risk"],
                "risk_level": interaction["level"],
                "warning": interaction["warning"]
            })

        result_df = pd.DataFrame(interaction_results)

        high_risk_count = len(result_df[result_df["risk_level"] == "High"])
        moderate_risk_count = len(result_df[result_df["risk_level"] == "Moderate"])
        low_risk_count = len(result_df[result_df["risk_level"] == "Low"])

        st.success("Drug interaction checking completed.")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Pairs Checked", len(result_df))

        with col2:
            st.metric("High Risk", high_risk_count)

        with col3:
            st.metric("Moderate Risk", moderate_risk_count)

        with col4:
            st.metric("Low Risk", low_risk_count)

        st.subheader("Drug Interaction Output")
        st.dataframe(result_df, use_container_width=True)

        st.subheader("Interaction Warning Cards")

        for item in interaction_results:
            level = item["risk_level"]

            if level == "High":
                st.error(
                    f"{risk_badge(level)}: {item['medicine_1']} + {item['medicine_2']} "
                    f"({item['risk_percent']}%)\n\n{item['warning']}"
                )
            elif level == "Moderate":
                st.warning(
                    f"{risk_badge(level)}: {item['medicine_1']} + {item['medicine_2']} "
                    f"({item['risk_percent']}%)\n\n{item['warning']}"
                )
            elif level == "Low":
                st.info(
                    f"{risk_badge(level)}: {item['medicine_1']} + {item['medicine_2']} "
                    f"({item['risk_percent']}%)\n\n{item['warning']}"
                )
            else:
                st.success(
                    f"{risk_badge(level)}: {item['medicine_1']} + {item['medicine_2']}\n\n"
                    f"{item['warning']}"
                )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_file = f"drug_interactions_{timestamp}.csv"
        json_file = f"drug_interactions_{timestamp}.json"

        csv_output_path = os.path.join(OUTPUT_DIR, csv_file)
        json_output_path = os.path.join(OUTPUT_DIR, json_file)

        result_df.to_csv(csv_output_path, index=False)

        result_data = {
            "input_file": selected_file,
            "input_path": csv_path,
            "medicines_checked": medicines,
            "total_pairs_checked": len(interaction_results),
            "high_risk_count": high_risk_count,
            "moderate_risk_count": moderate_risk_count,
            "low_risk_count": low_risk_count,
            "interaction_results": interaction_results,
            "created_at": str(datetime.now())
        }

        with open(json_output_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, indent=4)

        st.subheader("Saved Output")
        st.write("**CSV File:**", csv_output_path)
        st.write("**JSON File:**", json_output_path)

        st.download_button(
            "Download Interaction CSV",
            data=result_df.to_csv(index=False),
            file_name="drug_interactions.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download Interaction JSON",
            data=json.dumps(result_data, indent=4),
            file_name="drug_interactions.json",
            mime="application/json"
        )

        st.info("This output is ready for Medicine Recommendation Engine.")

        st.warning(
            "Medical Disclaimer: This system is for educational/internship project use only. "
            "Patients must always follow a qualified doctor's advice."
        )
