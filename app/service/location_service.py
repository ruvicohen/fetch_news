from geopy.geocoders import Nominatim


def get_coordinates(country, city):
    if not city or city.lower() == "null" or not country or country.lower() == "null":
        print(f"Invalid location: city={city}, country={country}")
        return None

    try:
        geolocator = Nominatim(user_agent="geoapi")

        location = f"{city}, {country}"

        result = geolocator.geocode(location)

        if result:
            return result.latitude, result.longitude
        else:
            return None
    except Exception as e:
        print(f"Error getting coordinates for {country}, {city}: {e}")
        return None


# coordinates = get_coordinates("Israel", "Tel Aviv")
# if coordinates:
#     print(f"Coordinates of Tel Aviv, Israel: {coordinates}")
# else:
#     print("Could not find coordinates.")
