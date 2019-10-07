

--
-- Create the database with a testuser
--

CREATE DATABASE IF NOT EXISTS `pythonlogin`;
-- GRANT ALL ON pythonlogin TO user@localhost IDENTIFIED BY "pass";
USE `pythonlogin`;

-- Ensure UTF8 as chacrter encoding within connection.
SET NAMES utf8;


--
-- Create table for Content
--


--
-- CREATE DATABASE IF NOT EXISTS `pythonlogin`;
-- USE `pythonlogin`;
DROP TABLE IF EXISTS `accounts`;
CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`image` VARCHAR(100) DEFAULT NULL,
  	`username` varchar(50) NOT NULL,
  	`password` varchar(255) NOT NULL,
  	`email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2;

DELETE FROM `accounts`;
INSERT INTO `accounts` (`id`, `image`, `username`, `password`, `email`) VALUES (2, 'static/user.png', 'test', 'test', 'test@test.com');


 

--
--
--
--   ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
