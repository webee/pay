CREATE TABLE payment(
  id CHAR(30) PRIMARY KEY, -- prefix with 'PAY'
  trade_id CHAR(30) NOT NULL,
  payer_account_id INT NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',
  created_on TIMESTAMP NOT NULL,
  updated_on TIMESTAMP NOT NULL,
  paybill_id VARCHAR(32),
  transaction_ended_on TIMESTAMP,
  confirmed_on TIMESTAMP
);


CREATE TABLE transfer(
  id CHAR(30) PRIMARY KEY, -- prefix with 'TFR'
  trade_id CHAR(30) NOT NULL,
  payer_account_id INT NOT NULL,
  payee_account_id INT NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL
);


CREATE TABLE event(
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  source_type ENUM('PAY', 'WITHDRAW', 'REFUND', 'TRANSFER') NOT NULL,
  source_id CHAR(30) NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE account_transaction_log(
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  event_id BIGINT UNSIGNED NOT NULL,
  account_id INT UNSIGNED NOT NULL,
  side ENUM('DEBIT', 'CREDIT') NOT NULL,
  amount DECIMAL(12, 2) NOT NULL,
  created_on TIMESTAMP NOT NULL,

  FOREIGN KEY event_id(event_id) REFERENCES event(id)
);