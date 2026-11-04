# SGK Café – Vagtplan (MVP)

Streamlit + GitHub + Supabase. Ingen medarbejderbilleder. Mobilvenlig ugevisning.

## Funktioner i første version
- E-mail/adgangskode-login gennem Supabase Authentication
- Roller: administrator og medarbejder
- Ugeoversigt med tjener-/opvaskervagter kl. 07.00–00.00
- Admin opretter, tildeler, udbyder, låser, offentliggør, redigerer og sletter vagter
- Medarbejdere tilbyder deres egne ulåste vagter og overtager vagter i ét atomisk databasekald
- Friønsker inden adminbestemt frist
- Oversigt over planlagte timer og Excel-eksport

## Kom i gang
1. Opret et privat repository på GitHub og upload alle filer fra denne mappe.
2. Opret et projekt i Supabase (vælg en passende EU-region) og åbne **SQL Editor**. Kør hele `schema.sql` én gang.
3. Under **Authentication → Users** opretter du din første bruger med e-mail og adgangskode (du kan invitere brugeren). Kopiér brugerens UUID.
4. I Supabase SQL Editor kører du (tilpas UUID/navn):
   ```sql
   insert into public.staff(id,name,role)
   values ('UUID-FRA-AUTH-USERS','Admin','admin');
   ```
5. Opret lokale secrets ved at kopiere `.streamlit/secrets.toml.example` til `.streamlit/secrets.toml`, og indsæt Supabase Project URL samt **publishable/anon key** fra Supabase. **Brug ALDRIG service_role/secret key i appen.**
6. Lokalt: `pip install -r requirements.txt` og derefter `streamlit run app.py`.
7. Til drift: Vælg en hostingplatform, der tillader personaledata og giver passende databehandleraftale. Tilføj samme variabler som miljøsecrets, og peg deployment på GitHub-repository og `app.py`.
8. Opret medarbejdere i Supabase Authentication → Users og registrer derefter deres UUID og navn under Administration i appen.

## Bemærkninger og begrænsninger
- Dette er en **første brugbar prototype**, ikke en færdig løn- eller arbejdstidsregistreringsløsning.
- Timer er **planlagte timer** og inkluderer pauser; ingen stempel-ur-funktion, løngodkendelse eller lovpligtig arbejdstidsdokumentation.
- Fraværsønsker er ikke automatisk en blokering ved administratorens tildeling; admin skal kontrollere dem.
- Administratorens ændringer og sletninger er endnu ikke fuldt audit-logget. Medarbejdernes overtagelser og udbud logges.
- Ingen pushbeskeder, bemandingskrav, vagtkopiering eller automatisk advarsel ved admin-tildeling af overlappende vagter i denne version.
- Administratoren kan tildele en vagt til en person uanset kompetenceflag; overtagelse er kompetencekontrolleret.
- Test opsætning, databaseadgang, brugerrettigheder og samtidige handlinger grundigt med testbrugere før rigtig drift.
- Opbevar ikke følsomme oplysninger i notes/friønsker.
- Brug private GitHub-repositories og HTTPS-hosting. Placér aldrig hemmelige nøgler i GitHub.
- Lovgivning, GDPR, backup, slettepolitik og databehandleraftaler skal vurderes før personaledata behandles i produktion.
