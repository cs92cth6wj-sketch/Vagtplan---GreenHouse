import io
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

st.markdown(
    """
<style>
:root { color-scheme: light; }
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F7F8F5 !important;
    color: #20372C !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container {
    max-width: 1120px !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}
h1, h2, h3, h4, h5, h6, p, li, span, label, div {
    color: #20372C;
}
h1 { font-weight: 780 !important; letter-spacing: -0.02em; }
h2, h3 { letter-spacing: -0.01em; }
[data-testid="stCaptionContainer"] { color: #839287 !important; }

/* Inputs */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] * {
    color: #20372C !important;
    font-weight: 600 !important;
}
[data-testid="stDateInput"] > div,
[data-testid="stTextInput"] > div,
[data-testid="stTextArea"] > div,
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div,
[data-testid="stNumberInput"] > div,
[data-testid="stTimeInput"] > div {
    background: transparent !important;
}
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"] > div,
[data-baseweb="textarea"],
[data-baseweb="select"],
textarea,
input {
    background: #FFFFFF !important;
    color: #20372C !important;
    border-radius: 12px !important;
    border-color: #CBD5CC !important;
    -webkit-text-fill-color: #20372C !important;
    caret-color: #20372C !important;
}
[data-baseweb="input"] input,
[data-baseweb="base-input"] input,
[data-baseweb="select"] input,
[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="textarea"] textarea,
[data-baseweb="calendar"] *,
[role="listbox"],
[role="option"] {
    color: #20372C !important;
    -webkit-text-fill-color: #20372C !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
    background: #FFFFFF !important;
    color: #20372C !important;
}
svg { color: #20372C !important; }

/* Kalender-popup: BaseWeb/Streamlit kan rendere denne i en separat portal.
   Sæt lys baggrund på hele popupen og mørk tekst på dage og overskrifter. */
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="popover"] [data-baseweb="calendar"],
[data-baseweb="calendar"],
[data-baseweb="calendar"] > div,
[data-baseweb="calendar"] [data-baseweb="datepicker"] {
    background-color: #FFFFFF !important;
    color: #20372C !important;
    color-scheme: light !important;
}
[data-baseweb="calendar"] button,
[data-baseweb="calendar"] [role="button"],
[data-baseweb="calendar"] [data-baseweb="day"],
[data-baseweb="calendar"] [data-baseweb="month"],
[data-baseweb="calendar"] [data-baseweb="year"],
[data-baseweb="calendar"] span,
[data-baseweb="calendar"] div {
    color: #20372C !important;
    -webkit-text-fill-color: #20372C !important;
}
/* Dage: uden for måned / deaktiverede datoer */
[data-baseweb="calendar"] [data-baseweb="day"]:disabled,
[data-baseweb="calendar"] [data-baseweb="day"][aria-disabled="true"],
[data-baseweb="calendar"] button:disabled {
    color: #89988C !important;
    -webkit-text-fill-color: #89988C !important;
}
/* Valgt dato fremhæves i SGK-guld, ikke i standard rød/mørk. */
[data-baseweb="calendar"] [data-baseweb="day"][aria-selected="true"],
[data-baseweb="calendar"] [data-baseweb="day"][data-selected="true"],
[data-baseweb="calendar"] [aria-selected="true"] {
    background-color: #CCAD61 !important;
    color: #20372C !important;
    -webkit-text-fill-color: #20372C !important;
    border-radius: 999px !important;
}
[data-baseweb="calendar"] [data-baseweb="day"]:hover:not(:disabled) {
    background-color: #F4E9C8 !important;
}
/* Pilenes SVG-ikoner og evt. måned/år-dropdowns. */
[data-baseweb="calendar"] svg,
[data-baseweb="calendar"] svg * {
    color: #20372C !important;
    fill: currentColor !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] div {
    color: #20372C !important;
}

/* Buttons */
[data-testid="stButton"] button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button {
    background: #FFFFFF !important;
    color: #20372C !important;
    border: 1px solid #C7D2C9 !important;
    border-radius: 14px !important;
    min-height: 2.7rem;
    box-shadow: none !important;
    font-weight: 600 !important;
}
button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: #CCAD61 !important;
    border-color: #CCAD61 !important;
    color: #20372C !important;
}
[data-testid="stButton"] button:hover,
[data-testid="stDownloadButton"] button:hover {
    border-color: #B89A52 !important;
    background: #F8F0D8 !important;
}
button[kind="primary"]:hover { background: #C2A153 !important; }

/* Tabs */
button[role="tab"] {
    color: #20372C !important;
    font-weight: 600 !important;
}
button[role="tab"][aria-selected="true"] {
    color: #20372C !important;
}

/* Cards and expanders */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E1E7E2;
    border-radius: 16px;
    padding: 12px 16px;
}
[data-testid="stExpander"] details {
    border: 1px solid #E1E7E2 !important;
    border-radius: 14px !important;
    background: #FFFFFF !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
}
.card-box {
    background: #FFFFFF;
    border: 1px solid #E1E7E2;
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 12px;
}
.card-title { font-size: 1.05rem; font-weight: 700; color: #20372C; margin: 0 0 6px 0; }
.card-sub { color: #6F7F74; font-size: 0.96rem; margin: 0; }
.status-pill {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    background: #F4EACA;
    color: #6B5621;
    margin-bottom: 8px;
}
.status-pill.gray { background: #EEF2EE; color: #516257; }
.status-pill.green { background: #E7F4EA; color: #326947; }
.summary-box {
    background: #FFFFFF;
    border: 1px solid #E1E7E2;
    border-radius: 16px;
    padding: 18px 20px;
    min-height: 104px;
}
.summary-label { color: #7E8F83; font-size: .95rem; margin-bottom: 8px; }
.summary-value { color: #20372C; font-size: 2rem; font-weight: 760; line-height: 1; }
.table-wrap {
    background: #FFFFFF;
    border: 1px solid #E1E7E2;
    border-radius: 16px;
    overflow: hidden;
}
.table-clean {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
}
.table-clean th {
    text-align: left;
    background: #F5F7F5;
    color: #20372C;
    font-weight: 700;
    padding: 12px 14px;
    border-bottom: 1px solid #E1E7E2;
}
.table-clean td {
    padding: 12px 14px;
    border-bottom: 1px solid #EDF1EE;
    color: #20372C;
    vertical-align: top;
}
.table-clean tr:last-child td { border-bottom: none; }
.muted { color: #839287 !important; }
.small-gap { margin-top: .3rem; }

@media (max-width: 760px) {
    .block-container { padding: 1rem .85rem 3rem !important; }
    h1 { font-size: 2rem !important; }
    .summary-value { font-size: 1.7rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

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
            st.markdown(f"<div class='card-sub'>{subtitle}</div>", unsafe_allow_html=True)
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
        html.append(f"<th>{col}</th>")
    html.append("</tr></thead><tbody>")
    for _, row in df.iterrows():
        html.append("<tr>")
        for col in df.columns:
            html.append(f"<td>{row[col]}</td>")
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

    period_cols = st.columns([1.2, 1.2, 4], gap="small")
    view = period_cols[0].radio("Periode", ["Alle kommende", "Vælg uge"], horizontal=True, label_visibility="collapsed")
    if view == "Vælg uge":
        chosen = period_cols[1].date_input("Vælg uge", date.today(), label_visibility="collapsed")
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
        st.info("Ingen offentliggjorte vagter matcher dine filtre.")
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
        st.info("Du har ingen kommende vagter.")
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
        with st.form("wish"):
            d = st.date_input("Jeg kan ikke arbejde denne dag", min_value=date.today())
            note = st.text_input("Bemærkning (valgfri)")
            if st.form_submit_button("Gem friønske", type="primary"):
                try:
                    db.table("unavailability").insert({"employee_id": me["id"], "day": d.isoformat(), "note": note}).execute()
                    refresh()
                except Exception as e:
                    fail(e)
    else:
        st.info("Der er ikke åbent for nye friønsker lige nu.")

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
    st.subheader("Timer")
    chosen_month = st.date_input("Vælg måned", date.today().replace(day=1))
    month = chosen_month.strftime("%Y-%m")
    visible = [
        s for s in shifts
        if s["published"] and s["shift_day"].startswith(month) and (admin or s["employee_id"] == me["id"])
    ]
    rows = [
        {
            "Dato": s["shift_day"],
            "Navn": names.get(s["employee_id"], "Ledig"),
            "Funktion": s["position"],
            "Fra": s["start_time"][:5],
            "Til": s["end_time"][:5],
            "Planlagte timer": str(hours(s)).replace(".", ","),
        }
        for s in visible
    ]
    df = pd.DataFrame(rows, columns=["Dato", "Navn", "Funktion", "Fra", "Til", "Planlagte timer"])

    total_hours = sum(hours(s) for s in visible)
    s1, s2 = st.columns(2, gap="small")
    with s1:
        summary_card("Planlagte timer", f"{total_hours:.2f}".replace(".", ","))
    with s2:
        summary_card("Antal vagter", len(visible))

    if df.empty:
        st.info("Ingen vagter i den valgte måned.")
    else:
        render_html_table(df)
        st.caption("Timerne er planlagte, ikke faktiske arbejdstimer. Pauser er ikke fratrukket.")
        summary = (
            pd.DataFrame([{"Navn": names.get(s["employee_id"], "Ledig"), "Timer": hours(s)} for s in visible])
            .groupby("Navn", as_index=False)["Timer"].sum()
        )
        summary["Timer"] = summary["Timer"].map(lambda x: f"{x:.2f}".replace(".", ","))
        st.markdown("### Timer pr. medarbejder")
        render_html_table(summary)
        buf = io.BytesIO()
        export_df = df.copy()
        export_sum = summary.copy()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Vagter")
            export_sum.to_excel(writer, index=False, sheet_name="Oversigt")
        st.download_button(
            "Download Excel",
            buf.getvalue(),
            file_name=f"SGK_vagttimer_{month}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

elif page == "Administration" and admin:
    st.subheader("Administration")
    tab1, tab2, tab3, tab4 = st.tabs(["Opret vagt", "Styr vagter", "Friønsker", "Medarbejdere"])

    with tab1:
        st.caption("Opret nye vagter og vælg, om de skal være ledige, tildelt eller låste.")
        with st.form("new_shift", clear_on_submit=True):
            dcol1, dcol2 = st.columns([1.2, 1.8], gap="small")
            day = dcol1.date_input("Dato", date.today())
            position = dcol2.selectbox("Funktion", ["Tjener", "Opvasker"])

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

    with tab2:
        st.caption("Ændringer gemmes direkte. Ikke-offentliggjorte vagter kan kun ses af admin.")
        upcoming = sorted(
            [s for s in shifts if s["shift_day"] >= date.today().isoformat()],
            key=lambda s: (s["shift_day"], s["start_time"]),
        )
        if not upcoming:
            st.info("Ingen kommende vagter")
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

    with tab3:
        current_deadline = None
        if settings and settings[0].get("wishes_deadline"):
            current_deadline = date.fromisoformat(settings[0]["wishes_deadline"])
        new_deadline = st.date_input("Frist for friønsker", value=current_deadline or (date.today() + timedelta(days=14)))
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
            st.info("Ingen friønsker registreret.")

    with tab4:
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
