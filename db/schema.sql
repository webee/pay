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
insert into trade_types values(3, '转账');
insert into trade_types values(4, '退款');

CREATE TABLE pay_trades(
  id int AUTO_INCREMENT PRIMARY KEY ,
  trade_type int NOT NULL ,
  source_channel varchar(128) NOT NULL ,
  source_order_id VARCHAR(60) NOT NULL ,
  source_order_name VARCHAR(254) NOT NULL ,
  payer VARCHAR(254) ,
  amount DECIMAL(12,2),
  created_at DATETIME DEFAULT current_timestamp,
  FOREIGN KEY pay_trades_type (trade_type) REFERENCES trade_types (id)
);