/**
 * src/api/match.ts
 * ----------------
 * All fetch logic for the NOC matching endpoint.
 * Currently wired to the Node/Gemini server.ts endpoint.
 * When teammates' S-BERT backend is ready, only the fetch URL here changes.
 */

import type { NocMatch, MatchApiResponse, Language } from '../types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const API_URL = import.meta.env.VITE_API_URL || '';

export async function fetchNocMatches(
  description: string,
  language: Language
): Promise<MatchApiResponse> {
  if (USE_MOCK) {
    await delay(2000);
    return getMockMatches(description);
  }

  const res = await fetch(`${API_URL}/api/match-noc`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ description, language }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Match API error: ${res.status}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Mock matches — three realistic examples for UI development
// ---------------------------------------------------------------------------

function getMockMatches(description: string): MatchApiResponse {
  const lower = description.toLowerCase();

  if (lower.includes('nurse') || lower.includes('hospital') || lower.includes('patient')) {
    return {
      matches: [
        { nocCode: '31301', title: 'Registered Nurse (RN)', description: 'Provide comprehensive nursing care in hospitals and clinical environments.', confidence: 94, category: 'Healthcare', definition: 'Registered nurses plan and provide nursing care to patients.' },
        { nocCode: '32101', title: 'Licensed Practical Nurse (LPN)', description: 'Provide supportive nursing services under supervision of medical practitioners.', confidence: 78, category: 'Healthcare' },
        { nocCode: '31102', title: 'General Practitioner & Family Physician', description: 'Diagnose and treat illnesses and physiological disorders.', confidence: 61, category: 'Healthcare' },
      ],
      fallbackMode: true,
    };
  }

  if (lower.includes('engineer') || lower.includes('civil') || lower.includes('construction')) {
    return {
      matches: [
        { nocCode: '21300', title: 'Civil Engineer', description: 'Plan, design and oversee construction of infrastructure and structural assets.', confidence: 93, category: 'Engineering', definition: 'Civil engineers plan, design, develop and manage projects.' },
        { nocCode: '22300', title: 'Civil Engineering Technologist', description: 'Provide technical support in civil design, surveying, and material testing.', confidence: 74, category: 'Engineering' },
        { nocCode: '72010', title: 'Construction Manager', description: 'Direct and coordinate construction crews on building projects.', confidence: 65, category: 'Trades' },
      ],
      fallbackMode: true,
    };
  }

  if (lower.includes('teach') || lower.includes('school') || lower.includes('education')) {
    return {
      matches: [
        { nocCode: '41201', title: 'Elementary and Secondary School Teacher', description: 'Teach academic courses to students following provincial curricula.', confidence: 91, category: 'Education', definition: 'Teachers instruct students in academic courses.' },
        { nocCode: '42202', title: 'Early Childhood Educator (ECE)', description: 'Plan and deliver developmental programs for young children.', confidence: 72, category: 'Education' },
        { nocCode: '41221', title: 'Education Policy Advisor', description: 'Research and advise on curriculum development and education policy.', confidence: 55, category: 'Education' },
      ],
      fallbackMode: true,
    };
  }

  // Generic fallback
  return {
    matches: [
      { nocCode: '31301', title: 'Registered Nurse (RN)', description: 'Matched based on healthcare and service competencies in your description.', confidence: 82, category: 'Healthcare' },
      { nocCode: '41201', title: 'School Teacher', description: 'Matched based on instructional and coordination skills in your description.', confidence: 74, category: 'Education' },
      { nocCode: '21300', title: 'Civil Engineer', description: 'Matched based on technical and planning skills in your description.', confidence: 65, category: 'Engineering' },
    ],
    fallbackMode: true,
  };
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
