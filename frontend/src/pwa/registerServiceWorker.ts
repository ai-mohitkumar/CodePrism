// Service Worker registration and PWA install prompt handler

export interface PWAInstallEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

let deferredPrompt: PWAInstallEvent | null = (window as any).deferredPWAInstallPrompt || null;
const installListeners: Array<(prompt: PWAInstallEvent | null) => void> = [];

export const registerServiceWorker = () => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker
      .register('/sw.js')
      .then((reg) => {
        console.log('[CodePrism PWA] Service Worker registered successfully, scope:', reg.scope);
      })
      .catch((err) => {
        console.warn('[CodePrism PWA] Service Worker registration failed:', err);
      });
  }

  // Listen for early captured prompt
  window.addEventListener('pwa-prompt-ready', (e: any) => {
    deferredPrompt = e.detail;
    (window as any).deferredPWAInstallPrompt = e.detail;
    installListeners.forEach((listener) => listener(deferredPrompt));
  });

  // Capture beforeinstallprompt event
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e as PWAInstallEvent;
    (window as any).deferredPWAInstallPrompt = deferredPrompt;
    installListeners.forEach((listener) => listener(deferredPrompt));
  });

  window.addEventListener('appinstalled', () => {
    console.log('[CodePrism PWA] App was installed successfully on this system');
    deferredPrompt = null;
    (window as any).deferredPWAInstallPrompt = null;
    installListeners.forEach((listener) => listener(null));
  });
};

export const onInstallPromptChange = (callback: (prompt: PWAInstallEvent | null) => void) => {
  installListeners.push(callback);
  callback(deferredPrompt || (window as any).deferredPWAInstallPrompt || null);
  return () => {
    const idx = installListeners.indexOf(callback);
    if (idx !== -1) installListeners.splice(idx, 1);
  };
};

export const hasDeferredPrompt = (): boolean => {
  return !!(deferredPrompt || (window as any).deferredPWAInstallPrompt);
};

export const triggerPWAInstall = async (): Promise<boolean> => {
  const promptEvent = deferredPrompt || (window as any).deferredPWAInstallPrompt;
  if (!promptEvent) {
    return false;
  }
  try {
    await promptEvent.prompt();
    const choice = await promptEvent.userChoice;
    deferredPrompt = null;
    (window as any).deferredPWAInstallPrompt = null;
    installListeners.forEach((listener) => listener(null));
    return choice.outcome === 'accepted';
  } catch (err) {
    console.error('[CodePrism PWA] Error invoking install prompt:', err);
    return false;
  }
};
