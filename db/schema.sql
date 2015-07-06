CREATE TABLE db_migration (
  latest_version INT
);

insert into db_migration values(0);

create table trade_types(
  id int PRIMARY KEY ,
  name VARCHAR(30)
) ;
insert into trade_types values(1, '支付');
insert into trade_types values(2, '提现');
insert into trade_types values(3, '退款');

CREATE TABLE pay_trade_records(
  id int AUTO_INCREMENT PRIMARY KEY ,
  trade_type int NOT NULL ,
  trade_serial_no VARCHAR(50) NOT NULL ,
  source_channel VARCHAR(128) NOT NULL ,
  source_order_id VARCHAR(60) NOT NULL ,
  source_user_id VARCHAR(32) NOT NULL ,
  source_account VARCHAR(32) NOT NULL ,
  amount DECIMAL(12,2) ,
  to_account VARCHAR(32) NOT NULL ,
  product_name VARCHAR(50) NOT NULL ,
  product_cat VARCHAR(50) NOT NULL ,
  product_desc VARCHAR(50) NOT NULL ,
  status VARCHAR(32) NOT NULL ,
  created_at TIMESTAMP DEFAULT current_timestamp,
  FOREIGN KEY pay_trades_type (trade_type) REFERENCES trade_types (id)
);