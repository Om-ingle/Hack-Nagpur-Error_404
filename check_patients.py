from db.patient_repo import get_all_patients

# Check all patients in database
patients = get_all_patients()

print("=== Patients in Database ===")
for patient in patients:
    print(f"Phone: {patient['phone_number']}, YOB: {patient['yob']}, Name: {patient.get('name', 'N/A')}")
print(f"\nTotal patients: {len(patients)}")

