'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileSearch, CheckCircle2, AlertCircle, HelpCircle, XCircle } from 'lucide-react';
import { getMatchStatusColor, getMatchStatusLabel, getPriorityColor, getPriorityLabel } from '@/lib/utils';
import type { RequirementMatch } from '@/lib/types';

interface EvidenceMapProps {
  matches: RequirementMatch[];
}

export function EvidenceMap({ matches }: EvidenceMapProps) {
  const [filter, setFilter] = useState<string>('all');

  const filteredMatches = matches.filter((m) => {
    if (filter === 'all') return true;
    if (filter === 'strong') return m.status === 'strong_match';
    if (filter === 'partial') return m.status === 'partial_match';
    if (filter === 'weak') return m.status === 'weak_evidence';
    if (filter === 'missing') return m.status === 'missing';
    return true;
  });

  return (
    <Card className="border border-slate-200 shadow-sm">
      <CardHeader className="pb-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <CardTitle className="text-lg font-bold flex items-center gap-2">
            <FileSearch className="h-5 w-5 text-indigo-600" />
            Bản Đồ Bằng Chứng (Evidence Mapping)
          </CardTitle>
          <Tabs value={filter} onValueChange={setFilter} className="w-auto">
            <TabsList className="grid grid-cols-5 h-8 text-xs">
              <TabsTrigger value="all">Tất cả ({matches.length})</TabsTrigger>
              <TabsTrigger value="strong">
                Strong ({matches.filter((m) => m.status === 'strong_match').length})
              </TabsTrigger>
              <TabsTrigger value="partial">
                Partial ({matches.filter((m) => m.status === 'partial_match').length})
              </TabsTrigger>
              <TabsTrigger value="weak">
                Weak ({matches.filter((m) => m.status === 'weak_evidence').length})
              </TabsTrigger>
              <TabsTrigger value="missing">
                Missing ({matches.filter((m) => m.status === 'missing').length})
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {filteredMatches.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-8">
            Không có yêu cầu nào trong danh mục này.
          </p>
        ) : (
          filteredMatches.map((m, index) => (
            <div
              key={index}
              className="p-4 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-all shadow-xs"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-slate-900">
                    {m.requirement}
                  </span>
                  <Badge variant="secondary" className="text-[10px] uppercase font-bold text-slate-500">
                    {m.requirement_importance}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={`text-[10px] font-bold ${getPriorityColor(m.priority)}`}
                  >
                    {getPriorityLabel(m.priority)}
                  </Badge>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${getMatchStatusColor(
                      m.status
                    )}`}
                  >
                    {getMatchStatusLabel(m.status)}
                  </span>
                </div>
              </div>

              {/* Recommendation */}
              {m.recommendation && (
                <div className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded border border-slate-100 mb-2">
                  <span className="font-semibold text-slate-800">Khuyến nghị: </span>
                  {m.recommendation}
                </div>
              )}

              {/* Evidence list */}
              {m.evidence && m.evidence.length > 0 ? (
                <div className="space-y-1.5 mt-2">
                  <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Bằng chứng trích xuất từ CV:
                  </span>
                  {m.evidence.map((ev, evIdx) => (
                    <div
                      key={evIdx}
                      className="text-xs pl-3 border-l-2 border-indigo-400 bg-indigo-50/30 p-2 rounded-r"
                    >
                      <p className="text-slate-800 italic font-mono text-[11px]">
                        &ldquo;{ev.source_text}&rdquo;
                      </p>
                      <div className="flex justify-between items-center text-[10px] text-slate-500 mt-1">
                        <span>Phần: <strong className="text-slate-700">{ev.source_section}</strong></span>
                        <span>{ev.explanation}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic mt-1">
                  Không tìm thấy bằng chứng liên quan trong CV gốc.
                </p>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
