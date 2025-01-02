def validate_location_details(location_details: dict) -> bool:
    required_keys = {"city", "country", "region"}
    if not isinstance(location_details, dict):
        return False

    if not required_keys.issubset(location_details.keys()):
        return False

    values = [location_details[key] for key in required_keys]

    not_validate_values = [value for value in values if value in ["null"] or not isinstance(value, str)]

    return False if not_validate_values else True