from services.validation_service import DataValidator


validator = DataValidator()

errors = validator.validate_all(
    "data/drivers.csv",
    "data/trips.csv",
    "data/driver_activity.csv"
)

print(f"Total validation errors: {len(errors)}")

print("\nFirst 20 errors:")

for error in errors[:20]:
    print("-", error)
