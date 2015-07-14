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

CREATE TABLE bank_card (
  id INT AUTO_INCREMENT PRIMARY KEY,
  account_id INT NOT NULL COMMENT '账号id',
  flag TINYINT NOT NULL COMMENT '0-对私，1-对公',
  card_no VARCHAR(21) NOT NULL COMMENT '用户银行卡, 对私必须是借记卡',
  account_name VARCHAR(12) NOT NULL COMMENT '用户银行账号姓名',
  bank_code VARCHAR(20) NOT NULL COMMENT '银行编码',
  province_code VARCHAR(20) NOT NULL COMMENT '开户行所在省编码',
  city_code VARCHAR(20) NOT NULL COMMENT '开户行所在市编码',
  branch_bank_name VARCHAR(50) NOT NULL COMMENT '开户支行名称',
  FOREIGN KEY bank_card_account_id (account_id) REFERENCES account(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '账号绑定的提现银行卡';
