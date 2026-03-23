CREATE TABLE translations (
    translation_id INTEGER PRIMARY KEY,
    tag_id         INTEGER NOT NULL,
    language_id    INTEGER NOT NULL,
    value          TEXT NOT NULL,
    created_at     TEXT,
    updated_at     TEXT,
    deleted_at     TEXT,
    FOREIGN KEY(tag_id) REFERENCES tags(tag_id),
    FOREIGN KEY(language_id) REFERENCES languages(language_id)
);
