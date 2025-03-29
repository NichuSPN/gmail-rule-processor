from entities.google import GmailService
from utils.gmail import get_required_data
from entities.db import GoogleDB


def onSuccess(_):
    pass


def onErrorEmailInsert(error):
    print("Error inserting email information into our database", error)


def onErrorLabelInsert(error):
    print("Error inserting labels into our database", error)


def main():
    try:
        gmail = GmailService()
        db = GoogleDB()
        print("Fetching emails and inserting into our database...")
        for message in gmail.messages_list(remainingMessages=100000):
            data = get_required_data(message)
            db.insert_email(data, onSuccess=onSuccess, onError=onErrorEmailInsert)
            db.bulk_insert_labels(
                data["message_id"],
                data["labels"],
                onSuccess=onSuccess,
                onError=onErrorLabelInsert,
            )
    except Exception as e:
        print("Error in script...", e)
    finally:
        print("Signing out...")
        gmail.logout()


if __name__ == "__main__":
    print("Starting script...")
    main()
    print("Done! Thanks for your patience...")
