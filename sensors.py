import os


def get_temperature():
    """Read the fridge temperature from a real sensor.

    Replace the placeholder implementation below with your actual sensor code.
    An optional environment override is also available for testing.
    """
    override = os.getenv("FRIDGE_TEMPERATURE")
    if override is not None:
        try:
            return round(float(override), 2)
        except ValueError:
            pass

    # TODO: Replace this return value with actual temperature sensor output.
    return None


def get_weight(item):
    """Read the weight of an inventory item from a scale sensor.

    Replace the body with your sensor integration logic.
    """
    return None
