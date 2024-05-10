
def make_query_dict(data_dict, prefix :str =""):
    """return query format dictionary from given data dictionary and prefix

    Args:
        data_dict (_type_): dictionary with query data
        prefix (str, optional): prefix. Defaults to "".
        
    Example) make_query_dict({'a': 1, 'b':2}, 'data__example')
    => return {'data__example__a' : 1, 'data__example__b': 2}
    """
    if prefix == "":
        return data_dict
    else:
        return {f'{prefix}__{k}' : v for k, v in data_dict.items()}
    
def tuple_to_list(data):
    if isinstance(data, dict):
        return {k: tuple_to_list(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [tuple_to_list(item) for item in data]
    elif isinstance(data, tuple):
        return [tuple_to_list(item) for item in data]
    else:
        return data