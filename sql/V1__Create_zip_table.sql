create table zip (
    pk_id int unsigned not null AUTO_INCREMENT,
    zipcode varchar(5) not null,
    lat numeric(7,4),
    lon numeric(7,4),
    city varchar(100),
    county varchar(50),
    state varchar(50),
    PRIMARY KEY (pk_id)
);
