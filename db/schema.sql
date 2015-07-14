CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);

CREATE TABLE client_info(
  id int AUTO_INCREMENT PRIMARY KEY ,
  name VARCHAR(32) ,
  created_at TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE account(
  id int AUTO_INCREMENT PRIMARY KEY ,
  client_id int NOT NULL,
  user_id VARCHAR(32) NOT NULL,

  FOREIGN KEY client_info_id (client_id) REFERENCES client_info(id)
);

CREATE TABLE payment(
  id CHAR(27) PRIMARY KEY ,
  client_id int NOT NULL ,
  order_id VARCHAR(64) NOT NULL ,
  product_name VARCHAR(50) NOT NULL ,
  product_category VARCHAR(50) NOT NULL ,
  product_desc VARCHAR(50) NOT NULL ,
  payer_account_id int NOT NULL ,
  payee_account_id int NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,
  ordered_on TIMESTAMP NOT NULL ,
  created_on TIMESTAMP DEFAULT current_timestamp ,
  callback_url VARCHAR(128) ,
  success SMALLINT , -- 0/1, FAIL/SUCCESS
  paybill_id VARCHAR(32) ,
  transaction_ended_on TIMESTAMP,

  FOREIGN KEY client_info_id (client_id) REFERENCES client_info(id)
);

CREATE TABLE bank_card(
  id INT AUTO_INCREMENT PRIMARY KEY,
  account_id INT NOT NULL,
  card_no VARCHAR(21) NOT NULL,
  bank_name VARCHAR(50) NOT NULL,
  bank_account_name VARCHAR(20) NOT NULL,
  bank_account_type VARCHAR(11) NOT NULL,
  reserved_phone VARCHAR(11) NOT NULL,
  province VARCHAR(10) NOT NULL,
  city VARCHAR(20) NOT NULL,
  FOREIGN KEY zyt_account_id (account_id) REFERENCES account(id)
);
