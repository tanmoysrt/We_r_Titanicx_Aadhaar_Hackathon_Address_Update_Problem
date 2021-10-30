from django import template
import json
register = template.Library()

@register.filter
def text_to_json(value):
    # print(value)
    try:
        return json.loads(value)
    except Exception as e:
        print(e)
        return {}

@register.filter
def get_value_json(value, key):
    # print(value["ip"])
    try:
        return value[key]
    except:
        return "N/A"
