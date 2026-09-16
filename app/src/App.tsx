import React, { useState, useEffect, useRef } from 'react';
import { AgrometProvider, useAgromet } from './context/AgrometContext';
import { MapBackground } from './components/MapBackground';
import { MapSearchBox } from './components/MapSearchBox';
import { MapGlassPanel } from './components/MapGlassPanel';
import { AppLanguage, AppScreen, FarmerProfile, CropItem } from './types';
import { DEFAULT_FARMER_PROFILE, INITIAL_CROPS } from './data/mockData';
import { LanguageModal } from './components/LanguageModal';

// Screens
import { SplashScreen } from './screens/SplashScreen';
import { LanguageScreen } from './screens/LanguageScreen';
import { AddLocationScreen } from './screens/AddLocationScreen';
import { FarmerProfileSetupScreen } from './screens/FarmerProfileSetupScreen';
import { AddCropScreen } from './screens/AddCropScreen';
import { HomeScreen } from './screens/HomeScreen';
import { WeatherScreen } from './screens/WeatherScreen';
import { MyCropsScreen } from './screens/MyCropsScreen';
import { CropDetailRiceScreen } from './screens/CropDetailRiceScreen';
import { CropDetailWheatScreen } from './screens/CropDetailWheatScreen';
import { AdvisoryHubScreen } from './screens/AdvisoryHubScreen';
import { FertilizerAdvisoryScreen } from './screens/FertilizerAdvisoryScreen';
import { IrrigationAdvisoryScreen } from './screens/IrrigationAdvisoryScreen';
import { CropSelectorScreen } from './screens/CropSelectorScreen';
import { AlertDetailsScreen } from './screens/AlertDetailsScreen';
import { FarmerProfileViewScreen } from './screens/FarmerProfileViewScreen';

export default function App() {
  return (
    <AgrometProvider>
      <ParamAppShell />
    </AgrometProvider>
  );
}

