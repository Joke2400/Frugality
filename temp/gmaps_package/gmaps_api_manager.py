import json
import requests
import time
from datetime import datetime
from webscraper.data.filepaths import FilePaths, GMapsAPIKeyPath
from webscraper.utils.helper_functions import fetch_local_data2, check_duplicates_and_append
from webscraper.utils.descriptors import StringAttribute, LowercaseStringAttribute, NumberAttribute, ListAttribute
from webscraper.utils.custom_data_classes import LocationAttribute, LocationTuple, StoreItem
from webscraper.data.urls import GMapsAPIUrls as GMAPS_URLS

class GMapsAPIManager:
    address                 =   StringAttribute()
    radius                  =   NumberAttribute()
    language                =   LowercaseStringAttribute()  
    keypath                 =   StringAttribute()
    key                     =   StringAttribute()
    stores                  =   ListAttribute()
    location                =   LocationAttribute()
    valid_stores            =   ListAttribute()
    missing_locations       =   ListAttribute()
    valid_store_chains      =   ListAttribute()

    def __init__(self, address=None, radius=5, language="fi", keypath=None, location=None):
        self.address = address
        self.radius = radius
        self.language = language
        self.keypath = keypath
        self.key = self.get_key()
        self.stores = self.get_stores()
        self.location = location
        self.valid_stores = []
        self.missing_locations = []
        self.valid_store_chains = [
            "s-market",
            "sale",
            "prisma",
            "alepa",
            "abc",
        ]
        
    def perform_api_request(self, url, payload, callback=None):
        #payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
        response = requests.get(url, params=payload)
        if response.status_code == 403:
            print("Response received was 403")
            time.sleep(100)
            response = requests.get(url, params=payload)

        if callback is not None:
            callback(response)
        return response

    def get_key(self):
        try:         
            with open(self.keypath,'r') as file:
                key = str(file.readline())
                return key
        except:
            try:
                with open(GMapsAPIKeyPath.keypath, 'r') as file:
                    key = str(file.readline())
                    return key
            except:
                raise Exception("Error occurred while attempting to read api-key")

    def get_stores(self):
        stores = []
        stores_json = fetch_local_data2(FilePaths.stores_path, "stores")
        if len(stores_json["stores"]) > 0:
            for store_dict in stores_json["stores"]:
                for key, value in store_dict.items():
                    if isinstance(value, str):
                        store_dict[key] = value.lower()
                stores = check_duplicates_and_append(stores, store_dict)
        return stores

    def get_location(self, payload=None):
        if payload is None:
            payload = {
                "address"   : self.address,
                "key"       : self.key,
                "language"  : self.language
                }
        response = self.perform_api_request(GMAPS_URLS.GEOCODE, payload)
        response = json.loads(response.content)

        formatted_address   = response["results"][0]["formatted_address"]
        lat                 = response["results"][0]["geometry"]["location"]["lat"]
        lon                 = response["results"][0]["geometry"]["location"]["lng"]
        place_id            = response["results"][0]["place_id"]
        plus_code           = response["results"][0]["plus_code"]["global_code"]
        
        location = LocationTuple(formatted_address, lat, lon, place_id, plus_code)
        return location

    def find_place(self, payload):
        response = self.perform_api_request(GMAPS_URLS.PLACE_FROM_TEXT, payload)
        response = json.loads(response.content)
        
        formatted_address   = response["candidates"][0]["formatted_address"]
        lat                 = response["candidates"][0]["geometry"]["location"]["lat"]
        lon                 = response["candidates"][0]["geometry"]["location"]["lng"]
        place_id            = response["candidates"][0]["place_id"]
        plus_code           = response["candidates"][0]["plus_code"]["global_code"]
        
        location = LocationTuple(formatted_address, lat, lon, place_id, plus_code)
        return location

    def nearby_search(self, keyword=None, payload=None):
        if payload is None:
            payload = {
                "location" : f"{self.location.lat},{self.location.lon}",
                "keyword" : keyword if keyword is not None else "",
                "language" : "fi",
                "type" : "store",
                "radius" : f"{self.radius*1000}",
                "key" : self.key
            }
        response = self.perform_api_request(GMAPS_URLS.NEARBY_SEARCH, payload)
        response = json.loads(response.content)
        found_stores = []
        for store in response["results"]:
            for valid_name in self.valid_store_chains:
                if valid_name in store["name"].lower():
                    vicinity = store["vicinity"]
                    lat = store["geometry"]["location"]["lat"]
                    lon = store["geometry"]["location"]["lng"]
                    place_id = store["place_id"]
                    plus_code = store["plus_code"]["global_code"]
                    
                    store_location = LocationTuple(vicinity, lat, lon, place_id, plus_code)
                    now = datetime.now()        
                    found_store = StoreItem(
                        name=store["name"],
                        chain=valid_name,
                        location=store_location,
                        date_added= now.strftime("%d/%m/%Y %H:%M:%S"),
                        last_updated= now.strftime("%d/%m/%Y %H:%M:%S")
                    )
                    found_stores.append(found_store)

        return self.filter_nearby_search(found_stores)

    def filter_nearby_search(self, found_stores):
        for item in found_stores:
            prevent_append = False
            if len(item.name.split(" ")) == 1:
                prevent_append = True

            if not prevent_append:
                for store in self.stores:
                    if item.name == store.name:
                        prevent_append = True
                        break
            if not prevent_append:
                self.stores.append(item)
                distance = item.location.get_distance((self.location.lat, self.location.lon))
                if distance <= self.radius:
                    self.valid_stores.append((item, distance))

        self.save_store_data()
        return self.valid_stores
                    
    def compare_local_items(self):
        self.valid_stores = []
        self.missing_locations = []
        
        for item in self.stores:
            if item.location is not None:
                distance = item.location.get_distance((self.location.lat, self.location.lon))
               
                #print(f"Address Coords: {address_coords} | Store Coords: {store_coords}")
                #print(f"Measured distance: {distance:.4f}km | Valid Radius: {self.radius}km")
                #print("\n")

                if distance <= self.radius:
                    self.valid_stores.append((item, distance))
            else:
                self.missing_locations.append(item)
        
        if len(self.missing_locations) > 0:
            print("Found local store items without a known location. ")

    def get_store_location_data(self):
        for missing_store in self.missing_locations:
            payload = {
                "input"         : missing_store.name, 
                "inputtype"     : "textquery",
                "locationbias"  : f"circle:{self.radius*1000}@{self.location.lat},{self.location.lon}",
                "fields"        : "formatted_address,name,geometry,place_id,plus_code",
                "key"           : self.key
                }
            location = self.find_place(payload)
            for store in self.stores:
                if store.name == missing_store.name:
                    store.location = location
                    break

    def save_store_data(self):
        stores_dict = {"stores" : []}
        for item in self.stores:
            stores_dict["stores"].append({
                "NAME" : item.name.title(),
                "CHAIN" : item.chain,
                "OPEN_TIMES" : item.open_times.title() if isinstance(item.open_times, str) else item.open_times,
                "ADDRESS" : item.address.title() if isinstance(item.address, str) else item.address,
                "LOCATION" : item.location,
                "DATE_ADDED" : item.date_added,
                "LAST_UPDATED" : item.last_updated,
                "HREF" : item.href,
                "SELECT" : item.select,
                })
                
        with open(FilePaths.stores_path, "w") as f:                                     
            json.dump(stores_dict, f, indent=2)
    
    def fetch_eligible_stores(self):
        if self.location is None:
            self.location = self.get_location()
        if self.valid_stores is None:
            self.compare_local_items()
        elif isinstance(self.valid_stores, list):
            if len(self.valid_stores) == 0:
                self.compare_local_items()

        if len(self.missing_locations) > 0:
            self.get_store_location_data()
            self.compare_local_items()
            self.save_store_data()
        return self.valid_stores