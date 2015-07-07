CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);


CREATE TABLE payments(
  id int AUTO_INCREMENT PRIMARY KEY ,
  order_source VARCHAR(32) NOT NULL ,
  order_id VARCHAR(64) NOT NULL ,

  product_name VARCHAR(50) NOT NULL ,
  product_category VARCHAR(50) NOT NULL ,
  product_desc VARCHAR(50) NOT NULL ,

  created_at TIMESTAMP DEFAULT current_timestamp,

  transaction_id VARCHAR(64) NOT NULL ,

  account_id VARCHAR(64) NOT NULL ,
  to_account_id VARCHAR(64) NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,

  -- nullable
  yeepay_transaction_id VARCHAR(64) ,
  success SMALLINT , -- 0/1, FAIL/SUCCESS
  end_at TIMESTAMP DEFAULT current_timestamp
);


CREATE TABLE accounts(
  id int AUTO_INCREMENT PRIMARY KEY ,
  account_id VARCHAR(64) NOT NULL UNIQUE ,
  password VARCHAR(64),
  pay_password VARCHAR(64),
  user_source VARCHAR(32),
  user_id VARCHAR(64),
  activated BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否激活'
);