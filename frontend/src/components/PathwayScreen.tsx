/**
 * PathwayScreen.tsx
 * -----------------
 * Displays the LLM-generated pathway card for a selected NOC match.
 *
 * Data flow:
 *   1. Mounts with a NocMatch (selected by user on MatchResults screen)
 *   2. Calls fetchPathway() from src/api/pathway.ts
 *   3. Renders the returned PathwayCard
 *
 * No fetch() calls here — all API logic is in src/api/pathway.ts.
 * No references to curatedPathways.ts — that file can be deleted.
 */

import { useState, useEffect } from 'react';
import {
  ArrowLeft, Calendar, Coins, Gift, AlertCircle, ExternalLink,
  ChevronRight, Sparkles, Copy, Check, ShieldAlert, Heart, Users
} from 'lucide-react';
import type { Language, NocMatch, PathwayCard, PathwayStep, UserInput } from '../types';
import { translations } from '../data/translations';
import { fetchPathway } from '../api/pathway';

interface PathwayScreenProps {
  currentLanguage: Language;
  match: NocMatch;
  userInput: UserInput;
  onBack: () => void;
  onReset: () => void;
}

// Maps flag codes → display labels and status colors
const FLAG_CONFIG = {
  no_docs:      { label: 'No documents needed', status: 'ready'   as const },
  english_test: { label: 'Language test required', status: 'pending' as const },
  fee:          { label: 'Fee required', status: 'pending' as const },
  assessment:   { label: 'Assessment required', status: 'info'    as const },
};

const STATUS_COLORS = {
  ready:   { text: 'text-[#3B6651] bg-[#EAF3EE] border-[#C2DEC3]/40', dot: 'bg-[#5A7D6C]' },
  pending: { text: 'text-[#865E26] bg-[#FAF4EB] border-[#F3E2C9]/40', dot: 'bg-[#A08E79]' },
  info:    { text: 'text-[#34627C] bg-[#E8F1F5] border-[#CCE2F0]/40', dot: 'bg-sky-500'   },
};

