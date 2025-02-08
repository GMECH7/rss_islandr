def risk_calc(weight_values: list) -> float:
    """
    TODO: I should know that happens if for example one value is passed when there are three risk factors contributing.
    _summary_

    Parameters
    ----------
    weight_values : list
        _description_

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

    return risk_value
