import base64
import csv
import html
import importlib
import shutil
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ASSETS_DIR = Path(__file__).parent / "assets"
OUTPUTS_DIR = Path(__file__).parent / "outputs"
PROJECT_LOGO_IMAGE_PATH = ASSETS_DIR / "ai_prescription_logo.png"

st.set_page_config(
    page_title="AI Prescription Reader",
    page_icon=str(PROJECT_LOGO_IMAGE_PATH) if PROJECT_LOGO_IMAGE_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

NAVBAR_IMAGE_PATH = ASSETS_DIR / "logo_related_navbar_background.png"
UI_BACKGROUND_IMAGE_PATH = ASSETS_DIR / "logo_related_ui_background.png"
PROFESSIONAL_CARD_IMAGE_PATH = ASSETS_DIR / "professional_card_medical.png"
OPTIMIZED_NAVBAR_IMAGE_PATH = ASSETS_DIR / "logo_related_navbar_background_optimized.jpg"
OPTIMIZED_UI_BACKGROUND_IMAGE_PATH = ASSETS_DIR / "logo_related_ui_background_optimized.jpg"
OPTIMIZED_PROFESSIONAL_CARD_IMAGE_PATH = ASSETS_DIR / "professional_card_medical_optimized.jpg"


@st.cache_data(show_spinner=False)
def image_to_data_url(image_path):
    if not image_path.exists():
        return ""
    mime_type = "image/jpeg" if image_path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


NAVBAR_IMAGE_URL = image_to_data_url(OPTIMIZED_NAVBAR_IMAGE_PATH)
UI_BACKGROUND_IMAGE_URL = image_to_data_url(OPTIMIZED_UI_BACKGROUND_IMAGE_PATH)
PROFESSIONAL_CARD_IMAGE_URL = image_to_data_url(OPTIMIZED_PROFESSIONAL_CARD_IMAGE_PATH)
PROJECT_LOGO_IMAGE_URL = image_to_data_url(PROJECT_LOGO_IMAGE_PATH)
NAVBAR_BACKGROUND = (
    "linear-gradient(135deg, rgba(8, 22, 36, 0.64) 0%, rgba(13, 43, 65, 0.5) 48%, rgba(5, 36, 50, 0.62) 100%), "
    f"url('{NAVBAR_IMAGE_URL}')"
    if NAVBAR_IMAGE_URL
    else "linear-gradient(135deg, #395b82 0%, #236f70 100%)"
)
UI_BACKGROUND = (
    "linear-gradient(rgba(248, 252, 253, 0.66), rgba(248, 252, 253, 0.82)), "
    f"url('{UI_BACKGROUND_IMAGE_URL}')"
    if UI_BACKGROUND_IMAGE_URL
    else "linear-gradient(180deg, #f8fcfd 0%, #eef7f7 100%)"
)
PROFESSIONAL_CARD_BACKGROUND = (
    "linear-gradient(90deg, rgba(255, 255, 255, 0.98) 0%, rgba(255, 255, 255, 0.93) 58%, rgba(255, 255, 255, 0.5) 100%), "
    f"url('{PROFESSIONAL_CARD_IMAGE_URL}')"
    if PROFESSIONAL_CARD_IMAGE_URL
    else "white"
)

# Initialize session state for current module and user state
if 'current_module' not in st.session_state:
    st.session_state.current_module = "Home"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'login_username' not in st.session_state:
    st.session_state.login_username = ""
if 'login_error' not in st.session_state:
    st.session_state.login_error = ""
if 'show_login_dialog' not in st.session_state:
    st.session_state.show_login_dialog = False
if 'show_features' not in st.session_state:
    st.session_state.show_features = False
if 'show_workflow' not in st.session_state:
    st.session_state.show_workflow = False
if 'language' not in st.session_state:
    st.session_state.language = "English"

module_list = [
    "Home",
    "Upload",
    "Preprocessing",
    "OCR",
    "Medicines",
    "Dosage",
    "Benefits",
    "Interactions",
    "Recommendations",
    "Dashboard",
    "Database"
]
workflow_module_list = [module for module in module_list if module != "Home"]

LANGUAGE_OPTIONS = {
    "English": "English",
    "Hindi": "हिन्दी",
    "Telugu": "తెలుగు",
}

TRANSLATIONS = {
    "English": {
        "language": "Language",
        "module_Home": "Home",
        "module_Upload": "Upload",
        "module_Preprocessing": "Preprocessing",
        "module_OCR": "OCR",
        "module_Medicines": "Medicines",
        "module_Dosage": "Dosage",
        "module_Benefits": "Benefits",
        "module_Interactions": "Interactions",
        "module_Recommendations": "Recommendations",
        "module_Dashboard": "Dashboard",
        "module_Database": "Database",
        "app_title": "AI Prescription Reader",
        "app_subtitle": "Advanced Medicine Intelligence & Analysis Platform",
        "logged_in": "Logged in",
        "guest": "Guest",
        "login_to_save": "Login to save data under your name",
        "login_store_info": "Login to store prescriptions and reports under your name.",
        "signed_in_as": "Signed in as:",
        "login": "Login",
        "logout": "Logout",
        "clear_output": "Clear All Output",
        "continue_workflow": "Continue Workflow",
        "previous": "Previous",
        "next": "Next",
        "start_upload": "Start Upload",
        "back_home": "Back Home",
        "step": "Step",
        "of": "of",
        "home_title": "Medicine Prescription Analysis Platform",
        "home_subtitle": "Advanced AI-powered medicine intelligence and prescription analysis system",
        "database_access": "Database Access",
        "cloud_storage": "Cloud Storage",
        "medical_disclaimer_title": "Medical Disclaimer",
        "medical_disclaimer_text": "This AI Prescription Reader is designed to assist with prescription text extraction and medicine information only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always confirm medicines, dosage, interactions, and recommendations with a licensed doctor or pharmacist before making health decisions.",
        "user_guide": "User Guide",
        "show_features": "Show Key Features",
        "show_workflow": "Show Application Workflow",
        "key_features": "Key Features",
        "image_processing": "Image Processing",
        "image_processing_text": "Advanced preprocessing and enhancement of prescription images",
        "ocr_technology": "OCR Technology",
        "ocr_technology_text": "Accurate text extraction using state-of-the-art OCR engines",
        "ai_analysis": "AI Analysis",
        "ai_analysis_text": "Intelligent medicine detection and interaction analysis",
        "application_workflow": "Application Workflow",
        "workflow_upload_title": "Upload Prescription",
        "workflow_upload_text": "Upload a clear image of your prescription document",
        "workflow_preprocess_title": "Image Processing",
        "workflow_preprocess_text": "Enhance and preprocess the image for better accuracy",
        "workflow_ocr_title": "Text Extraction",
        "workflow_ocr_text": "Extract text using advanced OCR technology",
        "workflow_medicine_title": "Medicine Detection",
        "workflow_medicine_text": "Identify and analyze all medicines in the prescription",
        "workflow_dosage_title": "Dosage Analysis",
        "workflow_dosage_text": "Extract dosage information and timing details",
        "workflow_safety_title": "Safety Check",
        "workflow_safety_text": "Check for drug interactions and contraindications",
        "workflow_recommendations_title": "Recommendations",
        "workflow_recommendations_text": "Get personalized health recommendations",
        "workflow_database_title": "Database Storage",
        "workflow_database_text": "Store results securely in MongoDB cloud database",
        "workspace_title": "AI Prescription Reader & Medicine Intelligence System",
        "workspace_text": "Understand your prescription in a better way with AI. Current workspace:",
        "upload_new": "Upload New",
        "summary_medicines": "Medicines Found",
        "summary_medicines_caption": "Total medicines detected",
        "summary_dosage": "Dosage Instructions",
        "summary_dosage_caption": "Dosage rows extracted",
        "summary_interactions": "Interactions Found",
        "summary_interactions_caption": "Potential interactions",
        "summary_recommendations": "Recommendations",
        "summary_recommendations_caption": "Better alternatives",
        "summary_completed": "Analysis Completed",
        "summary_completed_caption": "Current workflow progress",
    },
    "Hindi": {
        "language": "भाषा",
        "module_Home": "होम",
        "module_Upload": "अपलोड",
        "module_Preprocessing": "प्रीप्रोसेसिंग",
        "module_OCR": "ओसीआर",
        "module_Medicines": "दवाइयां",
        "module_Dosage": "खुराक",
        "module_Benefits": "लाभ",
        "module_Interactions": "इंटरैक्शन",
        "module_Recommendations": "सिफारिशें",
        "module_Dashboard": "डैशबोर्ड",
        "module_Database": "डेटाबेस",
        "app_title": "एआई प्रिस्क्रिप्शन रीडर",
        "app_subtitle": "उन्नत मेडिसिन इंटेलिजेंस और विश्लेषण प्लेटफॉर्म",
        "logged_in": "लॉग इन",
        "guest": "अतिथि",
        "login_to_save": "अपने नाम से डेटा सहेजने के लिए लॉगिन करें",
        "login_store_info": "प्रिस्क्रिप्शन और रिपोर्ट अपने नाम से सहेजने के लिए लॉगिन करें.",
        "signed_in_as": "लॉग इन उपयोगकर्ता:",
        "login": "लॉगिन",
        "logout": "लॉगआउट",
        "clear_output": "सभी आउटपुट साफ करें",
        "continue_workflow": "वर्कफ्लो जारी रखें",
        "previous": "पिछला",
        "next": "अगला",
        "start_upload": "अपलोड शुरू करें",
        "back_home": "होम पर जाएं",
        "step": "चरण",
        "of": "में से",
        "home_title": "मेडिसिन प्रिस्क्रिप्शन विश्लेषण प्लेटफॉर्म",
        "home_subtitle": "एआई-संचालित मेडिसिन इंटेलिजेंस और प्रिस्क्रिप्शन विश्लेषण सिस्टम",
        "database_access": "डेटाबेस एक्सेस",
        "cloud_storage": "क्लाउड स्टोरेज",
        "medical_disclaimer_title": "चिकित्सा अस्वीकरण",
        "medical_disclaimer_text": "यह एआई प्रिस्क्रिप्शन रीडर केवल प्रिस्क्रिप्शन टेक्स्ट निकालने और दवा संबंधी जानकारी में सहायता के लिए बनाया गया है. यह पेशेवर चिकित्सा सलाह, निदान या उपचार का विकल्प नहीं है. स्वास्थ्य निर्णय लेने से पहले दवाइयों, खुराक, इंटरैक्शन और सिफारिशों की पुष्टि हमेशा लाइसेंस प्राप्त डॉक्टर या फार्मासिस्ट से करें.",
        "user_guide": "उपयोगकर्ता गाइड",
        "show_features": "मुख्य सुविधाएं दिखाएं",
        "show_workflow": "एप्लिकेशन वर्कफ्लो दिखाएं",
        "key_features": "मुख्य सुविधाएं",
        "image_processing": "इमेज प्रोसेसिंग",
        "image_processing_text": "प्रिस्क्रिप्शन इमेज की उन्नत प्रीप्रोसेसिंग और सुधार",
        "ocr_technology": "ओसीआर तकनीक",
        "ocr_technology_text": "उन्नत ओसीआर इंजन से सटीक टेक्स्ट एक्सट्रैक्शन",
        "ai_analysis": "एआई विश्लेषण",
        "ai_analysis_text": "स्मार्ट दवा पहचान और इंटरैक्शन विश्लेषण",
        "application_workflow": "एप्लिकेशन वर्कफ्लो",
        "workflow_upload_title": "प्रिस्क्रिप्शन अपलोड करें",
        "workflow_upload_text": "अपने प्रिस्क्रिप्शन दस्तावेज़ की साफ इमेज अपलोड करें",
        "workflow_preprocess_title": "इमेज प्रोसेसिंग",
        "workflow_preprocess_text": "बेहतर सटीकता के लिए इमेज को सुधारें और प्रीप्रोसेस करें",
        "workflow_ocr_title": "टेक्स्ट एक्सट्रैक्शन",
        "workflow_ocr_text": "उन्नत ओसीआर तकनीक से टेक्स्ट निकालें",
        "workflow_medicine_title": "दवा पहचान",
        "workflow_medicine_text": "प्रिस्क्रिप्शन की सभी दवाइयों की पहचान और विश्लेषण करें",
        "workflow_dosage_title": "खुराक विश्लेषण",
        "workflow_dosage_text": "खुराक और समय की जानकारी निकालें",
        "workflow_safety_title": "सुरक्षा जांच",
        "workflow_safety_text": "दवा इंटरैक्शन और सावधानियों की जांच करें",
        "workflow_recommendations_title": "सिफारिशें",
        "workflow_recommendations_text": "व्यक्तिगत स्वास्थ्य सिफारिशें प्राप्त करें",
        "workflow_database_title": "डेटाबेस स्टोरेज",
        "workflow_database_text": "परिणामों को MongoDB क्लाउड डेटाबेस में सुरक्षित रखें",
        "workspace_title": "एआई प्रिस्क्रिप्शन रीडर और मेडिसिन इंटेलिजेंस सिस्टम",
        "workspace_text": "एआई की मदद से अपने प्रिस्क्रिप्शन को बेहतर समझें. वर्तमान वर्कस्पेस:",
        "upload_new": "नया अपलोड",
        "summary_medicines": "दवाइयां मिलीं",
        "summary_medicines_caption": "कुल पहचानी गई दवाइयां",
        "summary_dosage": "खुराक निर्देश",
        "summary_dosage_caption": "निकाली गई खुराक पंक्तियां",
        "summary_interactions": "इंटरैक्शन मिले",
        "summary_interactions_caption": "संभावित इंटरैक्शन",
        "summary_recommendations": "सिफारिशें",
        "summary_recommendations_caption": "बेहतर विकल्प",
        "summary_completed": "विश्लेषण पूरा",
        "summary_completed_caption": "वर्तमान वर्कफ्लो प्रगति",
    },
    "Telugu": {
        "language": "భాష",
        "module_Home": "హోమ్",
        "module_Upload": "అప్లోడ్",
        "module_Preprocessing": "ప్రీప్రాసెసింగ్",
        "module_OCR": "ఓసీఆర్",
        "module_Medicines": "మందులు",
        "module_Dosage": "మోతాదు",
        "module_Benefits": "ప్రయోజనాలు",
        "module_Interactions": "ఇంటరాక్షన్స్",
        "module_Recommendations": "సిఫార్సులు",
        "module_Dashboard": "డ్యాష్‌బోర్డ్",
        "module_Database": "డేటాబేస్",
        "app_title": "ఏఐ ప్రిస్క్రిప్షన్ రీడర్",
        "app_subtitle": "అధునాతన మెడిసిన్ ఇంటెలిజెన్స్ మరియు విశ్లేషణ వేదిక",
        "logged_in": "లాగిన్ అయ్యారు",
        "guest": "అతిథి",
        "login_to_save": "మీ పేరుతో డేటాను సేవ్ చేయడానికి లాగిన్ చేయండి",
        "login_store_info": "ప్రిస్క్రిప్షన్లు మరియు రిపోర్టులను మీ పేరుతో సేవ్ చేయడానికి లాగిన్ చేయండి.",
        "signed_in_as": "లాగిన్ అయినవారు:",
        "login": "లాగిన్",
        "logout": "లాగౌట్",
        "clear_output": "అన్ని అవుట్‌పుట్ క్లియర్ చేయండి",
        "continue_workflow": "వర్క్‌ఫ్లో కొనసాగించండి",
        "previous": "మునుపటి",
        "next": "తర్వాత",
        "start_upload": "అప్లోడ్ ప్రారంభించండి",
        "back_home": "హోమ్‌కు వెళ్ళండి",
        "step": "దశ",
        "of": "లో",
        "home_title": "మెడిసిన్ ప్రిస్క్రిప్షన్ విశ్లేషణ వేదిక",
        "home_subtitle": "ఏఐ ఆధారిత మెడిసిన్ ఇంటెలిజెన్స్ మరియు ప్రిస్క్రిప్షన్ విశ్లేషణ వ్యవస్థ",
        "database_access": "డేటాబేస్ యాక్సెస్",
        "cloud_storage": "క్లౌడ్ స్టోరేజ్",
        "medical_disclaimer_title": "వైద్య హెచ్చరిక",
        "medical_disclaimer_text": "ఈ ఏఐ ప్రిస్క్రిప్షన్ రీడర్ ప్రిస్క్రిప్షన్ టెక్స్ట్ ఎక్స్‌ట్రాక్షన్ మరియు మందుల సమాచారంలో సహాయం చేయడానికి మాత్రమే రూపొందించబడింది. ఇది వైద్య సలహా, నిర్ధారణ లేదా చికిత్సకు ప్రత్యామ్నాయం కాదు. ఆరోగ్య నిర్ణయాలకు ముందు మందులు, మోతాదు, ఇంటరాక్షన్స్ మరియు సిఫార్సులను తప్పనిసరిగా లైసెన్స్ పొందిన డాక్టర్ లేదా ఫార్మసిస్ట్‌తో నిర్ధారించండి.",
        "user_guide": "యూజర్ గైడ్",
        "show_features": "ముఖ్య ఫీచర్లు చూపించు",
        "show_workflow": "అప్లికేషన్ వర్క్‌ఫ్లో చూపించు",
        "key_features": "ముఖ్య ఫీచర్లు",
        "image_processing": "ఇమేజ్ ప్రాసెసింగ్",
        "image_processing_text": "ప్రిస్క్రిప్షన్ ఇమేజ్‌లకు అధునాతన ప్రీప్రాసెసింగ్ మరియు మెరుగుదల",
        "ocr_technology": "ఓసీఆర్ టెక్నాలజీ",
        "ocr_technology_text": "అధునాతన ఓసీఆర్ ఇంజిన్లతో ఖచ్చితమైన టెక్స్ట్ ఎక్స్‌ట్రాక్షన్",
        "ai_analysis": "ఏఐ విశ్లేషణ",
        "ai_analysis_text": "తెలివైన మందుల గుర్తింపు మరియు ఇంటరాక్షన్ విశ్లేషణ",
        "application_workflow": "అప్లికేషన్ వర్క్‌ఫ్లో",
        "workflow_upload_title": "ప్రిస్క్రిప్షన్ అప్లోడ్ చేయండి",
        "workflow_upload_text": "మీ ప్రిస్క్రిప్షన్ డాక్యుమెంట్ యొక్క స్పష్టమైన ఇమేజ్ అప్లోడ్ చేయండి",
        "workflow_preprocess_title": "ఇమేజ్ ప్రాసెసింగ్",
        "workflow_preprocess_text": "మెరుగైన ఖచ్చితత్వం కోసం ఇమేజ్‌ను మెరుగుపరచండి మరియు ప్రీప్రాసెస్ చేయండి",
        "workflow_ocr_title": "టెక్స్ట్ ఎక్స్‌ట్రాక్షన్",
        "workflow_ocr_text": "అధునాతన ఓసీఆర్ టెక్నాలజీతో టెక్స్ట్‌ను తీసుకోండి",
        "workflow_medicine_title": "మందుల గుర్తింపు",
        "workflow_medicine_text": "ప్రిస్క్రిప్షన్‌లోని అన్ని మందులను గుర్తించి విశ్లేషించండి",
        "workflow_dosage_title": "మోతాదు విశ్లేషణ",
        "workflow_dosage_text": "మోతాదు సమాచారం మరియు సమయ వివరాలను తీసుకోండి",
        "workflow_safety_title": "సేఫ్టీ చెక్",
        "workflow_safety_text": "మందుల ఇంటరాక్షన్స్ మరియు జాగ్రత్తలను తనిఖీ చేయండి",
        "workflow_recommendations_title": "సిఫార్సులు",
        "workflow_recommendations_text": "వ్యక్తిగత ఆరోగ్య సిఫార్సులను పొందండి",
        "workflow_database_title": "డేటాబేస్ స్టోరేజ్",
        "workflow_database_text": "ఫలితాలను MongoDB క్లౌడ్ డేటాబేస్‌లో భద్రంగా నిల్వ చేయండి",
        "workspace_title": "ఏఐ ప్రిస్క్రిప్షన్ రీడర్ & మెడిసిన్ ఇంటెలిజెన్స్ సిస్టమ్",
        "workspace_text": "ఏఐ సహాయంతో మీ ప్రిస్క్రిప్షన్‌ను మెరుగ్గా అర్థం చేసుకోండి. ప్రస్తుత వర్క్‌స్పేస్:",
        "upload_new": "కొత్త అప్లోడ్",
        "summary_medicines": "మందులు కనుగొనబడ్డాయి",
        "summary_medicines_caption": "మొత్తం గుర్తించిన మందులు",
        "summary_dosage": "మోతాదు సూచనలు",
        "summary_dosage_caption": "తీసుకున్న మోతాదు వరుసలు",
        "summary_interactions": "ఇంటరాక్షన్స్ కనుగొనబడ్డాయి",
        "summary_interactions_caption": "సంభావ్య ఇంటరాక్షన్స్",
        "summary_recommendations": "సిఫార్సులు",
        "summary_recommendations_caption": "మెరుగైన ప్రత్యామ్నాయాలు",
        "summary_completed": "విశ్లేషణ పూర్తయింది",
        "summary_completed_caption": "ప్రస్తుత వర్క్‌ఫ్లో పురోగతి",
    },
}


def t(key):
    language = st.session_state.get("language", "English")
    return TRANSLATIONS.get(language, TRANSLATIONS["English"]).get(key, TRANSLATIONS["English"].get(key, key))


def module_label(module):
    return t(f"module_{module}")

module_icon_files = {
    "Home": "home",
    "Upload": "upload",
    "Preprocessing": "preprocessing",
    "OCR": "ocr",
    "Medicines": "medicines",
    "Dosage": "dosage",
    "Benefits": "benefits",
    "Interactions": "interactions",
    "Recommendations": "recommendations",
    "Dashboard": "dashboard",
    "Database": "database",
}
MODULE_ICON_URLS = {
    module: image_to_data_url(ASSETS_DIR / "ui_icons" / f"{icon_file}.png")
    for module, icon_file in module_icon_files.items()
}
USER_ICON_URL = image_to_data_url(ASSETS_DIR / "ui_icons" / "user.png")


def set_current_module(module):
    if module not in module_list:
        return

    st.session_state.current_module = module


def get_current_module():
    module = st.session_state.get("current_module", "Home")
    if module not in module_list:
        module = "Home"
    st.session_state.current_module = module
    return module


def get_workflow_position(current_module):
    if not workflow_module_list:
        return "Home", 0

    workflow_current = current_module if current_module in workflow_module_list else workflow_module_list[0]
    return workflow_current, workflow_module_list.index(workflow_current)


def rerun_app():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def get_query_param_value(name):
    value = st.query_params.get(name, "")
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def clear_query_params(*names):
    for key in names:
        if key in st.query_params:
            del st.query_params[key]


def clear_keyboard_query_params():
    clear_query_params("keyboard_nav", "keyboard_nav_ts")


def handle_navbar_query_navigation():
    requested_module = get_query_param_value("nav")
    if not requested_module:
        return

    clear_query_params("nav")
    if requested_module in module_list:
        set_current_module(requested_module)
        rerun_app()


def get_keyboard_navigation_target(current_module, direction):
    if not workflow_module_list:
        return None

    if direction == "next":
        if current_module == "Home":
            return workflow_module_list[0]
        if current_module in workflow_module_list:
            _, current_index = get_workflow_position(current_module)
            if current_index < len(workflow_module_list) - 1:
                return workflow_module_list[current_index + 1]

    if direction == "prev" and current_module in workflow_module_list:
        _, current_index = get_workflow_position(current_module)
        if current_index > 0:
            return workflow_module_list[current_index - 1]

    return None


def handle_keyboard_navigation():
    direction = get_query_param_value("keyboard_nav")
    timestamp = get_query_param_value("keyboard_nav_ts")

    if direction not in {"next", "prev"}:
        return

    if timestamp and st.session_state.get("last_keyboard_nav_ts") == timestamp:
        clear_keyboard_query_params()
        return

    st.session_state.last_keyboard_nav_ts = timestamp
    current_module = get_current_module()
    target_module = get_keyboard_navigation_target(current_module, direction)
    clear_keyboard_query_params()

    if target_module and target_module != current_module:
        set_current_module(target_module)
        rerun_app()


def render_keyboard_navigation_listener():
    components.html(
        """
        <script>
            const listenerFlag = "data-prescription-reader-keynav";
            const parentDocument = window.parent.document;

            if (!parentDocument.documentElement.hasAttribute(listenerFlag)) {
                parentDocument.documentElement.setAttribute(listenerFlag, "true");
                parentDocument.addEventListener("keydown", (event) => {
                    const target = event.target;
                    const tagName = target && target.tagName ? target.tagName.toLowerCase() : "";
                    const isTyping = ["input", "textarea", "select"].includes(tagName) || target?.isContentEditable;

                    if (isTyping || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
                        return;
                    }

                    const direction = event.key === "ArrowRight" ? "next" : event.key === "ArrowLeft" ? "prev" : "";
                    if (!direction) {
                        return;
                    }

                    event.preventDefault();
                    const url = new URL(window.parent.location.href);
                    url.searchParams.set("keyboard_nav", direction);
                    url.searchParams.set("keyboard_nav_ts", Date.now().toString());
                    window.parent.location.href = url.toString();
                });
            }
        </script>
        """,
        height=0,
    )

# Helper callbacks for login and clearing output

def complete_login(username):
    username = username.strip()
    if not username:
        st.session_state.login_error = "Please enter your name to continue."
        st.session_state.logged_in = False
        return

    st.session_state.logged_in = True
    st.session_state.username = username
    st.session_state.login_error = ""
    st.session_state.show_login_dialog = False
    set_current_module("Home")


def login_user():
    complete_login(st.session_state.login_username)


def login_guest():
    complete_login("Guest")


def logout_user():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_username = ""
    st.session_state.login_error = ""
    st.session_state.show_login_dialog = False
    set_current_module("Home")


def clear_generated_outputs():
    if not OUTPUTS_DIR.exists():
        return 0

    outputs_root = OUTPUTS_DIR.resolve()
    removed_count = 0

    for output_dir in OUTPUTS_DIR.iterdir():
        if not output_dir.is_dir():
            continue

        resolved_output_dir = output_dir.resolve()
        if outputs_root not in resolved_output_dir.parents and resolved_output_dir != outputs_root:
            continue

        for item in output_dir.iterdir():
            resolved_item = item.resolve()
            if outputs_root not in resolved_item.parents:
                continue

            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            removed_count += 1

    return removed_count


def clear_all_output():
    current_module = get_current_module()
    removed_count = clear_generated_outputs()
    preserved = {
        'current_module': current_module,
        'logged_in': st.session_state.get('logged_in', False),
        'username': st.session_state.get('username', ''),
        'login_username': st.session_state.get('login_username', ''),
        'login_error': st.session_state.get('login_error', ''),
        'show_login_dialog': st.session_state.get('show_login_dialog', False),
        'show_features': st.session_state.get('show_features', False),
        'show_workflow': st.session_state.get('show_workflow', False),
        'language': st.session_state.get('language', 'English'),
        'clear_all_status': f"Cleared {removed_count} generated output item(s) across all sections."
    }
    st.session_state.clear()
    st.session_state.update(preserved)


def render_step_navigation(current_module, key_prefix="top"):
    workflow_current, current_index = get_workflow_position(current_module)
    is_home = current_module == "Home"

    if not workflow_module_list:
        return

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <h2 style="color: #667eea; text-align: center; margin-top: 1rem; margin-bottom: 1.5rem;">Navigate Through Steps</h2>
    """, unsafe_allow_html=True)

    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([1, 1, 2, 1, 1])

    with nav_col1:
        if not is_home and current_index > 0:
            if st.button("⬅️ Previous", key=f"{key_prefix}_prev_button", use_container_width=True):
                set_current_module(workflow_module_list[current_index - 1])
                rerun_app()
        else:
            st.write("")

    with nav_col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, rgba(39, 93, 115, 0.88) 0%, rgba(45, 82, 117, 0.82) 100%); border-radius: 10px; border-left: 4px solid rgba(255, 255, 255, 0.78);">
            <strong style="color: #ffffff; font-size: 1.1rem;">Step {current_index + 1} of {len(workflow_module_list)}</strong><br>
            <small style="color: rgba(255, 255, 255, 0.88);">{workflow_current}</small>
        </div>
        """, unsafe_allow_html=True)

    with nav_col5:
        if is_home:
            if st.button("Start Upload", key=f"{key_prefix}_start_button", use_container_width=True):
                set_current_module(workflow_module_list[0])
                rerun_app()
        elif current_index < len(workflow_module_list) - 1:
            if st.button("Next", key=f"{key_prefix}_next_button", use_container_width=True):
                set_current_module(workflow_module_list[current_index + 1])
                rerun_app()
        else:
            st.write("")

    st.markdown(f"""
    <div style="margin-top: 1.25rem; margin-bottom: 1.5rem;">
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 8px; margin-bottom: 0.5rem; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="width: {((current_index + 1) / len(workflow_module_list)) * 100}%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
        </div>
        <p style="text-align: center; font-size: 0.9rem; color: #667eea; font-weight: 600; margin-top: 0.5rem;">
            Progress: {current_index + 1}/{len(workflow_module_list)} steps • {int(((current_index + 1) / len(workflow_module_list)) * 100)}% Complete
        </p>
    </div>
    """, unsafe_allow_html=True)


