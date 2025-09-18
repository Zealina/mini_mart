-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS mini_mart_test_db;
CREATE USER IF NOT EXISTS 'mini_mart_test'@'localhost' IDENTIFIED BY 'mini_mart_test_pwd';
GRANT ALL PRIVILEGES ON `mini_mart_test_db`.* TO 'mini_mart_test'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'mini_mart_test'@'localhost';
FLUSH PRIVILEGES;
