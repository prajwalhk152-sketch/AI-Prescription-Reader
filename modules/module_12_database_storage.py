import streamlit as st
import pandas as pd
import os
from datetime import datetime
from bson import ObjectId
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.mongodb_manager import get_mongo_manager

REPORT_DIR = "outputs/module_12_database_storage"

os.makedirs(REPORT_DIR, exist_ok=True)


def serialize_document(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, list):
        return [serialize_document(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_document(item) for key, item in value.items()}
    return value


def summarize_document(document):
    summary = {}
    for key, value in document.items():
        if isinstance(value, list):
            summary[key] = f"{len(value)} item(s)"
        elif isinstance(value, dict):
            summary[key] = f"{len(value)} field(s)"
        else:
            summary[key] = value
    return summary


def readable_label(key):
    return key.replace("_", " ").title()


def render_simple_value(label, value):
    if value in (None, "", [], {}):
        st.write(f"**{label}:** Not available")
    elif isinstance(value, list):
        st.write(f"**{label}:** {len(value)} item(s)")
    elif isinstance(value, dict):
        st.write(f"**{label}:** {len(value)} detail(s)")
    else:
        st.write(f"**{label}:** {value}")


def render_list_section(title, items):
    st.markdown(f"**{title}**")

    if not items:
        st.info(f"No {title.lower()} saved for this record.")
        return

    if all(isinstance(item, dict) for item in items):
        st.dataframe(pd.DataFrame(items), use_container_width=True)
    else:
        for item in items:
            st.write(f"- {item}")


def render_dict_section(title, details):
    st.markdown(f"**{title}**")

    if not details:
        st.info(f"No {title.lower()} saved for this record.")
        return

    for key, value in details.items():
        render_simple_value(readable_label(key), value)


def render_record_in_simple_english(document, collection_name):
    if collection_name == "prescriptions":
        render_simple_value("Prescription ID", document.get("_id"))
        render_simple_value("User Name", document.get("user_id"))
        render_simple_value("Prescription File", document.get("file_name"))
        render_simple_value("Created On", document.get("created_at"))
        render_simple_value("Updated On", document.get("updated_at"))

        st.markdown("---")
        render_list_section("Detected Medicines", document.get("medicines", []))
        render_list_section("Dosage Information", document.get("dosage", []))
        render_list_section("Medicine Benefits", document.get("benefits", []))
        render_list_section("Drug Interactions", document.get("interactions", []))
        render_list_section("Recommendations", document.get("recommendations", []))

        ocr_text = document.get("ocr_text", "")
        if ocr_text:
            st.markdown("**Extracted Prescription Text**")
            st.write(ocr_text)

        render_dict_section("Other Details", document.get("metadata", {}))
        return

    if collection_name == "reports":
        render_simple_value("Report ID", document.get("_id"))
        render_simple_value("User Name", document.get("user_id"))
        render_simple_value("Prescription ID", document.get("prescription_id"))
        render_simple_value("Created On", document.get("created_at"))
        render_dict_section("Report Details", document.get("report_data", {}))
        return

    if collection_name == "medicines":
        for key, value in document.items():
            render_simple_value(readable_label(key), value)
        return

    for key, value in document.items():
        if isinstance(value, list):
            render_list_section(readable_label(key), value)
        elif isinstance(value, dict):
            render_dict_section(readable_label(key), value)
        else:
            render_simple_value(readable_label(key), value)


def latest_csv(folder):
    if not os.path.exists(folder):
        return None

    files = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith(".csv")
    ]

    if not files:
        return None

    return max(files, key=os.path.getctime)


def get_login_user():
    username = st.session_state.get("username", "").strip()
    if st.session_state.get("logged_in") and username:
        return username
    return ""


def require_login_user():
    login_user = get_login_user()
    if login_user:
        return login_user

    st.warning("Please login first. Stored prescriptions and reports are saved under the logged-in user name.")
    return ""


