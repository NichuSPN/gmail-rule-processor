import re

type_defs = {
    "text": {
        "allowed_operators": ["is", "is_not", "contains", "not_contains"],
        "pattern": r".+",
    },
    "datetime": {
        "allowed_operators": ["greater_than", "less_than"],
        "pattern": r"^\d+ (days|day|month|months|year|years)$",
    },
}

columns_to_type = {
    "from_address": "text",
    "subject": "text",
    "body": "text",
    "received_at": "datetime",
}

action_locations = ["INBOX", "SPAM", "TRASH"]
action_categories = [
    "CATEGORY_PERSONAL",
    "CATEGORY_SOCIAL",
    "CATEGORY_PROMOTIONS",
    "CATEGORY_UPDATES",
    "CATEGORY_FORUMS",
]


def validate_condition(condition):
    if condition["field"] not in columns_to_type:
        raise ValueError(f"Invalid field: {condition['field']}")
    col_type = columns_to_type[condition["field"]]
    value = condition["value"]
    operator = condition["operator"]
    if operator not in type_defs[col_type]["allowed_operators"]:
        raise ValueError(f"Invalid operator: {operator}")
    if not re.match(type_defs[col_type]["pattern"], value):
        raise ValueError(f"Invalid value: {value}")


def get_sql_condition(condition):
    validate_condition(condition)
    match condition["operator"]:
        case "contains":
            return f"{condition['field']} ilike '%{condition['value']}%'"
        case "not_contains":
            return f" ({condition['field']} not ilike '%{condition['value']}%')"
        case "is":
            return f"{condition['field']} = '{condition['value']}'"
        case "is_not":
            return f"{condition['field']} != '{condition['value']}'"
        case "greater_than":
            return f"{condition['field']} > now() - interval '{condition['value']}'"
        case "less_than":
            return f"{condition['field']} < now() - interval '{condition['value']}'"
        case _:
            raise ValueError(f"Invalid operator: {condition['operator']}")


def process_rule(rule):
    if rule["type"] == "rule":
        predicate = rule["predicate"]
        conditions = []
        # print(rule)
        for curr_rule in rule["rules"]:
            conditions.append(process_rule(curr_rule))
        if not conditions or len(conditions) == 0:
            return None
        if len(conditions) == 1:
            return conditions[0]
        if predicate == "any":
            return (
                "("
                + " or ".join([condition for condition in conditions if condition])
                + ")"
            )
        elif predicate == "all":
            return (
                "("
                + " and ".join([condition for condition in conditions if condition])
                + ")"
            )
        else:
            raise ValueError(f"Invalid predicate: {predicate}")
    elif rule["type"] == "condition":
        return get_sql_condition(rule)


def process_action(action):
    add_labels = []
    remove_labels = []
    if "unread" in action:
        if action["unread"]:
            add_labels.append("UNREAD")
        else:
            remove_labels.append("UNREAD")
    if "starred" in action and action["starred"]:
        add_labels.append("STARRED")
    if "important" in action and action["important"]:
        add_labels.append("IMPORTANT")
    if "location" in action:
        if action["location"] in action_locations:
            add_labels.append(action["location"])
            remove_labels += [
                location
                for location in action_locations
                if location != action["location"]
            ]
        else:
            raise ValueError(f"Invalid location: {action['location']}")
    if "category" in action:
        if action["category"] in action_categories:
            add_labels.append(action["category"])
            remove_labels += [
                category
                for category in action_categories
                if category != action["category"]
            ]
        else:
            raise ValueError(f"Invalid category: {action['category']}")
    return add_labels, remove_labels
