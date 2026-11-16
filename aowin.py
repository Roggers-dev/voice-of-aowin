import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & GHANA THEME STYLING
# ==========================================
st.set_page_config(
    page_title="Aowin Constituency Pulse & Decision Engine",
    page_icon="🇬🇭",
    layout="wide"
)

st.markdown("""
<style>
    /* Global Ghana Theme Styling */
    .stApp { background-color: #090d16; color: #f8fafc; }
    
    /* Hide Streamlit Community Cloud Deploy Button, Toolbar, Footer & Manage App Badge */
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    #MainMenu { visibility: hidden !important; display: none !important; }
    .viewerBadge_container__1QSob { display: none !important; }
    .stDeployButton { visibility: hidden !important; display: none !important; }
    header { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }

    /* Custom Ghana Accent Banners & Boxes */
    .ghana-header {
        background: linear-gradient(90deg, #dc2626 0%, #facc15 50%, #16a34a 100%);
        padding: 4px;
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .decision-box {
        background-color: #111827;
        border-left: 6px solid #facc15;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #f3f4f6;
    }
    .alert-box {
        background-color: #111827;
        border-left: 6px solid #dc2626;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #f3f4f6;
    }
    .success-box {
        background-color: #111827;
        border-left: 6px solid #16a34a;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #f3f4f6;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECURE DATABASE & AUTO-MIGRATION
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('aowin_voter_pulse.db', check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            status TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aowin_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_name TEXT,
            electoral_zone TEXT,
            priority_issue TEXT,
            will_vote TEXT,
            reaction TEXT,
            reason TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    
    # Create default admin account if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'mp_admin'")
    if not cursor.fetchone():
        secure_pass = hash_password("Aowin2026!")
        cursor.execute("INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, ?)",
                       ("mp_admin", secure_pass, "admin", "approved"))
        conn.commit()
    conn.close()

init_db()

def run_query(query, params=()):
    conn = sqlite3.connect('aowin_voter_pulse.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

def save_response(name, zone, issue, vote, reaction, reason):
    conn = sqlite3.connect('aowin_voter_pulse.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO aowin_responses (voter_name, electoral_zone, priority_issue, will_vote, reaction, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, zone, issue, vote, reaction, reason, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def load_responses():
    conn = sqlite3.connect('aowin_voter_pulse.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM aowin_responses ORDER BY id DESC", conn)
    conn.close()
    return df

# ==========================================
# 3. AUTHENTICATION SESSION STATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "role" not in st.session_state:
    st.session_state["role"] = ""

# ==========================================
# 4. SIDEBAR & NAVIGATION SETUP
# ==========================================
st.sidebar.markdown("<h3 style='color: #facc15;'>🇬🇭 Aowin MP Portal</h3>", unsafe_allow_html=True)

if st.session_state["authenticated"]:
    st.sidebar.markdown(f"**Logged in:** `{st.session_state['username']}`")
    st.sidebar.markdown(f"**Role:** `{st.session_state['role'].upper()}`")
    if st.sidebar.button("🔒 Sign Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        st.session_state["role"] = ""
        st.rerun()
    st.sidebar.markdown("---")

nav_options = ["Constituent Feedback Form", "MP Decision & Intelligence Dashboard"]
nav_choice = st.sidebar.radio("Navigation", nav_options)

# Developer Branding in Sidebar with Gold Accent
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='text-align: center; color: #9ca3af; font-size: 12px;'>"
    "System Developed by <b style='color: #facc15;'>ROG3RS</b><br>Contact: <b style='color: #16a34a;'>0542470810</b>"
    "</p>", 
    unsafe_allow_html=True
)

# ==========================================
# 5. MODULE ROUTING & EXECUTION
# ==========================================

# ------------------------------------------
# VIEW A: CONSTITUENT FEEDBACK FORM (PUBLIC)
# ------------------------------------------
if nav_choice == "Constituent Feedback Form":
    st.markdown("<div class='ghana-header'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #facc15;'>🇬🇭 Aowin Constituency Voice Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af;'>Empowering Enchi and all Aowin communities through data-driven representation.</p>", unsafe_allow_html=True)
    
    with st.form("aowin_voter_form"):
        voter_name = st.text_input("Your Name (Optional - leave blank if anonymous)")
        
        electoral_zone = st.selectbox("Select Your Electoral Area / Zone in Aowin:", [
            "Enchi Central / Town Area",
            "Yiwabra / Yakasi Zone",
            "Boinso / Omanpe Zone",
            "Sewum / Jema Zone",
            "Elluousenu / Achimfo Zone",
            "Boisiah / Kramokrom Zone",
            "Other Aowin Communities"
        ])
        
        priority_issue = st.selectbox("What is your #1 development priority for Aowin?", [
            "Cocoa Roads & Feeder Roads Access",
            "Agricultural Inputs & Cocoa Farming Support",
            "Education & Youth Employment / Scholarships",
            "Healthcare Delivery & Hospital Access",
            "Water & Rural Electricity Extension"
        ])
        
        will_vote = st.radio("Will you vote for the current MP in the upcoming election?", [
            "Yes, absolutely 👍", 
            "Undecided / Need to see more progress 🤝", 
            "No, leaning toward alternative 👎"
        ])
        
        st.markdown("### React to our leadership performance:")
        reaction = st.radio("Choose your emoji reaction:", [
            "🔥 Very Satisfied", 
            "😊 Satisfied & Hopeful", 
            "😐 Neutral / Waiting", 
            "😡 Frustrated / Needs Urgent Action"
        ], horizontal=True)
        
        reason = st.text_area("Why? (Share your reasons, community challenges, or specific suggestions):")
        
        submit_btn = st.form_submit_button("Submit My Feedback to MP", use_container_width=True)
        
        if submit_btn:
            save_response(
                voter_name if voter_name else "Anonymous Constituent", 
                electoral_zone, 
                priority_issue, 
                will_vote, 
                reaction, 
                reason
            )
            st.success("✅ Aseda! Your feedback has been securely registered to help improve development across Aowin.")

# ------------------------------------------
# VIEW B: MP DECISION & INTELLIGENCE DASHBOARD
# ------------------------------------------
elif nav_choice == "MP Decision & Intelligence Dashboard":
    
    # Check Authentication for Dashboard Access
    if not st.session_state["authenticated"]:
        st.markdown("<div class='ghana-header'></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #facc15;'>🔐 MP Portal Secure Sign-In</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #9ca3af;'>Authorized access only. Please sign in with your campaign credentials to view intelligence data.</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                u_input = st.text_input("Username")
                p_input = st.text_input("Password", type="password")
                login_btn = st.form_submit_button("Sign In to Dashboard", use_container_width=True)
                
                if login_btn:
                    hashed_p = hash_password(p_input)
                    user_record = run_query("SELECT role, status FROM users WHERE username = ? AND password = ?", (u_input, hashed_p))
                    if user_record:
                        role, status = user_record[0]
                        if status == "approved":
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = u_input
                            st.session_state["role"] = role
                            st.success("Authentication Successful! Loading dashboard...")
                            st.rerun()
                        else:
                            st.error("⚠️ Your account is pending approval.")
                    else:
                        st.error("❌ Invalid username or password.")
        st.stop()

    # --- AUTHORIZED DASHBOARD VIEW ---
    st.markdown("<div class='ghana-header'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #facc15;'>📊 Aowin MP Statistical Engine & Decision Hub</h2>", unsafe_allow_html=True)
    st.markdown("Automated statistical analytics, data-driven recommendations, and downloadable data exports.")
    
    df = load_responses()
    
    if not df.empty:
        total_responses = len(df)
        yes_votes = len(df[df["will_vote"].str.contains("Yes")])
        undecided_votes = len(df[df["will_vote"].str.contains("Undecided")])
        no_votes = len(df[df["will_vote"].str.contains("No")])
        
        yes_pct = (yes_votes / total_responses) * 100
        undecided_pct = (undecided_votes / total_responses) * 100
        no_pct = (no_votes / total_responses) * 100
        
        # --- STATISTICAL KPI METRICS ---
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Submissions", f"{total_responses:,}")
        with m2:
            st.metric("Supportive (Yes)", f"{yes_votes} ({yes_pct:.1f}%)")
        with m3:
            st.metric("Undecided Group", f"{undecided_votes} ({undecided_pct:.1f}%)")
        with m4:
            st.metric("Opposition (No)", f"{no_votes} ({no_pct:.1f}%)")
            
        st.markdown("---")
        
        # --- DATA DOWNLOAD SECTION ---
        st.markdown("### 📥 Download Constituent Data")
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download All Constituent Feedback (CSV)",
            data=csv_data,
            file_name=f"aowin_voter_feedback_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.markdown("---")
        
        # --- AUTOMATED DECISION ENGINE & FINDINGS ---
        st.markdown("### 🧠 Automated Statistical Findings & Campaign Decisions")
        
        top_issue = df["priority_issue"].mode()[0] if not df["priority_issue"].empty else "N/A"
        top_zone = df["electoral_zone"].mode()[0] if not df["electoral_zone"].empty else "N/A"
        
        if yes_pct >= 60:
            status_class = "success-box"
            strategic_advice = "Your approval rating is strong. Focus on maintaining community touchpoints and keeping campaign momentum active."
        elif undecided_pct > yes_pct:
            status_class = "decision-box"
            strategic_advice = "A large portion of voters are **Undecided**. Immediate community town halls in Enchi Central and surrounding zones are advised to clarify your policy achievements."
        else:
            status_class = "alert-box"
            strategic_advice = "Warning: Opposition and neutral sentiments are high. Immediate interventions on community concerns are required."

        st.markdown(f"""
            <div class="{status_class}">
                <b>📌 Key Statistical Finding:</b> The single most pressing issue across Aowin right now is <b style='color: #facc15;'>{top_issue}</b>, with the highest engagement originating from <b style='color: #16a34a;'>{top_zone}</b>.<br><br>
                <b>🎯 Automated Campaign Decision & Recommendation:</b><br>
                {strategic_advice}
            </div>
        """, unsafe_allow_html=True)
        
        # --- ZONE BREAKDOWN STATISTICS TABLE ---
        st.markdown("### 🗺️ Statistical Breakdown by Aowin Electoral Zones")
        zone_summary = df.groupby("electoral_zone").agg(
            Total_Feedback=('id', 'count'),
            Supportive_Count=('will_vote', lambda x: (x.str.contains("Yes")).sum())
        ).reset_index()
        zone_summary["Support_Rate_%"] = (zone_summary["Supportive_Count"] / zone_summary["Total_Feedback"] * 100).round(1)
        st.dataframe(zone_summary, use_container_width=True)

        st.markdown("### 📋 Raw Constituent Submissions & Reasons")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No constituent responses recorded yet. Share this portal link across Enchi and Aowin communities to start generating statistics.")

# ==========================================
# FOOTER WATERMARK WITH GHANA COLORS
# ==========================================
st.markdown("---")
st.markdown("<div class='ghana-header'></div>", unsafe_allow_html=True)
st.markdown(
    f"<p style='text-align: center; color: #9ca3af; font-size: 12px;'>"
    f"Aowin Constituent Pulse & Decision Engine | Developed by <b style='color: #facc15;'>ROG3RS</b> | Contact: <b style='color: #16a34a;'>0542470810</b>"
    f"</p>", 
    unsafe_allow_html=True
)