def generate_pdf(pdf_path,
                 medicines_df,
                 dosage_df,
                 benefits_df,
                 interactions_df,
                 recommendations_df):

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "AI Prescription Reader & Medicine Intelligence System",
            styles['Title']
        )
    )

    elements.append(
        Paragraph(
            "Final Patient Analysis Report",
            styles['Heading2']
        )
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated On: {datetime.now()}",
            styles['Normal']
        )
    )

    elements.append(PageBreak())

    elements.append(
        Paragraph("Detected Medicines", styles['Heading1'])
    )

    if medicines_df is not None:
        for _, row in medicines_df.iterrows():
            elements.append(
                Paragraph(
                    f"{row['medicine_name']} - {row['category']}",
                    styles['Normal']
                )
            )

    elements.append(PageBreak())

    elements.append(
        Paragraph("Dosage Information", styles['Heading1'])
    )

    if dosage_df is not None:
        for _, row in dosage_df.iterrows():
            elements.append(
                Paragraph(
                    str(row.to_dict()),
                    styles['Normal']
                )
            )

    elements.append(PageBreak())

    elements.append(
        Paragraph("Medicine Benefits", styles['Heading1'])
    )

    if benefits_df is not None:
        for _, row in benefits_df.iterrows():
            elements.append(
                Paragraph(
                    str(row.to_dict()),
                    styles['Normal']
                )
            )

    elements.append(PageBreak())

    elements.append(
        Paragraph("Drug Interactions", styles['Heading1'])
    )

    if interactions_df is not None:
        for _, row in interactions_df.iterrows():
            elements.append(
                Paragraph(
                    str(row.to_dict()),
                    styles['Normal']
                )
            )

    elements.append(PageBreak())

    elements.append(
        Paragraph("Recommendations", styles['Heading1'])
    )

    if recommendations_df is not None:
        for _, row in recommendations_df.iterrows():
            elements.append(
                Paragraph(
                    str(row.to_dict()),
                    styles['Normal']
                )
            )

    doc.build(elements)
