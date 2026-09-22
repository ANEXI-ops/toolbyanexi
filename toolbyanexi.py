# ═══════════════════════════════════════════════════════════
#  STUDENT FINDER BOT — AUTO-OSINT + TYPING + FLASK (Render)
# ═══════════════════════════════════════════════════════════

import os
import re
import html
import random
import hashlib
import asyncio
import urllib.parse
import threading
import requests
import dns.resolver
import phonenumbers
import pandas as pd
from phonenumbers import geocoder, carrier, timezone as ph_tz
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)

# ── Flask (Render ke liye) ──
from flask import Flask, jsonify

# ═══════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════
# Render pe environment variable se token milega, local pe fallback
BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN",
    "8676422370:AAGCUUz_jbecABc2gEkg1MxJcJ4QfCv3qLY"   # 👈 fallback (revoke kar)
)

EXCEL_FILE = "studentsdb3rdsem.xlsx"
CSV_FILES = [
    "students_data.csv",
    "feedback_sheet.csv",
    "feedback_sheet_2.csv",
]
HEADER_ROW = 2
MAX_RESULTS = 5
ENABLE_AUTO_OSINT = True

# ═══════════════════════════════════════════════
#  ROAST TARGET
# ═══════════════════════════════════════════════
TARGET_ENROLLMENT  = "256290305205"
TARGET_NAME_TOKENS = ["vishal", "vaghmarya", "fuljibhai"]
TARGET_EMAILS      = ["vshlone2@gmail.com", "jaydeeplala123@gmail.com"]
TARGET_MOBILES     = ["9727805566", "9979288800"]

ROASTS = [
    "😂 Abe yaar, <b>{q}</b> ko dhundh raha hai? Ye banda khud ko Google pe search karta hai!",
    "🔥 Wah bhai wah! <b>{q}</b> ka data chahiye? Pehle apni attendance 100% kar le!",
    "☝️ <b>{q}</b>?! Bhai ye toh college ka celebrity hai, iska data confidential hai 😎",
    "🤣 <b>{q}</b> ko search karne se pehle apna assignment complete kar le bhai!",
    "🚨 Alert! <b>{q}</b> ek legendary student hai — iska data sirf principal ke paas hai 😂",
    "💀 Bhai <b>{q}</b> ko kyu dhundh raha hai? Ye toh khud teachers ko dhundhta hai!",
    "🎯 <b>{q}</b>? Sorry bhai, VIP category. VIP ka data VIP ko milta hai 😏",
    "🤡 <b>{q}</b> search karne wale ko hum \"Time Waste Champion\" award dete hain 🏆",
    "😹 <b>{q}</b> toh star student hai — iske marks dekh ke Sharma ji ka beta bhi ro deta hai!",
    "🫡 <b>{q}</b> ka data? Pehle fee receipt dikha, phir sochta hoon 😂",
    "🔥 <b>{q}</b>?? Ye Insta pe bhi famous hai. Database chhota pad gaya iske liye 😎",
    "🤣 Bhai chill! <b>{q}</b> abhi canteen me samosa kha raha hai, baad me aana.",
    "💀 <b>{q}</b> ka data nahi milega. Yeh banda alag hi level ka hai bhai 😂",
    "🏆 <b>{q}</b>? Bhai ye toh legend hai. Iske liye alag database banwana padega 😅",
]

