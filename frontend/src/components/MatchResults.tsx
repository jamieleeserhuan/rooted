/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { ArrowLeft, Tag, BarChart3, HelpCircle, Check, Briefcase, Sparkles } from 'lucide-react';
import { Language, NocMatch } from '../types';
import { translations } from '../data/translations';

interface MatchResultsProps {
  currentLanguage: Language;
  matches: NocMatch[];
  onBack: () => void;
  onSelectMatch: (match: NocMatch) => void;
  isSandboxMode?: boolean;
}

export default function MatchResults({ currentLanguage, matches, onBack, onSelectMatch, isSandboxMode }: MatchResultsProps) {
  const t = translations[currentLanguage];

  // Map categories to beautiful styles and icons
  const getCategoryStyles = (category: string) => {
    const norm = (category || '').toLowerCase();
    if (norm.includes('health')) return { bg: 'bg-[#EAF3EE] text-[#3B6651] border-[#C2DEC3]/40', dot: 'bg-[#5A7D6C]' };
    if (norm.includes('engineer')) return { bg: 'bg-[#E8F1F5] text-[#34627C] border-[#CCE2F0]/40', dot: 'bg-sky-500' };
    if (norm.includes('educat')) return { bg: 'bg-[#FAF4EB] text-[#865E26] border-[#F3E2C9]/40', dot: 'bg-amber-500' };
    if (norm.includes('law')) return { bg: 'bg-[#F3EFF9] text-[#5A3886] border-[#DDD1ED]/40', dot: 'bg-purple-500' };
    if (norm.includes('trade')) return { bg: 'bg-[#FBF1EA] text-[#8D4D20] border-[#F3DCB7]/40', dot: 'bg-orange-500' };
    return { bg: 'bg-[#F7F5F0] text-[#7A7A75] border-[#E9E5DE]', dot: 'bg-[#A08E79]' };
  };

  return (
    <div className="w-full max-w-2xl bg-white border border-[#E9E5DE] rounded-[40px] p-6 md:p-10 shadow-[0_32px_64px_-16px_rgba(90,125,108,0.1)] mx-auto">
      {/* Header with Back button */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onBack}
          className="p-2 hover:bg-[#F7F5F0] rounded-xl transition text-[#A08E79] cursor-pointer"
          title={t.backButton}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h2 className="text-xl md:text-2xl font-bold font-serif text-[#2A2A28] tracking-tight">
          {t.resultsTitle}
        </h2>
      </div>

      <p className="text-[#5F5F5C] text-sm md:text-base mb-8 text-left leading-relaxed">
        {t.resultsInstruction}
      </p>

      {isSandboxMode && (
        <div className="mb-8 p-5 bg-[#FAF4EB] border border-[#F3E2C9]/60 rounded-2xl text-left flex gap-4 items-start shadow-xs">
          <Sparkles className="w-5.5 h-5.5 text-[#A08E79] shrink-0 mt-0.5" />
          <div className="space-y-1.5 select-none">
            <h4 className="text-xs font-bold text-[#865E26] uppercase tracking-wider">Simulated Sandbox Active</h4>
            <p className="text-[#7A7A75] text-xs leading-relaxed font-semibold">
              Because no <code className="bg-white px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-[#865E26] border border-[#F3E2C9]/40">GEMINI_API_KEY</code> has been set up in Settings, Rooted is running in simulated sandbox mode. Tracing completed with our local semantic matcher and mock pathways. To unlock dynamic translation & custom drafting, configure your API secret.
            </p>
          </div>
        </div>
      )}

      {/* Matches List */}
      <div className="space-y-4 text-left">
        {matches.map((match, idx) => {
          const catStyle = getCategoryStyles(match.category);
          return (
            <div
              key={idx}
              className="group border border-[#E9E5DE] hover:border-[#5A7D6C]/50 bg-white hover:bg-[#FBF9F6]/40 rounded-3xl p-5 md:p-6 transition-all duration-200 shadow-xs relative flex flex-col justify-between focus-within:ring-1 focus-within:ring-[#5A7D6C]/50"
            >
              {/* Category tag */}
              <div className="flex justify-between items-start gap-4 mb-3">
                <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold border ${catStyle.bg} flex items-center gap-1.5`}>
                  <span className={`w-2 h-2 rounded-full ${catStyle.dot}`} />
                  {match.category}
                </span>
                
                {/* Visual confidence metric */}
                <div className="flex items-center gap-2 text-xs font-bold text-[#343432]">
                  <BarChart3 className="w-4 h-4 text-[#5A7D6C]" />
                  <span>{t.confidenceLabel}: {match.confidence}%</span>
                </div>
              </div>

              {/* Title & NOC Code */}
              <div className="mb-4">
                <div className="flex items-center gap-2 mb-1.5">
                  <Briefcase className="w-4 h-4 text-[#5A7D6C]" />
                  <h3 className="text-lg font-bold font-serif text-[#2A2A28] group-hover:text-[#5A7D6C] leading-snug transition-colors">
                    {match.title}
                  </h3>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[#A08E79] font-bold tracking-widest uppercase">
                  <Tag className="w-3.5 h-3.5" />
                  <span>NOC CODE {match.nocCode}</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-[#5F5F5C] text-sm leading-relaxed mb-6">
                {match.description}
              </p>

              {/* Confidence Progress Slider (Text + Visual requirement) */}
              <div className="w-full mb-6">
                <div className="w-full bg-[#F1EDEA] rounded-full h-2">
                  <div 
                    className="bg-[#5A7D6C] h-2 rounded-full transition-all duration-300"
                    style={{ width: `${match.confidence}%` }}
                  />
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={() => onSelectMatch(match)}
                className="w-full flex items-center justify-center gap-2 px-5 py-3.5 bg-[#5A7D6C] hover:bg-[#4d6b5c] text-white font-bold rounded-[18px] text-sm transition min-h-[44px] cursor-pointer"
              >
                <Check className="w-4 h-4 shrink-0" />
                <span>{t.selectMatchCTA}</span>
              </button>
            </div>
          );
        })}
      </div>

      {/* Escape Hatch at bottom */}
      <div className="mt-8 border-t border-[#F1EDEA] pt-6 text-center">
        <button
          onClick={onBack}
          className="text-[#A08E79] hover:text-[#5A7D6C] hover:underline text-sm font-bold inline-flex items-center gap-1.5 transition cursor-pointer"
        >
          <HelpCircle className="w-4 h-4" />
          <span>{t.escapeHatch}</span>
        </button>
      </div>
    </div>
  );
}
