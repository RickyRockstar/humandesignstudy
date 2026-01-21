from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid
import os
import csv

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# -----------------------------
# VALID OPTIONS
# -----------------------------
VALID_TYPES = ["Generator","Manifesting Generator","Projector","Manifestor","Reflector"]
VALID_PROFILES = ["1/3","1/4","2/4","2/5","3/5","3/6","4/6","4/1","5/1","5/2","6/2","6/3"]
VALID_AUTHORITIES = ["Emotional","Sakral","Splenisch","Ego","Selbst-projiziert","Umwelt","Lunar"]

# -----------------------------
# DATA FOLDER
# -----------------------------
os.makedirs("data", exist_ok=True)
CSV_FILE = "data/responses.csv"

# -----------------------------
# HOME → CONSENT
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse(url="/consent", status_code=303)

@app.get("/consent", response_class=HTMLResponse)
def consent(request: Request):
    return templates.TemplateResponse("consent.html", {"request": request})

@app.post("/consent-submit")
def consent_submit(
    age_group: str = Form(...),
    gender: str = Form(...),
    agree: str = Form(...)
):
    if agree != "yes":
        raise HTTPException(status_code=400, detail="Consent required.")
    participant_id = str(uuid.uuid4())
    return RedirectResponse(
        url=f"/hd-instructions?participant_id={participant_id}&age_group={age_group}&gender={gender}",
        status_code=303
    )

# -----------------------------
# HD INSTRUCTIONS
# -----------------------------
@app.get("/hd-instructions", response_class=HTMLResponse)
def hd_instructions(request: Request,
                    participant_id: str,
                    age_group: str,
                    gender: str,
                    hd_known: Optional[str] = None):
    return templates.TemplateResponse(
        "hd_instructions.html",
        {"request": request,
         "participant_id": participant_id,
         "age_group": age_group,
         "gender": gender,
         "hd_known": hd_known
         }
    )

# -----------------------------
# HD ENTRY
# -----------------------------
@app.get("/hd-entry", response_class=HTMLResponse)
def hd_entry(request: Request,
             participant_id: str,
             age_group: str,
             gender: str,
             hd_known: str):
    return templates.TemplateResponse(
        "hd_entry.html",
        {
            "request": request,
            "participant_id": participant_id,
            "age_group": age_group,
            "gender": gender,
            "types": VALID_TYPES,
            "profiles": VALID_PROFILES,
            "authorities": VALID_AUTHORITIES,
            "hd_known": hd_known
        }
    )

# -----------------------------
# QUESTIONNAIRE
# -----------------------------
@app.post("/questionnaire", response_class=HTMLResponse)
def questionnaire(
    request: Request,
    participant_id: str = Form(...),
    age_group: str = Form(...),
    gender: str = Form(...),
    hd_type: str = Form(...),
    profile: str = Form(...),
    authority: str = Form(...),
    hd_known: str = Form(...)
):
    if hd_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail="Ungültiger Typ.")
    if profile not in VALID_PROFILES:
        raise HTTPException(status_code=400, detail="Ungültiges Profil.")
    if authority not in VALID_AUTHORITIES:
        raise HTTPException(status_code=400, detail="Ungültige Inner Authority.")

    return templates.TemplateResponse(
        "questionnaire.html",
        {
            "request": request,
            "participant_id": participant_id,
            "age_group": age_group,
            "gender": gender,
            "hd_type": hd_type,
            "profile": profile,
            "authority": authority,
            "hd_known": hd_known
        }
    )

# -----------------------------
# SUBMIT RESPONSES
# -----------------------------
@app.post("/submit-responses", response_class=HTMLResponse)
def submit_responses(
    request: Request,
    participant_id: str = Form(...),
    age_group: str = Form(...),
    gender: str = Form(...),
    hd_type: str = Form(...),
    profile: str = Form(...),
    authority: str = Form(...),
    hd_known: str = Form(...),

    q1: str = Form(...), q2: str = Form(...), q3: str = Form(...), q4: str = Form(...),
    q5: str = Form(...), q6: str = Form(...), q7: str = Form(...), q8: str = Form(...),
    q9: str = Form(...), q10: str = Form(...), q11: str = Form(...), q12: str = Form(...),
    q13: str = Form(...), q14: str = Form(...), q15: str = Form(...)
):
    # Convert all responses to int safely
    try:
        qs = [int(q) for q in [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15]]
    except ValueError:
        raise HTTPException(status_code=400, detail="Alle Fragen müssen beantwortet werden.")

    # Reverse scoring
    for idx in [0,4,6,7,11,13]:  # q1,q5,q7,q8,q12,q14
        qs[idx] = 6 - qs[idx]

    extraversion = round(sum(qs[0:3])/3, 2)
    freundlich = round(sum(qs[3:6])/3, 2)
    gewissenhaft = round(sum(qs[6:9])/3, 2)
    emotionale_labilitaet = round(sum(qs[9:12])/3, 2)
    offenheit = round(sum(qs[12:15])/3, 2)

    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "participant_id","age_group","gender","hd_type","profile","authority","hd_known",
                "q1","q2","q3","q4","q5","q6","q7","q8","q9",
                "q10","q11","q12","q13","q14","q15",
                "extraversion","freundlich","gewissenhaft",
                "emotionale_labilitaet","offenheit"
            ])
        writer.writerow([participant_id, age_group, gender, hd_type, profile, authority,hd_known, *qs,
                         extraversion, freundlich, gewissenhaft, emotionale_labilitaet, offenheit])

    return templates.TemplateResponse(
        "bf5_summary.html",
        {
            "request": request,
            "extraversion": extraversion,
            "freundlich": freundlich,
            "gewissenhaft": gewissenhaft,
            "emotionale_labilitaet": emotionale_labilitaet,
            "offenheit": offenheit
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)