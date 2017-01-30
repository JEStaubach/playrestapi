DROP VIEW participants;
DROP VIEW skilllevels;
DROP VIEW locations;
DROP VIEW boattypes;
DROP VIEW boatstyles;
DROP VIEW boats;
DROP VIEW paddles;
DROP VIEW shafts;
DROP VIEW trailers;

DROP TABLE participants_tbl;
DROP TABLE skilllevels_tbl;
DROP TABLE locations_tbl;
DROP TABLE boattypes_tbl;
DROP TABLE boatstyles_tbl;
DROP TABLE boats_tbl;
DROP TABLE paddles_tbl;
DROP TABLE shafts_tbl;
DROP TABLE trailers_tbl;

CREATE TABLE skilllevels_tbl (
	skilllevel_id INT NOT NULL AUTO_INCREMENT,
	skilllevel_name VARCHAR(256) NOT NULL,
	PRIMARY KEY (skilllevel_id)
);

CREATE VIEW skilllevels AS SELECT * FROM skilllevels_tbl;

CREATE TABLE participants_tbl(
   participant_id INT NOT NULL AUTO_INCREMENT,
   participant_name VARCHAR(256) NOT NULL,
   participant_phone VARCHAR(256),
   participant_email VARCHAR(256),
   participant_address TEXT,
   participant_dob DATE,
   skilllevel_fk INT,
   participant_is_member_aca BIT(1),
   participant_is_member_hth BIT(1),
   participant_have_waiver BIT(1),
   participant_current_fees BIT(1),
   participant_verified_swimmer BIT(1),
   PRIMARY KEY ( participant_id )
);

CREATE VIEW participants AS SELECT participants_tbl.*, skilllevels_tbl.* FROM participants_tbl, skilllevels_tbl WHERE participants_tbl.skilllevel_fk = skilllevels_tbl.skilllevel_id;

CREATE TABLE locations_tbl (
	location_id INT NOT NULL AUTO_INCREMENT,
	location_name VARCHAR(256) NOT NULL,
	PRIMARY KEY ( location_id )
);

CREATE VIEW locations AS SELECT * FROM locations_tbl;

CREATE TABLE boattypes_tbl (
	boattype_id INT NOT NULL AUTO_INCREMENT,
	boattype_name VARCHAR(256) NOT NULL,
	PRIMARY KEY ( boattype_id )
);

CREATE VIEW boattypes AS SELECT * FROM boattypes_tbl;

CREATE TABLE boatstyles_tbl (
	boatstyle_id INT NOT NULL AUTO_INCREMENT,
	boatstyle_name VARCHAR(256) NOT NULL,
	PRIMARY KEY ( boatstyle_id )
);

CREATE VIEW boatstyles AS SELECT * FROM boatstyles_tbl;

CREATE TABLE boats_tbl (
	boat_id INT NOT NULL AUTO_INCREMENT,
	boat_name VARCHAR(256) NOT NULL,
	boattype_fk INT NOT NULL,
	boatstyle_fk INT NOT NULL,
	boat_nomen VARCHAR(256),
	boat_make VARCHAR(256),
	boat_model VARCHAR(256),
	boat_construction VARCHAR(256),
	boat_description TEXT,
	boat_usable BIT(1),
	location_fk INT NOT NULL,
	boat_owner VARCHAR(256),
	PRIMARY KEY ( boat_id )
);

CREATE VIEW boats AS SELECT * FROM boats_tbl, boattypes_tbl, boatstyles_tbl, locations_tbl WHERE boats_tbl.location_fk = locations_tbl.location_id AND boats_tbl.boatstyle_fk = boatstyles_tbl.boatstyle_id AND boats_tbl.boattype_fk = boattypes_tbl.boattype_id;

CREATE TABLE shafts_tbl (
	shaft_id INT NOT NULL AUTO_INCREMENT,
	shaft_shape VARCHAR(256) NOT NULL,
	shaft_pieces INT NOT NULL,
	PRIMARY KEY ( shaft_id )
);

CREATE VIEW shafts AS SELECT * FROM shafts_tbl;

CREATE TABLE paddles_tbl (
	paddle_id INT NOT NULL AUTO_INCREMENT,
	paddle_name VARCHAR(256) NOT NULL,
	boattype_fk INT NOT NULL,
	boatstyle_fk INT NOT NULL,
	shaft_fk INT NOT NULL,
	paddle_make VARCHAR(256),
	paddle_model VARCHAR(256),
	paddle_size VARCHAR(256),
	paddle_construction VARCHAR(256),
	paddle_description TEXT,
	paddle_usable BIT(1),
	location_fk INT NOT NULL,
	paddle_owner VARCHAR(256),
	PRIMARY KEY ( paddle_id )
);

CREATE VIEW paddles AS SELECT * FROM paddles_tbl, boattypes_tbl, boatstyles_tbl, shafts_tbl, locations_tbl WHERE paddles_tbl.boattype_fk = boattypes_tbl.boattype_id AND paddles_tbl.boatstyle_fk = boatstyles_tbl.boatstyle_id AND paddles_tbl.shaft_fk = shafts_tbl.shaft_id AND paddles_tbl.location_fk = locations_tbl.location_id;

CREATE TABLE trailers_tbl (
	trailer_id INT NOT NULL AUTO_INCREMENT,
	trailer_name VARCHAR(256) NOT NULL,
	trailer_axles INT NOT NULL,
	trailer_description TEXT,
	trailer_vin VARCHAR(256),
	trailer_licenseplate_number VARCHAR(256),
	trailer_registration_expiration DATE,
	trailer_inspection_expiration DATE,
	trailer_usable BIT(1),
	trailer_owner VARCHAR(256),
	PRIMARY KEY ( trailer_id )
);

CREATE VIEW trailers AS SELECT * FROM trailers_tbl;