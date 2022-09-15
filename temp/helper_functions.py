import json
from math import radians, cos, sin, asin, sqrt
from .fpaths import FilePaths

def prepare_search_string(base_url, string):
    return (base_url + string.lower())

def unpack_nested_strings(iterable):
    '''
    Recursive function which takes every element inside a tuple, checks if it's a string, then appends it to a list which is then joined to
    a single string, then returned.
    The reason this is needed is because of how locators are stored in locators.py. These can have tuples containing tuples containing tuples, so recursive
    functions are required to extract a single list of strings. I'm also pretty sure i saw this function append each letter in a string as well which was unintented
    but oh well, it works.
    '''
    string_list = []
    for item in iterable:
        if isinstance(item, tuple) or isinstance(item, list):
            for x in unpack_nested_strings(item):
                string_list.append(x)
        elif type(item) is str:
            string_list.append(item)
        else:
            raise TypeError("Accessed item was not a string or a tuple/list")
    
    return "".join(string_list)

def check_dict_key_value_consistency(dictionary, known_data_pair, unknown_data_pair):
    '''
    check_consistency() is used instead now
    '''
    if known_data_pair[0] == "KEY":
        for key, value in dictionary.items():
            if known_data_pair[1].lower() == key.lower():
                if unknown_data_pair.lower() == value.lower():
                    return True
                else:
                    return False

    elif known_data_pair[0] == "VALUE":
        for key, value in dictionary.items():
            if known_data_pair[1].lower() == value.lower():
                if unknown_data_pair.lower() == key.lower():
                    return True
                else:
                    return False
    else:
        raise Exception("known_data_pair must be provided as a tuple with the first value in the tuple being either 'KEY' or 'VALUE' and the second value being the known data value")

def lower_iterable(iterable):
    if not isinstance(iterable, tuple) and not isinstance(iterable, list):
        raise TypeError("This function is only intended to check iterables containing strings or values that can be converted to strings")
    else:
        try:
            iterable = [str(i).lower() for i in iterable]
        except:
            print("Could not convert the data within the iterable to strings, please ensure that your input is correct.")
    return iterable

def check_consistency(first_data_tuple, second_data_tuple):
    first_bool = False
    second_bool = False
    if not isinstance(first_data_tuple, tuple):
        raise TypeError("This function is only intended to check two tuples containing two pairs of strings")
    try:
        first_data_tuple = [str(i) for i in first_data_tuple]   #Might be a bit performance intensive since this function gets called a lot
        second_data_tuple = [str(i) for i in second_data_tuple]
    except:
        print("Could not convert the data within the tuples to strings, please ensure that your input is correct.")
        
    if first_data_tuple[0].lower() == second_data_tuple[0].lower():
        first_bool = True
    if first_data_tuple[1].lower() == second_data_tuple[1].lower():
        second_bool = True

    if first_bool and second_bool:
        return {"RESULT" : True, "SPECIFY" : "BOTH"}
    elif first_bool and not second_bool:
        return {"RESULT" : False, "SPECIFY" : "FIRST"}
    elif not first_bool and second_bool:
        return {"RESULT" : False, "SPECIFY" : "SECOND"}
    else:
        return {"RESULT" : False, "SPECIFY" : "NEITHER"}

def fetch_local_data(path, key):
    try:         
        with open(path,'r') as file:
            try:
                for store in json.load(file)[key]:  #Issue when using this as a generator, json.load loads the entire file
                    yield store
            except:
                print("Could not retrieve store data from json file.")
                yield None
    except:
        print("Could not open json file. Either the file is missing or the wrong file path was used.")
        return {f"{key}" : []}

def fetch_local_data2(path, key):
    try:         
        with open(path,'r') as file:
            stores_dict = {f"{key}" : []}
            stores_json = json.load(file)[key]
            for item in stores_json:
                stores_dict["stores"].append(item)
            return stores_dict
    except:
        print("Could not open json file. Either the file is missing or the wrong file path was used.")
        stores_dict = {f"{key}" : []}
        with open(FilePaths.stores_path, "w") as f:  #Ensuring a store.json always exists, even though it may be empty                              
            json.dump(stores_dict, f, indent=2, sort_keys=True)

        return {f"{key}" : []}

def haversine(coords_1, coords_2):
    """
    Courtesy of some guy on stack overflow, so not my invention (I'm bad at math)

    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    lat1, lon1 = coords_1
    lat2, lon2 = coords_2

    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def check_duplicates_and_append(lst, provided_item):
    from .custom_data_classes import LocationTuple, StoreItem
    prevent_append = False

    for item in lst:
        if isinstance(item, StoreItem) and isinstance(provided_item["NAME"], str):
            if item.name == provided_item["NAME"].lower():
                prevent_append == True
                break
                
        elif isinstance(item["NAME"], str) and isinstance(provided_item["NAME"], str):
            if item["NAME"].lower() == provided_item["NAME"].lower():
                prevent_append = True
                break
        else:
            prevent_append = True
            break       
    
    if not prevent_append:
        store_location = None
        if provided_item["LOCATION"] is not None and isinstance(provided_item["LOCATION"], (list, tuple)):
            if len(provided_item) >= 5:
                store_location = LocationTuple(
                    provided_item["LOCATION"][0],
                    provided_item["LOCATION"][1],
                    provided_item["LOCATION"][2],
                    provided_item["LOCATION"][3],
                    provided_item["LOCATION"][4]      
                )
        store_item = StoreItem(
            name=provided_item["NAME"],
            chain=provided_item["CHAIN"],
            open_times=provided_item["OPEN_TIMES"],
            address=provided_item["ADDRESS"],
            location=store_location,
            date_added=provided_item["DATE_ADDED"],
            last_updated=provided_item["LAST_UPDATED"],
            href=provided_item["HREF"],
            select=provided_item["SELECT"]
        )
        lst.append(store_item)
                
    return lst