DELIMITER //
DROP PROCEDURE IF EXISTS addPresent;

CREATE PROCEDURE addPresent (
   presentNameIn VARCHAR(45),
   presentDescIn VARCHAR(255),
   presentPriceIn DOUBLE(65, 2),
   userIdIn INT
)
BEGIN
    INSERT INTO presents (presentName, presentDesc, presentPrice, userID) VALUES (presentNameIn, presentDescIn, presentPriceIn, userIdIn);

    IF (ROW_COUNT() = 0) THEN
      SIGNAL SQLSTATE '52711'
        SET MESSAGE_TEXT = 'Unable to create the present.';
    END IF;

    /* If the INSERT is successful, then this will return the Id for the record */
    SELECT LAST_INSERT_ID(); /* Specific to this session */

END //
DELIMITER ;
