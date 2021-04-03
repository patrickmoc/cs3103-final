DELIMITER //
CREATE PROCEDURE removePresent
(
	IN presentIDIn INT,
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
    
    IF(v_ownerID = executingUserID OR v_IsAdmin = true) THEN
        DELETE FROM presents
        WHERE presentID = presentIDIn;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to delete the present.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Access Denied.';
    END IF;

END //
DELIMITER ;
