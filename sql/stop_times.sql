CREATE TABLE `stop_times` (
    trip_id INT(11),
	arrival_time VARCHAR(8),
	arrival_time_seconds INT(11),
	departure_time VARCHAR(8),
	departure_time_seconds INT(11),
	stop_id INT(11),
	stop_sequence INT(11),
	stop_headsign VARCHAR(50),
	pickup_type INT(2),
	drop_off_type INT(2),
	KEY `trip_id` (trip_id),
	KEY `arrival_time_seconds` (arrival_time_seconds),
	KEY `departure_time_seconds` (departure_time_seconds),
	KEY `stop_id` (stop_id),
	KEY `stop_sequence` (stop_sequence),
	KEY `pickup_type` (pickup_type),
	KEY `drop_off_type` (drop_off_type)
);