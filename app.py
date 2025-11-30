import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -------------------------------
# LOAD CUSTOM THEME (MAROON-GOLD)
# -------------------------------
def load_css():
    st.markdown("""
        <style>

        .stApp {
            background-color: #fff8e6;
        }

        section[data-testid="stSidebar"] {
            background-color: #800000 !important;
        }

        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {
            color: white !important;
            font-weight: 600;
        }

        .stButton>button {
            background-color: #800000;
            color: white;
            border-radius: 8px;
            padding: 10px 18px;
            border: none;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #b30000;
        }

        h1, h2, h3 {
            color: #800000 !important;
        }

        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #800000;
            color: white;
            text-align: center;
            padding: 6px;
            font-size: 14px;
        }

        </style>
        """, unsafe_allow_html=True)

load_css()

# -------------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------------
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def connect_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPE
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["G_SHEET_ID"])
    return sheet

def ws(name):
    return connect_gsheet().worksheet(name)

# -------------------------------
# HOME PAGE
# -------------------------------
def home():
    st.image("updated logo.png", width=360)

    st.markdown("""
        <div style='text-align:center; margin-top:-15px;'>
            <h1><b>SPECTRA 2025</b></h1>
            <h2 style="color:#cc9900;"><i>Talent Meets Opportunity</i></h2>

            <p style="font-size:20px; margin-top:15px;">
                <b>45th Annual Day</b><br>
                <b>19th & 20th December, 2025</b><br>
                St. Gregorios Higher Secondary School
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <marquee style="background:#800000; color:white; padding:8px; font-size:18px; border-radius:5px;">
            📢 Welcome to SPECTRA 2025 – Registrations Open | Check Announcements for updates!
        </marquee>
    """, unsafe_allow_html=True)

    st.markdown("## Quick Links")

    col1, col2, col3 = st.columns(3)
    if col1.button("📢 Announcements"):
        st.session_state["page"] = "Announcements"
    if col2.button("🖼 Gallery"):
        st.session_state["page"] = "Gallery"
    if col3.button("📝 Registration"):
        st.session_state["page"] = "Registration"

    st.markdown("---")
    st.info("Use the sidebar to navigate.")

    st.markdown(
        """<div class="footer">© St. Gregorios H.S. School | SPECTTRA 2025</div>""",
        unsafe_allow_html=True
    )

# -------------------------------
# ANNOUNCEMENTS PAGE
# -------------------------------
def announcements():
    st.header("📢 Announcements")
    data = ws("Announcements").get_all_records()

    if not data:
        st.info("No announcements yet.")
    else:
        st.markdown("### Latest Updates")
        for row in reversed(data):
            st.markdown(f"""
                <div style="background:#fff1d6; padding:15px; border-left:6px solid #800000; border-radius:6px; margin-bottom:12px;">
                    <h4 style="color:#800000;">{row.get('title','')}</h4>
                    <p>{row.get('message','')}</p>
                    <span style="font-size:12px; color:#555;">{row.get('timestamp','')}</span>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔐 Admin — Add Announcement")

    pin = st.text_input("Enter Admin PIN", type="password")

    if pin == st.secrets["ADMIN_PIN"]:
        with st.form("ann_form"):
            title = st.text_input("Title")
            msg = st.text_area("Message")
            aud = st.text_input("Audience (optional)")
            post = st.form_submit_button("Post Announcement")

        if post:
            if not title or not msg:
                st.error("Title and message are required.")
            else:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ws("Announcements").append_row([ts, title, msg, aud])
                st.success("Announcement added!")
                st.experimental_rerun()
    else:
        st.caption("Enter Admin PIN to post announcements.")

# -------------------------------
# GALLERY PAGE
# -------------------------------
def gallery():
    st.header("🖼 Gallery")
    data = ws("Gallery").get_all_records()

    if data:
        classes = ["All"] + sorted({r["class"] for r in data if r["class"]})
        sel = st.selectbox("Filter by Class", classes)

        filtered = data if sel == "All" else [r for r in data if r["class"] == sel]

        for r in filtered:
            st.markdown(f"""
                <div style="background:#fff1d6; padding:15px; border-radius:10px; border:2px solid #800000; margin-bottom:15px;">
                    <img src="{r['image_url']}" style="width:100%; border-radius:10px;">
                    <h4 style="color:#800000;">{r['title']}</h4>
                    <p><b>Class:</b> {r['class']}</p>
                    <span style="font-size:12px; color:#555;">{r['timestamp']}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Gallery is empty.")

    st.markdown("---")
    st.subheader("🔐 Admin — Add Photo")

    pin = st.text_input("Admin PIN", type="password")

    if pin == st.secrets["ADMIN_PIN"]:
        with st.form("pic_form"):
            title = st.text_input("Caption")
            cls = st.selectbox("Class", ["6","7","8","9","10","11","12"])
            img = st.text_input("Image URL (from Google Drive)")
            add = st.form_submit_button("Add Photo")

        if add:
            if not img:
                st.error("Image URL is required.")
            else:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ws("Gallery").append_row([ts, title, cls, img])
                st.success("Photo added!")
                st.experimental_rerun()
    else:
        st.caption("Enter Admin PIN to upload.")

# -------------------------------
# REGISTRATION PAGE
# -------------------------------
def registration():
    st.header("📝 Event Registration")
    st.markdown("""
        <div style="background:#fff1d6; padding:15px; border-left:6px solid #800000; border-radius:6px;">
            Please enter correct details. Entries will be visible to coordinators.
        </div>
    """, unsafe_allow_html=True)

    events = ["Skit","Dance","Mime","Volunteer","Anchor","Choir","Special Item"]
    classes = [str(i) for i in range(6, 13)]
    secs = ["A","B","C","D","E"]

    with st.form("reg_form"):
        name = st.text_input("Student Name")
        col1, col2 = st.columns(2)
        cls = col1.selectbox("Class", classes)
        sec = col2.selectbox("Section", secs)
        event = st.selectbox("Select Item / Event", events)
        phone = st.text_input("Contact Number (Optional)")
        submit = st.form_submit_button("Submit")

    if submit:
        if not name:
            st.error("Student Name required.")
        else:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ws("Registrations").append_row([ts, name, cls, sec, event, phone])
            st.success("Registration submitted!")
            st.balloons()

# -------------------------------
# MAIN APP NAVIGATION
# -------------------------------
st.sidebar.title("SPECTRA 2025")
menu = ["Home","Announcements","Gallery","Registration"]

choice = st.sidebar.radio("Navigate", menu)

if choice == "Home":
    home()
elif choice == "Announcements":
    announcements()
elif choice == "Gallery":
    gallery()
elif choice == "Registration":
    registration()
