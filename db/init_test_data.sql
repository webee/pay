INSERT INTO client_info(name) VALUES('绿野活动');

INSERT INTO account(client_id, user_id) VALUES(1, '1');
INSERT INTO account(client_id, user_id) VALUES(1, '1001');

INSERT INTO bankcard(id, account_id, flag, card_no, account_name, bank_code, province_code, city_code, bank_name,
                     branch_bank_name, created_on)
  VALUES(1, 1, 0, '6222081202007688888', '张三', '03050000', '', '110001', '民生银行',
         '运城车站支行', current_timestamp());
