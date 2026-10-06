import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { MatchStatus, Priority } from './types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getPriorityColor(priority: Priority): string {
  switch (priority) {
    case 'must_fix': return 'text-red-600 bg-red-50 border-red-200';
    case 'should_fix': return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'nice_to_have': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'already_strong': return 'text-green-600 bg-green-50 border-green-200';
  }
}

export function getPriorityLabel(priority: Priority): string {
  switch (priority) {
    case 'must_fix': return '🔴 MUST FIX';
    case 'should_fix': return '🟠 SHOULD FIX';
    case 'nice_to_have': return '🟡 NICE TO HAVE';
    case 'already_strong': return '🟢 ALREADY STRONG';
  }
}

export function getMatchStatusColor(status: MatchStatus): string {
  switch (status) {
    case 'strong_match': return 'text-green-700 bg-green-100';
    case 'partial_match': return 'text-yellow-700 bg-yellow-100';
    case 'weak_evidence': return 'text-orange-700 bg-orange-100';
    case 'missing': return 'text-red-700 bg-red-100';
    case 'unknown': return 'text-gray-700 bg-gray-100';
  }
}

export function getMatchStatusLabel(status: MatchStatus): string {
  switch (status) {
    case 'strong_match': return 'Strong Match';
    case 'partial_match': return 'Partial Match';
    case 'weak_evidence': return 'Weak Evidence';
    case 'missing': return 'Missing';
    case 'unknown': return 'Unknown';
  }
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export const ACCEPTED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/msword': ['.doc'],
  'text/plain': ['.txt'],
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
