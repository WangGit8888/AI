```sql
CREATE TABLE bid_section_daily_report (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT  COMMENT '主键ID',
    section_name    VARCHAR(128)  NOT NULL             COMMENT '标段名称',
    section_id      BIGINT        NOT NULL             COMMENT '标段ID',
    reporter_id     BIGINT        NOT NULL             COMMENT '填报人ID',
    reporter_phone  VARCHAR(20)   NOT NULL DEFAULT ''  COMMENT '填报人电话',
    weather         VARCHAR(32)   NOT NULL DEFAULT ''  COMMENT '天气',
    temp_low        DECIMAL(4,1)  NOT NULL DEFAULT 0   COMMENT '低温温度(℃)',
    temp_high       DECIMAL(4,1)  NOT NULL DEFAULT 0   COMMENT '高温温度(℃)',
    delete_flag     INT           NOT NULL DEFAULT 0   COMMENT '删除标记 0未删除 1已删除',
    create_by       BIGINT(20)    DEFAULT NULL         COMMENT '创建人',
    create_date     DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_by       BIGINT(20)    DEFAULT NULL         COMMENT '修改人',
    update_date     DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    INDEX idx_section_id (section_id),
    INDEX idx_reporter_id (reporter_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标段每日填报记录';
```
