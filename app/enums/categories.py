from enum import Enum

class EventCategory(str, Enum):
    CONCERT = "concert"
    MOVIE = "movie"
    SPORTS = "sports"
    CONFERENCE = "conference"
    THEATRE = "theatre"
    OTHER = "other"
