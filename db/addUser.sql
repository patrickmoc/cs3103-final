DELIMITER //
DROP PROCEDURE IF EXISTS addUser;

CREATE PROCEDURE addUser(
   userName varchar(45),
   isAdmin tinyint(1)
)
BEGIN
    INSERT INTO users (userName, isAdmin) VALUES (userName, isAdmin);

    IF(ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create the user.';
    END IF;

    /* If the INSERT is successful, then this will return the Id for the record */
    SELECT LAST_INSERT_ID(); /* Specific to this session */

END //
DELIMITER ;