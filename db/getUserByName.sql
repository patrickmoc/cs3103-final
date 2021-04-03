DELIMITER //
DROP PROCEDURE IF EXISTS getUserByName;

CREATE PROCEDURE getUserByName(IN pUserName varchar(45))
BEGIN
    SELECT *
      FROM users
        WHERE userName = pUserName;
        
    IF (ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to find a valid user.';
        END IF;
END //
DELIMITER ;
