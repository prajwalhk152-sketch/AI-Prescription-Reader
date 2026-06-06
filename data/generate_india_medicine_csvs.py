import csv
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent
MEDICINE_ROWS = 50000

COMPANIES = [
    "Sun Pharma", "Cipla", "Dr Reddy's", "Lupin", "Aurobindo Pharma",
    "Torrent Pharma", "Alkem", "Zydus Lifesciences", "Mankind Pharma",
    "Glenmark", "Intas", "Alembic", "Abbott India", "Pfizer India",
    "GlaxoSmithKline", "Sanofi India", "Bayer", "Novartis India",
    "MSD India", "USV", "Micro Labs", "Aristo", "Ipca", "Wockhardt",
    "Cadila Pharma", "Emcure", "Hetero", "Biocon", "FDC", "Indoco",
    "Ajanta Pharma", "Eris Lifesciences", "JB Pharma", "Blue Cross",
    "Unichem", "RPG Life Sciences", "Serum Institute", "Panacea Biotec",
    "Troikaa", "Medley Pharma",
]

FORMS = ["Tablet", "Capsule", "Syrup", "Injection", "Oral Suspension", "Cream"]
STRENGTHS = ["50 mg", "100 mg", "125 mg", "250 mg", "500 mg", "650 mg", "1 g"]

