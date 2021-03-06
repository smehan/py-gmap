create table S2501_ACS (
    pk_id int unsigned not null AUTO_INCREMENT,
    HC01_VC01 float not null,
    HC01_VC01_MOE float not null,
    HC02_VC01 float not null,
    HC02_VC01_MOE float not null,
    HC03_VC01 float not null,
    HC03_VC01_MOE float not null,
    HC01_VC03 float not null,
    HC01_VC03_MOE float not null,
    HC02_VC03 float not null,
    HC02_VC03_MOE float not null,
    HC03_VC03 float not null,
    HC03_VC03_MOE float not null,
    HC01_VC04 float not null,
    HC01_VC04_MOE float not null,
    HC02_VC04 float not null,
    HC02_VC04_MOE float not null,
    HC03_VC04 float not null,
    HC03_VC04_MOE float not null,
    HC01_VC05 float not null,
    HC01_VC05_MOE float not null,
    HC02_VC05 float not null,
    HC02_VC05_MOE float not null,
    HC03_VC05 float not null,
    HC03_VC05_MOE float not null,
    HC01_VC06 float not null,
    HC01_VC06_MOE float not null,
    HC02_VC06 float not null,
    HC02_VC06_MOE float not null,
    HC03_VC06 float not null,
    HC03_VC06_MOE float not null,
    HC01_VC14 float not null,
    HC01_VC14_MOE float not null,
    HC02_VC14 float not null,
    HC02_VC14_MOE float not null,
    HC03_VC14 float not null,
    HC03_VC14_MOE float not null,
    HC01_VC15 float not null,
    HC01_VC15_MOE float not null,
    HC02_VC15 float not null,
    HC02_VC15_MOE float not null,
    HC03_VC15 float not null,
    HC03_VC15_MOE float not null,
    HC01_VC19 float not null,
    HC01_VC19_MOE float not null,
    HC02_VC19 float not null,
    HC02_VC19_MOE float not null,
    HC03_VC19 float not null,
    HC03_VC19_MOE float not null,
    HC01_VC39 float not null,
    HC01_VC39_MOE float not null,
    HC02_VC39 float not null,
    HC02_VC39_MOE float not null,
    HC03_VC39 float not null,
    HC03_VC39_MOE float not null,
    track_pk_id int unsigned,
    PRIMARY KEY (pk_id),
    FOREIGN KEY (track_pk_id) REFERENCES census_tract_2010 (pk_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);