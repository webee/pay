INSERT INTO client_info(name) VALUES('绿野活动');

INSERT INTO account(client_id, user_id) VALUES(1, '1');
INSERT INTO account(client_id, user_id) VALUES(1, '1001');

INSERT INTO virtual_account_bank_card(account_id, card_no, bank_name, bank_account_name, bank_account_type, reserved_phone, province, city)
  VALUES(1, '4219880509175347', '招商银行', '张三', 'Private', '1328760983', '北京', '北京');
