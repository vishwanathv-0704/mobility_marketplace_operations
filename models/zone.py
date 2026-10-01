class Zone:

    def __init__(self, city, zone_name):
        self.city = city
        self.zone_name = zone_name

    def get_identifier(self):
        return f"{self.city}-{self.zone_name}"

    def get_profile(self):
        return {
            "city": self.city,
            "zone_name": self.zone_name,
            "identifier": self.get_identifier()
        }
