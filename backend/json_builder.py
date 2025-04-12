class json:
    def __init__(self, status="error"):
        self.status = status
        self.data = []

    def set_data(self, data):
        self.data = data

    def set_status(self, status):
        self.status = status

    def build(self):
        response = {
            "status": self.status,
            "data": self.data
        }
        return self.dict_to_json(response)

    def dict_to_json(self, dictionary):
        json_string = "{"
        items = []
        for key, value in dictionary.items():
            value_str = self.value_to_json(value)
            items.append(f'"{key}": {value_str}')
        json_string += ", ".join(items)
        json_string += "}"
        return json_string

    def value_to_json(self, value):
        if isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, dict):
            return self.dict_to_json(value)
        elif isinstance(value, list):
            return self.list_to_json(value)
        elif isinstance(value, bool):
            return "true" if value else "false"
        else:
            return str(value)

    def list_to_json(self, value_list):
        return f"[{', '.join(self.value_to_json(v) for v in value_list)}]"



