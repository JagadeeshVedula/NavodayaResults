import streamlit as st
from supabase import create_client, Client
import time

# Page configuration
st.set_page_config(
    page_title="Navodaya Results Dashboard",
    page_icon="🎓",
    layout="centered"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #1E1E1E;
        text-align: center;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        width: 100%;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown('<h1 class="main-header">🎓 Navodaya Results Dashboard</h1>', unsafe_allow_html=True)

# Supabase Setup
# Using st.secrets is cleaner, but we want to fail gracefully if not set
try:
    supabase_url = "https://gscrjjtfawnudycbtqxl.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdzY3JqanRmYXdudWR5Y2J0cXhsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzI0NDYyOTQsImV4cCI6MjA0ODAyMjI5NH0.yQKItjeX1pYnjdah0zH4kKpT8ZkcpmHmDW1PKakRvFg"
except FileNotFoundError:
    st.error("Secrets not found. Please create `.streamlit/secrets.toml` with `SUPABASE_URL` and `SUPABASE_KEY`.")
    st.stop()
except KeyError:
    st.error("Supabase credentials missing in secrets. Please check keys `SUPABASE_URL` and `SUPABASE_KEY`.")
    st.stop()

@st.cache_resource
def init_connection():
    return create_client(supabase_url, supabase_key)

supabase = init_connection()

# Main Interface
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    roll_number = st.text_input("Enter Roll Number", placeholder="Type your RegNo here...", help="Enter the Registration Number.")
    phone_number = st.text_input("Enter Phone Number", placeholder="Type your Phone Number here...", help="Enter the Phone Number linked to the result.")
    
    submit_button = st.button("Search Result", type="primary")

if submit_button:
    if not roll_number or not phone_number:
        st.warning("⚠️ Please enter both Roll Number and Phone Number.")
    else:
        with st.spinner("Searching Supabase database..."):
            try:
                # Query Result for User matching both RegNo and Phone
                # Note: 'Phone' and 'Total' column names are assumed based on requirements. 
                # Adjust if actual column names in Supabase differ.
                user_response = supabase.table("Navodaya_Results").select("*").eq("RegNo", roll_number).eq("Phone", phone_number).execute()
                
                if user_response.data:
                    result = user_response.data[0]
                    user_total = result.get('Total')
                    
                    # Logic to check for Prize Money (Highest and 2nd Highest Total)
                    # We fetch the top distinct totals to determine rank
                    prize_message = None
                    if user_total is not None:
                        # Fetch top distinct totals
                        rank_response = supabase.table("Navodaya_Results").select("Total").order("Total", desc=True).limit(20).execute()
                        if rank_response.data:
                            # Get unique totals sorted descending
                            unique_totals = sorted(list(set([item['Total'] for item in rank_response.data if item['Total'] is not None])), reverse=True)
                            
                            if len(unique_totals) > 0 and user_total == unique_totals[0]:
                                prize_message = {
                                    "amount": "5000/-",
                                    "msg": "Congratulations! You have secured the 1st highest total."
                                }
                            elif len(unique_totals) > 1 and user_total == unique_totals[1]:
                                prize_message = {
                                    "amount": "3000/-",
                                    "msg": "Congratulations! You have secured the 2nd highest total."
                                }

                    st.success("Result found!")
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    
                    # Display Prize Section if eligible
                    if prize_message:
                        st.balloons()
                        st.markdown(f"""
                        <div style="background-color: #d1e7dd; color: #0f5132; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; border: 1px solid #badbcc; text-align: center;">
                            <h2 style="margin-top: 0;">🎉 {prize_message['msg']} 🎉</h2>
                            <h1 style="color: #198754; font-size: 3rem; margin: 1rem 0;">₹ {prize_message['amount']}</h1>
                            <p style="font-size: 1.2rem; font-weight: bold;">Please collect your amount from <span style="color: #0d6efd;">Dakshinamurty Tution Center</span>.</p>
                        </div>
                        """, unsafe_allow_html=True)

                    st.subheader("Student Details")
                    
                    # Displaying data cleanly, excluding 'id'
                    for key, value in result.items():
                        if key.lower() != 'id': # Exclude 'id' (case-insensitive check)
                            formatted_key = key.replace('_', ' ').title()
                            st.markdown(f"**{formatted_key}:** {value}")
                        
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("No results found matching those details. Please check Roll Number and Phone Number.")
                    
            except Exception as e:
                st.error(f"An error occurred while fetching data: {e}")

st.markdown("---")
st.caption("Powered by Streamlit & Supabase")
