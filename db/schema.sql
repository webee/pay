CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);

CREATE TABLE client_info(
  id int AUTO_INCREMENT PRIMARY KEY ,
  name VARCHAR(32) ,
  client_id CHAR(16) NOT NULL UNIQUE ,
  created_at TIMESTAMP DEFAULT current_timestamp
);


CREATE TABLE payment(
  id CHAR(27) PRIMARY KEY ,
  client_id VARCHAR(16) NOT NULL ,
  order_id VARCHAR(64) NOT NULL ,
  product_name VARCHAR(50) NOT NULL ,
  product_category VARCHAR(50) NOT NULL ,
  product_desc VARCHAR(50) NOT NULL ,
  account_id int ,
  to_account_id int NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,
  created_on TIMESTAMP DEFAULT current_timestamp,
  success SMALLINT , -- 0/1, FAIL/SUCCESS
  yeepay_transaction_id VARCHAR(64),
  transaction_ended_on TIMESTAMP
);


CREATE TABLE account(
  id int AUTO_INCREMENT PRIMARY KEY ,
  user_source VARCHAR(16),
  user_id VARCHAR(32)
);


CREATE TABLE virtual_account_bank_card(
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