MEDICINES = [
    ("Paracetamol", "Fever / Pain Relief", "Used to reduce fever and relieve mild to moderate pain."),
    ("Ibuprofen", "Pain Relief", "Used to reduce pain, swelling, and inflammation."),
    ("Aspirin", "Pain Relief", "Used for pain relief and sometimes for antiplatelet therapy under medical advice."),
    ("Diclofenac", "Pain Relief", "Used to reduce pain and inflammation when prescribed."),
    ("Aceclofenac", "Pain Relief", "Used for painful inflammatory conditions when prescribed."),
    ("Mefenamic Acid", "Pain Relief", "Used for pain relief including menstrual pain when prescribed."),
    ("Naproxen", "Pain Relief", "Used to reduce pain and inflammation."),
    ("Amoxicillin", "Antibiotic", "Antibiotic used for susceptible bacterial infections."),
    ("Amoxicillin Clavulanate", "Antibiotic", "Antibiotic combination used for susceptible bacterial infections."),
    ("Azithromycin", "Antibiotic", "Antibiotic used for susceptible respiratory, throat, and skin infections."),
    ("Cefixime", "Antibiotic", "Antibiotic used for susceptible bacterial infections."),
    ("Cefpodoxime", "Antibiotic", "Antibiotic used for susceptible bacterial infections."),
    ("Cefuroxime", "Antibiotic", "Antibiotic used for susceptible bacterial infections."),
    ("Ceftriaxone", "Antibiotic", "Injectable antibiotic used for serious susceptible infections."),
    ("Ciprofloxacin", "Antibiotic", "Antibiotic used for specific susceptible bacterial infections."),
    ("Ofloxacin", "Antibiotic", "Antibiotic used for specific susceptible bacterial infections."),
    ("Levofloxacin", "Antibiotic", "Antibiotic used for specific susceptible bacterial infections."),
    ("Doxycycline", "Antibiotic", "Antibiotic used for susceptible infections including acne and respiratory infections."),
    ("Metronidazole", "Antibiotic", "Used for anaerobic bacterial and protozoal infections when prescribed."),
    ("Tinidazole", "Antiparasitic", "Used for selected protozoal and anaerobic infections."),
    ("Albendazole", "Antiparasitic", "Used to treat worm infections when prescribed."),
    ("Ivermectin", "Antiparasitic", "Used for selected parasitic infections when prescribed."),
    ("Fluconazole", "Antifungal", "Used for susceptible fungal infections."),
    ("Itraconazole", "Antifungal", "Used for susceptible fungal infections."),
    ("Terbinafine", "Antifungal", "Used for susceptible fungal skin and nail infections."),
    ("Clotrimazole", "Antifungal", "Used for local fungal infections."),
    ("Ketoconazole", "Antifungal", "Used for susceptible fungal infections, commonly topical."),
    ("Acyclovir", "Antiviral", "Used for herpes virus infections when prescribed."),
    ("Oseltamivir", "Antiviral", "Used for influenza when clinically appropriate."),
    ("Metformin", "Diabetes Control", "Used to control blood sugar in type 2 diabetes."),
    ("Glimepiride", "Diabetes Control", "Used to lower blood sugar in type 2 diabetes."),
    ("Gliclazide", "Diabetes Control", "Used to lower blood sugar in type 2 diabetes."),
    ("Sitagliptin", "Diabetes Control", "Used to help control blood sugar in type 2 diabetes."),
    ("Vildagliptin", "Diabetes Control", "Used to help control blood sugar in type 2 diabetes."),
    ("Linagliptin", "Diabetes Control", "Used to help control blood sugar in type 2 diabetes."),
    ("Teneligliptin", "Diabetes Control", "Used to help control blood sugar in type 2 diabetes."),
    ("Dapagliflozin", "Diabetes Control", "Used to help control blood sugar in type 2 diabetes."),
    ("Empagliflozin", "Diabetes Control", "Used to help control blood sugar in type 2 diabetes."),
    ("Insulin Glargine", "Diabetes Control", "Long-acting insulin used for diabetes management."),
    ("Amlodipine", "Blood Pressure Control", "Used to control high blood pressure and angina."),
    ("Losartan", "Blood Pressure Control", "Used to control high blood pressure and protect kidneys in selected patients."),
    ("Telmisartan", "Blood Pressure Control", "Used to control high blood pressure."),
    ("Olmesartan", "Blood Pressure Control", "Used to control high blood pressure."),
    ("Ramipril", "Blood Pressure Control", "Used to control high blood pressure and support heart protection."),
    ("Enalapril", "Blood Pressure Control", "Used to control high blood pressure and heart failure."),
    ("Atenolol", "Blood Pressure Control", "Used for blood pressure and heart rate control."),
    ("Metoprolol", "Blood Pressure Control", "Used for blood pressure and heart rate control."),
    ("Propranolol", "Blood Pressure Control", "Used for heart rate control, migraine prevention, and other indications."),
    ("Nebivolol", "Blood Pressure Control", "Used to control high blood pressure."),
    ("Hydrochlorothiazide", "Blood Pressure Control", "Diuretic used to control blood pressure."),
    ("Furosemide", "Diuretic", "Used to reduce fluid overload when prescribed."),
    ("Spironolactone", "Diuretic", "Used for fluid control and selected heart or hormone conditions."),
    ("Atorvastatin", "Cholesterol Control", "Used to reduce cholesterol and cardiovascular risk."),
    ("Rosuvastatin", "Cholesterol Control", "Used to reduce cholesterol and cardiovascular risk."),
    ("Simvastatin", "Cholesterol Control", "Used to reduce cholesterol."),
    ("Fenofibrate", "Cholesterol Control", "Used to reduce triglycerides and support lipid control."),
    ("Clopidogrel", "Blood Thinner", "Used to reduce clotting risk under medical supervision."),
    ("Warfarin", "Blood Thinner", "Used as an anticoagulant with monitoring."),
    ("Rivaroxaban", "Blood Thinner", "Used as an anticoagulant for selected clotting risks."),
    ("Apixaban", "Blood Thinner", "Used as an anticoagulant for selected clotting risks."),
    ("Pantoprazole", "Acidity Relief", "Used to reduce stomach acid, acidity, and reflux symptoms."),
    ("Omeprazole", "Acidity Relief", "Used to reduce stomach acid and reflux symptoms."),
    ("Rabeprazole", "Acidity Relief", "Used to reduce stomach acid and reflux symptoms."),
    ("Esomeprazole", "Acidity Relief", "Used to reduce stomach acid and reflux symptoms."),
    ("Famotidine", "Acidity Relief", "Used to reduce stomach acid."),
    ("Domperidone", "Gastric Relief", "Used for nausea and gastric motility symptoms when prescribed."),
    ("Ondansetron", "Antiemetic", "Used to prevent or treat nausea and vomiting."),
    ("Dicyclomine", "GI Disorder", "Used for abdominal cramps and spasms when prescribed."),
    ("Loperamide", "Antidiarrheal", "Used for diarrhea symptom control when appropriate."),
    ("Lactulose", "Laxative", "Used to treat constipation and selected liver-related conditions."),
    ("Bisacodyl", "Laxative", "Used for constipation relief."),
    ("Cetirizine", "Allergy Relief", "Used to reduce allergy symptoms such as sneezing and itching."),
    ("Levocetirizine", "Allergy Relief", "Used to reduce allergy symptoms."),
    ("Fexofenadine", "Allergy Relief", "Used to reduce allergy symptoms with less drowsiness in many patients."),
    ("Loratadine", "Allergy Relief", "Used to reduce allergy symptoms."),
    ("Montelukast", "Asthma Relief", "Used for asthma and allergy control when prescribed."),
    ("Salbutamol", "Asthma Relief", "Used to relieve airway narrowing and wheezing."),
    ("Budesonide", "Asthma Relief", "Steroid used to control airway inflammation."),
    ("Formoterol", "Asthma Relief", "Long-acting bronchodilator used in inhaler combinations."),
    ("Tiotropium", "Respiratory", "Used for COPD or selected airway conditions."),
    ("Ambroxol", "Cough Relief", "Used as a mucolytic to help clear mucus."),
    ("Guaifenesin", "Cough Relief", "Used to loosen mucus in cough."),
    ("Dextromethorphan", "Cough Relief", "Used to suppress dry cough when appropriate."),
    ("Levothyroxine", "Thyroid Treatment", "Used to replace thyroid hormone in hypothyroidism."),
    ("Carbimazole", "Thyroid Treatment", "Used for hyperthyroidism under specialist supervision."),
    ("Ferrous Sulfate", "Iron Supplement", "Used to treat or prevent iron deficiency."),
    ("Folic Acid", "Vitamin Supplement", "Used to prevent or treat folate deficiency."),
    ("Vitamin D3", "Vitamin Supplement", "Used to support vitamin D levels and bone health."),
    ("Calcium Carbonate", "Calcium Supplement", "Used to support calcium intake and bone health."),
    ("Methylcobalamin", "Vitamin Supplement", "Used to support vitamin B12 levels and nerve health."),
    ("Ascorbic Acid", "Vitamin C Supplement", "Used to support vitamin C levels."),
    ("Zinc Sulfate", "Zinc Supplement", "Used to support zinc levels."),
    ("Mupirocin", "Skin Treatment", "Topical antibiotic used for selected skin infections."),
    ("Povidone Iodine", "Antibacterial", "Used as an antiseptic for skin and wound care."),
    ("Betamethasone", "Skin Treatment", "Topical or systemic steroid used for inflammation when prescribed."),
    ("Hydrocortisone", "Skin Treatment", "Steroid used for inflammation and allergic skin conditions."),
    ("Permethrin", "Skin Treatment", "Used for scabies and lice when prescribed."),
    ("Tretinoin", "Skin Treatment", "Used for acne and selected skin conditions."),
    ("Adapalene", "Skin Treatment", "Used for acne treatment."),
    ("Finasteride", "Prostate Disorder", "Used for prostate enlargement or hair loss in selected patients."),
    ("Tamsulosin", "Prostate Disorder", "Used to improve urination in prostate enlargement."),
    ("Silodosin", "Prostate Disorder", "Used to improve urination in prostate enlargement."),
    ("Alprazolam", "Anxiety Relief", "Used for anxiety symptoms only under close medical supervision."),
    ("Clonazepam", "Anxiety Relief", "Used for anxiety, seizures, or related conditions under supervision."),
    ("Escitalopram", "Mental Health", "Used for depression and anxiety disorders when prescribed."),
    ("Sertraline", "Mental Health", "Used for depression and anxiety disorders when prescribed."),
    ("Fluoxetine", "Mental Health", "Used for depression and anxiety disorders when prescribed."),
    ("Amitriptyline", "Mental Health", "Used for depression, neuropathic pain, or migraine prevention when prescribed."),
    ("Gabapentin", "Neuropathic Pain", "Used for nerve pain and selected seizure conditions."),
    ("Pregabalin", "Neuropathic Pain", "Used for nerve pain and selected seizure conditions."),
    ("Levetiracetam", "Antiepileptic", "Used to control seizures."),
    ("Sodium Valproate", "Antiepileptic", "Used to control seizures and selected mood conditions."),
]

