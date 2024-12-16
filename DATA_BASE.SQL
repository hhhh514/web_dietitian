USE test;
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,    
    height FLOAT,  
    weight FLOAT,
    body_type FLOAT,
    username VARCHAR(50) NOT NULL UNIQUE, 
    password VARCHAR(255) NOT NULL
);

CREATE TABLE dishes (
    dish_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL, 
    flavor BIT(4),  
    ingredients TEXT,
    recipe TEXT,  
    calories INT
);
ALTER TABLE dish 
ADD protein INT, 
ADD sodium INT, 
ADD fat INT, 
ADD minerals INT, 
ADD fiber INT, 
ADD vitamins INT;
CREATE TABLE menu (
    menu_id INT PRIMARY KEY AUTO_INCREMENT,
    dish_id INT,
    FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
);
CREATE TABLE user_requests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    request_content TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
CREATE TABLE recommendations (
    recommendation_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    menu_id INT,
    dish_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    FOREIGN KEY (dish_id) REFERENCES dishes(dish_id)
);
