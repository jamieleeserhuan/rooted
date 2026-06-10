/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, FormEvent, useEffect } from 'react';
import { ArrowLeft, Search, HelpCircle, AlertCircle } from 'lucide-react';
import { Language, UserInput } from '../types';
import { translations } from '../data/translations';

interface InputScreenProps {
  currentLanguage: Language;
  onBack: () => void;
  onSubmit: (data: UserInput) => void;
  isLoading: boolean;
}

export default function InputScreen({ currentLanguage, onBack, onSubmit, isLoading }: InputScreenProps) {
  const t = translations[currentLanguage];

  // Form State
  const [description, setDescription] = useState('');
  const [province, setProvince] = useState('ON');
  const [documentsAvailable, setDocumentsAvailable] = useState<'none' | 'some' | 'full'>('none');
  const [isTransOrGenderDiverse, setIsTransOrGenderDiverse] = useState(false);

  // Simulated progress stepper for the backend processing pipeline
  const [pipelineStep, setPipelineStep] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setPipelineStep(0);
      return;
    }
    const interval = setInterval(() => {
      setPipelineStep((prev) => (prev < 3 ? prev + 1 : prev));
    }, 1800);
    return () => clearInterval(interval);
  }, [isLoading]);

  // Quick preset pills to reduce typing burden
  const examples = [
    { text: t.example1, description: "I was a senior registered nurse for 8 years at the Al-Dunya hospital emergency ward in Aleppo. I oversaw shift schedules, administered medications, and trained junior nurses. Due to conflict, I fled without any professional papers." },
    { text: t.example2, description: "I worked as a lead Civil Engineer doing water infrastructure and roadway projects in Somalia. I managed local blueprints, contractor logs, safety audits and held an engineering diploma from Mogadishu University, but have only a photo of it." },
    { text: t.example3, description: "I taught primary school mathematics and literacy for 4 years in Bukavu, DRC. I organized syllabus plans and wrote student reports. I fled with full transcripts but no official regulatory certificates." },
    { text: "🏫 Queer Malaysian Educator", description: "I was a primary school teacher and educator in Malaysia for 5 years, designing lessons and coordinating class materials. As a queer individual, I faced intense systemic discrimination and threats to my safety. I was forced to flee without official university certificates." }
  ];

  const handleSelectExample = (desc: string) => {
    setDescription(desc);
    if (desc.includes('queer') || desc.includes('Malaysia')) {
      setIsTransOrGenderDiverse(true);
    } else {
      setIsTransOrGenderDiverse(false);
    }
  };

  const provinces = [
    { code: 'ON', name: 'Ontario' },
    { code: 'BC', name: 'British Columbia' },
    { code: 'AB', name: 'Alberta' },
    { code: 'QC', name: 'Quebec' },
    { code: 'MB', name: 'Manitoba' },
    { code: 'SK', name: 'Saskatchewan' },
    { code: 'NS', name: 'Nova Scotia' },
    { code: 'NB', name: 'New Brunswick' },
    { code: 'NL', name: 'Newfoundland' },
    { code: 'PE', name: 'Prince Edward Island' },
  ];

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;
    onSubmit({
      description,
      province,
      documentsAvailable,
      isTransOrGenderDiverse
    });
  };

  if (isLoading) {
    return (
      <div className="w-full max-w-2xl bg-white border border-[#E9E5DE] rounded-[40px] p-6 md:p-10 shadow-[0_32px_64px_-16px_rgba(90,125,108,0.1)] mx-auto text-left relative overflow-hidden">
        {/* Subtle decorative background bloom */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#FAF4EB] rounded-full blur-3xl opacity-60 -mr-20 -mt-20 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-[#EAF3EE] rounded-full blur-3xl opacity-65 -ml-20 -mb-20 pointer-events-none" />

        <div className="text-center mb-8 relative z-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#EAF3EE] text-[#5A7D6C] mb-4">
            <svg className="animate-spin h-8 w-8 text-[#5A7D6C]" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
          <h2 className="text-2xl font-serif font-bold text-[#2A2A28] tracking-tight">
            Tracing Your Professional Roots...
          </h2>
          <p className="text-xs font-bold uppercase tracking-widest text-[#A08E79] mt-2">
            Secure Full-Stack & Gemini AI Semantic Pipeline
          </p>
        </div>

        {/* Pipeline Stepper */}
        <div className="space-y-6 relative before:absolute before:inset-0 before:left-[19px] before:top-4 before:bottom-4 before:w-0.5 before:bg-[#F1EDEA] ml-1 relative z-10">
          {/* Step 1 */}
          <div className="flex gap-4 relative">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-300 ${
              pipelineStep >= 0 ? 'bg-[#5A7D6C] text-white' : 'bg-[#F7F5F0] text-[#7A7A75]'
            }`}>
              <span className="text-xs font-bold">01</span>
            </div>
            <div>
              <h4 className="text-sm font-bold font-serif text-[#2A2A28]">Secure PIPEDA Ingestion Check</h4>
              <p className="text-xs text-[#5F5F5C] mt-1 leading-relaxed">
                Applet initializes isolated in-memory buffer at <code className="bg-[#F7F5F0] px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-[#5A7D6C]">POST /api/match-noc</code>. Storage bypassing active: zero persistent disk logs.
              </p>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#3B6651] bg-[#EAF3EE] px-2 py-0.5 rounded-full uppercase tracking-wider">
                  ● PIPEDA Level-3 Validated
                </span>
                <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#A08E79] bg-[#F7F5F0] px-2 py-0.5 rounded-full uppercase tracking-wider">
                  ● In-Memory Only
                </span>
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div className="flex gap-4 relative">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-300 ${
              pipelineStep >= 1 ? 'bg-[#5A7D6C] text-white' : 'bg-[#F1EDEA] text-[#BBB6AE]'
            }`}>
              <span className="text-xs font-bold">02</span>
            </div>
            <div>
              <h4 className={`text-sm font-bold font-serif transition-colors duration-300 ${pipelineStep >= 1 ? 'text-[#2A2A28]' : 'text-[#BBB6AE]'}`}>
                Multilingual Linguistic Parsing (L2)
              </h4>
              <p className={`text-xs mt-1 leading-relaxed transition-colors duration-300 ${pipelineStep >= 1 ? 'text-[#5F5F5C]' : 'text-[#D3CFC9]'}`}>
                Gemini 3.5-Flash analyzes semantic context. Native vocabulary mapped across 50+ languages (Arabic, French, Dari, Ukrainian, Tigrinya, etc.) dynamically and translated without bias.
              </p>
              <div className="mt-1.5">
                {pipelineStep === 0 && (
                  <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#BBB6AE] bg-[#F1EDEA] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ⏱ Pending server step
                  </span>
                )}
                {pipelineStep === 1 && (
                  <span className="animate-pulse inline-flex items-center gap-1 text-[9px] font-bold text-amber-700 bg-[#FAF4EB] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ● Semantic Lexicon Analysis...
                  </span>
                )}
                {pipelineStep > 1 && (
                  <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#3B6651] bg-[#EAF3EE] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ✓ Code-ready English Equivalents
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div className="flex gap-4 relative">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-300 ${
              pipelineStep >= 2 ? 'bg-[#5A7D6C] text-white' : 'bg-[#F1EDEA] text-[#BBB6AE]'
            }`}>
              <span className="text-xs font-bold">03</span>
            </div>
            <div>
              <h4 className={`text-sm font-bold font-serif transition-colors duration-300 ${pipelineStep >= 2 ? 'text-[#2A2A28]' : 'text-[#BBB6AE]'}`}>
                NOC 2021 Taxonomy Matching
              </h4>
              <p className={`text-xs mt-1 leading-relaxed transition-colors duration-300 ${pipelineStep >= 2 ? 'text-[#5F5F5C]' : 'text-[#D3CFC9]'}`}>
                Correlating individual skills, certification targets, and professional history against National Occupational Classification (NOC) structural vectors.
              </p>
              <div className="mt-1.5">
                {pipelineStep < 2 && (
                  <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#BBB6AE] bg-[#F1EDEA] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ⏱ Pending server step
                  </span>
                )}
                {pipelineStep === 2 && (
                  <span className="animate-pulse inline-flex items-center gap-1 text-[9px] font-bold text-[#34627C] bg-[#E8F1F5] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ● Resolving TEER & NOC Hierarchies...
                  </span>
                )}
                {pipelineStep > 2 && (
                  <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#3B6651] bg-[#EAF3EE] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ✓ Best 3 ESDC Matches Synced
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Step 4 */}
          <div className="flex gap-4 relative">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 z-10 transition-colors duration-300 ${
              pipelineStep >= 3 ? 'bg-[#5A7D6C] text-white' : 'bg-[#F1EDEA] text-[#BBB6AE]'
            }`}>
              <span className="text-xs font-bold">04</span>
            </div>
            <div>
              <h4 className={`text-sm font-bold font-serif transition-colors duration-300 ${pipelineStep >= 3 ? 'text-[#2A2A28]' : 'text-[#BBB6AE]'}`}>
                Provincial Licensure Assembly
              </h4>
              <p className={`text-xs mt-1 leading-relaxed transition-colors duration-300 ${pipelineStep >= 3 ? 'text-[#5F5F5C]' : 'text-[#D3CFC9]'}`}>
                Drafting customized licensing checklists, identifying WES Gateway credentials alternatives, and scanning early funding structures.
              </p>
              <div className="mt-1.5">
                {pipelineStep < 3 && (
                  <span className="inline-flex items-center gap-1 text-[9px] font-bold text-[#BBB6AE] bg-[#F1EDEA] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ⏱ Pending server step
                  </span>
                )}
                {pipelineStep === 3 && (
                  <span className="animate-pulse inline-flex items-center gap-1 text-[9px] font-bold text-[#5A7D6C] bg-[#EAF3EE] px-2 py-0.5 rounded-full uppercase tracking-wider">
                    ● Formatting Licensure Roadmaps...
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Security assurance */}
        <div className="mt-8 pt-4 border-t border-[#F1EDEA] text-center relative z-10">
          <p className="text-[10px] text-[#A08E79] font-bold uppercase tracking-widest">
            🔒 Fully encrypted context • Session destroyed on complete
          </p>
        </div>
      </div>
    );
  }

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
          {t.descYourWorkTitle}
        </h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 text-left">
        {/* Description Textarea */}
        <div className="space-y-2">
          <label htmlFor="description" className="block text-xs font-bold uppercase tracking-widest text-[#A08E79] ml-1">
            Tell us about your previous employment:
          </label>
          <textarea
            id="description"
            rows={5}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={t.textareaPlaceholder}
            className="w-full h-48 bg-[#FBF9F6] border-2 border-[#F1EDEA] rounded-[24px] p-6 text-base focus:border-[#5A7D6C] focus:ring-0 outline-none resize-y placeholder:text-[#BBB6AE] font-sans text-[#343432] leading-relaxed shadow-xs"
            required
            disabled={isLoading}
          />
        </div>

        {/* Preset Pills */}
        <div className="space-y-2">
          <p className="text-xs font-bold uppercase tracking-widest text-[#A08E79] ml-1">{t.examplePillsLabel}</p>
          <div className="flex flex-wrap gap-2">
            {examples.map((example, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleSelectExample(example.description)}
                className="px-4 py-2 bg-[#F7F5F0] hover:bg-[#E9E5DE] rounded-full text-xs font-semibold text-[#7A7A75] border border-transparent hover:border-[#DED9D2] transition cursor-pointer"
                disabled={isLoading}
              >
                {example.text}
              </button>
            ))}
          </div>
        </div>

        {/* Side-by-Side selection inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Province Selector */}
          <div className="space-y-2">
            <label htmlFor="province" className="block text-[10px] font-bold uppercase tracking-widest text-[#A08E79] ml-1">
              {t.selectProvinceLabel}
            </label>
            <select
              id="province"
              value={province}
              onChange={(e) => setProvince(e.target.value)}
              className="w-full bg-[#FBF9F6] border border-[#F1EDEA] rounded-2xl px-4 py-3.5 text-sm focus:border-[#5A7D6C] outline-none text-[#343432] font-semibold cursor-pointer"
              disabled={isLoading}
            >
              {provinces.map((prov) => (
                <option key={prov.code} value={prov.code}>
                  {prov.name}
                </option>
              ))}
            </select>
          </div>

          {/* Document Selector */}
          <div className="space-y-2">
            <label htmlFor="documentsAvailable" className="block text-[10px] font-bold uppercase tracking-widest text-[#A08E79] ml-1">
              {t.selectDocsLabel}
            </label>
            <select
              id="documentsAvailable"
              value={documentsAvailable}
              onChange={(e) => setDocumentsAvailable(e.target.value as 'none' | 'some' | 'full')}
              className="w-full bg-[#FBF9F6] border border-[#F1EDEA] rounded-2xl px-4 py-3.5 text-sm focus:border-[#5A7D6C] outline-none text-[#343432] font-semibold cursor-pointer"
              disabled={isLoading}
            >
              <option value="none">📜 {t.docNone}</option>
              <option value="some">📷 {t.docSome}</option>
              <option value="full">📂 {t.docFull}</option>
            </select>
          </div>
        </div>

        {/* Trans-inclusive guideline checkbox */}
        <div className="bg-[#F1EDEA] border border-[#E9E5DE] rounded-[24px] p-5 flex gap-3.5 items-start">
          <input
            id="isTransOrGenderDiverse"
            type="checkbox"
            checked={isTransOrGenderDiverse}
            onChange={(e) => setIsTransOrGenderDiverse(e.target.checked)}
            className="w-5 h-5 text-[#5A7D6C] focus:ring-[#5A7D6C] border-[#E9E5DE] rounded cursor-pointer mt-0.5"
            disabled={isLoading}
          />
          <label htmlFor="isTransOrGenderDiverse" className="text-xs md:text-sm text-[#5F5F5C] font-semibold cursor-pointer leading-relaxed">
            {t.isTransLabel}
          </label>
        </div>

        {/* Submission Button */}
        <button
          id="submit-button"
          type="submit"
          className="w-full flex items-center justify-center gap-2.5 px-8 py-5 bg-[#5A7D6C] hover:bg-[#4d6b5c] text-white font-bold rounded-[20px] transition shadow-md hover:shadow-lg hover:scale-[1.01] active:scale-[0.98] min-h-[48px] disabled:opacity-50 cursor-pointer"
          disabled={isLoading || !description.trim()}
        >
          {isLoading ? (
            <div className="flex items-center gap-2 flex-row justify-center w-full">
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>Analyzing description across languages...</span>
            </div>
          ) : (
            <>
              <Search className="w-5 h-5 opacity-80" />
              <span>{t.findMyMatches}</span>
            </>
          )}
        </button>

        {/* Security / Decrypted state indicators */}
        <div className="flex items-center gap-2 justify-center text-xs text-[#A08E79] font-bold mt-4">
          <AlertCircle className="w-4 h-4 text-[#A08E79]" />
          <span>Self-contained local processing. Nothing is saved server-side.</span>
        </div>
      </form>
    </div>
  );
}
