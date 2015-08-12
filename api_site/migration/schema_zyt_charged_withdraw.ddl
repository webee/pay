CREATE TABLE charged_withdraw(
  id CHAR(30) PRIMARY KEY, -- prefix with 'CGW'
  account_id INT NOT NULL,
  bankcard_id INT UNSIGNED NOT NULL,
  actual_withdraw_amount DECIMAL(12, 2) NOT NULL,
  fee DECIMAL(12, 2) NOT NULL,
  async_callback_url VARCHAR(128),
  state ENUM('CREATED', 'CHARGED_FEE', 'SUCCESS', 'REFUNDED_FEE') NOT NULL DEFAULT 'CREATED',
  created_on TIMESTAMP NOT NULL,
  updated_on TIMESTAMP
)