#!/usr/bin/env python3
"""
Extracts the 100 kandakorlik questions from 'ТЕСТЫ по Чеканке.docx' and writes
them to quiz_seed_data.json, which init_db.py seeds into the database.

The DOCX is the source of truth. Re-run this after editing it:

    python extract_quizzes.py

Usage from the backend/ directory. No server or database needed.
"""

import json
import os
import re
import sys
import zipfile

DOCX_PATH = os.path.join(os.path.dirname(__file__), '..', 'ТЕСТЫ по Чеканке.docx')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'quiz_seed_data.json')

# The DOCX is one flat list of 100 questions; these are the topic boundaries.
QUIZ_GROUPS = [
    {
        "title": "O'qitish Metodikasi",
        "description": "Misga ishlov berishni o'qitish metodikasi, pedagogik yondashuvlar va dars tashkil etish. 1–25 savollar.",
        "range": (0, 25),
    },
    {
        "title": "Asboblar va Texnikalar",
        "description": "Kandakorlik asboblari, naqsh tushirish texnikalari va xavfsizlik qoidalari. 26–50 savollar.",
        "range": (25, 50),
    },
    {
        "title": "Metallning Xossalari",
        "description": "Mis, bronza, latunning fizik va kimyoviy xossalari, metallga ishlov berish jarayonlari. 51–75 savollar.",
        "range": (50, 75),
    },
    {
        "title": "Naqsh San'ati va Dizayn",
        "description": "Naqsh kompozitsiyasi, ornament, simmetriya, islimiy va geometrik naqsh turlari. 76–100 savollar.",
        "range": (75, 100),
    },
]

LETTERS = ['A', 'B', 'C', 'D']


def clean(s):
    """Word splits runs mid-sentence, which leaves stray spaces before punctuation."""
    return re.sub(r'\s+([,.;:!?])', r'\1', s.strip())


def read_docx_text(path):
    """Flatten word/document.xml into a single normalized line of text."""
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8')
    text = re.sub(r'<[^>]+>', ' ', xml)
    text = re.sub(r'\s+', ' ', text).strip()
    # Word turns straight quotes into curly ones; normalize so patterns match.
    return text.replace('‘', "'").replace('’', "'")


def parse_questions(text):
    """Split the flat text into question dicts, preserving DOCX order."""
    questions = []
    for block in re.split(r'(?=Savol \d+\s*:)', text):
        block = block.strip()
        number_match = re.match(r'Savol (\d+)', block)
        if not number_match:
            continue

        # Option labels are sometimes typed with a space ("A )"), so allow it.
        parts = {}
        for letter, next_letter in zip(LETTERS, LETTERS[1:]):
            m = re.search(rf'{letter}\s*\)\s*(.+?)\s+{next_letter}\s*\)', block, re.DOTALL)
            parts[letter] = m.group(1).strip() if m else None
        # The last option runs until the answer marker.
        m = re.search(r"D\s*\)\s*(.+?)\s+(?:\U0001F449|To'g'ri javob)", block, re.DOTALL)
        parts['D'] = m.group(1).strip() if m else None

        q_match = re.search(r'Savol \d+\s*:?\s*(.+?)\s+A\s*\)', block, re.DOTALL)
        ans_match = re.search(r"To'g'ri javob:\s*([ABCD])", block)

        if not q_match or not ans_match or not all(parts.values()):
            print(f"  ⚠ Could not parse: {block[:100]}", file=sys.stderr)
            continue

        correct = ans_match.group(1)
        questions.append({
            "number": int(number_match.group(1)),
            "question_text": clean(q_match.group(1)),
            "answers": [
                {"answer_text": clean(parts[l]), "is_correct": l == correct, "order": i + 1}
                for i, l in enumerate(LETTERS)
            ],
        })
    return questions


def main():
    sys.stdout.reconfigure(encoding='utf-8')

    text = read_docx_text(DOCX_PATH)
    questions = parse_questions(text)
    expected = len(re.findall(r'Savol \d+', text))
    print(f"✓ Parsed {len(questions)} of {expected} questions from DOCX")
    if len(questions) != expected:
        print("❌ Some questions failed to parse — fix the DOCX or the patterns above.",
              file=sys.stderr)
        sys.exit(1)

    quizzes = []
    for group in QUIZ_GROUPS:
        start, end = group["range"]
        selected = questions[start:end]
        quizzes.append({
            "title": group["title"],
            "description": group["description"],
            "time_limit_minutes": 30,
            "passing_score": 60.0,
            "questions": [
                {
                    "question_text": q["question_text"],
                    "question_type": "multiple_choice",
                    "order": i + 1,
                    "points": 1.0,
                    "answers": q["answers"],
                }
                for i, q in enumerate(selected)
            ],
        })
        print(f"  • {group['title']}: {len(selected)} questions")

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(quizzes, f, ensure_ascii=False, indent=2)
    total = sum(len(q["questions"]) for q in quizzes)
    print(f"✓ Wrote {len(quizzes)} quizzes / {total} questions to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
