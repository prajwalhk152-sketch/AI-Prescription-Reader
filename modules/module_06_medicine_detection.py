import os
import json
import pandas as pd
import re
import difflib
import csv
from datetime import datetime
from collections import defaultdict
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

INPUT_DIR = "outputs/module_05_ocr"
OUTPUT_DIR = "outputs/module_06_medicines"
DATA_DIR = Path(__file__).parent.parent / "data"
EXTERNAL_MEDICINE_DATABASE_PATH = DATA_DIR / "medicine_database.csv"
FUZZY_STOPWORDS = {
    "after", "before", "daily", "dose", "food", "hour", "hours", "meal", "meals",
    "morning", "night", "noon", "tablet", "tablets", "take", "times", "water",
    "with", "without",
}
MAX_EXACT_MEDICINE_TOKENS = 12

os.makedirs(OUTPUT_DIR, exist_ok=True)

MEDICINE_DATABASE = {
    # ============ FEVER & PAIN RELIEF ============
    "paracetamol": "Fever / Pain Relief",
    "acetaminophen": "Fever / Pain Relief",
    "crocin": "Fever / Pain Relief",
    "calpol": "Fever / Pain Relief",
    "dolo": "Fever / Pain Relief",
    "ibuprofen": "Pain Relief",
    "combiflam": "Pain Relief",
    "aspirin": "Pain Relief",
    "naproxen": "Pain Relief",
    "mefenamic acid": "Pain Relief",
    "meloxicam": "Pain Relief",
    "piroxicam": "Pain Relief",
    "diclofenac": "Pain Relief",
    "indomethacin": "Pain Relief",
    "zerodol": "Pain Relief",
    "zerodol-p": "Pain Relief",
    "brufen": "Pain Relief",
    "voveran": "Pain Relief",
    "sumo": "Pain Relief",
    "spasmo proxyvon": "Pain Relief",
    "emulsopin": "Pain Relief",
    
    # ============ ANTIBIOTICS ============
    "amoxicillin": "Antibiotic",
    "amoxycillin": "Antibiotic",
    "azithromycin": "Antibiotic",
    "azee": "Antibiotic",
    "azithral": "Antibiotic",
    "cefixime": "Antibiotic",
    "taxim-o": "Antibiotic",
    "cefspan": "Antibiotic",
    "ciprofloxacin": "Antibiotic",
    "cipro": "Antibiotic",
    "cifran": "Antibiotic",
    "ciplox": "Antibiotic",
    "levofloxacin": "Antibiotic",
    "levaquin": "Antibiotic",
    "doxycycline": "Antibiotic",
    "metronidazole": "Antibiotic",
    "augmentin": "Antibiotic",
    "monocef": "Antibiotic",
    "ceftriaxone": "Antibiotic",
    "fortum": "Antibiotic",
    "cefotaxime": "Antibiotic",
    "cloxacillin": "Antibiotic",
    "erythromycin": "Antibiotic",
    "tetracycline": "Antibiotic",
    "norfloxacin": "Antibiotic",
    "ofloxacin": "Antibiotic",
    "oflotas": "Antibiotic",
    "moxifloxacin": "Antibiotic",
    "sparfloxacin": "Antibiotic",
    "trovafloxacin": "Antibiotic",
    "gatifloxacin": "Antibiotic",
    "penicillin": "Antibiotic",
    "ampicillin": "Antibiotic",
    "piperacillin": "Antibiotic",
    
    # ============ ANTIVIRAL ============
    "oseltamivir": "Antiviral",
    "tamiflu": "Antiviral",
    "acyclovir": "Antiviral",
    "zovirax": "Antiviral",
    "valacyclovir": "Antiviral",
    "famciclovir": "Antiviral",
    "ganciclovir": "Antiviral",
    "ribavirin": "Antiviral",
    "remdesivir": "Antiviral",
    
    # ============ DIABETES CONTROL ============
    "metformin": "Diabetes Control",
    "glucophage": "Diabetes Control",
    "glycomet": "Diabetes Control",
    "glimepiride": "Diabetes Control",
    "amaryl": "Diabetes Control",
    "glimestar": "Diabetes Control",
    "voglibose": "Diabetes Control",
    "voglibose": "Diabetes Control",
    "sitagliptin": "Diabetes Control",
    "januvia": "Diabetes Control",
    "insulin": "Diabetes Control",
    "gliclazide": "Diabetes Control",
    "diamicron": "Diabetes Control",
    "glibenclamide": "Diabetes Control",
    "glyburide": "Diabetes Control",
    "tolbutamide": "Diabetes Control",
    "pioglitazone": "Diabetes Control",
    "actos": "Diabetes Control",
    "rosiglitazone": "Diabetes Control",
    "avandia": "Diabetes Control",
    "repaglinide": "Diabetes Control",
    "janumet": "Diabetes Control",
    "vildagliptin": "Diabetes Control",
    "linagliptin": "Diabetes Control",
    "saxagliptin": "Diabetes Control",
    "dapagliflozin": "Diabetes Control",
    "empagliflozin": "Diabetes Control",
    "canagliflozin": "Diabetes Control",
    "liraglutide": "Diabetes Control",
    "victoza": "Diabetes Control",
    "semaglutide": "Diabetes Control",
    "ozempic": "Diabetes Control",
    "dulaglutide": "Diabetes Control",
    "trulicity": "Diabetes Control",

    # ============ BLOOD PRESSURE CONTROL ============
    "amlodipine": "Blood Pressure Control",
    "amlong": "Blood Pressure Control",
    "stamlo": "Blood Pressure Control",
    "norvasc": "Blood Pressure Control",
    "losartan": "Blood Pressure Control",
    "losar": "Blood Pressure Control",
    "repace": "Blood Pressure Control",
    "cozaar": "Blood Pressure Control",
    "telmisartan": "Blood Pressure Control",
    "telma": "Blood Pressure Control",
    "telsartan": "Blood Pressure Control",
    "micardis": "Blood Pressure Control",
    "atenolol": "Blood Pressure Control",
    "tenormin": "Blood Pressure Control",
    "metoprolol": "Blood Pressure Control",
    "lopressor": "Blood Pressure Control",
    "propranolol": "Blood Pressure Control",
    "inderal": "Blood Pressure Control",
    "bisoprolol": "Blood Pressure Control",
    "lisinopril": "Blood Pressure Control",
    "prinivil": "Blood Pressure Control",
    "enalapril": "Blood Pressure Control",
    "vasotec": "Blood Pressure Control",
    "ramipril": "Blood Pressure Control",
    "altace": "Blood Pressure Control",
    "perindopril": "Blood Pressure Control",
    "valsartan": "Blood Pressure Control",
    "diovan": "Blood Pressure Control",
    "olmesartan": "Blood Pressure Control",
    "benicar": "Blood Pressure Control",
    "candesartan": "Blood Pressure Control",
    "atacand": "Blood Pressure Control",
    "irbesartan": "Blood Pressure Control",
    "avapro": "Blood Pressure Control",
    "diltiazem": "Blood Pressure Control",
    "cardizem": "Blood Pressure Control",
    "verapamil": "Blood Pressure Control",
    "isoptin": "Blood Pressure Control",
    "nifedipine": "Blood Pressure Control",
    "adalat": "Blood Pressure Control",
    "labetalol": "Blood Pressure Control",
    "trandate": "Blood Pressure Control",
    "methyldopa": "Blood Pressure Control",
    "aldomet": "Blood Pressure Control",
    "clonidine": "Blood Pressure Control",
    "catapres": "Blood Pressure Control",
    "hydralazine": "Blood Pressure Control",
    "apresoline": "Blood Pressure Control",
    "spironolactone": "Blood Pressure Control",
    "aldactone": "Blood Pressure Control",
    "hydrochlorothiazide": "Blood Pressure Control",
    "hctz": "Blood Pressure Control",
    "furosemide": "Blood Pressure Control",
    "lasix": "Blood Pressure Control",
    "torsemide": "Blood Pressure Control",
    "demadex": "Blood Pressure Control",
    "carvedilol": "Blood Pressure Control",
    "coreg": "Blood Pressure Control",
    "nebivolol": "Blood Pressure Control",
    "bystolic": "Blood Pressure Control",
    
    # ============ CHOLESTEROL CONTROL ============
    "atorvastatin": "Cholesterol Control",
    "atorlip": "Cholesterol Control",
    "lipicure": "Cholesterol Control",
    "lipitor": "Cholesterol Control",
    "rosuvastatin": "Cholesterol Control",
    "rozavel": "Cholesterol Control",
    "rosuvas": "Cholesterol Control",
    "crestor": "Cholesterol Control",
    "simvastatin": "Cholesterol Control",
    "zocor": "Cholesterol Control",
    "pravastatin": "Cholesterol Control",
    "pravachol": "Cholesterol Control",
    "lovastatin": "Cholesterol Control",
    "mevacor": "Cholesterol Control",
    "fluvastatin": "Cholesterol Control",
    "lescol": "Cholesterol Control",
    "pitavastatin": "Cholesterol Control",
    "ezetimibe": "Cholesterol Control",
    "zetia": "Cholesterol Control",
    "fenofibrate": "Cholesterol Control",
    "tricor": "Cholesterol Control",
    "gemfibrozil": "Cholesterol Control",
    "lopid": "Cholesterol Control",
    "bezafibrate": "Cholesterol Control",
    "benfotiamine": "Cholesterol Control",
    
    # ============ ALLERGY RELIEF ============
    "cetirizine": "Allergy Relief",
    "levocetirizine": "Allergy Relief",
    "xyzal": "Allergy Relief",
    "fexofenadine": "Allergy Relief",
    "allegra": "Allergy Relief",
    "loratadine": "Allergy Relief",
    "claritin": "Allergy Relief",
    "terfenadine": "Allergy Relief",
    "seldane": "Allergy Relief",
    "astemizole": "Allergy Relief",
    "hismanal": "Allergy Relief",
    "desloratadine": "Allergy Relief",
    "clarinex": "Allergy Relief",
    "azelastine": "Allergy Relief",
    "astepro": "Allergy Relief",
    "olopatadine": "Allergy Relief",
    "patanol": "Allergy Relief",
    "ketotifen": "Allergy Relief",
    "zaditor": "Allergy Relief",
    "promethazine": "Allergy Relief",
    "phenergan": "Allergy Relief",
    "diphenhydramine": "Allergy Relief",
    "benadryl": "Allergy Relief",
    "chlorpheniramine": "Allergy Relief",
    "chlor-trimeton": "Allergy Relief",
    "hydroxyzine": "Allergy Relief",
    "vistaril": "Allergy Relief",
    "cyproheptadine": "Allergy Relief",
    "periactin": "Allergy Relief",
    
    # ============ ACIDITY & GASTRIC RELIEF ============
    "pantoprazole": "Acidity Relief",
    "pan-d": "Acidity Relief",
    "pantocid": "Acidity Relief",
    "omeprazole": "Acidity Relief",
    "prilosec": "Acidity Relief",
    "omez": "Acidity Relief",
    "rabeprazole": "Acidity Relief",
    "razo": "Acidity Relief",
    "rabicip": "Acidity Relief",
    "esomeprazole": "Acidity Relief",
    "nexium": "Acidity Relief",
    "lansoprazole": "Acidity Relief",
    "prevacid": "Acidity Relief",
    "dexlansoprazole": "Acidity Relief",
    "famotidine": "Acidity Relief",
    "pepcid": "Acidity Relief",
    "rantac": "Acidity Relief",
    "rantidine": "Acidity Relief",
    "ranitidine": "Acidity Relief",
    "zantac": "Acidity Relief",
    "cimetidine": "Acidity Relief",
    "tagamet": "Acidity Relief",
    "nizatidine": "Acidity Relief",
    "axid": "Acidity Relief",
    "gelusil": "Acidity & Gastric Relief",
    "digene": "Acidity & Gastric Relief",
    "aluminium hydroxide": "Antacid",
    "magnesium hydroxide": "Antacid",
    "calcium carbonate": "Antacid",
    "sodium bicarbonate": "Antacid",
    "sucralfate": "Gastric Relief",
    "carafate": "Gastric Relief",
    "metoclopramide": "Gastric Relief",
    "reglan": "Gastric Relief",
    "domperidone": "Gastric Relief",
    "motilium": "Gastric Relief",
    "mosapride": "Gastric Relief",
    
    # ============ ASTHMA & BRONCHITIS ============
    "salbutamol": "Asthma Relief",
    "albuterol": "Asthma Relief",
    "ventolin": "Asthma Relief",
    "montelukast": "Asthma Relief",
    "singulair": "Asthma Relief",
    "budesonide": "Asthma Relief",
    "pulmicort": "Asthma Relief",
    "fluticasone": "Asthma Relief",
    "flovent": "Asthma Relief",
    "beclomethasone": "Asthma Relief",
    "ciclesonide": "Asthma Relief",
    "mometasone": "Asthma Relief",
    "terbutaline": "Asthma Relief",
    "brethine": "Asthma Relief",
    "ipratropium": "Asthma Relief",
    "atrovent": "Asthma Relief",
    "theophylline": "Asthma Relief",
    "aminophylline": "Asthma Relief",
    "zafirlukast": "Asthma Relief",
    "accolate": "Asthma Relief",
    "roflumilast": "Asthma Relief",
    "daliresp": "Asthma Relief",
    "cromoglycate": "Asthma Relief",
    "intal": "Asthma Relief",
    "nedocromil": "Asthma Relief",
    "tilade": "Asthma Relief",
    
    # ============ THYROID TREATMENT ============
    "thyroxine": "Thyroid Treatment",
    "levothyroxine": "Thyroid Treatment",
    "synthroid": "Thyroid Treatment",
    "eltroxin": "Thyroid Treatment",
    "liothyronine": "Thyroid Treatment",
    "cytomel": "Thyroid Treatment",
    "liotrix": "Thyroid Treatment",
    "thionamide": "Thyroid Treatment",
    "propylthiouracil": "Thyroid Treatment",
    "methimazole": "Thyroid Treatment",
    "tapazole": "Thyroid Treatment",
    "carbimazole": "Thyroid Treatment",
    "neo-mercazole": "Thyroid Treatment",
    
    # ============ VITAMINS & SUPPLEMENTS ============
    "becosules": "Vitamin Supplement",
    "becadexamin": "Vitamin Supplement",
    "supradyn": "Vitamin Supplement",
    "neurobion": "Vitamin Supplement",
    "limcee": "Vitamin C Supplement",
    "vitamin c": "Vitamin C Supplement",
    "ascorbic acid": "Vitamin C Supplement",
    "vitamin b1": "Vitamin B Complex",
    "thiamine": "Vitamin B Complex",
    "vitamin b2": "Vitamin B Complex",
    "riboflavin": "Vitamin B Complex",
    "vitamin b3": "Vitamin B Complex",
    "niacin": "Vitamin B Complex",
    "vitamin b5": "Vitamin B Complex",
    "pantothenic acid": "Vitamin B Complex",
    "vitamin b6": "Vitamin B Complex",
    "pyridoxine": "Vitamin B Complex",
    "vitamin b12": "Vitamin B Complex",
    "cyanocobalamin": "Vitamin B Complex",
    "vitamin b complex": "Vitamin B Complex",
    "folic acid": "Vitamin B Complex",
    "methylfolate": "Vitamin B Complex",
    "vitamin a": "Vitamin Supplement",
    "retinol": "Vitamin Supplement",
    "vitamin d": "Vitamin Supplement",
    "vitamin d2": "Vitamin Supplement",
    "ergocalciferol": "Vitamin Supplement",
    "vitamin d3": "Vitamin Supplement",
    "cholecalciferol": "Vitamin Supplement",
    "vitamin e": "Vitamin Supplement",
    "tocopherol": "Vitamin Supplement",
    "vitamin k": "Vitamin Supplement",
    "phylloquinone": "Vitamin Supplement",
    "menadione": "Vitamin Supplement",
    "biotin": "Vitamin Supplement",
    "inositol": "Vitamin Supplement",
    "choline": "Vitamin Supplement",
    "coenzyme q10": "Vitamin Supplement",
    "ubiquinone": "Vitamin Supplement",
    "fish oil": "Supplement",
    "omega 3": "Supplement",
    "ginseng": "Supplement",
    "echinacea": "Supplement",
    "garlic": "Supplement",
    "turmeric": "Supplement",
    "ginger": "Supplement",
    "glucosamine": "Supplement",
    "chondroitin": "Supplement",
    
    # ============ MINERALS & CALCIUM ============
    "calcium": "Calcium Supplement",
    "calcium carbonate": "Calcium Supplement",
    "shelcal": "Calcium Supplement",
    "calcirol": "Calcium Supplement",
    "iron": "Iron Supplement",
    "ferrous sulfate": "Iron Supplement",
    "ferrous fumarate": "Iron Supplement",
    "zinc": "Zinc Supplement",
    "magnesium": "Magnesium Supplement",
    "potassium": "Potassium Supplement",
    "sodium": "Sodium Supplement",
    "iodine": "Iodine Supplement",
    "selenium": "Selenium Supplement",
    "copper": "Copper Supplement",
    "manganese": "Manganese Supplement",
    "chromium": "Chromium Supplement",
    
    # ============ SKIN TREATMENT ============
    "clobetasol": "Skin Treatment",
    "mupirocin": "Skin Treatment",
    "bactroban": "Skin Treatment",
    "neomycin": "Skin Treatment",
    "bacitracin": "Skin Treatment",
    "polymyxin b": "Skin Treatment",
    "hydrocortisone": "Skin Treatment",
    "mometasone": "Skin Treatment",
    "betamethasone": "Skin Treatment",
    "triamcinolone": "Skin Treatment",
    "fluticasone": "Skin Treatment",
    "clotrimazole": "Skin Treatment",
    "miconazole": "Skin Treatment",
    "fluconazole": "Skin Treatment",
    "terbinafine": "Skin Treatment",
    "ketoconazole": "Skin Treatment",
    "selenium sulfide": "Skin Treatment",
    "salicylic acid": "Skin Treatment",
    "benzoyl peroxide": "Skin Treatment",
    "tretinoin": "Skin Treatment",
    "adapalene": "Skin Treatment",
    "isotretinoin": "Skin Treatment",
    "accutane": "Skin Treatment",
    "dapsone": "Skin Treatment",
    "azelaic acid": "Skin Treatment",
    "permethrin": "Skin Treatment",
    "ivermectin": "Skin Treatment",
    "methotrexate": "Skin Treatment",
    "sulfasalazine": "Skin Treatment",
    
    # ============ BLOOD THINNERS & CARDIOVASCULAR ============
    "warfarin": "Blood Thinner",
    "coumadin": "Blood Thinner",
    "clopidogrel": "Blood Thinner",
    "plavix": "Blood Thinner",
    "ecosprin": "Blood Thinner",
    "aspirin": "Blood Thinner",
    "ticlopidine": "Blood Thinner",
    "ticlid": "Blood Thinner",
    "prasugrel": "Blood Thinner",
    "effient": "Blood Thinner",
    "ticagrelor": "Blood Thinner",
    "brilinta": "Blood Thinner",
    "dabigatran": "Blood Thinner",
    "pradaxa": "Blood Thinner",
    "rivaroxaban": "Blood Thinner",
    "xarelto": "Blood Thinner",
    "apixaban": "Blood Thinner",
    "eliquis": "Blood Thinner",
    "edoxaban": "Blood Thinner",
    "lixiana": "Blood Thinner",
    "heparin": "Blood Thinner",
    "enoxaparin": "Blood Thinner",
    "lovenox": "Blood Thinner",
    "dalteparin": "Blood Thinner",
    "fragmin": "Blood Thinner",
    "tinzaparin": "Blood Thinner",
    "innohep": "Blood Thinner",
    "fondaparinux": "Blood Thinner",
    "arixtra": "Blood Thinner",
    "atorvastatin": "Cholesterol Control",
    "isosorbide dinitrate": "Heart Medication",
    "isordil": "Heart Medication",
    "nitroglycerin": "Heart Medication",
    "nitrostat": "Heart Medication",
    "hydralazine": "Blood Pressure Control",
    "digoxin": "Heart Medication",
    "digitalis": "Heart Medication",
    "amiodarone": "Heart Medication",
    "cordarone": "Heart Medication",
    "flecainide": "Heart Medication",
    "tambocor": "Heart Medication",
    "procainamide": "Heart Medication",
    "pronestyl": "Heart Medication",
    "quinidine": "Heart Medication",
    "disopyramide": "Heart Medication",
    "norpace": "Heart Medication",
    
    # ============ ANTIBACTERIAL & ANTIMICROBIAL ============
    "chlorhexidine": "Antibacterial",
    "povidone iodine": "Antibacterial",
    "betadine": "Antibacterial",
    "alcohol": "Antibacterial",
    "hexachlorophene": "Antibacterial",
    "triclosan": "Antibacterial",
    "sulfadiazine": "Antibacterial",
    "sulfamethoxazole": "Antibacterial",
    "trimethoprim": "Antibacterial",
    "bactrim": "Antibacterial",
    "cotrimoxazole": "Antibacterial",
    
    # ============ ANTIFUNGAL ============
    "amphotericin b": "Antifungal",
    "fluconazole": "Antifungal",
    "itraconazole": "Antifungal",
    "voriconazole": "Antifungal",
    "posaconazole": "Antifungal",
    "echinocandin": "Antifungal",
    "caspofungin": "Antifungal",
    "micafungin": "Antifungal",
    "anidulafungin": "Antifungal",
    "griseofulvin": "Antifungal",
    "fulvicin": "Antifungal",
    "terbinafine": "Antifungal",
    "lamisil": "Antifungal",
    "nystatin": "Antifungal",
    "mycostatin": "Antifungal",
    
    # ============ ANTIPARASITIC ============
    "albendazole": "Antiparasitic",
    "zentel": "Antiparasitic",
    "mebendazole": "Antiparasitic",
    "vermox": "Antiparasitic",
    "levamisole": "Antiparasitic",
    "piperazine": "Antiparasitic",
    "pyrantel pamoate": "Antiparasitic",
    "pin-x": "Antiparasitic",
    "ivermectin": "Antiparasitic",
    "stromectol": "Antiparasitic",
    "metronidazole": "Antiparasitic",
    "tinidazole": "Antiparasitic",
    "nitazoxanide": "Antiparasitic",
    
    # ============ ANTIEMETICS (NAUSEA/VOMITING) ============
    "ondansetron": "Antiemetic",
    "zofran": "Antiemetic",
    "granisetron": "Antiemetic",
    "kytril": "Antiemetic",
    "ramosetron": "Antiemetic",
    "palonosetron": "Antiemetic",
    "aloxi": "Antiemetic",
    "prochlorperazine": "Antiemetic",
    "compazine": "Antiemetic",
    "metoclopramide": "Antiemetic",
    "reglan": "Antiemetic",
    "domperidone": "Antiemetic",
    "motilium": "Antiemetic",
    "dexamethasone": "Antiemetic",
    "methylprednisolone": "Antiemetic",
    
    # ============ DEPRESSION & ANXIETY ============
    "sertraline": "Depression / Anxiety",
    "zoloft": "Depression / Anxiety",
    "fluoxetine": "Depression / Anxiety",
    "prozac": "Depression / Anxiety",
    "paroxetine": "Depression / Anxiety",
    "paxil": "Depression / Anxiety",
    "citalopram": "Depression / Anxiety",
    "celexa": "Depression / Anxiety",
    "escitalopram": "Depression / Anxiety",
    "lexapro": "Depression / Anxiety",
    "venlafaxine": "Depression / Anxiety",
    "effexor": "Depression / Anxiety",
    "duloxetine": "Depression / Anxiety",
    "cymbalta": "Depression / Anxiety",
    "bupropion": "Depression / Anxiety",
    "wellbutrin": "Depression / Anxiety",
    "mirtazapine": "Depression / Anxiety",
    "remeron": "Depression / Anxiety",
    "amitriptyline": "Depression / Anxiety",
    "elavil": "Depression / Anxiety",
    "nortriptyline": "Depression / Anxiety",
    "pamelor": "Depression / Anxiety",
    "doxepin": "Depression / Anxiety",
    "silenor": "Depression / Anxiety",
    
    # ============ PSYCHIATRIC MEDICATIONS ============
    "risperidone": "Psychiatric",
    "risperdal": "Psychiatric",
    "quetiapine": "Psychiatric",
    "seroquel": "Psychiatric",
    "aripiprazole": "Psychiatric",
    "abilify": "Psychiatric",
    "olanzapine": "Psychiatric",
    "zyprexa": "Psychiatric",
    "haloperidol": "Psychiatric",
    "haldol": "Psychiatric",
    
    # ============ NEUROPATHIC PAIN & SEIZURE CONTROL ============
    "gabapentin": "Neuropathic Pain",
    "neurontin": "Neuropathic Pain",
    "pregabalin": "Neuropathic Pain",
    "lyrica": "Neuropathic Pain",
    "levetiracetam": "Seizure Control",
    "keppra": "Seizure Control",
    "lamotrigine": "Seizure Control",
    "lamictal": "Seizure Control",
    
    "diazepam": "Anxiety Relief",
    "valium": "Anxiety Relief",
    "alprazolam": "Anxiety Relief",
    "xanax": "Anxiety Relief",
    "lorazepam": "Anxiety Relief",
    "ativan": "Anxiety Relief",
    "clonazepam": "Anxiety Relief",
    "klonopin": "Anxiety Relief",
    "buspirone": "Anxiety Relief",
    "buspar": "Anxiety Relief",
    "hydroxyzine": "Anxiety Relief",
    "vistaril": "Anxiety Relief",
    
    # ============ SLEEP DISORDERS ============
    "zolpidem": "Sleep Disorder",
    "ambien": "Sleep Disorder",
    "eszopiclone": "Sleep Disorder",
    "lunesta": "Sleep Disorder",
    "zaleplon": "Sleep Disorder",
    "sonata": "Sleep Disorder",
    "ramelteon": "Sleep Disorder",
    "rozerem": "Sleep Disorder",
    "melatonin": "Sleep Disorder",
    "diphenhydramine": "Sleep Disorder",
    "sominex": "Sleep Disorder",
    
    # ============ MIGRAINE & HEADACHE ============
    "sumatriptan": "Migraine Relief",
    "imitrex": "Migraine Relief",
    "rizatriptan": "Migraine Relief",
    "maxalt": "Migraine Relief",
    "zolmitriptan": "Migraine Relief",
    "zomig": "Migraine Relief",
    "naratriptan": "Migraine Relief",
    "amerge": "Migraine Relief",
    "frovatriptan": "Migraine Relief",
    "frova": "Migraine Relief",
    "eletriptan": "Migraine Relief",
    "relpax": "Migraine Relief",
    "almotriptan": "Migraine Relief",
    "axert": "Migraine Relief",
    "ergotamine": "Migraine Relief",
    "cafergot": "Migraine Relief",
    "dihydroergotamine": "Migraine Relief",
    "migranal": "Migraine Relief",
    "topiramate": "Migraine Relief",
    "topamax": "Migraine Relief",
    "valproic acid": "Migraine Relief",
    "amitriptyline": "Migraine Relief",
    "propranolol": "Migraine Relief",
    "timolol": "Migraine Relief",
    "verapamil": "Migraine Relief",
    
    # ============ OSTEOPOROSIS & BONE ============
    "alendronate": "Osteoporosis",
    "fosomax": "Osteoporosis",
    "risedronate": "Osteoporosis",
    "actonel": "Osteoporosis",
    "ibandronate": "Osteoporosis",
    "boniva": "Osteoporosis",
    "zoledronic acid": "Osteoporosis",
    "reclast": "Osteoporosis",
    "denosumab": "Osteoporosis",
    "prolia": "Osteoporosis",
    "raloxifene": "Osteoporosis",
    "evista": "Osteoporosis",
    "teriparatide": "Osteoporosis",
    "forteo": "Osteoporosis",
    "abaloparatide": "Osteoporosis",
    "tymlos": "Osteoporosis",
    "romosozumab": "Osteoporosis",
    "evenity": "Osteoporosis",
    "estrogen": "Osteoporosis",
    "hormone replacement": "Osteoporosis",
    
    # ============ ARTHRITIS & INFLAMMATION ============
    "ibuprofen": "Arthritis Relief",
    "naproxen": "Arthritis Relief",
    "indomethacin": "Arthritis Relief",
    "meloxicam": "Arthritis Relief",
    "celecoxib": "Arthritis Relief",
    "celebrex": "Arthritis Relief",
    "rofecoxib": "Arthritis Relief",
    "vioxx": "Arthritis Relief",
    "methylprednisolone": "Arthritis Relief",
    "prednisone": "Arthritis Relief",
    "prednisolone": "Arthritis Relief",
    "dexamethasone": "Arthritis Relief",
    "methotrexate": "Arthritis Relief",
    "sulfasalazine": "Arthritis Relief",
    "azathioprine": "Arthritis Relief",
    "infliximab": "Arthritis Relief",
    "etanercept": "Arthritis Relief",
    "adalimumab": "Arthritis Relief",
    "certolizumab": "Arthritis Relief",
    "golimumab": "Arthritis Relief",
    "rituximab": "Arthritis Relief",
    "abatacept": "Arthritis Relief",
    "anakinra": "Arthritis Relief",
    "tocilizumab": "Arthritis Relief",
    "janus kinase": "Arthritis Relief",
    
    # ============ RESPIRATORY CONDITIONS ============
    "fluticasone": "Respiratory",
    "albuterol": "Respiratory",
    "ipratropium": "Respiratory",
    "tiotropium": "Respiratory",
    "spiriva": "Respiratory",
    "formoterol": "Respiratory",
    "salmeterol": "Respiratory",
    "theophylline": "Respiratory",
    "guaifenesin": "Cough Suppressant",
    "dextromethorphan": "Cough Suppressant",
    "diphenhydramine": "Cough Suppressant",
    "benzonatate": "Cough Suppressant",
    "tessalon": "Cough Suppressant",
    "codeine": "Cough Suppressant",
    "hydrocodone": "Cough Suppressant",
    "metaproterenol": "Respiratory",
    "levalbuterol": "Respiratory",
    "xopenex": "Respiratory",
    
    # ============ GASTROINTESTINAL DISORDERS ============
    "bisacodyl": "Laxative",
    "dulcolax": "Laxative",
    "senna": "Laxative",
    "docusate": "Laxative",
    "colace": "Laxative",
    "polyethylene glycol": "Laxative",
    "golytely": "Laxative",
    "miralax": "Laxative",
    "lactulose": "Laxative",
    "magnesium citrate": "Laxative",
    "magnesium sulfate": "Laxative",
    "sodium phosphate": "Laxative",
    "castor oil": "Laxative",
    "mineral oil": "Laxative",
    "psyllium husk": "Laxative",
    "methylcellulose": "Laxative",
    "loperamide": "Antidiarrheal",
    "imodium": "Antidiarrheal",
    "bismuth subsalicylate": "Antidiarrheal",
    "peptobismol": "Antidiarrheal",
    "diphenoxylate": "Antidiarrheal",
    "atropine": "Antidiarrheal",
    "dicyclomine": "GI Disorder",
    "bentyl": "GI Disorder",
    "hyoscyamine": "GI Disorder",
    "levsin": "GI Disorder",
    "cimetidine": "GI Disorder",
    "ranitidine": "GI Disorder",
    "misoprostol": "GI Disorder",
    "cytotec": "GI Disorder",
    
    # ============ URINARY/BLADDER DISORDERS ============
    "oxybutynin": "Urinary Disorder",
    "ditropan": "Urinary Disorder",
    "tolterodine": "Urinary Disorder",
    "detrol": "Urinary Disorder",
    "solifenacin": "Urinary Disorder",
    "vesicare": "Urinary Disorder",
    "darifenacin": "Urinary Disorder",
    "enablex": "Urinary Disorder",
    "trospium": "Urinary Disorder",
    "sanctura": "Urinary Disorder",
    "mirabegron": "Urinary Disorder",
    "myrbetriq": "Urinary Disorder",
    "bethanechol": "Urinary Disorder",
    "urecholine": "Urinary Disorder",
    "finasteride": "Prostate Disorder",
    "proscar": "Prostate Disorder",
    "dutasteride": "Prostate Disorder",
    "avodart": "Prostate Disorder",
    "tamsulosin": "Prostate Disorder",
    "flomax": "Prostate Disorder",
    "terazosin": "Prostate Disorder",
    "doxazosin": "Prostate Disorder",
    "alfuzosin": "Prostate Disorder",
    "silodosin": "Prostate Disorder",
    
    # ============ ANTICANCER & IMMUNOSUPPRESSANTS ============
    "methotrexate": "Cancer / Immunosuppressant",
    "azathioprine": "Cancer / Immunosuppressant",
    "mycophenolate": "Cancer / Immunosuppressant",
    "cyclosporine": "Cancer / Immunosuppressant",
    "tacrolimus": "Cancer / Immunosuppressant",
    "sirolimus": "Cancer / Immunosuppressant",
    "everolimus": "Cancer / Immunosuppressant",
    "leflunomide": "Cancer / Immunosuppressant",
    "hydroxychloroquine": "Immunosuppressant",
    "chloroquine": "Immunosuppressant",
    "sulfasalazine": "Immunosuppressant",
    
    # ============ ENZYME & HORMONE SUPPLEMENTS ============
    "pancreatin": "Enzyme Supplement",
    "lipase": "Enzyme Supplement",
    "amylase": "Enzyme Supplement",
    "protease": "Enzyme Supplement",
    "lactase": "Enzyme Supplement",
    "levothyroxine": "Hormone Replacement",
    "liothyronine": "Hormone Replacement",
    "estrogen": "Hormone Replacement",
    "progesterone": "Hormone Replacement",
    "testosterone": "Hormone Replacement",
    "hydrocortisone": "Hormone Replacement",
    "prednisone": "Hormone Replacement",
    
    # ============ INDIAN BRAND NAMES ============
    "disprin": "Fever / Pain Relief",
    "saridon": "Fever / Pain Relief",
    "metacin": "Fever / Pain Relief",
    "nimulid": "Pain Relief",
    "relispray": "Pain Relief",
    "sinarest": "Pain Relief",
    "volini": "Pain Relief",
    "moov": "Pain Relief",
    "tiger balm": "Pain Relief",
    "amoxyclav": "Antibiotic",
    "moxicip": "Antibiotic",
    "moxikind-cv": "Antibiotic",
    "azex": "Antibiotic",
    "cifixime": "Antibiotic",
    "citralka": "Acidity Relief",
    "digestal": "Gastric Relief",
    "betnesol": "Skin Treatment",
    "flamazine": "Skin Treatment",
    "povidone iodine": "Skin Treatment",
    "savlon": "Skin Treatment",
    "fucidin": "Skin Treatment",
    "canesten": "Skin Treatment",
    "candid": "Skin Treatment",
    "ecosprin-av": "Blood Thinner",
    "disprin-cv": "Blood Thinner",
    "calmpose": "Anxiety Relief",
    "ativan": "Anxiety Relief",
    "somatize": "Sleep Disorder",
    "prodoxol": "Sleep Disorder",
    "melatonin-sr": "Sleep Disorder",
}


