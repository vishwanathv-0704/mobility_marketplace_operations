import csv
from datetime import datetime


class DataValidator:

    # ========================================================
    # REQUIRED COLUMNS
    # ========================================================

    DRIVER_COLUMNS = {
        "driver_id",
        "driver_name",
        "city",
        "vehicle_type",
        "rating",
        "status"
    }

    TRIP_COLUMNS = {
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
    }

    ACTIVITY_COLUMNS = {
        "driver_id",
        "timestamp",
        "status"
    }

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(self):

        self.errors = []

    # ========================================================
    # LOAD CSV ROWS
    # ========================================================

    def read_csv(self, file_path):

        with open(file_path, "r", newline="") as file:

            reader = csv.DictReader(file)

            return list(reader), reader.fieldnames

    # ========================================================
    # REQUIRED COLUMN VALIDATION
    # ========================================================

    def validate_required_columns(
        self,
        actual_columns,
        required_columns,
        dataset_name
    ):

        missing_columns = (
            required_columns - set(actual_columns or [])
        )

        for column in missing_columns:

            self.errors.append(
                f"{dataset_name}: Missing required column '{column}'"
            )

    # ========================================================
    # MISSING VALUE VALIDATION
    # ========================================================

    def validate_missing_values(
        self,
        rows,
        columns,
        dataset_name
    ):

        for row_number, row in enumerate(rows, start=2):

            for column in columns:

                value = row.get(column)

                if value is None or value.strip() == "":

                    # pickup/drop timestamps can be empty
                    # for cancelled trips, so don't flag them here
                    if (
                        dataset_name == "Trips"
                        and column in {
                            "pickup_time",
                            "drop_time",
                            "cancellation_reason"
                        }
                    ):
                        continue

                    self.errors.append(
                        f"{dataset_name}: Row {row_number} "
                        f"has missing value in '{column}'"
                    )

    # ========================================================
    # DRIVER ID VALIDATION
    # ========================================================

    def validate_driver_ids(
        self,
        driver_rows,
        trip_rows
    ):

        valid_driver_ids = {
            row["driver_id"]
            for row in driver_rows
            if row.get("driver_id")
        }

        for row_number, row in enumerate(trip_rows, start=2):

            driver_id = row.get("driver_id")

            if driver_id and driver_id not in valid_driver_ids:

                self.errors.append(
                    f"Trips: Row {row_number} references "
                    f"unknown driver ID '{driver_id}'"
                )

    # ========================================================
    # TIMESTAMP VALIDATION
    # ========================================================

    def validate_timestamp(
        self,
        value,
        field_name,
        row_number,
        dataset_name
    ):

        if not value:
            return None

        try:

            return datetime.strptime(
                value,
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            self.errors.append(
                f"{dataset_name}: Row {row_number} has "
                f"invalid timestamp in '{field_name}'"
            )

            return None

    def validate_timestamps(self, trip_rows):

        for row_number, row in enumerate(trip_rows, start=2):

            request_time = self.validate_timestamp(
                row.get("request_time"),
                "request_time",
                row_number,
                "Trips"
            )

            pickup_time = self.validate_timestamp(
                row.get("pickup_time"),
                "pickup_time",
                row_number,
                "Trips"
            )

            drop_time = self.validate_timestamp(
                row.get("drop_time"),
                "drop_time",
                row_number,
                "Trips"
            )

            # ------------------------------------------------
            # Validate chronological order
            # ------------------------------------------------

            if (
                request_time
                and pickup_time
                and pickup_time < request_time
            ):

                self.errors.append(
                    f"Trips: Row {row_number} has "
                    f"pickup time before request time"
                )

            if (
                pickup_time
                and drop_time
                and drop_time < pickup_time
            ):

                self.errors.append(
                    f"Trips: Row {row_number} has "
                    f"drop time before pickup time"
                )

    # ========================================================
    # FARE VALIDATION
    # ========================================================

    def validate_fares(self, trip_rows):

        for row_number, row in enumerate(trip_rows, start=2):

            fare_value = row.get("fare")

            if not fare_value:
                continue

            try:

                fare = float(fare_value)

                if fare < 0:

                    self.errors.append(
                        f"Trips: Row {row_number} has "
                        f"negative fare: {fare}"
                    )

            except ValueError:

                self.errors.append(
                    f"Trips: Row {row_number} has "
                    f"invalid fare value: '{fare_value}'"
                )

    # ========================================================
    # TRIP DURATION VALIDATION
    # ========================================================

    def validate_trip_durations(self, trip_rows):

        for row_number, row in enumerate(trip_rows, start=2):

            pickup = row.get("pickup_time")
            drop = row.get("drop_time")

            if not pickup or not drop:
                continue

            try:

                pickup_time = datetime.strptime(
                    pickup,
                    "%Y-%m-%d %H:%M:%S"
                )

                drop_time = datetime.strptime(
                    drop,
                    "%Y-%m-%d %H:%M:%S"
                )

                duration = (
                    drop_time - pickup_time
                ).total_seconds() / 60

                if duration < 0:

                    self.errors.append(
                        f"Trips: Row {row_number} has "
                        f"invalid trip duration"
                    )

            except ValueError:
                # Timestamp validation already reports this.
                continue

    # ========================================================
    # COMPLETE VALIDATION
    # ========================================================

    def validate_all(
        self,
        drivers_path,
        trips_path,
        activity_path
    ):

        # Reset errors for every validation run
        self.errors = []

        # ----------------------------------------------------
        # Read datasets
        # ----------------------------------------------------

        driver_rows, driver_columns = self.read_csv(
            drivers_path
        )

        trip_rows, trip_columns = self.read_csv(
            trips_path
        )

        activity_rows, activity_columns = self.read_csv(
            activity_path
        )

        # ----------------------------------------------------
        # Required columns
        # ----------------------------------------------------

        self.validate_required_columns(
            driver_columns,
            self.DRIVER_COLUMNS,
            "Drivers"
        )

        self.validate_required_columns(
            trip_columns,
            self.TRIP_COLUMNS,
            "Trips"
        )

        self.validate_required_columns(
            activity_columns,
            self.ACTIVITY_COLUMNS,
            "Driver Activity"
        )

        # ----------------------------------------------------
        # Missing values
        # ----------------------------------------------------

        if self.DRIVER_COLUMNS.issubset(
            set(driver_columns or [])
        ):

            self.validate_missing_values(
                driver_rows,
                self.DRIVER_COLUMNS,
                "Drivers"
            )

        if self.TRIP_COLUMNS.issubset(
            set(trip_columns or [])
        ):

            self.validate_missing_values(
                trip_rows,
                self.TRIP_COLUMNS,
                "Trips"
            )

        if self.ACTIVITY_COLUMNS.issubset(
            set(activity_columns or [])
        ):

            self.validate_missing_values(
                activity_rows,
                self.ACTIVITY_COLUMNS,
                "Driver Activity"
            )

        # ----------------------------------------------------
        # Cross-dataset validation
        # ----------------------------------------------------

        self.validate_driver_ids(
            driver_rows,
            trip_rows
        )

        # ----------------------------------------------------
        # Timestamp validation
        # ----------------------------------------------------

        self.validate_timestamps(
            trip_rows
        )

        # ----------------------------------------------------
        # Fare validation
        # ----------------------------------------------------

        self.validate_fares(
            trip_rows
        )

        # ----------------------------------------------------
        # Duration validation
        # ----------------------------------------------------

        self.validate_trip_durations(
            trip_rows
        )

        return self.errors
