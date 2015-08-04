CREATE TABLE identifying_code(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(32) NOT NULL,
  code VARCHAR(32) NOT NULL,
  expire_at TIMESTAMP NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;