class DriverAnalyzer:

    def __init__(self, drivers, trips):

        self.drivers = drivers
        self.trips = trips

        # Dictionary index:
        # driver_id -> Driver object
        self.driver_index = {
            driver.driver_id: driver
            for driver in drivers
        }

    # ========================================================
    # SEARCH DRIVER
    # ========================================================

    def get_driver(self, driver_id):

        return self.driver_index.get(driver_id)

    # ========================================================
    # GET DRIVER TRIPS
    # ========================================================

    def get_driver_trips(self, driver_id):

        return [
            trip
            for trip in self.trips
            if trip.driver_id == driver_id
        ]

    # ========================================================
    # DRIVER PERFORMANCE
    # ========================================================

    def analyze_driver(self, driver_id):

        driver = self.get_driver(driver_id)

        if driver is None:
            return None

        driver_trips = self.get_driver_trips(driver_id)

        total_trips = len(driver_trips)

        completed_trips = sum(
            1
            for trip in driver_trips
            if trip.status == "Completed"
        )

        cancelled_trips = sum(
            1
            for trip in driver_trips
            if trip.status == "Cancelled"
        )

        revenue = sum(
            trip.fare
            for trip in driver_trips
            if trip.status == "Completed"
        )

        completed = [
            trip
            for trip in driver_trips
            if trip.status == "Completed"
        ]

        # ----------------------------------------------------
        # Rates
        # ----------------------------------------------------

        if total_trips > 0:

            completion_rate = (
                completed_trips / total_trips
            ) * 100

            cancellation_rate = (
                cancelled_trips / total_trips
            ) * 100

        else:

            completion_rate = 0
            cancellation_rate = 0

        # ----------------------------------------------------
        # Average fare
        # ----------------------------------------------------

        if completed:

            average_fare = (
                sum(trip.fare for trip in completed)
                / len(completed)
            )

        else:

            average_fare = 0

        # ----------------------------------------------------
        # Average distance
        # ----------------------------------------------------

        if completed:

            average_distance = (
                sum(
                    trip.distance_km
                    for trip in completed
                )
                / len(completed)
            )

        else:

            average_distance = 0

        # ----------------------------------------------------
        # Average fare per KM
        # ----------------------------------------------------

        if completed:

            total_distance = sum(
                trip.distance_km
                for trip in completed
            )

            if total_distance > 0:

                average_fare_per_km = (
                    revenue / total_distance
                )

            else:

                average_fare_per_km = 0

        else:

            average_fare_per_km = 0

        return {

            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "city": driver.city,
            "rating": driver.rating,
            "status": driver.status,

            "total_trips": total_trips,
            "completed_trips": completed_trips,
            "cancelled_trips": cancelled_trips,

            "completion_rate": round(
                completion_rate,
                2
            ),

            "cancellation_rate": round(
                cancellation_rate,
                2
            ),

            "revenue": round(
                revenue,
                2
            ),

            "average_fare": round(
                average_fare,
                2
            ),

            "average_distance": round(
                average_distance,
                2
            ),

            "average_fare_per_km": round(
                average_fare_per_km,
                2
            )
        }
