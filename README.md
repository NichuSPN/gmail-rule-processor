# Gmail Rule Processor

A standalone Python script that integrates with Gmail API to fetch emails, store them in a database, and perform rule-based actions on them.

**Note:** This read me is from the context of running in Mac. Please adjust the steps accoring to the OS you are running it in.

## Overview

This project allows you to:
- Authenticate to Gmail API using OAuth
- Fetch emails from your inbox
- Store emails in a relational database
- Process emails based on customizable rules
- Perform actions like marking emails as read/unread or moving them to different folders

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Google Cloud Platform account

### Installation

1. Clone this repository:
```bash
git clone https://github.com/nichuspn/gmail-rule-processor.git
cd gmail-rule-processor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up OAuth credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create OAuth credentials (Desktop app)
   - Download credentials JSON file and save as `credentials.json` in project root

4. Set up the database:
   - Setup basic postgres in your system
   - Go into db_setup folder `cd db_setup`
   - Give execute access for `createdb.sh` using `chmod +x createdb.sh`
   - Run it using `./createdb.sh`

5. Configure environment variables in `.env` file from `.env.example`:
Mostly you should not have to change things if the setup is same
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=gmaildb
```

## Project Structure

```
├── 1_fetch_emails.py       # Script to fetch emails from Gmail and store in database
├── 2_update_emails.py      # Script to process rules on stored emails
├── README.md               # Project documentation
├── .env.example            # Example environment variables
├── .env                    # Environment variables configuration
├── credentials.json        # OAuth credentials for Gmail API
├── requirements.txt        # Project dependencies
├── config/
│   └── rule.json           # Rule definitions for email processing
├── db_setup/
│   ├── createdb.sh         # Database creation script
│   └── init.sql            # SQL schema initialization script
├── entities/
│   ├── db/
│   │   ├── __init__.py
│   │   └── googledb.py     # Database operations for Gmail data
│   └── google/
│       ├── __init__.py
│       ├── gmail.py        # Gmail API service implementation
│       └── google.py       # Google API authentication
└── utils/
    ├── gmail.py            # Helper functions for Gmail operations
    └── rules_and_actions.py # Rule processing logic
```

### Key Files and Directories

- **Main Scripts**:
  - `1_fetch_emails.py`: Authenticates with Gmail API, fetches emails, and stores them in the database
  - `2_update_emails.py`: Processes rules and applies actions to matching emails

- **Configuration**:
  - `config/rule.json`: Contains the rule definitions for processing emails
  - `.env`: Environment variables for database connections and other settings

- **Database**:
  - `db_setup/`: Contains scripts for setting up the PostgreSQL database
  - `entities/db/googledb.py`: Database operations specific to Gmail data

- **Gmail Integration**:
  - `entities/google/gmail.py`: Implementation of the Gmail service for API interactions
  - `entities/google/google.py`: Handles Google API authentication
  - `utils/gmail.py`: Helper functions for common Gmail operations

- **Rule Processing**:
  - `utils/rules_and_actions.py`: Logic for processing rules and applying actions to emails

## Usage

### Fetching Emails

```bash
python 1_fetch_emails.py
```

This will:
1. Authenticate with Gmail API
2. Fetch emails from your inbox
3. Store them in the database

### Processing Rules

```bash
python 2_update_emails.py
```

This will:
1. Load rules from `config/rule.json`
2. Query emails from the database based on these rules
3. Perform specified actions on matching emails

## Rule Format

Rules are defined in JSON format:

```json
{
  "rule": {
    "predicate": "all", 
    "type": "rule",
    "rules": [
      {
        "type": "condition",
        "field": "from_address",
        "operator": "contains",
        "value": "example.com"
      },
      {
        "type": "condition",
        "field": "subject",
        "operator": "contains",
        "value": "important"
      }
    ]
  },
  "action": {
    "unread": true,
    "starred": true,
    "important": true,
    "location": "INBOX",
    "category": "CATEGORY_PERSONAL"
  }
}
```

### Rule Types

- **Fields**: `from_address`, `subject`, `body`, `received_at`
- **Operators for text fields**: `contains`, `not_contains`, `is`, `is_not`
- **Operators for date fields**: `greater_than`, `less_than`
- **Predicates**: `all` (all conditions must match), `any` (at least one condition must match)

### Actions

- Mark as read/unread: `"unread": true/false`
- Mark as starred: `"starred": true`
- Mark as important: `"important": true`
- Move message: `"location": "INBOX"/"SPAM"/"TRASH"`
- Change category: `"category": "CATEGORY_PERSONAL"/"CATEGORY_SOCIAL"/etc.`

## Database Schema

```sql
CREATE TABLE emails (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  subject TEXT,
  from_address TEXT,
  to_address TEXT,
  body_text TEXT,
  snippet TEXT,
  received_date TIMESTAMP,
  labels JSONB
);
```

## Examples

### Example Rule 1: Mark promotional emails as read

```json
{
  "rule": {
    "predicate": "any",
    "type": "rule",
    "rules": [
      {
        "type": "condition",
        "field": "from_address",
        "operator": "contains",
        "value": "marketing"
      },
      {
        "type": "condition",
        "field": "subject",
        "operator": "contains",
        "value": "newsletter"
      }
    ]
  },
  "action": {
    "unread": false,
    "category": "CATEGORY_PROMOTIONS"
  }
}
```

### Example Rule 2: Move old emails to trash

```json
{
  "rule": {
    "predicate": "all",
    "type": "rule",
    "rules": [
      {
        "type": "condition",
        "field": "received_at",
        "operator": "less_than",
        "value": "6 months"
      },
      {
        "type": "condition",
        "field": "subject",
        "operator": "not_contains",
        "value": "important"
      }
    ]
  },
  "action": {
    "location": "TRASH"
  }
}
```