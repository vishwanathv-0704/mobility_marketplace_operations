import csv

from models.driver import Driver
from models.trip import Trip
from models.zone import Zone


class DataLoader:

    def load_drivers(self, file_path):
        drivers = []

        with open(file_path, "r", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                driver = Driver(
                    driver_id=row["driver_id"],
                    driver_name=row["driver_name"],
                    city=row["city"],
                    vehicle_type=row["vehicle_type"],
                    rating=row["rating"],
                    status=row["status"]
                )

                drivers.append(driver)

        return drivers

    def load_trips(self, file_path):
        trips = []

        with open(file_path, "r", newline="") as file:

            reader = csv.DictReader(file)

            for row in reader:

                trip = Trip(
                    trip_id=row["trip_id"],
                    driver_id=row["driver_id"],
                    rider_id=row["rider_id"],
                    city=row["city"],
                    pickup_zone=row["pickup_zone"],
                    drop_zone=row["drop_zone"],
                    request_time=row["request_time"],
                    pickup_time=row["pickup_time"],
                    drop_time=row["drop_time"],
                    distance_km=row["distance_km"],
                    fare=row["fare"],
                    status=row["status"],
                    cancellation_reason=row["cancellation_reason"]
                )

                trips.append(trip)

        return trips

    def load_zones(self, trips):
        zones = {}

        for trip in trips:

            pickup_key = (
                trip.city,
                trip.pickup_zone
            )

            drop_key = (
                trip.city,
                trip.drop_zone
            )

            if pickup_key not in zones:

                zones[pickup_key] = Zone(
                    trip.city,
                    trip.pickup_zone
                )

            if drop_key not in zones:

                zones[drop_key] = Zone(
                    trip.city,
                    trip.drop_zone
                )

        return list(zones.values())



