import os
import json
import csv
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from functools import lru_cache
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
OUTPUT_DIR = "outputs/module_08_benefits"
DATA_DIR = Path(__file__).parent.parent / "data"
MEDICINE_BENEFITS_DATABASE_PATH = DATA_DIR / "medicine_benefits_database.csv"

os.makedirs(OUTPUT_DIR, exist_ok=True)
load_dotenv()

BENEFITS_DATABASE = {
    "Paracetamol": "Used to reduce fever and relieve mild to moderate pain such as headache and body pain.",
    "Crocin": "Used to reduce fever and relieve pain. It commonly contains paracetamol.",
    "Calpol": "Used for fever and pain relief, especially in children when prescribed by a doctor.",
    "Dolo": "Used to reduce fever and relieve pain. It commonly contains paracetamol.",
    "Ibuprofen": "Used to reduce pain, swelling, and inflammation.",
    "Aspirin": "Used for pain relief and sometimes to reduce blood clotting risk under medical advice.",
    "Amoxicillin": "An antibiotic used to treat bacterial infections such as throat, ear, and respiratory infections.",
    "Azithromycin": "An antibiotic used to treat bacterial infections such as throat, chest, and skin infections.",
    "Cefixime": "An antibiotic used to treat bacterial infections.",
    "Cetirizine": "Used to reduce allergy symptoms such as sneezing, runny nose, and itching.",
    "Levocetirizine": "Used to treat allergy symptoms such as sneezing, itching, and watery eyes.",
    "Metformin": "Used to control blood sugar levels in patients with type 2 diabetes.",
    "Amlodipine": "Used to control high blood pressure and improve blood flow.",
    "Losartan": "Used to control high blood pressure and protect the heart and kidneys.",
    "Atorvastatin": "Used to reduce cholesterol and lower the risk of heart disease.",
    "Rosuvastatin": "Used to reduce cholesterol levels and support heart health.",
    "Pantoprazole": "Used to reduce stomach acid and treat acidity, heartburn, and gastric problems.",
    "Omeprazole": "Used to reduce stomach acid and treat acidity and acid reflux.",
    "Rabeprazole": "Used to reduce acidity and stomach acid-related problems.",
    "Warfarin": "Used as a blood thinner to prevent harmful blood clots.",
    "Clopidogrel": "Used to reduce the risk of blood clots and support heart health.",
    "Ecosprin": "Used as a blood thinner under doctor supervision.",
    "Salbutamol": "Used to relieve breathing problems caused by asthma or airway narrowing.",
    "Montelukast": "Used to help control asthma and allergy symptoms.",
    "Thyroxine": "Used to treat low thyroid hormone levels.",
    "Levothyroxine": "Used to treat hypothyroidism by replacing thyroid hormone.",
    "Becosules": "Vitamin supplement used to support general health and vitamin deficiency.",
    "Supradyn": "Multivitamin supplement used to support energy and general wellness.",
    "Neurobion": "Vitamin B supplement used for nerve health.",
    "Limcee": "Vitamin C supplement used to support immunity.",
    "Shelcal": "Calcium supplement used for bone health.",
    "Digene": "Used to relieve acidity, gas, and indigestion.",
    "Gelusil": "Used to relieve acidity and gas."
}


def normalize_medicine_key(medicine_name):
    return " ".join(str(medicine_name).strip().lower().split())


@lru_cache(maxsize=1)
def load_medicine_benefits_database():
    if not MEDICINE_BENEFITS_DATABASE_PATH.exists():
        return {}

    benefits = {}
    with MEDICINE_BENEFITS_DATABASE_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = normalize_medicine_key(row.get("medicine_name", ""))
            if key:
                benefits[key] = row

    return benefits


def get_database_benefit(medicine_name):
    database_match = load_medicine_benefits_database().get(
        normalize_medicine_key(medicine_name)
    )
    if not database_match:
        return ""

    return database_match.get("benefit_explanation", "").strip()


@st.cache_data(show_spinner=False)
def get_medicine_files():
    if not os.path.exists(INPUT_DIR):
        return []

    files = []
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".csv"):
            files.append(file)

    return sorted(files, reverse=True)


def generate_benefit(medicine_name, category):
    if medicine_name in BENEFITS_DATABASE:
        return BENEFITS_DATABASE[medicine_name]

    database_benefit = get_database_benefit(medicine_name)
    if database_benefit:
        return database_benefit

    return (
        f"{medicine_name} is generally used for {category.lower()}. "
        "Please follow the doctor's prescription and do not self-medicate."
    )


