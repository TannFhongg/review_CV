// === Enums ===
export type MatchStatus = 'strong_match' | 'partial_match' | 'weak_evidence' | 'missing' | 'unknown';
export type Priority = 'must_fix' | 'should_fix' | 'nice_to_have' | 'already_strong';
export type Importance = 'required' | 'preferred' | 'nice_to_have';
export type SkillCategory = 'technical' | 'soft' | 'tool' | 'domain';

// === JD Models ===
export interface SkillRequirement {
  name: string;
  category: SkillCategory;
  importance: Importance;
  context: string | null;
  keywords: string[];
}

export interface StructuredJD {
  job_title: string;
  company: string | null;
  location: string | null;
  employment_type: string | null;
  seniority_level: string | null;
  required_skills: SkillRequirement[];
  preferred_skills: SkillRequirement[];
  responsibilities: string[];
  education_requirements: string[];
  experience_requirements: string[];
  technical_requirements: string[];
  soft_skills: string[];
  language_requirements: string[];
  domain_knowledge: string[];
  tools: string[];
  keywords: string[];
  raw_text: string;
}

// === CV Models ===
export interface ContactInfo {
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  github: string | null;
  website: string | null;
  location: string | null;
}

export interface Education {
  institution: string;
  degree: string;
  field: string | null;
  start_date: string | null;
  end_date: string | null;
  gpa: string | null;
  details: string[];
}

export interface WorkExperience {
  company: string;
  title: string;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  description: string;
  responsibilities: string[];
  technologies: string[];
  achievements: string[];
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  role: string | null;
  highlights: string[];
  url: string | null;
}

export interface StructuredCV {
  name: string;
  title: string | null;
  summary: string | null;
  contact: ContactInfo;
  education: Education[];
  experience: WorkExperience[];
  projects: Project[];
  technical_skills: string[];
  soft_skills: string[];
  certifications: string[];
  languages: string[];
  achievements: string[];
  raw_text: string;
}

// === Match Models ===
export interface EvidenceItem {
  source_section: string;
  source_text: string;
  relevance_score: number;
  explanation: string;
}

export interface RequirementMatch {
  requirement: string;
  requirement_importance: Importance;
  status: MatchStatus;
  evidence: EvidenceItem[];
  recommendation: string | null;
  priority: Priority;
  confidence: number;
}

export interface AlignmentScore {
  overall: number;
  technical_skills: number;
  experience_relevance: number;
  responsibilities_alignment: number;
  keyword_coverage: number;
  education_alignment: number;
  cv_clarity: number;
  methodology_notes: string;
}

export interface CVSuggestion {
  section: string;
  original_text: string;
  suggested_text: string;
  change_description: string;
  reason: string;
  jd_requirement: string;
  evidence: string;
  priority: Priority;
  accepted: boolean | null;
}

export interface AnalysisResult {
  structured_jd: StructuredJD;
  structured_cv: StructuredCV;
  matches: RequirementMatch[];
  alignment_score: AlignmentScore;
  top_recommendations: RequirementMatch[];
  suggestions: CVSuggestion[];
  strong_count: number;
  partial_count: number;
  weak_count: number;
  missing_count: number;
  analyzed_at: string;
  processing_time_seconds: number;
}
