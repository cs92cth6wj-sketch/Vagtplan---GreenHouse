import io
from datetime import date, datetime, timedelta, time
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="SGK Café | Vagtplan",page_icon="📅",layout="wide",initial_sidebar_state="collapsed")
# En ensartet lys visning på både mobil og desktop.
# Farverne er også fastlagt i .streamlit/config.toml.
st.markdown("""<style>
/* SGK design: alle kontroller har lyse flader og læsbar mørk tekst. */
:root { color-scheme: light; }
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
  background: #F8F9F7 !important;
  color: #21352B !important;
}
[data-testid="stHeader"] { background: rgba(248,249,247,.97) !important; }
[data-testid="stSidebar"] { background: #EDF1EB !important; }
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] span,
[data-testid="stAppViewContainer"] small,
[data-testid="stAppViewContainer"] .stMarkdown { color: #21352B; }
h1 { color: #21352B !important; font-weight: 750 !important; letter-spacing: -.025em; }
h2,h3 { color: #21352B !important; }
/* Inputs & baseweb wrappers (date, select, segmented control) */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stTimeInput"] [data-baseweb="input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"] {
  background-color: #FFFFFF !important;
  border: 1px solid #C8D2CA !important;
  border-radius: 9px !important;
}
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTimeInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background: #FFFFFF !important;
  color: #21352B !important;
  -webkit-text-fill-color: #21352B !important;
  caret-color: #21352B !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder { color: #79867D !important; -webkit-text-fill-color: #79867D !important; }
[data-testid="stDateInput"] svg,
[data-testid="stSelectbox"] svg,
[data-testid="stMultiSelect"] svg { fill: #21352B !important; color: #21352B !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * { color: #21352B !important; }
/* Streamlit dropdowns/datepicker are portaled outside the app container. */
[data-baseweb="popover"], [data-baseweb="menu"],
[data-baseweb="calendar"], [role="listbox"], [role="option"] {
  background: #FFFFFF !important; color: #21352B !important;
}
[data-baseweb="popover"] *, [data-baseweb="menu"] *,
[data-baseweb="calendar"] * { color: #21352B !important; }
[role="option"][aria-selected="true"] { background: #F1E5C6 !important; }
/* Radio navigation and segmented controls */
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label { color: #21352B !important; }
[data-testid="stRadio"] label span,
[data-testid="stCheckbox"] label span { color: #21352B !important; }
[data-testid="stSegmentedControl"] [data-baseweb="button-group"] {
  background: #FFFFFF !important; border: 1px solid #D5DED6 !important; border-radius: 9px !important;
}
[data-testid="stSegmentedControl"] button {
  background: #FFFFFF !important; color: #21352B !important; border-color: #D5DED6 !important;
}
[data-testid="stSegmentedControl"] button[aria-pressed="true"],
[data-testid="stSegmentedControl"] button[data-active="true"] {
  background: #F1E5C6 !important; color: #21352B !important;
}
[data-testid="stSegmentedControl"] button * { color: #21352B !important; }
/* Buttons: no destructive red fallback */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
  border-radius: 9px !important; font-weight: 600 !important;
  color: #21352B !important; background: #FFFFFF !important; border: 1px solid #BCCABC !important;
}
.stButton button:hover, .stFormSubmitButton button:hover, .stDownloadButton button:hover {
  background: #F1E5C6 !important; border-color: #CCAD61 !important; color: #21352B !important;
}
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"],
.stDownloadButton button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
  background: #CCAD61 !important; border: 1px solid #B89A4D !important; color: #172A20 !important;
}
.stButton button[kind="primary"] *, .stFormSubmitButton button[kind="primary"] * { color: #172A20 !important; }
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: 12px !important;
}
[data-testid="stMetric"] { background: #FFFFFF !important; padding: 14px !important; border: 1px solid #E0E8E0 !important; }
[data-testid="stVerticalBlockBorderWrapper"] > div { background-color: #FFFFFF !important; }
[data-testid="stTabs"] button { color: #21352B !important; }
[data-testid="stTabs"] button[aria-selected="true"] { border-bottom-color: #CCAD61 !important; }
[data-testid="stDataFrame"] { border-radius: 9px; overflow: hidden; }
@media (max-width: 700px) {
  .block-container { padding-top: 1.4rem !important; padding-left: .85rem !important; padding-right: .85rem !important; }
  h1 { font-size: 1.85rem !important; }
  [data-testid="stRadio"] [role="radiogroup"] { gap: .35rem !important; }
}
</style>""", unsafe_allow_html=True)