@st.dialog("Login")
def render_login_popup():
    st.markdown(
        f"""
        <div class="login-dialog-copy">
            Sign in with your name so prescriptions and reports are stored under your account.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.text_input(
        "Login name",
        key="login_username",
        placeholder="Enter your name",
    )

    if st.session_state.get("login_error"):
        st.error(st.session_state.login_error)

    login_col, guest_col = st.columns([1, 1])
    with login_col:
        if st.button("Login", key="popup_login_button", use_container_width=True):
            login_user()
            if st.session_state.logged_in:
                rerun_app()
    with guest_col:
        if st.button("Continue as Guest", key="popup_guest_button", use_container_width=True):
            login_guest()
            rerun_app()


def render_bottom_navigation(current_module):
    workflow_current, current_index = get_workflow_position(current_module)
    is_home = current_module == "Home"

    if not workflow_module_list:
        return

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 0.75rem;">
            <strong style="color: #445; font-size: 1rem;">Continue Workflow</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    back_col, info_col, next_col = st.columns([1.2, 2.5, 1.2])

    with back_col:
        if not is_home and current_index > 0:
            if st.button("Previous", key="bottom_prev_button", use_container_width=True):
                set_current_module(workflow_module_list[current_index - 1])
                rerun_app()

    with info_col:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.85rem 1rem; background: rgba(255,255,255,0.86); border: 1px solid rgba(102,126,234,0.22); border-radius: 8px;">
                <span style="color: #667eea; font-weight: 700;">Step {current_index + 1} of {len(workflow_module_list)}</span>
                <span style="color: #555;"> · {workflow_current}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with next_col:
        if is_home:
            if st.button("Start Upload", key="bottom_start_button", use_container_width=True):
                set_current_module(workflow_module_list[0])
                rerun_app()
        elif current_index < len(workflow_module_list) - 1:
            if st.button("Next", key="bottom_next_button", use_container_width=True):
                set_current_module(workflow_module_list[current_index + 1])
                rerun_app()
        else:
            if st.button("Back Home", key="bottom_home_button", use_container_width=True):
                set_current_module("Home")
                rerun_app()

# Custom CSS for better styling with TOP navigation
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="collapsedControl"] {
        display: none;
    }

    .stApp {
        background: UI_BACKGROUND_IMAGE;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }
    
    /* Main container styling */
    .main {
        padding-top: 0rem;
        background: transparent;
    }
    
    /* Top navigation bar styling */
    .top-nav-bar {
        position: sticky;
        top: 0;
        background: NAVBAR_BACKGROUND_IMAGE;
        background-size: cover;
        background-position: center;
        padding: 1.2rem 2rem 1.4rem 2rem;
        border-radius: 18px 18px 0 0;
        margin: 0 0 0 0;
        z-index: 999;
        overflow: hidden;
    }

    .top-nav-button-panel {
        background: NAVBAR_BACKGROUND_IMAGE;
        background-size: cover;
        background-position: center bottom;
        margin: 0 0 2rem 0;
        padding: 0 2rem 1.25rem 2rem;
        border-radius: 0 0 18px 18px;
        box-shadow: 0 10px 28px rgba(18, 30, 48, 0.32);
        border-bottom: 1px solid rgba(255, 255, 255, 0.24);
        overflow-x: auto;
        overflow-y: hidden;
        scrollbar-width: thin;
        scrollbar-color: rgba(255, 255, 255, 0.75) rgba(255, 255, 255, 0.18);
    }

    .top-nav-button-panel::-webkit-scrollbar {
        height: 8px;
    }

    .top-nav-button-panel::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.18);
        border-radius: 999px;
    }

    .top-nav-button-panel::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.75);
        border-radius: 999px;
    }

    .top-nav-button-row {
        display: flex;
        align-items: stretch;
        gap: 0.55rem;
    }

    .top-nav-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
        min-width: max-content;
        min-height: 46px;
        padding: 0.65rem 1.05rem;
        background-color: rgba(255, 255, 255, 0.22);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.32);
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 700;
        white-space: nowrap;
        line-height: 1.2;
        text-align: center;
        text-decoration: none;
        text-shadow: 0 1px 6px rgba(0, 0, 0, 0.35);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(6px);
        transition: transform 0.18s ease, background-color 0.18s ease, border-color 0.18s ease;
    }

    .top-nav-button:hover {
        background-color: rgba(255, 255, 255, 0.34);
        color: white;
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-1px);
    }

    .top-nav-button.active {
        background-color: rgba(255, 255, 255, 0.28);
        color: white;
        border-color: rgba(255, 255, 255, 0.72);
        text-shadow: 0 1px 6px rgba(0, 0, 0, 0.35);
    }

    @media (max-width: 700px) {
        .top-nav-button-panel {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .top-nav-button {
            min-height: 44px;
            padding: 0.6rem 0.9rem;
            font-size: 0.86rem;
        }
    }
    
    .nav-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        gap: 1rem;
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 0;
    }

    .nav-logo {
        width: 58px;
        height: 58px;
        flex: 0 0 58px;
        object-fit: contain;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.96);
        padding: 0.32rem;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.22);
    }

    .nav-option-logo {
        width: 1.25rem;
        height: 1.25rem;
        object-fit: contain;
        border-radius: 0.28rem;
        background: rgba(255, 255, 255, 0.92);
        padding: 0.08rem;
        vertical-align: -0.28rem;
        margin-right: 0.35rem;
    }

    .user-status-icon {
        width: 1.15rem;
        height: 1.15rem;
        object-fit: cover;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.95);
        padding: 0.06rem;
        margin-right: 0.35rem;
        vertical-align: -0.22rem;
    }

    .hero-title-logo {
        width: 2.5rem;
        height: 2.5rem;
        object-fit: contain;
        border-radius: 0.65rem;
        background: white;
        padding: 0.16rem;
        margin-right: 0.55rem;
        vertical-align: -0.55rem;
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.18);
    }

    .card-logo {
        width: 2.2rem;
        height: 2.2rem;
        object-fit: contain;
        border-radius: 0.55rem;
        background: white;
        padding: 0.16rem;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.16);
    }

    .module-card-icon {
        width: 2.4rem;
        height: 2.4rem;
        object-fit: cover;
        border-radius: 0.65rem;
        background: white;
        padding: 0.12rem;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.16);
    }
    
    .nav-title {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.45);
    }
    
    .nav-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
        margin-top: 0.25rem;
        text-shadow: 0 1px 8px rgba(0, 0, 0, 0.42);
    }

    .nav-user-status {
        color: white;
        text-align: right;
        font-size: 0.95rem;
        line-height: 1.45;
        text-shadow: 0 1px 8px rgba(0, 0, 0, 0.45);
    }

    .nav-user-subtitle {
        opacity: 0.88;
        font-size: 0.84rem;
    }
    
    @media (max-width: 900px) {
        .nav-header {
            align-items: flex-start;
            flex-direction: column;
            gap: 0.75rem;
        }

        .nav-logo {
            width: 50px;
            height: 50px;
            flex-basis: 50px;
        }

        .nav-user-status {
            text-align: left;
        }
    }
    
    /* Hero section styling */
    .hero-section {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
        border-left: 5px solid #667eea;
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2.5rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
    }
    
    .hero-title {
        color: #667eea;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
    }
    
    .hero-subtitle {
        color: #555;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Professional card styling */
    .professional-card {
        background: PROFESSIONAL_CARD_BACKGROUND_IMAGE;
        background-size: auto 100%;
        background-position: right center;
        background-repeat: no-repeat;
        border-radius: 12px;
        padding: 1.5rem 13rem 1.5rem 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
        min-height: 120px;
        overflow: hidden;
    }
    
    .professional-card:hover {
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }

    @media (max-width: 900px) {
        .professional-card {
            background-size: 12rem auto;
            background-position: right bottom;
            padding-right: 1.5rem;
        }
    }
    
    .card-icon {
        font-size: 1.8rem;
    }
    
    .card-title {
        color: #667eea;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 0;
    }
    
    .card-subtitle {
        color: #888;
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Workflow stats */
    .workflow-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Workflow step */
    .workflow-step {
        display: flex;
        gap: 1.5rem;
        margin: 1.5rem 0;
        align-items: flex-start;
    }
    
    .step-icon {
        width: 58px;
        min-width: 58px;
        height: 58px;
        border-radius: 14px;
        object-fit: cover;
        box-shadow: 0 4px 14px rgba(102, 126, 234, 0.16);
    }
    
    .step-content {
        flex: 1;
        padding-top: 0.5rem;
    }
    
    .step-title {
        color: #667eea;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0 0 0.3rem 0;
    }
    
    .step-description {
        color: #666;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-current {
        background-color: #cce5ff;
        color: #004085;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .status-ready {
        background-color: #d4edda;
        color: #155724;
    }
    
    /* Feature grid */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.15);
        transform: translateY(-3px);
    }
    
    .feature-icon {
        width: 72px;
        height: 72px;
        object-fit: cover;
        border-radius: 18px;
        margin-bottom: 1rem;
        box-shadow: 0 5px 16px rgba(102, 126, 234, 0.16);
    }
    
    .feature-title {
        color: #667eea;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 0 0 0.5rem 0;
    }
    
    .feature-text {
        color: #666;
        font-size: 0.9rem;
        margin: 0;
    }

    .workspace-overview {
        margin: 0.25rem 0 1rem 0;
    }

    .workspace-topline {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .workspace-title h1 {
        color: #101827;
        font-size: 1.85rem;
        line-height: 1.15;
        font-weight: 800;
        margin: 0 0 0.35rem 0;
    }

    .workspace-title p {
        color: #334155;
        font-size: 0.98rem;
        margin: 0;
    }

    .workspace-action {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        padding: 0.65rem 1rem;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(37, 99, 235, 0.26);
        color: #0b5ed7;
        font-weight: 750;
        text-decoration: none;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
        white-space: nowrap;
    }

    .workspace-action:hover {
        color: #084fb8;
        border-color: rgba(37, 99, 235, 0.42);
        transform: translateY(-1px);
    }

    .summary-card-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(150px, 1fr));
        gap: 0.8rem;
        margin: 0.8rem 0 1.1rem 0;
    }

    .summary-card {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-height: 100px;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        backdrop-filter: blur(8px);
    }

    .summary-card img {
        width: 52px;
        height: 52px;
        object-fit: cover;
        border-radius: 16px;
        flex: 0 0 52px;
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.12);
    }

    .summary-label {
        color: #101827;
        font-size: 0.88rem;
        font-weight: 800;
        margin: 0;
    }

    .summary-value {
        color: #0f172a;
        font-size: 1.85rem;
        line-height: 1.05;
        font-weight: 850;
        margin: 0.45rem 0 0.25rem 0;
    }

    .summary-caption {
        color: #475569;
        font-size: 0.82rem;
        margin: 0;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        padding: 0.9rem 1rem;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        background: rgba(255, 255, 255, 0.9);
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 8px;
        font-weight: 750;
    }

    @media (max-width: 1100px) {
        .summary-card-grid {
            grid-template-columns: repeat(2, minmax(180px, 1fr));
        }
    }

    @media (max-width: 700px) {
        .workspace-topline {
            flex-direction: column;
        }

        .summary-card-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Divider */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
    }

    .login-dialog-copy {
        color: #445;
        font-size: 0.98rem;
        line-height: 1.5;
        margin-bottom: 1rem;
    }

    .medical-disclaimer {
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid rgba(180, 122, 24, 0.28);
        border-left: 5px solid #d99426;
        border-radius: 8px;
        padding: 1rem 1.1rem;
        margin: 1.25rem 0 0.25rem 0;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.07);
    }

    .medical-disclaimer strong {
        display: block;
        color: #7a4a08;
        font-size: 0.98rem;
        margin-bottom: 0.25rem;
    }

    .medical-disclaimer p {
        color: #334155;
        font-size: 0.92rem;
        line-height: 1.55;
        margin: 0;
    }
</style>
""".replace("NAVBAR_BACKGROUND_IMAGE", NAVBAR_BACKGROUND).replace("UI_BACKGROUND_IMAGE", UI_BACKGROUND).replace("PROFESSIONAL_CARD_BACKGROUND_IMAGE", PROFESSIONAL_CARD_BACKGROUND), unsafe_allow_html=True)

