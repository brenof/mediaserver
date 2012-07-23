CREATE TABLE users (
    email       text,
    id          UUID,
    password	text,
    PRIMARY KEY(id),
    UNIQUE(email)
);
