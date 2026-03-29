import streamlit as st
from groq import Groq
import json

@st.cache_resource
def get_groq():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

STAGE_SYSTEM_PROMPTS = {
    "pitch": """You are an expert technical recruiter reaching out to a candidate about a job opportunity.
Your goal is to pitch the role in a compelling, concise way and gauge their interest.
Be professional but warm. Keep it short — this is a first contact.
Do NOT use generic phrases. Reference specific things from the JD.
End with a clear question: are they open to hearing more?
Respond in plain text only. No markdown.""",

    "screening": """You are an expert technical recruiter conducting a screening conversation.
You have already pitched the role and the candidate is interested.
Now ask targeted screening questions based on the JD to assess fit.
Ask ONE question at a time. Be conversational, not interrogative.
After getting answers, probe deeper if needed. Summarize at the end.
Respond in plain text only. No markdown.""",

    "negotiation": """You are an expert technical recruiter in negotiation mode.
You understand salary benchmarks, notice periods, and competing offers.
Your goal is to bridge gaps between candidate expectations and the JD offer range.
Be empathetic but firm. Offer value beyond salary (growth, culture, opportunity).
If there's a hard blocker, acknowledge it and ask if there's a way to resolve it.
Respond in plain text only. No markdown.""",

    "followup": """You are a recruiter sending a follow-up message to a candidate.
Keep it brief and professional. Reference the last conversation point.
Create mild urgency without pressure. Offer to answer any questions.
Respond in plain text only. No markdown.""",

    "interview_slot": """You are a recruiter confirming interview scheduling with a candidate.
Provide the calendar link and any prep info from the JD context.
Be warm and encouraging. Make them feel good about moving forward.
Respond in plain text only. No markdown.""",

    "rejection": """You are a recruiter sending a respectful rejection message.
Be kind, brief, and leave the door open for future opportunities.
Do not give detailed reasons. Thank them for their time.
Respond in plain text only. No markdown.""",
}

def generate_message(
    stage: str,
    candidate: dict,
    jd: dict,
    conversation_history: list = None,
    extra_context: str = ""
) -> str:
    client = get_groq()

    system = STAGE_SYSTEM_PROMPTS.get(stage, STAGE_SYSTEM_PROMPTS["pitch"])

    # Build context block
    context = f"""
CANDIDATE:
- Name: {candidate.get('name', 'Candidate')}
- Current Role: {candidate.get('current_role', 'Unknown')}
- Current Company: {candidate.get('current_company', 'Unknown')}
- Experience: {candidate.get('experience_years', '?')} years
- Current Salary: {candidate.get('current_salary', 'Unknown')}
- Expected Salary: {candidate.get('expected_salary', 'Unknown')}
- Notice Period: {candidate.get('notice_period', 'Unknown')}
- Location: {candidate.get('location', 'Unknown')}
- Notes: {candidate.get('notes', '')}

JOB DESCRIPTION:
- Title: {jd.get('title', 'Role')}
- Skills Required: {jd.get('skills', '')}
- Salary Range: {jd.get('salary_range', 'Competitive')}
- Calendly Link: {jd.get('calendly_link', '')}
- Additional Info: {jd.get('description', '')}

{('EXTRA CONTEXT: ' + extra_context) if extra_context else ''}
"""

    messages = [{"role": "system", "content": system}]

    # Add prior conversation as context
    if conversation_history:
        history_text = "\n".join([
            f"{'RECRUITER' if m['direction'] == 'outbound' else 'CANDIDATE'}: {m['message']}"
            for m in conversation_history[-10:]  # last 10 messages
        ])
        messages.append({
            "role": "user",
            "content": f"{context}\n\nPRIOR CONVERSATION:\n{history_text}\n\nGenerate the next recruiter message for stage: {stage}"
        })
    else:
        messages.append({
            "role": "user",
            "content": f"{context}\n\nGenerate an outreach message for stage: {stage}"
        })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7,
        max_tokens=600,
    )

    return response.choices[0].message.content.strip()


def analyze_candidate_response(response_text: str, jd: dict) -> dict:
    """Parse candidate response to extract signals: interest, salary, notice period, blockers."""
    client = get_groq()

    prompt = f"""Analyze this candidate response in the context of a recruitment conversation.

JOB: {jd.get('title', 'Role')} | Salary: {jd.get('salary_range', 'Unknown')}

CANDIDATE RESPONSE:
{response_text}

Extract the following as JSON (keys: interest_level, mentioned_salary, mentioned_notice, blockers, recommended_next_stage, summary):
- interest_level: "high" | "medium" | "low" | "unknown"
- mentioned_salary: any salary figure mentioned or null
- mentioned_notice: any notice period mentioned or null  
- blockers: list of blockers or issues mentioned (empty list if none)
- recommended_next_stage: "screening" | "negotiation" | "interview_slot" | "followup" | "rejection"
- summary: 1-2 sentence summary of their response

Return ONLY valid JSON. No explanation."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=300,
    )

    try:
        text = response.choices[0].message.content.strip()
        # Clean JSON fences if present
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {
            "interest_level": "unknown",
            "mentioned_salary": None,
            "mentioned_notice": None,
            "blockers": [],
            "recommended_next_stage": "followup",
            "summary": response_text[:200]
        }


def summarize_conversation(conversations: list, candidate: dict, jd: dict) -> str:
    """Generate a full conversation summary for the Validator."""
    client = get_groq()

    history = "\n".join([
        f"{'RECRUITER' if m['direction'] == 'outbound' else 'CANDIDATE'}: {m['message']}"
        for m in conversations
    ])

    prompt = f"""Summarize this recruitment conversation for handoff to the next stage (Validator).

CANDIDATE: {candidate.get('name')} | ROLE: {jd.get('title', 'Unknown') if jd else 'Unknown'}

CONVERSATION:
{history}

Write a structured summary covering:
1. Candidate interest level and enthusiasm
2. Skills/experience match signals
3. Salary expectations vs offered range
4. Notice period
5. Any blockers or concerns
6. Overall recommendation (Proceed / Hold / Reject)

Keep it factual and concise. Plain text, no markdown."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()
