-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 20, 2021 at 06:31 AM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.2.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+05:30";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `farmers`
--

-- --------------------------------------------------------

--
-- Table structure for table `addagroproducts`
--

CREATE TABLE `user` (
  `id` int(11) PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(50) NOT NULL UNIQUE,
  `email` varchar(50) NOT NULL UNIQUE,
  `type` varchar(5) NOT NULL DEFAULT 'User',
  `password` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `user` (`username`, `email`, `type`, `password`) VALUES ('Mohammed', 'mohammed@gmail.com', 'admin', 'gAAAAABjzMYf3gLSf-QOGGlhw5AMZD7IoFas9BAHXsrOaoPgiRG2hUanRpiE573ZpvLeJskMXgNrw6k4yQ32pT2ovdQ7pqZDkQ=='),
  ('Manish', 'manish123@gmail.com', 'admin', 'gAAAAABjzMbpHpvPCpI4tzBToWV_LHxOGSIb7pyMifsMz5p0fRLd59uTK1Y0dfMb_gWzuXTjHbc3nPWmWdBEGitvKZGGT5n5eA=='),
  ('Prateek', 'prateek.reddy@gmail.com', 'admin', 'gAAAAABjzMcuuCHMMoLNdDU75TR6ULP-2Hpi6HGKfWbvLPcEakBFIIKyVPNQlvSnzgSz8kmpQKRRD-HDJdyRFEm2XXeEre9QAg==');

-- --------------------------------------------------------



CREATE TABLE `register` (
  `rid` int(11) PRIMARY KEY AUTO_INCREMENT,
  `farmername` varchar(50) NOT NULL UNIQUE,
  `adharnumber` varchar(20) NOT NULL UNIQUE,
  `age` int(100) NOT NULL,
  `gender` varchar(50) NOT NULL,
  `phonenumber` varchar(12) NOT NULL UNIQUE,
  `address` varchar(50) NOT NULL,
  `id` int(11) NOT NULL,
  CONSTRAINT reg_FK FOREIGN KEY(`id`) REFERENCES user(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Table structure for table `farming`
--

CREATE TABLE `farming` (
  `fid` int(11) PRIMARY KEY AUTO_INCREMENT,
  `farmingtype` varchar(200) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `farming` (`farmingtype`) VALUES
('Seed Farming'),
('Vegetable'),
('Diary Product'),
('Material');

CREATE TABLE `farmingtypes` (
  `rid` int(11) NOT NULL,
  `fid` int(11) NOT NULL,
  CONSTRAINT ft_FK_1 FOREIGN KEY(`rid`) REFERENCES register(`rid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT ft_FK_2 FOREIGN KEY(`fid`) REFERENCES farming(`fid`) ON DELETE CASCADE ON UPDATE CASCADE
);



CREATE TABLE `addagroproducts` (
  `username` varchar(50) NOT NULL,
  `email` varchar(50) NOT NULL,
  `pid` int(11) PRIMARY KEY AUTO_INCREMENT,
  `productname` varchar(100) NOT NULL,
  `productdesc` text NOT NULL,
  `price` int(100) NOT NULL,
  `rid` int(11) NOT NULL,
  `fid` int(11) NOT NULL,
  CONSTRAINT ag_FK_1 FOREIGN KEY(`rid`) REFERENCES register(`rid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT ag_FK_2 FOREIGN KEY(`fid`) REFERENCES farming(`fid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `addagroproducts`
--

INSERT INTO `addagroproducts` (`username`, `email`, `pid`, `productname`, `productdesc`, `price`) VALUES
('Mohammed', 'mohammed@gmail.com', 1, 'GIRIJA CAULIFLOWER', ' Tips for Growing Cauliflower. Well drained medium loam and or sandy loam soils are suitable.', 520),
('manish', 'manish123@gmail.com', 2, 'COTTON', 'Cotton is a soft, fluffy staple fiber that grows in a boll,around the seeds of the cotton ', 563),
('prateek', 'prateek.reddy@gmail.com', 3, 'silk', 'silk is best business developed from coocon for saries preparation and so on', 582);




-- --------------------------------------------------------

--
-- Table structure for table `test`
--

--
-- Table structure for table `trig`
--

CREATE TABLE `trig` (
  `id` int(11) PRIMARY KEY AUTO_INCREMENT,
  `action` varchar(200) NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- Triggers `register`
--
DELIMITER $$
CREATE TRIGGER `deletionreg` BEFORE DELETE ON `register` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('Farmer Deleted: ', OLD.farmername),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `insertionreg` AFTER INSERT ON `register` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('Farmer Added: ', NEW.farmername),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `updationreg` AFTER UPDATE ON `register` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('Farmer Updated: ', NEW.farmername),NOW());
END$$
DELIMITER ;

-- Triggers `user`
--
DELIMITER $$
CREATE TRIGGER `deletionusr` BEFORE DELETE ON `user` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('User Deleted: ', OLD.username),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `insertionusr` AFTER INSERT ON `user` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('User Added: ', NEW.username),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `updationusr` AFTER UPDATE ON `user` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('User Updated: ', NEW.username),NOW());
END$$
DELIMITER ;

-- Triggers `add agroproducts`
--
DELIMITER $$
CREATE TRIGGER `deletionagro` BEFORE DELETE ON `addagroproducts` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT(OLD.username, " deleted ", OLD.productname),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `insertionagro` AFTER INSERT ON `addagroproducts` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT(NEW.username, " added ", NEW.productname),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `updationagro` AFTER UPDATE ON `addagroproducts` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT(NEW.username, " updated ", NEW.productname),NOW());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER `insertionfarm` AFTER INSERT ON `farming` FOR EACH ROW
BEGIN
  INSERT INTO trig(action, timestamp) VALUES(CONCAT('Farming Type Inserted: ', NEW.farmingtype),NOW());
END$$
DELIMITER ;
