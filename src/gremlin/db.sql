create database nova;

use nova;

create table flavor_type (
  id int auto_increment,
  name varchar(32),
  property varchar(32),
  primary key(id)
);

create table flavor (
  id int auto_increment,
  name varchar(32),
  property varchar(32),
  type_id int,
  primary key(id),
  foreign key fk_type(type_id) references flavor_type(id)
);

create table instance (
  id int auto_increment,
  name varchar(32),
  description varchar(32),
  flavor_id int,
  max_num int,
  primary key(id),
  foreign key fk_flavor(flavor_id) references flavor(id)
);
