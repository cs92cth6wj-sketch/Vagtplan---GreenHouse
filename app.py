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
:root { color-scheme: light; }
.stApp, [data-testid="stAppViewContainer"] {background:#F7F8F5; color:#20372C;}
[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1120px; padding-top:2rem; padding-bottom:3rem;}
h1,h2,h3,h4 {color:#20372C; letter-spacing:-.02em;}
[data-testid="stWidgetLabel"] * {color:#20372C !important; font-weight:600;}
[data-testid="stCaptionContainer"] {color:#6E8074 !important;}
/* Individual widgets, no styling of all div/span/svg elements. */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stNumberInput"] [data-baseweb="input"] {
  background:#FFFFFF !important; color:#20372C !important;
  border:1px solid #CBD5CC !important; border-radius:10px !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] span,
[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-testid="stNumberInput"] input {
  color:#20372C !important; -webkit-text-fill-color:#20372C !important;
  caret-color:#20372C !important;
}
[data-baseweb="popover"] [role="listbox"], [role="listbox"], [role="option"] {
  background:#FFFFFF !important; color:#20372C !important;
}
[data-baseweb="popover"] [role="option"] *, [role="option"] * { color:#20372C !important; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button {
  background:#FFFFFF !important; color:#20372C !important;
  border:1px solid #C9D5CC !important; border-radius:11px !important;
  min-height:2.55rem; font-weight:600;
}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
  background:#CCAD61 !important; border-color:#CCAD61 !important;
  color:#20372C !important;
}
button[role="tab"],button[role="tab"] * {color:#20372C !important;}
[data-testid="stExpander"] details {background:#FFFFFF; border-radius:12px;}
[data-testid="stPopoverBody"] {background:#FFFFFF !important; color:#20372C !important; border:1px solid #E1E7E2 !important;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px;}
.status-pill {display:inline-block;padding:4px 10px;border-radius:50px;
  font-size:.81rem;font-weight:650;background:#F4EACA;color:#6B5621;margin-bottom:7px;}
.status-pill.gray {background:#EEF2EE;color:#516257;}
.status-pill.green {background:#E7F4EA;color:#326947;}
.card-title {font-size:1.03rem;font-weight:730;color:#20372C;margin:2px 0;}
.card-sub {font-size:.93rem;color:#6B7C70;margin-top:4px;}
.summary-box {background:#FFFFFF;border:1px solid #E1E7E2;border-radius:14px;
  padding:14px 18px;min-height:88px;}
.summary-label {color:#6F8175;font-size:.9rem;margin-bottom:7px;}
.summary-value {color:#20372C;font-size:1.75rem;font-weight:740;line-height:1.2;}
.table-wrap {border:1px solid #E1E7E2;border-radius:13px;overflow-x:auto;background:#FFF;}
.table-clean {width:100%;border-collapse:collapse;font-size:.91rem;}
.table-clean th {text-align:left;background:#F2F5F1;color:#20372C;padding:11px 13px;white-space:nowrap;}
.table-clean td {color:#20372C;padding:11px 13px;border-top:1px solid #ECF0ED;}
@media(max-width:760px){.block-container{padding:1rem .8rem 3rem !important;}
 h1{font-size:1.85rem !important;}}
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
    """Lys kalender bygget med Streamlits egne knapper i stedet for den mørke BaseWeb-datopopup."""
    if key not in st.session_state:
        st.session_state[key] = max(initial or date.today(), min_date) if min_date else (initial or date.today())
    if key + "_month" not in st.session_state:
        st.session_state[key + "_month"] = st.session_state[key].replace(day=1)
    chosen = st.session_state[key]
    st.markdown(f"**{label}**")
    with st.popover(f"{chosen:%d/%m/%Y}  ·  Vælg dato", use_container_width=True):
        month_start = st.session_state[key + "_month"]
        previous, heading, following = st.columns([1, 4, 1], vertical_alignment="center")
        if previous.button("‹", key=key + "_prev", use_container_width=True):
            y, m = month_start.year, month_start.month - 1
            if m == 0: y, m = y - 1, 12
            st.session_state[key + "_month"] = date(y, m, 1)
            st.rerun()
        heading.markdown(f"**{DANISH_MONTHS[month_start.month-1].capitalize()} {month_start.year}**")
        if following.button("›", key=key + "_next", use_container_width=True):
            y, m = month_start.year, month_start.month + 1
            if m == 13: y, m = y + 1, 1
            st.session_state[key + "_month"] = date(y, m, 1)
            st.rerun()
        for col, dayname in zip(st.columns(7, gap="small"), DANISH_DAYS):
            col.markdown(f"<div style='text-align:center;color:#637367;font-weight:650'>{dayname}</div>", unsafe_allow_html=True)
        for week in calendar.monthcalendar(month_start.year, month_start.month):
            cols = st.columns(7, gap="small")
            for column, day_number in zip(cols, week):
                if day_number == 0:
                    column.write(" ")
                    continue
                this_date = date(month_start.year, month_start.month, day_number)
                is_disabled = min_date is not None and this_date < min_date
                if column.button(str(day_number), key=f"{key}_{this_date.isoformat()}",
                                 disabled=is_disabled, type="primary" if this_date == chosen else "secondary",
                                 use_container_width=True):
                    st.session_state[key] = this_date
                    st.rerun()
    return chosen


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
        st.info("Ingen tildelte vagter i den valgte måned.")
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
    tab1, tab2, tab3, tab4 = st.tabs(["Opret vagt", "Styr vagter", "Friønsker", "Medarbejdere"])

    with tab1:
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
