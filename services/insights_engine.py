from collections import Counter


class InsightsEngine:

    def __init__(self, trips, anomalies=None):
        self.trips = trips
        self.anomalies = anomalies or []

    def generate(self):
        insights = []

        if not self.trips:
            return ["No trip data available."]

        # 1. Highest demand zone
        zones = Counter()

        for trip in self.trips:
            if trip.pickup_zone:
                zones[trip.pickup_zone] += 1

        if zones:
            zone, count = zones.most_common(1)[0]
            insights.append(
                f"{zone} has the highest trip demand with {count} requests."
            )

        # 2. Peak demand time
        time_slots = Counter()

        for trip in self.trips:
            if trip.request_time:
                hour = trip.request_time.hour

                if 0 <= hour < 6:
                    slot = "00-06"
                elif 6 <= hour < 9:
                    slot = "06-09"
                elif 9 <= hour < 12:
                    slot = "09-12"
                elif 12 <= hour < 15:
                    slot = "12-15"
                elif 15 <= hour < 18:
                    slot = "15-18"
                elif 18 <= hour < 21:
                    slot = "18-21"
                else:
                    slot = "21-00"

                time_slots[slot] += 1

        if time_slots:
            slot, count = time_slots.most_common(1)[0]
            insights.append(
                f"The {slot} period has the highest trip demand with {count} requests."
            )

        # 3. Cancellation insight
        cancellations = [
            trip for trip in self.trips
            if trip.status == "Cancelled"
        ]

        if cancellations:
            reasons = Counter(
                trip.cancellation_reason or "Unknown"
                for trip in cancellations
            )

            reason, count = reasons.most_common(1)[0]

            insights.append(
                f"{reason} is the largest cancellation category with {count} cancellations."
            )

        # 4. Anomaly count
        insights.append(
            f"{len(self.anomalies)} trips/driver records have been flagged as anomalies."
        )

        return insights
