from core.config_parser import risk_limits_color


def risk_calc(weight_values: list, roundoff=3) -> float:
    """
    _summary_

    Parameters
    ----------
    weight_values : list
        _description_
    roundoff : int, optional
        _description_, by default 3

    Returns
    -------
    float
        _description_
    """
    if len(weight_values) == 0:
        return 0.0

    risk_value = 1.0
    for val in weight_values:
        risk_value *= val

    return round(risk_value, roundoff)


def risk_color_assignment(value: float) -> str:
    """ """
    for color in risk_limits_color:
        limit_1 = risk_limits_color[color][0]
        limit_2 = risk_limits_color[color][1]
        if limit_1 <= value <= limit_2:
            break

    return color
