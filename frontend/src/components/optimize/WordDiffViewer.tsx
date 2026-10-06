'use client';

import React, { useState } from 'react';
import { diffWordsWithSpace } from 'diff';
import { Copy, Check, Eye, Columns } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface WordDiffViewerProps {
  originalText: string;
  suggestedText: string;
}

export function WordDiffViewer({ originalText, suggestedText }: WordDiffViewerProps) {
  const [viewMode, setViewMode] = useState<'inline' | 'split'>('inline');
  const [copied, setCopied] = useState<boolean>(false);

  // Compute diff parts
  const diffParts = diffWordsWithSpace(originalText || '', suggestedText || '');

  const handleCopy = async () => {
    await navigator.clipboard.writeText(suggestedText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-3">
      {/* View Mode Controls & Copy Button */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
        <div className="flex items-center gap-1.5 bg-slate-100/80 p-0.5 rounded-lg text-xs">
          <button
            type="button"
            onClick={() => setViewMode('inline')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md font-medium transition-all ${
              viewMode === 'inline'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Eye className="h-3.5 w-3.5" />
            <span>Trực quan (Track Changes)</span>
          </button>
          <button
            type="button"
            onClick={() => setViewMode('split')}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-md font-medium transition-all ${
              viewMode === 'split'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Columns className="h-3.5 w-3.5" />
            <span>Song song (Side-by-Side)</span>
          </button>
        </div>

        {/* Copy 1-Click Button */}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleCopy}
          className="text-xs h-7 px-2.5 text-slate-700 hover:text-blue-700 hover:border-blue-300"
        >
          {copied ? (
            <>
              <Check className="h-3.5 w-3.5 mr-1 text-emerald-600" />
              <span className="text-emerald-700 font-semibold">Đã sao chép!</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5 mr-1 text-slate-500" />
              <span>Sao chép câu tối ưu</span>
            </>
          )}
        </Button>
      </div>

      {/* Legend Guide */}
      <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-500 bg-slate-50/60 px-3 py-1.5 rounded-md border border-slate-100">
        <span className="font-semibold text-slate-600">Chú giải:</span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 bg-emerald-200 border border-emerald-400 rounded-xs"></span>
          <strong className="text-emerald-800">Màu xanh:</strong> Từ khóa mới được bổ sung
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 bg-rose-200 border border-rose-400 rounded-xs"></span>
          <strong className="text-rose-800">Màu đỏ gạch ngang:</strong> Từ cũ được lược bỏ / thay thế
        </span>
      </div>

      {/* Main Diff Content */}
      {viewMode === 'inline' ? (
        /* INLINE UNIFIED DIFF (Track Changes) */
        <div className="p-4 rounded-lg bg-white border border-slate-200 text-xs font-mono leading-relaxed min-h-[140px] whitespace-pre-wrap shadow-xs">
          {diffParts.map((part, idx) => {
            if (part.added) {
              return (
                <mark
                  key={idx}
                  className="bg-emerald-100 text-emerald-900 font-semibold px-1 py-0.5 rounded border-b-2 border-emerald-500 not-italic no-underline"
                >
                  {part.value}
                </mark>
              );
            }
            if (part.removed) {
              return (
                <del
                  key={idx}
                  className="bg-rose-100/90 text-rose-800 line-through px-1 py-0.5 rounded opacity-80 decoration-rose-600 decoration-1"
                >
                  {part.value}
                </del>
              );
            }
            return <span key={idx} className="text-slate-800">{part.value}</span>;
          })}
        </div>
      ) : (
        /* SPLIT SIDE-BY-SIDE DIFF */
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Left: Original with highlighted removals */}
          <div className="space-y-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              Nội dung gốc (Trước)
            </span>
            <div className="p-3.5 rounded-lg bg-rose-50/20 border border-rose-200/60 text-xs font-mono text-slate-800 leading-relaxed min-h-[140px] whitespace-pre-wrap shadow-xs">
              {diffParts.map((part, idx) => {
                if (part.removed) {
                  return (
                    <mark
                      key={idx}
                      className="bg-rose-200 text-rose-900 line-through px-1 py-0.5 rounded font-semibold not-italic"
                    >
                      {part.value}
                    </mark>
                  );
                }
                if (part.added) {
                  return null; // hide added in the left original view
                }
                return <span key={idx}>{part.value}</span>;
              })}
            </div>
          </div>

          {/* Right: Suggested with highlighted additions */}
          <div className="space-y-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Nội dung tối ưu (Sau)
            </span>
            <div className="p-3.5 rounded-lg bg-emerald-50/30 border border-emerald-300 text-xs font-mono text-slate-900 leading-relaxed min-h-[140px] whitespace-pre-wrap shadow-xs font-medium">
              {diffParts.map((part, idx) => {
                if (part.added) {
                  return (
                    <mark
                      key={idx}
                      className="bg-emerald-200 text-emerald-950 px-1 py-0.5 rounded font-bold border-b-2 border-emerald-600 not-italic"
                    >
                      {part.value}
                    </mark>
                  );
                }
                if (part.removed) {
                  return null; // hide removed in the right suggested view
                }
                return <span key={idx}>{part.value}</span>;
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
