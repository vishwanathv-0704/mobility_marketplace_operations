from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import os
import pandas as pd

from services.data_loader import DataLoader
from services.validation_service import DataValidator
from services.anomaly_detector import AnomalyDetector
from services.insights_engine import InsightsEngine


app = Flask(__name__)

UPLOAD_FOLDER = "data/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def read_csv_safely(path):
    """
    Safely read a CSV file.

    Returns:
        dataframe, error_message
    """

    # Completely empty file
    if os.path.getsize(path) == 0:
        return pd.DataFrame(), "File is completely empty."

    try:
        df = pd.read_csv(path)

        # CSV contains headers but no rows
        if df.empty:
            return df, "File contains headers but no data rows."

        return df, None

    except pd.errors.EmptyDataError:
        return pd.DataFrame(), "File is completely empty."

    except pd.errors.ParserError:
        return pd.DataFrame(), "CSV file is malformed or incorrectly formatted."

    except UnicodeDecodeError:
        return pd.DataFrame(), "CSV file contains unsupported character encoding."

    except Exception as e:
        return pd.DataFrame(), f"Unable to read CSV: {str(e)}"


def validate_required_columns(df, required_columns, dataset_name):
    """
    Check whether required columns exist.
    """

    errors = []

    if df.empty:
        return errors

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    for column in missing_columns:
        errors.append(
            f"{dataset_name}: Missing required column '{column}'."
        )

    return errors


def validate_basic_dataframe(df, dataset_name):
    """
    Generic dataframe-level validation.
    """

    errors = []

    if df.empty:
        return errors

    # Duplicate column names
    duplicate_columns = df.columns[
        df.columns.duplicated()
    ].tolist()

    for column in duplicate_columns:
        errors.append(
            f"{dataset_name}: Duplicate column '{column}'."
        )

    # Completely blank columns
    for column in df.columns:

        if df[column].isna().all():

            errors.append(
                f"{dataset_name}: Column '{column}' contains only missing values."
            )

    return errors


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


# =========================================================
# PROCESS DATA
# =========================================================

