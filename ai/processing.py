import json
import os
import re
from functools import lru_cache

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Try to import AI libraries (graceful fallback if not available)
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


def transcribe_audio(audio_bytes):
    """Convert audio to text using Whisper (with fallback)"""
    if not audio_bytes:
        return None

    try:
        # Handle both bytes and UploadedFile objects
        if hasattr(audio_bytes, "read"):
            # It's an UploadedFile object
            audio_data = audio_bytes.read()
        else:
            # It's already bytes
            audio_data = audio_bytes

        # Save audio temporarily
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_data)

        # Try Groq first
        if groq_client:
            with open("temp_audio.wav", "rb") as file:
                transcription = groq_client.audio.transcriptions.create(
                    file=file, model="whisper-large-v3"
                )
            return transcription.text

        # Try OpenAI as fallback
        if openai and openai.api_key:
            with open("temp_audio.wav", "rb") as file:
                transcription = openai.audio.transcriptions.create(model="whisper-1", file=file)
            return transcription.text
        st.warning("⚠️ Voice processing not available. Please use text input.")
        return None

    except Exception as e:
        st.error(f"Voice processing failed: {e}")
        return None


def translate_to_english(text):
    """Translate any language text to English using AI"""
    if not text:
        return text

    # Check if text is already in English (simple heuristic)
    # If it contains mostly ASCII and common English words, skip translation
    english_indicators = ["my", "is", "am", "have", "pain", "year", "old", "name"]
    text_lower = text.lower()
    if sum(word in text_lower for word in english_indicators) >= 2:
        return text  # Likely already English

    prompt = f"""Translate the following text to English. If it's already in English, return it as is.
Return ONLY the translated text, nothing else.

Text: "{text}"
"""

    try:
        # Try Groq first
        if groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()

        # Try OpenAI as fallback
        if openai and openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()

        # No AI available, return original
        return text

    except Exception as e:
        st.warning(f"Translation failed, using original text: {e}")
        return text


@lru_cache(maxsize=100)
def extract_patient_data_cached(transcript):
    """Cached version of extract_patient_data"""
    return extract_patient_data(transcript)


def extract_patient_data(transcript):
    """Extract structured data from voice transcript (with fallback)

    NOTE: This function expects English input. Use translate_to_english() first
    if the transcript is in another language.
    """
    if not transcript:
        return {"error": "No transcript provided"}

    # Translate to English first to ensure consistent processing
    english_transcript = translate_to_english(transcript)

    prompt = f"""
Extract patient information from this medical consultation text.
Return ONLY valid JSON with these exact fields:
{{
  "name": "patient full name or null",
  "age": integer or null,
  "symptoms": ["list of medical symptoms"],
  "emergency_detected": boolean
}}

Rules:
- If no medical symptoms detected, return {{"error": "No symptoms found"}}
- Emergency keywords: heart attack, stroke, severe bleeding, unconscious
- Symptoms should be in English medical terms

Text: "{english_transcript}"
"""

    try:
        # Try Groq first
        if groq_client:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Updated to current model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},  # Force JSON response
            )
            result = response.choices[0].message.content
            # Clean up response - remove markdown code blocks if present
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            if result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
            return json.loads(result)

        # Try OpenAI as fallback
        if openai and openai.api_key:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            result = response.choices[0].message.content
            return json.loads(result)
        # Use simple regex fallback
        return extract_from_text(english_transcript)

    except Exception as e:
        st.warning(f"AI extraction failed, using simple parsing: {e}")
        return extract_from_text(english_transcript)


def extract_from_text(text_input):
    """Simple regex extraction for fallback - handles English and transliterated text"""
    if not text_input:
        return {"error": "No text provided"}

    text_lower = text_input.lower()

    # Name extraction - look for common patterns in multiple languages
    name = "Unknown"
    name_patterns = [
        r"(?:my name is|i am|this is|मेरा नाम|naam)\s+([A-Za-zÀ-ÿ\u0900-\u097F]+)",
        r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # Name at start (English)
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text_input, re.IGNORECASE | re.UNICODE)
        if match:
            potential_name = match.group(1).strip()
            # Filter out common non-name words
            if potential_name.lower() not in [
                "thank",
                "you",
                "hello",
                "hi",
                "और",
                "है",
                "मुझे",
                "हो",
                "रही",
            ]:
                name = potential_name
                break

    # Age extraction - look for numbers between 1-120
    age = None
    age_patterns = [
        r"(?:i am|age|aged|years old|year old|उम्र|साल)\s*(\d{1,3})",
        r"(\d{1,3})\s*(?:years old|year old|yrs old|yr old|साल|वर्ष)",
        r"\b(\d{1,3})\s*(?:years|yrs|साल)\b",
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text_lower)
        if match:
            potential_age = int(match.group(1))
            if 1 <= potential_age <= 120:
                age = potential_age
                break

    # If no age found, try any 2-3 digit number
    if not age:
        numbers = re.findall(r"\b(\d{1,3})\b", text_input)
        for num in numbers:
            num_int = int(num)
            if 1 <= num_int <= 120:
                age = num_int
                break

    # Symptom extraction - use the full transcript as symptoms
    # This works better for multilingual input
    symptoms = [text_input]

    # Emergency detection - multilingual keywords
    emergency_keywords = [
        "heart attack",
        "stroke",
        "bleeding",
        "unconscious",
        "emergency",
        "severe pain",
        "chest pain",
        "दिल का दौरा",
        "गंभीर",
        "खून",
        "बेहोश",
    ]
    emergency_detected = any(word in text_lower for word in emergency_keywords)

    return {
        "name": name,
        "age": age,
        "symptoms": symptoms,
        "emergency_detected": emergency_detected,
    }


# Test function
if __name__ == "__main__":
    test_transcript = "My name is Rajesh Kumar, I am 45 years old, I have severe chest pain"
    result = extract_patient_data(test_transcript)
    print("AI Extraction Result:", result)