COMMON_BRANDS = [
    ("Crocin", "Paracetamol", "Fever / Pain Relief", "GSK Consumer Healthcare"),
    ("Calpol", "Paracetamol", "Fever / Pain Relief", "GSK Consumer Healthcare"),
    ("Dolo 650", "Paracetamol", "Fever / Pain Relief", "Micro Labs"),
    ("Combiflam", "Ibuprofen Paracetamol", "Pain Relief", "Sanofi India"),
    ("Brufen", "Ibuprofen", "Pain Relief", "Abbott India"),
    ("Voveran", "Diclofenac", "Pain Relief", "Novartis India"),
    ("Zerodol", "Aceclofenac", "Pain Relief", "Ipca"),
    ("Disprin", "Aspirin", "Pain Relief", "Reckitt"),
    ("Azee", "Azithromycin", "Antibiotic", "Cipla"),
    ("Azithral", "Azithromycin", "Antibiotic", "Alembic"),
    ("Taxim-O", "Cefixime", "Antibiotic", "Alkem"),
    ("Cifran", "Ciprofloxacin", "Antibiotic", "Sun Pharma"),
    ("Augmentin", "Amoxicillin Clavulanate", "Antibiotic", "GSK"),
    ("Moxikind-CV", "Amoxicillin Clavulanate", "Antibiotic", "Mankind Pharma"),
    ("Glycomet", "Metformin", "Diabetes Control", "USV"),
    ("Telma", "Telmisartan", "Blood Pressure Control", "Glenmark"),
    ("Amlong", "Amlodipine", "Blood Pressure Control", "Micro Labs"),
    ("Stamlo", "Amlodipine", "Blood Pressure Control", "Dr Reddy's"),
    ("Atorlip", "Atorvastatin", "Cholesterol Control", "Cipla"),
    ("Rozavel", "Rosuvastatin", "Cholesterol Control", "Sun Pharma"),
    ("Ecosprin", "Aspirin", "Blood Thinner", "USV"),
    ("Pantocid", "Pantoprazole", "Acidity Relief", "Sun Pharma"),
    ("Omez", "Omeprazole", "Acidity Relief", "Dr Reddy's"),
    ("Razo", "Rabeprazole", "Acidity Relief", "Dr Reddy's"),
    ("Digene", "Antacid", "Acidity Relief", "Abbott India"),
    ("Allegra", "Fexofenadine", "Allergy Relief", "Sanofi India"),
    ("Montek", "Montelukast", "Asthma Relief", "Sun Pharma"),
    ("Asthalin", "Salbutamol", "Asthma Relief", "Cipla"),
    ("Eltroxin", "Levothyroxine", "Thyroid Treatment", "GSK"),
    ("Shelcal", "Calcium Vitamin D3", "Calcium Supplement", "Torrent Pharma"),
    ("Neurobion", "Vitamin B Complex", "Vitamin Supplement", "Merck"),
    ("Supradyn", "Multivitamin", "Vitamin Supplement", "Bayer"),
    ("Limcee", "Ascorbic Acid", "Vitamin C Supplement", "Abbott India"),
    ("Zentel", "Albendazole", "Antiparasitic", "GSK"),
    ("Candid", "Clotrimazole", "Antifungal", "Glenmark"),
    ("Betadine", "Povidone Iodine", "Antibacterial", "Win Medicare"),
    ("Volini", "Diclofenac Topical", "Pain Relief", "Sun Pharma"),
    ("Moov", "Topical Analgesic", "Pain Relief", "Reckitt"),
    ("Sinarest", "Cold Combination", "Cold Relief", "Centaur Pharma"),
]


