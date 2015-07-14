CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);

CREATE TABLE client_info(
  id int AUTO_INCREMENT PRIMARY KEY ,
  name VARCHAR(32) ,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE account(
  id int AUTO_INCREMENT PRIMARY KEY ,
  client_id INT NOT NULL,
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
  payer_account_id INT NOT NULL ,
  payee_account_id INT NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,
  ordered_on TIMESTAMP NOT NULL ,
  created_on TIMESTAMP NOT NULL ,
  callback_url VARCHAR(128) ,
  success SMALLINT , -- 0/1, FAIL/SUCCESS
  paybill_id VARCHAR(32) ,
  transaction_ended_on TIMESTAMP,

  FOREIGN KEY client_info_id (client_id) REFERENCES client_info(id)
);


CREATE TABLE bankcard(
  id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
  account_id INT NOT NULL COMMENT '银行卡对应的账号',
  flag TINYINT NOT NULL COMMENT '0-对私，1-对公',
  card_no VARCHAR(21) NOT NULL COMMENT '银行账号，对私必须是借记卡',
  account_name VARCHAR(12) NOT NULL COMMENT '用户银行账号姓名',
  bank_code VARCHAR(12) NOT NULL COMMENT '银行编码',
  province_code VARCHAR(12) NOT NULL COMMENT '开户行所在省编码',
  city_code VARCHAR(12) NOT NULL COMMENT '开户行所在市编码',
  branch_bank_name VARCHAR(50) NOT NULL COMMENT '开户支行名称',
  created_on TIMESTAMP NOT NULL,
  updated_on TIMESTAMP NOT NULL,
  FOREIGN KEY bankcard_account_id (account_id) REFERENCES account(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '提款绑定银行卡';


CREATE TABLE withdraw(
  id CHAR(32) PRIMARY KEY COMMENT '订单id',
  account_id INT NOT NULL COMMENT '提现账号',
  bankcard_id INT NOT NULL COMMENT '提现到银行号id',
  amount DECIMAL(12, 2) NOT NULL COMMENT '提现金额',
  created_on TIMESTAMP NOT NULL COMMENT '创建时间',
  paybill_id VARCHAR(18) COMMENT '第三方交易订单id',
  result SMALLINT COMMENT '提现结果',
  settle_date CHAR(8) COMMENT '成功支付，清算日期',
  failure_info VARCHAR(255) COMMENT '提现失败原因',
  ended_on TIMESTAMP NOT NULL COMMENT '结束时间',
  FOREIGN KEY withdraw_account_id (account_id) REFERENCES account(id),
  FOREIGN KEY withdraw_bankcard_id (bankcard_id) REFERENCES bankcard(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '提现订单';


CREATE TABLE secured_account_transaction_log(
  transaction_id CHAR(27) PRIMARY KEY,
  type VARCHAR(16) NOT NULL, -- e.g. PAY
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY transaction_id(transaction_id) REFERENCES payment(id)
);

CREATE TABLE zyt_cash_transaction_log(
  id INT AUTO_INCREMENT PRIMARY KEY,
  type VARCHAR(6) NOT NULL, -- e.g. BORROW, LEND
  amount DECIMAL(12, 2) NOT NULL, -- BORROW: amount is positive, otherwise it is negative
  created_on TIMESTAMP NOT NULL
);
