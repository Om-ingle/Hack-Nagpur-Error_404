import os
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY")) if os.getenv("GROQ_API_KEY") else None
except ImportError:
    groq_client = None

try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY") if os.getenv("OPENAI_API_KEY") else None
except ImportError:
    openai = None

def generate_doctor_summary(current_symptoms, patient_age, risk_level, previous_visits=None):
    """
    Generate a SHORT clinical summary for doctor review.
    
    Args:
        current_symptoms: String of current symptoms
        patient_age: Integer age of patient
        risk_level: String (HIGH/MEDIUM/LOW)
        previous_visits: Optional list of previous visit dicts with symptoms and notes
    
    Returns:
        String: 3-4 line clinical summary
    """
    if not current_symptoms:
        return "No symptoms reported. Unable to generate summary."
    
    # Build context
    history_context = ""
    if previous_visits and len(previous_visits) > 0:
        history_items = []
        for visit in previous_visits[:3]:  # Last 3 visits only
            if visit.get('symptoms_raw'):
                history_items.append(f"- {visit['symptoms_raw']}")
        if history_items:
            history_context = f"\nPrevious visits:\n" + "\n".join(history_items)
    
    prompt = f"""You are a clinical assistant. Generate a SHORT, CLEAR, 3-4 line summary for a doctor.

Current patient:
- Age: {patient_age} years
- Current symptoms: {current_symptoms}
- Risk level: {risk_level}{history_context}

Requirements:
- Maximum 4 lines
- Clinical, neutral tone
- NO diagnosis or medical claims
- Highlight urgency indicators if present
- Mention relevant history if available
- Assistive only, not prescriptive

Format:
Line 1: Patient demographics and presenting complaint
Line 2: Key symptom details or history
Line 3: Risk assessment context
Line 4: Recommendation (e.g., "Prompt evaluation recommended")

Generate the summary now:"""
    
    try:
        # Try Groq first
        if groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            summary = response.choices[0].message.content.strip()
            return summary
        
        # Try OpenAI as fallback
        elif openai and openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=200
            )
            summary = response.choices[0].message.content.strip()
            return summary
        
        # Simple fallback if no AI available
        else:
            return generate_simple_summary(current_symptoms, patient_age, risk_level, previous_visits)
    
    except Exception as e:
        print(f"AI summary generation failed: {e}")
        return generate_simple_summary(current_symptoms, patient_age, risk_level, previous_visits)

def generate_simple_summary(symptoms, age, risk_level, previous_visits=None):
    """Fallback rule-based summary generation"""
    
    # Extract gender-neutral presentation
    age_group = "pediatric" if age < 18 else "adult" if age < 65 else "elderly"
    
    # Check for emergency keywords
    emergency_keywords = ['chest pain', 'heart attack', 'stroke', 'bleeding', 'unconscious', 'severe']
    has_emergency = any(kw in symptoms.lower() for kw in emergency_keywords)
    
    # Build summary lines
    line1 = f"{age_group.capitalize()} patient ({age} years) presenting with {symptoms[:50]}{'...' if len(symptoms) > 50 else ''}."
    
    if previous_visits and len(previous_visits) > 0:
        line2 = f"Previous visit history available ({len(previous_visits)} recorded visits)."
    else:
        line2 = "No previous visit history on record."
    
    urgency = "high" if risk_level == "HIGH" or has_emergency else "moderate" if risk_level == "MEDIUM" else "standard"
    line3 = f"Risk assessment indicates {urgency} urgency level."
    
    if has_emergency:
        line4 = "Immediate medical evaluation strongly recommended."
    elif risk_level == "HIGH":
        line4 = "Prompt medical evaluation recommended."
    else:
        line4 = "Standard consultation and evaluation recommended."
    
    return f"{line1}\n{line2}\n{line3}\n{line4}"