def slug(text):
    return "".join(part[0] for part in text.replace("'", "").split() if part).upper()[:4]


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_medicines():
    rows = []
    seen = set()

    for brand, generic, category, company in COMMON_BRANDS:
        key = brand.lower()
        if key not in seen:
            seen.add(key)
            rows.append({
                "medicine_name": brand,
                "generic_name": generic,
                "category": category,
                "company": company,
                "dosage_form": "",
                "strength": "",
                "country_focus": "India",
                "data_note": "Common Indian brand or commonly prescribed medicine name.",
            })

    for generic, category, benefit in MEDICINES:
        for company in COMPANIES:
            for form in FORMS:
                for strength in STRENGTHS:
                    if len(rows) >= MEDICINE_ROWS:
                        return rows
                    name = f"{generic} {strength} {form} {slug(company)}"
                    key = name.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append({
                        "medicine_name": name,
                        "generic_name": generic,
                        "category": category,
                        "company": company,
                        "dosage_form": form,
                        "strength": strength,
                        "country_focus": "India",
                        "data_note": "Generated generic/company SKU-style entry from real active ingredient and real manufacturer name; verify before clinical use.",
                    })
    return rows


def build_benefits(medicine_rows):
    benefit_by_generic = {generic: benefit for generic, _, benefit in MEDICINES}
    return [
        {
            "medicine_name": row["medicine_name"],
            "generic_name": row["generic_name"],
            "category": row["category"],
            "company": row["company"],
            "benefit_explanation": benefit_by_generic.get(
                row["generic_name"],
                f"Used for {row['category'].lower()} when prescribed by a qualified clinician.",
            ),
            "patient_note": "Use only as prescribed. This educational dataset is not a substitute for medical advice.",
        }
        for row in medicine_rows
    ]


