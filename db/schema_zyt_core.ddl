CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);


CREATE TABLE client_info(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY ,
  name VARCHAR(32) ,
  created_at TIMESTAMP NOT NULL
);


CREATE TABLE account(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  client_id INT UNSIGNED NOT NULL,
  user_id VARCHAR(32) NOT NULL,
  created_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY client_user_uiq_idx (client_id, user_id),
  FOREIGN KEY client_info_id (client_id) REFERENCES client_info(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE payment(
  id CHAR(30) PRIMARY KEY , -- prefix with 'PAY'
  trade_id CHAR(30) NOT NULL ,
  payer_account_id INT NOT NULL ,
  payee_account_id INT NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',
  created_on TIMESTAMP NOT NULL ,
  updated_on TIMESTAMP NOT NULL ,
  paybill_id VARCHAR(32) ,
  transaction_ended_on TIMESTAMP,
  confirmed_on TIMESTAMP
);