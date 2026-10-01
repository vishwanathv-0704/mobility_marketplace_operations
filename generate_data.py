import csv
import random
import os
from datetime import datetime, timedelta


# ============================================================
# CONFIGURATION
# ============================================================

NUM_DRIVERS = 250
NUM_TRIPS = 4500

START_DATE = datetime(2023, 10, 1)

CITIES = [
    "Bangalore",
    "Mumbai",
    "Delhi"
]

ZONES = {
    "Bangalore": [
        "Koramangala",
        "Indiranagar",
        "Whitefield",
        "HSR Layout",
        "Jayanagar"
    ],
    "Mumbai": [
        "Bandra",
        "Andheri",
        "Colaba",
        "Powai",
        "Juhu"
    ],
    "Delhi": [
        "Connaught Place",
        "Saket",
        "Vasant Kunj",
        "Dwarka",
        "Rohini"
    ]
}

NAMES = [
    "Rahul",
    "Amit",
    "Priya",
    "Neha",
    "Vikram",
    "Suresh",
    "Ravi",
    "Anjali",
    "Karan",
    "Pooja"
]

VEHICLE_TYPES = [
    "Hatchback",
    "Sedan",
    "SUV"
]

STATUS_DRIVER = [
    "Active",
    "Active",
    "Active",
    "Active",
    "Inactive"
]

CANCEL_REASONS = [
    "Driver Cancelled",
    "Rider Cancelled",
    "Driver Not Found",
    "Payment Issue",
    "Other"
]


# ============================================================
# SETUP
# ============================================================

os.makedirs("data", exist_ok=True)

# ============================================================
# HELPER FUNCTION
# ============================================================

def random_date(start, days=30):
    """
    Generate a random datetime within the given number of days.
    """
    return start + timedelta(
        days=random.randint(0, days - 1),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )


# ============================================================
# GENERATE DRIVERS
# ============================================================

def generate_drivers():

    print("Generating drivers.csv...")

    drivers = []

    with open("data/drivers.csv", "w", newline="") as f:

        writer = csv.writer(f)

        # CSV header
        writer.writerow([
            "driver_id",
            "driver_name",
            "city",
            "vehicle_type",
            "rating",
            "status"
        ])

        for i in range(1, NUM_DRIVERS + 1):

            driver_id = f"D{100 + i}"

            city = random.choice(CITIES)

            driver = {
                "driver_id": driver_id,
                "driver_name": random.choice(NAMES),
                "city": city,
                "vehicle_type": random.choice(VEHICLE_TYPES),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "status": random.choice(STATUS_DRIVER)
            }

            drivers.append(driver)

            writer.writerow(driver.values())

    return drivers


# ============================================================
# GENERATE TRIPS
# ============================================================

