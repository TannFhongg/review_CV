'use client';

import React, { useState } from 'react';
import {
  FileText,
  Sparkles,
  Copy,
  Check,
  Download,
  Edit3,
  Eye,
  Loader2,
  Send,
  Building,
  User,
  ShieldCheck,
  RotateCcw,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { AnalysisResult, CoverLetterResponse } from '@/lib/types';
import { generateCoverLetter } from '@/lib/api';

interface CoverLetterGeneratorProps {
  result: AnalysisResult;
}

export function CoverLetterGenerator({ result }: CoverLetterGeneratorProps) {
  const [tone, setTone] = useState<'professional' | 'enthusiastic' | 'concise'>('professional');
  const [language, setLanguage] = useState<'vi' | 'en'>('vi');
  const [customNotes, setCustomNotes] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [coverLetter, setCoverLetter] = useState<CoverLetterResponse | null>(null);
  const [editableText, setEditableText] = useState<string>('');
  const [activeMode, setActiveMode] = useState<'preview' | 'edit'>('preview');
  const [copied, setCopied] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await generateCoverLetter({
        structured_jd: result.structured_jd,
        structured_cv: result.structured_cv,
        tone,
        language,
        custom_instructions: customNotes.trim() ? customNotes.trim() : null,
      });
      setCoverLetter(res);
      setEditableText(res.full_letter);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Không thể tạo Cover Letter. Vui lòng thử lại.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    const textToCopy = editableText || coverLetter?.full_letter || '';
    if (!textToCopy) return;
    await navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (format: 'txt' | 'md') => {
    const textToDownload = editableText || coverLetter?.full_letter || '';
    if (!textToDownload) return;

    const candidateSlug = (result.structured_cv.name || 'Candidate')
      .replace(/\s+/g, '_')
      .toLowerCase();
    const roleSlug = (result.structured_jd.job_title || 'Position')
      .replace(/\s+/g, '_')
      .toLowerCase();
    const filename = `Cover_Letter_${candidateSlug}_${roleSlug}.${format}`;

    const blob = new Blob([textToDownload], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Intro Header Card */}
      <Card className="border border-slate-200 shadow-sm bg-gradient-to-r from-blue-50/50 via-white to-indigo-50/40">
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <CardTitle className="text-lg font-bold text-slate-900">
                  Trình tạo Cover Letter theo Job Description
                </CardTitle>
                <p className="text-xs text-slate-500 mt-0.5">
                  Thư ứng tuyển được tạo riêng cho vị trí này, bám sát các dự án và kỹ năng thực tế từ CV của bạn.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs border-emerald-300 bg-emerald-50 text-emerald-800">
                <ShieldCheck className="h-3.5 w-3.5 mr-1 text-emerald-600" />
                Tuyệt đối không bịa đặt
              </Badge>
            </div>
          </div>
        </CardHeader>

        {/* Options & Configuration Form */}
        <CardContent className="pt-2 border-t border-slate-100">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Tone Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 block">
                Phong cách (Tone):
              </label>
              <div className="grid grid-cols-3 gap-1.5 bg-slate-100 p-1 rounded-lg text-xs">
                <button
                  type="button"
                  onClick={() => setTone('professional')}
                  className={`py-1.5 px-2 rounded-md font-medium text-center transition-all ${
                    tone === 'professional'
                      ? 'bg-white text-blue-700 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  👔 Chuẩn mực
                </button>
                <button
                  type="button"
                  onClick={() => setTone('enthusiastic')}
                  className={`py-1.5 px-2 rounded-md font-medium text-center transition-all ${
                    tone === 'enthusiastic'
                      ? 'bg-white text-blue-700 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  🚀 Nhiệt huyết
                </button>
                <button
                  type="button"
                  onClick={() => setTone('concise')}
                  className={`py-1.5 px-2 rounded-md font-medium text-center transition-all ${
                    tone === 'concise'
                      ? 'bg-white text-blue-700 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  ⚡ Súc tích
                </button>
              </div>
            </div>

            {/* Language Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 block">
                Ngôn ngữ thư:
              </label>
              <div className="grid grid-cols-2 gap-1.5 bg-slate-100 p-1 rounded-lg text-xs">
                <button
                  type="button"
                  onClick={() => setLanguage('vi')}
                  className={`py-1.5 px-2 rounded-md font-medium text-center transition-all ${
                    language === 'vi'
                      ? 'bg-white text-blue-700 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  🇻🇳 Tiếng Việt
                </button>
                <button
                  type="button"
                  onClick={() => setLanguage('en')}
                  className={`py-1.5 px-2 rounded-md font-medium text-center transition-all ${
                    language === 'en'
                      ? 'bg-white text-blue-700 shadow-xs'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  🇬🇧 English
                </button>
              </div>
            </div>

            {/* Generate Action Button */}
            <div className="space-y-1.5 flex flex-col justify-end">
              <Button
                type="button"
                className="w-full h-9 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs shadow-xs"
                disabled={isLoading}
                onClick={handleGenerate}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Đang viết Cover Letter...
                  </>
                ) : coverLetter ? (
                  <>
                    <RotateCcw className="h-3.5 w-3.5 mr-1.5" />
                    Tạo lại với tùy chọn mới
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5 mr-1.5" />
                    Tạo Cover Letter ngay
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Optional notes input */}
          <div className="mt-3 pt-3 border-t border-slate-100">
            <input
              type="text"
              value={customNotes}
              onChange={(e) => setCustomNotes(e.target.value)}
              placeholder="Ghi chú thêm (Tùy chọn: ví dụ: Nhấn mạnh kinh nghiệm Qt và Embedded Linux; sẵn sàng phỏng vấn sớm)..."
              className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:outline-hidden focus:border-blue-400 bg-white placeholder:text-slate-400"
            />
          </div>
        </CardContent>
      </Card>

      {/* Error alert */}
      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs">
          ⚠️ {error}
        </div>
      )}

      {/* When Cover Letter is NOT yet generated */}
      {!coverLetter && !isLoading && (
        <Card className="border border-dashed border-slate-200 text-center py-12 px-4 bg-white">
          <div className="max-w-md mx-auto space-y-4">
            <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 mx-auto flex items-center justify-center">
              <Send className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-800">
                Sẵn sàng tạo thư ứng tuyển thuyết phục
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Hệ thống sẽ tổng hợp các điểm mạnh, công nghệ và dự án tương thích nhất trong CV của bạn với vị trí{' '}
                <strong className="text-slate-700">{result.structured_jd.job_title}</strong> để tạo nên một lá thư chỉn chu và trung thực.
              </p>
            </div>
            <Button
              type="button"
              onClick={handleGenerate}
              className="bg-blue-600 hover:bg-blue-700 text-xs px-6"
            >
              <Sparkles className="h-3.5 w-3.5 mr-2" /> Bắt đầu tạo Cover Letter
            </Button>
          </div>
        </Card>
      )}

      {/* When Loading */}
      {isLoading && (
        <Card className="border border-slate-200 p-12 text-center bg-white">
          <Loader2 className="h-8 w-8 text-blue-600 animate-spin mx-auto mb-3" />
          <h4 className="text-sm font-bold text-slate-800">AI đang phân tích và viết thư ứng tuyển...</h4>
          <p className="text-xs text-slate-500 mt-1">
            Đang trích xuất bằng chứng từ CV và liên kết với các yêu cầu cốt lõi trong JD
          </p>
        </Card>
      )}

      {/* When Cover Letter IS generated */}
      {coverLetter && !isLoading && (
        <div className="space-y-4">
          {/* Metadata & Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-3 rounded-xl border border-slate-200 shadow-xs">
            {/* View / Edit Mode Switch */}
            <div className="flex items-center gap-1.5 bg-slate-100 p-0.5 rounded-lg text-xs">
              <button
                type="button"
                onClick={() => setActiveMode('preview')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md font-medium transition-all ${
                  activeMode === 'preview'
                    ? 'bg-white text-blue-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Eye className="h-3.5 w-3.5" />
                <span>Xem trước (Trang thư)</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveMode('edit')}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-md font-medium transition-all ${
                  activeMode === 'edit'
                    ? 'bg-white text-blue-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Edit3 className="h-3.5 w-3.5" />
                <span>Chỉnh sửa trực tiếp</span>
              </button>
            </div>

            {/* Quick Metrics */}
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="bg-slate-100 px-2 py-1 rounded-md font-medium">
                📊 {editableText.split(/\s+/).filter(Boolean).length} từ
              </span>
              <span className="bg-slate-100 px-2 py-1 rounded-md font-medium">
                {language === 'vi' ? '🇻🇳 Tiếng Việt' : '🇬🇧 English'}
              </span>
            </div>

            {/* Export & Copy Actions */}
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleDownload('txt')}
                className="text-xs h-8 px-2.5 text-slate-700 hover:text-blue-700"
              >
                <Download className="h-3.5 w-3.5 mr-1" /> .TXT
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => handleDownload('md')}
                className="text-xs h-8 px-2.5 text-slate-700 hover:text-blue-700"
              >
                <Download className="h-3.5 w-3.5 mr-1" /> .MD
              </Button>
              <Button
                type="button"
                size="sm"
                onClick={handleCopy}
                className="text-xs h-8 px-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold"
              >
                {copied ? (
                  <>
                    <Check className="h-3.5 w-3.5 mr-1 text-emerald-300" />
                    <span>Đã sao chép!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3.5 w-3.5 mr-1" />
                    <span>Sao chép toàn bộ</span>
                  </>
                )}
              </Button>
            </div>
          </div>

          {/* Highlighted Strengths Badge Row */}
          {coverLetter.key_strengths_highlighted && coverLetter.key_strengths_highlighted.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 p-2.5 bg-blue-50/60 rounded-lg border border-blue-100 text-xs text-blue-900">
              <span className="font-semibold flex items-center gap-1">
                <Sparkles className="h-3.5 w-3.5 text-blue-600" />
                Điểm mạnh được làm nổi bật trong thư:
              </span>
              {coverLetter.key_strengths_highlighted.map((strength, idx) => (
                <span
                  key={idx}
                  className="bg-white px-2 py-0.5 rounded-md border border-blue-200 text-[11px] font-medium text-slate-700 shadow-2xs"
                >
                  ✓ {strength}
                </span>
              ))}
            </div>
          )}

          {/* Letter Body Area */}
          <Card className="border border-slate-200 shadow-sm bg-white overflow-hidden">
            {activeMode === 'preview' ? (
              /* PREVIEW LETTERHEAD MODE */
              <div className="p-8 sm:p-12 max-w-3xl mx-auto space-y-6 text-slate-800 font-serif leading-relaxed text-sm bg-white min-h-[500px]">
                {/* Letter Header */}
                <div className="border-b border-slate-200 pb-4 space-y-1 font-sans">
                  <h3 className="text-xl font-bold text-slate-900">
                    {result.structured_cv.name || 'Ứng viên'}
                  </h3>
                  <div className="text-xs text-slate-500 flex flex-wrap gap-x-4 gap-y-1">
                    {result.structured_cv.contact?.email && (
                      <span>Email: {result.structured_cv.contact.email}</span>
                    )}
                    {result.structured_cv.contact?.phone && (
                      <span>SĐT: {result.structured_cv.contact.phone}</span>
                    )}
                    {result.structured_cv.contact?.location && (
                      <span>Địa chỉ: {result.structured_cv.contact.location}</span>
                    )}
                  </div>
                </div>

                {/* Recipient info */}
                <div className="font-sans text-xs text-slate-600 space-y-1 pt-1">
                  <div className="flex items-center gap-1 font-bold text-slate-800">
                    <Building className="h-3.5 w-3.5 text-slate-400" />
                    Ban Tuyển dụng {result.structured_jd.company || 'Quý công ty'}
                  </div>
                  <div>
                    Vị trí: <strong>{result.structured_jd.job_title}</strong>
                  </div>
                  <div className="text-slate-400">
                    Tiêu đề thư: {coverLetter.subject}
                  </div>
                </div>

                {/* Salutation */}
                <div className="font-bold text-slate-900 pt-2">
                  {coverLetter.salutation}
                </div>

                {/* Opening */}
                <p className="text-slate-700 leading-relaxed text-justify">
                  {coverLetter.opening}
                </p>

                {/* Body Paragraphs */}
                {coverLetter.body_paragraphs.map((p, idx) => (
                  <p key={idx} className="text-slate-700 leading-relaxed text-justify">
                    {p}
                  </p>
                ))}

                {/* Closing */}
                <p className="text-slate-700 leading-relaxed text-justify">
                  {coverLetter.closing}
                </p>

                {/* Sign-off & Signature */}
                <div className="pt-4 space-y-3 font-sans">
                  <p className="text-slate-700 whitespace-pre-line">
                    {coverLetter.sign_off}
                  </p>
                </div>
              </div>
            ) : (
              /* DIRECT EDIT TEXTAREA MODE */
              <div className="p-4 bg-slate-50">
                <div className="flex items-center justify-between pb-2 text-xs text-slate-500">
                  <span>Bạn có thể tự do chỉnh sửa nội dung thư trước khi sao chép hoặc tải về:</span>
                  <button
                    type="button"
                    onClick={() => setEditableText(coverLetter.full_letter)}
                    className="text-blue-600 hover:underline font-medium"
                  >
                    Khôi phục bản gốc AI
                  </button>
                </div>
                <textarea
                  value={editableText}
                  onChange={(e) => setEditableText(e.target.value)}
                  rows={20}
                  className="w-full p-4 rounded-lg border border-slate-300 font-mono text-xs leading-relaxed text-slate-900 focus:outline-hidden focus:border-blue-500 bg-white shadow-2xs resize-y"
                  placeholder="Nội dung Cover Letter..."
                />
              </div>
            )}
          </Card>
        </div>
      )}
    </div>
  );
}
