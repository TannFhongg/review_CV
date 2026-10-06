'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Target, ArrowRight, AlertTriangle } from 'lucide-react';
import { getPriorityColor, getPriorityLabel } from '@/lib/utils';
import type { RequirementMatch } from '@/lib/types';

interface TopRecommendationsListProps {
  recommendations: RequirementMatch[];
  onGoToOptimize?: () => void;
}

export function TopRecommendationsList({
  recommendations,
  onGoToOptimize,
}: TopRecommendationsListProps) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <Card className="border border-slate-200">
        <CardContent className="p-6 text-center text-slate-500">
          Không có khuyến nghị quan trọng nào cần khắc phục. CV đã rất phù hợp!
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border border-slate-200 shadow-sm">
      <CardHeader className="pb-3 flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Target className="h-5 w-5 text-rose-600" />
            Top 5 Điểm Cần Cải Thiện Đầu Tiên
          </CardTitle>
          <p className="text-xs text-slate-500 mt-1">
            Những điều chỉnh mang lại tác động lớn nhất tới độ tương thích của CV
          </p>
        </div>
        {onGoToOptimize && (
          <button
            onClick={onGoToOptimize}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            Tới màn hình tối ưu <ArrowRight className="h-3.5 w-3.5" />
          </button>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {recommendations.slice(0, 5).map((rec, index) => (
          <div
            key={index}
            className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/70 hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-start justify-between gap-3 mb-1.5">
              <div className="flex items-center gap-2">
                <span className="flex items-center justify-center w-5 h-5 rounded-full bg-slate-200 text-slate-700 text-xs font-bold shrink-0">
                  {index + 1}
                </span>
                <span className="font-semibold text-sm text-slate-900">
                  {rec.requirement}
                </span>
              </div>
              <Badge
                variant="outline"
                className={`text-[10px] font-bold px-2 py-0.5 border ${getPriorityColor(rec.priority)}`}
              >
                {getPriorityLabel(rec.priority)}
              </Badge>
            </div>

            <p className="text-xs text-slate-700 ml-7 leading-relaxed font-medium">
              💡 {rec.recommendation}
            </p>

            {rec.status === 'missing' && (
              <div className="ml-7 mt-2 flex items-center gap-1.5 text-[11px] text-amber-700 bg-amber-50/80 px-2.5 py-1 rounded border border-amber-200/60">
                <AlertTriangle className="h-3 w-3 shrink-0" />
                <span>
                  Chính sách không bịa đặt: Chỉ thêm vào CV nếu bạn thực sự có kinh nghiệm này.
                </span>
              </div>
            )}

            {rec.evidence && rec.evidence.length > 0 && (
              <div className="ml-7 mt-2 text-[11px] text-slate-500 bg-white p-2 rounded border border-slate-200/60">
                <span className="font-semibold text-slate-700">Bằng chứng hiện tại: </span>
                <span className="italic">
                  &ldquo;{rec.evidence[0].source_text}&rdquo;
                </span>{' '}
                ({rec.evidence[0].source_section})
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
