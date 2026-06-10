/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { HelpCircle, ArrowRight, Languages, Sparkles, ShieldCheck } from 'lucide-react';
import { Language } from '../types';
import { translations } from '../data/translations';
import LiquidEther from './LiquidEther';
import FlowingMenu from './FlowingMenu';

interface HomeProps {
  currentLanguage: Language;
  setLanguage: (lang: Language) => void;
  onStart: () => void;
}

export default function Home({ currentLanguage, setLanguage, onStart }: HomeProps) {
  const [showHowItWorksModal, setShowHowItWorksModal] = useState(false);
  const t = translations[currentLanguage];

  const categoryPills = [
    { label: t.healthcare, color: 'bg-[#EAF3EE] text-[#3B6651] border-[#C2DEC3]/50' },
    { label: t.engineering, color: 'bg-[#E8F1F5] text-[#34627C] border-[#CCE2F0]/50' },
    { label: t.education, color: 'bg-[#FAF4EB] text-[#865E26] border-[#F3E2C9]/50' },
    { label: t.law, color: 'bg-[#F3EFF9] text-[#5A3886] border-[#DDD1ED]/50' },
    { label: t.trades, color: 'bg-[#FBF1EA] text-[#8D4D20] border-[#F3DCB7]/50' },
  ];

  const pathwaysList = [
    { link: '#', text: t.healthcare, image: 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=400' },
    { link: '#', text: t.engineering, image: 'https://images.unsplash.com/photo-1581094794329-c8112a89af12?auto=format&fit=crop&q=80&w=400' },
    { link: '#', text: t.education, image: 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&q=80&w=400' },
    { link: '#', text: t.law, image: 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&q=80&w=400' }
  ];

  const isRtl = currentLanguage === 'ar' || currentLanguage === 'dr';

  return (
    <div className="relative flex flex-col items-center justify-between py-6 px-2 md:px-4 min-h-screen">
      {/* Absolute background interactive canvas */}
      <div className="absolute inset-0 z-0 overflow-hidden" id="ambient-liquid-container" style={{ pointerEvents: 'auto' }}>
        <LiquidEther
          colors={['#5A7D6C', '#A08E79', '#C2DEC3', '#E1DBD2']}
          mouseForce={15}
          cursorSize={80}
          resolution={0.4}
          autoDemo={true}
          autoSpeed={0.4}
        />
      </div>

      {/* Absolute Language Switcher Top Right */}
      <div className={`absolute top-0 ${isRtl ? 'left-0' : 'right-0'} z-10 flex items-center gap-2 bg-[#E9E5DE]/90 backdrop-blur-xs hover:bg-[#DED9D2] transition px-4 py-2 rounded-full text-stone-700 text-sm font-medium shadow-sm border border-[#E9E5DE]`}>
        <Languages className="w-4 h-4 text-[#A08E79]" />
        <select
          value={currentLanguage}
          onChange={(e) => setLanguage(e.target.value as Language)}
          className="bg-transparent border-none outline-none font-semibold cursor-pointer py-0.5 text-xs md:text-sm text-[#343432]"
          aria-label="Select Language"
        >
          <option value="en" className="bg-white">English (EN)</option>
          <option value="fr" className="bg-white">Français (FR)</option>
          <option value="ar" className="bg-white">العربية (AR)</option>
          <option value="dr" className="bg-white">دری (DR)</option>
        </select>
      </div>

      {/* Main Branding Card */}
      <div className="w-full max-w-2xl bg-white/95 backdrop-blur-md border border-[#E9E5DE]/80 rounded-[40px] p-8 md:p-12 shadow-[0_32px_64px_-16px_rgba(90,125,108,0.1)] mt-16 flex flex-col items-center text-center z-10">
        {/* Logo Icon */}
        <div className="w-14 h-14 bg-[#5A7D6C] rounded-2xl flex items-center justify-center mb-6 shadow-md transition-transform hover:scale-105">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        </div>

        <h1 className="text-4xl md:text-5xl font-bold font-serif text-[#2A2A28] tracking-tight mb-2">
          {t.appName}
        </h1>
        <p className="text-xl md:text-2xl font-serif text-[#5A7D6C] italic tracking-wide mb-6">
          {/* Tagline is "Your skills are real. Let Canada see them." */}
          Your skills are real. <span className="text-[#343432]">Let Canada see them.</span>
        </p>

        <p className="text-[#5F5F5C] leading-relaxed text-sm md:text-base max-w-lg mb-8">
          {t.briefExplanation}
        </p>

        {/* Categories Section */}
        <div className="w-full mb-8">
          <div className="flex flex-wrap justify-center gap-2">
            {categoryPills.map((pill, index) => (
              <span
                key={index}
                className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border ${pill.color} transition-all duration-300 hover:scale-105`}
              >
                {pill.label}
              </span>
            ))}
            <span className="px-3.5 py-1.5 rounded-full text-xs font-semibold border border-transparent bg-[#F7F5F0] text-[#7A7A75] italic">
              + 400 more
            </span>
          </div>
        </div>

        {/* Ethical / Privacy Guarantee ABOVE CTA */}
        <div className="w-full bg-[#F1EDEA]/90 border border-[#E9E5DE] rounded-[24px] p-5 mb-8 text-left flex gap-4 items-start">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shrink-0 shadow-sm border border-[#E9E5DE]/40">
            <ShieldCheck className="w-5 h-5 text-[#A08E79]" />
          </div>
          <div className="space-y-0.5">
            <h3 className="text-xs font-bold text-[#2A2A28] uppercase tracking-wider">
              Privacy First Commitment
            </h3>
            <p className="text-[#7A7A75] text-xs md:text-sm leading-relaxed">
              {t.privacyAboveCTA}
            </p>
          </div>
        </div>

        {/* Primary and Secondary CTA Buttons */}
        <div className="w-full flex flex-col sm:flex-row gap-4 justify-center">
          <button
            id="start-button"
            onClick={onStart}
            className="flex items-center justify-center gap-2.5 px-8 py-4.5 bg-[#5A7D6C] hover:bg-[#4d6b5c] text-white font-bold rounded-[20px] transition shadow-md hover:shadow-lg hover:scale-[1.01] active:scale-[0.98] min-h-[48px] cursor-pointer w-full sm:w-auto"
          >
            <span>{t.startCTA}</span>
            <ArrowRight className="w-5 h-5 opacity-80" />
          </button>

          <button
            id="how-works-button"
            onClick={() => setShowHowItWorksModal(true)}
            className="flex items-center justify-center gap-2 px-6 py-4.5 border border-transparent hover:border-[#DED9D2] text-[#7A7A75] bg-[#F7F5F0] hover:bg-[#E9E5DE] font-semibold rounded-[20px] transition duration-150 active:scale-[0.98] min-h-[48px] cursor-pointer"
          >
            <HelpCircle className="w-4 h-4 text-[#A08E79]" />
            <span>{t.howItWorksCTA}</span>
          </button>
        </div>
      </div>

      {/* Flowing Menu Section */}
      <div className="w-full max-w-2xl mt-8 mb-4 overflow-hidden rounded-[32px] border border-[#E9E5DE] bg-white/90 backdrop-blur-md shadow-xs z-10" id="interactive-pathway-carousel">
        <div className="p-4 bg-[#F7F5F0]/80 border-b border-[#E9E5DE] text-center select-none">
          <h3 className="text-xs font-bold text-[#5A7D6C] uppercase tracking-wider flex items-center justify-center gap-1.5">
            <Sparkles className="w-4 h-4 text-[#A08E79]" /> Explore Interactive Pathways
          </h3>
        </div>
        <div style={{ height: '180px', position: 'relative' }}>
          <FlowingMenu 
            items={pathwaysList} 
            textColor="#5A7D6C"
            bgColor="transparent"
            marqueeBgColor="#5A7D6C"
            marqueeTextColor="#ffffff"
            borderColor="#E9E5DE"
            speed={16}
          />
        </div>
      </div>

      {/* Multilingual How it Works Modal */}
      {showHowItWorksModal && (
        <div className="fixed inset-0 bg-[#343432]/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-[32px] border border-[#E9E5DE] p-6 md:p-8 max-w-xl w-full shadow-2xl relative">
            <h2 className="text-xl md:text-2xl font-bold font-serif text-[#2A2A28] mb-4 flex items-center gap-2 border-b border-[#F1EDEA] pb-3">
              <Sparkles className="w-5 h-5 text-[#5A7D6C]" />
              <span>{t.howItWorksTitle}</span>
            </h2>
            
            <div className="space-y-4 mb-6 text-[#5F5F5C] text-sm leading-relaxed text-left">
              <p>{t.howItWorksText1}</p>
              <p>{t.howItWorksText2}</p>
              <p>{t.howItWorksText3}</p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setShowHowItWorksModal(false)}
                className="px-6 py-2.5 bg-[#5A7D6C] hover:bg-[#4d6b5c] text-white rounded-xl font-bold text-sm transition cursor-pointer"
              >
                {t.closeCTA}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

