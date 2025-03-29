create schema gmail authorization username;

create table gmail.messages (
    message_id text,
    thread_id text,
    from_address text,
    to_address text,
    subject text,
    body text,
    received_at timestamptz,
    PRIMARY KEY (message_id)
);

create table gmail.labels (
    label text,
    PRIMARY KEY (label)
);

-- https://developers.google.com/workspace/gmail/api/guides/labels#types_of_labels
insert into gmail.labels (label) 
values ('INBOX'),
    ('SPAM'),
    ('TRASH'),
    ('UNREAD'),
    ('STARRED'),
    ('IMPORTANT'),
    ('CATEGORY_PERSONAL'),
    ('CATEGORY_SOCIAL'),
    ('CATEGORY_PROMOTIONS'),
    ('CATEGORY_UPDATES'),
    ('CATEGORY_FORUMS'),
    ('SENT'),
    ('DRAFT');

create table gmail.message_labels (
    message_id text,
    label text,
    PRIMARY KEY (message_id, label)
);

alter table gmail.message_labels
add constraint message_labels_fk_message_id 
foreign key (message_id) references gmail.messages(message_id);

alter table gmail.message_labels
add constraint message_labels_fk_label 
foreign key (label) references gmail.labels(label);
