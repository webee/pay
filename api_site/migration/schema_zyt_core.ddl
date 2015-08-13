CREATE TABLE bankcard(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  account_id INT UNSIGNED NOT NULL COMMENT '银行卡对应的账号',
  flag TINYINT NOT NULL COMMENT '0-对私，1-对公',
  card_no VARCHAR(21) NOT NULL COMMENT '银行账号，对私必须是借记卡',
  card_type ENUM('DEBIT', 'CREDIT') NOT NULL COMMENT '借记卡，或者信用卡',
  account_name VARCHAR(12) NOT NULL COMMENT '用户银行账号姓名',
  bank_code VARCHAR(12) NOT NULL COMMENT '银行编码',
  province_code VARCHAR(12) NOT NULL COMMENT '开户行所在省编码',
  city_code VARCHAR(12) NOT NULL COMMENT '开户行所在市编码',
  bank_name VARCHAR(12) NOT NULL COMMENT '银行名称',
  branch_bank_name VARCHAR(50) NOT NULL COMMENT '开户支行名称',
  created_on TIMESTAMP NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE trade_order(
  id CHAR(30) PRIMARY KEY, -- prefix with 'ODX'
  type ENUM('PAY', 'REFUND', 'WITHDRAW', 'TRANSFER') NOT NULL,
  source_id CHAR(30) NOT NULL,
  from_account_id INT NOT NULL,
  to_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  state VARCHAR(16) NOT NULL,
  info VARCHAR(256) NOT NULL,
  created_on TIMESTAMP NOT NULL,
  updated_on TIMESTAMP NOT NULL,

  UNIQUE KEY source_id (source_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'PAY'
  trade_order_id CHAR(30) NOT NULL,
  trade_info VARCHAR(256),
  payer_account_id INT NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',
  created_on TIMESTAMP NOT NULL,
  updated_on TIMESTAMP NOT NULL,
  paybill_id VARCHAR(32),
  transaction_ended_on TIMESTAMP,
  confirmed_on TIMESTAMP,

  FOREIGN KEY trade_order_id(trade_order_id) REFERENCES trade_order(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE prepaid(
  id CHAR(30) PRIMARY KEY, -- prefix with 'PRP'
  account_id INT UNSIGNED NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE transfer(
  id CHAR(30) PRIMARY KEY, -- prefix with 'TFR'
  trade_id VARCHAR(30) NOT NULL,
  payer_account_id INT NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  trade_info VARCHAR(128) DEFAULT '',
  created_on TIMESTAMP NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE withdraw(
  id CHAR(30) PRIMARY KEY, -- prefix with 'WDR'
  trade_id VARCHAR(30),
  account_id INT UNSIGNED NOT NULL COMMENT '提现账号',
  bankcard_id INT UNSIGNED NOT NULL COMMENT '提现到银行号id',
  amount DECIMAL(12, 2) NOT NULL,
  async_callback_url VARCHAR(128),
  created_on TIMESTAMP NOT NULL,
  state ENUM('FROZEN', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'FROZEN',

  paybill_id VARCHAR(18) COMMENT '第三方交易订单id',
  result VARCHAR(32),
  failure_info VARCHAR(255) COMMENT '提现失败原因',
  updated_on TIMESTAMP,

  FOREIGN KEY bankcard_id(bankcard_id) REFERENCES bankcard(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE refund(
  id CHAR(30) PRIMARY KEY,  -- prefix with 'RFD'
  trade_order_id CHAR(30) NOT NULL,
  payment_id CHAR(30) NOT NULL, -- id prefixed with 'PAY'
  payer_account_id INT UNSIGNED NOT NULL,
  payee_account_id INT UNSIGNED NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',
  trade_info VARCHAR(256),

  refund_serial_no VARCHAR(16) COMMENT '退款流水号',
  updated_on TIMESTAMP,

  FOREIGN KEY trade_order_id(trade_order_id) REFERENCES trade_order(id),
  FOREIGN KEY payment_id(payment_id) REFERENCES payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE account_balance(
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  account_id INT UNSIGNED NOT NULL,
  account ENUM('CASH', 'FROZEN', 'ASSET') NOT NULL,
  side ENUM('DEBIT', 'CREDIT', 'BOTH') NOT NULL COMMENT '记账方向, both: 余额，其它：各方向发生额',
  balance DECIMAL(12, 2) NOT NULL COMMENT '余额',
  last_transaction_log_id BIGINT NOT NULL COMMENT '结算最后账户日志id',
  settled_on TIMESTAMP NOT NULL COMMENT '结算日期时间'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE event(
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  source_type ENUM('PAY', 'WITHDRAW:FROZEN', 'WITHDRAW:SUCCESS', 'WITHDRAW:FAILED', 'REFUND', 'TRANSFER', 'PREPAID') NOT NULL,
  source_id CHAR(30) NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  trade_info VARCHAR(256),
  created_on TIMESTAMP NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE cash_account_transaction_log(
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  event_id BIGINT UNSIGNED NOT NULL,
  account_id INT UNSIGNED NOT NULL,
  side ENUM('DEBIT', 'CREDIT') NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY event_id(event_id) REFERENCES event(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE frozen_account_transaction_log(
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  event_id BIGINT UNSIGNED NOT NULL,
  account_id INT UNSIGNED NOT NULL,
  side ENUM('DEBIT', 'CREDIT') NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY event_id(event_id) REFERENCES event(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE asset_account_transaction_log(
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  event_id BIGINT UNSIGNED NOT NULL,
  account_id INT UNSIGNED NOT NULL,
  side ENUM('DEBIT', 'CREDIT') NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY event_id(event_id) REFERENCES event(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;