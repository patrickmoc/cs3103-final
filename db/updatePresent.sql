DELIMITER //
DROP PROCEDURE IF EXISTS updatePresent;

CREATE PROCEDURE updatePresent
(
    IN presentIDIn INT,
    IN presentNameIn VARCHAR(45),
    IN presentDescIn VARCHAR(255),
    IN presentPriceIn DOUBLE(65, 2),
    IN executingUserID INT
)
BEGIN

    DECLARE v_ownerID INT;
    DECLARE v_IsAdmin BOOLEAN;
    
    SELECT userID
    INTO v_ownerID
    FROM presents
    WHERE presentID = presentIDIn;

    SELECT isAdmin
    INTO v_IsAdmin
    FROM users
    WHERE userID = executingUserID;
    
    IF (v_ownerID = executingUserID OR v_IsAdmin = true) THEN
        UPDATE presents
        SET presentName = presentNameIn, presentDesc = presentDescIn, presentPrice = presentPriceIn
        WHERE presentID = presentIDIn;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to update the present.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Access Denied.';
    END IF;

END //
DELIMITER ;