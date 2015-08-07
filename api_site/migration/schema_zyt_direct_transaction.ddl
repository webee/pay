CREATE TABLE direct_payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'DRP'
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
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',

  UNIQUE KEY order_uiq_idx (channel_id, order_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;