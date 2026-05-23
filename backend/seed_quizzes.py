"""
Seed script: parses ТЕСТЫ по Чеканке.docx and creates 4 quizzes of 25 questions each.
Run from backend/ directory: python seed_quizzes.py
"""
import sys, os, zipfile, re, requests

sys.stdout.reconfigure(encoding='utf-8')

API = "http://localhost:8000"
DOCX_PATH = os.path.join(os.path.dirname(__file__), '..', 'ТЕСТЫ по Чеканке.docx')
SCHOOL_ID = 1  # Buxoro — used for all general quizzes

# ── 1. Login ─────────────────────────────────────────────────────────────────
resp = requests.post(f"{API}/api/auth/login", json={"username": "admin", "password": "Admin@1234"})
if resp.status_code != 200:
    print("Login failed:", resp.text); sys.exit(1)
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print("✓ Logged in as admin")

# ── 2. Parse DOCX ────────────────────────────────────────────────────────────
with zipfile.ZipFile(DOCX_PATH) as z:
    with z.open('word/document.xml') as f:
        xml = f.read().decode('utf-8')
text = re.sub(r'<[^>]+>', ' ', xml)
text = re.sub(r'\s+', ' ', text).strip()
text = text.replace('‘', "'").replace('’', "'")

# Split into per-question blocks
blocks = re.split(r'(?=Savol \d+\s*:)', text)

questions = []
for block in blocks:
    block = block.strip()
    if not re.match(r'Savol \d+', block):
        continue

    q_match    = re.search(r'Savol \d+\s*:?\s*(.+?)\s+A\)', block, re.DOTALL)
    a_match    = re.search(r'A\)\s*(.+?)\s+B\)', block, re.DOTALL)
    b_match    = re.search(r'B\)\s*(.+?)\s+C\)', block, re.DOTALL)
    c_match    = re.search(r'C\)\s*(.+?)\s+D\)', block, re.DOTALL)
    d_match    = re.search(r"D\)\s*(.+?)\s+👉", block, re.DOTALL)
    ans_match  = re.search(r"To'g'ri javob:\s*([ABCD])", block)

    if not all([q_match, a_match, b_match, c_match, d_match, ans_match]):
        print(f"  ⚠ Could not parse block: {block[:80]}")
        continue

    correct_letter = ans_match.group(1)
    opts = {
        'A': a_match.group(1).strip(),
        'B': b_match.group(1).strip(),
        'C': c_match.group(1).strip(),
        'D': d_match.group(1).strip(),
    }

    questions.append({
        'question_text': q_match.group(1).strip(),
        'answers': [
            {'answer_text': opts[l], 'is_correct': (l == correct_letter), 'order': i+1}
            for i, l in enumerate(['A', 'B', 'C', 'D'])
        ]
    })

print(f"✓ Parsed {len(questions)} questions from DOCX")

# ── 3. Define 4 quiz groups ──────────────────────────────────────────────────
quiz_defs = [
    {
        'title': "O'qitish Metodikasi",
        'description': "Misga ishlov berishni o'qitish metodikasi, pedagogik yondashuvlar va dars tashkil etish. 1–25 savollar.",
        'questions': questions[0:25],
    },
    {
        'title': "Asboblar va Texnikalar",
        'description': "Kandakorlik asboblari, naqsh tushirish texnikalari va xavfsizlik qoidalari. 26–50 savollar.",
        'questions': questions[25:50],
    },
    {
        'title': "Metallning Xossalari",
        'description': "Mis, bronza, latunning fizik va kimyoviy xossalari, metallga ishlov berish jarayonlari. 51–75 savollar.",
        'questions': questions[50:75],
    },
    {
        'title': "Naqsh San'ati va Dizayn",
        'description': "Naqsh kompozitsiyasi, ornament, simmetriya, islimiy va geometrik naqsh turlari. 76–100 savollar.",
        'questions': questions[75:100],
    },
]

# ── 4. Create and publish each quiz ──────────────────────────────────────────
for qdef in quiz_defs:
    payload = {
        "school_id": SCHOOL_ID,
        "title": qdef['title'],
        "description": qdef['description'],
        "time_limit_minutes": 30,
        "passing_score": 60.0,
        "questions": [
            {
                "question_text": q['question_text'],
                "question_type": "multiple_choice",
                "order": idx + 1,
                "points": 1.0,
                "answers": q['answers'],
            }
            for idx, q in enumerate(qdef['questions'])
        ]
    }

    r = requests.post(f"{API}/api/quizzes/", json=payload, headers=headers)
    if r.status_code != 201:
        print(f"  ✗ Failed to create '{qdef['title']}': {r.text}"); continue

    quiz_id = r.json()['id']
    print(f"  ✓ Created quiz #{quiz_id}: {qdef['title']} ({len(qdef['questions'])} questions)")

    pub = requests.patch(f"{API}/api/quizzes/{quiz_id}/publish", headers=headers)
    if pub.status_code == 200:
        print(f"    ✓ Published quiz #{quiz_id}")
    else:
        print(f"    ⚠ Publish failed: {pub.text}")

print("\n✅ All done!")
