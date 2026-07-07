BEGIN TRANSACTION;

ALTER TABLE Gwenseek 
ADD COLUMN IF NOT EXISTS created_at 
TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));

ALTER TABLE Users
ADD COLUMN IF NOT EXISTS modified_at 
TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));

UPDATE Gwenseek
SET created_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
WHERE created_at IS NULL;

UPDATE Users
SET modified_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
WHERE modified_at IS NULL;

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