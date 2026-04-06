import streamlit as st
import requests
import json
from datetime import datetime
import base64
import io

# Page configuration
st.set_page_config(
    page_title="Gemini Interview Q&A Generator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .qa-container {
        background-color: #f8f9fa;
        border-left: 4px solid #0066cc;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .qa-topic {
        color: #0066cc;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .qa-question {
        color: #333;
        font-weight: 600;
        margin: 1rem 0 0.5rem 0;
        font-size: 1rem;
    }
    .qa-answer {
        color: #555;
        margin: 0.5rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .results-counter {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: bold;
        color: #0066cc;
    }
    .pii-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .pii-content {
        color: #856404;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8001"


def check_api_health():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def process_resume(file, num_questions: int):
    """Call FastAPI to process resume and generate Q&A"""
    try:
        with st.spinner("📤 Processing resume and generating questions..."):
            files = {"file": (file.name, file.getbuffer(), "application/octet-stream")}
            params = {"num_questions": num_questions}
            
            response = requests.post(
                f"{API_URL}/api/process-resume",
                files=files,
                params=params,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            return data, None
        else:
            error_detail = response.json().get("detail", f"Status {response.status_code}")
            return None, error_detail
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        return None, f"Error: {str(e)}"


def generate_qa_from_text(experience: str, num_questions: int):
    """Call FastAPI to generate Q&A from text input"""
    try:
        payload = {
            "candidate_experience": experience,
            "num_questions": num_questions
        }
        
        with st.spinner("🔄 Generating interview questions..."):
            response = requests.post(
                f"{API_URL}/api/generate",
                json=payload,
                timeout=60
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                raw_qa = data.get("data", "")
                # Parse raw QA into structured format
                qa_items = parse_qa_response(raw_qa)
                return qa_items, None
            else:
                return None, data.get("error", "Unknown error occurred")
        else:
            return None, f"API Error: {response.status_code}"
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        return None, f"Error: {str(e)}"


def parse_qa_response(response_text: str) -> list:
    """Parse Q&A response into structured list"""
    import re
    qa_items = []
    
    if not response_text:
        return qa_items
    
    # Try JSON pattern first
    json_pattern = r'\{[^{}]*"Topic"[^{}]*"Question"[^{}]*"Answer"[^{}]*\}'
    matches = re.finditer(json_pattern, response_text, re.DOTALL)
    
    for match in matches:
        try:
            json_str = match.group(0).replace('\n', ' ')
            qa_data = json.loads(json_str)
            if all(key in qa_data for key in ['Topic', 'Question', 'Answer']):
                qa_items.append({
                    'Topic': str(qa_data['Topic']).strip(),
                    'Question': str(qa_data['Question']).strip(),
                    'Answer': str(qa_data['Answer']).strip()
                })
        except json.JSONDecodeError:
            continue
    
    return qa_items


def download_excel(qa_items: list, candidate_name: str = ""):
    """Convert QA items to Excel file"""
    try:
        qa_json = json.dumps(qa_items)
        
        with st.spinner("⏳ Generating Excel file..."):
            params = {"candidate_name": candidate_name}
            response = requests.post(
                f"{API_URL}/api/download-excel",
                data={"qa_items_json": qa_json},
                params=params if candidate_name else {},
                timeout=30
            )
        
        if response.status_code == 200:
            return response.content, None
        else:
            return None, "Failed to generate Excel file"
    except Exception as e:
        return None, f"Error: {str(e)}"


def display_qa_results(qa_items: list):
    """Display Q&A results in a user-friendly format"""
    if not qa_items:
        st.warning("No Q&A items to display")
        return
    
    # Results summary
    st.markdown(f"""
    <div class="results-counter">
        📊 Total Questions: {len(qa_items)} | Successfully Generated ✓
    </div>
    """, unsafe_allow_html=True)
    
    # Display each Q&A in an expander
    for idx, qa in enumerate(qa_items, 1):
        topic = qa.get("Topic", "Interview Q&A")
        question = qa.get("Question", "")
        answer = qa.get("Answer", "")
        
        with st.expander(f"**Q{idx}** | {topic}", expanded=(idx <= 3)):
            st.markdown(f"""
            <div class="qa-container">
                <div class="qa-topic">📌 Topic: {topic}</div>
                <div class="qa-question">❓ Question:</div>
                <div class="qa-answer">{question}</div>
                <div class="qa-question">✅ Answer:</div>
                <div class="qa-answer">{answer}</div>
            </div>
            """, unsafe_allow_html=True)


# Main app
def main():
    # Header
    st.title("🤖 Gemini Interview Q&A Generator")
    st.markdown("Generate comprehensive interview questions from resumes using Google Gemini AI")
    
    # Check API connection
    if not check_api_health():
        st.error("❌ **FastAPI Backend Not Running**\n\nPlease ensure the FastAPI backend is running at `http://localhost:8001`")
        st.info("Run the backend with: `python -m uvicorn backend.main:app --port 8001` from the project directory")
        st.stop()
    else:
        st.success("✓ Backend connected")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("---")
        
        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=100,
            value=30,
            step=5,
            help="Total number of interview questions to generate"
        )
        
        st.markdown("---")
        st.markdown("### 📋 Features")
        st.markdown("""
        ✓ **Resume Parsing** - PDF & DOCX support
        ✓ **PII Redaction** - Protects sensitive data
        ✓ **Excel Export** - Professional formatted output
        ✓ **AI-Powered** - Google Gemini 2.5 Flash
        """)
    
    # Main content - Tabs for different input methods
    tab1, tab2 = st.tabs(["📝 Text Input", "📄 Resume Upload"])
    
    with tab1:
        st.subheader("Enter Candidate Experience")
        
        # Example text
        with st.expander("📌 See example format"):
            st.text("""Python, PySpark, pandas, numpy, data analysis, MySQL, SQL,
matplotlib, data profiling, data governance, ETL, Apache Spark,
statistics, machine learning, Tableau, Power BI""")
        
        candidate_experience = st.text_area(
            "Candidate Experience & Skills",
            placeholder="Enter candidate's tools, languages, and experience...",
            height=150,
            help="Comma-separated list of technologies, tools, and skills"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🚀 Generate Q&A", use_container_width=True, key="generate_text"):
                if candidate_experience.strip():
                    qa_items, error = generate_qa_from_text(candidate_experience, num_questions)
                    
                    if qa_items:
                        st.session_state.last_qa_items = qa_items
                        st.session_state.last_candidate_name = "Candidate"
                        st.markdown("### ✅ Generated Interview Q&A")
                        display_qa_results(qa_items)
                        
                        # Download options
                        col_excel, col_txt = st.columns([1, 1])
                        
                        with col_excel:
                            excel_data, excel_error = download_excel(qa_items, "Candidate")
                            if excel_data:
                                st.download_button(
                                    label="📊 Download as Excel",
                                    data=excel_data,
                                    file_name=f"interview_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                    else:
                        st.error(f"❌ Error: {error}")
                else:
                    st.warning("⚠️ Please enter candidate experience")
        
        with col2:
            st.info("💡 **Tip:** Be specific about tools and experience levels for better questions")
    
    with tab2:
        st.subheader("Upload & Process Resume")
        st.markdown("Supported formats: **PDF** and **Word (.docx)**")
        
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=["pdf", "docx"],
            help="Upload your resume in PDF or DOCX format"
        )
        
        if uploaded_file:
            st.success(f"✓ File selected: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🚀 Process & Generate Q&A", use_container_width=True, key="generate_resume"):
                    result, error = process_resume(uploaded_file, num_questions)
                    
                    if result and result.get("status") == "success":
                        # Store for later use
                        st.session_state.last_qa_items = result.get("qa_items", [])
                        st.session_state.last_candidate_name = Path(uploaded_file.name).stem
                        
                        # Show PII warning if detected
                        if result.get("pii_detected"):
                            st.markdown(f"""
                            <div class="pii-warning">
                                <div class="pii-content">
                                <strong>🔒 PII Detection Report:</strong><br>
                                ✓ PII has been detected and removed before sending to AI<br>
                                • Emails found: {len(result.get('pii_summary', {}).get('emails', []))}<br>
                                • Phone numbers found: {len(result.get('pii_summary', {}).get('phone_numbers', []))}<br>
                                • URLs found: {len(result.get('pii_summary', {}).get('urls', []))}<br>
                                <br>
                                Your sensitive information is protected! Only skills and experience are sent to AI.
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("### ✅ Generated Interview Q&A")
                        qa_items = result.get("qa_items", [])
                        
                        if qa_items:
                            display_qa_results(qa_items)
                            
                            # Summary
                            col_info1, col_info2, col_info3 = st.columns(3)
                            with col_info1:
                                st.metric("Questions Generated", len(qa_items))
                            with col_info2:
                                st.metric("File Type", result.get("file_type", "").upper())
                            with col_info3:
                                st.metric("Text Length", f"{result.get('extracted_text_length', 0)} chars")
                            
                            # Download options
                            col_excel, col_txt = st.columns([1, 1])
                            
                            with col_excel:
                                excel_data, excel_error = download_excel(qa_items, st.session_state.last_candidate_name)
                                if excel_data:
                                    st.download_button(
                                        label="📊 Download as Excel",
                                        data=excel_data,
                                        file_name=f"interview_qa_{st.session_state.last_candidate_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        use_container_width=True
                                    )
                            
                            with col_txt:
                                # Convert to text format
                                txt_content = "\n\n".join([
                                    f"Topic: {qa['Topic']}\n\nQuestion: {qa['Question']}\n\nAnswer: {qa['Answer']}"
                                    for qa in qa_items
                                ])
                                st.download_button(
                                    label="📄 Download as Text",
                                    data=txt_content,
                                    file_name=f"interview_qa_{st.session_state.last_candidate_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                        else:
                            st.warning("No Q&A items generated. Please check your resume content.")
                    else:
                        st.error(f"❌ Error: {error}")
            
            with col2:
                st.info("💡 **How it works:**\n1. Resume text is extracted\n2. Personal info (names, emails) is removed\n3. Skills are sent to AI for questions\n4. Results are formatted in Excel")
        else:
            st.info("👆 Upload a resume file (PDF or DOCX) to get started")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888;'>
    <small>Powered by Google Gemini 2.5 Flash | Built with Streamlit, FastAPI & Professional Resume Parsing</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # Initialize session state
    if "last_qa_items" not in st.session_state:
        st.session_state.last_qa_items = []
    if "last_candidate_name" not in st.session_state:
        st.session_state.last_candidate_name = ""
    
    from pathlib import Path
    main()
