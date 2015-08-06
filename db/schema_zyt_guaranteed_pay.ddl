CREATE TABLE guaranteed_payment(
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
  state ENUM('CREATED', 'SECURED', 'FAILED', 'CONFIRMED', 'REFUNDED') NOT NULL DEFAULT 'CREATED',

  UNIQUE KEY order_uiq_idx (channel_id, order_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE payment_group(
  group_id VARCHAR(16) NOT NULL,
  payment_id CHAR(30) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  PRIMARY KEY primary_key (group_id, payment_id),
  FOREIGN KEY payment_id (payment_id) REFERENCES guaranteed_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE secure_payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'SCP'
  guaranteed_payment_id CHAR(30) NOT NULL,
  payer_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY guaranteed_payment_id(guaranteed_payment_id) REFERENCES guaranteed_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE confirm_payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'CFP'
  guaranteed_payment_id CHAR(30) NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY guaranteed_payment_id(guaranteed_payment_id) REFERENCES guaranteed_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE guaranteed_refund(
  id CHAR(30) PRIMARY KEY,  -- prefix with 'GTR'
  guaranteed_payment_id CHAR(30) NOT NULL,
  payer_account_id INT UNSIGNED NOT NULL,
  payee_account_id INT UNSIGNED NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  async_callback_url VARCHAR(128),
  created_on TIMESTAMP NOT NULL,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',

  refund_serial_no VARCHAR(16) COMMENT '退款流水号',
  updated_on TIMESTAMP,

  FOREIGN KEY guaranteed_payment_id(guaranteed_payment_id) REFERENCES guaranteed_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;