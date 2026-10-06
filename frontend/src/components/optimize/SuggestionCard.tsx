'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Check, X, ArrowRight, ShieldCheck, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';
import { getPriorityColor, getPriorityLabel } from '@/lib/utils';
import type { CVSuggestion } from '@/lib/types';

interface SuggestionCardProps {
  suggestion: CVSuggestion;
  currentIndex: number;
  totalCount: number;
  onAccept: () => void;
  onReject: () => void;
  onPrev: () => void;
  onNext: () => void;
}

export function SuggestionCard({
  suggestion,
  currentIndex,
  totalCount,
  onAccept,
  onReject,
  onPrev,
  onNext,
}: SuggestionCardProps) {
  const isAccepted = suggestion.accepted === true;
  const isRejected = suggestion.accepted === false;

  return (
    <Card className="border border-slate-200 shadow-md">
      <CardHeader className="pb-3 border-b border-slate-100 bg-slate-50/50">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-500" />
            <CardTitle className="text-base font-bold text-slate-900">
              Gợi ý #{currentIndex + 1} / {totalCount} — Phần: {suggestion.section}
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={`text-xs font-bold border ${getPriorityColor(suggestion.priority)}`}
            >
              {getPriorityLabel(suggestion.priority)}
            </Badge>
            {isAccepted && (
              <Badge className="bg-emerald-600 text-white text-xs">
                Đã chấp nhận ✓
              </Badge>
            )}
            {isRejected && (
              <Badge variant="destructive" className="text-xs">
                Đã bỏ qua ✗
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Before & After comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Before */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
              Nội dung gốc (Trước)
            </span>
            <div className="p-4 rounded-lg bg-rose-50/30 border border-rose-100 text-xs font-mono text-slate-800 leading-relaxed min-h-[120px]">
              {suggestion.original_text}
            </div>
          </div>

          {/* After */}
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
              Nội dung tối ưu (Sau)
            </span>
            <div className="p-4 rounded-lg bg-emerald-50/40 border border-emerald-200 text-xs font-mono text-slate-900 leading-relaxed min-h-[120px] font-medium">
              {suggestion.suggested_text}
            </div>
          </div>
        </div>

        {/* Change explanation & grounding */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 p-4 bg-slate-50 rounded-lg border border-slate-100 text-xs">
          <div>
            <span className="font-bold text-slate-700 block mb-1">Thay đổi gì?</span>
            <p className="text-slate-600 leading-relaxed">{suggestion.change_description}</p>
          </div>
          <div>
            <span className="font-bold text-slate-700 block mb-1">Tại sao thay đổi?</span>
            <p className="text-slate-600 leading-relaxed">{suggestion.reason}</p>
            <span className="text-[11px] text-blue-600 mt-1 block">
              Yêu cầu JD: <strong>{suggestion.jd_requirement}</strong>
            </span>
          </div>
          <div>
            <span className="font-bold text-slate-700 flex items-center gap-1 mb-1">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
              Bằng chứng từ CV gốc:
            </span>
            <p className="text-slate-600 italic leading-relaxed">
              &ldquo;{suggestion.evidence}&rdquo;
            </p>
          </div>
        </div>

        {/* Action buttons & pagination */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          {/* Nav buttons */}
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={currentIndex === 0}
              onClick={onPrev}
            >
              <ChevronLeft className="h-4 w-4 mr-1" /> Trước
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={currentIndex >= totalCount - 1}
              onClick={onNext}
            >
              Tiếp <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>

          {/* Accept / Reject */}
          <div className="flex items-center gap-3">
            <Button
              type="button"
              variant={isRejected ? 'destructive' : 'outline'}
              className="text-xs"
              onClick={onReject}
            >
              <X className="h-4 w-4 mr-1.5" /> Bỏ qua gợi ý
            </Button>
            <Button
              type="button"
              className={`text-xs ${
                isAccepted ? 'bg-emerald-600 hover:bg-emerald-700' : 'bg-blue-600 hover:bg-blue-700'
              }`}
              onClick={onAccept}
            >
              <Check className="h-4 w-4 mr-1.5" /> Chấp nhận gợi ý
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
