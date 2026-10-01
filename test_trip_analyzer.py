from services.data_loader import DataLoader
from services.trip_analyzer import TripAnalyzer


loader = DataLoader()

trips = loader.load_trips(
    "data/trips.csv"
)

analyzer = TripAnalyzer(trips)

summary = analyzer.get_summary()


print("\nTRIP ANALYTICS")
print("------------------------------")

print("Total Trips:",
      summary["total_trips"])

print("Completed Trips:",
      summary["completed_trips"])

print("Cancelled Trips:",
      summary["cancelled_trips"])

print("Completion Rate:",
      summary["completion_rate"], "%")

print("Cancellation Rate:",
      summary["cancellation_rate"], "%")

print("Total Revenue:",
      summary["total_revenue"])

print("Average Fare:",
      summary["average_fare"])

print("Average Distance:",
      summary["average_distance"])

print("\nTrips By Status:")
print(summary["trips_by_status"])

print("\nCancellation Reasons:")
print(summary["cancellation_reasons"])


# Test dictionary search

first_trip_id = trips[0].trip_id

trip = analyzer.get_trip(first_trip_id)

print("\nSEARCH TEST")
print("------------------------------")

if trip:
    print("Found Trip:", trip.trip_id)
else:
    print("Trip not found")
