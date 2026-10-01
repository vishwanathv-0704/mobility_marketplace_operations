class RankingUtils:

    @staticmethod
    def rank_by_value(data, descending=True):
        """
        Sort a dictionary by its values.

        Example:
        {"D101": 20, "D102": 35, "D103": 15}

        returns:
        [("D102", 35), ("D101", 20), ("D103", 15)]
        """

        return sorted(
            data.items(),
            key=lambda item: item[1],
            reverse=descending
        )

    @staticmethod
    def top_n(data, n=5):

        ranked = RankingUtils.rank_by_value(data)

        return ranked[:n]

    @staticmethod
    def bottom_n(data, n=5):

        ranked = RankingUtils.rank_by_value(
            data,
            descending=False
        )

        return ranked[:n]
