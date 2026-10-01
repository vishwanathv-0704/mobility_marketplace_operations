from services.data_loader import DataLoader
from services.advanced_analyzer import AdvancedAnalyzer


# Load existing data
loader = DataLoader()

#data = loader.load_all()
drivers=loader.load_drivers("data/drivers.csv")
trips=loader.load_trips("data/trips.csv")
zones=loader.load_zones(trips)

data={
"drivers":drivers,
"trips":trips,
"zones":zones
}


trips = data["trips"]
drivers = data["drivers"]
zones = data["zones"]

analyzer = AdvancedAnalyzer(
    trips,
    drivers
)


# ---------------------------------------------------------
# TOP-K
# ---------------------------------------------------------

print("\n" + "=" * 50)
print("TOP-K DRIVERS")
print("=" * 50)

for driver, count in analyzer.top_drivers_by_completed(5):
    print(driver, "->", count, "completed trips")


print("\nTOP-K ZONES")

for zone, count in analyzer.top_zones_by_demand(5):
    print(zone, "->", count, "requests")


# ---------------------------------------------------------
# IDLE TIME
# ---------------------------------------------------------

print("\n" + "=" * 50)
print("IDLE TIME ANALYSIS")
print("=" * 50)

idle_results = analyzer.idle_time_analysis(30)

print("Idle gaps found:", len(idle_results))

for result in idle_results[:5]:
    print(result)


# ---------------------------------------------------------
# PEAK DEMAND
# ---------------------------------------------------------

print("\n" + "=" * 50)
print("PEAK DEMAND")
print("=" * 50)

for slot, count in analyzer.peak_demand().items():
    print(slot, "->", count)


# ---------------------------------------------------------
# DRIVER UTILIZATION
# ---------------------------------------------------------

print("\n" + "=" * 50)
print("DRIVER UTILIZATION")
print("=" * 50)

utilization = analyzer.driver_utilization()

print("Drivers analyzed:", len(utilization))

for driver in utilization[:5]:
    print(driver)


# ---------------------------------------------------------
# CANCELLATION INTELLIGENCE
# ---------------------------------------------------------

print("\n" + "=" * 50)
print("CANCELLATION INTELLIGENCE")
print("=" * 50)

cancellation = analyzer.cancellation_analysis()

print(
    "Total cancellations:",
    cancellation["total_cancellations"]
)

print("\nBy reason:")

for reason, count in cancellation["by_reason"].items():
    print(reason, "->", count)

print("\nBy zone:")

for zone, count in sorted(
    cancellation["by_zone"].items(),
    key=lambda x: x[1],
    reverse=True
)[:5]:
    print(zone, "->", count)


print("\nDAY 3 ANALYTICS TEST COMPLETE")
