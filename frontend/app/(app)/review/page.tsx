"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import api from "../../../lib/api";

export default function ReviewPage() {
  const [selectedCrop, setSelectedCrop] = useState<number | null>(null);
  const [crops, setCrops] = useState<any[]>([]);
  const search = useSearchParams();
  const image_id = search.get("image_id");

  // If detection results available, use them; otherwise fall back to mock
  const mockCrops = [];

  useEffect(() => {
    if (!image_id) return;
    (async () => {
      try {
        const res = await api.detectImage(image_id);
        // Map boxes to UI coordinates (percentage-based) — simplistic mapping
        const mapped = res.boxes.map((b: any, i: number) => ({
          id: i + 1,
          x: Math.max(0, (b.x1 / res.width) * 100),
          y: Math.max(0, (b.y1 / res.height) * 100),
          width: Math.min(100, ((b.x2 - b.x1) / res.width) * 100),
          height: Math.min(100, ((b.y2 - b.y1) / res.height) * 100),
          type: b.label || "Photo",
        }));
        setCrops(mapped);
      } catch (e) {
        console.error("Detect failed", e);
      }
    })();
  }, [image_id]);

  return (
    <div className="h-screen flex flex-col bg-slate-900 text-slate-100 overflow-hidden">
      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 border-b border-slate-800 bg-slate-950">
        <div className="flex items-center gap-4">
          <Link href="/upload" className="text-slate-400 hover:text-white transition-colors">
            ← Back
          </Link>
          <div className="h-4 w-px bg-slate-800"></div>
          <span className="font-semibold tracking-tight">scan_001.jpg</span>
          <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            3 Detected
          </span>
        </div>
        
        <div className="flex gap-3">
          <button className="px-4 py-2 text-sm font-medium bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors border border-slate-700">
            Add Manual Crop
          </button>
          <button className="px-6 py-2 text-sm font-medium bg-primary hover:bg-primary-hover rounded-lg transition-colors text-white shadow-lg shadow-primary/20">
            Extract & Enhance
          </button>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* Canvas Area */}
        <div className="flex-1 relative flex items-center justify-center bg-slate-900 overflow-hidden p-8">
          {/* Mock Canvas Container */}
          <div className="relative w-full max-w-3xl aspect-[3/4] bg-slate-800 rounded-lg border border-slate-700 shadow-2xl overflow-hidden flex items-center justify-center">
             <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
             
             {/* Mock Scan Image */}
             <div className="w-[80%] h-[90%] bg-slate-200 rounded relative shadow-inner">
                {/* Crops */}
                {(crops.length ? crops : mockCrops).map((crop) => (
                  <div
                    key={crop.id}
                    onClick={() => setSelectedCrop(crop.id)}
                    className={`absolute border-2 cursor-pointer transition-colors
                      ${selectedCrop === crop.id 
                        ? 'border-red-500 bg-red-500/10 z-10' 
                        : 'border-red-500/50 hover:border-red-500/80 bg-transparent'}
                    `}
                    style={{
                      left: `${crop.x}%`,
                      top: `${crop.y}%`,
                      width: `${crop.width}%`,
                      height: `${crop.height}%`
                    }}
                  >
                    {/* Handles */}
                    {selectedCrop === crop.id && (
                      <>
                        <div className="absolute -top-1.5 -left-1.5 w-3 h-3 bg-white border-2 border-red-500 rounded-full"></div>
                        <div className="absolute -top-1.5 -right-1.5 w-3 h-3 bg-white border-2 border-red-500 rounded-full"></div>
                        <div className="absolute -bottom-1.5 -left-1.5 w-3 h-3 bg-white border-2 border-red-500 rounded-full"></div>
                        <div className="absolute -bottom-1.5 -right-1.5 w-3 h-3 bg-white border-2 border-red-500 rounded-full"></div>
                        
                        <div className="absolute -top-6 left-0 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded shadow-sm">
                          {crop.type}
                        </div>
                      </>
                    )}
                  </div>
                ))}
             </div>
          </div>
          
          {/* Zoom controls */}
          <div className="absolute bottom-6 right-6 flex bg-slate-800 rounded-lg border border-slate-700 overflow-hidden shadow-lg">
            <button className="p-2 hover:bg-slate-700 transition-colors text-slate-400 hover:text-white">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" /></svg>
            </button>
            <div className="w-px bg-slate-700"></div>
            <button className="p-2 hover:bg-slate-700 transition-colors text-slate-400 hover:text-white">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" /></svg>
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-80 bg-slate-950 border-l border-slate-800 flex flex-col h-full overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h3 className="font-semibold text-slate-200">Review Output</h3>
            <p className="text-xs text-slate-500 mt-1">Select a crop to adjust parameters</p>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {mockCrops.map((crop) => (
              <div 
                key={crop.id}
                onClick={() => setSelectedCrop(crop.id)}
                className={`
                  p-3 rounded-xl border transition-all cursor-pointer flex gap-3
                  ${selectedCrop === crop.id 
                    ? 'border-primary bg-primary/5 shadow-md shadow-primary/5' 
                    : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'}
                `}
              >
                <div className="w-16 h-16 bg-slate-800 rounded flex-shrink-0 flex items-center justify-center overflow-hidden">
                   {/* Thumbnail placeholder */}
                   <div className="text-xs text-slate-600 font-medium">Crop {crop.id}</div>
                </div>
                <div className="flex-1 flex flex-col justify-center">
                  <div className="text-sm font-medium text-slate-300">Extracted {crop.type}</div>
                  <div className="text-xs text-slate-500 mt-1">Ready for Revitalize</div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="p-4 bg-slate-900 border-t border-slate-800">
             <div className="flex items-center justify-between mb-4">
               <span className="text-sm font-medium text-slate-300">Auto-Rotate</span>
               <div className="w-10 h-5 bg-primary rounded-full relative cursor-pointer">
                 <div className="absolute right-1 top-0.5 w-4 h-4 bg-white rounded-full"></div>
               </div>
             </div>
             <div className="flex items-center justify-between">
               <span className="text-sm font-medium text-slate-300">Color Revitalize</span>
               <div className="w-10 h-5 bg-primary rounded-full relative cursor-pointer">
                 <div className="absolute right-1 top-0.5 w-4 h-4 bg-white rounded-full"></div>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
