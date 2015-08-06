INSERT INTO user_domain(id, name) VALUES(1, '绿野用户中心');
INSERT INTO user_domain(id, name) VALUES(2, '担保用户中心');

INSERT INTO channel(id, user_domain_id, name) VALUES(1, 1, '绿叶活动');

INSERT INTO account(user_domain_id, user_id, info) VALUES(2, 1, '担保账户');
