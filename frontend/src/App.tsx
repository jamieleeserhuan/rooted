/**
 * App.tsx
 * -------
 * Top-level screen router. Manages which screen is shown and passes
 * data between screens. No fetch() calls here — those live in src/api/.
 */

import { useState } from 'react';
import { AlertCircle, LifeBuoy } from 'lucide-react';
import type { Language, NocMatch, UserInput, Screen } from './types';
import { fetchNocMatches } from './api/match';
import Home from './components/Home';
import InputScreen from './components/InputScreen';
import MatchResults from './components/MatchResults';
import PathwayScreen from './components/PathwayScreen';

export default function App() {
  const [screen, setScreen] = useState<Screen>('home');
  const [currentLanguage, setCurrentLanguage] = useState<Language>('en');

  // Data passed between screens
  const [userInput, setUserInput] = useState<UserInput | null>(null);
  const [matches, setMatches] = useState<NocMatch[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<NocMatch | null>(null);

  // UI state
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);
  const [matchError, setMatchError] = useState('');
  const [isSandboxMode, setIsSandboxMode] = useState(false);

  const isRtl = currentLanguage === 'ar' || currentLanguage === 'dr';

  // Called when user submits their description on InputScreen
  const handleDescriptionSubmit = async (input: UserInput) => {
    setIsLoadingMatches(true);
    setMatchError('');
    setUserInput(input);

    try {
      const data = await fetchNocMatches(input.description, currentLanguage);
      setMatches(data.matches);
      setIsSandboxMode(!!data.fallbackMode);
      setScreen('results');
    } catch (error: any) {
      setMatchError(error.message || 'Could not find matching occupations. Please try again.');
    } finally {
      setIsLoadingMatches(false);
    }
  };

  // Called when user clicks a NOC match card on MatchResults
  const handleSelectMatch = (match: NocMatch) => {
    setSelectedMatch(match);
    setScreen('pathway');
  };

  const handleReset = () => {
    setMatches([]);
    setSelectedMatch(null);
    setMatchError('');
    setScreen('input');
  };

  return (
    <div
      className="min-h-screen bg-[#F7F5F0] text-[#343432] antialiased py-6 px-4 md:px-8 flex flex-col justify-between"
      dir={isRtl ? 'rtl' : 'ltr'}
    >
      {/* Header */}
      <header className="w-full max-w-4xl mx-auto flex items-center justify-between border-b border-[#E9E5DE] pb-5 mb-5">
        <button
          onClick={() => setScreen('home')}
          className="flex items-center gap-3 cursor-pointer select-none group"
        >
          <div className="w-10 h-10 bg-[#5A7D6C] rounded-xl flex items-center justify-center text-white font-bold group-hover:scale-105 transition-transform shadow-sm">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <span className="font-serif font-bold text-2xl tracking-tight text-[#2A2A28]">Rooted</span>
        </button>

        <div className="flex items-center gap-4">
          {import.meta.env.VITE_USE_MOCK === 'true' && (
            <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full">
              Mock mode
            </span>
          )}
          <a
            href="https://github.com/jamieleeserhuan/rooted"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#A08E79] hover:text-[#5A7D6C] transition p-1"
          >
            <LifeBuoy className="w-5 h-5" />
          </a>
        </div>
      </header>

      {/* Main content */}
      <main className="w-full max-w-4xl mx-auto flex-1 flex flex-col justify-center py-6">

        {/* Error banner — shown above any screen */}
        {matchError && (
          <div className="w-full max-w-2xl mx-auto mb-6 p-5 border border-red-200 bg-red-50 text-red-800 rounded-2xl text-sm font-semibold flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-700 shrink-0 mt-0.5" />
            <div>
              <p>{matchError}</p>
              <button
                onClick={() => setMatchError('')}
                className="text-xs text-red-900 border border-red-300 px-2 py-0.5 rounded mt-2 hover:bg-white transition"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        {screen === 'home' && (
          <Home
            currentLanguage={currentLanguage}
            setLanguage={setCurrentLanguage}
            onStart={() => setScreen('input')}
          />
        )}

        {screen === 'input' && (
          <InputScreen
            currentLanguage={currentLanguage}
            onBack={() => setScreen('home')}
            onSubmit={handleDescriptionSubmit}
            isLoading={isLoadingMatches}
          />
        )}

        {screen === 'results' && (
          <MatchResults
            currentLanguage={currentLanguage}
            matches={matches}
            onBack={() => setScreen('input')}
            onSelectMatch={handleSelectMatch}
            isSandboxMode={isSandboxMode}
          />
        )}

        {screen === 'pathway' && selectedMatch && userInput && (
          <PathwayScreen
            currentLanguage={currentLanguage}
            match={selectedMatch}
            userInput={userInput}
            onBack={() => setScreen('results')}
            onReset={handleReset}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="w-full max-w-4xl mx-auto border-t border-[#E9E5DE] pt-5 mt-10 flex flex-col sm:flex-row items-center justify-between text-[10px] font-bold uppercase tracking-[0.16em] text-[#A08E79] gap-3">
        <div className="flex flex-wrap justify-center sm:justify-start gap-6">
          <span>NOC Database 2024</span>
          <span>ESDC Regulated Tools</span>
          <span>FCRP Bridging Programs</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#5A7D6C]" />
          <span>AI Integrity: Verified Small Model</span>
        </div>
      </footer>
    </div>
  );
}