if st.session_state.show_login_dialog:
    render_login_popup()

handle_navbar_query_navigation()
handle_keyboard_navigation()
render_keyboard_navigation_listener()

selected = get_current_module()

def get_module_icon_html(module, class_name, alt_text=None):
    icon_url = MODULE_ICON_URLS.get(module, "")
    if not icon_url:
        return ""
    alt = html.escape(alt_text if alt_text is not None else f"{module} icon", quote=True)
    return f'<img class="{class_name}" src="{icon_url}" alt="{alt}">'


user_icon_html = (
    f'<img class="user-status-icon" src="{USER_ICON_URL}" alt="">'
    if USER_ICON_URL
    else ""
)
status_html = (
    f'<div class="nav-user-status"><div>{user_icon_html}<strong>{html.escape(st.session_state.username)}</strong></div>'
    '<div class="nav-user-subtitle">Logged in</div></div>'
    if st.session_state.logged_in
    else '<div class="nav-user-status"><div><strong>Guest</strong></div>'
    '<div class="nav-user-subtitle">Login to save data under your name</div></div>'
)
logo_html = (
    f'<img class="nav-logo" src="{PROJECT_LOGO_IMAGE_URL}" alt="AI Prescription Reader logo">'
    if PROJECT_LOGO_IMAGE_URL
    else '<div class="nav-logo" style="display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 800; color: #275d73;">AI</div>'
)

