DELIMITER //
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  userID    INT             NOT NULL AUTO_INCREMENT,
  userName  varchar(45)     NOT NULL,
  isAdmin   boolean         NOT NULL,
  PRIMARY KEY (userID)
); //

DROP TABLE IF EXISTS presents;
CREATE TABLE presents (
  presentID     INT             NOT NULL AUTO_INCREMENT,
  userID        INT             NOT NULL,
  presentName   varchar(45)     NOT NULL,
  presentDesc   varchar(255),
  presentPrice  DOUBLE           NOT NULL,
  PRIMARY KEY (presentID),
  FOREIGN KEY (userID) REFERENCES users (userID)
); //
DELIMITER ;