def show_module_12_database_storage():

    st.title("Database Storage & Report Generation")

    login_user = require_login_user()
    if not login_user:
        return

    st.info(f"Database records will be stored and searched for: **{login_user}**")

    # Tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Store Analysis", 
        "View Prescriptions", 
        "View Stored Data",
        "Generate Report",
        "Database Statistics"
    ])

    # Initialize MongoDB connection
    try:
        db_manager = get_mongo_manager()
        st.success("Connected to MongoDB")
    except Exception as e:
        st.error(f"MongoDB Connection Error: {e}")
        st.info("Ensure MongoDB is running locally or check .env configuration")
        return

    # TAB 1: Store Prescription Analysis
    with tab1:
        st.header("Store Prescription Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_id = st.text_input(
                "Login User",
                value=login_user,
                disabled=True,
                help="Records are saved under the current logged-in user name."
            )
            file_name = st.text_input(
                "Prescription File Name",
                value="prescription_001.jpg",
                help="Original prescription file name"
            )
        
        with col2:
            st.write("")
            st.write("")
            store_button = st.button(
                "Store Analysis to MongoDB",
                key="store_analysis"
            )
        
        if store_button:
            # Load data from CSV outputs
            medicine_csv = latest_csv("outputs/module_06_medicines")
            dosage_csv = latest_csv("outputs/module_07_dosage")
            benefits_csv = latest_csv("outputs/module_08_benefits")
            interaction_csv = latest_csv("outputs/module_09_interactions")
            recommendation_csv = latest_csv("outputs/module_10_recommendations")
            
            # Load OCR text if available
            ocr_files = []
            ocr_dir = "outputs/module_05_ocr"
            if os.path.exists(ocr_dir):
                ocr_files = [f for f in os.listdir(ocr_dir) if f.endswith("_text.txt")]
            
            ocr_text = ""
            if ocr_files:
                with open(os.path.join(ocr_dir, ocr_files[-1]), 'r') as f:
                    ocr_text = f.read()
            
            # Convert DataFrames to dictionaries
            medicines = []
            dosage = []
            benefits = []
            interactions = []
            recommendations = []
            
            if medicine_csv:
                medicines = pd.read_csv(medicine_csv).to_dict('records')
            if dosage_csv:
                dosage = pd.read_csv(dosage_csv).to_dict('records')
            if benefits_csv:
                benefits = pd.read_csv(benefits_csv).to_dict('records')
            if interaction_csv:
                interactions = pd.read_csv(interaction_csv).to_dict('records')
            if recommendation_csv:
                recommendations = pd.read_csv(recommendation_csv).to_dict('records')
            
            # Store in MongoDB
            prescription_id = db_manager.store_prescription_analysis(
                user_id=user_id,
                file_name=file_name,
                medicines=medicines,
                dosage=dosage,
                benefits=benefits,
                interactions=interactions,
                recommendations=recommendations,
                ocr_text=ocr_text,
                metadata={
                    "analysis_date": datetime.now().isoformat(),
                    "login_user": login_user,
                    "modules_used": [6, 7, 8, 9, 10]
                }
            )
            
            if prescription_id:
                st.success("Prescription stored successfully.")
                st.info(f"Prescription ID: `{prescription_id}`")
                st.json({
                    "user_id": user_id,
                    "prescription_id": prescription_id,
                    "medicines_count": len(medicines),
                    "stored_at": datetime.now().isoformat()
                })
            else:
                st.error("Failed to store prescription analysis")

    # TAB 2: View Prescriptions
    with tab2:
        st.header("View User Prescriptions")
        
        user_id = st.text_input(
            "Logged-in user",
            value=login_user,
            disabled=True,
            key="view_user_id"
        )
        
        if st.button("Retrieve Prescriptions", key="retrieve_button"):
            prescriptions = db_manager.get_user_prescriptions(user_id, limit=10)
            
            if prescriptions:
                st.success(f"Found {len(prescriptions)} prescription(s)")
                
                for idx, prescription in enumerate(prescriptions, 1):
                    with st.expander(
                        f"Prescription {idx}: {prescription['file_name']} "
                        f"({prescription['created_at'].strftime('%Y-%m-%d %H:%M')})"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Detected Medicines")
                            if prescription['medicines']:
                                medicines_df = pd.DataFrame(prescription['medicines'])
                                st.dataframe(medicines_df, use_container_width=True)
                            else:
                                st.info("No medicines detected")
                            
                            st.subheader("Dosage Information")
                            if prescription['dosage']:
                                dosage_df = pd.DataFrame(prescription['dosage'])
                                st.dataframe(dosage_df, use_container_width=True)
                            else:
                                st.info("No dosage information")
                        
                        with col2:
                            st.subheader("Benefits")
                            if prescription['benefits']:
                                benefits_df = pd.DataFrame(prescription['benefits'])
                                st.dataframe(benefits_df, use_container_width=True)
                            else:
                                st.info("No benefits found")
                            
                            st.subheader("Interactions")
                            if prescription['interactions']:
                                interactions_df = pd.DataFrame(prescription['interactions'])
                                st.dataframe(interactions_df, use_container_width=True)
                            else:
                                st.info("No interactions found")
                        
                        # Delete button
                        if st.button(
                            "Delete this prescription",
                            key=f"delete_{prescription['_id']}"
                        ):
                            if db_manager.delete_prescription(prescription['_id']):
                                st.success("Prescription deleted successfully")
                                st.rerun()
                            else:
                                st.error("Failed to delete prescription")
            else:
                st.warning(f"No prescriptions found for user: {user_id}")

    # TAB 3: View Stored Data
    with tab3:
        st.header("View Stored Data")

        collections = ["prescriptions", "medicines", "reports"]
        selected_collection = st.selectbox(
            "Select collection",
            collections,
            key="stored_data_collection"
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            limit = st.number_input(
                "Records to show",
                min_value=1,
                max_value=100,
                value=10,
                step=1,
                key="stored_data_limit"
            )
        with col2:
            sort_order = st.selectbox(
                "Sort order",
                ["Newest first", "Oldest first"],
                key="stored_data_sort_order"
            )

        sort_direction = -1 if sort_order == "Newest first" else 1

        if st.button("View Stored Data", key="view_stored_data_button"):
            collection = db_manager.db[selected_collection]
            query = (
                {"user_id": login_user}
                if selected_collection in {"prescriptions", "reports"}
                else {}
            )
            documents = list(
                collection.find(query)
                .sort("created_at", sort_direction)
                .limit(int(limit))
            )

            if not documents:
                st.warning(f"No records found in `{selected_collection}`.")
            else:
                clean_documents = [serialize_document(doc) for doc in documents]
                summary_rows = [summarize_document(doc) for doc in clean_documents]

                st.success(f"Showing {len(clean_documents)} record(s) from `{selected_collection}`")
                st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

                st.subheader("Record Details")
                for index, document in enumerate(clean_documents, 1):
                    title = document.get("file_name") or document.get("name") or document.get("_id")
                    created_at = document.get("created_at", "No date")
                    with st.expander(f"Record {index}: {title} | {created_at}"):
                        render_record_in_simple_english(document, selected_collection)

    # TAB 4: Generate Report
    with tab4:
        st.header("Generate PDF Report")
        
        user_id = st.text_input(
            "Logged-in user for PDF report",
            value=login_user,
            disabled=True,
            key="pdf_user_id"
        )
        
        if st.button("Generate PDF Report", key="generate_pdf_button"):
            prescriptions = db_manager.get_user_prescriptions(user_id, limit=1)
            
            if prescriptions:
                prescription = prescriptions[0]
                
                medicines_df = pd.DataFrame(prescription['medicines']) if prescription['medicines'] else None
                dosage_df = pd.DataFrame(prescription['dosage']) if prescription['dosage'] else None
                benefits_df = pd.DataFrame(prescription['benefits']) if prescription['benefits'] else None
                interactions_df = pd.DataFrame(prescription['interactions']) if prescription['interactions'] else None
                recommendations_df = pd.DataFrame(prescription['recommendations']) if prescription['recommendations'] else None
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_name = f"Prescription_Report_{user_id}_{timestamp}.pdf"
                pdf_path = os.path.join(REPORT_DIR, pdf_name)
                
                generate_pdf(
                    pdf_path,
                    medicines_df,
                    dosage_df,
                    benefits_df,
                    interactions_df,
                    recommendations_df
                )
                
                st.success("PDF report generated successfully.")
                
                with open(pdf_path, "rb") as pdf:
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf,
                        file_name=pdf_name,
                        mime="application/pdf"
                    )
                
                # Store report metadata in MongoDB
                report_id = db_manager.store_user_report(
                    user_id=user_id,
                    prescription_id=prescription['_id'],
                    report_data={
                        "pdf_file_name": pdf_name,
                        "pdf_path": pdf_path,
                        "login_user": login_user,
                        "generated_at": datetime.now().isoformat()
                    }
                )
                
                if report_id:
                    st.info(f"Report metadata stored: `{report_id}`")
            else:
                st.warning(f"No prescriptions found for user: {user_id}")

    # TAB 5: Database Statistics
    with tab5:
        st.header("Database Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            prescriptions_stats = db_manager.get_collection_stats("prescriptions")
            st.metric(
                "Total Prescriptions",
                prescriptions_stats.get("total_documents", 0)
            )
        
        with col2:
            medicines_stats = db_manager.get_collection_stats("medicines")
            st.metric(
                "Total Medicines",
                medicines_stats.get("total_documents", 0)
            )
        
        with col3:
            reports_stats = db_manager.get_collection_stats("reports")
            st.metric(
                "Total Reports",
                reports_stats.get("total_documents", 0)
            )
        
        st.subheader("Collection Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Prescriptions Collection**")
            st.json(prescriptions_stats)
        
        with col2:
            st.write("**Medicines Collection**")
            st.json(medicines_stats)
        
        st.write("**Reports Collection**")
        st.json(reports_stats)
        
        if st.button("Refresh Statistics"):
            st.rerun()
        
        st.subheader("MongoDB Connection Info")
        st.info(f"""
        **Database Name:** {db_manager.db_name}
        **Connection Status:** {'Connected' if db_manager.is_connected() else 'Disconnected'}
        **Server:** {db_manager.uri}
        """)
