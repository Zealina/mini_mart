-- prepares a MySQL server for the project

CREATE DATABASE IF NOT EXISTS mini_mart_prod_db;
CREATE USER IF NOT EXISTS 'mini_mart_prod'@'localhost' IDENTIFIED BY 'mini_mart_prod_pwd';
GRANT ALL PRIVILEGES ON `mini_mart_prod_db`.* TO 'mini_mart_prod'@'localhost';
GRANT SELECT ON `performance_schema`.* TO 'mini_mart_prod'@'localhost';
FLUSH PRIVILEGES;