def generate_trips(drivers):

    print("Generating trips.csv...")

    with open("data/trips.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "trip_id",
            "driver_id",
            "rider_id",
            "city",
            "pickup_zone",
            "drop_zone",
            "request_time",
            "pickup_time",
            "drop_time",
            "distance_km",
            "fare",
            "status",
            "cancellation_reason"
        ])

        for i in range(1, NUM_TRIPS + 1):

            trip_id = f"T{1000 + i}"

            # ------------------------------------------------
            # Inject unknown driver IDs
            # ------------------------------------------------

            if i in [100, 500, 900]:

                driver = {
                    "driver_id": "D9999",
                    "city": "Bangalore"
                }

            else:

                driver = random.choice(drivers)

            driver_id = driver["driver_id"]
            city = driver["city"]

            # ------------------------------------------------
            # Select zones
            # ------------------------------------------------

            pickup_zone = random.choice(ZONES[city])

            drop_zone = random.choice(ZONES[city])

            # Pickup and drop zone should normally differ
            while drop_zone == pickup_zone:
                drop_zone = random.choice(ZONES[city])

            # ------------------------------------------------
            # Rider
            # ------------------------------------------------

            rider_id = f"R{random.randint(1000, 5000)}"

            # ------------------------------------------------
            # Request time
            # ------------------------------------------------

            request_time = random_date(START_DATE)

            # ------------------------------------------------
            # Trip status
            # Approx. 11.5% cancellation rate
            # ------------------------------------------------

            is_cancelled = random.random() < 0.115

            status = "Cancelled" if is_cancelled else "Completed"

            # ------------------------------------------------
            # Cancelled trip
            # ------------------------------------------------

            if is_cancelled:

                cancellation_reason = random.choices(
                    CANCEL_REASONS,
                    weights=[35, 25, 20, 10, 10]
                )[0]

                pickup_time = ""
                drop_time = ""

                distance_km = 0.0
                fare = 0.0

            # ------------------------------------------------
            # Completed trip
            # ------------------------------------------------

            else:

                cancellation_reason = ""

                pickup_time = request_time + timedelta(
                    minutes=random.randint(2, 15)
                )

                distance_km = round(
                    random.uniform(2.0, 25.0),
                    1
                )

                drop_time = pickup_time + timedelta(
                    minutes=int(
                        distance_km * random.uniform(2.5, 4.0)
                    )
                )

                fare = round(
                    distance_km * random.uniform(15.0, 25.0) + 50
                )

            # =================================================
            # INJECT ANOMALIES
            # =================================================

            # 17 trips with missing pickup timestamps
            if i % 250 == 0 and i <= 250 * 17:
                pickup_time = ""

            # 4 trips with negative fare
            if i in [50, 150, 250, 350]:
                fare = -abs(fare)

            # Drop time earlier than pickup time
            if i in [400, 800]:

                # Make sure pickup_time is a datetime
                if isinstance(pickup_time, datetime):

                    drop_time = pickup_time - timedelta(minutes=10)

            # Unusually high fare
            if i in [1000, 2000]:
                fare = 5000.0

            # =================================================
            # FORMAT DATETIME VALUES
            # =================================================

            request_string = request_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            if isinstance(pickup_time, datetime):

                pickup_string = pickup_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            else:

                pickup_string = pickup_time

            if isinstance(drop_time, datetime):

                drop_string = drop_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            else:

                drop_string = drop_time

            # =================================================
            # WRITE ROW
            # =================================================

            writer.writerow([
                trip_id,
                driver_id,
                rider_id,
                city,
                pickup_zone,
                drop_zone,
                request_string,
                pickup_string,
                drop_string,
                distance_km,
                fare,
                status,
                cancellation_reason
            ])


# ============================================================
# GENERATE DRIVER ACTIVITY
# ============================================================

def generate_driver_activity(drivers):

    print("Generating driver_activity.csv...")

    with open("data/driver_activity.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "driver_id",
            "timestamp",
            "status"
        ])

        activity_statuses = [
            "Online",
            "Busy",
            "Idle",
            "Offline"
        ]

        for driver in drivers:

            # Generate activity only for active drivers
            if driver["status"] == "Inactive":
                continue

            current_time = START_DATE + timedelta(
                days=random.randint(0, 5)
            )

            # Generate a few shifts
            for _ in range(random.randint(5, 15)):

                # --------------------------------------------
                # Login
                # --------------------------------------------

                writer.writerow([
                    driver["driver_id"],
                    current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Online"
                ])

                # --------------------------------------------
                # Status changes
                # --------------------------------------------

                for _ in range(random.randint(3, 10)):

                    current_time += timedelta(
                        minutes=random.randint(15, 120)
                    )

                    writer.writerow([
                        driver["driver_id"],
                        current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        random.choice([
                            "Busy",
                            "Idle"
                        ])
                    ])

                # --------------------------------------------
                # Logout
                # --------------------------------------------

                current_time += timedelta(
                    minutes=random.randint(10, 60)
                )

                writer.writerow([
                    driver["driver_id"],
                    current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Offline"
                ])

                # --------------------------------------------
                # Next shift
                # --------------------------------------------

                current_time += timedelta(
                    hours=random.randint(12, 24)
                )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("Starting data generation...")

    drivers_data = generate_drivers()

    generate_trips(drivers_data)

    generate_driver_activity(drivers_data)

    print("Data generation complete!")
    print("Files saved in the 'data/' directory.")
