-- MySQL dump 10.13  Distrib 8.4.8, for macos15 (arm64)
--
-- Host: localhost    Database: WETHER_DB
-- ------------------------------------------------------
-- Server version	8.4.8

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `climate_baseline`
--

DROP TABLE IF EXISTS `climate_baseline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `climate_baseline` (
  `baseline_id` int NOT NULL AUTO_INCREMENT,
  `month` int NOT NULL,
  `month_name` varchar(15) DEFAULT NULL,
  `normal_avg_temp_c` float DEFAULT NULL,
  `normal_max_temp_c` float DEFAULT NULL,
  `normal_min_temp_c` float DEFAULT NULL,
  `normal_precip_mm` float DEFAULT NULL,
  `normal_humidity_pct` int DEFAULT NULL,
  `normal_wind_ms` float DEFAULT NULL,
  `normal_cloud_cover_pct` int DEFAULT NULL,
  `normal_rainy_days` int DEFAULT NULL,
  PRIMARY KEY (`baseline_id`),
  UNIQUE KEY `month` (`month`)
) ENGINE=InnoDB AUTO_INCREMENT=481 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `climate_baseline`
--

LOCK TABLES `climate_baseline` WRITE;
/*!40000 ALTER TABLE `climate_baseline` DISABLE KEYS */;
INSERT INTO `climate_baseline` VALUES (1,1,'January',10.2,18.4,3.6,17.5,62,1.2,28,3),(2,2,'February',12,20.3,5.5,24.3,60,1.4,31,5),(3,3,'March',16.7,25.1,9.3,51,58,1.9,43,8),(4,4,'April',20.2,28.9,13.1,85.5,66,2.1,56,9),(5,5,'May',23,31.4,16.2,162.8,76,2.4,68,13),(6,6,'June',24.4,30.3,19.7,498.9,88,2.8,92,22),(7,7,'July',24.8,29.7,20.4,797.5,92,2.6,95,26),(8,8,'August',24.6,29.9,20.1,734.1,91,2.5,94,25),(9,9,'September',23.4,28.7,18.9,429.4,87,2.2,88,20),(10,10,'October',19.8,26.4,13.7,83.7,72,1.7,55,8),(11,11,'November',14.5,22.1,7.7,20.6,63,1.4,35,4),(12,12,'December',10.8,18.8,4.1,13,60,1.2,27,3);
/*!40000 ALTER TABLE `climate_baseline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `daily_forecast`
--

