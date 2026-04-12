TEACHING_SYSTEM = """\
You are a senior physician teaching a medical student.
Your tone is concise, clinically relevant, and mechanism-focused — exactly as you would sound on hospital rounds.
Output only valid JSON. No prose before or after.
"""

TEACHING_USER_TEMPLATE = """\
Given this flashcard:
[Front]: {front}
[Back]: {back}

Transform it into a hospital-style teaching interaction for USMLE Step 1 learning.

Return this exact JSON structure:
{{
  "attending_question": "A short attending-style version of the question",
  "correct_answer": "The correct concise answer",
  "step_by_step_explanation": "A concise educational explanation of the mechanism or reasoning (2-4 sentences)",
  "wrong_answer_analysis": [
    "Wrong answer 1 and why it is wrong",
    "Wrong answer 2 and why it is wrong",
    "Wrong answer 3 and why it is wrong"
  ],
  "high_yield_takeaway": "One-line test-day takeaway",
  "follow_up_questions": [
    "Follow-up pimp question 1 — easier or foundational",
    "Follow-up pimp question 2 — harder or more integrative"
  ],
  "mcq_options": [
    "Correct option (must be index 0)",
    "Plausible distractor 1",
    "Plausible distractor 2",
    "Plausible distractor 3"
  ]
}}

Rules:
- Keep content medically accurate and high-yield
- Prioritize Step 1 mechanistic learning
- Do not copy copyrighted prep resources
- Make distractors plausible and educational
- Make follow-up questions increase in difficulty
- Explanations should be concise, not long essays
- Output JSON only
"""

GRADING_SYSTEM = """\
You are a medical educator grading a student's free-recall answer.
Be fair but strict: partial credit for partial understanding.
Output only valid JSON. No prose before or after.
"""

GRADING_USER_TEMPLATE = """\
Question: {question}
Correct answer: {correct}
Student's answer: {user_answer}

Score the student's answer 0-4 using this rubric:
4 = fully correct — captures the essential concept precisely
3 = mostly correct — correct concept with minor omission or imprecision
2 = partially correct — shows some understanding but misses key mechanism
1 = related but insufficient — relevant content but misses the actual answer
0 = incorrect or blank

Return JSON:
{{
  "score": <0-4 integer>,
  "justification": "<one sentence explaining the score>"
}}
"""
