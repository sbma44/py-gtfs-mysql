CREATE TABLE `calendar_dates` (
    service_id INT(11),
    `date` VARCHAR(8),
    date_timestamp INT(11),
    exception_type INT(2),
    KEY `service_id` (service_id),
    KEY `date_timestamp` (date_timestamp),
    KEY `exception_type` (exception_type)    
);