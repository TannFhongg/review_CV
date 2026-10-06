'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Info, Award } from 'lucide-react';
import type { AlignmentScore } from '@/lib/types';

interface AlignmentScoreCardProps {
  score: AlignmentScore;
}

export function AlignmentScoreCard({ score }: AlignmentScoreCardProps) {
  const getScoreColor = (val: number) => {
    if (val >= 80) return 'text-emerald-600';
    if (val >= 60) return 'text-amber-600';
    return 'text-rose-600';
  };

  const dimensions = [
    { label: 'Kỹ năng kỹ thuật (Technical)', value: score.technical_skills, weight: '30%' },
    { label: 'Kinh nghiệm thực tế (Experience)', value: score.experience_relevance, weight: '25%' },
    { label: 'Trách nhiệm công việc (Responsibilities)', value: score.responsibilities_alignment, weight: '20%' },
    { label: 'Phủ từ khóa (Keyword Coverage)', value: score.keyword_coverage, weight: '10%' },
    { label: 'Học vấn & Bằng cấp (Education)', value: score.education_alignment, weight: '10%' },
    { label: 'Cấu trúc & Độ rõ ràng (Clarity)', value: score.cv_clarity, weight: '5%' },
  ];

  return (
    <Card className="border border-slate-200 shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <Award className="h-5 w-5 text-blue-600" />
            CV ↔ JD Alignment Score
          </CardTitle>
          <span className="text-xs text-slate-400 font-normal">
            Không phỏng đoán cơ hội phỏng vấn • Tính toán minh bạch
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          {/* Main Radial Score */}
          <div className="flex flex-col items-center justify-center p-6 bg-slate-50 rounded-xl border border-slate-100 text-center">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Độ tương thích tổng thể
            </span>
            <div className={`text-5xl font-black my-2 ${getScoreColor(score.overall)}`}>
              {score.overall}
              <span className="text-xl text-slate-400 font-normal">/100</span>
            </div>
            <p className="text-xs text-slate-500 mt-1 max-w-[200px]">
              {score.overall >= 80
                ? 'Độ tương thích rất cao với vị trí tuyển dụng'
                : score.overall >= 60
                ? 'Tương thích khá tốt, cần bổ sung một số điểm nhấn'
                : 'Cần tái cấu trúc và bổ sung nhiều bằng chứng trọng yếu'}
            </p>
          </div>

          {/* Breakdown bars */}
          <div className="md:col-span-2 space-y-3">
            {dimensions.map((dim, index) => (
              <div key={index} className="space-y-1">
                <div className="flex justify-between text-xs font-medium text-slate-700">
                  <span>
                    {dim.label} <span className="text-slate-400 font-normal">({dim.weight})</span>
                  </span>
                  <span className={`font-bold ${getScoreColor(dim.value)}`}>
                    {dim.value}/100
                  </span>
                </div>
                <Progress value={dim.value} className="h-2" />
              </div>
            ))}
          </div>
        </div>

        {/* Methodology note */}
        {score.methodology_notes && (
          <div className="mt-4 p-3 bg-blue-50/60 rounded-lg text-xs text-blue-900 border border-blue-100 flex gap-2">
            <Info className="h-4 w-4 text-blue-600 shrink-0 mt-0.5" />
            <div className="whitespace-pre-line leading-relaxed">
              {score.methodology_notes}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
