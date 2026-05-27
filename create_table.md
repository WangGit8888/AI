生成通用建表语句
逻辑:将我发你的的汉字字段起合适的列名并选合适的属性类型,需要带上下面的共有字段

1、以下是所有表的都有的字段(若无特殊声明)
    id 主键 BIGINT
    delete_flag 删除标记 0未删除；1已删除 INT
    create_by 创建人 bigint(20)
    create_date 创建时间 datetime
    update_by 修改人 bigint(20)
    update_date 修改时间 datetimeINTBIG


生成 表名.md 文件