DELIMITER //
DROP PROCEDURE IF EXISTS getPresentById;

CREATE PROCEDURE getPresentById(IN presentIdIn INT)
BEGIN
    SELECT *
      FROM presents
        WHERE presentID = presentIdIn;

END //
DELIMITER ;