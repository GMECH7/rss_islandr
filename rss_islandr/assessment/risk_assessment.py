from core.config_parser import risk_limits_color
from core.logger_config import logger_decorator


@logger_decorator
def risk_calc(weight_values: list[float]) -> float:
    """
    Calculates the risk value based on the provided weight values.

    Parameters
    ----------
    weight_values : list[float]
        List of weight values to be multiplied together.
    Returns
    -------
    float
    """
    risk_value = 1.0
    for val in weight_values:
        risk_value *= val

    return risk_value


@logger_decorator
def risk_color_assignment(value: float) -> str:
    """
    Assigns a color based on the risk value.
    """
    for color in risk_limits_color:
        limit_1 = risk_limits_color[color][0]
        limit_2 = risk_limits_color[color][1]
        if limit_1 <= value <= limit_2:
            break

    return color
