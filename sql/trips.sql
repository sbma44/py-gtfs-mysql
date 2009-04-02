CREATE TABLE `trips` (
    route_id INT(11),
	service_id INT(11),
	trip_id INT(11) PRIMARY KEY,
	trip_headsign VARCHAR(255),
	trip_short_name VARCHAR(255),
	direction_id TINYINT(1),
	block_id INT(11),
	shape_id INT(11),
	KEY `route_id` (route_id),
	KEY `service_id` (service_id),
	KEY `direction_id` (direction_id),
	KEY `block_id` (block_id),
	KEY `shape_id` (shape_id)
);