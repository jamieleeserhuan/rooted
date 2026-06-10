/**
 * src/api/pathway.ts
 * ------------------
 * All fetch logic for the /pathway endpoint (pathway.py).
 *
 * This is the ONLY place in the frontend that talks to the pathway backend.
 * Components never call fetch() directly — they call fetchPathway() instead.
 *
 * TO USE MOCK DATA (while backend is in development):
 *   Set VITE_USE_MOCK=true in your .env.local
 *
 * TO USE REAL BACKEND:
 *   Set VITE_USE_MOCK=false (or remove it)
 */

import type { PathwayCard, NocMatch } from '../types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';
const API_URL = import.meta.env.VITE_API_URL || '';

// ---------------------------------------------------------------------------
// Main function — this is what components call
// ---------------------------------------------------------------------------

export async function fetchPathway(match: NocMatch): Promise<PathwayCard> {
  if (USE_MOCK) {
    // Simulate network delay so loading states are visible during development
    await delay(1200);
    return getMockPathwayCard(match.nocCode, match.title);
  }

  const res = await fetch(`${API_URL}/api/pathway`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      noc_code: match.nocCode,
      title: match.title,
      // Use full definition if available, fall back to short description
      definition: match.definition || match.description,
    }),
  });

  if (!res.ok) {
    throw new Error(`Pathway API error: ${res.status}`);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Mock data — realistic PathwayCard shape for UI development
// Returns different cards for known NOC codes, generic card for unknown ones
// ---------------------------------------------------------------------------

function getMockPathwayCard(nocCode: string, title: string): PathwayCard {
  const mockCards: Record<string, PathwayCard> = {
    '31301': {
      noc_code: '31301',
      occupation_title: 'Registered Nurse (RN)',
      province: 'Ontario',
      is_regulated: true,
      estimated_time_months_min: 12,
      estimated_time_months_max: 24,
      typical_cost_cad: 2500,
      cost_note: 'assessment and licensing fees',
      steps: [
        {
          number: 1,
          heading: 'Begin NNAS credential assessment',
          description: 'Submit your nursing credentials to the National Nursing Assessment Service (NNAS). If you lack original documents due to displacement, NNAS can issue a Document Advisory that forwards your profile to CNO for alternative review.',
          flag: 'assessment',
        },
        {
          number: 2,
          heading: 'Apply to the College of Nurses of Ontario (CNO)',
          description: 'Register on the CNO portal and select the internationally educated nurse pathway. CNO accepts statutory declarations as an alternative to official documents under their Special Circumstances Policy.',
          flag: 'no_docs',
        },
        {
          number: 3,
          heading: 'Complete language proficiency test',
          description: 'Demonstrate English or French competency at IELTS 7+ or CELBAN. Free language training for nurses is available through settlement agencies via the LINC program.',
          flag: 'english_test',
        },
        {
          number: 4,
          heading: 'Complete bridging program or SPEP',
          description: 'Enrol in a nursing bridging program (e.g. CARE Centre, George Brown College) or apply to the Supervised Practice Experience Partnership (SPEP) for paid clinical hours in Ontario hospitals.',
          flag: 'fee',
        },
        {
          number: 5,
          heading: 'Pass the NCLEX-RN exam',
          description: 'Register and pass the National Council Licensure Examination. Windmill Microlending can cover prep course and exam fees.',
          flag: 'fee',
        },
      ],
      funding_note: 'Windmill Microlending: up to $15,000 low-interest loans. Ontario Bridging Participant Assistance Program (OBPAP): up to $5,000 in bursaries.',
      disclaimer: 'This pathway is AI-generated and may not reflect the latest regulatory requirements. Always verify with the College of Nurses of Ontario (cno.org) or a certified immigration professional.',
    },

    '21300': {
      noc_code: '21300',
      occupation_title: 'Civil Engineer',
      province: 'Ontario',
      is_regulated: true,
      estimated_time_months_min: 18,
      estimated_time_months_max: 36,
      typical_cost_cad: 3000,
      cost_note: 'to start',
      steps: [
        {
          number: 1,
          heading: 'Get credentials assessed by WES',
          description: 'Submit your engineering degree to World Education Services (WES) for a Canadian equivalency report. If original transcripts are unavailable, WES accepts statutory declarations under their refugee documentation policy.',
          flag: 'assessment',
        },
        {
          number: 2,
          heading: 'Apply to Professional Engineers Ontario (PEO)',
          description: 'Begin the PEO licensing process using your WES report. PEO will assess your academic and work experience against Canadian standards.',
          flag: 'fee',
        },
        {
          number: 3,
          heading: 'Complete the Professional Practice Exam (PPE)',
          description: 'Pass the PEO Professional Practice Exam covering Canadian law and ethics. Study materials are available free through PEO.',
          flag: 'fee',
        },
        {
          number: 4,
          heading: 'Complete supervised work experience',
          description: 'Accumulate 48 months of acceptable engineering experience, with at least 12 months in Canada under a licensed P.Eng. Many Ontario employers actively hire internationally trained engineers for this purpose.',
          flag: null,
        },
      ],
      funding_note: 'Ontario CARE for Skilled Immigrants: up to $4,500 for licensing. Windmill Microlending available for exam and course fees.',
      disclaimer: 'This pathway is AI-generated. Always verify current requirements with Professional Engineers Ontario at peo.on.ca.',
    },

    '41201': {
      noc_code: '41201',
      occupation_title: 'Elementary and Secondary School Teacher',
      province: 'Ontario',
      is_regulated: true,
      estimated_time_months_min: 6,
      estimated_time_months_max: 18,
      typical_cost_cad: 1200,
      cost_note: 'certification fees',
      steps: [
        {
          number: 1,
          heading: 'Apply to the Ontario College of Teachers (OCT)',
          description: 'Submit your teaching credentials to OCT for review. OCT accepts statutory declarations as supplementary evidence if official transcripts are unavailable due to conflict or displacement.',
          flag: 'assessment',
        },
        {
          number: 2,
          heading: 'Complete language proficiency requirement',
          description: 'Demonstrate English or French proficiency. OCT accepts IELTS Academic 7.5+ or equivalent. Free preparation support is available through settlement agencies.',
          flag: 'english_test',
        },
        {
          number: 3,
          heading: 'Complete Additional Qualification (AQ) courses if required',
          description: 'OCT may require specific AQ courses to align your qualifications with Ontario curriculum. Many are available online through OISE or Ontario universities.',
          flag: 'fee',
        },
      ],
      funding_note: 'Ontario Immigrant Nominee Program (OINP) may fast-track teachers. ACCES Employment offers free teacher bridging programs.',
      disclaimer: 'This pathway is AI-generated. Verify current requirements with the Ontario College of Teachers at oct.ca.',
    },
  };

  // Return a specific mock if we have one, otherwise a generic card
  return mockCards[nocCode] ?? getGenericMockCard(nocCode, title);
}

function getGenericMockCard(nocCode: string, title: string): PathwayCard {
  return {
    noc_code: nocCode,
    occupation_title: title,
    province: 'Ontario',
    is_regulated: false,
    estimated_time_months_min: 3,
    estimated_time_months_max: 12,
    typical_cost_cad: 0,
    cost_note: 'varies',
    steps: [
      {
        number: 1,
        heading: 'Get a credential assessment',
        description: 'Contact WES (World Education Services) to have your foreign credentials evaluated for Canadian equivalency. If you lack original documents, ask about their statutory declaration option.',
        flag: 'assessment',
      },
      {
        number: 2,
        heading: 'Connect with a settlement agency',
        description: 'A local newcomer settlement agency such as OCISO or ACCES Employment can help you identify the specific licensing body for your occupation and province.',
        flag: null,
      },
      {
        number: 3,
        heading: 'Search the Job Bank for your NOC code',
        description: 'Use Canada\'s official Job Bank to find employers actively hiring for NOC ' + nocCode + ' and understand what qualifications they expect.',
        flag: null,
      },
    ],
    funding_note: 'Many settlement agencies offer free bridging support and job placement for refugees.',
    disclaimer: 'This pathway is AI-generated and may not reflect the latest regulatory requirements. Always verify with the relevant regulatory body or a certified immigration professional.',
  };
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
