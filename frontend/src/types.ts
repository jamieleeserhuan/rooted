/**
 * types.ts
 * --------
 * All shared TypeScript types for Rooted.
 *
 * IMPORTANT: These types are written to match the ACTUAL backend response
 * shapes. Do not change field names here without also changing them in
 * the corresponding backend Pydantic models.
 *
 * Backend → Frontend mapping:
 *   pathway.py PathwayCard  →  PathwayCard (this file)
 *   match endpoint          →  NocMatch (this file)
 */

// ---------------------------------------------------------------------------
// App-level types
// ---------------------------------------------------------------------------

export type Language = 'en' | 'fr' | 'ar' | 'dr';

export type Screen = 'home' | 'input' | 'results' | 'pathway';

export interface UserInput {
  description: string;
  province: string;
  documentsAvailable: 'none' | 'some' | 'full';
  isTransOrGenderDiverse: boolean;
}

// ---------------------------------------------------------------------------
// NOC matching (from S-BERT endpoint — your teammates' code)
// Keep nocCode as camelCase to match existing frontend usage
// ---------------------------------------------------------------------------

export interface NocMatch {
  nocCode: string;       // e.g. "31301"
  title: string;         // e.g. "Registered nurses and registered psychiatric nurses"
  description: string;   // short plain-language description
  confidence: number;    // 0–100 match score
  category: string;      // e.g. "Healthcare", "Engineering"
  definition?: string;   // full NOC definition — used when calling /pathway
}

// ---------------------------------------------------------------------------
// Pathway card (from pathway.py — Jamie's code)
// Field names match pathway.py's PathwayCard Pydantic model exactly.
// ---------------------------------------------------------------------------

export type StepFlag = 'no_docs' | 'english_test' | 'fee' | 'assessment' | null;

export interface PathwayStep {
  number: number;
  heading: string;
  description: string;
  flag: StepFlag;
}

export interface PathwayCard {
  noc_code: string;
  occupation_title: string;
  province: string;
  is_regulated: boolean;
  estimated_time_months_min: number;
  estimated_time_months_max: number;
  typical_cost_cad: number;
  cost_note: string;
  steps: PathwayStep[];
  funding_note: string | null;
  disclaimer: string;
}

// ---------------------------------------------------------------------------
// API response wrappers
// ---------------------------------------------------------------------------

export interface MatchApiResponse {
  matches: NocMatch[];
  fallbackMode?: boolean;  // true when running without Gemini key
}

export interface PathwayApiResponse extends PathwayCard {}

// ---------------------------------------------------------------------------
// Loading states — used to drive UI feedback
// ---------------------------------------------------------------------------

export type LoadingState = 'idle' | 'loading' | 'success' | 'error';
