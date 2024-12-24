def validate_location_details(location_details):
    required_keys = {"city", "country", "region"}
    if not isinstance(location_details, dict):
        return False

    if not required_keys.issubset(location_details.keys()):
        return False

    for key in required_keys:
        value = location_details[key]
        if value not in ["null"] and not isinstance(value, str):
            return False

    return True