try:
    URL=st.secrets["SUPABASE_URL"]
    KEY=st.secrets["SUPABASE_ANON_KEY"]
except KeyError:
    st.error("Tilføj SUPABASE_URL og SUPABASE_ANON_KEY i Streamlit Secrets.")
    st.stop()

if "db" not in st.session_state:
    st.session_state.db=create_client(URL,KEY)
db=st.session_state.db

def get(table):
    return db.table(table).select("*").execute().data or []

def fail(e):
    st.error(f"Handlingen kunne ikke gennemføres: {e}")

def refresh():
    st.rerun()

def dates_of_week(day):
    monday=day-timedelta(days=day.weekday())
    return monday,monday+timedelta(days=6)

def hours(s):
    a=datetime.strptime(s["start_time"][:5],"%H:%M")
    b=datetime.strptime(s["end_time"][:5],"%H:%M")
    if b<=a: b+=timedelta(days=1)
    return round((b-a).total_seconds()/3600,2)

def display_shift(s,names):
    lock=" · 🔒" if s["locked"] else ""
    offer=" · LEDIG" if s["offered"] else ""
    return f'{s["start_time"][:5]}–{s["end_time"][:5]} · {s["position"]} · {names.get(s["employee_id"],"Ikke tildelt")}{lock}{offer}'

st.title("SGK Café · Vagtplan")
st.caption("Silkeborg Golfklub · Overblik over caféens vagter")
if "user" not in st.session_state:
    with st.form("login"):
        email=st.text_input("E-mail")
        password=st.text_input("Adgangskode",type="password")
        sent=st.form_submit_button("Log ind",type="primary")
    if sent:
        try:
            resp=db.auth.sign_in_with_password({"email":email,"password":password})
            st.session_state.user=resp.user.id
            refresh()
        except Exception:
            st.error("Login mislykkedes. Tjek e-mail og adgangskode.")
    st.stop()

try:
    current=db.auth.get_user()
    if not current or not current.user or current.user.id!=st.session_state.user:
        raise ValueError("Login udløbet")
    staff=get("staff")
    me=next((x for x in staff if x["id"]==current.user.id and x["active"]),None)
    if not me:
        st.warning("Din konto er endnu ikke aktiveret som medarbejder. Kontakt administrator.")
        if st.button("Log ud"):
            db.auth.sign_out();st.session_state.clear();refresh()
        st.stop()
except Exception as e:
    st.session_state.clear()
    st.warning("Sessionen er udløbet. Log ind igen.")
    st.stop()

admin=me["role"]=="admin"
names={x["id"]:x["name"] for x in staff}
with st.sidebar:
    st.write(f'Logget ind: **{me["name"]}**')
    if st.button("Log ud"):
        db.auth.sign_out();st.session_state.clear();refresh()

pages=["Vagtplan","Mine vagter","Friønsker","Timer"]+(["Administration"] if admin else [])
page=st.radio("Navigation",pages,horizontal=True,label_visibility="collapsed")
try:
    shifts=get("shifts")
    wishes=get("unavailability")
    settings=get("settings")
except Exception as e:
    fail(e);st.stop()

if page=="Vagtplan":
    week=st.date_input("Vælg en dato i ugen",date.today())
    monday,sunday=dates_of_week(week)
    st.subheader(f"Uge {monday.isocalendar().week} · {monday:%d/%m}–{sunday:%d/%Y}")
    kind=st.segmented_control("Vis vagter",["Alle","Tjener","Opvasker"],default="Alle")
    current_shifts=[s for s in shifts if monday<=date.fromisoformat(s["shift_day"])<=sunday and (kind=="Alle" or s["position"]==kind)]
    for i in range(7):
        d=monday+timedelta(days=i)
        day_shifts=sorted([s for s in current_shifts if s["shift_day"]==d.isoformat()],key=lambda x:x["start_time"])
        with st.container(border=True):
            st.markdown(f"**{['Mandag','Tirsdag','Onsdag','Torsdag','Fredag','Lørdag','Søndag'][i]} {d:%d/%m}**")
            if not day_shifts: st.caption("Ingen vagter")
            for s in day_shifts:
                a,b=st.columns([5,2])
                a.write(display_shift(s,names))
                if s["offered"] and not s["locked"] and s["employee_id"]!=me["id"]:
                    if b.button("Overtag",key="claim_"+s["id"]):
                        try: db.rpc("claim_shift",{"p_shift":s["id"]}).execute();st.success("Vagten er overtaget");refresh()
                        except Exception as e: fail(e)
                elif s["employee_id"]==me["id"] and not s["locked"]:
                    if b.button("Annuller udbud" if s["offered"] else "Udbyd vagt",key="offer_"+s["id"]):
                        try:
                            fn="cancel_my_offer" if s["offered"] else "offer_my_shift"
                            db.rpc(fn,{"p_shift":s["id"]}).execute();refresh()
                        except Exception as e: fail(e)

