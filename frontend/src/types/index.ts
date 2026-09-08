export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  created_at: string;
}

export interface HiringCriteria {
  id: number;
  role_title: string;
  required_skills: string;
  job_description: string;
  required_experience: string;
  education_requirement: string;
  minimum_score: number;
  created_by: number;
  created_at: string;
  candidate_count: number;
}

export interface Candidate {
  id: number;
  criteria_id: number;
  name: string;
  email: string;
  phone: string;
  gender: string;
  institute: string;
  degree: string;
  skills: string;
  experience: string;
  projects: string;
  certifications: string;
  location: string;
  resume_category: string;
  match_score: number;
  matched_skills: string;
  missing_skills: string;
  ai_status: string;
  manual_status: string;
  final_status: string;
  blind_reviewed: boolean;
  created_at: string;
  rank?: number;
}

export interface EmailLog {
  id: number;
  candidate_id: number;
  email_type: string;
  email_status: string;
  sent_at: string;
  candidate_name: string;
}

export interface DashboardStats {
  total_candidates: number;
  total_criteria: number;
  shortlisted: number;
  rejected: number;
  selected: number;
  on_hold: number;
  pending: number;
  avg_match_score: number;
  category_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
}

export type CandidateStatus =
  | 'Pending'
  | 'AI Shortlisted'
  | 'Manually Shortlisted'
  | 'Rejected'
  | 'Selected'
  | 'On Hold'
  | 'shortlisted'
  | 'pending'
  | 'rejected'
  | 'selected'
  | 'on_hold';

// Helper to parse comma-separated skills string into array
export function parseSkills(skillsStr: string): string[] {
  if (!skillsStr) return [];
  return skillsStr.split(',').map((s) => s.trim()).filter(Boolean);
}
