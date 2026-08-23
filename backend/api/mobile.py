import os
import io
import zipfile
import socket
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/mobile", tags=["Mobile & APK Distribution"])

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@router.get("/network-info")
async def get_network_info():
    """Returns local network IP and PWA mobile access URLs."""
    local_ip = get_local_ip()
    return {
        "local_ip": local_ip,
        "frontend_port": 5173,
        "backend_port": 8080,
        "mobile_web_url": f"http://{local_ip}:5173",
        "backend_url": f"http://{local_ip}:8080"
    }

@router.get("/download-package")
async def download_mobile_package():
    """Generates and serves a packaged CodePrism Android distribution bundle."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Include Android App Manifest
        android_manifest = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.codeprism.compiler"
    android:versionCode="1"
    android:versionName="1.0.0">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="CodePrism"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|keyboardHidden|screenSize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
        zf.writestr("AndroidManifest.xml", android_manifest)
        
        # Include README Instructions for Android Sideload / TWA
        instructions = """# CodePrism Mobile Package (Android & iOS)

## 📲 Option 1: Instant 1-Tap PWA Install (Recommended)
1. Open Chrome/Safari on your phone.
2. Navigate to your CodePrism Live URL.
3. Tap "Add to Home screen" or "Install App".
4. CodePrism runs as a full-screen, offline-capable standalone IDE!

## 🤖 Option 2: Build Native APK with Bubblewrap / TWA
1. Install Bubblewrap CLI:
   npm install -g @bubblewrap/cli
2. Initialize from CodePrism Manifest:
   bubblewrap init --manifest=http://<YOUR_IP>:5173/manifest.json
3. Build Signed APK:
   bubblewrap build
"""
        zf.writestr("INSTALL_GUIDE.md", instructions)
        
        # Include PWA manifest copy
        manifest_path = os.path.join("frontend", "public", "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                zf.writestr("manifest.json", f.read())

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=CodePrism-Mobile-v1.0.0.zip"
        }
    )