DROP TABLE IF EXISTS `daily_forecast`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `daily_forecast` (
  `forecast_id` int NOT NULL AUTO_INCREMENT,
  `season_id` int DEFAULT NULL,
  `forecast_date` date NOT NULL,
  `year` int DEFAULT NULL,
  `month` int DEFAULT NULL,
  `month_name` varchar(15) DEFAULT NULL,
  `avg_temp_c` float DEFAULT NULL,
  `max_temp_c` float DEFAULT NULL,
  `min_temp_c` float DEFAULT NULL,
  `precip_mm` float DEFAULT NULL,
  `precip_probability_pct` int DEFAULT NULL,
  `humidity_pct` int DEFAULT NULL,
  `wind_speed_ms` float DEFAULT NULL,
  `wind_gust_ms` float DEFAULT NULL,
  `wind_direction` varchar(10) DEFAULT NULL,
  `cloud_cover_pct` int DEFAULT NULL,
  `visibility_km` float DEFAULT NULL,
  `uv_index` float DEFAULT NULL,
  `dewpoint_c` float DEFAULT NULL,
  `pressure_hpa` int DEFAULT NULL,
  `weather_description` varchar(255) DEFAULT NULL,
  `data_source` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`forecast_id`),
  UNIQUE KEY `forecast_date` (`forecast_date`),
  KEY `season_id` (`season_id`),
  CONSTRAINT `daily_forecast_ibfk_1` FOREIGN KEY (`season_id`) REFERENCES `seasons` (`season_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=641 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `daily_forecast`
--

LOCK TABLES `daily_forecast` WRITE;
/*!40000 ALTER TABLE `daily_forecast` DISABLE KEYS */;
INSERT INTO `daily_forecast` VALUES (1,2,'2026-04-12',2026,4,'April',19.3,23.1,15.3,0,0,61,1.7,3.8,'E',2,24,6,11.3,894,'Few clouds','Weatherbit API'),(2,2,'2026-04-13',2026,4,'April',20.3,26.2,13.9,0.0078125,20,49,1.7,3.7,'SW',12,24,10,8.6,896,'Few clouds','Weatherbit API'),(3,2,'2026-04-14',2026,4,'April',21.2,26.5,15.7,0.03125,20,54,1.8,3.8,'SSW',22,24,10,11,895,'Scattered clouds','Weatherbit API'),(4,2,'2026-04-15',2026,4,'April',21.7,26.8,16.9,0,0,54,1.9,4,'SSW',6,24,10,11.6,893,'Few clouds','Weatherbit API'),(5,2,'2026-04-16',2026,4,'April',23.1,29.1,16.1,0.0468674,20,46,1.9,4.5,'SSW',14,24,10,10.5,894,'Few clouds','Weatherbit API'),(6,2,'2026-04-17',2026,4,'April',22.1,31,17.6,0.0625,20,46,2.6,3.8,'WSW',17,24,11,8.8,870,'Few clouds','Weatherbit API'),(7,2,'2026-04-18',2026,4,'April',23.6,30.2,19,0.125,20,34,2.9,3,'SW',29,24,11,6.4,846,'Scattered clouds','Weatherbit API'),(8,2,'2026-04-19',2026,4,'April',24.5,31.9,19.2,0.0625,20,27,3,2.9,'SSW',20,24,11,4,845,'Few clouds','Weatherbit API'),(9,2,'2026-04-20',2026,4,'April',25.3,33.3,18.3,0,0,23,3,3.1,'WSW',6,24,11,1.8,844,'Few clouds','Weatherbit API'),(10,2,'2026-04-21',2026,4,'April',25.6,32.9,20.2,0,0,21,2.9,2.9,'W',36,24,11,1,844,'Scattered clouds','Weatherbit API'),(11,2,'2026-04-22',2026,4,'April',20.1,24.3,18.3,0.8125,20,32,2.4,2.5,'WSW',11,24,11,3,843,'Few clouds','Weatherbit API'),(12,2,'2026-04-23',2026,4,'April',21.8,28.4,16,0.5625,15,32,2.2,2.3,'W',5,24,11,4,844,'Few clouds','Weatherbit API'),(13,2,'2026-04-24',2026,4,'April',15.6,20.4,11.5,19.2764,85,59,1.2,2.4,'SW',33,19.3,11,6.5,805,'Heavy rain','Weatherbit API'),(14,2,'2026-04-25',2026,4,'April',23.1,27.1,18.9,1.56836,35,69,1.3,3.6,'WSW',19,24,0,17,896,'Few clouds','Weatherbit API'),(15,2,'2026-04-26',2026,4,'April',21.8,27,18,7.64551,70,77,1.2,3.2,'S',37,23.3,11,17.5,893,'Moderate rain','Weatherbit API'),(16,2,'2026-04-27',2026,4,'April',22.7,27.9,19,10.6602,80,78,1.3,3.5,'S',22,24,11,18.4,891,'Moderate rain','Weatherbit API'),(20,2,'2026-04-28',2026,4,'April',21.6,25.3,18.3,16.4062,85,83,1,3,'SSE',43,18,10,18.5,891,'Heavy rain','Weatherbit API'),(21,2,'2026-04-29',2026,4,'April',20.3,23.6,17.8,22.8854,90,84,1.1,3,'SE',64,18.2,7,17.5,892,'Heavy rain','Weatherbit API'),(22,2,'2026-04-30',2026,4,'April',19.6,22.2,16.2,2.82828,50,81,1.1,3.1,'SSW',53,20.3,8,16.1,888,'Light rain','Weatherbit API'),(23,2,'2026-05-01',2026,5,'May',17.4,20.8,15.6,2.125,40,68,1.6,1.6,'SSW',64,23,11,11.3,845,'Light rain','Weatherbit API'),(24,2,'2026-05-02',2026,5,'May',17,19.2,15.1,5.625,75,74,1.4,1.4,'SSE',68,22.3,11,12.2,844,'Light rain','Weatherbit API'),(25,2,'2026-05-03',2026,5,'May',15.8,20.4,13.9,10.875,80,80,1.5,1.4,'SW',80,20.1,11,12.3,845,'Moderate rain','Weatherbit API'),(26,2,'2026-05-04',2026,5,'May',16.1,18.7,14.1,24,90,77,2.2,2.3,'WSW',47,18.4,11,11.9,846,'Heavy rain','Weatherbit API'),(27,2,'2026-05-05',2026,5,'May',19.5,25,13.2,0.375,10,56,2,1.8,'WSW',32,24,11,9.9,846,'Scattered clouds','Weatherbit API'),(28,2,'2026-05-06',2026,5,'May',15.5,17.8,13.3,7.875,80,74,3.8,4.2,'NNW',56,23.8,11,10.7,844,'Light rain','Weatherbit API'),(29,2,'2026-05-07',2026,5,'May',15.9,18.3,13.6,5.125,70,72,2,2,'NNW',76,16.6,11,10.6,844,'Light rain','Weatherbit API'),(30,2,'2026-05-08',2026,5,'May',10.7,12.2,9.3,11.574,85,84,1.2,2,'NNW',69,15.4,11,8,764,'Moderate rain','Weatherbit API'),(31,2,'2026-05-09',2026,5,'May',11.7,16.1,7.9,4.84579,70,73,1.3,1.7,'NW',43,18.1,11,7.1,764,'Light shower rain','Weatherbit API'),(32,2,'2026-05-10',2026,5,'May',10.7,14.2,7.7,11.9546,85,82,1.6,2.2,'S',25,20.4,11,7.7,762,'Moderate rain','Weatherbit API'),(304,2,'2026-05-11',2026,5,'May',10.2,12.9,7.8,13.0545,85,81,2,2.8,'S',38,17.6,11,7.1,761,'Moderate rain','Weatherbit API');
/*!40000 ALTER TABLE `daily_forecast` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `monthly_historical`
--

DROP TABLE IF EXISTS `monthly_historical`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `monthly_historical` (
  `record_id` int NOT NULL AUTO_INCREMENT,
  `season_id` int DEFAULT NULL,
  `year` int NOT NULL,
  `month` int NOT NULL,
  `month_name` varchar(15) DEFAULT NULL,
  `avg_temp_c` float DEFAULT NULL,
  `max_temp_c` float DEFAULT NULL,
  `min_temp_c` float DEFAULT NULL,
  `total_precip_mm` float DEFAULT NULL,
  `avg_humidity_pct` int DEFAULT NULL,
  `avg_wind_spd_ms` float DEFAULT NULL,
  `avg_cloud_cover_pct` int DEFAULT NULL,
  `rainy_days` int DEFAULT NULL,
  PRIMARY KEY (`record_id`),
  UNIQUE KEY `unique_month_year` (`year`,`month`),
  KEY `season_id` (`season_id`),
  CONSTRAINT `monthly_historical_ibfk_1` FOREIGN KEY (`season_id`) REFERENCES `seasons` (`season_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monthly_historical`
--

LOCK TABLES `monthly_historical` WRITE;
/*!40000 ALTER TABLE `monthly_historical` DISABLE KEYS */;
INSERT INTO `monthly_historical` VALUES (1,1,2010,1,'January',10.2,18.1,3.5,18.4,62,1.2,28,4),(2,1,2010,2,'February',12.1,20.3,5.6,24.7,60,1.4,32,5),(3,2,2010,3,'March',16.8,25.1,9.4,47.2,57,1.8,42,7),(4,2,2010,4,'April',20.3,28.9,13.2,82.6,65,2.1,55,9),(5,2,2010,5,'May',23.1,31.4,16.3,158.3,75,2.4,68,13),(6,3,2010,6,'June',24.5,30.2,19.8,498.7,88,2.8,92,22),(7,3,2010,7,'July',24.8,29.6,20.4,787.2,92,2.6,95,26),(8,3,2010,8,'August',24.6,29.8,20.1,724.5,91,2.5,94,25),(9,3,2010,9,'September',23.5,28.7,18.9,421.3,87,2.2,88,20),(10,4,2010,10,'October',19.8,26.4,13.7,84.5,72,1.7,55,8),(11,4,2010,11,'November',14.6,22.1,7.8,19.2,63,1.4,35,4),(12,1,2010,12,'December',10.9,18.8,4.1,11.6,60,1.2,27,3),(13,1,2011,1,'January',9.8,17.6,3.1,15.2,61,1.1,26,3),(14,1,2011,2,'February',11.7,19.9,5.2,21.3,59,1.3,30,4),(15,2,2011,3,'March',16.2,24.8,8.9,52.1,58,1.9,44,8),(16,2,2011,4,'April',19.8,28.4,12.7,91.4,67,2.2,58,10),(17,2,2011,5,'May',22.8,31.1,15.9,172.6,77,2.5,71,14),(18,3,2011,6,'June',24.2,29.9,19.5,512.3,89,2.9,93,23),(19,3,2011,7,'July',24.5,29.3,20.1,812.7,93,2.7,96,27),(20,3,2011,8,'August',24.3,29.5,19.8,748.2,92,2.6,95,26),(21,3,2011,9,'September',23.1,28.4,18.6,445.8,88,2.3,89,21),(22,4,2011,10,'October',19.3,26.1,13.2,92.3,73,1.8,57,9),(23,4,2011,11,'November',14.1,21.7,7.3,22.4,64,1.5,36,4),(24,1,2011,12,'December',10.4,18.4,3.7,14.2,61,1.3,28,3),(25,1,2012,1,'January',10.5,18.4,3.8,20.1,63,1.2,29,4),(26,1,2012,2,'February',12.4,20.6,5.9,28.3,61,1.4,33,5),(27,2,2012,3,'March',17.1,25.4,9.7,55.8,59,1.9,45,8),(28,2,2012,4,'April',20.6,29.2,13.5,88.7,66,2.1,57,10),(29,2,2012,5,'May',23.4,31.7,16.6,164.5,76,2.4,69,13),(30,3,2012,6,'June',24.7,30.5,20.1,487.2,88,2.7,91,22),(31,3,2012,7,'July',25.1,30,20.7,801.4,93,2.6,96,27),(32,3,2012,8,'August',24.9,30.1,20.4,736.8,92,2.5,94,25),(33,3,2012,9,'September',23.8,29,19.2,412.6,87,2.2,87,19),(34,4,2012,10,'October',20.1,26.7,14,78.3,71,1.7,54,8),(35,4,2012,11,'November',14.9,22.4,8.1,17.5,62,1.4,34,4),(36,1,2012,12,'December',11.2,19.1,4.4,10.8,59,1.2,26,3),(37,1,2013,1,'January',9.5,17.3,2.9,12.8,60,1.1,25,3),(38,1,2013,2,'February',11.4,19.6,4.9,19.7,58,1.3,29,4),(39,2,2013,3,'March',15.9,24.5,8.6,43.6,56,1.8,41,7),(40,2,2013,4,'April',19.5,28.1,12.4,76.8,64,2,53,8),(41,2,2013,5,'May',22.5,30.8,15.6,148.9,74,2.3,66,12),(42,3,2013,6,'June',23.9,29.6,19.2,468.4,87,2.7,90,21),(43,3,2013,7,'July',24.2,29,19.8,768.9,91,2.5,94,25),(44,3,2013,8,'August',24,29.2,19.5,704.3,90,2.4,93,24),(45,3,2013,9,'September',22.8,28.1,18.3,398.7,86,2.1,86,19),(46,4,2013,10,'October',19,25.8,12.9,68.4,70,1.6,52,7),(47,4,2013,11,'November',13.8,21.4,7,15.8,61,1.3,33,3),(48,1,2013,12,'December',10.1,18.1,3.4,9.4,58,1.1,25,2),(49,1,2014,1,'January',10.8,18.7,4.1,22.6,64,1.3,30,4),(50,1,2014,2,'February',12.7,20.9,6.2,30.8,62,1.5,34,6),(51,2,2014,3,'March',17.4,25.7,10,58.4,60,2,46,8),(52,2,2014,4,'April',20.9,29.5,13.8,94.2,68,2.2,59,10),(53,2,2014,5,'May',23.7,32,16.9,178.3,78,2.5,72,15),(54,3,2014,6,'June',25,30.8,20.4,524.6,90,2.9,94,23),(55,3,2014,7,'July',25.4,30.3,21,842.1,94,2.7,97,27),(56,3,2014,8,'August',25.2,30.4,20.7,778.5,93,2.6,96,26),(57,3,2014,9,'September',24.1,29.3,19.5,458.3,89,2.3,90,21),(58,4,2014,10,'October',20.4,27,14.3,96.8,74,1.8,58,9),(59,4,2014,11,'November',15.2,22.7,8.4,24.1,65,1.5,37,5),(60,1,2014,12,'December',11.5,19.4,4.7,16.3,62,1.3,29,3),(61,1,2015,1,'January',10,17.9,3.3,16.7,61,1.2,27,3),(62,1,2015,2,'February',11.9,20.1,5.4,23.2,59,1.4,31,4),(63,2,2015,3,'March',16.5,24.9,9.1,49.8,57,1.8,43,7),(64,2,2015,4,'April',20,28.7,13,85.3,66,2.1,56,9),(65,2,2015,5,'May',22.9,31.2,16.1,162.7,76,2.4,69,13),(66,3,2015,6,'June',24.3,30,19.6,502.8,88,2.8,92,22),(67,3,2015,7,'July',24.7,29.4,20.2,791.3,92,2.6,95,26),(68,3,2015,8,'August',24.5,29.6,19.9,727.8,91,2.5,94,25),(69,3,2015,9,'September',23.3,28.5,18.7,424.6,87,2.2,88,20),(70,4,2015,10,'October',19.6,26.2,13.5,86.9,72,1.7,55,8),(71,4,2015,11,'November',14.4,21.9,7.6,20.8,63,1.4,35,4),(72,1,2015,12,'December',10.7,18.6,3.9,12.9,60,1.2,27,3),(73,1,2016,1,'January',10.3,18.2,3.6,19.3,62,1.2,28,4),(74,1,2016,2,'February',12.2,20.4,5.7,25.6,60,1.4,32,5),(75,2,2016,3,'March',16.9,25.2,9.5,51.4,58,1.9,43,8),(76,2,2016,4,'April',20.4,29,13.3,84.1,65,2.1,56,9),(77,2,2016,5,'May',23.2,31.5,16.4,160.8,75,2.4,68,13),(78,3,2016,6,'June',24.6,30.3,19.9,504.2,88,2.8,92,22),(79,3,2016,7,'July',24.9,29.7,20.5,793.6,92,2.6,96,27),(80,3,2016,8,'August',24.7,29.9,20.2,730.1,91,2.5,94,25),(81,3,2016,9,'September',23.6,28.8,19,427.8,87,2.2,88,20),(82,4,2016,10,'October',19.9,26.5,13.8,88.2,72,1.7,56,8),(83,4,2016,11,'November',14.7,22.2,7.9,21.4,63,1.4,35,4),(84,1,2016,12,'December',11,18.9,4.2,13.2,60,1.2,28,3),(85,1,2017,1,'January',9.7,17.5,3,14.1,60,1.1,26,3),(86,1,2017,2,'February',11.6,19.8,5.1,20.5,58,1.3,30,4),(87,2,2017,3,'March',16.1,24.7,8.8,46.3,56,1.8,42,7),(88,2,2017,4,'April',19.7,28.3,12.6,80.5,64,2,54,9),(89,2,2017,5,'May',22.7,31,15.8,155.4,75,2.3,67,12),(90,3,2017,6,'June',24.1,29.8,19.4,476.3,87,2.7,91,21),(91,3,2017,7,'July',24.4,29.2,20,776.4,91,2.5,95,26),(92,3,2017,8,'August',24.2,29.4,19.7,712.7,90,2.4,93,24),(93,3,2017,9,'September',23,28.3,18.5,410.2,86,2.1,87,19),(94,4,2017,10,'October',19.2,26,13.1,74.6,70,1.6,53,7),(95,4,2017,11,'November',14,21.6,7.2,18.7,61,1.3,34,4),(96,1,2017,12,'December',10.3,18.3,3.6,11.5,59,1.1,26,3),(97,1,2018,1,'January',10.6,18.5,3.9,21.4,63,1.2,29,4),(98,1,2018,2,'February',12.5,20.7,6,27.4,61,1.4,33,5),(99,2,2018,3,'March',17.2,25.5,9.8,54.2,59,1.9,44,8),(100,2,2018,4,'April',20.7,29.3,13.6,90.8,67,2.1,57,10),(101,2,2018,5,'May',23.5,31.8,16.7,170.5,77,2.5,70,14),(102,3,2018,6,'June',24.8,30.6,20.2,516.4,89,2.8,93,23),(103,3,2018,7,'July',25.2,30.1,20.8,831.8,93,2.7,96,27),(104,3,2018,8,'August',25,30.2,20.5,768.2,92,2.5,95,26),(105,3,2018,9,'September',23.9,29.1,19.3,450.6,88,2.3,89,21),(106,4,2018,10,'October',20.2,26.8,14.1,93.4,73,1.8,57,9),(107,4,2018,11,'November',15,22.5,8.2,22.8,64,1.5,36,5),(108,1,2018,12,'December',11.3,19.2,4.5,15.1,61,1.3,28,3),(109,1,2019,1,'January',9.9,17.8,3.2,15.9,61,1.1,27,3),(110,1,2019,2,'February',11.8,20,5.3,22.4,59,1.4,31,4),(111,2,2019,3,'March',16.4,24.8,9,48.7,57,1.8,43,7),(112,2,2019,4,'April',19.9,28.6,12.9,83.4,65,2.1,55,9),(113,2,2019,5,'May',22.8,31.1,16,160.2,76,2.4,68,13),(114,3,2019,6,'June',24.2,29.9,19.5,494.3,88,2.7,91,22),(115,3,2019,7,'July',24.6,29.3,20.1,784.7,91,2.6,95,26),(116,3,2019,8,'August',24.4,29.5,19.8,721.3,90,2.5,93,25),(117,3,2019,9,'September',23.2,28.4,18.6,418.9,86,2.1,87,19),(118,4,2019,10,'October',19.5,26.1,13.4,82.7,71,1.7,54,8),(119,4,2019,11,'November',14.3,21.8,7.5,19.6,62,1.4,34,4),(120,1,2019,12,'December',10.6,18.5,3.8,12.3,60,1.2,27,3),(121,1,2020,1,'January',10.1,17.9,3.4,17.8,62,1.2,28,4),(122,1,2020,2,'February',12,20.2,5.5,24.1,60,1.4,32,5),(123,2,2020,3,'March',16.7,25,9.3,50.6,57,1.9,43,8),(124,2,2020,4,'April',20.2,28.8,13.1,87.3,66,2.1,56,9),(125,2,2020,5,'May',23,31.3,16.2,166.4,76,2.4,69,14),(126,3,2020,6,'June',24.4,30.1,19.7,508.1,88,2.8,92,22),(127,3,2020,7,'July',24.8,29.5,20.3,798.6,92,2.6,96,27),(128,3,2020,8,'August',24.6,29.7,20,735.2,91,2.5,94,25),(129,3,2020,9,'September',23.4,28.6,18.8,430.4,87,2.2,88,20),(130,4,2020,10,'October',19.7,26.3,13.6,89.1,72,1.7,55,8),(131,4,2020,11,'November',14.5,22,7.7,21.2,63,1.4,35,4),(132,1,2020,12,'December',10.8,18.7,4,13.7,60,1.2,28,3),(133,1,2021,1,'January',10.4,18.3,3.7,20.6,63,1.2,29,4),(134,1,2021,2,'February',12.3,20.5,5.8,26.3,61,1.4,33,5),(135,2,2021,3,'March',17,25.3,9.6,53.1,58,1.9,44,8),(136,2,2021,4,'April',20.5,29.1,13.4,86.6,66,2.1,57,10),(137,2,2021,5,'May',23.3,31.6,16.5,162.9,76,2.4,69,13),(138,3,2021,6,'June',24.7,30.4,20,506.8,89,2.8,93,22),(139,3,2021,7,'July',25,29.8,20.6,798.3,93,2.6,96,27),(140,3,2021,8,'August',24.8,30,20.3,734.7,92,2.5,95,26),(141,3,2021,9,'September',23.7,28.9,19.1,432.1,87,2.2,89,20),(142,4,2021,10,'October',20,26.6,13.9,91.4,72,1.7,56,9),(143,4,2021,11,'November',14.8,22.3,8,22.1,63,1.4,36,4),(144,1,2021,12,'December',11.1,19,4.3,14.5,61,1.2,28,3),(145,1,2022,1,'January',9.6,17.4,2.9,13.4,60,1.1,25,3),(146,1,2022,2,'February',11.5,19.7,5,19.8,58,1.3,29,4),(147,2,2022,3,'March',16,24.6,8.7,44.9,56,1.8,41,7),(148,2,2022,4,'April',19.6,28.2,12.5,78.2,64,2,53,8),(149,2,2022,5,'May',22.6,30.9,15.7,153.7,74,2.3,66,12),(150,3,2022,6,'June',24,29.7,19.3,472.6,87,2.7,90,21),(151,3,2022,7,'July',24.3,29.1,19.9,772.1,91,2.5,94,25),(152,3,2022,8,'August',24.1,29.3,19.6,708.4,90,2.4,92,24),(153,3,2022,9,'September',22.9,28.2,18.4,406.8,85,2.1,86,19),(154,4,2022,10,'October',19.1,25.9,13,72.3,70,1.6,52,7),(155,4,2022,11,'November',13.9,21.5,7.1,17.4,61,1.3,33,3),(156,1,2022,12,'December',10.2,18.2,3.5,10.7,58,1.1,25,2),(157,1,2023,1,'January',10.7,18.6,4,22.3,64,1.3,30,4),(158,1,2023,2,'February',12.6,20.8,6.1,29.1,62,1.5,34,5),(159,2,2023,3,'March',17.3,25.6,9.9,56.7,60,1.9,45,8),(160,2,2023,4,'April',20.8,29.4,13.7,92.5,67,2.2,58,10),(161,2,2023,5,'May',23.6,31.9,16.8,175.2,77,2.5,71,15),(162,3,2023,6,'June',24.9,30.7,20.3,520.7,90,2.9,94,23),(163,3,2023,7,'July',25.3,30.2,20.9,845.3,94,2.7,97,27),(164,3,2023,8,'August',25.1,30.3,20.6,781.6,93,2.6,96,26),(165,3,2023,9,'September',24,29.2,19.4,461.8,89,2.3,90,21),(166,4,2023,10,'October',20.3,26.9,14.2,97.6,74,1.8,58,9),(167,4,2023,11,'November',15.1,22.6,8.3,24.8,65,1.5,37,5),(168,1,2023,12,'December',11.4,19.3,4.6,16.8,62,1.3,29,3),(169,1,2024,1,'January',10,17.9,3.2,16.3,61,1.2,27,3),(170,1,2024,2,'February',11.9,20.1,5.4,22.8,59,1.4,31,5),(171,2,2024,3,'March',16.6,25,9.2,51.8,57,1.8,43,8),(172,2,2024,4,'April',20.1,28.7,13.1,86.4,65,2.1,56,9),(173,2,2024,5,'May',22.9,31.2,16.1,163.8,75,2.4,68,13),(174,3,2024,6,'June',24.3,30,19.6,499.4,88,2.8,92,22),(175,3,2024,7,'July',24.7,29.4,20.2,788.5,92,2.6,95,26),(176,3,2024,8,'August',24.5,29.6,19.9,724.9,91,2.5,94,25),(177,3,2024,9,'September',23.3,28.5,18.7,422.7,86,2.2,87,20),(178,4,2024,10,'October',19.6,26.2,13.5,85.3,71,1.7,55,8),(179,4,2024,11,'November',14.4,21.9,7.6,20.4,62,1.4,34,4),(180,1,2024,12,'December',10.7,18.6,3.9,13.1,60,1.2,27,3);
/*!40000 ALTER TABLE `monthly_historical` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `seasons`
--

DROP TABLE IF EXISTS `seasons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `seasons` (
  `season_id` int NOT NULL AUTO_INCREMENT,
  `season_name` varchar(20) NOT NULL,
  `month_start` int DEFAULT NULL,
  `month_end` int DEFAULT NULL,
  `tourism_level` varchar(20) DEFAULT NULL,
  `avg_temp_c` float DEFAULT NULL,
  `avg_precip_mm` float DEFAULT NULL,
  `avg_humidity_pct` float DEFAULT NULL,
  `avg_cloud_cover_pct` float DEFAULT NULL,
  `rainy_days_per_month` int DEFAULT NULL,
  `climate_description` text,
  `season_highlights` text,
  `key_features` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`season_id`),
  UNIQUE KEY `season_name` (`season_name`)
) ENGINE=InnoDB AUTO_INCREMENT=161 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `seasons`
--

