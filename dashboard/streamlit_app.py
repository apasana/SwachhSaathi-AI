from __future__ import annotations

import io

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(page_title="SwachhSaathi AI", layout="wide")


TEXT = {
    "English": {
        "menu": "SwachhSaathi Menu",
        "api_base": "FastAPI base URL",
        "language": "Language",
        "login": "Login",
        "auth_mode": "Auth Mode",
        "logout": "Logout",
        "username": "Username",
        "password": "Password",
        "register": "Register",
        "full_name": "Full Name",
        "role": "Role",
        "register_now": "Register Now",
        "sign_in": "Sign In",
        "login_failed": "Invalid username or password",
        "register_failed": "Registration failed",
        "register_ok": "Registration successful. Please login.",
        "login_hint": "Create an account from sidebar Register, then login.",
        "logged_in_as": "Logged in as",
        "home": "Home",
        "report": "Report Issue",
        "track": "Track Complaint",
        "history": "My History",
        "insights": "Insights",
        "manage": "Manage Complaints",
        "refresh": "Refresh",
        "title": "SwachhSaathi AI",
        "caption": "User-side waste reporting and tracking portal",
        "report_card": "Report Waste Issue",
        "track_card": "Track Complaints",
        "insight_card": "View Insights",
        "report_help": "Submit location, description, and optional image.",
        "track_help": "Search complaint status using ticket ID.",
        "insight_help": "See complaint trends and risk alerts.",
        "quick_flow": "Citizen -> Report Issue -> AI Processing -> MongoDB -> Prediction -> Authority Insights",
        "report_subtitle": "Fill in complaint details. Image is optional but supported.",
        "name": "Your Name",
        "phone": "Contact Number",
        "location": "Location",
        "location_hint": "e.g., Ward 12 Main Road",
        "description": "Waste Description",
        "description_hint": "Describe the issue in detail",
        "reported_via": "Reported Via",
        "upload": "Upload Image (optional)",
        "submit": "Submit Complaint",
        "submit_ok": "Complaint submitted successfully",
        "submit_fail": "Complaint submission failed",
        "ticket": "Ticket ID",
        "risk": "Risk Level",
        "waste": "Waste Type",
        "fill_time": "Predicted Bin Fill Time (hrs)",
        "status": "Status",
        "track_subtitle": "Track complaint status by ticket ID.",
        "enter_ticket": "Enter Ticket ID",
        "track_hint": "e.g., SSA-20260417-AB12CD34",
        "track_now": "Track Now",
        "track_fail": "Unable to track ticket",
        "invalid_ticket": "Please enter a valid ticket ID.",
        "history_subtitle": "View your complaint history by contact number.",
        "search_history": "Search History",
        "no_history": "No complaints found for this number.",
        "insights_title": "Dashboard and Insights",
        "load_fail": "Unable to load dashboard data",
        "total": "Total Complaints",
        "resolved": "Resolved",
        "pending": "Pending",
        "high_risk": "High Risk",
        "waste_dist": "Waste Distribution",
        "risk_dist": "Risk Levels",
        "alerts": "Predicted Alerts",
        "recent": "Recent Complaints",
        "no_data": "No complaints submitted yet.",
        "no_alerts": "No alerts to display.",
        "manage_title": "Authority Complaint Management",
        "select_ticket": "Select Ticket",
        "new_status": "New Status",
        "assigned_to": "Assign To",
        "notes": "Authority Notes",
        "update_status": "Update Status",
        "update_ok": "Complaint status updated successfully",
        "update_fail": "Unable to update complaint status",
    },
    "Hindi": {
        "menu": "स्वच्छसाथी मेनू",
        "api_base": "FastAPI URL",
        "language": "भाषा",
        "login": "लॉगिन",
        "auth_mode": "ऑथ मोड",
        "logout": "लॉगआउट",
        "username": "यूज़रनेम",
        "password": "पासवर्ड",
        "register": "रजिस्टर",
        "full_name": "पूरा नाम",
        "role": "भूमिका",
        "register_now": "अभी रजिस्टर करें",
        "sign_in": "साइन इन",
        "login_failed": "गलत यूज़रनेम या पासवर्ड",
        "register_failed": "रजिस्ट्रेशन नहीं हुआ",
        "register_ok": "रजिस्ट्रेशन सफल हुआ। अब लॉगिन करें।",
        "login_hint": "साइडबार में रजिस्टर करके लॉगिन करें।",
        "logged_in_as": "लॉगिन यूज़र",
        "home": "होम",
        "report": "शिकायत दर्ज करें",
        "track": "शिकायत ट्रैक करें",
        "history": "मेरी हिस्ट्री",
        "insights": "इनसाइट्स",
        "manage": "शिकायत प्रबंधन",
        "refresh": "रिफ्रेश",
        "title": "स्वच्छसाथी AI",
        "caption": "यूज़र साइड वेस्ट रिपोर्टिंग और ट्रैकिंग पोर्टल",
        "report_card": "कचरा समस्या दर्ज करें",
        "track_card": "शिकायत स्थिति देखें",
        "insight_card": "विश्लेषण देखें",
        "report_help": "लोकेशन, विवरण और वैकल्पिक इमेज सबमिट करें।",
        "track_help": "टिकट ID से शिकायत की स्थिति खोजें।",
        "insight_help": "ट्रेंड, रिस्क और अलर्ट देखें।",
        "quick_flow": "नागरिक -> शिकायत -> AI प्रोसेसिंग -> MongoDB -> प्रिडिक्शन -> अथॉरिटी इनसाइट्स",
        "report_subtitle": "शिकायत विवरण भरें। इमेज वैकल्पिक है।",
        "name": "आपका नाम",
        "phone": "मोबाइल नंबर",
        "location": "लोकेशन",
        "location_hint": "जैसे: वार्ड 12 मेन रोड",
        "description": "समस्या का विवरण",
        "description_hint": "समस्या विस्तार से लिखें",
        "reported_via": "रिपोर्ट माध्यम",
        "upload": "इमेज अपलोड करें (वैकल्पिक)",
        "submit": "शिकायत भेजें",
        "submit_ok": "शिकायत सफलतापूर्वक दर्ज हुई",
        "submit_fail": "शिकायत दर्ज नहीं हुई",
        "ticket": "टिकट ID",
        "risk": "रिस्क लेवल",
        "waste": "कचरा प्रकार",
        "fill_time": "बिन भरने का समय (घंटे)",
        "status": "स्थिति",
        "track_subtitle": "टिकट ID से शिकायत ट्रैक करें।",
        "enter_ticket": "टिकट ID दर्ज करें",
        "track_hint": "जैसे: SSA-20260417-AB12CD34",
        "track_now": "ट्रैक करें",
        "track_fail": "टिकट ट्रैक नहीं हुआ",
        "invalid_ticket": "कृपया सही टिकट ID दर्ज करें।",
        "history_subtitle": "मोबाइल नंबर से शिकायत इतिहास देखें।",
        "search_history": "हिस्ट्री खोजें",
        "no_history": "इस नंबर के लिए कोई शिकायत नहीं मिली।",
        "insights_title": "डैशबोर्ड और इनसाइट्स",
        "load_fail": "डैशबोर्ड डेटा लोड नहीं हुआ",
        "total": "कुल शिकायतें",
        "resolved": "निपटाई गई",
        "pending": "लंबित",
        "high_risk": "हाई रिस्क",
        "waste_dist": "कचरा वितरण",
        "risk_dist": "रिस्क स्तर",
        "alerts": "प्रिडिक्टेड अलर्ट",
        "recent": "हाल की शिकायतें",
        "no_data": "अभी कोई शिकायत नहीं है।",
        "no_alerts": "अभी कोई अलर्ट नहीं है।",
        "manage_title": "अथॉरिटी शिकायत प्रबंधन",
        "select_ticket": "टिकट चुनें",
        "new_status": "नई स्थिति",
        "assigned_to": "किसे असाइन करें",
        "notes": "अथॉरिटी नोट्स",
        "update_status": "स्थिति अपडेट करें",
        "update_ok": "स्थिति सफलतापूर्वक अपडेट हुई",
        "update_fail": "स्थिति अपडेट नहीं हुई",
    },
}


