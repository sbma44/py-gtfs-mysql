CREATE TABLE `routes` (
    route_id INT(11) PRIMARY KEY,
	agency_id VARCHAR(11),
	route_short_name VARCHAR(50),
	route_long_name VARCHAR(255),
	route_type INT(2),
	route_text_color VARCHAR(255),
	route_color VARCHAR(255),
	route_url VARCHAR(255),
	route_desc VARCHAR(255),
	KEY `agency_id` (agency_id),
	KEY `route_type` (route_type)
);