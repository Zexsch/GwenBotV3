BEGIN TRANSACTION;

DELETE FROM Subs
WHERE user IN (
    SELECT user_id FROM Users
    WHERE modified_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-180 days')
);

DELETE FROM Gwenseek
WHERE user IN (
    SELECT user_id FROM Users
    WHERE modified_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-180 days')
);

UPDATE Users
SET user_name = 'Unknown User'
WHERE modified_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-180 days')
  AND user_name != 'Unknown User';

COMMIT;