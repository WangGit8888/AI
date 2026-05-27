package com.example.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.example.entity.BidSectionDailyReport;
import com.example.service.BidSectionDailyReportService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/report")
@Tag(name = "标段每日填报", description = "填报记录的增删改查接口")
public class BidSectionDailyReportController {

    @Autowired
    private BidSectionDailyReportService service;

    @GetMapping
    @Operation(summary = "查询填报列表")
    public List<BidSectionDailyReport> list() {
        return service.list();
    }

    @GetMapping("/{id}")
    @Operation(summary = "按ID查询填报记录")
    public BidSectionDailyReport getById(@PathVariable @Parameter(description = "记录ID") Long id) {
        return service.getById(id);
    }

    @PostMapping
    @Operation(summary = "新增填报记录")
    public boolean save(@RequestBody BidSectionDailyReport entity) {
        return service.save(entity);
    }

    @PutMapping("/{id}")
    @Operation(summary = "修改填报记录")
    public boolean update(@PathVariable @Parameter(description = "记录ID") Long id,
                          @RequestBody BidSectionDailyReport entity) {
        entity.setId(id);
        return service.updateById(entity);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "删除填报记录")
    public boolean delete(@PathVariable @Parameter(description = "记录ID") Long id) {
        return service.removeById(id);
    }

    @GetMapping("/section/{sectionId}")
    @Operation(summary = "按标段ID查询填报记录")
    public List<BidSectionDailyReport> listBySection(
            @PathVariable @Parameter(description = "标段ID") Long sectionId) {
        QueryWrapper<BidSectionDailyReport> qw = new QueryWrapper<>();
        qw.eq("section_id", sectionId);
        qw.orderByDesc("create_date");
        return service.list(qw);
    }
}