# ═══════════════════════════════════════════════
#  SCREENSHOT DATA
# ═══════════════════════════════════════════════
SCREENSHOT_DATA = {
    "256290305004": ("AHIR DHRUVKUMAR JAYESHBHAI",            "ahirjayesh269@gmail.com",           "9099821439"),
    "256290305006": ("AHIR MAYANKBHAI BIPINBHAI",             "ahirmayank87@gmail.com",            "7383624573"),
    "256290305008": ("BARIYA DHRUVKUMAR ASHVINBHAI",          "dhruvbariya766@gmail.com",          "9313876921"),
    "256290305010": ("BARIYA ROHIT MUKESH",                   "Sejalbariya29@gmail.com",           "9023379994"),
    "256290305012": ("BHIMDA SHUBHAMKUMAR NARENDRABHAI",      "bhimdashubham2009@gmail.com",       "8866311261"),
    "256290305013": ("BUTANI KRISHIV KIRITBHAI",              "Krishivbutani18025@gmail.com",      "9601785530"),
    "256290305015": ("CHAUHAN RAJVIR MAHENDRABHAI",           "sushilabenmchauhan2008@gmail.com",  "7069501390"),
    "256290305023": ("DIWAN AMAN PYARMADAR",                  "diwanaman2160@gmail.com",           "8160132906"),
    "256290305024": ("DIWAN MOHMMEDZAID ILYASAGANI",          "ZAIDGAMERZ2049@GMAIL.COM",          "9512305072"),
    "256290305026": ("GADARIYA MEET BHUPENDRASINH",           "ddharatigararia@gmail.com",         "9316167238"),
    "256290305028": ("GANDHI JENIL PRAGNESHKUMAR",            "gandhijenil1505@gmail.com",         "6352907051"),
    "256290305030": ("GHANCHI RIZAWAN YUNUSHBHAI",            "Ghanchiyunush438@gmail.com",        "7383902608"),
    "256290305034": ("GOHIL DHAVALBHAI MUKESHBHAI",           "gohildthaval0743@gmail.com",        "9773404691"),
    "256290305040": ("GOHIL NIRAV NARESHBHAI",                "gohilanresh971@gmail.com",          "9979388960"),
    "256290305050": ("KACHHIYA KUSHALKUMAR SANJAYBHAI",       "kachhiyakrinalkachhiya@gmail.com",  "9998079666"),
    "256290305055": ("KAYASTH NEEL PRADIPKUMAR",              "shetalkayasht271@gmail.com",        "9574859142"),
    "256290305065": ("MACHHI BHARGAV MUKESHBHAI",             "seemammachhi@gmail.com",            "9723468510"),
    "256290305068": ("MACHHI JAJUMAR JASHVANTBHAI",           "jaswantmachhi2017@gmail.com",       "9904936596"),
    "256290305070": ("MACHHI MOHIT RAKESHBHAI",               "kaddhadyas@gmail.com",              "76968697024"),
    "256290305071": ("MACHHI OMKUMAR ASHOKBHAI",              "machhiom77@gmail.com",              "9737852427"),
    "256290305072": ("MACHHI PARTHIV HARISHANKAR",            "suniele93@gmail.com",               "9624549003"),
    "256290305074": ("MACHHI SHUBHAM TARUNBHAI",              "jigneshantdel12@gmail.com",         "9904076390"),
    "256290305076": ("MACHHI TANMAY PRAVINBHAI",              "machhidivyang019@gmail.com",        "8758250771"),
    "256290305079": ("MAHIDA HARIPALSINH BHARATSINH",         "mahidaharpal92@gmail.com",          "7623049257"),
    "256290305084": ("MAKWANA KABIRKUMAR PRITESHBHAI",        "ndparmar2812@gmail.com",            "9824533199"),
    "256290305086": ("MAKWANA MAULIKBHAI VIMALBHAI",          "maulikhapul42@gmail.com",           "9328762041"),
    "256290305087": ("MAKWANA NAITIK MAHENDRABHAI",           "mahendramakwana88906@gmail.com",    "9723847063"),
    "256290305097": ("MISTRY HET JAYESHBHAI",                 "hetmistry1109@gmail.com",           "9316358795"),
    "256290305107": ("PAREKH YAKSH HIRENKUMAR",               "yakshparekh12@gmail.com",           "9725916209"),
    "256290305122": ("PATANVADIYA TARUNBHAI RAJUBHAI",        "rajuthakor9898236282@gmail.com",    "9157784388"),
    "256290305123": ("PATEL AYAN IRFANBHAI",                  "irfanpatel4423@gmail.com",          "9227111284"),
    "256290305124": ("PATEL AYUSH HARESHBHAI",                "hareshpatel968@gmail.com",          "8989280199"),
    "256290305128": ("PATEL DHRUVALKUMAR PRAKASHBHAI",        "pp6484077@gmail.com",               "8460113560"),
    "256290305129": ("PATEL DHRUVIK ANILBHAI",                "dhruvik2009@gmail.com",             "6352286480"),
    "256290305132": ("PATEL FENILKUMAR KAMLESHBHAI",          "patelkrish4927@gmail.com",          "9313339032"),
    "256290305134": ("PATEL HENIL SANJAYBHAI",                "bmp407@gmail.com",                  "9638263597"),
    "256290305135": ("PATEL HET PRADIPBHAI",                  "meshwapatel2595@gmail.com",         "9825953167"),
    "256290305139": ("PATEL JENISH MITULKUMAR",               "jeniship2710@gmail.com",            "9157507626"),
    "256290305144": ("PATEL MEETKUMAR SHITALBHAI",            "truptipatel25820@gmail.com",        "9586704350"),
    "256290305147": ("PATEL NAITIKKUMAR DILIPBHAI",           "naitikpatel160309@gmail.com",       "9023305984"),
    "256290305151": ("PATEL PAL KAMLESH",                     "palpatel1077@gmail.com",            "8460800169"),
    "256290305152": ("PATEL PARTH MAHESHBHAI",                "maheshbhapatel764@gmail.com",       "9428021545"),
    "256290305153": ("PATEL PAVANKUMAR SATISHBHAI",           "patelpavan0409@gmail.com",          "9978340351"),
    "256290305156": ("PATEL SMIT MANISHBHAI",                 "patelsmit5630@gmail.com",           "9510840433"),
    "256290305157": ("PATEL SMITKUMAR JITUBHAI",              "pijtu4646@gmail.com",               "7046307822"),
    "256290305167": ("PATEL VRAJ RAKESHKUMAR",                "rmidhi12777@gmail.com",             "9537098899"),
    "256290305168": ("PATEL YASHKUMAR PRATAPBHAI",            "yp608247@gmail.com",                "9537603338"),
    "256290305170": ("PATHAN MOHAMMADSHAKIBKHAN SAJIDKHANMUZAFARKHAN", "SAKIBPATHAN9555@GMAIL.COM", "9274287156"),
    "256290305171": ("PRAJAPATI ADITYAKUMAR HARENDRAKUMAR",   "adityaprajapati1055@gmail.com",     "9510571264"),
    "256290305172": ("RAJ MAHIRAJ JITENDRASINH",              "rajmahiraj3636@gmail.com",          "7383434369"),
    "256290305180": ("RATHOD MANAVBHAI DHARMESHBHAI",         "MANAVRATHOD2505@GMAIL.COM",         "7573838929"),
    "256290305182": ("RATHOD RAHULBHAI GANPATBHAI",           "rahulrathod10889@gmail.com",        "6355289670"),
    "256290305183": ("RATHOD SHIVANGI ARVINDBHAI",            "shivangirathod10@gmail.com",        "7069929564"),
    "256290305186": ("ROHIT PARTHKUMAR PRAVINBHAI",           "pr1650493@gmail.com",               "8200339933"),
    "256290305187": ("SAIYAD FAHIM ARIF",                     "zameergraphics09@gmail.com",        "9904144100"),
    "256290305193": ("SODAVALA DHAVALKUMAR PRAVINBHAI",       "amar12@gmail.com",                  "9662413380"),
    "256290305194": ("SOLANKI BHARGAVKUMAR ANILBHAI",         "anilmahida779@gmail.com",           "8980133850"),
    "256290305195": ("SOLANKI PREM KARTIKBHAI",               "premnizama3112@gmail.com",          "9510068030"),
    "256290305198": ("SUNAR NANDRAJ BHARAT",                  "BBOYPITER2@GMAIL.COM",              "9227074369"),
    "256290305199": ("TANDEL PARTH VIJAYBHAI",                "tandelparijivijaybhai70@gmail.com", "8849536988"),
    "256290305202": ("THAKOR VANSHKUMAR SURENDRABHAI",        "surendrathakor2178@gmail.com",      "9428687016"),
    "256290305205": ("VAGHMARYA VISHALBHAI FULJIBHAI",        "jaydeeplala123@gmail.com",          "9979288800"),
    "256290305210": ("VALAND BHAVYKUMAR NILESHBHAI",          "nileshbhaivaland@gmail.com",        "8849363689"),
    "256290305212": ("VALAND VRAJ RAJUBHAI",                  "valandvraj26@gmail.com",            "9624993480"),
    "256290305213": ("VANZA SHIVAM PARESHKUMAR",              "paresh.k.vanza@gmail.com",          "9727663902"),
    "256290305215": ("VASAVA AYUSH KUMAR SATISHBHAI",         "skvasava213@gmail.com",             "9725908429"),
    "256290305224": ("VASAVA YES BHIKHABHAI",                 "bhikhabhiavashava@gmail.com",       "9512464266"),
    "256290305225": ("VORA JAYESH HIMMATBHAI",                "himatpatel529@gmail.com",           "9510923071"),
}

