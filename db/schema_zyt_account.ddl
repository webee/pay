CREATE TABLE client_info(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY ,
  name VARCHAR(32) ,
  created_at TIMESTAMP NOT NULL
);


CREATE TABLE account(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  client_id INT UNSIGNED NOT NULL,
  user_id VARCHAR(32) NOT NULL,
  'desc' VARCHAR(32),
  created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY client_user_uiq_idx (client_id, user_id),
  FOREIGN KEY client_info_id (client_id) REFERENCES client_info(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
