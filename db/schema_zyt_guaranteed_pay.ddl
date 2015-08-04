CREATE TABLE guaranteed_payment(
  id CHAR(30) PRIMARY KEY , -- prefix with 'GTP'
  client_id INT UNSIGNED NOT NULL ,
  order_id VARCHAR(64) NOT NULL ,
  product_name VARCHAR(50) NOT NULL ,
  product_category VARCHAR(50) NOT NULL ,
  product_desc VARCHAR(50) NOT NULL ,
  payer_account_id INT NOT NULL ,
  payee_account_id INT NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,
  refunded_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
  ordered_on TIMESTAMP NOT NULL ,
  created_on TIMESTAMP NOT NULL ,
  updated_on TIMESTAMP,
  client_callback_url VARCHAR(128),
  client_async_callback_url VARCHAR(128),
  state ENUM('CREATED', 'SECURED', 'FAILED', 'CONFIRMED', 'REFUND_PREPARED', 'REFUNDING') NOT NULL DEFAULT 'CREATED',
  paybill_id VARCHAR(32) ,
  transaction_ended_on TIMESTAMP,
  confirmed_on TIMESTAMP,

  UNIQUE KEY client_order_uiq_idx (client_id, order_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE payment_group(
  group_id VARCHAR(16) NOT NULL,
  payment_id CHAR(30) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  PRIMARY KEY primary_key (group_id, payment_id),
  FOREIGN KEY payment_id (payment_id) REFERENCES guaranteed_payment(id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE secured_account(
  client_id INT UNSIGNED NOT NULL,
  account_id INT UNSIGNED NOT NULL,
  created_on TIMESTAMP NOT NULL,

  UNIQUE KEY unique_key (client_id, account_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
