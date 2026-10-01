import heapq
from collections import Counter, defaultdict
from datetime import datetime


class AdvancedAnalyzer:

    def __init__(self, trips, drivers=None, activities=None):
        self.trips = trips
        self.drivers = drivers or []
        self.activities = activities or []

    def top_k(self, data, k=5):
        if not data or k <= 0:
            return []

        heap = []

        for key, value in data.items():
            item = (value, key)

            if len(heap) < k:
                heapq.heappush(heap, item)
            elif item > heap[0]:
                heapq.heapreplace(heap, item)

        return sorted(heap, reverse=True)

    def top_drivers_by_completed(self, k=5):
        counts = Counter()

        for trip in self.trips:
            if trip.status == "Completed":
                counts[trip.driver_id] += 1

        return self.top_k(counts, k)

    def top_zones_by_demand(self, k=5):
        counts = Counter()

        for trip in self.trips:
            if trip.pickup_zone:
                counts[trip.pickup_zone] += 1

        return self.top_k(counts, k)

    def idle_time_analysis(self, threshold_minutes=30):
        driver_trips = defaultdict(list)

        for trip in self.trips:
            if trip.status != "Completed":
                continue

            pickup = self._parse_time(trip.pickup_time)
            drop = self._parse_time(trip.drop_time)

            if pickup and drop:
                driver_trips[trip.driver_id].append(
                    (pickup, drop, trip.trip_id)
                )

        results = []

        for driver_id, trips in driver_trips.items():
            trips.sort(key=lambda x: x[0])

            for i in range(len(trips) - 1):
                current = trips[i]
                next_trip = trips[i + 1]

                idle_minutes = (
                    next_trip[0] - current[1]
                ).total_seconds() / 60

                if idle_minutes >= threshold_minutes:
                    results.append({
                        "driver_id": driver_id,
                        "previous_trip": current[2],
                        "next_trip": next_trip[2],
                        "idle_minutes": round(idle_minutes, 2)
                    })

        return sorted(
            results,
            key=lambda x: x["idle_minutes"],
            reverse=True
        )

    def peak_demand(self):
        slots = Counter()

        for trip in self.trips:
            request_time = self._parse_time(trip.request_time)

            if not request_time:
                continue

            hour = request_time.hour

            if 6 <= hour < 9:
                slot = "06-09"
            elif 9 <= hour < 12:
                slot = "09-12"
            elif 12 <= hour < 15:
                slot = "12-15"
            elif 15 <= hour < 18:
                slot = "15-18"
            elif 18 <= hour < 21:
                slot = "18-21"
            elif 21 <= hour < 24:
                slot = "21-00"
            else:
                slot = "00-06"

            slots[slot] += 1

        return dict(
            sorted(
                slots.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

    def driver_utilization(self, high_threshold=70, medium_threshold=40):
        driver_data = defaultdict(
            lambda: {
                "online": 0,
                "busy": 0,
                "idle": 0
            }
        )

        grouped = defaultdict(list)

        for activity in self.activities:

            if isinstance(activity, dict):
                driver_id = activity.get("driver_id")
                timestamp = activity.get("timestamp")
                status = activity.get("status")
            else:
                driver_id = getattr(activity, "driver_id", None)
                timestamp = getattr(activity, "timestamp", None)
                status = getattr(activity, "status", None)

            timestamp = self._parse_time(timestamp)

            if driver_id and timestamp:
                grouped[driver_id].append(
                    (timestamp, status)
                )

        results = []

        for driver_id, events in grouped.items():
            events.sort(key=lambda x: x[0])

            for i in range(len(events) - 1):
                current_time, current_status = events[i]
                next_time, _ = events[i + 1]

                minutes = (
                    next_time - current_time
                ).total_seconds() / 60

                if current_status == "Online":
                    driver_data[driver_id]["online"] += minutes
                elif current_status == "Busy":
                    driver_data[driver_id]["busy"] += minutes
                elif current_status == "Idle":
                    driver_data[driver_id]["idle"] += minutes

        for driver_id, values in driver_data.items():
            online_hours = values["online"] / 60
            busy_hours = values["busy"] / 60
            idle_hours = values["idle"] / 60

            if online_hours > 0:
                utilization = (busy_hours / online_hours) * 100
            else:
                utilization = 0

            if utilization >= high_threshold:
                category = "High Utilization"
            elif utilization >= medium_threshold:
                category = "Medium Utilization"
            else:
                category = "Low Utilization"

            results.append({
                "driver_id": driver_id,
                "online_hours": round(online_hours, 2),
                "busy_hours": round(busy_hours, 2),
                "idle_hours": round(idle_hours, 2),
                "utilization": round(utilization, 2),
                "category": category
            })

        return sorted(
            results,
            key=lambda x: x["utilization"],
            reverse=True
        )

    def cancellation_analysis(self):
        cancellations = [
            trip
            for trip in self.trips
            if trip.status == "Cancelled"
        ]

        by_reason = Counter()
        by_zone = Counter()
        by_driver = Counter()

        for trip in cancellations:
            reason = trip.cancellation_reason or "Unknown"
            zone = trip.pickup_zone or "Unknown"
            driver = trip.driver_id or "Unknown"

            by_reason[reason] += 1
            by_zone[zone] += 1
            by_driver[driver] += 1

        return {
            "total_cancellations": len(cancellations),
            "by_reason": dict(by_reason),
            "by_zone": dict(by_zone),
            "by_driver": dict(by_driver)
        }

    @staticmethod
    def _parse_time(value):
        if not value:
            return None

        if isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(
                str(value),
                "%Y-%m-%d %H:%M:%S"
            )
        except (ValueError, TypeError):
            return None
