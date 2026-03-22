CREATE DATABASE IF NOT EXISTS piano_app;
USE piano_app;

-- 家长表
CREATE TABLE parents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 孩子表
CREATE TABLE children (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT NOT NULL,
    name VARCHAR(80) NOT NULL,
    age INT,
    password_hash VARCHAR(255) NOT NULL,
    game_balance INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE
);

-- 练琴记录表
CREATE TABLE practice_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    child_id INT NOT NULL,
    date DATE NOT NULL,
    practice_minutes INT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE,
    UNIQUE KEY unique_daily_record (child_id, date)
);

-- 游戏时间奖励表
CREATE TABLE game_awards (
    id INT PRIMARY KEY AUTO_INCREMENT,
    parent_id INT NOT NULL,
    child_id INT NOT NULL,
    game_minutes INT NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE,
    FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX idx_child_parent ON children(parent_id);
CREATE INDEX idx_practice_child ON practice_records(child_id);
CREATE INDEX idx_practice_date ON practice_records(date);
CREATE INDEX idx_award_parent ON game_awards(parent_id);
CREATE INDEX idx_award_child ON game_awards(child_id);
