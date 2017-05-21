CREATE TABLE IF NOT EXISTS `FOLLOWERS` (
	`leader_url_token` VARCHAR(100) NOT NULL COMMENT '领导与追随者关系的短url',
	`url_token` VARCHAR(100) NOT NULL,
	`IS_followed` INT(1) NOT NULL COMMENT '是否追随',
	`avatar_url_temp` VARCHAR(100) NOT NULL COMMENT '背景图片链接',
	`user_type` VARCHAR(100) NOT NULL COMMENT '用户类型',
	`gender` INT(1) NOT NULL DEFAULT 0 COMMENT '0男1女-1未知',
	`follower_count` INT(9) NOT NULL COMMENT '粉丝人数',
	`url` VARCHAR(100) NOT NULL COMMENT '个人主页url',
	`name` VARCHAR(100) NOT NULL COMMENT '姓名',
	`answer_count` INT(9) NOT NULL COMMENT '答案总数',
	`is_advertiser` INT(1) NOT NULL ,
	`avatar_url` VARCHAR(100) NOT NULL COMMENT '头像url',
	`Is_following` INT(1) NOT NULL ,
	`is_org` INT(1) NOT NULL COMMENT '是否公司',
	`headline` VARCHAR(200) NOT NULL COMMENT '一句话简介',
	`badge` VARCHAR(100) NOT NULL,
	`user_id` VARCHAR(100) NOT NULL COMMENT '用户ID',
	`articles_count` INT(9) NOT NULL COMMENT '文章总数',
	PRIMARY KEY (`leader_url_token`)
)
COLLATE='utf8_general_ci'
ENGINE=MyISAM
;
