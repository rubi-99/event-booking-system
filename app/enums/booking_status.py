from enum import Enum 

class BookingStatus(str,Enum):
    CONFIRMED= "CONFIRMED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

