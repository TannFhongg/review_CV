'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  Upload,
  BarChart3,
  FileSearch,
  Wand2,
  Download,
  RotateCcw,
  AlertCircle,
  Loader2,
  CheckCircle2,
  Mail,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

import { FileUploader } from '@/components/upload/FileUploader';
import { AlignmentScoreCard } from '@/components/analysis/AlignmentScoreCard';
import { MatchSummaryCards } from '@/components/analysis/MatchSummaryCards';
import { TopRecommendationsList } from '@/components/analysis/TopRecommendationsList';
import { EvidenceMap } from '@/components/analysis/EvidenceMap';
import { SuggestionCard } from '@/components/optimize/SuggestionCard';
import { CoverLetterGenerator } from '@/components/cover-letter/CoverLetterGenerator';
import { ExportModule } from '@/components/export/ExportModule';

import { useAnalysisStore } from '@/stores/analysisStore';
import { analyzeCV } from '@/lib/api';

const SAMPLE_JD = `Senior C++ Software Engineer — Automotive
Company: TechAuto GmbH
Location: Ho Chi Minh City, Vietnam
Employment Type: Full-time

Requirements:
- 3+ years of experience in C++ development
- Strong knowledge of Qt framework (Qt Widgets, QML)
- Experience with Linux development and embedded systems
- Familiarity with automotive protocols (CAN, LIN, UDS)
- Version control with Git
- Good communication skills in English

Preferred:
- Experience with Docker and CI/CD pipelines
- Knowledge of AUTOSAR architecture
- Experience with Agile/Scrum methodology

Responsibilities:
- Develop and maintain C++ applications for automotive ECU testing
- Design and implement Qt-based GUI applications
- Write unit tests and perform code reviews
- Document software architecture`;

const SAMPLE_CV = `VO VAN TUAN
Fresher C++ Software Engineer
Email: tuanvo@example.com
Phone: +84 123 456 789
GitHub: github.com/tuanvo
Location: Ho Chi Minh City, Vietnam

EDUCATION
Ho Chi Minh City University of Technology (HCMUT)
Bachelor of Engineering — Computer Engineering (2020 - 2024, GPA: 3.2/4.0)

PROJECTS
VTuber Avatar Control Panel
- Developed a Qt Widgets application for controlling VTuber avatar states
- Implemented interactive UI controls using signal/slot communication
- Technologies: C++, Qt Widgets, Qt Creator

Embedded Weather Station
- Built weather monitoring system on Raspberry Pi with Embedded Linux
- Sensor data acquisition via I2C/SPI protocols
- Technologies: C, Embedded Linux, Raspberry Pi, Python

Smart Home Controller
- Designed a home automation system using ESP32
- Implemented CAN bus communication between modules
- Technologies: C++, FreeRTOS, CAN protocol

TECHNICAL SKILLS
- Languages: C++, C, Python
- Frameworks: Qt, FreeRTOS
- Tools: Git, VS Code, Qt Creator
- Platforms: Linux, Raspberry Pi, ESP32
- Protocols: CAN, I2C, SPI

LANGUAGES
- Vietnamese: Native | English: Intermediate (IELTS 6.0)`;

