DELIMITER //
CREATE PROCEDURE removeUser
(
	IN userIDIn INT,
    IN executingUserID INT
)
BEGIN

    DECLARE v_IsAdmin BOOLEAN;

    SELECT isAdmin
    INTO v_IsAdmin
    FROM users
    WHERE userID = executingUserID;
    
    IF(v_IsAdmin = true) THEN
        DELETE FROM users
        WHERE userID = userIDIn;
        
        IF(ROW_COUNT() = 0) THEN
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Unable to delete the user.';
        END IF;
    ELSE
        SIGNAL SQLSTATE '52711'
            SET MESSAGE_TEXT = 'Access Denied.';
    END IF;

END //
DELIMITER ;
