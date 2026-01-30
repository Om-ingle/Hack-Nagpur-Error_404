from db.schema import initialize_database

if __name__ == "__main__":
    print("Initializing SQLite database...")
    initialize_database()
    print("\n=== Sample Login Credentials ===")
    print("SENIOR Doctor: Role=SENIOR, PIN=1234")
    print("JUNIOR Doctor: Role=JUNIOR, PIN=5678")
    print("SENIOR Doctor: Role=SENIOR, PIN=9999")
