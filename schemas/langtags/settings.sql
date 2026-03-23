CREATE TABLE settings (
    setting_id     INTEGER PRIMARY KEY,
    parameter_name TEXT NOT NULL UNIQUE,
    language_id    INTEGER
);

INSERT INTO settings (parameter_name, language_id) VALUES ("current_language", 0);
INSERT INTO settings (parameter_name, language_id) VALUES ("default_language", 2);
INSERT INTO settings (parameter_name, language_id) VALUES ("system_language", 0);