LOCK TABLES `seasons` WRITE;
/*!40000 ALTER TABLE `seasons` DISABLE KEYS */;
INSERT INTO `seasons` VALUES (1,'Winter',12,2,'High',11,16.8,61,29,3,'Winter in Pokhara is characterised by clear skies, cool temperatures, and very low precipitation. Daytime highs typically reach 17–20°C, while nights are cold, frequently dropping to 3–6°C in the valley floor. This period is widely considered the best season for mountain visibility — the Annapurna and Machapuchare (Fishtail) peaks are clearly visible from Phewa Lake on most days.','[\"Clear, dry conditions - ideal for trekking and paragliding\", \"Strong diurnal temperature range (up to 15\\u00b0C between night and day)\", \"Fog in the valley during early mornings is common in December-January\", \"Peak tourist season; accommodation demand is at its highest\"]','Clear skies, cold nights, Himalaya views at best'),(2,'Pre-Monsoon',3,5,'Moderate',20,103.7,67,56,9,'Temperatures warm rapidly through March as the sun\'s angle increases. By May, daytime highs routinely exceed 30°C, and humidity starts to climb in advance of the monsoon. Pre-monsoon thunderstorms become frequent from April onward, often developing in the afternoon as convective activity increases over the heated valley and surrounding hills.','[\"Rhododendron forests bloom vividly in March-April at higher elevations\", \"Afternoon thunderstorms with lightning and heavy localised downpours\", \"Haze and reduced visibility on some days due to agricultural burning\", \"Good conditions for trekking in March; increasingly uncomfortable by late May\"]','Warming temps, occasional storms, flowers bloom'),(3,'Monsoon',6,9,'Low',24.3,596.4,89,92,23,'The South Asian Monsoon typically arrives in Pokhara around 10–15 June, bringing a dramatic increase in precipitation that can transform the landscape within days. Pokhara receives by far the most rainfall of any Nepalese city during this period, with July being the wettest month (averaging 750–850 mm). Cloud cover is persistent, often exceeding 90%, and sunshine hours drop sharply.','[\"Over 80% of annual rainfall falls between June and September\", \"Phewa Lake and surrounding wetlands fill significantly\", \"High risk of flash floods, landslides, and road closures on mountain roads\", \"Leeches common on trekking trails; generally not recommended for beginners\", \"Temperature stays warm (23-25\\u00b0C avg) due to high humidity and cloud cover\"]','Heavy rain, lush scenery, frequent flooding risk'),(4,'Post-Monsoon',10,11,'Very High',17.1,57,67,44,6,'After the monsoon retreats (usually by early October), Pokhara enters its most celebrated season. The air is exceptionally clean after months of heavy rain, visibility is superb, and the sky is a deep, unobstructed blue. Temperatures are mild and comfortable.','[\"Best mountain panoramas of the entire year\", \"Comfortable trekking temperatures: 15-24\\u00b0C during the day\", \"Second peak tourist season after winter - very high hotel occupancy\", \"Risk of early-season frosts at elevations above 3,000 m by November\"]','Crystal clear air, best mountain views, mild temps');
/*!40000 ALTER TABLE `seasons` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-26  1:28:45