def generate_local_genai_explanation(medicine_name, category):
    base_benefit = generate_benefit(medicine_name, category)
    return (
        f"{medicine_name} belongs to the {category} group. {base_benefit} "
        "In simple terms, it may help manage the condition written in the prescription, "
        "but the exact reason, dose, and duration should always be confirmed with the doctor. "
        "Avoid changing the dose or replacing it with another medicine without medical advice."
    )


def generate_api_genai_explanation(medicine_name, category):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None, "OPENAI_API_KEY is not configured. Used local GenAI-style explanation."

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = (
        "Explain this medicine for a patient in 3 short, clear sentences. "
        "Avoid diagnosis, avoid dosage instructions, and include a safety reminder.\n\n"
        f"Medicine: {medicine_name}\n"
        f"Category: {category}"
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You write patient-friendly medicine explanations for a prescription reader app.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 160,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        explanation = data["choices"][0]["message"]["content"].strip()
        return explanation, f"Generated with {model}"
    except Exception as error:
        return None, f"GenAI API unavailable ({error}). Used local GenAI-style explanation."


def generate_genai_benefit(medicine_name, category, use_api):
    if use_api:
        explanation, status = generate_api_genai_explanation(medicine_name, category)
        if explanation:
            return explanation, status

        return generate_local_genai_explanation(medicine_name, category), status

    if get_database_benefit(medicine_name):
        return (
            generate_local_genai_explanation(medicine_name, category),
            "Generated from 50,000 medicine benefits database",
        )

    return generate_local_genai_explanation(medicine_name, category), "Generated locally"


def show_module_08_benefits():
    st.title("Medicine Benefits Explanation")

    st.write(
        "This step uses GenAI-style medicine explanation to describe detected medicines in simple patient-friendly language."
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

    use_api_genai = st.checkbox(
        "Use API GenAI explanations when OPENAI_API_KEY is configured",
        value=False,
        help="When disabled or unavailable, the app uses a safe local GenAI-style explanation."
    )

    if st.button("Generate Medicine Benefits"):
        benefits_output = []
        genai_status_messages = []

        for _, row in df.iterrows():
            medicine_name = str(row["medicine_name"])
            category = str(row["category"])
            explanation, genai_status = generate_genai_benefit(
                medicine_name,
                category,
                use_api_genai
            )
            genai_status_messages.append(genai_status)

            benefits_output.append({
                "medicine_name": medicine_name,
                "category": category,
                "benefit_explanation": explanation,
                "generation_method": genai_status,
                "patient_note": "Take this medicine only as prescribed by your doctor."
            })

        benefit_df = pd.DataFrame(benefits_output)

        st.success("Medicine benefits generated successfully.")
        if genai_status_messages:
            st.caption(" | ".join(sorted(set(genai_status_messages))))

        st.subheader("Medicine Benefits Output")
        st.dataframe(benefit_df, use_container_width=True)

        st.subheader("Patient-Friendly Medicine Cards")

        for item in benefits_output:
            with st.expander(item["medicine_name"]):
                st.write("**Category:**", item["category"])
                st.write("**Benefit:**", item["benefit_explanation"])
                st.caption(item["generation_method"])
                st.warning(item["patient_note"])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_file = f"medicine_benefits_{timestamp}.csv"
        json_file = f"medicine_benefits_{timestamp}.json"

        csv_output_path = os.path.join(OUTPUT_DIR, csv_file)
        json_output_path = os.path.join(OUTPUT_DIR, json_file)

        benefit_df.to_csv(csv_output_path, index=False)

        result_data = {
            "input_file": selected_file,
            "input_path": csv_path,
            "benefits": benefits_output,
            "total_medicines": len(benefits_output),
            "created_at": str(datetime.now())
        }

        with open(json_output_path, "w", encoding="utf-8") as file:
            json.dump(result_data, file, indent=4)

        st.subheader("Saved Output")
        st.write("**CSV File:**", csv_output_path)
        st.write("**JSON File:**", json_output_path)

        st.download_button(
            "Download Benefits CSV",
            data=benefit_df.to_csv(index=False),
            file_name="medicine_benefits.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download Benefits JSON",
            data=json.dumps(result_data, indent=4),
            file_name="medicine_benefits.json",
            mime="application/json"
        )

        st.info("This output is ready for Drug Interaction Warning System.")
