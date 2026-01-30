from ai_processing import extract_from_text, extract_patient_data

# Test cases
test_cases = [
    "My name is Rajesh Kumar, I am 45 years old, I have chest pain and breathing difficulty",
    "I am Priya Sharma, 32 years old, suffering from fever and headache",
    "This is Amit Patel, age 28, I have stomach pain",
    "Thank you",
    "John Doe 55 years old severe chest pain"
]

print("=== Testing Fallback Extraction ===\n")
for test in test_cases:
    print(f"Input: {test}")
    result = extract_from_text(test)
    print(f"Result: {result}\n")

print("\n=== Testing AI Extraction ===\n")
test = "My name is Rajesh Kumar, I am 45 years old, I have chest pain"
print(f"Input: {test}")
result = extract_patient_data(test)
print(f"Result: {result}")
