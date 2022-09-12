from typing import NamedTuple
from .helper_functions import haversine
from ..utils.descriptors import DataStringAttribute, LocationAttribute

class LocationTuple(NamedTuple):
    formatted_address : str
    lat : str
    lon : str
    place_id : str = None
    plus_code : str = None

    def get_distance(self, provided_location):
        return haversine(provided_location, (self.lat, self.lon))

class StoreItem:
    name            = DataStringAttribute()
    chain           = DataStringAttribute()
    open_times      = DataStringAttribute()
    address         = DataStringAttribute()
    date_added      = DataStringAttribute()
    last_updated    = DataStringAttribute()
    href            = DataStringAttribute()
    select          = DataStringAttribute()
    location        = LocationAttribute()

    def __init__(self, 
            name : str, 
            chain : str, 
            open_times : str = None, 
            address : str = None,
            location : LocationTuple = None, 
            date_added : str = None, 
            last_updated : str = None, 
            href : str = None, 
            select : str = None):
        self.name = name
        self.chain = chain
        self.open_times = open_times
        self.address = address
        self.location = location
        self.date_added = date_added
        self.last_updated = last_updated
        self.href = href
        self.select = select

    def __repr__(self):
        return f"StoreItem({self.name},{self.open_times},{self.address},{self.location},{self.date_added},{self.last_updated},{self.href},{self.select})"