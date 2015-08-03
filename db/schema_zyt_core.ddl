CREATE TABLE payment(
  id CHAR(30) PRIMARY KEY , -- prefix with 'PAY'
  trade_id CHAR(30) NOT NULL ,
  payer_account_id INT NOT NULL ,
  payee_account_id INT NOT NULL ,
  amount DECIMAL(12, 2) NOT NULL ,
  state ENUM('CREATED', 'SUCCESS', 'FAILED') NOT NULL DEFAULT 'CREATED',
  created_on TIMESTAMP NOT NULL ,
  updated_on TIMESTAMP NOT NULL ,
  paybill_id VARCHAR(32) ,
  transaction_ended_on TIMESTAMP,
  confirmed_on TIMESTAMP
);