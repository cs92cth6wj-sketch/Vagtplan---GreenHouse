import io
from datetime import date, datetime, timedelta, time
import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="SGK Café | Vagtplan",page_icon="📅",layout="wide",initial_sidebar_state="collapsed")
# En ensartet lys visning på både mobil og desktop.
# Farverne er også fastlagt i .streamlit/config.toml.
st.markdown("""<style>
:root { color-scheme: light; }
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] {
  background-color:#F8F9F7 !important; color:#21352B !important;
}
[data-testid="stHeader"] { background:transparent !important; }
.block-container { max-width:1080px !important; padding-top:2.8rem !important; padding-bottom:3rem !important; }
h1,h2,h3,h4 { color:#21352B !important; letter-spacing:-.02em; }
h1 { font-weight:760 !important; }
[data-testid="stCaptionContainer"] { color:#6E8074 !important; }
[data-testid="stWidgetLabel"] *, [data-testid="stWidgetLabel"] { color:#21352B !important; }
/* Apply matching backgrounds and foregrounds to both the input and its wrapper. */
[data-baseweb="input"],[data-baseweb="base-input"],
[data-baseweb="select"],[data-baseweb="select"]>div,
[data-baseweb="textarea"] {background:#FFF !important; color:#21352B !important; border-color:#C6D2C9 !important;}
[data-baseweb="input"] input,[data-baseweb="base-input"] input,
[data-baseweb="select"] input,textarea,input {
  color:#21352B !important; -webkit-text-fill-color:#21352B !important;
  caret-color:#21352B !important; color-scheme:light !important;
}
[data-baseweb="select"] *,[data-baseweb="input"] svg {color:#21352B !important;}
[data-baseweb="popover"],[data-baseweb="menu"],[data-baseweb="calendar"],
[role="listbox"],[role="option"] {background:#FFF !important;color:#21352B !important;}
[data-baseweb="popover"] *,[data-baseweb="menu"] *,[data-baseweb="calendar"] *,[role="option"] * {color:#21352B !important;}
/* All navigation uses Streamlit buttons, never segmented-control dark pills. */
[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button,
[data-testid="stDownloadButton"] button {
  background:#FFF !important; color:#21352B !important;
  border:1px solid #CED9D0 !important; border-radius:11px !important;
  min-height:2.5rem; box-shadow:none !important;
}
[data-testid="stButton"] button *,[data-testid="stFormSubmitButton"] button * {color:inherit !important;}
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
  background:#CCAD61 !important;color:#21352B !important;border-color:#CCAD61 !important;
  font-weight:650 !important;
}
[data-testid="stButton"] button:hover {border-color:#B69A55 !important; background:#F8F0DA !important;}
[data-testid="stButton"] button[kind="primary"]:hover {background:#C2A153 !important;}
[data-testid="stMetric"] {background:#FFF !important;border:1px solid #E4E9E5; padding:12px 16px;border-radius:12px;}
/* Shift cards are native st.container(border=True) – visible with a compact layout. */
[data-testid="stVerticalBlockBorderWrapper"]>div[style*="border"],
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:14px !important;}
@media(max-width:750px) {
  .block-container {padding:1.1rem .8rem 3rem !important;}
  h1 {font-size:1.85rem !important;}
  [data-testid="stHorizontalBlock"] {gap:.4rem !important;}
  [data-testid="stButton"] button {font-size:.8rem !important;}
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

def shift_state(s):
    # En udbudt, allerede tildelt vagt forbliver medarbejderens ansvar
    # indtil en anden overtager via den atomiske databasefunktion.
    if s["offered"]:
        return "Til overtagelse" if s["employee_id"] else "Ledig"
    return "Besat" if s["employee_id"] else "Ikke tildelt"


def display_shift(s, names):
    owner = names.get(s["employee_id"], "Ikke tildelt")
    status = shift_state(s)
    lock = " · Låst" if s["locked"] else ""
    return f'{s["start_time"][:5]}–{s["end_time"][:5]} · {s["position"]} · {owner} · {status}{lock}'


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
if st.session_state.get("active_page") not in pages:
    st.session_state.active_page="Vagtplan"
nav_cols=st.columns(len(pages),gap="small")
for col,nav_page in zip(nav_cols,pages):
    if col.button(nav_page, key="nav_"+nav_page, type="primary" if st.session_state.active_page==nav_page else "secondary", use_container_width=True):
        st.session_state.active_page=nav_page
        st.rerun()
page=st.session_state.active_page
try:
    shifts=get("shifts")
    wishes=get("unavailability")
    settings=get("settings")
except Exception as e:
    fail(e);st.stop()

if page=="Vagtplan":
    st.subheader("Vagtoversigt")
    st.caption("Kun offentliggjorte vagter. Ubesatte og udbudte vagter kan overtages; øvrige viser, hvem der er på arbejde.")
    view=st.radio("Vis periode", ["Alle kommende", "Vælg uge"], horizontal=True, label_visibility="collapsed")
    if view=="Vælg uge":
        chosen=st.date_input("Vælg en dato i ugen", date.today())
        first,last=dates_of_week(chosen)
        st.caption(f"Uge {first.isocalendar().week} · {first:%d/%m}–{last:%d/%Y}")
    else:
        first=date.today()
        last=None
    c_filter,c_role=st.columns(2, gap="small")
    availability=c_filter.selectbox("Status", ["Alle vagter", "Ledige / til overtagelse", "Besatte"])
    kind=c_role.selectbox("Funktion", ["Alle", "Tjener", "Opvasker"])
    published=[s for s in shifts
               if s["published"]
               and s["shift_day"]>=first.isoformat()
               and (last is None or s["shift_day"]<=last.isoformat())
               and (kind=="Alle" or s["position"]==kind)
               and (availability=="Alle vagter" or
                    (availability=="Ledige / til overtagelse" and s["offered"]) or
                    (availability=="Besatte" and not s["offered"] and s["employee_id"]))]
    published.sort(key=lambda s:(s["shift_day"],s["start_time"],s["position"]))
    offered_count=sum(bool(s["offered"]) for s in published)
    a,b=st.columns(2)
    a.metric("Viste vagter",len(published))
    b.metric("Ledige / til overtagelse",offered_count)
    if not published:
        st.info("Ingen offentliggjorte vagter matcher dine filtre.")
    else:
        weekdays=["Mandag","Tirsdag","Onsdag","Torsdag","Fredag","Lørdag","Søndag"]
        grouped={}
        for shift in published:
            grouped.setdefault(shift["shift_day"], []).append(shift)
        # Only dates with published shifts are displayed.
        for day,items in grouped.items():
            d=date.fromisoformat(day)
            st.markdown(f"#### {weekdays[d.weekday()]} {d:%d/%m/%Y}")
            for shift in items:
                with st.container(border=True):
                    details,action=st.columns([4,1.2],gap="small",vertical_alignment="center")
                    with details:
                        state=shift_state(shift)
                        st.markdown(f'**{shift["start_time"][:5]}–{shift["end_time"][:5]}  ·  {shift["position"]}**')
                        if shift["offered"] and shift["employee_id"]:
                            st.caption(f'Ledig til overtagelse · Ansvarlig indtil overtagelse: {names.get(shift["employee_id"],"Ukendt")}')
                        elif shift["offered"]:
                            st.caption("Ledig · Ingen medarbejder tildelt")
                        else:
                            st.caption(f'{state} · {names.get(shift["employee_id"],"Ikke tildelt")}{" · Låst" if shift["locked"] else ""}')
                        if shift.get("notes"):
                            st.caption(shift["notes"])
                    with action:
                        if shift["offered"] and not shift["locked"] and shift["employee_id"]!=me["id"]:
                            if st.button("Overtag",key="claim_"+shift["id"],type="primary",use_container_width=True):
                                try:
                                    db.rpc("claim_shift",{"p_shift":shift["id"]}).execute()
                                    st.success("Vagten er overtaget")
                                    refresh()
                                except Exception as e: fail(e)
                        elif shift["employee_id"]==me["id"] and not shift["locked"]:
                            if st.button("Træk tilbage" if shift["offered"] else "Udbyd",key="offer_"+shift["id"],use_container_width=True):
                                try:
                                    fn="cancel_my_offer" if shift["offered"] else "offer_my_shift"
                                    db.rpc(fn,{"p_shift":shift["id"]}).execute()
                                    refresh()
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
