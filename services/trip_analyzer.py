class TripAnalyzer:

    def __init__(self, trips):

        self.trips = trips

        # Dictionary index:
        # trip_id -> Trip object
        self.trip_index = {
            trip.trip_id: trip
            for trip in trips
        }

    # ========================================================
    # SEARCH TRIP
    # ========================================================

    def get_trip(self, trip_id):

        return self.trip_index.get(trip_id)

    # ========================================================
    # BASIC TRIP COUNTS
    # ========================================================

    def total_trips(self):

        return len(self.trips)

    def completed_trips(self):

        return sum(
            1
            for trip in self.trips
            if trip.status == "Completed"
        )

    def cancelled_trips(self):

        return sum(
            1
            for trip in self.trips
            if trip.status == "Cancelled"
        )

    # ========================================================
    # COMPLETION / CANCELLATION RATE
    # ========================================================

    def completion_rate(self):

        total = self.total_trips()

        if total == 0:
            return 0

        return round(
            (self.completed_trips() / total) * 100,
            2
        )

    def cancellation_rate(self):

        total = self.total_trips()

        if total == 0:
            return 0

        return round(
            (self.cancelled_trips() / total) * 100,
            2
        )

    # ========================================================
    # REVENUE
    # ========================================================

    def total_revenue(self):

        return round(
            sum(
                trip.fare
                for trip in self.trips
                if trip.status == "Completed"
            ),
            2
        )

    # ========================================================
    # AVERAGE FARE
    # ========================================================

    def average_fare(self):

        completed = [
            trip
            for trip in self.trips
            if trip.status == "Completed"
        ]

        if not completed:
            return 0

        return round(
            sum(trip.fare for trip in completed)
            / len(completed),
            2
        )

    # ========================================================
    # AVERAGE DISTANCE
    # ========================================================

    def average_distance(self):

        completed = [
            trip
            for trip in self.trips
            if trip.status == "Completed"
        ]

        if not completed:
            return 0

        return round(
            sum(
                trip.distance_km
                for trip in completed
            ) / len(completed),
            2
        )

    # ========================================================
    # TRIPS BY STATUS
    # ========================================================

    def trips_by_status(self):

        status_count = {}

        for trip in self.trips:

            status = trip.status

            if status not in status_count:
                status_count[status] = 0

            status_count[status] += 1

        return status_count

    # ========================================================
    # CANCELLATION REASONS
    # ========================================================

    def cancellation_reasons(self):

        reasons = {}

        for trip in self.trips:

            if trip.status != "Cancelled":
                continue

            reason = trip.cancellation_reason

            if not reason:
                reason = "Unknown"

            reasons[reason] = (
                reasons.get(reason, 0) + 1
            )

        return reasons

    # ========================================================
    # COMPLETE SUMMARY
    # ========================================================

    def get_summary(self):

        return {
            "total_trips": self.total_trips(),

            "completed_trips":
                self.completed_trips(),

            "cancelled_trips":
                self.cancelled_trips(),

            "completion_rate":
                self.completion_rate(),

            "cancellation_rate":
                self.cancellation_rate(),

            "total_revenue":
                self.total_revenue(),

            "average_fare":
                self.average_fare(),

            "average_distance":
                self.average_distance(),

            "trips_by_status":
                self.trips_by_status(),

            "cancellation_reasons":
                self.cancellation_reasons()
        }
