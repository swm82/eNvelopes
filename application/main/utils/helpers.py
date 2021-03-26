# Helper methods - move to seperate pkg
def decimal_to_int(value):
    string_value = str(value)
    if '.' not in string_value:
        return int(string_value) * 100
    parts = string_value.split('.')
    intvalue = int(''.join(parts))
    return intvalue

def format_currency(value):
    return "$" + str(float(value)/100)