DELIMITER //
DROP PROCEDURE IF EXISTS getUserById;

CREATE PROCEDURE getUserById(IN pUserId INT)
BEGIN
    SELECT *
      FROM users
        WHERE userID = pUserId;

   IF (ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to find a valid user.';
        END IF;
END //