def build_interactions():
    pairs = [
        ("Warfarin", "Aspirin", 95, "High", "May increase bleeding risk. Doctor review is required."),
        ("Warfarin", "Ibuprofen", 90, "High", "May increase serious bleeding risk."),
        ("Warfarin", "Diclofenac", 90, "High", "May increase bleeding risk, including stomach bleeding."),
        ("Aspirin", "Ibuprofen", 75, "Moderate", "May increase stomach bleeding risk and reduce aspirin heart-protection effect."),
        ("Aspirin", "Clopidogrel", 80, "High", "May increase bleeding risk. Use only under doctor supervision."),
        ("Clopidogrel", "Omeprazole", 65, "Moderate", "May reduce clopidogrel effect in some patients."),
        ("Clopidogrel", "Pantoprazole", 35, "Low", "Usually preferred over some alternatives, but follow doctor advice."),
        ("Metformin", "Alcohol", 85, "High", "May increase risk of lactic acidosis and low blood sugar."),
        ("Insulin Glargine", "Glimepiride", 70, "Moderate", "May increase low blood sugar risk. Monitoring is important."),
        ("Metformin", "Ibuprofen", 45, "Low", "Kidney function should be considered, especially in dehydration or kidney disease."),
        ("Losartan", "Ibuprofen", 65, "Moderate", "May reduce blood pressure effect and affect kidney function."),
        ("Telmisartan", "Ibuprofen", 65, "Moderate", "May reduce blood pressure effect and affect kidney function."),
        ("Ramipril", "Spironolactone", 80, "High", "May increase potassium levels. Doctor monitoring is required."),
        ("Losartan", "Spironolactone", 78, "High", "May increase potassium levels. Doctor monitoring is required."),
        ("Amlodipine", "Simvastatin", 70, "Moderate", "May increase statin side effects. Doctor monitoring may be needed."),
        ("Clarithromycin", "Atorvastatin", 88, "High", "May increase statin toxicity risk. Doctor review is recommended."),
        ("Azithromycin", "Warfarin", 80, "High", "May increase blood thinning effect and bleeding risk."),
        ("Propranolol", "Salbutamol", 75, "Moderate", "Beta blockers may reduce bronchodilator effect."),
        ("Cetirizine", "Alcohol", 60, "Moderate", "May increase drowsiness and reduce alertness."),
        ("Levocetirizine", "Alcohol", 60, "Moderate", "May increase drowsiness and reduce alertness."),
        ("Fluconazole", "Warfarin", 88, "High", "May increase warfarin effect and bleeding risk."),
        ("Fluconazole", "Atorvastatin", 70, "Moderate", "May increase statin side-effect risk."),
        ("Doxycycline", "Calcium Carbonate", 60, "Moderate", "Calcium may reduce doxycycline absorption if taken together."),
        ("Levothyroxine", "Calcium Carbonate", 65, "Moderate", "Calcium may reduce levothyroxine absorption if taken together."),
        ("Levothyroxine", "Ferrous Sulfate", 65, "Moderate", "Iron may reduce levothyroxine absorption if taken together."),
        ("Ciprofloxacin", "Calcium Carbonate", 65, "Moderate", "Calcium may reduce antibiotic absorption if taken together."),
        ("Ciprofloxacin", "Iron Supplement", 65, "Moderate", "Iron may reduce antibiotic absorption if taken together."),
        ("Ondansetron", "Azithromycin", 60, "Moderate", "May increase heart rhythm risk in susceptible patients."),
        ("Escitalopram", "Tramadol", 80, "High", "May increase serotonin syndrome or seizure risk."),
        ("Sertraline", "Aspirin", 60, "Moderate", "May increase bleeding tendency in some patients."),
    ]
    return [
        {
            "medicine_1": med1,
            "medicine_2": med2,
            "risk_percent": risk,
            "risk_level": level,
            "warning": warning,
            "patient_note": "Interaction screening is educational and must be verified by a clinician.",
        }
        for med1, med2, risk, level, warning in pairs
    ]


def main():
    medicine_rows = build_medicines()
    if len(medicine_rows) < MEDICINE_ROWS:
        raise RuntimeError(f"Only generated {len(medicine_rows)} medicine rows.")

    write_csv(
        DATA_DIR / "medicine_database.csv",
        ["medicine_name", "generic_name", "category", "company", "dosage_form", "strength", "country_focus", "data_note"],
        medicine_rows,
    )
    write_csv(
        DATA_DIR / "medicine_benefits_database.csv",
        ["medicine_name", "generic_name", "category", "company", "benefit_explanation", "patient_note"],
        build_benefits(medicine_rows),
    )
    write_csv(
        DATA_DIR / "medicine_interactions_database.csv",
        ["medicine_1", "medicine_2", "risk_percent", "risk_level", "warning", "patient_note"],
        build_interactions(),
    )
    print(f"Generated {len(medicine_rows)} medicines, {len(medicine_rows)} benefits, and {len(build_interactions())} interactions.")


if __name__ == "__main__":
    main()
