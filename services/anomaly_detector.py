class AnomalyDetector:

    def __init__(
        self,
        trips,
        drivers,
        max_trip_minutes=180,
        max_fare=5000,
        max_cancellation_rate=0.30,
        min_rating=3.0,
        max_trip_count=100
    ):
        self.trips = trips
        self.drivers = drivers

        self.max_trip_minutes = max_trip_minutes
        self.max_fare = max_fare
        self.max_cancellation_rate = max_cancellation_rate
        self.min_rating = min_rating
        self.max_trip_count = max_trip_count

        self.driver_ids = {
            driver.driver_id for driver in drivers
        }

    def detect(self):
        anomalies = []

        anomalies.extend(self._check_trips())
        anomalies.extend(self._check_drivers())

        return anomalies

    def _check_trips(self):
        anomalies = []

        for trip in self.trips:

            # Negative fare
            if trip.fare < 0:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Negative fare"
                })

            # Zero / negative distance
            if trip.distance_km <= 0:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Zero or negative distance"
                })

            # Invalid / missing timestamps
            if trip.pickup_time is None or trip.drop_time is None:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Invalid timestamps"
                })

            elif trip.drop_time < trip.pickup_time:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Drop time < pickup time"
                })

            else:
                duration = trip.calculate_duration()

                if duration is not None and duration > self.max_trip_minutes:
                    anomalies.append({
                        "type": "Trip",
                        "id": trip.trip_id,
                        "issue": "Extremely long trip duration"
                    })

            # Unknown driver
            if trip.driver_id not in self.driver_ids:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Unknown driver"
                })

            # Unusual fare
            if trip.fare > self.max_fare:
                anomalies.append({
                    "type": "Trip",
                    "id": trip.trip_id,
                    "issue": "Unusual fare"
                })

        return anomalies

    def _check_drivers(self):
        anomalies = []

        trip_counts = {}
        cancelled_counts = {}

        for trip in self.trips:
            driver_id = trip.driver_id

            trip_counts[driver_id] = trip_counts.get(driver_id, 0) + 1

            if trip.status == "Cancelled":
                cancelled_counts[driver_id] = (
                    cancelled_counts.get(driver_id, 0) + 1
                )

        for driver in self.drivers:

            driver_id = driver.driver_id
            total = trip_counts.get(driver_id, 0)
            cancelled = cancelled_counts.get(driver_id, 0)

            # High cancellation rate
            if total > 0:
                cancellation_rate = cancelled / total

                if cancellation_rate > self.max_cancellation_rate:
                    anomalies.append({
                        "type": "Driver",
                        "id": driver_id,
                        "issue": "Cancellation rate > threshold"
                    })

            # Unusually high trip count
            if total > self.max_trip_count:
                anomalies.append({
                    "type": "Driver",
                    "id": driver_id,
                    "issue": "Unusually high trip count"
                })

            # Low rating
            if driver.rating < self.min_rating:
                anomalies.append({
                    "type": "Driver",
                    "id": driver_id,
                    "issue": "Low rating"
                })

        return anomalies
