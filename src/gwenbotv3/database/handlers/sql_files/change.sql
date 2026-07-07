BEGIN TRANSACTION;

ALTER TABLE Gwenseek
ADD created_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));

ALTER TABLE Users
ADD modified_at TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));

CREATE TRIGGER IF NOT EXISTS trg_users_modified_at
AFTER UPDATE OF user_name, is_anonymised ON Users
FOR EACH ROW
WHEN NEW.user_name IS NOT OLD.user_name
   OR NEW.is_anonymised IS NOT OLD.is_anonymised
BEGIN
    UPDATE Users
    SET modified_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    WHERE user_id = OLD.user_id;
END;

COMMIT;