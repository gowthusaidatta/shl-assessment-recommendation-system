"""
Simple Streamlit frontend for SHL Assessment Recommendations.
"""
import streamlit as st
import requests
import pandas as pd

# Page config
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide"
)

# Title
st.title("🎯 SHL Assessment Recommendation System")
st.markdown("Find the perfect SHL assessments for your hiring needs")

# Sidebar
st.sidebar.header("About")
st.sidebar.info(
    "This system uses AI-powered Retrieval-Augmented Generation (RAG) "
    "to recommend relevant SHL Individual Test Solutions based on your job requirements."
)

# API endpoint
API_URL = st.sidebar.text_input(
    "API Endpoint",
    value="http://localhost:8000",
    help="URL of the recommendation API"
)

# Main interface
st.header("Enter Your Job Requirements")

query = st.text_area(
    "Job Description or Query",
    height=150,
    placeholder="Example: I am hiring for Java developers who can collaborate effectively with business teams...",
    help="Describe the role you're hiring for, including technical skills, soft skills, and any specific requirements."
)

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("🔍 Get Recommendations", type="primary"):
        if not query or len(query) < 10:
            st.error("Please enter a query with at least 10 characters")
        else:
            with st.spinner("Analyzing your requirements and finding the best assessments..."):
                try:
                    # Call API
                    response = requests.post(
                        f"{API_URL}/recommend",
                        json={"text": query},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        recommendations = data["recommendations"]
                        
                        st.success(f"Found {len(recommendations)} recommended assessments!")
                        
                        # Display recommendations
                        st.header("📊 Recommended Assessments")
                        
                        for i, rec in enumerate(recommendations, 1):
                            with st.expander(f"{i}. {rec['assessment_name']} (Score: {rec['score']:.2f})"):
                                st.markdown(f"**URL:** [{rec['url']}]({rec['url']})")
                                st.markdown(f"**Relevance Score:** {rec['score']:.4f}")
                        
                        # Download as CSV
                        df = pd.DataFrame(recommendations)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name="shl_recommendations.csv",
                            mime="text/csv"
                        )
                    
                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to API. Make sure the server is running.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with col2:
    if st.button("Clear"):
        st.rerun()

# Examples
st.header("💡 Example Queries")
examples = [
    "I am hiring for Java developers who can also collaborate effectively with my business teams.",
    "Looking to hire mid-level professionals who are proficient in Python, SQL and JavaScript.",
    "I need cognitive and personality tests for analyst positions.",
    "Hiring sales representatives with strong communication and negotiation skills.",
    "Need assessments for entry-level software engineers with problem-solving abilities."
]

for example in examples:
    if st.button(f"Try: {example[:70]}...", key=example):
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "**SHL Assessment Recommendation System** | "
    "Built with FastAPI, Sentence-Transformers & FAISS"
)
