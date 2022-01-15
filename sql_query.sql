
create database mystorage;
use mystorage;
create table users(email varchar(50), password varchar(20), name varchar(50), user varchar(20), primary key(email));
create table shared(filename varchar(500), path varchar(500), email varchar(500),emailto varchar(500), date varchar(100), id varchar(500));