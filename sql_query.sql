
create database cloudstore;
use cloudstore;
create table users(email varchar(50), password varchar(20), name varchar(50), user varchar(20), primary key(email));
create table shared(filename varchar(500), path varchar(500), email varchar(500),emailto varchar(500), date varchar(100), id varchar(500));
CREATE table video (filename varchar(100),time varchar(100),id varchar(100),CONSTRAINT Person PRIMARY KEY (id,filename));