CREATE TABLE rooms (
    `room_no` int(11) NOT NULL AUTO_INCREMENT,
    `room_name` varchar(100) NOT NULL,
    `messages_no` int(10) NOT NULL DEFAULT 0,
    PRIMARY KEY (`room_no`),
    UNIQUE KEY `room_name` (`room_name`)
) ENGINE=InnoDB;

CREATE TABLE users (
    `user_no` int(4) NOT NULL AUTO_INCREMENT,
    `user_name` varchar(40) NOT NULL,
    `user_password` varchar(40) NOT NULL,
    `messages_no` int(10) NOT NULL DEFAULT 0,
    PRIMARY KEY (`user_no`),
    UNIQUE KEY `user_name` (`user_name`)
) ENGINE=InnoDB;

INSERT INTO rooms (room_name) VALUES ('all');
INSERT INTO rooms (room_name) VALUES ('random');
INSERT INTO rooms (room_name) VALUES ('bazar');
INSERT INTO rooms (room_name) VALUES ('gaming');