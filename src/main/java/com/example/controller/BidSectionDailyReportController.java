package com.example.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.example.entity.BidSectionDailyReport;
import com.example.service.BidSectionDailyReportService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/report")
public class BidSectionDailyReportController {

    @Autowired
    private BidSectionDailyReportService service;

    @GetMapping
    public List<BidSectionDailyReport> list() {
        return service.list();
    }

    @GetMapping("/{id}")
    public BidSectionDailyReport getById(@PathVariable Long id) {
        return service.getById(id);
    }

    @PostMapping
    public boolean save(@RequestBody BidSectionDailyReport entity) {
        return service.save(entity);
    }

    @PutMapping("/{id}")
    public boolean update(@PathVariable Long id, @RequestBody BidSectionDailyReport entity) {
        entity.setId(id);
        return service.updateById(entity);
    }

    @DeleteMapping("/{id}")
    public boolean delete(@PathVariable Long id) {
        return service.removeById(id);
    }

    @GetMapping("/section/{sectionId}")
    public List<BidSectionDailyReport> listBySection(@PathVariable Long sectionId) {
        QueryWrapper<BidSectionDailyReport> qw = new QueryWrapper<>();
        qw.eq("section_id", sectionId);
        qw.orderByDesc("create_date");
        return service.list(qw);
    }
}
