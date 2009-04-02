CREATE TABLE `calendar` (
    service_id INT(11),
	monday TINYINT(1),
	tuesday TINYINT(1),
	wednesday TINYINT(1),
	thursday TINYINT(1),
	friday TINYINT(1),
	saturday TINYINT(1),
	sunday TINYINT(1),
	start_date VARCHAR(8),	
	end_date VARCHAR(8),
	start_date_timestamp INT(11),
	end_date_timestamp INT(11),
	KEY `service_id` (service_id),
    KEY `start_date_timestamp` (start_date_timestamp),
	KEY `end_date_timestamp` (end_date_timestamp)
);