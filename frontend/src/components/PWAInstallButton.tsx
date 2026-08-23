import React, { useState, useEffect } from 'react';
import { 
  Download, 
  Smartphone, 
  Share, 
  PlusSquare, 
  X, 
  Monitor, 
  CheckCircle2, 
  Sparkles,
  ArrowRight,
  QrCode,
  Copy,
  Check,
  PackageCheck,
  Wifi,
  Laptop
} from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { onInstallPromptChange, triggerPWAInstall, hasDeferredPrompt } from '../pwa/registerServiceWorker';
import axios from 'axios';

interface PWAInstallProps {
  mode?: 'pc' | 'mobile' | 'all';
  isMobileDrawer?: boolean;
}

export const PWAInstallButton: React.FC<PWAInstallProps> = ({ 
  mode = 'all',
  isMobileDrawer = false 
}) => {
  const [canNativeInstall, setCanNativeInstall] = useState<boolean>(false);
  const [showMobileModal, setShowMobileModal] = useState<boolean>(false);
  const [isStandalone, setIsStandalone] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [mobileUrl, setMobileUrl] = useState<string>('');

  useEffect(() => {
    // Check if running inside installed standalone PWA
    const isStandaloneMode = 
      window.matchMedia('(display-mode: standalone)').matches || 
      (window.navigator as any).standalone === true;
    setIsStandalone(isStandaloneMode);

    // Get current URL or local IP for mobile access
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    const currentOrigin = `${window.location.protocol}//${hostname}${port}`;
    setMobileUrl(currentOrigin);

    // Try fetching detected LAN IP from backend
    axios.get('http://127.0.0.1:8080/api/mobile/network-info')
      .then((res) => {
        if (res.data?.mobile_web_url) {
          setMobileUrl(res.data.mobile_web_url);
        }
      })
      .catch(() => {});

    const unsubscribe = onInstallPromptChange((prompt) => {
      setCanNativeInstall(!!prompt);
    });

    return () => unsubscribe();
  }, []);

  if (isStandalone) {
    return null;
  }

  // 1-Click Direct Desktop Install (No guide modal)
  const handleDirectPCInstall = async () => {
    const success = await triggerPWAInstall();
    if (!success) {
      // If browser has already handled or requires address-bar click in Chrome/Edge:
      alert('To install CodePrism on this PC:\nClick the Install icon (💻 or ⊕) in the right side of your browser address bar!');
    }
  };

  const handleOpenMobile = () => {
    setShowMobileModal(true);
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(mobileUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadPackage = () => {
    window.open('http://127.0.0.1:8080/api/mobile/download-package', '_blank');
  };

  return (
    <>
      {/* Direct PC Install Button */}
      {(mode === 'pc' || mode === 'all') && (
        <button
          onClick={handleDirectPCInstall}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-md shadow-blue-900/30 transition-all active:scale-95 cursor-pointer"
          title="Directly install CodePrism on this PC as a standalone app"
        >
          <Monitor className="w-3.5 h-3.5 text-blue-200" />
          <span>Install PC</span>
        </button>
      )}

      {/* Mobile Install Button */}
      {(mode === 'mobile' || mode === 'all') && (
        <button
          onClick={handleOpenMobile}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-900/30 transition-all active:scale-95 cursor-pointer ${
            isMobileDrawer ? 'w-full justify-center py-2.5 text-sm' : ''
          }`}
          title="Install / Download CodePrism on Mobile Phone (Android / iOS)"
        >
          <Smartphone className="w-3.5 h-3.5 text-emerald-200" />
          <span>Mobile App</span>
        </button>
      )}

      {/* Mobile QR & Package Modal */}
      {showMobileModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in select-none">
          <div className="w-full max-w-lg bg-[#0E1424] border border-emerald-500/40 rounded-2xl shadow-2xl overflow-hidden flex flex-col relative">
            {/* Close Button */}
            <button
              onClick={() => setShowMobileModal(false)}
              className="absolute top-4 right-4 p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors z-10"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Header */}
            <div className="px-6 py-4 bg-[#12182D] border-b border-gray-800 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 via-teal-600 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20 shrink-0">
                <Smartphone className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>Install CodePrism on Mobile</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold">
                    Android & iOS
                  </span>
                </h3>
                <p className="text-xs text-gray-400">Scan QR code or download mobile package for full-screen standalone IDE</p>
              </div>
            </div>

            {/* Content Body */}
            <div className="p-6 space-y-4 font-sans text-xs select-text">
              <div className="flex flex-col sm:flex-row items-center gap-5 p-4 bg-black/50 rounded-2xl border border-gray-800">
                {/* QR Code */}
                <div className="p-3 bg-white rounded-xl shadow-lg shrink-0 flex items-center justify-center">
                  <QRCodeSVG
                    value={mobileUrl}
                    size={120}
                    level="M"
                    includeMargin={false}
                  />
                </div>

                {/* Instructions */}
                <div className="space-y-2 text-center sm:text-left">
                  <div className="flex items-center justify-center sm:justify-start gap-1.5 text-emerald-400 font-bold text-sm">
                    <Wifi className="w-4 h-4" />
                    <span>Scan with Phone Camera</span>
                  </div>
                  <p className="text-gray-300 text-xs leading-relaxed">
                    Point your <strong>Android or iPhone camera</strong> at this QR code to open CodePrism on your phone.
                  </p>
                  <div className="text-[11px] text-gray-400">
                    Tap <strong>"Install app"</strong> or <strong>"Add to Home screen"</strong> on your phone to run full-screen!
                  </div>
                </div>
              </div>

              {/* Direct Mobile Link */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-bold text-gray-400 block uppercase tracking-wider">
                  Or Open this URL on your phone's browser:
                </span>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={mobileUrl}
                    className="flex-1 px-3 py-2 rounded-xl bg-gray-900 border border-gray-700 text-emerald-300 font-mono text-xs focus:outline-none"
                  />
                  <button
                    onClick={handleCopyLink}
                    className="px-3 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm transition-colors shrink-0"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copied ? 'Copied!' : 'Copy Link'}</span>
                  </button>
                </div>
              </div>

              {/* Mobile Package Download Button */}
              <button
                onClick={handleDownloadPackage}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs shadow-md flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Download Android Mobile Package (.zip)</span>
              </button>
            </div>

            {/* Footer */}
            <div className="px-6 py-3 bg-[#0A0F1D] border-t border-gray-800 flex items-center justify-between">
              <span className="text-[11px] text-gray-500 font-mono">CodePrism Universal Platform</span>
              <button
                onClick={() => setShowMobileModal(false)}
                className="px-4 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-white font-bold text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