@app.route("/process", methods=["POST"])
def process_data():

    # -----------------------------------------------------
    # GET FILES
    # -----------------------------------------------------

    drivers_file = request.files.get("drivers")
    trips_file = request.files.get("trips")
    activity_file = request.files.get("activity")

    if not drivers_file or not trips_file or not activity_file:

        return render_template(
            "index.html",
            error="Please upload all three CSV files."
        )


    # -----------------------------------------------------
    # SAVE FILES
    # -----------------------------------------------------

    drivers_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(drivers_file.filename)
    )

    trips_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(trips_file.filename)
    )

    activity_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        secure_filename(activity_file.filename)
    )

    try:

        drivers_file.save(drivers_path)
        trips_file.save(trips_path)
        activity_file.save(activity_path)

    except Exception as e:

        return render_template(
            "index.html",
            error=f"Error saving uploaded files: {str(e)}"
        )


    # =====================================================
    # STEP 1 — SAFELY READ FILES
    # =====================================================

    drivers, drivers_read_error = read_csv_safely(
        drivers_path
    )

    trips, trips_read_error = read_csv_safely(
        trips_path
    )

    activity, activity_read_error = read_csv_safely(
        activity_path
    )


    # =====================================================
    # VALIDATION ERRORS
    # =====================================================

    errors = []


    # -----------------------------------------------------
    # FILE-LEVEL ERRORS
    # -----------------------------------------------------

    if drivers_read_error:
        errors.append(
            f"Drivers dataset: {drivers_read_error}"
        )

    if trips_read_error:
        errors.append(
            f"Trips dataset: {trips_read_error}"
        )

    if activity_read_error:
        errors.append(
            f"Driver activity dataset: {activity_read_error}"
        )


    # =====================================================
    # BASIC DATAFRAME VALIDATION
    # =====================================================

    errors.extend(
        validate_basic_dataframe(
            drivers,
            "Drivers"
        )
    )

    errors.extend(
        validate_basic_dataframe(
            trips,
            "Trips"
        )
    )

    errors.extend(
        validate_basic_dataframe(
            activity,
            "Driver Activity"
        )
    )


    # =====================================================
    # REQUIRED COLUMN VALIDATION
    # =====================================================

    # Drivers
    driver_required_columns = [
        "driver_id"
    ]

    errors.extend(
        validate_required_columns(
            drivers,
            driver_required_columns,
            "Drivers"
        )
    )


    # Trips
    trip_required_columns = [
        "trip_id",
        "driver_id",
        "pickup_time",
        "drop_time",
        "distance_km",
        "fare"
    ]

    trip_column_errors = validate_required_columns(
        trips,
        trip_required_columns,
        "Trips"
    )

    errors.extend(trip_column_errors)


    # =====================================================
    # CUSTOM TRIP VALIDATION
    # =====================================================

    # Only perform these checks if the columns actually exist.

    if not trips.empty:

        # -------------------------------------------------
        # Missing values
        # -------------------------------------------------

        for column in trip_required_columns:

            if column in trips.columns:

                missing_count = trips[column].isna().sum()

                if missing_count > 0:

                    errors.append(
                        f"Trips: Column '{column}' contains "
                        f"{missing_count} missing value(s)."
                    )


        # -------------------------------------------------
        # Duplicate trip IDs
        # -------------------------------------------------

        if "trip_id" in trips.columns:

            duplicate_count = trips["trip_id"].duplicated().sum()

            if duplicate_count > 0:

                errors.append(
                    f"Trips: {duplicate_count} duplicate trip ID(s) found."
                )


        # -------------------------------------------------
        # Invalid distance
        # -------------------------------------------------

        if "distance_km" in trips.columns:

            numeric_distance = pd.to_numeric(
                trips["distance_km"],
                errors="coerce"
            )

            invalid_distance = (
                numeric_distance.isna()
                | (numeric_distance <= 0)
            ).sum()

            if invalid_distance > 0:

                errors.append(
                    f"Trips: {invalid_distance} invalid "
                    f"distance value(s) found."
                )


        # -------------------------------------------------
        # Invalid fare
        # -------------------------------------------------

        if "fare" in trips.columns:

            numeric_fare = pd.to_numeric(
                trips["fare"],
                errors="coerce"
            )

            invalid_fare = (
                numeric_fare.isna()
                | (numeric_fare < 0)
            ).sum()

            if invalid_fare > 0:

                errors.append(
                    f"Trips: {invalid_fare} invalid "
                    f"fare value(s) found."
                )


        # -------------------------------------------------
        # Timestamp validation
        # -------------------------------------------------

        pickup_times = None
        drop_times = None

        if "pickup_time" in trips.columns:

            pickup_times = pd.to_datetime(
                trips["pickup_time"],
                errors="coerce"
            )

            invalid_pickup = pickup_times.isna().sum()

            if invalid_pickup > 0:

                errors.append(
                    f"Trips: {invalid_pickup} invalid "
                    f"pickup timestamp(s) found."
                )


        if "drop_time" in trips.columns:

            drop_times = pd.to_datetime(
                trips["drop_time"],
                errors="coerce"
            )

            invalid_drop = drop_times.isna().sum()

            if invalid_drop > 0:

                errors.append(
                    f"Trips: {invalid_drop} invalid "
                    f"drop timestamp(s) found."
                )


        # -------------------------------------------------
        # Drop before pickup
        # -------------------------------------------------

        if pickup_times is not None and drop_times is not None:

            valid_times = (
                pickup_times.notna()
                & drop_times.notna()
            )

            invalid_order = (
                valid_times
                & (drop_times < pickup_times)
            ).sum()

            if invalid_order > 0:

                errors.append(
                    f"Trips: {invalid_order} trip(s) have "
                    f"drop time before pickup time."
                )


    # =====================================================
    # RUN EXISTING VALIDATOR
    # =====================================================

    # Only call the existing validator when the basic files
    # are structurally usable.
    #
    # This prevents the old validation service from crashing
    # on things like missing trip_id.

    structural_trip_error = (
        trips.empty
        or len(trip_column_errors) > 0
    )

    if not structural_trip_error:

        try:

            validator = DataValidator()

            existing_errors = validator.validate_all(
                drivers_path,
                trips_path,
                activity_path
            )

            if existing_errors:

                errors.extend(existing_errors)

        except Exception as e:

            errors.append(
                f"Validation service warning: {str(e)}"
            )


    # =====================================================
    # LOAD DATA
    # =====================================================

    loader = DataLoader()

    # Defaults
    loaded_drivers = pd.DataFrame()
    loaded_trips = pd.DataFrame()
    zones = set()


    # -----------------------------------------------------
    # LOAD DRIVERS
    # -----------------------------------------------------

    if not drivers.empty:

        try:

            loaded_drivers = loader.load_drivers(
                drivers_path
            )

        except Exception as e:

            errors.append(
                f"Drivers dataset could not be loaded: {str(e)}"
            )


    # -----------------------------------------------------
    # LOAD TRIPS
    # -----------------------------------------------------

    # IMPORTANT:
    # Never call load_trips if the file is empty or
    # required columns are missing.

    if not trips.empty and not trip_column_errors:

        try:

            loaded_trips = loader.load_trips(
                trips_path
            )

        except Exception as e:

            errors.append(
                f"Trips dataset could not be loaded: {str(e)}"
            )

            loaded_trips = pd.DataFrame()


    # -----------------------------------------------------
    # LOAD ZONES
    # -----------------------------------------------------

    if not loaded_trips.empty:

        try:

            zones = loader.load_zones(
                loaded_trips
            )

        except Exception as e:

            errors.append(
                f"Zone information could not be loaded: {str(e)}"
            )

            zones = set()


    # =====================================================
    # ANOMALY DETECTION
    # =====================================================

    anomalies = []


    if not loaded_trips.empty:

        try:

            detector = AnomalyDetector(
                loaded_trips,
                loaded_drivers
            )

            anomalies = detector.detect()

        except Exception as e:

            errors.append(
                f"Anomaly detection warning: {str(e)}"
            )

            anomalies = []


    # =====================================================
    # OPERATIONAL INSIGHTS
    # =====================================================

    insights = []


    if loaded_trips.empty:

        insights = [
            "No trip data available."
        ]

    else:

        try:

            engine = InsightsEngine(
                loaded_trips,
                anomalies
            )

            insights = engine.generate()

        except Exception as e:

            errors.append(
                f"Insights generation warning: {str(e)}"
            )

            insights = [
                "Operational insights could not be generated."
            ]


    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    summary = {

        "drivers": len(loaded_drivers),

        "trips": len(loaded_trips),

        "zones": len(zones),

        "validation_errors": len(errors),

        "anomalies": len(anomalies)

    }


    # =====================================================
    # DASHBOARD
    # =====================================================

    return render_template(

        "dashboard.html",

        summary=summary,

        errors=errors,

        anomalies=anomalies,

        insights=insights

    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)