def normalize_database_name(name):
    normalized = name.lower()
    normalized = re.sub(r"[^a-zA-Z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def normalize_medicine_database_keys():
    normalized_database = {}
    for name, category in MEDICINE_DATABASE.items():
        normalized_name = normalize_database_name(name)
        if normalized_name:
            normalized_database.setdefault(normalized_name, category)
    MEDICINE_DATABASE.clear()
    MEDICINE_DATABASE.update(normalized_database)


def load_external_medicine_database():
    if not EXTERNAL_MEDICINE_DATABASE_PATH.exists():
        return 0

    loaded_count = 0
    with open(EXTERNAL_MEDICINE_DATABASE_PATH, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = normalize_database_name(row.get("medicine_name") or "")
            category = (row.get("category") or "RxNav Medicine").strip()
            if not name:
                continue
            if name not in MEDICINE_DATABASE:
                MEDICINE_DATABASE[name] = category
                loaded_count += 1

    return loaded_count


def build_medicine_candidate_index():
    index = defaultdict(list)
    for medicine, category in MEDICINE_DATABASE.items():
        if medicine:
            index[medicine[0]].append((medicine, category))
    return index


def build_exact_medicine_index():
    index = defaultdict(dict)
    for medicine, category in MEDICINE_DATABASE.items():
        token_count = len(medicine.split())
        if 1 <= token_count <= MAX_EXACT_MEDICINE_TOKENS:
            index[token_count][medicine] = category
    return index


normalize_medicine_database_keys()
EXTERNAL_MEDICINE_COUNT = load_external_medicine_database()
MEDICINE_CANDIDATE_INDEX = build_medicine_candidate_index()
EXACT_MEDICINE_INDEX = build_exact_medicine_index()


@st.cache_data(show_spinner=False)
def get_ocr_text_files():
    if not os.path.exists(INPUT_DIR):
        return []

    files = []

    for file in os.listdir(INPUT_DIR):
        if file.endswith(".txt"):
            files.append(file)

    return sorted(files, reverse=True)


@st.cache_data(show_spinner=False)
def read_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_words(text):
    """Extract individual words from text for matching."""
    cleaned = clean_text(text)
    return cleaned.split()


def add_detected_medicine(detected, medicine, category, confidence, detection_method, score):
    if medicine in detected:
        return

    detected[medicine] = {
        "medicine_name": medicine.title(),
        "category": category,
        "confidence": confidence,
        "detection_method": detection_method,
        "score": score
    }


def fuzzy_match_medicine(word, medicine_name, threshold=0.75):
    """
    Perform fuzzy matching between a word and a medicine name.
    Returns a match score.
    """
    ratio = difflib.SequenceMatcher(None, word, medicine_name).ratio()
    return ratio >= threshold, ratio


@st.cache_data(show_spinner=False)
def get_fuzzy_candidates(word):
    if not word:
        return []
    return [
        (medicine, category)
        for medicine, category in MEDICINE_CANDIDATE_INDEX.get(word[0], [])
        if " " not in medicine
        and len(medicine) <= 30
        and abs(len(word) - len(medicine)) <= 3
    ]


@st.cache_data(show_spinner=False)
def get_medicine_categories():
    categories = {}
    for _, category in MEDICINE_DATABASE.items():
        categories[category] = categories.get(category, 0) + 1
    return categories


def remove_nested_exact_matches(detected_medicines):
    exact_items = [
        item for item in detected_medicines
        if item["detection_method"] == "Exact Phrase Match"
    ]
    filtered = []

    for item in detected_medicines:
        item_name = item["medicine_name"].lower()
        item_tokens = item_name.split()
        is_nested = False

        if item["detection_method"] == "Exact Phrase Match":
            for other in exact_items:
                other_name = other["medicine_name"].lower()
                if item_name == other_name:
                    continue
                if len(other_name.split()) <= len(item_tokens):
                    continue
                if re.search(r"\b" + re.escape(item_name) + r"\b", other_name):
                    is_nested = True
                    break

        if not is_nested:
            filtered.append(item)

    return filtered


@st.cache_data(show_spinner=False)
def detect_medicines(text):
    """
    Advanced medicine detection with exact matching and fuzzy matching.
    Returns list of detected medicines with confidence scores.
    """
    words = extract_words(text)
    detected = {}
    exact_matched_words = set()
    
    # Step 1: Exact phrase matching using the normalized OCR tokens.
    max_tokens = min(MAX_EXACT_MEDICINE_TOKENS, len(words))
    for token_count in range(max_tokens, 0, -1):
        candidate_lookup = EXACT_MEDICINE_INDEX.get(token_count, {})
        if not candidate_lookup:
            continue

        for start in range(0, len(words) - token_count + 1):
            phrase = " ".join(words[start:start + token_count])
            category = candidate_lookup.get(phrase)
            if category:
                exact_matched_words.update(words[start:start + token_count])
                add_detected_medicine(
                    detected,
                    phrase,
                    category,
                    "High",
                    "Exact Phrase Match",
                    1.0
                )
    
    # Step 2: Fuzzy matching for misspellings and variations (only if not already detected)
    for word in words:
        if len(word) < 4:  # Skip very short words
            continue
        if word in FUZZY_STOPWORDS:
            continue
        if word in exact_matched_words:
            continue
            
        for medicine, category in get_fuzzy_candidates(word):
            if medicine in detected:  # Skip if already detected
                continue
            
            is_match, score = fuzzy_match_medicine(word, medicine, threshold=0.82)
            
            if is_match:
                medicine_key = medicine.lower()
                if medicine_key not in detected:
                    confidence = "Very High" if score > 0.95 else "High" if score > 0.85 else "Medium"
                    detected[medicine_key] = {
                        "medicine_name": medicine.title(),
                        "category": category,
                        "confidence": confidence,
                        "detection_method": "Fuzzy Match (Typo Detection)",
                        "score": round(score, 2)
                    }
    
    # Convert dictionary to list and sort by confidence
    result = remove_nested_exact_matches(list(detected.values()))
    confidence_order = {"Very High": 4, "High": 3, "Medium": 2, "Low": 1}
    result.sort(key=lambda x: confidence_order.get(x["confidence"], 0), reverse=True)
    
    return result


def show_module_06_medicine_detection():
    st.title("Medicine Name Detection using NLP")

    st.write(
        "Advanced medicine detection system that identifies all types of medicines from OCR text. "
        "Uses exact matching and fuzzy matching for typo/spelling variations."
    )
    
    # Display database statistics
    with st.expander("Medicine Database Statistics"):
        categories = get_medicine_categories()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Medicines", len(MEDICINE_DATABASE))
        col2.metric("Disease Categories", len(categories))
        col3.metric("Detection Methods", 3)
        st.caption(f"External RxNav entries loaded: {EXTERNAL_MEDICINE_COUNT}")
        
        st.write("**Medicines by Category:**")
        cat_df = pd.DataFrame(list(categories.items()), columns=["Category", "Count"])
        cat_df = cat_df.sort_values("Count", ascending=False)
        st.dataframe(cat_df, use_container_width=True)

    text_files = get_ocr_text_files()

    if not text_files:
        st.warning("No OCR text found. Please complete OCR text extraction first.")
        return

    selected_file = st.selectbox(
        "Select OCR text file from above OCR text extraction",
        text_files
    )

    text_path = os.path.join(INPUT_DIR, selected_file)
    ocr_text = read_text_file(text_path)

    st.subheader("OCR Text Input")
    st.text_area("Extracted OCR Text", ocr_text, height=250)

    if st.button("Detect Medicines"):
        detected_medicines = detect_medicines(ocr_text)

        st.subheader("Detection Results")

        if detected_medicines:
            df = pd.DataFrame(detected_medicines)
            
            # Display detection statistics
            col1, col2, col3 = st.columns(3)
            col1.metric("Medicines Detected", len(detected_medicines))
            col2.metric("High Confidence", len([m for m in detected_medicines if m["confidence"] in ["High", "Very High"]]))
            col3.metric("Detection Rate", f"{(len(detected_medicines)/len(MEDICINE_DATABASE)*100):.1f}%")

            st.success("Medicine detection completed successfully.")
            
            # Display dataframe with custom formatting
            st.dataframe(df, use_container_width=True)
            
            # Show detection method breakdown
            st.write("**Detection Methods Used:**")
            methods = df["detection_method"].value_counts()
            st.bar_chart(methods)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            csv_file = f"detected_medicines_{timestamp}.csv"
            json_file = f"detected_medicines_{timestamp}.json"

            csv_path = os.path.join(OUTPUT_DIR, csv_file)
            json_path = os.path.join(OUTPUT_DIR, json_file)

            df.to_csv(csv_path, index=False)

            result_data = {
                "input_file": selected_file,
                "input_path": text_path,
                "detected_medicines": detected_medicines,
                "total_medicines_detected": len(detected_medicines),
                "detection_timestamp": str(datetime.now()),
                "database_size": len(MEDICINE_DATABASE),
                "categories_covered": len(set(MEDICINE_DATABASE.values()))
            }

            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(result_data, file, indent=4)

            st.write("**CSV Output:**", csv_path)
            st.write("**JSON Output:**", json_path)

            st.download_button(
                "Download Medicine CSV",
                data=df.to_csv(index=False),
                file_name="detected_medicines.csv",
                mime="text/csv"
            )

            st.download_button(
                "Download Medicine JSON",
                data=json.dumps(result_data, indent=4),
                file_name="detected_medicines.json",
                mime="application/json"
            )

            st.info("This output is ready for Dosage & Timing Extraction.")

        else:
            st.error("No medicines detected.")

            st.info(
                "Try improving OCR output or add more medicine names "
                "to the MEDICINE_DATABASE dictionary."
            )
