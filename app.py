import io
import calendar
from html import escape
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="SGK Café | Vagtplan",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""<style>
/* SGK V6 – one coherent light palette. No blue UI elements. */
:root {color-scheme: light !important; --sgk-text:#20372C; --sgk-control:#F0F2F0; --sgk-border:#CCD4CD; --sgk-gold:#CCAD61;}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background-color:#F7F8F5 !important; color:#20372C !important;
}
[data-testid="stHeader"] {background:transparent !important;}
.block-container {max-width:1120px !important;padding-top:2rem !important;padding-bottom:3rem !important;}
h1,h2,h3,h4,h5,h6 {color:#20372C !important;letter-spacing:-.02em;}
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label {color:#20372C !important;opacity:1 !important;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {color:#66796E !important;opacity:1 !important;}

/* Input wrappers, including BaseWeb internal layers. */
.stApp div[data-baseweb="input"], .stApp div[data-baseweb="base-input"],
.stApp div[data-baseweb="textarea"], .stApp div[data-baseweb="select"],
.stApp div[data-baseweb="select"]>div, .stApp div[data-baseweb="select"]>div>div,
.stApp [data-testid="stTextInput"] div[data-baseweb="input"],
.stApp [data-testid="stDateInput"] div[data-baseweb="input"],
.stApp [data-testid="stSelectbox"] div[data-baseweb="select"],
.stApp [data-testid="stTextArea"] div[data-baseweb="textarea"] {
  background-color:#F0F2F0 !important;
  color:#20372C !important;
  border-color:#CCD4CD !important;
  box-shadow:none !important;
}
.stApp div[data-baseweb="input"], .stApp div[data-baseweb="select"]>div,
.stApp div[data-baseweb="textarea"] {
  border:1px solid #CCD4CD !important; border-radius:11px !important;
}
.stApp input, .stApp textarea, .stApp select,
.stApp div[data-baseweb="select"] input,
.stApp div[data-baseweb="select"] span,
.stApp div[data-baseweb="select"] [role="combobox"],
.stApp div[data-baseweb="select"] [aria-selected],
.stApp div[data-baseweb="select"]>div *,
.stApp [data-testid="stTextInput"] input {
  background-color:transparent !important;
  color:#20372C !important; -webkit-text-fill-color:#20372C !important;
  caret-color:#20372C !important; opacity:1 !important;
}
.stApp input::placeholder, .stApp textarea::placeholder {
  color:#63766A !important; -webkit-text-fill-color:#63766A !important;opacity:1 !important;
}
.stApp div[data-baseweb="select"] svg, .stApp div[data-baseweb="input"] svg {
  color:#20372C !important;fill:#20372C !important;
}
.stApp div[data-baseweb="input"]:focus-within,
.stApp div[data-baseweb="select"]:focus-within,
.stApp div[data-baseweb="textarea"]:focus-within {
  border-color:#A58B4D !important; outline:2px solid #CCAD61 !important;
  outline-offset:0 !important;box-shadow:0 0 0 1px #CCAD61 !important;
}
/* The list popup can be rendered outside .stApp */
div[data-baseweb="popover"],div[data-baseweb="menu"],div[role="listbox"],
li[role="option"],div[role="option"] {background:#FFFFFF !important;color:#20372C !important;}
div[data-baseweb="popover"] *,div[data-baseweb="menu"] *,[role="listbox"] *,[role="option"] * {
 color:#20372C !important;-webkit-text-fill-color:#20372C !important;
}
[role="option"]:hover,[role="option"][aria-selected="true"] {background:#EFE5CB !important;}
/* Date popups, if any date widget is introduced again. */
[data-baseweb="calendar"], [data-baseweb="calendar"] * {background-color:#FFFFFF !important;color:#20372C !important;}
[data-baseweb="calendar"] button[aria-selected="true"] {background:#CCAD61 !important;color:#20372C !important;}
/* Buttons, navigation and hover/focus states. */
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button {
 background:#FFFFFF !important;color:#20372C !important;border:1px solid #CCD4CD !important;
 border-radius:11px !important;min-height:2.6rem !important; font-weight:650 !important;
 box-shadow:none !important;
}
[data-testid="stButton"] button *,[data-testid="stFormSubmitButton"] button *,
[data-testid="stDownloadButton"] button * {color:inherit !important;}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
 background:#CCAD61 !important;color:#20372C !important;border-color:#CCAD61 !important;
}
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover {
 background:#F4EACD !important;border-color:#A58B4D !important;
}
[data-testid="stButton"] button:focus-visible,[data-testid="stFormSubmitButton"] button:focus-visible,
[data-testid="stDownloadButton"] button:focus-visible {outline:3px solid #CCAD61 !important;outline-offset:2px !important;}
/* Native checkbox and radio accents, not blue/red. */
input[type="checkbox"],input[type="radio"] {accent-color:#A58B4D !important;}
[data-testid="stCheckbox"] *,[data-testid="stRadio"] * {opacity:1 !important;}
/* Neutral message cards replace native blue st.info. */
.sgk-notice {background:#F0F2F0;border:1px solid #CCD4CD;border-left:4px solid #CCAD61;
 border-radius:12px;padding:15px 18px;color:#20372C;font-size:.95rem;line-height:1.5;}
.sgk-notice strong {color:#20372C;}
[data-testid="stExpander"] details {background:#FFF !important;border:1px solid #DFE4DF !important;border-radius:12px !important;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px !important;}
.status-pill {display:inline-block;padding:4px 10px;border-radius:50px;font-size:.81rem;
 font-weight:650;background:#F4EACA;color:#6B5621;margin-bottom:7px;}
.status-pill.gray {background:#EEF2EE;color:#516257;}
.status-pill.green {background:#E7F4EA;color:#326947;}
.card-title {font-size:1.03rem;font-weight:730;color:#20372C;margin:2px 0;}
.card-sub {font-size:.93rem;color:#51685A;margin-top:4px;}
.summary-box {background:#FFF;border:1px solid #DFE4DF;border-radius:14px;padding:14px 18px;min-height:88px;}
.summary-label {color:#51685A;font-size:.9rem;margin-bottom:7px;}
.summary-value {color:#20372C;font-size:1.75rem;font-weight:740;line-height:1.2;}
.table-wrap {border:1px solid #DFE4DF;border-radius:13px;overflow-x:auto;background:#FFF;}
.table-clean {width:100%;border-collapse:collapse;font-size:.91rem;}
.table-clean th {text-align:left;background:#F0F2F0;color:#20372C;padding:11px 13px;white-space:nowrap;}
.table-clean td {color:#20372C;padding:11px 13px;border-top:1px solid #E7EEE8;}
@media(max-width:760px) {.block-container{padding:1rem .8rem 3rem !important;}h1{font-size:1.85rem !important;}}

/* V7: comprehensive neutral surfaces and focus rings (all views). */
:root { --primary-color:#CCAD61; --primary:#CCAD61; --secondary-background-color:#F0F2F0; }
.stApp :is([data-testid="stTextInput"],[data-testid="stTextArea"],[data-testid="stSelectbox"],
[data-testid="stNumberInput"],[data-testid="stDateInput"],[data-testid="stTimeInput"],
[data-testid="stMultiSelect"]) :is([data-baseweb="input"],[data-baseweb="base-input"],
[data-baseweb="select"],[data-baseweb="textarea"],[role="combobox"]) {
 background:#F0F2F0 !important; background-color:#F0F2F0 !important;
 color:#20372C !important; -webkit-text-fill-color:#20372C !important;
 border-color:#CCD4CD !important; box-shadow:none !important; outline-color:#CCAD61 !important;
}
.stApp [data-baseweb="select"] > div,
.stApp [data-baseweb="select"] > div > div,
.stApp [data-baseweb="select"] [role="combobox"],
.stApp [data-baseweb="input"] > div,
.stApp [data-baseweb="base-input"] > div {
 background:#F0F2F0 !important; color:#20372C !important;
}
.stApp :is(input,textarea,select,[role="combobox"],[data-baseweb="select"] span,[data-baseweb="select"] div) {
 color:#20372C !important; -webkit-text-fill-color:#20372C !important;
}
.stApp :is([data-baseweb="select"],[data-baseweb="input"],[data-baseweb="textarea"],button):focus,
.stApp :is([data-baseweb="select"],[data-baseweb="input"],[data-baseweb="textarea"],button):focus-within,
.stApp :is(input,textarea,button):focus-visible {
 border-color:#B69A55 !important; box-shadow:0 0 0 2px #CCAD61 !important;
 outline:0 !important;
}
/* Native alerts, errors and progress indicators: never blue. */
.stApp [data-testid="stAlert"],.stApp [data-testid="stNotification"],
.stApp [role="alert"] {
 background:#F0F2F0 !important; color:#20372C !important;
 border:1px solid #CCD4CD !important; border-radius:12px !important;
}
.stApp [data-testid="stAlert"] *, .stApp [role="alert"] * {color:#20372C !important;}
.stApp [data-testid="stAlert"] svg {color:#A58B4D !important;fill:none !important;}
/* Neutral dataframes/tables, tabs, links and menus. */
.stApp [data-testid="stDataFrame"],.stApp [data-testid="stTable"],
.stApp [data-testid="stMetric"],.stApp [data-testid="stExpander"] {
 border-color:#CCD4CD !important;box-shadow:none !important;
}
.stApp a,.stApp a:visited {color:#20372C !important;}
.stApp a:focus-visible {outline:2px solid #CCAD61 !important;}
.stApp button[role="tab"],.stApp button[role="tab"] * {color:#20372C !important;}
.stApp button[role="tab"][aria-selected="true"] {border-bottom-color:#CCAD61 !important;}
/* Popovers are portal-mounted and can be outside the app root. */
[data-baseweb="popover"],[data-baseweb="popover"] > div,
[data-baseweb="menu"],[role="listbox"],[role="option"] {
 background:#FFFFFF !important;color:#20372C !important;border-color:#CCD4CD !important;
}
[data-baseweb="popover"] *:focus-visible,[role="option"]:focus-visible {
 outline:2px solid #CCAD61 !important;box-shadow:none !important;
}
/* Avoid browser/Streamlit blue highlights in selection controls. */
.stApp input[type="checkbox"],.stApp input[type="radio"] {accent-color:#CCAD61 !important;}
.stApp ::selection {background:#E9D9AA;color:#20372C;}

</style>""",unsafe_allow_html=True)

try:
    URL = st.secrets["SUPABASE_URL"]
    KEY = st.secrets["SUPABASE_ANON_KEY"]
except KeyError:
    st.error("Tilføj SUPABASE_URL og SUPABASE_ANON_KEY i Streamlit Secrets.")
    st.stop()

if "db" not in st.session_state:
    st.session_state.db = create_client(URL, KEY)
db = st.session_state.db


def get(table):
    return db.table(table).select("*").execute().data or []


def notice(message):
    """Neutral information notice – avoids Streamlit's blue default alert."""
    st.markdown(f'<div class="sgk-notice">{escape(str(message))}</div>', unsafe_allow_html=True)


def fail(e):
    st.error(f"Handlingen kunne ikke gennemføres: {e}")


def refresh():
    st.rerun()


def dates_of_week(day):
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)


def hours(shift):
    a = datetime.strptime(shift["start_time"][:5], "%H:%M")
    b = datetime.strptime(shift["end_time"][:5], "%H:%M")
    if b <= a:
        b += timedelta(days=1)
    return round((b - a).total_seconds() / 3600, 2)


DANISH_MONTHS = ["januar", "februar", "marts", "april", "maj", "juni", "juli", "august", "september", "oktober", "november", "december"]
DANISH_DAYS = ["M", "T", "O", "T", "F", "L", "S"]


def calendar_picker(label, key, initial=None, min_date=None):
    """Stabil datovælger uden en browser-popup med uforudsigelige temafarver."""
    starting = initial or date.today()
    if key not in st.session_state:
        st.session_state[key] = max(starting, min_date) if min_date else starting
    chosen = st.session_state[key]
    st.markdown(f"**{label}**")
    cols = st.columns([1, 1.8, 1.2], gap="small")
    years = list(range(min(chosen.year, date.today().year) - 2, max(chosen.year, date.today().year) + 9))
    year = cols[2].selectbox("År", years, index=years.index(chosen.year), key=f"{key}_year")
    month = cols[1].selectbox("Måned", list(range(1, 13)), index=chosen.month - 1,
                              format_func=lambda x: DANISH_MONTHS[x - 1].capitalize(), key=f"{key}_month")
    max_day = calendar.monthrange(year, month)[1]
    day = cols[0].selectbox("Dag", list(range(1, max_day + 1)),
                            index=min(chosen.day, max_day) - 1, key=f"{key}_day")
    result = date(year, month, day)
    if min_date and result < min_date:
        st.warning(f"Vælg en dato fra {min_date:%d/%m/%Y} og frem.")
        return result
    st.session_state[key] = result
    return result


def month_picker(key, label="Vælg måned"):
    st.markdown(f"**{label}**")
    today = date.today()
    if key not in st.session_state:
        st.session_state[key] = (today.year, today.month)
    year, month = st.session_state[key]
    c1, c2 = st.columns([2, 1], gap="small")
    month = c1.selectbox("Måned", list(range(1, 13)), index=month - 1,
                         format_func=lambda v: DANISH_MONTHS[v - 1].capitalize(), key=key + "_m")
    year = c2.selectbox("År", list(range(today.year - 3, today.year + 6)),
                        index=max(0, min(8, year - (today.year - 3))), key=key + "_y")
    st.session_state[key] = (year, month)
    return f"{year:04d}-{month:02d}"


def shift_state(shift):
    if shift["offered"]:
        return "Til overtagelse" if shift["employee_id"] else "Ledig"
    return "Besat" if shift["employee_id"] else "Ikke tildelt"


def display_shift(shift, names):
    owner = names.get(shift["employee_id"], "Ikke tildelt")
    status = shift_state(shift)
    lock = " · Låst" if shift["locked"] else ""
    return f'{shift["start_time"][:5]}–{shift["end_time"][:5]} · {shift["position"]} · {owner} · {status}{lock}'


def nav_buttons(pages, active_key="active_page"):
    if st.session_state.get(active_key) not in pages:
        st.session_state[active_key] = pages[0]
    cols = st.columns(len(pages), gap="small")
    for col, name in zip(cols, pages):
        if col.button(
            name,
            key=f"nav_{name}",
            type="primary" if st.session_state[active_key] == name else "secondary",
            use_container_width=True,
        ):
            st.session_state[active_key] = name
            st.rerun()
    return st.session_state[active_key]


def summary_card(label, value):
    st.markdown(
        f"<div class='summary-box'><div class='summary-label'>{label}</div><div class='summary-value'>{value}</div></div>",
        unsafe_allow_html=True,
    )


def format_shift_note(shift, names):
    if shift["offered"] and shift["employee_id"]:
        return f"Ansvarlig indtil overtagelse: {names.get(shift['employee_id'], 'Ukendt')}"
    if shift["offered"]:
        return "Ingen medarbejder tildelt endnu"
    return names.get(shift["employee_id"], "Ikke tildelt")


def shift_status_class(shift):
    state = shift_state(shift)
    if state == "Besat":
        return "green"
    if state == "Til overtagelse":
        return ""
    return "gray"


def render_shift_card(shift, names, current_user_id=None, allow_actions=True, compact=False):
    state = shift_state(shift)
    hours_txt = str(hours(shift)).replace(".", ",")
    pill_class = shift_status_class(shift)
    title = f"{shift['start_time'][:5]}–{shift['end_time'][:5]} · {shift['position']} · {hours_txt} timer"
    subtitle = format_shift_note(shift, names)
    lock_txt = " · Låst" if shift["locked"] else ""
    with st.container(border=True):
        left, right = st.columns([5, 1.4], gap="small")
        with left:
            st.markdown(
                f"<div class='status-pill {pill_class}'>{state}{lock_txt}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='card-title'>{title}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card-sub'>{escape(subtitle)}</div>", unsafe_allow_html=True)
            if shift.get("notes"):
                st.caption(shift["notes"])
        with right:
            if not allow_actions:
                return
            if shift["offered"] and not shift["locked"] and shift["employee_id"] != current_user_id:
                if st.button("Overtag", key=f"claim_{shift['id']}", type="primary", use_container_width=True):
                    try:
                        db.rpc("claim_shift", {"p_shift": shift["id"]}).execute()
                        st.success("Vagten er overtaget")
                        refresh()
                    except Exception as e:
                        fail(e)
            elif shift["employee_id"] == current_user_id and not shift["locked"]:
                label = "Træk tilbage" if shift["offered"] else "Udbyd"
                if st.button(label, key=f"offer_{shift['id']}", use_container_width=True):
                    try:
                        fn = "cancel_my_offer" if shift["offered"] else "offer_my_shift"
                        db.rpc(fn, {"p_shift": shift["id"]}).execute()
                        refresh()
                    except Exception as e:
                        fail(e)


def render_html_table(df):
    if df.empty:
        return
    html = ["<div class='table-wrap'><table class='table-clean'><thead><tr>"]
    for col in df.columns:
        html.append(f"<th>{escape(str(col))}</th>")
    html.append("</tr></thead><tbody>")
    for _, row in df.iterrows():
        html.append("<tr>")
        for col in df.columns:
            html.append(f"<td>{escape(str(row[col]))}</td>")
        html.append("</tr>")
    html.append("</tbody></table></div>")
    st.markdown("".join(html), unsafe_allow_html=True)


st.title("SGK Café · Vagtplan")
st.caption("Silkeborg Golfklub · Overblik over caféens vagter")

if "user" not in st.session_state:
    with st.form("login"):
        email = st.text_input("E-mail")
        password = st.text_input("Adgangskode", type="password")
        sent = st.form_submit_button("Log ind", type="primary")
    if sent:
        try:
            resp = db.auth.sign_in_with_password({"email": email, "password": password})
            st.session_state.user = resp.user.id
            refresh()
        except Exception:
            st.error("Login mislykkedes. Tjek e-mail og adgangskode.")
    st.stop()

try:
    current = db.auth.get_user()
    if not current or not current.user or current.user.id != st.session_state.user:
        raise ValueError("Login udløbet")
    staff = get("staff")
    me = next((x for x in staff if x["id"] == current.user.id and x["active"]), None)
    if not me:
        st.warning("Din konto er endnu ikke aktiveret som medarbejder. Kontakt administrator.")
        if st.button("Log ud"):
            db.auth.sign_out()
            st.session_state.clear()
            refresh()
        st.stop()
except Exception:
    st.session_state.clear()
    st.warning("Sessionen er udløbet. Log ind igen.")
    st.stop()

admin = me["role"] == "admin"
names = {x["id"]: x["name"] for x in staff}

with st.sidebar:
    st.write(f"Logget ind: **{me['name']}**")
    if st.button("Log ud"):
        db.auth.sign_out()
        st.session_state.clear()
        refresh()

pages = ["Vagtplan", "Mine vagter", "Friønsker", "Timer"] + (["Administration"] if admin else [])
page = nav_buttons(pages)

try:
    shifts = get("shifts")
    wishes = get("unavailability")
    settings = get("settings")
except Exception as e:
    fail(e)
    st.stop()

if page == "Vagtplan":
    st.subheader("Vagtoversigt")
    st.caption("Kun offentliggjorte vagter. Ubesatte og udbudte vagter kan overtages; øvrige viser, hvem der er på arbejde.")

    view = st.radio("Periode", ["Alle kommende", "Vælg uge"], horizontal=True)
    if view == "Vælg uge":
        chosen = calendar_picker("Ugevalg", "week_picker", date.today())
        first, last = dates_of_week(chosen)
        st.caption(f"Uge {first.isocalendar().week} · {first:%d/%m}–{last:%d/%Y}")
    else:
        first = date.today()
        last = None

    filt1, filt2 = st.columns(2, gap="small")
    availability = filt1.selectbox("Status", ["Alle vagter", "Ledige / til overtagelse", "Besatte"])
    kind = filt2.selectbox("Funktion", ["Alle", "Tjener", "Opvasker"])

    published = [
        s for s in shifts
        if s["published"]
        and s["shift_day"] >= first.isoformat()
        and (last is None or s["shift_day"] <= last.isoformat())
        and (kind == "Alle" or s["position"] == kind)
        and (
            availability == "Alle vagter"
            or (availability == "Ledige / til overtagelse" and s["offered"])
            or (availability == "Besatte" and not s["offered"] and s["employee_id"])
        )
    ]
    published.sort(key=lambda s: (s["shift_day"], s["start_time"], s["position"]))

    m1, m2 = st.columns(2, gap="small")
    with m1:
        summary_card("Viste vagter", len(published))
    with m2:
        summary_card("Ledige / til overtagelse", sum(bool(s["offered"]) for s in published))

    if not published:
        notice("Ingen offentliggjorte vagter matcher dine filtre.")
    else:
        weekdays = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
        grouped = {}
        for shift in published:
            grouped.setdefault(shift["shift_day"], []).append(shift)
        for day, items in grouped.items():
            d = date.fromisoformat(day)
            st.markdown(f"### {weekdays[d.weekday()]} {d:%d/%m/%Y}")
            for shift in items:
                render_shift_card(shift, names, current_user_id=me["id"], allow_actions=True)

elif page == "Mine vagter":
    mine = sorted(
        [s for s in shifts if s["employee_id"] == me["id"] and s["shift_day"] >= date.today().isoformat()],
        key=lambda x: (x["shift_day"], x["start_time"]),
    )
    st.subheader("Mine vagter")
    st.caption("Her kan du se dine kommende vagter og udbyde dem igen, hvis du bliver forhindret.")
    summary_card("Kommende vagter", len(mine))
    if not mine:
        notice("Du har ingen kommende vagter.")
    else:
        last_day = None
        for shift in mine:
            if shift["shift_day"] != last_day:
                d = date.fromisoformat(shift["shift_day"])
                st.markdown(f"### {d:%A %d/%m/%Y}".replace("Monday", "Mandag").replace("Tuesday", "Tirsdag").replace("Wednesday", "Onsdag").replace("Thursday", "Torsdag").replace("Friday", "Fredag").replace("Saturday", "Lørdag").replace("Sunday", "Søndag"))
                last_day = shift["shift_day"]
            render_shift_card(shift, names, current_user_id=me["id"], allow_actions=True)

elif page == "Friønsker":
    deadline = settings[0].get("wishes_deadline") if settings else None
    st.subheader("Friønsker")
    st.caption(f"Frist for friønsker: {deadline or 'Ikke fastsat'}")
    mine = [w for w in wishes if w["employee_id"] == me["id"]]
    if deadline and date.today() <= date.fromisoformat(deadline):
        chosen_wish_day = calendar_picker("Dag, jeg ikke kan arbejde", "wish_day", date.today(), min_date=date.today())
        with st.form("wish"):
            d = chosen_wish_day
            note = st.text_input("Bemærkning (valgfri)")
            if st.form_submit_button("Gem friønske", type="primary"):
                try:
                    db.table("unavailability").insert({"employee_id": me["id"], "day": d.isoformat(), "note": note}).execute()
                    refresh()
                except Exception as e:
                    fail(e)
    else:
        notice("Der er ikke åbent for nye friønsker lige nu.")

    if mine:
        rows = pd.DataFrame(
            [{"Dato": w["day"], "Bemærkning": w["note"] or "-"} for w in sorted(mine, key=lambda x: x["day"])]
        )
        render_html_table(rows)
        if deadline and date.today() <= date.fromisoformat(deadline):
            st.markdown("##### Slet friønske")
            for w in sorted(mine, key=lambda x: x["day"]):
                c1, c2 = st.columns([5, 1])
                c1.write(f"{w['day']} · {w['note'] or '-'}")
                if c2.button("Slet", key=f"delwish_{w['id']}"):
                    try:
                        db.table("unavailability").delete().eq("id", w["id"]).execute()
                        refresh()
                    except Exception as e:
                        fail(e)

elif page == "Timer":
    st.subheader("Timer og bemanding")
    month = month_picker("hours_month")
    month_shifts = [s for s in shifts if s["published"] and s["shift_day"].startswith(month)]
    assigned = [s for s in month_shifts if s["employee_id"] is not None and (admin or s["employee_id"] == me["id"])]
    open_shifts = [s for s in month_shifts if s["employee_id"] is None] if admin else []
    total_assigned = sum(hours(s) for s in assigned)
    total_open = sum(hours(s) for s in open_shifts)

    m1, m2, m3 = st.columns(3, gap="small")
    with m1: summary_card("Tildelte timer", f"{total_assigned:.2f}".replace(".", ","))
    with m2: summary_card("Ledige vagttimer" if admin else "Mine vagter", f"{total_open:.2f}".replace(".", ",") if admin else len(assigned))
    with m3: summary_card("Tildelte vagter", len(assigned))

    st.markdown("### Timer pr. medarbejder" if admin else "### Mine planlagte vagter")
    assigned_rows = [{
        "Dato": s["shift_day"], "Navn": names.get(s["employee_id"], "Ukendt"),
        "Funktion": s["position"], "Fra": s["start_time"][:5], "Til": s["end_time"][:5],
        "Planlagte timer": hours(s)
    } for s in sorted(assigned, key=lambda x: (x["shift_day"], x["start_time"]))]
    assigned_df = pd.DataFrame(assigned_rows, columns=["Dato", "Navn", "Funktion", "Fra", "Til", "Planlagte timer"])
    if assigned_df.empty:
        notice("Ingen tildelte vagter i den valgte måned.")
        summary = pd.DataFrame(columns=["Navn", "Timer"])
    else:
        summary = assigned_df.groupby("Navn", as_index=False)["Planlagte timer"].sum()
        summary.columns = ["Navn", "Timer"]
        show_summary = summary.copy()
        show_summary["Timer"] = show_summary["Timer"].map(lambda v: f"{v:.2f}".replace(".", ","))
        render_html_table(show_summary)
        with st.expander("Vis alle tildelte vagter"):
            shown = assigned_df.copy()
            shown["Planlagte timer"] = shown["Planlagte timer"].map(lambda v: f"{v:.2f}".replace(".", ","))
            render_html_table(shown)

    if admin:
        st.markdown("### Ledige vagter – manglende bemanding")
        if open_shifts:
            open_rows = [{"Dato": s["shift_day"], "Funktion": s["position"], "Fra": s["start_time"][:5],
                          "Til": s["end_time"][:5], "Timer": hours(s)} for s in sorted(open_shifts, key=lambda x: (x["shift_day"], x["start_time"]))]
            open_df = pd.DataFrame(open_rows)
            shown_open = open_df.copy()
            shown_open["Timer"] = shown_open["Timer"].map(lambda v: f"{v:.2f}".replace(".", ","))
            render_html_table(shown_open)
        else:
            open_df = pd.DataFrame(columns=["Dato", "Funktion", "Fra", "Til", "Timer"])
            st.caption("Ingen ubesatte vagter i denne måned.")
    st.caption("Timerne er planlagte, ikke faktisk registrerede arbejdstimer. Pauser er ikke fratrukket. Udbudte vagter tæller fortsat hos den ansvarlige medarbejder, indtil en kollega overtager.")

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        assigned_df.to_excel(writer, index=False, sheet_name="Tildelte vagter")
        summary.to_excel(writer, index=False, sheet_name="Medarbejdertimer")
        if admin:
            open_df.to_excel(writer, index=False, sheet_name="Ledige vagter")
    st.download_button("Download Excel-rapport", buf.getvalue(),
                       file_name=f"SGK_vagttimer_{month}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif page == "Administration" and admin:
    st.subheader("Administration")
    sections = ["Opret vagt", "Styr vagter", "Friønsker", "Medarbejdere"]
    if st.session_state.get("admin_section") not in sections:
        st.session_state.admin_section = sections[0]
    section_cols = st.columns(4, gap="small")
    for section_col, section_name in zip(section_cols, sections):
        if section_col.button(section_name, key="admin_section_" + section_name,
                              type="primary" if st.session_state.admin_section == section_name else "secondary",
                              use_container_width=True):
            st.session_state.admin_section = section_name
            st.rerun()
    st.divider()

    if st.session_state.admin_section == "Opret vagt":
        st.caption("Opret nye vagter og vælg, om de skal være ledige, tildelt eller låste.")
        day = calendar_picker("Dato for vagten", "new_shift_date", date.today())
        with st.form("new_shift", clear_on_submit=True):
            position = st.selectbox("Funktion", ["Tjener", "Opvasker"])

            c1, c2 = st.columns(2)
            options = [f"{h:02d}:{m:02d}" for h in range(7, 24) for m in (0, 15, 30, 45)] + ["00:00"]
            start = c1.selectbox("Fra", options[:-1], index=8)
            end = c2.selectbox("Til", options, index=36)

            valid_staff = [
                x for x in staff
                if x["active"] and (x["can_waiter"] if position == "Tjener" else x["can_dishwasher"])
            ]
            choices = {"Ledig (udbydes)": None, **{x["name"] + " · " + x["id"][:6]: x["id"] for x in valid_staff}}
            who = st.selectbox("Tildel til", list(choices))

            c3, c4 = st.columns(2)
            locked = c3.checkbox("Låst vagt (kun admin kan ændre)")
            publish = c4.checkbox("Offentliggør straks", value=False)
            note = st.text_area("Bemærkning", height=90)
            submitted = st.form_submit_button("Opret vagt", type="primary")

        if submitted:
            if options.index(end) <= options.index(start):
                st.error("Sluttid skal ligge efter starttid (00:00 betyder midnat).")
            elif locked and choices[who] is None:
                st.error("Låste vagter skal tildeles en medarbejder.")
            else:
                try:
                    db.table("shifts").insert(
                        {
                            "shift_day": day.isoformat(),
                            "start_time": start,
                            "end_time": end,
                            "position": position,
                            "employee_id": choices[who],
                            "locked": locked,
                            "published": publish,
                            "offered": choices[who] is None and not locked,
                            "notes": note,
                        }
                    ).execute()
                    st.success("Vagt oprettet")
                    refresh()
                except Exception as e:
                    fail(e)

    elif st.session_state.admin_section == "Styr vagter":
        st.caption("Ændringer gemmes direkte. Ikke-offentliggjorte vagter kan kun ses af admin.")
        upcoming = sorted(
            [s for s in shifts if s["shift_day"] >= date.today().isoformat()],
            key=lambda s: (s["shift_day"], s["start_time"]),
        )
        if not upcoming:
            notice("Ingen kommende vagter")
        for s in upcoming:
            with st.expander(f"{s['shift_day']} · {display_shift(s, names)} · {'Publiceret' if s['published'] else 'Kladde'}"):
                opts = {"Ledig": None, **{x['name'] + ' · ' + x['id'][:6]: x['id'] for x in staff if x['active'] and (x['can_waiter'] if s['position'] == 'Tjener' else x['can_dishwasher'])}}
                existing = next((k for k, v in opts.items() if v == s["employee_id"]), "Ledig")
                col1, col2, col3 = st.columns(3)
                who = col1.selectbox("Medarbejder", list(opts), index=list(opts).index(existing), key="ass_" + s["id"])
                lock = col2.checkbox("Låst", value=s["locked"], key="lock_" + s["id"])
                pub = col3.checkbox("Offentliggjort", value=s["published"], key="pub_" + s["id"])
                c1, c2 = st.columns(2)
                if c1.button("Gem ændringer", key="save_" + s["id"], type="primary"):
                    if lock and opts[who] is None:
                        st.error("Låst vagt kræver medarbejder")
                    else:
                        try:
                            db.table("shifts").update(
                                {
                                    "employee_id": opts[who],
                                    "locked": lock,
                                    "published": pub,
                                    "offered": opts[who] is None and not lock,
                                }
                            ).eq("id", s["id"]).execute()
                            refresh()
                        except Exception as e:
                            fail(e)
                if c2.button("Slet vagt", key="del_" + s["id"]):
                    try:
                        db.table("shifts").delete().eq("id", s["id"]).execute()
                        refresh()
                    except Exception as e:
                        fail(e)

    elif st.session_state.admin_section == "Friønsker":
        current_deadline = None
        if settings and settings[0].get("wishes_deadline"):
            current_deadline = date.fromisoformat(settings[0]["wishes_deadline"])
        new_deadline = calendar_picker("Frist for friønsker", "deadline_date", current_deadline or (date.today() + timedelta(days=14)))
        if st.button("Gem frist", type="primary"):
            try:
                db.table("settings").update({"wishes_deadline": new_deadline.isoformat()}).eq("id", 1).execute()
                refresh()
            except Exception as e:
                fail(e)
        if wishes:
            wish_rows = pd.DataFrame(
                [{"Dato": w["day"], "Medarbejder": names.get(w["employee_id"], "Ukendt"), "Bemærkning": w["note"] or "-"} for w in sorted(wishes, key=lambda x: x["day"])]
            )
            render_html_table(wish_rows)
        else:
            notice("Ingen friønsker registreret.")

    elif st.session_state.admin_section == "Medarbejdere":
        st.caption("Opret først brugeren i Supabase → Authentication → Users. Indsæt derefter brugerens UUID her.")
        with st.form("add_staff"):
            uid = st.text_input("Bruger-UUID fra Supabase")
            name = st.text_input("Navn")
            role = st.selectbox("Rolle", ["employee", "admin"])
            c1, c2 = st.columns(2)
            waiter = c1.checkbox("Kan være tjener", True)
            dishwasher = c2.checkbox("Kan være opvasker", True)
            if st.form_submit_button("Tilføj medarbejder", type="primary"):
                try:
                    if any(x["id"] == uid.strip() for x in staff):
                        st.warning("Denne bruger findes allerede i medarbejderlisten. Opret ikke samme bruger igen.")
                        st.stop()
                    db.table("staff").insert(
                        {
                            "id": uid.strip(),
                            "name": name.strip(),
                            "role": role,
                            "can_waiter": waiter,
                            "can_dishwasher": dishwasher,
                        }
                    ).execute()
                    refresh()
                except Exception as e:
                    fail(e)
        people = pd.DataFrame(
            [
                {
                    "Navn": p["name"],
                    "Rolle": "Admin" if p["role"] == "admin" else "Medarbejder",
                    "Tjener": "Ja" if p["can_waiter"] else "Nej",
                    "Opvasker": "Ja" if p["can_dishwasher"] else "Nej",
                    "Aktiv": "Ja" if p["active"] else "Nej",
                }
                for p in staff
            ]
        )
        render_html_table(people)
