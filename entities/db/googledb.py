import os
from dotenv import load_dotenv
from arena.data import Postgres

load_dotenv()


class GoogleDB(Postgres):
    def __init__(self, host=None, port=None, user=None, password=None, dbname=None):
        config = {
            "host": host or os.getenv("POSTGRES_HOST"),
            "port": port or os.getenv("POSTGRES_PORT"),
            "user": user or os.getenv("POSTGRES_USER"),
            "password": password or os.getenv("POSTGRES_PASSWORD"),
            "database": dbname or os.getenv("POSTGRES_DB"),
        }
        super().__init__(config)
        self.gmail_message_fields = {
            "message_id": "text",
            "thread_id": "text",
            "from_address": "text",
            "to_address": "text",
            "subject": "text",
            "body": "text",
            "received_at": "timestamptz",
        }

    def clean_data(self, email_data, required_fields={}):
        clean_data = {}
        # print(email_data)
        for field in required_fields:
            datatype = self.gmail_message_fields[field]
            if field not in email_data:
                clean_data[field] = "null"
            elif datatype == "number":
                clean_data[field] = (
                    f"{email_data[field]}" if email_data[field] is not None else "null"
                )
            elif datatype == "timestamptz":
                clean_data[field] = (
                    f"'{email_data[field]}'::timestamptz"
                    if email_data[field] is not None
                    else "null"
                )
            else:
                if email_data[field] is not None:
                    email_data[field] = email_data[field].replace("'", "''")
                clean_data[field] = (
                    f"'{email_data[field]}'"
                    if email_data[field] is not None
                    else "null"
                )

        return clean_data

    def insert_email(self, email_data, onSuccess=None, onError=None):
        clean_data = self.clean_data(email_data, self.gmail_message_fields)
        # print(clean_data)
        query = """
            insert into gmail.messages ( message_id,
                thread_id,
                from_address,
                to_address,
                subject,
                body,
                received_at)
            values ({{message_id}},
                {{thread_id}},
                {{from_address}},
                {{to_address}},
                {{subject}},
                {{body}},
                {{received_at}})
            on conflict (message_id) do update set
                thread_id = {{thread_id}},
                from_address = {{from_address}},
                to_address = {{to_address}},
                subject = {{subject}},
                body = {{body}},
                received_at = {{received_at}};
        """
        return self.run_query(
            query,
            params=clean_data,
            isUpdate=True,
            onSuccess=onSuccess,
            onError=onError,
        )

    def bulk_insert_labels(
        self, message_id, label_data_list, onSuccess=None, onError=None
    ):
        """
        Insert multiple emails in a single query for better performance.

        Args:
            email_data_list: List of dictionaries containing email data
            onSuccess: Success callback function
            onError: Error callback function

        Returns:
            Result from run_query method
        """
        if not label_data_list:
            return True, []

        # Generate values section for each email
        values_list = []
        for label in label_data_list:
            values_part = f"""(
                '{message_id}', 
                '{label}'
            )"""
            values_list.append(values_part)

        # Combine all values into one query
        values_clause = ",\n".join(values_list)

        query = """
        insert into gmail.message_labels (
            message_id, label
        ) values 
        {{values_clause}}
        on conflict (message_id, label) do nothing;
        """

        return self.run_query(
            query,
            params={"values_clause": values_clause},
            isUpdate=True,
            onSuccess=onSuccess,
            onError=onError,
        )
        