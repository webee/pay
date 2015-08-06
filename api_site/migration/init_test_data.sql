INSERT INTO user_domain(name) VALUES('绿野用户中心');

INSERT INTO account(user_domain_id, user_id) VALUES(1, '1');
INSERT INTO account(user_domain_id, user_id) VALUES(1, '1001');
INSERT INTO account(user_domain_id, user_id) VALUES(1, '1002');

INSERT INTO client_info(user_domain_id, name) VALUES(1, '绿野活动');

INSERT INTO bankcard(id, account_id, flag, card_no, card_type, account_name, bank_code, province_code, city_code, bank_name,
                     branch_bank_name, created_on)
  VALUES(1, 1, 0, '6217000010057123526', 'DEBIT', '易旺', '01050000', '110000', '110000', '中国建设银行',
         '北京市朝阳区芍药居支行', current_timestamp());
