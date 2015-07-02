drop database if exists lvye_pay;
create database lvye_pay DEFAULT CHARACTER SET utf8;
GRANT USAGE ON *.* TO lvye_pay;
drop user lvye_pay;
create user lvye_pay identified by 'p@55word';
update mysql.user set password=password('p@55word') where user='lvye_pay' or user='lvye_pay@localhost';
grant all privileges on lvye_pay.* to 'lvye_pay'@'localhost';
flush privileges;