elif page=="Mine vagter":
    mine=sorted([s for s in shifts if s["employee_id"]==me["id"] and s["shift_day"]>=date.today().isoformat()],key=lambda x:(x["shift_day"],x["start_time"]))
    st.metric("Kommende vagter",len(mine))
    for s in mine:
        st.write(f'**{s["shift_day"]}** · {display_shift(s,names)}')
    if not mine: st.info("Du har ingen kommende vagter.")

elif page=="Friønsker":
    deadline=settings[0].get("wishes_deadline") if settings else None
    st.caption(f'Frist for friønsker: {deadline or "Ikke fastsat"}')
    mine=[w for w in wishes if w["employee_id"]==me["id"]]
    if deadline and date.today()<=date.fromisoformat(deadline):
        with st.form("wish"):
            d=st.date_input("Jeg kan ikke arbejde denne dag",min_value=date.today())
            note=st.text_input("Bemærkning (valgfri)")
            if st.form_submit_button("Gem friønske",type="primary"):
                try:
                    db.table("unavailability").insert({"employee_id":me["id"],"day":d.isoformat(),"note":note}).execute();refresh()
                except Exception as e: fail(e)
    else:
        st.info("Der er ikke åbent for nye friønsker lige nu.")
    for w in sorted(mine,key=lambda x:x["day"]):
        a,b=st.columns([5,1]);a.write(f'{w["day"]} · {w["note"]}')
        if deadline and date.today()<=date.fromisoformat(deadline) and b.button("Slet",key=w["id"]):
            try: db.table("unavailability").delete().eq("id",w["id"]).execute();refresh()
            except Exception as e: fail(e)

