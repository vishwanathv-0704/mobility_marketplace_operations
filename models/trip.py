from datetime import datetime


class Trip:

    def __init__(
        self,
        trip_id,
        driver_id,
        rider_id,
        city,
        pickup_zone,
        drop_zone,
        request_time,
        pickup_time,
        drop_time,
        distance_km,
        fare,
        status,
        cancellation_reason
    ):
        self.trip_id = trip_id
        self.driver_id = driver_id
        self.rider_id = rider_id
        self.city = city
        self.pickup_zone = pickup_zone
        self.drop_zone = drop_zone

        self.request_time = self._parse_datetime(request_time)
        self.pickup_time = self._parse_datetime(pickup_time)
        self.drop_time = self._parse_datetime(drop_time)

        self.distance_km = float(distance_km)
        self.fare = float(fare)
        self.status = status
        self.cancellation_reason = cancellation_reason

    @staticmethod
    def _parse_datetime(value):

        if not value:
            return None

        return datetime.strptime(
            value,
            "%Y-%m-%d %H:%M:%S"
        )

    def is_completed(self):
        return self.status == "Completed"

    def calculate_duration(self):

        if self.pickup_time is None or self.drop_time is None:
            return None

        duration = self.drop_time - self.pickup_time

        return duration.total_seconds() / 60

    def calculate_fare_per_km(self):

        if self.distance_km <= 0:
            return None

        return self.fare / self.distance_km
