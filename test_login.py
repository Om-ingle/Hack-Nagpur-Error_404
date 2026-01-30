from db.patient_repo import get_patient_by_phone, verify_patient

# Test login with existing credentials
phone = "9822635646"
yob = 2004

print(f"Testing login with Phone: {phone}, YOB: {yob}")

# Check if patient exists
patient = get_patient_by_phone(phone)

if patient:
    print(f"\nPatient found:")
    print(f"  Phone: {patient['phone_number']}")
    print(f"  YOB in DB: {patient['yob']} (type: {type(patient['yob'])})")
    print(f"  YOB entered: {yob} (type: {type(yob)})")
    print(f"  Match: {patient['yob'] == yob}")
    
    # Test verification
    verified = verify_patient(phone, yob)
    print(f"\nVerification result: {'SUCCESS' if verified else 'FAILED'}")
else:
    print("\nNo patient found with this phone number")