# ═══════════════════════════════════════════════
#  FLASK APP (Render ke liye — pehle define karo)
# ═══════════════════════════════════════════════
flask_app = Flask(__name__)


@flask_app.route("/")
@flask_app.route("/health")
def health_check():
    total = len(DF) if "DF" in globals() else 0
    return jsonify({
        "status": "ok",
        "service": "Student Finder Bot",
        "students": total,
    })


# ═══════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════
def normalize_enr(x) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip()
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return re.sub(r"[^a-zA-Z0-9]", "", s)


def _is_empty(v):
    if pd.isna(v):
        return True
    s = str(v).strip().lower()
    return s in ("", "nan", "nat", "none", "****", ",", "na", "n/a", "-")


def esc(s):
    return html.escape(str(s))


def build_full_name(row):
    name = row.get("Name of Student")
    if pd.notna(name) and str(name).strip() not in ("", "nan"):
        return str(name).strip()
    parts = []
    for col in ["First Name", "Middle Name", "Last Name"]:
        v = row.get(col)
        if pd.notna(v) and str(v).strip() not in ("", "nan"):
            parts.append(str(v).strip())
    return " ".join(parts)


def _find_enrollment_col(df):
    for c in df.columns:
        cl = str(c).lower()
        if "enrollment" in cl or "enroll" in cl:
            return c
    return None


