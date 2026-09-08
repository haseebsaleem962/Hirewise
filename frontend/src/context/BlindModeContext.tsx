'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

interface BlindModeContextType {
  blindMode: boolean;
  toggleBlindMode: () => void;
}

const BlindModeContext = createContext<BlindModeContextType>({
  blindMode: false,
  toggleBlindMode: () => {},
});

export function BlindModeProvider({ children }: { children: ReactNode }) {
  const [blindMode, setBlindMode] = useState(false);

  const toggleBlindMode = () => setBlindMode((prev) => !prev);

  return (
    <BlindModeContext.Provider value={{ blindMode, toggleBlindMode }}>
      {children}
    </BlindModeContext.Provider>
  );
}

export const useBlindMode = () => useContext(BlindModeContext);