def t(key: str) -> str:
    language = st.session_state.get("language", "English")
    return TEXT.get(language, TEXT["English"]).get(key, key)


def _api_base_url() -> str:
    return st.sidebar.text_input(t("api_base"), value="http://127.0.0.1:8000").rstrip("/")


def fetch_summary(base_url: str) -> dict:
    response = requests.get(f"{base_url}/dashboard/summary", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_complaints(base_url: str) -> list[dict]:
    response = requests.get(f"{base_url}/complaints?limit=100", timeout=10)
    response.raise_for_status()
    return response.json()


def fetch_history(base_url: str, contact_number: str) -> list[dict]:
    response = requests.get(f"{base_url}/complaints/history/{contact_number}?limit=100", timeout=10)
    response.raise_for_status()
    return response.json()


def submit_complaint(base_url: str, form_data: dict, image_file) -> tuple[bool, dict | str]:
    try:
        files = None
        if image_file is not None:
            image_bytes = image_file.getvalue()
            files = {
                "image": (
                    image_file.name,
                    io.BytesIO(image_bytes),
                    image_file.type or "application/octet-stream",
                )
            }
        response = requests.post(f"{base_url}/complaints/upload", data=form_data, files=files, timeout=20)
        response.raise_for_status()
        return True, response.json()
    except Exception as exc:
        return False, str(exc)


def update_status(base_url: str, ticket_id: str, status: str, assigned_to: str, authority_notes: str) -> tuple[bool, dict | str]:
    try:
        payload = {
            "status": status,
            "assigned_to": assigned_to or None,
            "authority_notes": authority_notes or None,
        }
        response = requests.patch(f"{base_url}/complaints/{ticket_id}/status", json=payload, timeout=15)
        response.raise_for_status()
        return True, response.json()
    except Exception as exc:
        return False, str(exc)


def api_login(base_url: str, username: str, password: str) -> tuple[bool, dict | str]:
    try:
        payload = {"username": username, "password": password}
        response = requests.post(f"{base_url}/auth/login", json=payload, timeout=15)
        response.raise_for_status()
        return True, response.json().get("data", {})
    except Exception as exc:
        return False, str(exc)


def api_register(base_url: str, username: str, password: str, full_name: str, contact_number: str, role: str) -> tuple[bool, dict | str]:
    try:
        payload = {
            "username": username,
            "password": password,
            "full_name": full_name,
            "contact_number": contact_number,
            "role": role,
        }
        response = requests.post(f"{base_url}/auth/register", json=payload, timeout=15)
        if response.status_code == 409:
            return False, "User already exists. Please use Login or register with a different username/contact number."
        response.raise_for_status()
        return True, response.json().get("data", {})
    except Exception as exc:
        return False, str(exc)


def init_session() -> None:
    if "auth" not in st.session_state:
        st.session_state.auth = None
    if "language" not in st.session_state:
        st.session_state.language = "English"
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"


def render_login(base_url: str) -> None:
    st.sidebar.markdown(f"### {t('login')}")
    mode_label = st.sidebar.radio(
        t("auth_mode"),
        [t("login"), t("register")],
        index=0 if st.session_state.auth_mode == "login" else 1,
    )
    st.session_state.auth_mode = "login" if mode_label == t("login") else "register"

    if st.session_state.auth_mode == "login":
        username = st.sidebar.text_input(t("username"), key="login_user")
        password = st.sidebar.text_input(t("password"), type="password", key="login_pass")
        if st.sidebar.button(t("sign_in"), key="login_btn"):
            ok, user = api_login(base_url, username.strip(), password)
            if ok:
                st.session_state.auth = {
                    "username": user.get("username"),
                    "role": user.get("role"),
                    "name": user.get("full_name"),
                    "contact_number": user.get("contact_number"),
                }
                st.rerun()
            st.sidebar.error(f"{t('login_failed')}: {user}")

    if st.session_state.auth_mode == "register":
        reg_name = st.sidebar.text_input(t("full_name"), key="reg_name")
        reg_phone = st.sidebar.text_input(t("phone"), key="reg_phone")
        reg_user = st.sidebar.text_input(t("username"), key="reg_user")
        reg_pass = st.sidebar.text_input(t("password"), type="password", key="reg_pass")
        reg_role = st.sidebar.selectbox(t("role"), ["citizen", "authority"], key="reg_role")
        if st.sidebar.button(t("register_now"), key="reg_btn"):
            ok, result = api_register(base_url, reg_user.strip(), reg_pass, reg_name.strip(), reg_phone.strip(), reg_role)
            if ok:
                st.session_state.auth_mode = "login"
                st.session_state.login_user = reg_user.strip()
                st.sidebar.success(t("register_ok"))
            else:
                st.sidebar.error(f"{t('register_failed')}: {result}")


def render_auth_info() -> None:
    auth = st.session_state.auth
    if not auth:
        return
    st.sidebar.success(f"{t('logged_in_as')}: {auth['name']} ({auth['role']})")
    if st.sidebar.button(t("logout")):
        st.session_state.auth = None
        st.rerun()


def render_home() -> None:
    st.title(t("title"))
    st.caption(t("caption"))

    left, mid, right = st.columns(3)
    with left:
        st.info(f"{t('report_card')}\n\n{t('report_help')}")
    with mid:
        st.info(f"{t('track_card')}\n\n{t('track_help')}")
    with right:
        st.info(f"{t('insight_card')}\n\n{t('insight_help')}")

    st.markdown(
        f"### Quick Flow\n{t('quick_flow')}"
    )


def render_report_issue(base_url: str) -> None:
    st.subheader(t("report_card"))
    st.write(t("report_subtitle"))

    with st.form("complaint_form", clear_on_submit=True):
        citizen_name = st.text_input(t("name"), value=(st.session_state.auth or {}).get("name", ""))
        contact_number = st.text_input(t("phone"))
        location = st.text_input(t("location"), placeholder=t("location_hint"))
        description = st.text_area(t("description"), placeholder=t("description_hint"))
        reported_via = st.selectbox(t("reported_via"), options=["web", "mobile", "kiosk"])
        image_file = st.file_uploader(t("upload"), type=["jpg", "jpeg", "png", "webp"])
        submitted = st.form_submit_button(t("submit"))

    if not submitted:
        return

    form_data = {
        "description": description,
        "location": location,
        "citizen_name": citizen_name,
        "contact_number": contact_number,
        "reported_via": reported_via,
    }

    ok, result = submit_complaint(base_url, form_data, image_file)
    if not ok:
        st.error(f"{t('submit_fail')}: {result}")
        return

    complaint = result.get("data", {})
    st.success(t("submit_ok"))

    top1, top2, top3 = st.columns(3)
    top1.metric(t("ticket"), complaint.get("ticket_id", "NA"))
    top2.metric(t("risk"), complaint.get("risk_level", "NA"))
    top3.metric(t("waste"), complaint.get("waste_type", "NA"))

    low1, low2 = st.columns(2)
    low1.metric(t("fill_time"), complaint.get("predicted_bin_fill_hours", "NA"))
    low2.metric(t("status"), complaint.get("status", "NA"))

    st.json(complaint)


def render_track(base_url: str) -> None:
    st.subheader(t("track"))
    st.write(t("track_subtitle"))
    ticket_id = st.text_input(t("enter_ticket"), placeholder=t("track_hint"))

    if st.button(t("track_now")):
        if not ticket_id.strip():
            st.warning(t("invalid_ticket"))
            return

        try:
            response = requests.get(f"{base_url}/complaints/{ticket_id.strip()}", timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            st.error(f"{t('track_fail')}: {exc}")
            return

        c1, c2, c3 = st.columns(3)
        c1.metric(t("status"), data.get("status", "NA"))
        c2.metric(t("risk"), data.get("risk_level", "NA"))
        c3.metric(t("waste"), data.get("waste_type", "NA"))
        st.metric(t("fill_time"), data.get("predicted_bin_fill_hours", "NA"))
        st.json(data)


def render_history(base_url: str) -> None:
    st.subheader(t("history"))
    st.write(t("history_subtitle"))
    number = st.text_input(t("phone"), key="history_phone")

    if st.button(t("search_history")):
        if not number.strip():
            st.warning(t("phone"))
            return
        try:
            history = fetch_history(base_url, number.strip())
        except Exception as exc:
            st.error(f"{t('load_fail')}: {exc}")
            return

        if not history:
            st.info(t("no_history"))
            return

        history_df = pd.DataFrame(history)
        show_cols = [
            column
            for column in ["ticket_id", "description", "location", "risk_level", "status", "predicted_bin_fill_hours", "created_at"]
            if column in history_df.columns
        ]
        st.dataframe(history_df[show_cols], use_container_width=True, hide_index=True)


def render_insights(base_url: str) -> None:
    st.subheader(t("insights_title"))

    try:
        summary = fetch_summary(base_url)
        complaints = fetch_complaints(base_url)
    except Exception as exc:
        st.error(f"{t('load_fail')}: {exc}")
        return

    metrics = summary["metrics"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("total"), metrics["total_complaints"])
    col2.metric(t("resolved"), metrics["resolved_complaints"])
    col3.metric(t("pending"), metrics["pending_complaints"])
    col4.metric(t("high_risk"), metrics["high_risk_complaints"])

    st.divider()
    left, right = st.columns(2)

    with left:
        st.markdown(f"#### {t('waste_dist')}")
        if summary["waste_distribution"]:
            waste_df = pd.DataFrame(list(summary["waste_distribution"].items()), columns=["Waste Type", "Count"])
            st.plotly_chart(px.pie(waste_df, names="Waste Type", values="Count", hole=0.35), use_container_width=True)
        else:
            st.info(t("no_data"))

    with right:
        st.markdown(f"#### {t('risk_dist')}")
        if summary["risk_distribution"]:
            risk_df = pd.DataFrame(list(summary["risk_distribution"].items()), columns=["Risk Level", "Count"])
            st.plotly_chart(px.bar(risk_df, x="Risk Level", y="Count", color="Risk Level"), use_container_width=True)
        else:
            st.info(t("no_data"))

    st.markdown(f"#### {t('alerts')}")
    alerts_df = pd.DataFrame(summary["predicted_alerts"])
    if not alerts_df.empty:
        st.dataframe(alerts_df, use_container_width=True, hide_index=True)
    else:
        st.info(t("no_alerts"))

    st.markdown(f"#### {t('recent')}")
    if complaints:
        complaints_df = pd.DataFrame(complaints)
        visible_columns = [
            column
            for column in [
                "ticket_id",
                "location",
                "description",
                "waste_type",
                "risk_level",
                "status",
                "predicted_bin_fill_hours",
                "created_at",
            ]
            if column in complaints_df.columns
        ]
        st.dataframe(complaints_df[visible_columns], use_container_width=True, hide_index=True)
    else:
        st.info(t("no_data"))


def render_manage_complaints(base_url: str) -> None:
    st.subheader(t("manage_title"))
    try:
        complaints = fetch_complaints(base_url)
    except Exception as exc:
        st.error(f"{t('load_fail')}: {exc}")
        return

    if not complaints:
        st.info(t("no_data"))
        return

    option_map = {
        f"{item.get('ticket_id')} | {item.get('status')} | {item.get('location')}": item.get("ticket_id")
        for item in complaints
    }
    selected = st.selectbox(t("select_ticket"), options=list(option_map.keys()))
    selected_ticket = option_map[selected]

    status = st.selectbox(t("new_status"), ["new", "under_review", "assigned", "resolved"])
    assigned_to = st.text_input(t("assigned_to"))
    notes = st.text_area(t("notes"))

    if st.button(t("update_status")):
        ok, result = update_status(base_url, selected_ticket, status, assigned_to, notes)
        if ok:
            st.success(t("update_ok"))
            st.json(result)
        else:
            st.error(f"{t('update_fail')}: {result}")


init_session()
st.sidebar.title(t("menu"))
st.session_state.language = st.sidebar.selectbox(t("language"), ["English", "Hindi"], index=0 if st.session_state.language == "English" else 1)
API_BASE_URL = _api_base_url()

if not st.session_state.auth:
    render_login(API_BASE_URL)
    st.title(t("title"))
    st.info(t("login_hint"))
    st.stop()

render_auth_info()

role = st.session_state.auth["role"]
if role == "authority":
    page = st.sidebar.radio("Navigate", [t("home"), t("report"), t("track"), t("history"), t("insights"), t("manage")])
else:
    page = st.sidebar.radio("Navigate", [t("home"), t("report"), t("track"), t("history"), t("insights")])

if st.sidebar.button(t("refresh")):
    st.rerun()

if page == t("home"):
    render_home()
elif page == t("report"):
    render_report_issue(API_BASE_URL)
elif page == t("track"):
    render_track(API_BASE_URL)
elif page == t("history"):
    render_history(API_BASE_URL)
elif page == t("insights"):
    render_insights(API_BASE_URL)
else:
    render_manage_complaints(API_BASE_URL)