# ═══════════════════════════════════════════════
#  LOAD + MERGE
# ═══════════════════════════════════════════════
def load_students():
    dfs = []

    if os.path.exists(EXCEL_FILE):
        try:
            xl = pd.ExcelFile(EXCEL_FILE)
            for sheet in xl.sheet_names:
                try:
                    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet, header=HEADER_ROW,
                                       dtype=str, engine="openpyxl")
                except Exception:
                    continue
                df = df.dropna(how="all")
                if df.empty:
                    continue
                df["__source__"] = f"excel:{sheet}"
                dfs.append(df)
                print(f"✅ Excel '{sheet}': {len(df)} rows")
        except Exception as e:
            print(f"⚠️ Excel load fail: {e}")
    else:
        print(f"⚠️ Excel nahi mili: {EXCEL_FILE}")

    for csv_path in CSV_FILES:
        if not os.path.exists(csv_path):
            print(f"⚠️ '{csv_path}' nahi mili, skip")
            continue
        try:
            df = pd.read_csv(csv_path, header=HEADER_ROW, dtype=str, on_bad_lines="skip")
            df = df.dropna(how="all")
            if df.empty:
                print(f"ℹ️ '{csv_path}' empty, skip")
                continue
            df["__source__"] = f"csv:{csv_path}"
            dfs.append(df)
            print(f"✅ '{csv_path}': {len(df)} rows")
        except Exception as e:
            print(f"⚠️ '{csv_path}' fail: {e}")

    if not dfs:
        raise ValueError("Koi bhi file load nahi hui!")

    for df in dfs:
        enr_col = _find_enrollment_col(df)
        if enr_col:
            df.rename(columns={enr_col: "Enrollment"}, inplace=True)
        else:
            if len(df.columns) >= 3:
                df.rename(columns={df.columns[2]: "Enrollment"}, inplace=True)
        df["__norm_enr__"] = df["Enrollment"].apply(normalize_enr) if "Enrollment" in df.columns else ""

    base = max(dfs, key=lambda d: d.shape[1]).copy()
    others = [d for d in dfs if d is not base]
    print(f"\n📌 BASE: '{base['__source__'].iloc[0]}' ({base.shape[1]} columns)")
    base["__row_id__"] = base.index.astype(str)

    for other in others:
        extra_map = {}
        for _, r in other.iterrows():
            k = r["__norm_enr__"]
            if k and k not in extra_map:
                extra_map[k] = r

        filled = 0
        for col in other.columns:
            if col.startswith("__") or col in base.columns:
                continue
            if other[col].apply(_is_empty).all():
                continue
            base[col] = pd.NA

        for idx, brow in base.iterrows():
            k = brow["__norm_enr__"]
            if not k or k not in extra_map:
                continue
            erow = extra_map[k]
            for col in base.columns:
                if col.startswith("__") or col not in erow.index:
                    continue
                if _is_empty(base.at[idx, col]) and not _is_empty(erow[col]):
                    base.at[idx, col] = erow[col]
                    filled += 1
        print(f"✅ Enrich '{other['__source__'].iloc[0]}': {filled} fields bhare")

    sc_count = 0
    for idx, row in base.iterrows():
        k = row["__norm_enr__"]
        if k in SCREENSHOT_DATA:
            name, email, mobile = SCREENSHOT_DATA[k]
            if _is_empty(row.get("Name of Student")) and name:
                base.at[idx, "Name of Student"] = name
                sc_count += 1
            for col in ["Registered Email", "Email"]:
                if col in base.columns and _is_empty(row.get(col)):
                    base.at[idx, col] = email
                    break
            for col in ["Registered Mobile Number", "Contact Number"]:
                if col in base.columns and _is_empty(row.get(col)):
                    base.at[idx, col] = mobile
                    break
    print(f"✅ Screenshot data: {sc_count} naam bhare")

    if "Name of Student" not in base.columns:
        base["Name of Student"] = ""
    base["Name of Student"] = base.apply(build_full_name, axis=1)

    real = base[base["__norm_enr__"].str.match(r"^\d+$", na=False)].copy()
    notreal = base[~base["__norm_enr__"].str.match(r"^\d+$", na=False)].copy()
    base = pd.concat([real, notreal], ignore_index=True)

    print(f"\n📊 TOTAL students: {len(base)}")
    print(f"📊 Total columns: {base.shape[1]}")
    return base


