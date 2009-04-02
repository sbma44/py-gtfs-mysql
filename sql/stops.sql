CREATE TABLE `stops` (
    stop_id INT(11) PRIMARY KEY,
    stop_code VARCHAR(50),
	stop_name VARCHAR(255),
	stop_desc VARCHAR(255),
	stop_lat DECIMAL(8,6),
	stop_lon DECIMAL(8,6),
	zone_id INT(11),
	stop_url VARCHAR(255),
	location_type INT(2),
	parent_station INT(11),
	KEY `zone_id` (zone_id),
	KEY `stop_lat` (stop_lat),
	KEY `stop_lon` (stop_lon),
	KEY `location_type` (location_type),
	KEY `parent_station` (parent_station)
);