export default function Home() {
  const {
    jdFile,
    cvFile,
    jdText,
    cvText,
    status,
    errorMessage,
    result,
    currentSuggestionIndex,
    setJdFile,
    setCvFile,
    setJdText,
    setCvText,
    setStatus,
    setError,
    setResult,
    acceptSuggestion,
    rejectSuggestion,
    setCurrentSuggestionIndex,
    reset,
  } = useAnalysisStore();

  const [activeTab, setActiveTab] = useState<string>('overview');

  const handleUseSampleData = () => {
    setJdFile(null);
    setCvFile(null);
    setJdText(SAMPLE_JD);
    setCvText(SAMPLE_CV);
  };

  const handleStartAnalysis = async () => {
    try {
      setStatus('uploading');
      const data = await analyzeCV(jdFile, cvFile, jdText || null, cvText || null);
      setResult(data);
      setActiveTab('overview');
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error
          ? err.message
          : 'Đã xảy ra lỗi không xác định khi phân tích.';
      setError(errorMsg);
    }
  };

  const hasInputs =
    (jdFile !== null || (jdText && jdText.trim().length > 0)) &&
    (cvFile !== null || (cvText && cvText.trim().length > 0));

  const isLoading = status !== 'idle' && status !== 'done' && status !== 'error';

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 pb-16">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between max-w-6xl">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 leading-tight">
                AI Job Application Copilot
              </h1>
              <p className="text-[11px] text-slate-500 hidden sm:block">
                Tối ưu hóa CV theo JD cụ thể • Dựa trên bằng chứng thực tế
              </p>
            </div>
          </div>

          {result && (
            <Button
              variant="outline"
              size="sm"
              onClick={reset}
              className="text-xs text-slate-600 hover:text-slate-900"
            >
              <RotateCcw className="h-3.5 w-3.5 mr-1" /> Phân tích mới
            </Button>
          )}
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Error Banner */}
        {errorMessage && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Lỗi phân tích</AlertTitle>
            <AlertDescription className="text-xs mt-1">
              {errorMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* ================= SCREEN 1: UPLOAD & INPUT ================= */}
        {!result && (
          <div className="space-y-8">
            {/* Hero Banner */}
            <div className="text-center max-w-2xl mx-auto pt-4 pb-2">
              <h2 className="text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">
                Tối ưu CV của bạn cho đúng công việc mục tiêu
              </h2>
              <p className="mt-3 text-sm text-slate-600 leading-relaxed">
                Hệ thống so khớp thông minh dựa trên bằng chứng trong CV gốc.
                <strong className="text-slate-800"> Tuyệt đối không bịa đặt kinh nghiệm hay kỹ năng ảo.</strong>
              </p>

              <div className="mt-4">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleUseSampleData}
                  className="text-xs text-blue-600 border-blue-200 bg-blue-50/50 hover:bg-blue-100/50"
                >
                  ⚡ Nạp dữ liệu mẫu (C++ Automotive Fresher)
                </Button>
              </div>
            </div>

            {/* Upload Inputs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FileUploader
                title="Job Description (Mô tả công việc)"
                iconColor="text-blue-600"
                file={jdFile}
                text={jdText}
                onFileChange={setJdFile}
                onTextChange={setJdText}
                placeholderText="Dán nội dung Job Description (JD) vào đây..."
              />

              <FileUploader
                title="CV / Resume của bạn"
                iconColor="text-emerald-600"
                file={cvFile}
                text={cvText}
                onFileChange={setCvFile}
                onTextChange={setCvText}
                placeholderText="Dán nội dung CV hiện tại của bạn vào đây..."
              />
            </div>

            {/* Action Button */}
            <div className="text-center pt-2">
              <Button
                size="lg"
                className="px-10 h-12 text-sm font-semibold bg-blue-600 hover:bg-blue-700 shadow-md transition-all"
                disabled={!hasInputs || isLoading}
                onClick={handleStartAnalysis}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Đang phân tích dữ liệu...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Bắt đầu phân tích & tối ưu
                  </>
                )}
              </Button>

              <p className="text-xs text-slate-400 mt-3 flex items-center justify-center gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                Bảo mật tuyệt đối: Tệp tải lên sẽ được xóa ngay lập tức sau khi trích xuất.
              </p>
            </div>
          </div>
        )}

        {/* ================= SCREEN 2-5: ANALYSIS DASHBOARD ================= */}
        {result && (
          <div className="space-y-6">
            {/* Header info bar */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
              <div>
                <span className="text-xs text-slate-400">Vị trí mục tiêu:</span>
                <h2 className="text-base font-bold text-slate-900">
                  {result.structured_jd.job_title}
                  {result.structured_jd.company && (
                    <span className="text-slate-500 font-normal">
                      {' '}
                      • {result.structured_jd.company}
                    </span>
                  )}
                </h2>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400">Ứng viên:</span>
                <p className="text-sm font-semibold text-slate-800">
                  {result.structured_cv.name || 'Ứng viên'}
                </p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid grid-cols-2 sm:grid-cols-5 h-auto sm:h-11 bg-slate-200/70 p-1 rounded-xl gap-1">
                <TabsTrigger
                  value="overview"
                  className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:shadow-xs flex items-center gap-1.5"
                >
                  <BarChart3 className="h-4 w-4" />
                  <span>Tổng quan & Điểm</span>
                </TabsTrigger>
                <TabsTrigger
                  value="evidence"
                  className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:shadow-xs flex items-center gap-1.5"
                >
                  <FileSearch className="h-4 w-4" />
                  <span>Bản đồ bằng chứng</span>
                </TabsTrigger>
                <TabsTrigger
                  value="optimize"
                  className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:shadow-xs flex items-center gap-1.5"
                >
                  <Wand2 className="h-4 w-4" />
                  <span>Tối ưu hóa ({result.suggestions.length})</span>
                </TabsTrigger>
                <TabsTrigger
                  value="cover-letter"
                  className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:shadow-xs flex items-center gap-1.5"
                >
                  <Mail className="h-4 w-4 text-blue-600" />
                  <span>Cover Letter ✉️</span>
                </TabsTrigger>
                <TabsTrigger
                  value="export"
                  className="text-xs font-semibold data-[state=active]:bg-white data-[state=active]:shadow-xs flex items-center gap-1.5"
                >
                  <Download className="h-4 w-4" />
                  <span>Xuất báo cáo</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>

            {/* TAB 1: OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <AlignmentScoreCard score={result.alignment_score} />

                <MatchSummaryCards
                  strongCount={result.strong_count}
                  partialCount={result.partial_count}
                  weakCount={result.weak_count}
                  missingCount={result.missing_count}
                  onFilterChange={() => setActiveTab('evidence')}
                />

                <TopRecommendationsList
                  recommendations={result.top_recommendations}
                  onGoToOptimize={() => setActiveTab('optimize')}
                />
              </div>
            )}

            {/* TAB 2: EVIDENCE MAPPING */}
            {activeTab === 'evidence' && (
              <div className="space-y-6">
                <EvidenceMap matches={result.matches} />
              </div>
            )}

            {/* TAB 3: OPTIMIZE CV */}
            {activeTab === 'optimize' && (
              <div className="space-y-6">
                {result.suggestions.length === 0 ? (
                  <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
                    <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto mb-2" />
                    <h3 className="text-base font-bold text-slate-800">
                      CV đã phù hợp tối đa
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      Không cần viết lại nội dung nào đáng kể.
                    </p>
                  </div>
                ) : (
                  <SuggestionCard
                    suggestion={result.suggestions[currentSuggestionIndex]}
                    currentIndex={currentSuggestionIndex}
                    totalCount={result.suggestions.length}
                    onAccept={() => acceptSuggestion(currentSuggestionIndex)}
                    onReject={() => rejectSuggestion(currentSuggestionIndex)}
                    onPrev={() =>
                      setCurrentSuggestionIndex(
                        Math.max(0, currentSuggestionIndex - 1)
                      )
                    }
                    onNext={() =>
                      setCurrentSuggestionIndex(
                        Math.min(
                          result.suggestions.length - 1,
                          currentSuggestionIndex + 1
                        )
                      )
                    }
                  />
                )}
              </div>
            )}

            {/* TAB 4: COVER LETTER GENERATOR */}
            {activeTab === 'cover-letter' && (
              <div className="space-y-6">
                <CoverLetterGenerator result={result} />
              </div>
            )}

            {/* TAB 5: EXPORT */}
            {activeTab === 'export' && (
              <div className="space-y-6">
                <ExportModule result={result} />
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