print("📥 Loading data...")
DF = load_students()


# ═══════════════════════════════════════════════
#  SEARCH + FORMAT
# ═══════════════════════════════════════════════
def search_students(df, query):
    q = str(query).strip()
    if not q:
        return df.iloc[0:0]
    q_lower = q.lower()
    mask = pd.Series(False, index=df.index)
    for col in df.columns:
        if col.startswith("__"):
            continue
        mask |= df[col].astype(str).str.lower().str.contains(re.escape(q_lower), na=False)
    return df[mask]


def clean_val(v):
    if _is_empty(v):
        return None
    s = str(v).strip()
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return s


def format_student_telegram(row):
    priority = [
        "Name of Student", "Enrollment", "Enrollment Number", "Sr. No.",
        "Student type", "Class", "Batch (Practical)", "Batch (Tutorial)",
        "Branch", "Program Level", "Active Semester",
        "Admission Year", "Academic Year", "Project Mentor",
        "DOB(YYYY-MM-DD)", "Date of Birth",
        "Gender(Male/Female)", "Gender",
        "Cast(General/General(EWS)/SEBC/SC/ST)", "Candidate Category", "Admitted Category",
        "Nationality", "Hindu", "Minority", "Native Place",
        "Email", "Registered Email",
        "Contact Number", "Registered Mobile Number",
        "Father Name", "Mother Name",
        "Father's Mobile No.", "Father's Email Address",
        "Aadhar Number",
        "Present Address", "Permanent Address",
        "Present Address - State", "Present Address - District",
        "Present Address - Taluka", "Present Address - Pincode",
        "Permanent Address - State", "Permanent Address - District",
        "Student Full Name (As Per Last Board Exam)",
    ]
    lines, shown = [], set()
    for key in priority:
        if key in row.index:
            v = clean_val(row[key])
            if v:
                lines.append(f"• <b>{esc(key)}</b>: {esc(v)}")
                shown.add(key)

    extras = []
    for key in row.index:
        if key in shown or key.startswith("__"):
            continue
        v = clean_val(row[key])
        if v:
            extras.append(f"• <i>{esc(key)}</i>: {esc(v)}")

    if extras:
        lines.append("")
        lines.append("<b>─── Extra Fields ───</b>")
        lines.extend(extras)

    return "\n".join(lines) if lines else "⚠️ NO DATA"


def extract_contacts(row):
    email = None
    for col in ["Email", "Registered Email", "Father's Email Address"]:
        if col in row.index:
            v = clean_val(row[col])
            if v and "@" in v and "father" not in col.lower():
                email = v.split()[0].strip()
                break
    if not email:
        for col in ["Email", "Registered Email"]:
            if col in row.index:
                v = clean_val(row[col])
                if v and "@" in v:
                    email = v
                    break

    mobile = None
    for col in ["Contact Number", "Registered Mobile Number", "Father's Mobile No."]:
        if col in row.index:
            v = clean_val(row[col])
            if v:
                digits = re.sub(r"\D", "", v)
                if len(digits) >= 10:
                    mobile = digits[-10:]
                    break

    username = email.split("@")[0] if email else None
    return email, mobile, username


