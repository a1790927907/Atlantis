import json


# 将所有的"Object of type datetime is not JSON serializable" 直接转换掉
def format_dict_to_be_json_serializable(source: dict, return_new: bool = True):
    def extract_list_data(source_list: list):
        for index, v in enumerate(source_list):
            if isinstance(v, dict):
                format_dict_to_be_json_serializable(v)
            elif isinstance(v, list):
                extract_list_data(v)
            else:
                try:
                    json.dumps(v)
                except TypeError as _e1:
                    source_list[index] = str(v)

    for key, value in source.items():
        if isinstance(value, list):
            extract_list_data(value)
        elif isinstance(value, dict):
            format_dict_to_be_json_serializable(value)
        else:
            if value is None:
                continue
            try:
                json.dumps(value)
            except TypeError as _e:
                source[key] = str(value)
    if return_new:
        return source.copy()