navbar_html = (
    '<div class="top-nav-bar">'
    '<div class="nav-header">'
    '<div class="nav-brand">'
    f'{logo_html}'
    '<div>'
    '<div class="nav-title">AI Prescription Reader</div>'
    '<div class="nav-subtitle">Advanced Medicine Intelligence & Analysis Platform</div>'
    '</div>'
    '</div>'
    f'{status_html}'
    '</div>'
    '</div>'
)

st.markdown(navbar_html, unsafe_allow_html=True)

def get_top_nav_icon_html(option):
    return get_module_icon_html(option, "nav-option-logo", "")


def count_latest_csv_rows(output_subdir):
    output_dir = OUTPUTS_DIR / output_subdir
    if not output_dir.exists():
        return 0

    csv_files = sorted(output_dir.glob("*.csv"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not csv_files:
        return 0

    try:
        with csv_files[0].open(newline="", encoding="utf-8") as file:
            return sum(1 for _ in csv.DictReader(file))
    except Exception:
        return 0


def render_summary_card(module, label, value, caption):
    return (
        '<div class="summary-card">'
        f'{get_module_icon_html(module, "summary-icon", label)}'
        '<div>'
        f'<p class="summary-label">{html.escape(label)}</p>'
        f'<p class="summary-value">{html.escape(str(value))}</p>'
        f'<p class="summary-caption">{html.escape(caption)}</p>'
        '</div>'
        '</div>'
    )


def render_workspace_overview(current_module):
    _, current_index = get_workflow_position(current_module)
    completion_percent = int(((current_index + 1) / len(workflow_module_list)) * 100) if workflow_module_list else 0
    cards = [
        render_summary_card("Medicines", t("summary_medicines"), count_latest_csv_rows("module_06_medicines"), t("summary_medicines_caption")),
        render_summary_card("Dosage", t("summary_dosage"), count_latest_csv_rows("module_07_dosage"), t("summary_dosage_caption")),
        render_summary_card("Interactions", t("summary_interactions"), count_latest_csv_rows("module_09_interactions"), t("summary_interactions_caption")),
        render_summary_card("Recommendations", t("summary_recommendations"), count_latest_csv_rows("module_10_recommendations"), t("summary_recommendations_caption")),
        render_summary_card("Dashboard", t("summary_completed"), f"{completion_percent}%", t("summary_completed_caption")),
    ]
    st.markdown(
        f"""
        <section class="workspace-overview">
            <div class="workspace-topline">
                <div class="workspace-title">
                    <h1>AI Prescription Reader &amp; Medicine Intelligence System</h1>
                    <p>Understand your prescription in a better way with AI. Current workspace: {html.escape(current_module)}</p>
                </div>
                <a class="workspace-action" href="?nav=Upload" target="_self" onclick="window.parent.location.href=this.href; return false;">Upload New</a>
            </div>
            <div class="summary-card-grid">
                {''.join(cards)}
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


nav_items_html = "".join(
    (
        f'<a class="top-nav-button{" active" if option == selected else ""}" '
        f'href="?nav={html.escape(option, quote=True)}" target="_self" '
        f'onclick="window.parent.location.href=this.href; return false;">'
        f'<span>{get_top_nav_icon_html(option)}{html.escape(option)}</span>'
        '</a>'
    )
    for option in module_list
)
st.markdown(
    f'<nav class="top-nav-button-panel" aria-label="Main navigation">'
    f'<div class="top-nav-button-row">{nav_items_html}</div>'
    f'</nav>',
    unsafe_allow_html=True
)

selected = get_current_module()

login_col1, language_col, login_col2, login_col3 = st.columns([2, 1, 1, 1])

with login_col1:
    if not st.session_state.logged_in:
        st.info("Login to store prescriptions and reports under your name.")
    else:
        st.markdown(f"**Signed in as:** {st.session_state.username}")

with language_col:
    st.selectbox(
        "Language",
        options=list(LANGUAGE_OPTIONS.keys()),
        format_func=lambda value: LANGUAGE_OPTIONS[value],
        key="language",
    )

with login_col2:
    if st.session_state.logged_in:
        st.button("Logout", key="logout_button", use_container_width=True, on_click=logout_user)
    else:
        if st.button("Login", key="login_button", use_container_width=True):
            st.session_state.show_login_dialog = True
            rerun_app()

with login_col3:
    st.button("Clear All Output", key="clear_output_button", use_container_width=True, on_click=clear_all_output)

if "clear_all_status" in st.session_state:
    st.success(st.session_state["clear_all_status"])

if selected != "Home":
    render_workspace_overview(selected)

if selected == "Home":
    st.markdown("---")

    hero_logo_html = (
        f'<img class="hero-title-logo" src="{PROJECT_LOGO_IMAGE_URL}" alt="">'
        if PROJECT_LOGO_IMAGE_URL
        else ""
    )
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">HERO_LOGO Medicine Prescription Analysis Platform</h1>
        <p class="hero-subtitle">Advanced AI-powered medicine intelligence and prescription analysis system</p>
    </div>
    """.replace("HERO_LOGO", hero_logo_html), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""<div class="stat-box"><p class="stat-number">24/7</p><p class="stat-label">Database Access</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="stat-box"><p class="stat-number">MongoDB</p><p class="stat-label">Cloud Storage</p></div>""", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="medical-disclaimer">
            <div>
                <strong>Medical Disclaimer</strong>
                <p>
                    This AI Prescription Reader is designed to assist with prescription text extraction and medicine information only.
                    It is not a substitute for professional medical advice, diagnosis, or treatment. Always confirm medicines,
                    dosage, interactions, and recommendations with a licensed doctor or pharmacist before making health decisions.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    with st.expander("User Guide", expanded=False):
        toggle_col1, toggle_col2 = st.columns(2)
        with toggle_col1:
            st.session_state.show_features = st.checkbox(
                "Show Key Features",
                value=st.session_state.show_features,
                key="show_features_checkbox",
                help="Toggle visibility of the key features section."
            )
        with toggle_col2:
            st.session_state.show_workflow = st.checkbox(
                "Show Application Workflow",
                value=st.session_state.show_workflow,
                key="show_workflow_checkbox",
                help="Toggle visibility of the workflow section."
            )

    if st.session_state.show_features:
        st.markdown("""<h2 style="color: #667eea; text-align: center; margin-top: 2rem;">Key Features</h2>""", unsafe_allow_html=True)
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        with feature_col1:
            st.markdown(f"""<div class="feature-item">{get_module_icon_html("Preprocessing", "feature-icon", "Image processing")}<h3 class="feature-title">Image Processing</h3><p class="feature-text">Advanced preprocessing and enhancement of prescription images</p></div>""", unsafe_allow_html=True)
        with feature_col2:
            st.markdown(f"""<div class="feature-item">{get_module_icon_html("OCR", "feature-icon", "OCR technology")}<h3 class="feature-title">OCR Technology</h3><p class="feature-text">Accurate text extraction using state-of-the-art OCR engines</p></div>""", unsafe_allow_html=True)
        with feature_col3:
            st.markdown(f"""<div class="feature-item">{get_module_icon_html("Medicines", "feature-icon", "AI medicine analysis")}<h3 class="feature-title">AI Analysis</h3><p class="feature-text">Intelligent medicine detection and interaction analysis</p></div>""", unsafe_allow_html=True)

    if st.session_state.show_features or st.session_state.show_workflow:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    if st.session_state.show_workflow:
        st.markdown("""<h2 style="color: #667eea; text-align: center; margin-top: 2rem;">Application Workflow</h2>""", unsafe_allow_html=True)
        workflow_steps = [
            ("Upload", "Upload Prescription", "Upload a clear image of your prescription document"),
            ("Preprocessing", "Image Processing", "Enhance and preprocess the image for better accuracy"),
            ("OCR", "Text Extraction", "Extract text using advanced OCR technology"),
            ("Medicines", "Medicine Detection", "Identify and analyze all medicines in the prescription"),
            ("Dosage", "Dosage Analysis", "Extract dosage information and timing details"),
            ("Interactions", "Safety Check", "Check for drug interactions and contraindications"),
            ("Recommendations", "Recommendations", "Get personalized health recommendations"),
            ("Database", "Database Storage", "Store results securely in MongoDB cloud database"),
        ]
        workflow_html = "".join(
            f'<div class="workflow-step">{get_module_icon_html(module, "step-icon", title)}'
            f'<div class="step-content"><h3 class="step-title">{html.escape(title)}</h3>'
            f'<p class="step-description">{html.escape(description)}</p></div></div>'
            for module, title, description in workflow_steps
        )
        st.markdown(workflow_html, unsafe_allow_html=True)

    render_bottom_navigation(selected)
    st.stop()

st.markdown("---")

module_map = {
    "Upload": ("module_03_upload", "show_module_03_upload"),
    "Preprocessing": ("module_04_preprocessing", "show_module_04_preprocessing"),
    "OCR": ("module_05_ocr", "show_module_05_ocr"),
    "Medicines": ("module_06_medicine_detection", "show_module_06_medicine_detection"),
    "Dosage": ("module_07_dosage_extraction", "show_module_07_dosage_extraction"),
    "Benefits": ("module_08_benefits", "show_module_08_benefits"),
    "Interactions": ("module_09_interactions", "show_module_09_interactions"),
    "Recommendations": ("module_10_recommendations", "show_module_10_recommendations"),
    "Dashboard": ("module_11_dashboard", "show_module_11_dashboard"),
    "Database": ("module_12_database_storage", "show_module_12_database_storage"),
}


@st.cache_resource(show_spinner=False)
def get_module_function(module_name):
    if module_name not in module_map:
        raise ValueError(f"Unknown module: {module_name}")

    module_file, func_name = module_map[module_name]
    module = importlib.import_module(f"modules.{module_file}")

    if not hasattr(module, func_name):
        raise AttributeError(f"Module '{module_file}' does not define '{func_name}'")

    return getattr(module, func_name)


# Get current selected module from session state
current_module = get_current_module()

# Display current module
if current_module in module_map:
    module_icon_html = get_module_icon_html(current_module, "module-card-icon", current_module)
    # Add module header card
    st.markdown(f"""
    <div class="professional-card">
        <div class="card-header">
            {module_icon_html}
            <div style="flex: 1;">
                <h3 class="card-title">{current_module}</h3>
                <p class="card-subtitle">Processing and analysis in progress...</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    get_module_function(current_module)()
    render_bottom_navigation(current_module)