# ═══════════════════════════════════════════════
#  🕵️ OSINT FUNCTIONS
# ═══════════════════════════════════════════════
OSINT_HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 10)"}

USERNAME_SITES = [
    ("GitHub",       "https://github.com/{}"),
    ("Twitter/X",    "https://x.com/{}"),
    ("Instagram",    "https://instagram.com/{}"),
    ("Reddit",       "https://reddit.com/user/{}"),
    ("Pinterest",    "https://pinterest.com/{}"),
    ("Medium",       "https://medium.com/@{}"),
    ("Dev.to",       "https://dev.to/{}"),
    ("HackerNews",   "https://news.ycombinator.com/user?id={}"),
    ("Behance",      "https://behance.net/{}"),
    ("Dribbble",     "https://dribbble.com/{}"),
    ("SoundCloud",   "https://soundcloud.com/{}"),
    ("Twitch",       "https://twitch.tv/{}"),
    ("YouTube",      "https://youtube.com/@{}"),
    ("Telegram",     "https://t.me/{}"),
    ("Facebook",     "https://facebook.com/{}"),
    ("LinkedIn",     "https://linkedin.com/in/{}"),
    ("Snapchat",     "https://snapchat.com/add/{}"),
    ("TikTok",       "https://tiktok.com/@{}"),
    ("Steam",        "https://steamcommunity.com/id/{}"),
    ("Mastodon",     "https://mastodon.social/@{}"),
    ("CodePen",      "https://codepen.io/{}"),
    ("Replit",       "https://replit.com/@{}"),
    ("HackerRank",   "https://hackerrank.com/{}"),
    ("LeetCode",     "https://leetcode.com/{}"),
    ("Keybase",      "https://keybase.io/{}"),
    ("About.me",     "https://about.me/{}"),
]


def _url_exists(url, timeout=6):
    try:
        r = requests.get(url, headers=OSINT_HEADERS, timeout=timeout, allow_redirects=True)
        return r.status_code == 200
    except Exception:
        return False


def osint_email_block(email):
    out = ["<b>📧 EMAIL INTEL</b>", f"<code>{esc(email)}</code>"]
    if not re.fullmatch(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", email):
        out.append("❌ Invalid format")
        return "\n".join(out)

    domain = email.split("@", 1)[1]

    try:
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(email)}?truncateResponse=true",
            headers={"User-Agent": "OSINT-Tool"},
            timeout=10
        )
        if r.status_code == 200:
            breaches = r.json()
            out.append(f"🚨 <b>{len(breaches)} breach(es)!</b>")
            for b in breaches[:5]:
                out.append(f"   🔴 {esc(b.get('Name','?'))} ({esc(b.get('BreachDate','?'))})")
        elif r.status_code == 404:
            out.append("✅ No breaches — safe")
        elif r.status_code == 429:
            out.append("⏳ HIBP rate limit")
        else:
            out.append(f"⚠️ HIBP status {r.status_code}")
    except Exception:
        out.append("⚠️ HIBP check fail")

    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    try:
        r = requests.get(f"https://www.gravatar.com/avatar/{h}.json",
                         headers=OSINT_HEADERS, timeout=6)
        if r.status_code == 200:
            data = r.json().get("entry", [{}])[0]
            out.append(f"🖼️ <b>Gravatar:</b> ✅ Profile mila")
            if data.get("displayName"):
                out.append(f"   👤 {esc(data['displayName'])}")
            if data.get("accounts"):
                accs = [f"{a.get('shortname','?')}" for a in data["accounts"][:5]]
                out.append(f"   🔗 Linked: {esc(', '.join(accs))}")
        else:
            out.append("🖼️ Gravatar: ❌")
    except Exception:
        pass

    try:
        mx = dns.resolver.resolve(domain, "MX")
        out.append(f"📮 MX: ✅ {esc(str(mx[0].exchange).rstrip('.'))}")
    except Exception:
        out.append("📮 MX: ❌ (fake domain?)")

    return "\n".join(out)


