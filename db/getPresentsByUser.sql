DELIMITER //
DROP PROCEDURE IF EXISTS getPresentsByUser;

CREATE PROCEDURE getPresentsByUser(IN userIDIn INT)
BEGIN
    SELECT *
    FROM presents
    WHERE userID = userIDIn;
END //
DELIMITER ;