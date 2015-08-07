INSERT INTO user_domain(id, name) VALUES(1, '担保用户中心');
INSERT INTO user_domain(id, name) VALUES(2, '绿野用户中心');

INSERT INTO account(user_domain_id, user_id, info) VALUES(1, 1, '担保账户');
INSERT INTO account(user_domain_id, user_id, info) VALUES(2, 0, '绿野账户');

INSERT INTO channel(id, user_domain_id, name) VALUES(1, 2, '绿野活动');
INSERT INTO channel(id, user_domain_id, name) VALUES(2, 2, '自游通');

