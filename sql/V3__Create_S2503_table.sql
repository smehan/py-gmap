create table S2503_ACS (
    pk_id int unsigned not null AUTO_INCREMENT,
    HC01_VC01 float not null,
    HC02_VC01 float not null,
    HC03_VC01 float not null,
    HC01_VC03 float not null,
    HC02_VC03 float not null,
    HC03_VC03 float not null,
    HC01_VC04 float not null,
    HC02_VC04 float not null,
    HC03_VC04 float not null,
    HC01_VC05 float not null,
    HC02_VC05 float not null,
    HC03_VC05 float not null,
    HC01_VC06 float not null,
    HC02_VC06 float not null,
    HC03_VC06 float not null,
    HC01_VC07 float not null,
    HC02_VC07 float not null,
    HC03_VC07 float not null,
    HC01_VC08 float not null,
    HC02_VC08 float not null,
    HC03_VC08 float not null,
    HC01_VC09 float not null,
    HC02_VC09 float not null,
    HC03_VC09 float not null,
    HC01_VC10 float not null,
    HC02_VC10 float not null,
    HC03_VC10 float not null,
    HC01_VC11 float not null,
    HC02_VC11 float not null,
    HC03_VC11 float not null,
    HC01_VC12 float not null,
    HC02_VC12 float not null,
    HC03_VC12 float not null,
    HC01_VC13 float not null,
    HC02_VC13 float not null,
    HC03_VC13 float not null,
    HC01_VC14 float not null,
    HC02_VC14 float not null,
    HC03_VC14 float not null,
    track_pk_id int unsigned,
    PRIMARY KEY (pk_id),
    FOREIGN KEY (track_pk_id) REFERENCES census_tract_2010 (pk_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);