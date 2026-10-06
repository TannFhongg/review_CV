'use client';

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FileText, Upload, X, Edit3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatFileSize, ACCEPTED_FILE_TYPES, MAX_FILE_SIZE } from '@/lib/utils';

interface FileUploaderProps {
  title: string;
  iconColor: string;
  file: File | null;
  text: string;
  onFileChange: (file: File | null) => void;
  onTextChange: (text: string) => void;
  placeholderText?: string;
}

export function FileUploader({
  title,
  iconColor,
  file,
  text,
  onFileChange,
  onTextChange,
  placeholderText = 'Dán nội dung văn bản vào đây...',
}: FileUploaderProps) {
  const [isTextMode, setIsTextMode] = useState<boolean>(Boolean(text && !file));

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileChange(acceptedFiles[0]);
        setIsTextMode(false);
      }
    },
    [onFileChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
  });

  return (
    <Card className="border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
      <CardHeader className="pb-3 flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          <FileText className={`h-5 w-5 ${iconColor}`} />
          {title}
        </CardTitle>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="text-xs text-slate-500 hover:text-slate-800"
          onClick={() => {
            setIsTextMode(!isTextMode);
          }}
        >
          <Edit3 className="h-3.5 w-3.5 mr-1" />
          {isTextMode ? 'Tải tệp tin' : 'Dán văn bản'}
        </Button>
      </CardHeader>
      <CardContent>
        {isTextMode ? (
          <div className="space-y-2">
            <textarea
              className="w-full h-44 p-3 text-sm rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono bg-slate-50/50 resize-none"
              placeholder={placeholderText}
              value={text}
              onChange={(e) => onTextChange(e.target.value)}
            />
            <div className="flex justify-between items-center text-xs text-slate-400">
              <span>Độ dài: {text.length.toLocaleString()} ký tự</span>
              {text && (
                <button
                  type="button"
                  onClick={() => onTextChange('')}
                  className="text-red-500 hover:underline"
                >
                  Xóa nội dung
                </button>
              )}
            </div>
          </div>
        ) : file ? (
          <div className="flex items-center justify-between p-4 bg-slate-50 border border-slate-200 rounded-lg">
            <div className="flex items-center gap-3 overflow-hidden">
              <FileText className={`h-8 w-8 shrink-0 ${iconColor}`} />
              <div className="overflow-hidden">
                <p className="text-sm font-medium text-slate-800 truncate">
                  {file.name}
                </p>
                <p className="text-xs text-slate-500">
                  {formatFileSize(file.size)}
                </p>
              </div>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-slate-400 hover:text-red-600 shrink-0"
              onClick={() => onFileChange(null)}
              title="Xóa tệp này"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50/50'
                : 'border-slate-200 hover:border-blue-400 bg-slate-50/30'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="h-8 w-8 mx-auto text-slate-400 mb-2" />
            <p className="text-sm font-medium text-slate-700">
              {isDragActive
                ? 'Thả tệp vào đây...'
                : 'Kéo thả tệp hoặc nhấn để chọn'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Hỗ trợ PDF, DOCX, TXT (tối đa 10MB)
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
