import ast


def extract_dicts_from_string(data_string: str) -> list[dict]:
    """
    Create a list of dictionaries from a given string.
    """
    dicts = []
    brace_level = 0
    current_dict = ""

    for char in data_string:
        if char == "{":
            if brace_level == 0:
                current_dict = ""
            brace_level += 1
        if brace_level > 0:
            current_dict += char
        if char == "}":
            brace_level -= 1
            if brace_level == 0:
                try:
                    parsed = ast.literal_eval(current_dict)
                    if isinstance(parsed, dict):
                        dicts.append(parsed)
                except Exception as e:
                    raise Exception(f"Failed to parse: {current_dict}\nError: {e}")

    return dicts
