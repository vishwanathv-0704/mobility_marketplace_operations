from services.ranking_utils import RankingUtils


driver_trips = {
    "D101": 22,
    "D102": 45,
    "D103": 18,
    "D104": 67,
    "D105": 31
}


print("\nSORTING / RANKING")
print("------------------------------")

print("All drivers ranked:")

for driver, trips in RankingUtils.rank_by_value(driver_trips):
    print(driver, "->", trips)


print("\nTOP 3")

for driver, trips in RankingUtils.top_n(
    driver_trips, 3
):
    print(driver, "->", trips)


print("\nBOTTOM 2")

for driver, trips in RankingUtils.bottom_n(
    driver_trips, 2
):
    print(driver, "->", trips)
