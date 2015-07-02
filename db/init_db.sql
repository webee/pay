drop database if exists cs;
create database cs;
drop user cs;
create user cs identified by 'p@55word';
update mysql.user set password=password('p@55word') where user='cs' or user='cs@localhost';
grant all privileges on cs.* to 'cs'@'localhost';
flush privileges;
