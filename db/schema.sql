CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);

-- 自游通客户端信息
CREATE TABLE client_info(
  id int AUTO_INCREMENT PRIMARY KEY ,
  name VARCHAR(32) ,
  client_id VARCHAR(16) NOT NULL UNIQUE ,
  key_value VARCHAR(64) NOT NULL ,
  created_at TIMESTAMP DEFAULT current_timestamp
);

-- 支付记录
CREATE TABLE payment(
  id int AUTO_INCREMENT PRIMARY KEY ,
  client_id VARCHAR(16) NOT NULL ,
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


-- 自游通账号
CREATE TABLE account(
  id int AUTO_INCREMENT PRIMARY KEY ,
  account_id VARCHAR(64) NOT NULL UNIQUE ,
  user_source VARCHAR(16),
  user_id VARCHAR(32),
  activated BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否激活'
);