export default function PathwayScreen({ currentLanguage, match, userInput, onBack, onReset }: PathwayScreenProps) {
  const t = translations[currentLanguage];

  // Pathway card fetched from pathway.py via /api/pathway
  const [card, setCard] = useState<PathwayCard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');


  // Fetch pathway card when component mounts or match changes
  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError('');
    setCard(null);

    fetchPathway(match)
      .then(data => {
        if (!cancelled) setCard(data);
      })
      .catch(err => {
        if (!cancelled) setError(err.message || 'Could not load pathway. Please try again.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => { cancelled = true; };
  }, [match.nocCode]);



  // Helper: derive step status from flag
  const getStepStatus = (step: PathwayStep) => {
    const config = step.flag ? FLAG_CONFIG[step.flag] : null;
    return config?.status || 'ready';
  };

  // ---------------------------------------------------------------------------
  // Loading state
  // ---------------------------------------------------------------------------

  if (isLoading) {
    return (
      <div className="w-full max-w-3xl bg-white border border-[#E9E5DE] rounded-[40px] p-10 shadow-[0_32px_64px_-16px_rgba(90,125,108,0.1)] mx-auto flex items-center justify-center min-h-[360px]">
        <div className="text-center space-y-4">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#EAF3EE]">
            <svg className="animate-spin h-8 w-8 text-[#5A7D6C]" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-bold font-serif text-[#2A2A28]">Generating your pathway...</h3>
            <p className="text-xs text-[#A08E79] mt-1">Llama 3.1 is building your personalised steps</p>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Error state
  // ---------------------------------------------------------------------------

  if (error || !card) {
    return (
      <div className="w-full max-w-3xl bg-white border border-[#E9E5DE] rounded-[40px] p-10 mx-auto">
        <div className="flex items-start gap-3 p-5 bg-red-50 border border-red-200 rounded-2xl">
          <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-800">{error || 'Something went wrong.'}</p>
            <button onClick={onBack} className="text-xs text-red-700 underline mt-2">Go back</button>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Render pathway card
  // ---------------------------------------------------------------------------

  return (
    <div className="w-full max-w-3xl bg-white border border-[#E9E5DE] rounded-[40px] p-5 md:p-10 shadow-[0_32px_64px_-16px_rgba(90,125,108,0.1)] mx-auto space-y-8">

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#F1EDEA] pb-6 text-left">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="p-2 hover:bg-[#F7F5F0] rounded-xl transition text-[#A08E79] cursor-pointer">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-xl md:text-2xl font-bold font-serif text-[#2A2A28] tracking-tight leading-tight">
              {card.occupation_title}
            </h2>
            <p className="text-xs font-bold text-[#A08E79] uppercase tracking-widest mt-1.5">
              {card.province} — NOC {card.noc_code}
              {card.is_regulated && (
                <span className="ml-2 text-[#3B6651] bg-[#EAF3EE] px-2 py-0.5 rounded-full">Regulated</span>
              )}
            </p>
          </div>
        </div>
        <button
          onClick={onReset}
          className="px-4 py-2 text-xs font-semibold text-[#7A7A75] bg-[#F7F5F0] hover:bg-[#E9E5DE] border border-[#E9E5DE] rounded-xl self-start md:self-center transition cursor-pointer"
        >
          Start New Search
        </button>
      </div>

      {/* Time + Cost stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
        <div className="bg-white border border-[#E9E5DE] rounded-2xl p-5 shadow-sm flex items-start gap-4">
          <div className="p-3 bg-[#EAF3EE] rounded-xl text-[#3B6651] border border-[#C2DEC3]/40 shrink-0">
            <Calendar className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-[10px] font-bold text-[#A08E79] uppercase tracking-widest mb-0.5">{t.estTime}</h4>
            <p className="text-base font-bold text-[#343432]">
              {card.estimated_time_months_min}–{card.estimated_time_months_max} months
            </p>
          </div>
        </div>

        <div className="bg-white border border-[#E9E5DE] rounded-2xl p-5 shadow-sm flex items-start gap-4">
          <div className="p-3 bg-[#FAF4EB] rounded-xl text-[#865E26] border border-[#F3E2C9]/40 shrink-0">
            <Coins className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-[10px] font-bold text-[#A08E79] uppercase tracking-widest mb-0.5">{t.estCost}</h4>
            <p className="text-base font-bold text-[#343432]">
              {card.typical_cost_cad > 0
                ? `$${card.typical_cost_cad.toLocaleString()} CAD ${card.cost_note}`
                : `${card.cost_note}`
              }
            </p>
          </div>
        </div>
      </div>

      {/* Funding */}
      {card.funding_note && (
        <div className="bg-[#F1EDEA] border border-[#E9E5DE] rounded-2xl p-6 text-left">
          <div className="flex items-center gap-2.5 mb-3">
            <Gift className="w-5 h-5 text-[#5A7D6C]" />
            <h3 className="text-sm font-bold text-[#2A2A28] uppercase tracking-wider">{t.fundingEarly}</h3>
          </div>
          <p className="text-xs md:text-sm text-[#5F5F5C] leading-relaxed">{card.funding_note}</p>
        </div>
      )}

      {/* Step-by-step roadmap */}
      <div className="space-y-6 text-left">
        <h3 className="text-lg font-bold font-serif text-[#2A2A28] tracking-tight border-b border-[#F1EDEA] pb-2">
          Your Step-by-Step Pathway
        </h3>

        <div className="relative border-l-2 border-[#E9E5DE] pl-6 ml-4 space-y-8">
          {card.steps.map((step) => {
            const status = getStepStatus(step);
            const color = STATUS_COLORS[status];
            const flagConfig = step.flag ? FLAG_CONFIG[step.flag] : null;

            return (
              <div key={step.number} className="relative group p-1">
                {/* Timeline dot */}
                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full border-2 border-white bg-[#A08E79] group-hover:bg-[#5A7D6C] transition shadow-xs" />

                <div className="flex flex-wrap justify-between items-start gap-3 mb-2">
                  <h4 className="text-base font-bold font-serif text-[#2A2A28] leading-snug">
                    Step {step.number}: {step.heading}
                  </h4>
                  {flagConfig && (
                    <span className={`px-2.5 py-1 rounded-lg text-[10px] font-bold tracking-wider border uppercase flex items-center gap-1.5 ${color.text}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${color.dot}`} />
                      {flagConfig.label}
                    </span>
                  )}
                </div>

                <p className="text-[#5F5F5C] text-sm leading-relaxed max-w-2xl">
                  {step.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Childcare support */}
      <div className="bg-[#FAF4EB] border border-[#F3E2C9]/40 rounded-2xl p-6 text-left space-y-2.5 shadow-xs">
        <div className="flex items-center gap-2 text-[#865E26]">
          <Heart className="w-5 h-5 shrink-0" />
          <h3 className="text-sm font-bold uppercase tracking-wider">{t.childcareSec}</h3>
        </div>
        <p className="text-xs md:text-sm text-[#7A7A75] leading-relaxed">{t.childcareText}</p>
        <p className="text-xs font-semibold text-[#865E26] bg-white border border-[#F3E2C9]/50 p-3 rounded-xl leading-relaxed">
          📍 Contact your local municipality for childcare subsidy options during your bridging program or licensing exams.
        </p>
      </div>

      {/* Trans-inclusive guidance */}
      {userInput.isTransOrGenderDiverse && (
        <div className="bg-[#F3EFF9] border border-[#DDD1ED]/40 rounded-2xl p-6 text-left space-y-2.5">
          <div className="flex items-center gap-2 text-[#5A3886]">
            <Users className="w-5 h-5 shrink-0" />
            <h3 className="text-sm font-bold uppercase tracking-wider">{t.transGuidanceTitle}</h3>
          </div>
          <p className="text-xs md:text-sm text-[#5F5F5C] leading-relaxed">
            Many trans and non-binary refugees encounter name mismatches on documents from their birth countries.
            Canadian human rights frameworks guarantee preferred name processing with regulatory bodies.
          </p>
          <p className="text-xs font-semibold text-[#5A3886] bg-white border border-[#DDD1ED]/50 p-3 rounded-xl leading-relaxed">
            💡 Submit a statutory declaration of transition alongside any settlement letter to have provincial regulators process your application under your preferred name.
          </p>
        </div>
      )}

      {/* Know your rights */}
      <div className="bg-[#EAF3EE] border border-[#C2DEC3]/40 rounded-2xl p-5 text-left flex gap-3.5 items-start">
        <ShieldAlert className="w-6 h-6 text-[#5A7D6C]" />
        <div className="space-y-1.5">
          <h4 className="text-xs font-bold text-[#2A2A28] uppercase tracking-wider">{t.knowYourRightsTitle}</h4>
          <p className="text-[#5F5F5C] text-xs md:text-sm leading-relaxed">{t.rightsText}</p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-[#F1EDEA] border border-[#E9E5DE] rounded-xl p-4 text-xs text-[#7A7A75] leading-relaxed text-left">
        <h5 className="font-bold text-[#2A2A28] uppercase tracking-wider mb-1">{t.disclaimerTitle}</h5>
        <p>{card.disclaimer}</p>
      </div>
    </div>
  );
}