function ParamAppShell() {
  const { prediction, loading, currentCoords, setLocation, domainFallbackNote, requestLocation, gpsStatus } = useAgromet();
  const [showSplash, setShowSplash] = useState<boolean>(true);
  const [sheetOpen, setSheetOpen] = useState<boolean>(false);
  const [windowWidth, setWindowWidth] = useState<number>(() =>
    typeof window !== 'undefined' ? window.innerWidth : 1200
  );
  const touchStartY = useRef<number | null>(null);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMobile = windowWidth < 768;

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartY.current === null) return;
    const deltaY = e.changedTouches[0].clientY - touchStartY.current;
    if (deltaY < -30) {
      setSheetOpen(true);
    } else if (deltaY > 30) {
      setSheetOpen(false);
    }
    touchStartY.current = null;
  };

  // Application State with LocalStorage fallbacks
  const [language, setLanguage] = useState<AppLanguage>(() => {
    const saved = localStorage.getItem('param_lang');
    return (saved as AppLanguage) || 'mr';
  });

  const [currentScreen, setCurrentScreen] = useState<AppScreen>(() => {
    const saved = localStorage.getItem('param_screen');
    // Default to home screen on app start (splash is rendered topmost overlay)
    return (saved as AppScreen) && saved !== 'splash' ? (saved as AppScreen) : 'home';
  });

  const [farmerProfile, setFarmerProfile] = useState<FarmerProfile>(() => {
    try {
      const saved = localStorage.getItem('param_farmer');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
    return DEFAULT_FARMER_PROFILE;
  });

  const [crops, setCrops] = useState<CropItem[]>(() => {
    try {
      const saved = localStorage.getItem('param_crops');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error(e);
    }
    return INITIAL_CROPS;
  });

  const [activeAdvisoryCropId, setActiveAdvisoryCropId] = useState<string>('rice-1');
  const [isLanguageModalOpen, setIsLanguageModalOpen] = useState<boolean>(false);
  const [navigationHistory, setNavigationHistory] = useState<AppScreen[]>([]);

  // Keep localStorage in sync
  useEffect(() => {
    localStorage.setItem('param_lang', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('param_screen', currentScreen);
  }, [currentScreen]);

  useEffect(() => {
    localStorage.setItem('param_farmer', JSON.stringify(farmerProfile));
  }, [farmerProfile]);

  useEffect(() => {
    localStorage.setItem('param_crops', JSON.stringify(crops));
  }, [crops]);

  // Navigate helper with history stack
  const navigateTo = (screen: AppScreen) => {
    setNavigationHistory((prev) => [...prev, currentScreen]);
    setCurrentScreen(screen);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const navigateBack = () => {
    if (navigationHistory.length > 0) {
      const previous = navigationHistory[navigationHistory.length - 1];
      setNavigationHistory((prev) => prev.slice(0, -1));
      setCurrentScreen(previous);
    } else {
      setCurrentScreen('home');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const updateProfile = (updated: Partial<FarmerProfile>) => {
    setFarmerProfile((prev) => ({ ...prev, ...updated }));
  };

  const addOrUpdateCrop = (crop: CropItem) => {
    setCrops((prev) => {
      const existingIdx = prev.findIndex((c) => c.id === crop.id);
      if (existingIdx >= 0) {
        const copy = [...prev];
        copy[existingIdx] = crop;
        return copy;
      }
      return [crop, ...prev];
    });
    setActiveAdvisoryCropId(crop.id);
  };

  const activeCrop =
    crops.find((c) => c.id === activeAdvisoryCropId) || crops[0] || INITIAL_CROPS[0];

  return (
    <div className="w-full h-screen overflow-hidden relative bg-transparent pointer-events-none">
      {/* PARAM Splash: topmost fixed overlay, auto-dismisses with minimum hold 1200ms and 400ms fadeout */}
      {showSplash && (
        <SplashScreen onDismiss={() => setShowSplash(false)} />
      )}

      {/* 1. MapBackground mounted once as first child */}
      <MapBackground
        center={currentCoords}
        onPick={setLocation}
        onLocate={requestLocation}
      />

      {/* 2. Search box & Glass panel on map layer (zIndex: 20, hidden when sheet is FULL) */}
      {!sheetOpen && (
        <>
          <MapSearchBox
            onSelectResult={(lat, lon) => setLocation(lat, lon)}
            isMobile={isMobile}
          />
          <MapGlassPanel
            prediction={prediction}
            loading={loading}
            domainFallbackNote={domainFallbackNote}
            isMobile={isMobile}
          />
          {/* Temporary visible GPS debug chip (zIndex: 30, readable on phone without DevTools) */}
          <div
            className="fixed left-4 top-[72px] max-w-[48vw] md:max-w-md px-2.5 py-1.5 rounded-lg bg-black/90 text-emerald-400 font-mono text-[11px] leading-tight shadow-xl border border-neutral-700 pointer-events-auto select-all break-words"
            style={{ zIndex: 30 }}
          >
            {gpsStatus}
          </div>
        </>
      )}

      {/* 3. AppSheet wrapping the PARAM app */}
      <div
        className="app-sheet pointer-events-auto"
        style={{
          position: 'fixed',
          left: sheetOpen ? 0 : (isMobile ? 0 : '50%'),
          transform: sheetOpen ? 'none' : (isMobile ? 'none' : 'translateX(-50%)'),
          bottom: 0,
          width: sheetOpen ? '100vw' : '100%',
          maxWidth: sheetOpen ? '100vw' : (isMobile ? '100%' : '430px'),
          height: sheetOpen ? '100vh' : '140px',
          zIndex: 10,
          borderRadius: sheetOpen ? 0 : '24px 24px 0 0',
          background: 'rgba(255, 255, 255, 0.92)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          boxShadow: '0 -8px 32px rgba(0, 0, 0, 0.18)',
          transition: 'all 300ms cubic-bezier(0.32, 0.72, 0, 1)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        {/* PEEK STATE (sheetOpen = false): height 140px */}
        {!sheetOpen && (
          <div
            className="w-full h-full flex flex-col justify-between p-4 cursor-pointer select-none"
            onClick={() => setSheetOpen(true)}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
          >
            {/* 40px drag handle / grab bar */}
            <div className="w-full flex justify-center pt-1 pb-2">
              <div className="w-10 h-1.5 bg-neutral-400/70 rounded-full" />
            </div>

            {/* Current village name + taluka line and current temp */}
            <div className="flex items-center justify-between pb-2 px-1">
              <div className="min-w-0 flex-1 pr-3">
                <div className="flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[20px] text-primary">location_on</span>
                  <h3 className="text-base font-bold text-neutral-900 truncate">
                    {prediction ? prediction.name : 'Kolhapur (M Corp.)'}
                  </h3>
                </div>
                <p className="text-xs text-neutral-600 truncate pl-6">
                  {prediction
                    ? `${prediction.state} • Elev: ${prediction.elevation_m.toFixed(0)}m • ${prediction.inside_validated_band ? 'Validated' : 'Extrapolated'}`
                    : 'Kolhapur, Maharashtra'}
                </p>
                {domainFallbackNote && prediction?.in_domain === false && (
                  <p className="text-[10px] text-amber-700 font-medium pl-6 truncate mt-0.5">
                    {domainFallbackNote}
                  </p>
                )}
              </div>

              <div className="text-right shrink-0">
                <span className="text-2xl font-black text-neutral-900">
                  {prediction ? `${prediction.temp_c.toFixed(1)}°C` : '24.4°C'}
                </span>
                <span className="block text-[10px] text-neutral-500 font-medium">
                  seasonal mean (JJAS)
                </span>
              </div>
            </div>
          </div>
        )}

        {/* FULL STATE (sheetOpen = true): height 100vh */}
        {sheetOpen && (
          <div className="w-full h-full flex flex-col relative overflow-hidden">
            {/* Top drag bar / chevron to collapse */}
            <div
              className="w-full h-8 shrink-0 flex items-center justify-between px-4 cursor-pointer select-none bg-surface/90 border-b border-outline-variant/20 z-50"
              onClick={() => setSheetOpen(false)}
              onTouchStart={handleTouchStart}
              onTouchEnd={handleTouchEnd}
              title="Tap or drag down to view map"
            >
              <div className="flex items-center gap-1.5 text-xs font-semibold text-neutral-600 truncate">
                <span className="material-symbols-outlined text-[16px] text-primary">location_on</span>
                <span className="truncate">{prediction ? `${prediction.name}, ${prediction.state}` : 'PARAM'}</span>
              </div>

              {/* 40px grab bar */}
              <div className="w-10 h-1.5 bg-neutral-400/70 rounded-full" />

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setSheetOpen(false);
                }}
                className="text-neutral-500 hover:text-neutral-800 flex items-center p-0.5 rounded"
                aria-label="Collapse sheet"
              >
                <span className="material-symbols-outlined text-[20px]">keyboard_arrow_down</span>
              </button>
            </div>

            {/* Scrollable PARAM column: all 16 screens + bottom nav */}
            <div
              className="flex-1 overflow-y-auto overscroll-contain relative min-h-0"
              style={{ transform: 'translateZ(0)' }}
            >
        {/* Render Screen according to currentScreen */}
        {currentScreen === 'splash' && (
          <HomeScreen
            onNavigate={(screen) => navigateTo(screen)}
            language={language}
            farmerProfile={farmerProfile}
            onOpenProfile={() => navigateTo('profile_view')}
            onToggleLanguage={() => setIsLanguageModalOpen(true)}
          />
        )}

        {currentScreen === 'language' && (
          <LanguageScreen
            currentLanguage={language}
            onSelectLanguage={(lang) => setLanguage(lang)}
            onContinue={() => navigateTo('add_location')}
            onBack={() => navigateTo('home')}
          />
        )}

        {currentScreen === 'add_location' && (
          <AddLocationScreen
            farmerProfile={farmerProfile}
            onUpdateProfile={updateProfile}
            onContinue={() => navigateTo('farmer_profile_setup')}
            onBack={() => navigateTo('language')}
            language={language}
          />
        )}

        {currentScreen === 'farmer_profile_setup' && (
          <FarmerProfileSetupScreen
            farmerProfile={farmerProfile}
            onUpdateProfile={updateProfile}
            onContinue={() => navigateTo('add_crop')}
            onBack={() => navigateTo('add_location')}
            onChangeLocation={() => navigateTo('add_location')}
            language={language}
          />
        )}

        {currentScreen === 'add_crop' && (
          <AddCropScreen
            crops={crops}
            onAddOrUpdateCrop={addOrUpdateCrop}
            onContinueToHome={() => navigateTo('home')}
            onBack={navigateBack}
            language={language}
            isInitialOnboarding={navigationHistory.includes('farmer_profile_setup')}
          />
        )}

        {currentScreen === 'home' && (
          <HomeScreen
            farmerProfile={farmerProfile}
            language={language}
            onNavigate={(screen) => navigateTo(screen)}
            onToggleLanguage={() => setIsLanguageModalOpen(true)}
          />
        )}

        {currentScreen === 'weather' && (
          <WeatherScreen
            language={language}
            onNavigate={(screen) => navigateTo(screen)}
            onToggleLanguage={() => setIsLanguageModalOpen(true)}
            onOpenProfile={() => navigateTo('farmer_profile')}
          />
        )}

        {currentScreen === 'crops' && (
          <MyCropsScreen
            crops={crops}
            onOpenCropDetail={(cropId) => {
              if (cropId.includes('wheat')) {
                navigateTo('crop_detail_wheat');
              } else {
                navigateTo('crop_detail_rice');
              }
            }}
            onOpenAddCrop={() => navigateTo('add_crop')}
            onNavigate={(screen) => navigateTo(screen)}
            language={language}
            onToggleLanguage={() => setIsLanguageModalOpen(true)}
            onOpenProfile={() => navigateTo('farmer_profile')}
          />
        )}

        {currentScreen === 'crop_detail_rice' && (
          <CropDetailRiceScreen
            onBack={navigateBack}
            onNavigate={(screen) => navigateTo(screen)}
            language={language}
          />
        )}

        {currentScreen === 'crop_detail_wheat' && (
          <CropDetailWheatScreen
            onBack={navigateBack}
            onNavigate={(screen) => navigateTo(screen)}
            language={language}
          />
        )}

        {currentScreen === 'advisory' && (
          <AdvisoryHubScreen
            activeCrop={activeCrop}
            onOpenCropSelector={() => navigateTo('crop_selector')}
            onNavigate={(screen) => navigateTo(screen)}
            language={language}
            onToggleLanguage={() => setIsLanguageModalOpen(true)}
            onOpenProfile={() => navigateTo('farmer_profile')}
          />
        )}

        {currentScreen === 'advisory_fertilizer' && (
          <FertilizerAdvisoryScreen
            onBack={navigateBack}
            language={language}
          />
        )}

        {currentScreen === 'advisory_irrigation' && (
          <IrrigationAdvisoryScreen
            onBack={navigateBack}
            language={language}
          />
        )}

        {currentScreen === 'crop_selector' && (
          <CropSelectorScreen
            crops={crops}
            activeCropId={activeAdvisoryCropId}
            onSelectCrop={(id) => setActiveAdvisoryCropId(id)}
            onAddNewCrop={() => navigateTo('add_crop')}
            onClose={() => navigateTo('advisory')}
            language={language}
          />
        )}

        {currentScreen === 'alerts' && (
          <AlertDetailsScreen
            onBack={navigateBack}
            onNavigate={(screen) => navigateTo(screen)}
            language={language}
          />
        )}

        {currentScreen === 'farmer_profile' && (
          <FarmerProfileViewScreen
            farmerProfile={farmerProfile}
            onUpdateProfile={updateProfile}
            onBack={() => navigateTo('home')}
            language={language}
            onToggleLanguage={() => setIsLanguageModalOpen(true)}
            onChangeLocation={() => navigateTo('add_location')}
          />
        )}

        {/* Global Language Selection Modal */}
        <LanguageModal
          isOpen={isLanguageModalOpen}
          currentLanguage={language}
          onClose={() => setIsLanguageModalOpen(false)}
          onSelectLanguage={(lang) => {
            setLanguage(lang);
            setIsLanguageModalOpen(false);
          }}
        />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
