package com.example.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.entity.BidSectionDailyReport;
import com.example.mapper.BidSectionDailyReportMapper;
import com.example.service.BidSectionDailyReportService;
import org.springframework.stereotype.Service;

@Service
public class BidSectionDailyReportServiceImpl
        extends ServiceImpl<BidSectionDailyReportMapper, BidSectionDailyReport>
        implements BidSectionDailyReportService {
}
