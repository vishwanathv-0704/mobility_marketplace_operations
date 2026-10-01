from services.data_loader import DataLoader
from services.zone_analyzer import ZoneAnalyzer


loader = DataLoader()

trips = loader.load_trips(
    "data/trips.csv"
)

analyzer = ZoneAnalyzer(trips)


print("\nZONE ANALYTICS")
print("------------------------------")


zones = analyzer.all_zones()

print("Total Zones:", len(zones))


# Test first zone

zone = zones[0]

result = analyzer.analyze_zone(zone)


print("\nSelected Zone:", zone)
print("------------------------------")

for key, value in result.items():

    print(
        f"{key}: {value}"
    )


# Test another zone if available

if len(zones) > 1:

    zone2 = zones[1]

    print("\nAnother Zone:", zone2)
    print("------------------------------")

    result2 = analyzer.analyze_zone(zone2)

    for key, value in result2.items():

        print(
            f"{key}: {value}"
        )


# Test invalid zone

print("\nINVALID ZONE TEST")
print("------------------------------")

result3 = analyzer.analyze_zone(
    "Unknown Zone"
)

print("Result:", result3)
