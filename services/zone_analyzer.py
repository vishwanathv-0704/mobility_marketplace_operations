class ZoneAnalyzer:

    def __init__(self, trips):

        self.trips = trips

        # Dictionary index:
        # zone -> list of trips
        self.zone_index = {}

        self._build_zone_index()

    # ========================================================
    # BUILD ZONE INDEX
    # ========================================================

    def _build_zone_index(self):

        for trip in self.trips:

            pickup_zone = trip.pickup_zone
            drop_zone = trip.drop_zone

            # Pickup zone
            if pickup_zone not in self.zone_index:
                self.zone_index[pickup_zone] = []

            self.zone_index[pickup_zone].append(trip)

            # Drop zone
            if drop_zone not in self.zone_index:
                self.zone_index[drop_zone] = []

            self.zone_index[drop_zone].append(trip)

    # ========================================================
    # GET TRIPS FOR A ZONE
    # ========================================================

    def get_zone_trips(self, zone):

        return self.zone_index.get(zone, [])

    # ========================================================
    # TOTAL TRIPS IN ZONE
    # ========================================================

    def trip_count(self, zone):

        return len(
            self.get_zone_trips(zone)
        )

    # ========================================================
    # COMPLETED TRIPS
    # ========================================================

    def completed_trips(self, zone):

        return sum(
            1
            for trip in self.get_zone_trips(zone)
            if trip.status == "Completed"
        )

    # ========================================================
    # CANCELLED TRIPS
    # ========================================================

    def cancelled_trips(self, zone):

        return sum(
            1
            for trip in self.get_zone_trips(zone)
            if trip.status == "Cancelled"
        )

    # ========================================================
    # REVENUE
    # ========================================================

    def revenue(self, zone):

        return round(
            sum(
                trip.fare
                for trip in self.get_zone_trips(zone)
                if trip.status == "Completed"
            ),
            2
        )

    # ========================================================
    # AVERAGE FARE
    # ========================================================

    def average_fare(self, zone):

        completed = [
            trip
            for trip in self.get_zone_trips(zone)
            if trip.status == "Completed"
        ]

        if not completed:
            return 0

        return round(
            sum(
                trip.fare
                for trip in completed
            ) / len(completed),
            2
        )

    # ========================================================
    # COMPLETION RATE
    # ========================================================

    def completion_rate(self, zone):

        total = self.trip_count(zone)

        if total == 0:
            return 0

        return round(
            (
                self.completed_trips(zone)
                / total
            ) * 100,
            2
        )

    # ========================================================
    # ZONE SUMMARY
    # ========================================================

    def analyze_zone(self, zone):

        if zone not in self.zone_index:
            return None

        return {

            "zone": zone,

            "total_trips":
                self.trip_count(zone),

            "completed_trips":
                self.completed_trips(zone),

            "cancelled_trips":
                self.cancelled_trips(zone),

            "completion_rate":
                self.completion_rate(zone),

            "revenue":
                self.revenue(zone),

            "average_fare":
                self.average_fare(zone)
        }

    # ========================================================
    # ALL ZONES
    # ========================================================

    def all_zones(self):

        return list(
            self.zone_index.keys()
        )
