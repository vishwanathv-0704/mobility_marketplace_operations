from services.data_loader import DataLoader
from services.driver_analyzer import DriverAnalyzer


loader = DataLoader()

drivers = loader.load_drivers(
    "data/drivers.csv"
)

trips = loader.load_trips(
    "data/trips.csv"
)


analyzer = DriverAnalyzer(
    drivers,
    trips
)


driver_id = drivers[0].driver_id

result = analyzer.analyze_driver(
    driver_id
)


print("\nDRIVER PERFORMANCE")
print("------------------------------")

for key, value in result.items():

    print(
        f"{key}: {value}"
    )
