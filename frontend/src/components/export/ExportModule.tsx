'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Copy, Check, FileDown, Shield, TrendingUp } from 'lucide-react';
import type { AnalysisResult } from '@/lib/types';

interface ExportModuleProps {
  result: AnalysisResult;
}

export function ExportModule({ result }: ExportModuleProps) {
  const [copied, setCopied] = useState(false);

  // Generate markdown report on client side if API is not invoked
  const generateMarkdown = () => {
    const lines: string[] = [];
    lines.push(`# BÁO CÁO TỐI ƯU HÓA CV CHO VỊ TRÍ: ${result.structured_jd.job_title}`);
    lines.push(`- **Ứng viên:** ${result.structured_cv.name}`);
    lines.push(`- **Tổng điểm tương thích:** ${result.alignment_score.overall}/100`);
    lines.push(`- **Thời gian phân tích:** ${new Date(result.analyzed_at).toLocaleString('vi-VN')}`);
    lines.push('');
    lines.push('## 1. ĐIỂM SỐ CHI TIẾT');
    lines.push(`- Kỹ năng kỹ thuật: ${result.alignment_score.technical_skills}/100`);
    lines.push(`- Kinh nghiệm liên quan: ${result.alignment_score.experience_relevance}/100`);
    lines.push(`- Trách nhiệm công việc: ${result.alignment_score.responsibilities_alignment}/100`);
    lines.push(`- Phủ từ khóa: ${result.alignment_score.keyword_coverage}/100`);
    lines.push(`- Học vấn: ${result.alignment_score.education_alignment}/100`);
    lines.push(`- Độ rõ ràng: ${result.alignment_score.cv_clarity}/100`);
    lines.push('');
    lines.push('## 2. TOP CẢI THIỆN ĐẦU TIÊN');
    result.top_recommendations.forEach((r, i) => {
      lines.push(`${i + 1}. **${r.requirement}** [${r.priority}]`);
      lines.push(`   Khuyến nghị: ${r.recommendation}`);
    });
    lines.push('');
    lines.push('## 3. GỢI Ý ĐÃ CHẤP NHẬN');
    const accepted = result.suggestions.filter((s) => s.accepted === true);
    if (accepted.length === 0) {
      lines.push('*Chưa có gợi ý nào được đánh dấu chấp nhận.*');
    } else {
      accepted.forEach((s, i) => {
        lines.push(`### ${i + 1}. Phần ${s.section} (Yêu cầu: ${s.jd_requirement})`);
        lines.push('**TRƯỚC:**');
        lines.push(`> ${s.original_text}`);
        lines.push('**SAU:**');
        lines.push(`> ${s.suggested_text}`);
        lines.push(`- Thay đổi: ${s.change_description}`);
        lines.push(`- Bằng chứng: ${s.evidence}`);
        lines.push('');
      });
    }

    return lines.join('\n');
  };

  const handleDownloadMarkdown = () => {
    const md = generateMarkdown();
    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `CV_Optimization_Report_${result.structured_cv.name.replace(/\s+/g, '_')}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `cv_copilot_analysis.json`);
    downloadAnchor.click();
  };

  const handleCopyClipboard = async () => {
    const md = generateMarkdown();
    await navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Projected score improvement if accepted suggestions applied
  const acceptedCount = result.suggestions.filter((s) => s.accepted === true).length;
  const projectedBoost = Math.min(15, acceptedCount * 3);
  const projectedOverall = Math.min(100, result.alignment_score.overall + projectedBoost);

  return (
    <div className="space-y-6">
      {/* Before / After Projected Comparison Table */}
      <Card className="border border-slate-200 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-emerald-600" />
            Dự Phóng Điểm Tương Thích (Before vs After)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50 text-slate-600">
                  <th className="py-2.5 px-3 font-semibold">Chỉ số đánh giá</th>
                  <th className="py-2.5 px-3 font-semibold text-center">Trước tối ưu (Gốc)</th>
                  <th className="py-2.5 px-3 font-semibold text-center">Sau tối ưu (Dự phóng)</th>
                  <th className="py-2.5 px-3 font-semibold text-right">Tăng trưởng</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="py-2.5 px-3 font-bold text-slate-900">Tổng điểm tương thích (Overall)</td>
                  <td className="py-2.5 px-3 text-center font-bold text-slate-600">{result.alignment_score.overall}/100</td>
                  <td className="py-2.5 px-3 text-center font-bold text-emerald-600">{projectedOverall}/100</td>
                  <td className="py-2.5 px-3 text-right font-bold text-emerald-600">+{projectedBoost}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-700">Kỹ năng kỹ thuật</td>
                  <td className="py-2.5 px-3 text-center text-slate-600">{result.alignment_score.technical_skills}</td>
                  <td className="py-2.5 px-3 text-center text-emerald-600">{Math.min(100, result.alignment_score.technical_skills + projectedBoost)}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-600">+{projectedBoost}</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 text-slate-700">Độ khớp từ khóa ATS</td>
                  <td className="py-2.5 px-3 text-center text-slate-600">{result.alignment_score.keyword_coverage}</td>
                  <td className="py-2.5 px-3 text-center text-emerald-600">{Math.min(100, result.alignment_score.keyword_coverage + Math.round(projectedBoost * 1.2))}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-600">+{Math.round(projectedBoost * 1.2)}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-slate-400 mt-2 italic">
            * Điểm dự phóng phản ánh mức cải thiện khi đưa các từ khóa và nội dung đã chấp nhận ({acceptedCount}/{result.suggestions.length} gợi ý) vào CV.
          </p>
        </CardContent>
      </Card>

      {/* Export Actions */}
      <Card className="border border-slate-200 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <Download className="h-5 w-5 text-blue-600" />
            Tải Xuất Dữ Liệu & Báo Cáo
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Button
              type="button"
              variant="outline"
              className="flex items-center gap-2 h-11"
              onClick={handleDownloadMarkdown}
            >
              <FileDown className="h-4 w-4 text-indigo-600" />
              <span>Tải Báo cáo Markdown</span>
            </Button>
            <Button
              type="button"
              variant="outline"
              className="flex items-center gap-2 h-11"
              onClick={handleDownloadJSON}
            >
              <Download className="h-4 w-4 text-emerald-600" />
              <span>Tải Dữ liệu JSON</span>
            </Button>
            <Button
              type="button"
              variant="outline"
              className="flex items-center gap-2 h-11"
              onClick={handleCopyClipboard}
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4 text-emerald-600" />
                  <span>Đã sao chép!</span>
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4 text-slate-600" />
                  <span>Sao chép vào Clipboard</span>
                </>
              )}
            </Button>
          </div>

          <div className="mt-4 p-3 bg-slate-50 rounded-lg text-xs text-slate-500 flex items-center gap-2 border border-slate-100">
            <Shield className="h-4 w-4 text-emerald-600 shrink-0" />
            <span>
              Tất cả dữ liệu phân tích chỉ lưu trong phiên trình duyệt của bạn và tự động giải phóng khi đóng trang.
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
