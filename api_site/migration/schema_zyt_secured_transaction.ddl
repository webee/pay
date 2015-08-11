CREATE TABLE secured_payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'GTP'
  channel_id INT UNSIGNED NOT NULL,
  order_id VARCHAR(64) NOT NULL,
  product_name VARCHAR(50) NOT NULL,
  product_category VARCHAR(50) NOT NULL,
  product_desc VARCHAR(50) NOT NULL,
  payer_account_id INT NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  refunded_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
  ordered_on TIMESTAMP NOT NULL,
  created_on TIMESTAMP NOT NULL,
  updated_on TIMESTAMP,
  client_callback_url VARCHAR(128),
  client_async_callback_url VARCHAR(128),
  state ENUM('CREATED', 'SECURED', 'FAILED', 'CONFIRMED', 'REFUNDING', 'REFUNDED') NOT NULL DEFAULT 'CREATED',

  UNIQUE KEY order_uiq_idx (channel_id, order_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE payment_group(
  group_id VARCHAR(16) NOT NULL,
  payment_id CHAR(30) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  PRIMARY KEY primary_key (group_id, payment_id),
  FOREIGN KEY payment_id (payment_id) REFERENCES secured_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE request_secured_payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'SCP'
  secured_payment_id CHAR(30) NOT NULL,
  payer_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY secured_payment_id(secured_payment_id) REFERENCES secured_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE confirm_payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'CFP'
  secured_payment_id CHAR(30) NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY secured_payment_id(secured_payment_id) REFERENCES secured_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE secured_refund(
  id CHAR(30) PRIMARY KEY,  -- prefix with 'GTR'
  secured_payment_id CHAR(30) NOT NULL,
  payer_account_id INT UNSIGNED NOT NULL,
  payee_account_id INT UNSIGNED NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  async_callback_url VARCHAR(128),
  created_on TIMESTAMP NOT NULL,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',

  refund_serial_no VARCHAR(16) COMMENT '退款流水号',
  updated_on TIMESTAMP,

  FOREIGN KEY secured_payment_id(secured_payment_id) REFERENCES secured_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;