elif page=="Timer":
    month=st.date_input("Vælg måned",date.today()).strftime("%Y-%m")
    visible=[s for s in shifts if s["published"] and s["shift_day"].startswith(month) and (admin or s["employee_id"]==me["id"])]
    rows=[{"Dato":s["shift_day"],"Navn":names.get(s["employee_id"],"Ledig"),"Funktion":s["position"],"Fra":s["start_time"][:5],"Til":s["end_time"][:5],"Planlagte timer":hours(s)} for s in visible]
    df=pd.DataFrame(rows,columns=["Dato","Navn","Funktion","Fra","Til","Planlagte timer"])
    st.metric("Planlagte timer",f'{df["Planlagte timer"].sum():.2f}'.replace(".",","))
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.caption("Timerne er planlagte, ikke faktiske arbejdstimer. Pauser er ikke fratrukket.")
    if not df.empty:
        summary=df.groupby("Navn",as_index=False)["Planlagte timer"].sum()
        st.subheader("Timer pr. medarbejder")
        st.dataframe(summary,use_container_width=True,hide_index=True)
        buf=io.BytesIO()
        with pd.ExcelWriter(buf,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Vagter")
            summary.to_excel(writer,index=False,sheet_name="Oversigt")
        st.download_button("Download Excel",buf.getvalue(),file_name=f"SGK_vagttimer_{month}.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif page=="Administration" and admin:
    tab1,tab2,tab3,tab4=st.tabs(["Opret vagt","Styr vagter","Friønsker","Medarbejdere"])
    with tab1:
        with st.form("new_shift",clear_on_submit=True):
            day=st.date_input("Dato",date.today())
            position=st.selectbox("Funktion",["Tjener","Opvasker"])
            c1,c2=st.columns(2)
            options=[f"{h:02d}:{m:02d}" for h in range(7,24) for m in (0,15,30,45)]+["00:00"]
            start=c1.selectbox("Fra",options[:-1],index=8)
            end=c2.selectbox("Til",options,index=36)
            choices={"Ledig (udbydes)":None,**{x["name"]+" · "+x["id"][:6]:x["id"] for x in staff if x["active"] and (x["can_waiter"] if position=="Tjener" else x["can_dishwasher"])}}
            who=st.selectbox("Tildel til",list(choices))
            locked=st.checkbox("Låst vagt (kun admin kan ændre)")
            publish=st.checkbox("Offentliggør straks",value=False)
            note=st.text_input("Bemærkning")
            submitted=st.form_submit_button("Opret vagt",type="primary")
        if submitted:
            if options.index(end)<=options.index(start): st.error("Sluttid skal ligge efter starttid (00:00 betyder midnat).")
            elif locked and choices[who] is None: st.error("Låste vagter skal tildeles en medarbejder.")
            else:
                try:
                    db.table("shifts").insert({"shift_day":day.isoformat(),"start_time":start,"end_time":end,"position":position,"employee_id":choices[who],"locked":locked,"published":publish,"offered":choices[who] is None and not locked,"notes":note}).execute()
                    st.success("Vagt oprettet")
                except Exception as e: fail(e)
    with tab2:
        st.caption("Ændringer gemmes direkte. Ikke-offentliggjorte vagter kan kun ses af admin.")
        upcoming=sorted([s for s in shifts if s["shift_day"]>=date.today().isoformat()],key=lambda s:(s["shift_day"],s["start_time"]))
        for s in upcoming:
            with st.expander(f'{s["shift_day"]} · {display_shift(s,names)} · {"Publiceret" if s["published"] else "Kladde"}'):
                opts={"Ledig":None,**{x["name"]+" · "+x["id"][:6]:x["id"] for x in staff if x["active"] and (x["can_waiter"] if s["position"]=="Tjener" else x["can_dishwasher"])}}
                existing=next((k for k,v in opts.items() if v==s["employee_id"]),"Ledig")
                who=st.selectbox("Medarbejder",list(opts),index=list(opts).index(existing),key="ass_"+s["id"])
                lock=st.checkbox("Låst",value=s["locked"],key="lock_"+s["id"])
                pub=st.checkbox("Offentliggjort",value=s["published"],key="pub_"+s["id"])
                c1,c2=st.columns(2)
                if c1.button("Gem ændringer",key="save_"+s["id"]):
                    if lock and opts[who] is None: st.error("Låst vagt kræver medarbejder")
                    else:
                        try:
                            db.table("shifts").update({"employee_id":opts[who],"locked":lock,"published":pub,"offered":opts[who] is None and not lock}).eq("id",s["id"]).execute();refresh()
                        except Exception as e: fail(e)
                if c2.button("Slet vagt",key="del_"+s["id"]):
                    try: db.table("shifts").delete().eq("id",s["id"]).execute();refresh()
                    except Exception as e: fail(e)
        if not upcoming: st.info("Ingen kommende vagter")
    with tab3:
        new_deadline=st.date_input("Frist for friønsker",value=date.fromisoformat(settings[0]["wishes_deadline"]) if settings and settings[0]["wishes_deadline"] else date.today()+timedelta(days=14))
        if st.button("Gem frist"):
            try: db.table("settings").update({"wishes_deadline":new_deadline.isoformat()}).eq("id",1).execute();refresh()
            except Exception as e: fail(e)
        for w in sorted(wishes,key=lambda x:x["day"]): st.write(f'{w["day"]} · **{names.get(w["employee_id"],"Ukendt")}** · {w["note"]}')
    with tab4:
        st.caption("Opret først brugeren i Supabase → Authentication → Users. Indsæt derefter brugerens UUID her.")
        with st.form("add_staff"):
            uid=st.text_input("Bruger-UUID fra Supabase")
            name=st.text_input("Navn")
            role=st.selectbox("Rolle",["employee","admin"])
            waiter=st.checkbox("Kan være tjener",True)
            dishwasher=st.checkbox("Kan være opvasker",True)
            if st.form_submit_button("Tilføj medarbejder"):
                try:
                    db.table("staff").insert({"id":uid.strip(),"name":name.strip(),"role":role,"can_waiter":waiter,"can_dishwasher":dishwasher}).execute();refresh()
                except Exception as e: fail(e)
        for person in staff: st.write(f'**{person["name"]}** · {"Admin" if person["role"]=="admin" else "Medarbejder"}')
