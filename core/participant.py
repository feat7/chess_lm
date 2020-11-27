class Participant:

    def __init__(self, name: str, idx: int, current_elo_rating: float = 1000.0, score: float = 0.0):
        """Participant of the tournament

        Args:
            current_elo_rating (int, optional): [description]. Defaults to 1000.
            score (float, optional): [description]. Defaults to 0.0.
        """

        self._current_elo_rating = current_elo_rating
        self._current_competitor = None

        self.name = name
        self.idx = idx
        self.score = score
        self.games_played = 0

    @property
    def current_elo_rating(self):
        return self._current_elo_rating

    @current_elo_rating.setter
    def current_elo_rating(self, elo_rating: float):
        self._current_elo_rating = elo_rating

    @property
    def current_competitor(self):
        """Get current competitor

        Returns:
            Participant|None: index of the current competitor
        """
        # TODO: get name of the competor along with the index
        return self._current_competitor

    @current_competitor.setter
    def current_competitor(self, competitor):
        """Set current competitor

        Args:
            competitor (Participant): Patricipant object to set current competitor
        """
        # Throw error if competitor is not a participant
        assert type(competitor) == Participant

        self._current_competitor = competitor