def osint_mobile_block(mobile):
    out = ["<b>📱 MOBILE INTEL</b>", f"<code>{esc(mobile)}</code>"]
    num = re.sub(r"\D", "", mobile)
    if len(num) == 10:
        num = "+91" + num

    try:
        p = phonenumbers.parse(num, None)
        if not phonenumbers.is_valid_number(p):
            out.append("❌ Invalid number")
            return "\n".join(out)

        country = geocoder.description_for_number(p, "en") or "?"
        carr = carrier.name_for_number(p, "en") or "Unknown"
        out.append(f"🌍 {esc(country)} | 📡 {esc(carr)}")

        ntype = phonenumbers.number_type(p)
        type_map = {0: "📱 Mobile", 1: "☎️ Landline", 2: "📞 Fixed/Mobile",
                    3: "🆓 Toll-free", 4: "💰 Premium", 6: "💻 VoIP"}
        out.append(f"📋 {type_map.get(ntype, 'Other')}")

        last10 = num[-10:]
        out.append(f"🔗 <a href='https://wa.me/91{last10}'>WhatsApp</a>")
        out.append(f"🔗 <a href='https://t.me/+{num}'>Telegram</a>")
        out.append(f"🔗 <a href='https://www.truecaller.com/search/in/{last10}'>Truecaller</a>")
    except Exception as e:
        out.append(f"⚠️ {esc(str(e))}")

    return "\n".join(out)


def osint_username_block(username, max_sites=25):
    out = ["<b>👤 USERNAME HUNT</b>", f"<code>@{esc(username)}</code>"]

    if not re.fullmatch(r"[a-zA-Z0-9_.-]{2,32}", username):
        out.append("❌ Invalid username")
        return "\n".join(out)

    found = []
    for name, url_tmpl in USERNAME_SITES[:max_sites]:
        url = url_tmpl.format(username)
        if _url_exists(url):
            found.append((name, url))

    if found:
        out.append(f"✅ <b>{len(found)} ACCOUNTS FOUND:</b>")
        for name, url in found:
            out.append(f"   • <a href='{url}'>{esc(name)}</a>")
    else:
        out.append("❌ 0 ACCOUNTS FOUND")

    return "\n".join(out)


def auto_osint_report(row):
    email, mobile, username = extract_contacts(row)

    if not email and not mobile and not username:
        return None

    blocks = []

    if email:
        try:
            blocks.append(osint_email_block(email))
        except Exception as e:
            blocks.append(f"<b>📧 EMAIL INTEL</b>\n⚠️ Error: {esc(str(e))}")

    if mobile:
        try:
            blocks.append(osint_mobile_block(mobile))
        except Exception as e:
            blocks.append(f"<b>📱 MOBILE INTEL</b>\n⚠️ Error: {esc(str(e))}")

    if username:
        try:
            blocks.append(osint_username_block(username, max_sites=20))
        except Exception as e:
            blocks.append(f"<b>👤 USERNAME HUNT</b>\n⚠️ Error: {esc(str(e))}")

    return "\n\n━━━━━━━━━━━━━━━\n\n".join(blocks)


# ═══════════════════════════════════════════════
#  🎬 TYPING ANIMATION
# ═══════════════════════════════════════════════
async def typing_animation(context, chat_id, seconds=3):
    end = asyncio.get_event_loop().time() + seconds
    while asyncio.get_event_loop().time() < end:
        try:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception:
            pass
        await asyncio.sleep(2.5)


# ═══════════════════════════════════════════════
#  🎯 ROAST
# ═══════════════════════════════════════════════
def is_target(q):
    raw = str(q).lower().strip()
    compact = re.sub(r"[^a-z0-9]", "", raw)
    if TARGET_ENROLLMENT in compact:
        return True
    for em in TARGET_EMAILS:
        if em.lower() in raw:
            return True
    mobile_only = re.sub(r"[^0-9]", "", raw)
    for mob in TARGET_MOBILES:
        if mob in mobile_only:
            return True
    name_only = re.sub(r"[^a-z ]", " ", raw)
    hits = sum(1 for tok in TARGET_NAME_TOKENS if tok in name_only)
    return hits >= 2


