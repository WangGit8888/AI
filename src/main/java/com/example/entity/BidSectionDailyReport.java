package com.example.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;

import java.math.BigDecimal;
import java.util.Date;

@TableName("bid_section_daily_report")
public class BidSectionDailyReport {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String sectionName;
    private Long sectionId;
    private Long reporterId;
    private String reporterPhone;
    private String weather;
    private BigDecimal tempLow;
    private BigDecimal tempHigh;
    private Integer deleteFlag;

    @TableField("create_by")
    private Long createBy;

    @TableField("create_date")
    private Date createDate;

    @TableField("update_by")
    private Long updateBy;

    @TableField("update_date")
    private Date updateDate;

    // getters and setters

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getSectionName() { return sectionName; }
    public void setSectionName(String sectionName) { this.sectionName = sectionName; }

    public Long getSectionId() { return sectionId; }
    public void setSectionId(Long sectionId) { this.sectionId = sectionId; }

    public Long getReporterId() { return reporterId; }
    public void setReporterId(Long reporterId) { this.reporterId = reporterId; }

    public String getReporterPhone() { return reporterPhone; }
    public void setReporterPhone(String reporterPhone) { this.reporterPhone = reporterPhone; }

    public String getWeather() { return weather; }
    public void setWeather(String weather) { this.weather = weather; }

    public BigDecimal getTempLow() { return tempLow; }
    public void setTempLow(BigDecimal tempLow) { this.tempLow = tempLow; }

    public BigDecimal getTempHigh() { return tempHigh; }
    public void setTempHigh(BigDecimal tempHigh) { this.tempHigh = tempHigh; }

    public Integer getDeleteFlag() { return deleteFlag; }
    public void setDeleteFlag(Integer deleteFlag) { this.deleteFlag = deleteFlag; }

    public Long getCreateBy() { return createBy; }
    public void setCreateBy(Long createBy) { this.createBy = createBy; }

    public Date getCreateDate() { return createDate; }
    public void setCreateDate(Date createDate) { this.createDate = createDate; }

    public Long getUpdateBy() { return updateBy; }
    public void setUpdateBy(Long updateBy) { this.updateBy = updateBy; }

    public Date getUpdateDate() { return updateDate; }
    public void setUpdateDate(Date updateDate) { this.updateDate = updateDate; }
}
