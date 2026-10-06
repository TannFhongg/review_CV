'use client';

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle2, AlertCircle, HelpCircle, XCircle } from 'lucide-react';

interface MatchSummaryCardsProps {
  strongCount: number;
  partialCount: number;
  weakCount: number;
  missingCount: number;
  activeFilter?: string;
  onFilterChange?: (filter: string) => void;
}

export function MatchSummaryCards({
  strongCount,
  partialCount,
  weakCount,
  missingCount,
  activeFilter,
  onFilterChange,
}: MatchSummaryCardsProps) {
  const cards = [
    {
      id: 'strong',
      title: 'Phù hợp mạnh',
      count: strongCount,
      icon: CheckCircle2,
      color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
      activeRing: 'ring-2 ring-emerald-500',
      desc: 'Bằng chứng rõ ràng & trực tiếp',
    },
    {
      id: 'partial',
      title: 'Phù hợp một phần',
      count: partialCount,
      icon: AlertCircle,
      color: 'text-amber-700 bg-amber-50 border-amber-200',
      activeRing: 'ring-2 ring-amber-500',
      desc: 'Có kinh nghiệm liên quan',
    },
    {
      id: 'weak',
      title: 'Bằng chứng yếu',
      count: weakCount,
      icon: HelpCircle,
      color: 'text-orange-700 bg-orange-50 border-orange-200',
      activeRing: 'ring-2 ring-orange-500',
      desc: 'Đề cập mờ nhạt hoặc gián tiếp',
    },
    {
      id: 'missing',
      title: 'Còn thiếu',
      count: missingCount,
      icon: XCircle,
      color: 'text-rose-700 bg-rose-50 border-rose-200',
      activeRing: 'ring-2 ring-rose-500',
      desc: 'Chưa có thông tin trong CV',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {cards.map((c) => {
        const Icon = c.icon;
        const isSelected = activeFilter === c.id;
        return (
          <Card
            key={c.id}
            onClick={() => onFilterChange && onFilterChange(isSelected ? 'all' : c.id)}
            className={`cursor-pointer transition-all border ${c.color} ${
              isSelected ? c.activeRing : 'hover:shadow-sm'
            }`}
          >
            <CardContent className="p-4 flex flex-col justify-between h-full">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold">{c.title}</span>
                <Icon className="h-4 w-4" />
              </div>
              <div>
                <div className="text-3xl font-extrabold">{c.count}</div>
                <p className="text-[11px] opacity-80 mt-1">{c.desc}</p>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
