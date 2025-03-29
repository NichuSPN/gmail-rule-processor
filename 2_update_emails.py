from utils.rules_and_actions import process_rule, process_action
from entities.db.googledb import GoogleDB
from entities.google.gmail import GmailService
import json

rule_location = "config/rule.json"


def get_rule_and_action():
    with open(rule_location, "r") as file:
        file_content = json.load(file)

    return file_content["rule"], file_content["action"]


def get_message_ids_by_rule(rule):
    condition = process_rule(rule)
    if condition:
        condition = "where " + condition
    else:
        condition = ""
    db = GoogleDB()
    message_ids = db.get_message_ids_by_condition(
        condition,
        onSuccess=lambda result: [record[0] for record in result],
        onError=lambda error: print("Error getting message ids", error),
    )
    if len(message_ids) == 0:
        print("No message ids found")
        return
    return message_ids


def message_id_chunks(message_ids, chunk_size=100):
    n = len(message_ids)
    for i in range(0, n, chunk_size):
        yield message_ids[i : min(i + chunk_size, n)]


def make_the_action(message_ids, action):
    add_labels, remove_labels = process_action(action)
    gmail = GmailService()
    print("Making the action...")
    for chunk in message_id_chunks(message_ids, 100):
        gmail.bulk_modify_message_labels(chunk, add_labels, remove_labels)
    print("Action made... Logging out...")
    gmail.logout()


def main():
    rule, action = get_rule_and_action()
    print("Rule and action fetched...")
    message_ids = get_message_ids_by_rule(rule)
    if message_ids:
        print("Message ids fetched...")
        make_the_action(message_ids, action)


if __name__ == "__main__":
    print("Starting script...")
    main()
    print("Script completed...")