# ═══════════════════════════════════════════════
#  TELEGRAM HANDLERS
# ═══════════════════════════════════════════════
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚠️ Disclaimer: This bot is intended for educational and administrative "
        "purposes only. The owner/developer assumes no liability for any misuse, "
        "privacy violations, or illegal activities conducted by users. Use responsibly.\n\n"
        "USE - Send Name, enrollment, email, mobile, city, branch, caste\n\n"
        "🔎 Examples:\n"
        "• AHIR AYUSH\n"
        "• 256290305001\n"
        "• Bharuch\n"
        "• SEBC\n"
        "• CH1\n\n"
        f"📊 Total students: {len(DF)}\n"
        f"🕵️ Auto-OSINT: {'ON' if ENABLE_AUTO_OSINT else 'OFF'}"
    )
    await update.message.reply_text(text)


async def help_cmd(update, context):
    await start_cmd(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = (update.message.text or "").strip()
    if not query:
        return

    # 🎯 ROAST
    if is_target(query):
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await asyncio.sleep(1.5)
        roast = random.choice(ROASTS).format(q=esc(query))
        await update.message.reply_text(roast, parse_mode="HTML")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        results = search_students(DF, query)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: <code>{esc(e)}</code>", parse_mode="HTML")
        return

    if results.empty:
        await update.message.reply_text(
            f"❌ <b>{esc(query)}</b> not found.\n"
            f"Check spelling or try a shorter keyword.",
            parse_mode="HTML"
        )
        return

    total = len(results)

    await update.message.reply_text(
        f"✅ <b>{total}</b> result(s) found for <b>{esc(query)}</b>:",
        parse_mode="HTML"
    )

    for i, (_, row) in enumerate(results.head(MAX_RESULTS).iterrows(), 1):
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        await asyncio.sleep(0.8)

        block = f"<b>━━━ #{i} ━━━</b>\n" + format_student_telegram(row)
        chunks = [block[j:j+3800] for j in range(0, len(block), 3800)]
        for c in chunks:
            try:
                await update.message.reply_text(c, parse_mode="HTML")
            except Exception:
                try:
                    await update.message.reply_text(re.sub(r"<[^>]+>", "", c))
                except Exception:
                    pass

        # 🕵️ AUTO-OSINT
        if ENABLE_AUTO_OSINT and i == 1 and not is_target(query):
            osint_msg = await update.message.reply_text(
                "🕵️ <b>Auto-Investigation start...</b>\n"
                "<i>Email, Mobile, Username checking...</i>",
                parse_mode="HTML"
            )

            for stage in [
                "🔍 <b>Stage 1/4:</b> Email intel... <i>(breaches + gravatar)</i>",
                "📡 <b>Stage 2/4:</b> Mobile carrier intel...",
                "👤 <b>Stage 3/4:</b> Username hunt (25+ sites)...",
                "🧩 <b>Stage 4/4:</b> Report compile...",
            ]:
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                await asyncio.sleep(0.7)
                try:
                    await osint_msg.edit_text(stage, parse_mode="HTML")
                except Exception:
                    pass

            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            try:
                loop = asyncio.get_event_loop()
                report = await loop.run_in_executor(None, auto_osint_report, row)
            except Exception as e:
                report = f"⚠️ OSINT error: {esc(str(e))}"

            if report:
                header = "🕵️ <b>AUTO-OSINT REPORT</b>\n<i>Public data only</i>\n\n"
                full = header + report
                chunks = [full[j:j+3800] for j in range(0, len(full), 3800)]
                try:
                    await osint_msg.edit_text(chunks[0], parse_mode="HTML", disable_web_page_preview=True)
                except Exception:
                    await osint_msg.edit_text(re.sub(r"<[^>]+>", "", chunks[0])[:4000])
                for c in chunks[1:]:
                    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
                    await asyncio.sleep(0.5)
                    try:
                        await update.message.reply_text(c, parse_mode="HTML", disable_web_page_preview=True)
                    except Exception:
                        await update.message.reply_text(re.sub(r"<[^>]+>", "", c)[:4000])
            else:
                try:
                    await osint_msg.edit_text("🕵️ No email/mobile available for OSINT on this student.")
                except Exception:
                    pass

    if total > MAX_RESULTS:
        await update.message.reply_text(
            f"… and <b>{total - MAX_RESULTS}</b> more results. Be more specific.",
            parse_mode="HTML"
        )


# ═══════════════════════════════════════════════
#  FLASK RUNNER + TELEGRAM MAIN
# ═══════════════════════════════════════════════
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    print(f"🌐 Flask server starting on port {port}")
    flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


def main():
    # Flask ko background thread me chalao
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Telegram bot foreground me
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
