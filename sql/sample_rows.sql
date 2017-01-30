INSERT INTO skilllevels_tbl ( skilllevel_name ) VALUES ( 'Hopper' );
INSERT INTO skilllevels_tbl ( skilllevel_name ) VALUES ( 'Bunny' );
INSERT INTO skilllevels_tbl ( skilllevel_name ) VALUES ( 'Rabbit' );
INSERT INTO skilllevels_tbl ( skilllevel_name ) VALUES ( 'Jack Rabbit' );
INSERT INTO skilllevels_tbl ( skilllevel_name ) VALUES ( 'Jackalope' );

INSERT INTO participants_tbl ( participant_name, participant_phone, participant_email, participant_address, participant_dob, skilllevel_fk, participant_is_member_aca, participant_is_member_hth, participant_have_waiver, participant_current_fees, participant_verified_swimmer) VALUES ('John Doe','(518) 555-5555','test@test.com','1 Main Street, Albany, NY 12209','1980-01-01', 3, b'1', b'1', b'0', b'0', b'0' );

INSERT INTO locations_tbl ( location_name ) VALUES ( 'Purple Trailer' );
INSERT INTO locations_tbl ( location_name ) VALUES ( 'Red Trailer' );
INSERT INTO locations_tbl ( location_name ) VALUES ( 'Dummy\'s Basement' );
INSERT INTO locations_tbl ( location_name ) VALUES ( 'Dummy\'s Barn' );
INSERT INTO locations_tbl ( location_name ) VALUES ( 'Bubba\'s Garage' );
INSERT INTO locations_tbl ( location_name ) VALUES ( 'Gump\'s Home' );

INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Sprint' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Marathon' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Down River' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'White Water' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Free Style' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Surf Ski' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Scupper' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'SUP' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'Dragon Boat' );
INSERT INTO boattypes_tbl ( boattype_name ) VALUES ( 'War Canoe' );

INSERT INTO boatstyles_tbl ( boatstyle_name ) VALUES ( 'Canoe' );
INSERT INTO boatstyles_tbl ( boatstyle_name ) VALUES ( 'Kayak' );
INSERT INTO boatstyles_tbl ( boatstyle_name ) VALUES ( 'Paddle Board' );

INSERT INTO boats_tbl ( boat_name, boattype_fk, boatstyle_fk, boat_nomen, boat_make, boat_model, boat_construction, boat_description, boat_usable, location_fk, boat_owner  ) VALUES ( 'Baby Blue', 0, 1, 'K-4', 'Van Deusen', '', 'Carbon Fiber', 'Baby Blue Van Deusen K-4', b'0', 3, 'Club' );

INSERT INTO shafts_tbl ( shaft_shape, shaft_pieces ) VALUES ( 'Round', 1 );
INSERT INTO shafts_tbl ( shaft_shape, shaft_pieces ) VALUES ( 'Round', 2 );
INSERT INTO shafts_tbl ( shaft_shape, shaft_pieces ) VALUES ( 'Oval', 1 );
INSERT INTO shafts_tbl ( shaft_shape, shaft_pieces ) VALUES ( 'Oval', 2 );

INSERT INTO paddles_tbl ( paddle_name, boattype_fk, boatstyle_fk, shaft_fk, paddle_make, paddle_model, paddle_size, paddle_construction, paddle_description, paddle_usable, location_fk, paddle_owner ) VALUES ( 'SK001', 0, 1, 0, 'Unbranded', 'Parallel Wing', 'Adult Large', 'Full Carbon', 'Black Full Carbon K-1 Paddle with White Rabbit - Red Head Band Sticker', b'1', 2, 'Tim Dummy' );

INSERT INTO trailers_tbl ( trailer_name, trailer_axles, trailer_description, trailer_vin, trailer_licenseplate_number, trailer_registration_expiration, trailer_inspection_expiration, trailer_usable, trailer_owner ) VALUES ( 'Purple Trailer', 2, 'Purple 2-axle, 3 mast', '', '', NULL, NULL, b'0', 'Club' );
INSERT INTO trailers_tbl ( trailer_name, trailer_axles, trailer_description, trailer_vin, trailer_licenseplate_number, trailer_registration_expiration, trailer_inspection_expiration, trailer_usable, trailer_owner ) VALUES ( 'Red Trailer', 1, 'Red 1-axle, 2 mast', '', '', NULL, NULL, b'0', 'Club' );
