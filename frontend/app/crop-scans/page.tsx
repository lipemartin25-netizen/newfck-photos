"use client";

import React from "react";
import { useDropzone } from "react-dropzone";
import { 
  Camera, Check, Shield, Zap, RefreshCw, Sparkles, User, 
  ChevronRight, Trash, Download, RotateCw, RefreshCw as LoopIcon,
  Sliders, Grid, Layers, Eye, Image as ImageIcon, Plus, SlidersHorizontal
} from "lucide-react";

interface DetectedBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  score: number;
  label: string;
}

interface ScanFile {
  id: string;
  name: string;
  url: string;
  width: number;
  height: number;
  boxes: DetectedBox[];
  status: "pending" | "processing" | "reviewed" | "error";
}

export default function EditorPage() {
  const [scans, setScans] = React.useState<ScanFile[]>([]);
  const [activeScanId, setActiveScanId] = React.useState<string | null>(null);
  
  // Custom sliders
  const [brightness, setBrightness] = React.useState(0);
  const [contrast, setContrast] = React.useState(0);
  const [saturation, setSaturation] = React.useState(0);
  const [yellowCast, setYellowCast] = React.useState(0);
  
  // AI thresholds
  const [confidence, setConfidence] = React.useState(0.15);
  const [overlap, setOverlap] = React.useState(0.05);

  const activeScan = scans.find(s => s.id === activeScanId) || null;

  const onDrop = React.useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach((file) => {
      const id = Math.random().toString(36).substring(7);
      const url = URL.createObjectURL(file);
      
      const newScan: ScanFile = {
        id,
        name: file.name,
        url,
        width: 1200,
        height: 800,
        boxes: [
          { x1: 50, y1: 50, x2: 450, y2: 350, score: 0.89, label: "photo" },
          { x1: 500, y1: 80, x2: 900, y2: 420, score: 0.94, label: "photo" },
          { x1: 200, y1: 450, x2: 700, y2: 750, score: 0.78, label: "photo" }
        ],
        status: "processing"
      };

      setScans(prev => [...prev, newScan]);
      if (!activeScanId) setActiveScanId(id);

      // Simulate AI loading D Dino
      setTimeout(() => {
        setScans(prev => prev.map(s => s.id === id ? { ...s, status: "reviewed" } : s));
      }, 1000);
    });
  }, [activeScanId]);

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  const handleBBoxResize = (index: number, xDelta: number, yDelta: number) => {
    if (!activeScan) return;
    const ratioX = activeScan.width / 900;
    const ratioY = activeScan.height / 600;

    setScans(prev => prev.map(s => {
      if (s.id !== activeScan.id) return s;
      const b = [...s.boxes];
      b[index] = {
        ...b[index],
        x2: Math.min(s.width, Math.max(b[index].x1 + 50, b[index].x2 + (xDelta * ratioX))),
        y2: Math.min(s.height, Math.max(b[index].y1 + 50, b[index].y2 + (yDelta * ratioY))),
      };
      return { ...s, boxes: b };
    }));
  };

  const handleBBoxMove = (index: number, xDelta: number, yDelta: number) => {
    if (!activeScan) return;
    const ratioX = activeScan.width / 900;
    const ratioY = activeScan.height / 600;
    const dx = xDelta * ratioX;
    const dy = yDelta * ratioY;

    setScans(prev => prev.map(s => {
      if (s.id !== activeScan.id) return s;
      const b = [...s.boxes];
      const box = b[index];
      const width = box.x2 - box.x1;
      const height = box.y2 - box.y1;
      
      let newX1 = box.x1 + dx;
      let newY1 = box.y1 + dy;
      let newX2 = newX1 + width;
      let newY2 = newY1 + height;
      
      if (newX1 < 0) { newX1 = 0; newX2 = width; }
      if (newY1 < 0) { newY1 = 0; newY2 = height; }
      if (newX2 > s.width) { newX2 = s.width; newX1 = s.width - width; }
      if (newY2 > s.height) { newY2 = s.height; newY1 = s.height - height; }

      b[index] = { ...box, x1: newX1, y1: newY1, x2: newX2, y2: newY2 };
      return { ...s, boxes: b };
    }));
  };

  const handleAddBox = () => {
    if (!activeScan) return;
    setScans(prev => prev.map(s => {
      if (s.id !== activeScan.id) return s;
      const newBox: DetectedBox = {
        x1: 100, y1: 100, x2: 400, y2: 400, score: 1.0, label: "manual"
      };
      return { ...s, boxes: [...s.boxes, newBox] };
    }));
  };

  const handleRemoveBox = (index: number) => {
    if (!activeScan) return;
    setScans(prev => prev.map(s => {
      if (s.id !== activeScan.id) return s;
      const b = s.boxes.filter((_, i) => i !== index);
      return { ...s, boxes: b };
    }));
  };

  const applyPreset = (preset: string) => {
    if (preset === "sharper") {
      setBrightness(-5);
      setContrast(15);
      setSaturation(0);
      setYellowCast(10);
    } else if (preset === "vivid") {
      setBrightness(5);
      setContrast(20);
      setSaturation(25);
      setYellowCast(0);
    } else if (preset === "vintage") {
      setBrightness(-10);
      setContrast(-5);
      setSaturation(-35);
      setYellowCast(30);
    } else {
      setBrightness(0);
      setContrast(0);
      setSaturation(0);
      setYellowCast(0);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-slate-900 text-slate-100 font-sans select-none">
      {/* Editor Header */}
      <header className="h-16 px-6 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center">
            <Camera className="w-4.5 h-4.5 text-white" />
          </div>
          <span className="font-bold text-sm tracking-tight">Newfkc Photos</span>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-black">v2.0 PRO</span>
        </div>

        <div className="flex items-center gap-3">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl shadow-md flex items-center gap-1.5 transition-all">
            <Download className="w-4 h-4" />
            Save All crops
          </button>
          <a href="/" className="px-4 py-2 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white font-bold text-xs rounded-xl transition-all">
            Exit
          </a>
        </div>
      </header>

      {/* Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar: Thumbs list (AutoSplitter style) */}
        <aside className="w-64 border-r border-slate-800 bg-slate-950/50 flex flex-col justify-between">
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            <h3 className="text-xs font-black tracking-wider text-slate-500 uppercase mb-4">Batch Queue ({scans.length})</h3>
            
            {scans.length === 0 ? (
              <div {...getRootProps()} className="border-2 border-dashed border-slate-800 rounded-2xl p-6 text-center hover:border-indigo-500 transition-all cursor-pointer">
                <input {...getInputProps()} />
                <Plus className="w-8 h-8 text-slate-650 mx-auto mb-2" />
                <p className="text-xs text-slate-500 font-semibold leading-relaxed">Add scans to queue</p>
              </div>
            ) : (
              scans.map((scan) => (
                <div 
                  key={scan.id}
                  onClick={() => setActiveScanId(scan.id)}
                  className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center gap-3 relative ${
                    scan.id === activeScanId 
                      ? "border-indigo-500/80 bg-indigo-950/20 shadow-md" 
                      : "border-slate-800/60 bg-slate-900/40 hover:bg-slate-900/80"
                  }`}
                >
                  <div className="w-12 h-12 rounded-lg bg-slate-800 overflow-hidden flex items-center justify-center relative border border-slate-700">
                    <img src={scan.url} alt="scan" className="object-cover w-full h-full" />
                    {scan.status === "processing" && (
                      <div className="absolute inset-0 bg-slate-950/60 flex items-center justify-center">
                        <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold truncate text-slate-300">{scan.name}</p>
                    <span className={`text-[10px] font-bold ${
                      scan.status === "reviewed" ? "text-emerald-400" : "text-amber-400 animate-pulse"
                    }`}>
                      {scan.status === "reviewed" ? `${scan.boxes.length} photos` : "Extracting..."}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
          
          {scans.length > 0 && (
            <div {...getRootProps()} className="p-4 border-t border-slate-800 bg-slate-950">
              <input {...getInputProps()} />
              <button className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-slate-300 font-bold text-xs rounded-xl flex items-center justify-center gap-2 border border-slate-800/80">
                <Plus className="w-4 h-4" />
                Add More Scans
              </button>
            </div>
          )}
        </aside>

        {/* Central Canvas Workspace */}
        <main className="flex-1 bg-slate-900 flex flex-col overflow-hidden relative">
          {activeScan ? (
            <div className="flex-1 relative flex items-center justify-center p-8 overflow-auto">
              {/* Canvas viewport container */}
              <div className="relative border border-slate-800 shadow-2xl rounded-2xl overflow-hidden bg-slate-950" style={{ width: "900px", height: "600px" }}>
                <img src={activeScan.url} alt="scan active" className="w-full h-full object-contain pointer-events-none" />

                {/* Overlaid bounding boxes with red frames (AutoSplitter style) */}
                {activeScan.boxes.map((box, index) => (
                  <div 
                    key={index}
                    className="absolute border border-red-600 shadow-[0_0_8px_rgba(220,38,38,0.3)] bg-red-500/10 transition-all cursor-move"
                    style={{
                      left: `${(box.x1 / activeScan.width) * 100}%`,
                      top: `${(box.y1 / activeScan.height) * 100}%`,
                      width: `${((box.x2 - box.x1) / activeScan.width) * 100}%`,
                      height: `${((box.y2 - box.y1) / activeScan.height) * 100}%`
                    }}
                    onMouseDown={(e) => {
                      if ((e.target as HTMLElement).tagName === 'BUTTON' || (e.target as HTMLElement).tagName === 'path' || (e.target as HTMLElement).tagName === 'svg') return;
                      const moveHandler = (me: MouseEvent) => handleBBoxMove(index, me.movementX, me.movementY);
                      const upHandler = () => {
                        window.removeEventListener("mousemove", moveHandler);
                        window.removeEventListener("mouseup", upHandler);
                      };
                      window.addEventListener("mousemove", moveHandler);
                      window.addEventListener("mouseup", upHandler);
                    }}
                  >
                    {/* Corner anchors for resizing */}
                    <div 
                      onMouseDown={(e) => {
                        e.stopPropagation();
                        const moveHandler = (me: MouseEvent) => handleBBoxResize(index, me.movementX, me.movementY);
                        const upHandler = () => {
                          window.removeEventListener("mousemove", moveHandler);
                          window.removeEventListener("mouseup", upHandler);
                        };
                        window.addEventListener("mousemove", moveHandler);
                        window.addEventListener("mouseup", upHandler);
                      }}
                      className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-red-600 border border-white cursor-se-resize shadow-md"
                    />

                    {/* Confidence tag */}
                    <div className="absolute top-1.5 left-1.5 px-1.5 py-0.5 rounded bg-red-600 text-white text-[9px] font-black uppercase tracking-wider">
                      {box.score === 1.0 ? "manual" : `IA: ${(box.score * 100).toFixed(0)}%`}
                    </div>

                    {/* Remove crop handle */}
                    <button 
                      onClick={() => handleRemoveBox(index)}
                      className="absolute top-1.5 right-1.5 w-4.5 h-4.5 rounded bg-red-700/80 hover:bg-red-800 text-white flex items-center justify-center hover:scale-105 active:scale-95"
                    >
                      <Trash className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Floating Toolbar */}
              <div className="absolute bottom-6 left-1/2 -translate-x-1/2 px-5 py-3 rounded-full bg-slate-950/90 border border-slate-800/80 shadow-xl flex items-center gap-5 backdrop-blur-md">
                <button onClick={handleAddBox} className="p-2 hover:bg-slate-800 rounded-xl text-slate-355 hover:text-white flex items-center gap-1.5 text-xs font-bold transition-all">
                  <Plus className="w-4 h-4 text-indigo-400" />
                  Add Manual Box
                </button>
                <div className="w-px h-5 bg-slate-800" />
                <button onClick={() => setScans([])} className="p-2 hover:bg-red-950/30 rounded-xl text-slate-400 hover:text-red-400 flex items-center gap-1.5 text-xs font-bold transition-all">
                  <Trash className="w-4 h-4" />
                  Reset Sheet
                </button>
              </div>
            </div>
          ) : (
            <div {...getRootProps()} className="flex-1 flex flex-col items-center justify-center cursor-pointer p-8">
              <input {...getInputProps()} />
              <Camera className="w-16 h-16 text-slate-700 animate-pulse mb-4" />
              <h3 className="text-xl font-bold mb-2">No scanned sheet active</h3>
              <p className="text-sm text-slate-500 font-semibold max-w-sm text-center">
                Upload scans from your scanner or album pages to begin the automated splitting process.
              </p>
            </div>
          )}
        </main>

        {/* Right Sidebar: Retouching & AI tuning (AutoSplitter style) */}
        <aside className="w-72 border-l border-slate-800 bg-slate-950/40 p-5 overflow-y-auto space-y-6">
          <div>
            <h3 className="text-xs font-black tracking-wider text-slate-500 uppercase mb-4 flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5" />
              Tuning presets
            </h3>
            <div className="grid grid-cols-2 gap-2">
              <button onClick={() => applyPreset("sharper")} className="py-2 bg-slate-900 hover:bg-slate-850 border border-slate-800/80 rounded-xl text-xs font-semibold hover:text-white transition-all text-center">
                Sharper Scan
              </button>
              <button onClick={() => applyPreset("vivid")} className="py-2 bg-slate-900 hover:bg-slate-850 border border-slate-800/80 rounded-xl text-xs font-semibold hover:text-white transition-all text-center">
                Vivid Scan
              </button>
              <button onClick={() => applyPreset("vintage")} className="py-2 bg-slate-900 hover:bg-slate-850 border border-slate-800/80 rounded-xl text-xs font-semibold hover:text-white transition-all text-center">
                Vintage Scan
              </button>
              <button onClick={() => applyPreset("reset")} className="py-2 bg-slate-900 hover:bg-slate-850 border border-slate-800/80 rounded-xl text-xs font-semibold hover:text-white transition-all text-center">
                Reset sliders
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xs font-black tracking-wider text-slate-500 uppercase flex items-center gap-2">
              <SlidersHorizontal className="w-3.5 h-3.5" />
              Custom Color Retouch
            </h3>

            {/* Brightness */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1 text-slate-400">
                <span>Brightness</span>
                <span>{brightness}%</span>
              </div>
              <input type="range" min="-50" max="50" value={brightness} onChange={e => setBrightness(Number(e.target.value))} className="w-full accent-indigo-500" />
            </div>

            {/* Contrast */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1 text-slate-400">
                <span>Contrast</span>
                <span>{contrast}%</span>
              </div>
              <input type="range" min="-50" max="50" value={contrast} onChange={e => setContrast(Number(e.target.value))} className="w-full accent-indigo-500" />
            </div>

            {/* Saturation */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1 text-slate-400">
                <span>Saturation</span>
                <span>{saturation}%</span>
              </div>
              <input type="range" min="-50" max="50" value={saturation} onChange={e => setSaturation(Number(e.target.value))} className="w-full accent-indigo-500" />
            </div>

            {/* Yellow Cast (Acid paper corrector) */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1 text-slate-400">
                <span>Yellow Cast Corrector</span>
                <span>{yellowCast}%</span>
              </div>
              <input type="range" min="0" max="100" value={yellowCast} onChange={e => setYellowCast(Number(e.target.value))} className="w-full accent-indigo-500" />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 space-y-4">
            <h3 className="text-xs font-black tracking-wider text-slate-500 uppercase flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5" />
              AI Object thresholds
            </h3>
            
            {/* Confidence Slider */}
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1 text-slate-400">
                <span>Confidence</span>
                <span>{(confidence * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0.05" max="0.95" step="0.05" value={confidence} onChange={e => setConfidence(Number(e.target.value))} className="w-full accent-indigo-500" />
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
