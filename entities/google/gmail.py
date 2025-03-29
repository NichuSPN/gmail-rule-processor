import os
from dotenv import load_dotenv
from .google import GoogleService

load_dotenv()


class GmailService(GoogleService):
    def __init__(self, scopes=None, cred_path=None, token_path=None):
        default_scopes = [
            os.getenv(
                "GMAIL_READ_SCOPE", "https://www.googleapis.com/auth/gmail.readonly"
            ),
            os.getenv(
                "GMAIL_MODIFY_SCOPE", "https://www.googleapis.com/auth/gmail.modify"
            ),
        ]
        super().__init__("gmail", "v1", scopes or default_scopes, cred_path, token_path)
        self.page_size = int(os.getenv("GMAIL_PAGE_SIZE", "5"))

    def messages_list(self, pageToken=None, remainingMessages=1000, labels=["INBOX"]):
        if self.service is None:
            self.authenticate()

        if remainingMessages <= 0:
            return

        results = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                pageToken=pageToken,
                maxResults=min(remainingMessages, self.page_size),
                labelIds=labels,
            )
            .execute()
        )

        messages = results.get("messages", [])
        pageToken = results.get("nextPageToken")

        if len(messages) == 0:
            return

        for message in messages:
            yield (
                self.service.users()
                .messages()
                .get(userId="me", id=message["id"])
                .execute()
            )

        if pageToken:
            yield from self.messages_list(
                pageToken, remainingMessages - len(messages), labels
            )

    def bulk_modify_message_labels(
        self, message_ids, add_labels=None, remove_labels=None
    ):
        if self.service is None:
            self.authenticate()

        add_labels = add_labels or []
        remove_labels = remove_labels or []

        body = {
            "ids": message_ids,
            "addLabelIds": add_labels,
            "removeLabelIds": remove_labels,
        }

        return (
            self.service.users()
            .messages()
            .batchModify(userId="me", body=body)
            .execute()
        )
