"use client";

import React from "react";
import { Camera, Search, Filter, Calendar, Grid, Layers, Download, Trash, Heart } from "lucide-react";

interface CropPhoto {
  id: string;
  name: string;
  url: string;
  year?: number;
  tags: string[];
}

export default function GalleryPage() {
  const [photos, setPhotos] = React.useState<CropPhoto[]>([
    { id: "1", name: "Family picnic 1978_001.jpg", url: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300", year: 1978, tags: ["family", "outdoor"] },
    { id: "2", name: "Grandma birthday 1985_002.jpg", url: "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=300", year: 1985, tags: ["birthday", "interior"] },
    { id: "3", name: "Beach trip 1992_001.jpg", url: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300", year: 1992, tags: ["beach", "sea", "summer"] }
  ]);
  const [search, setSearch] = React.useState("");

  const filtered = photos.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase()) || 
    p.tags.some(t => t.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Your Photos Library</h1>
          <p className="text-sm text-slate-500 font-semibold mt-1">Manage and export all extracted photo outputs</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search by tag, year..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold text-slate-300 focus:outline-none focus:border-indigo-500 w-60"
            />
          </div>
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs rounded-xl flex items-center gap-1.5 transition-all">
            <Download className="w-4 h-4" />
            Export Library
          </button>
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/40 rounded-3xl border border-slate-900/80">
          <Camera className="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <h3 className="text-lg font-bold mb-1">No items found</h3>
          <p className="text-sm text-slate-500 font-semibold">Try modifying your filters or search query.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {filtered.map((photo) => (
            <div key={photo.id} className="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all flex flex-col relative shadow-sm">
              <div className="aspect-[4/3] bg-slate-800 relative overflow-hidden">
                <img src={photo.url} alt={photo.name} className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300" />
                {photo.year && (
                  <span className="absolute top-3 left-3 px-2 py-0.5 rounded-full bg-slate-950/80 text-indigo-400 text-[10px] font-black tracking-wide">
                    {photo.year}
                  </span>
                )}
                
                {/* Actions overlay */}
                <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <button className="p-2 bg-slate-900/90 rounded-lg hover:bg-indigo-600 text-white transition-all hover:scale-105 active:scale-95">
                    <Heart className="w-4 h-4" />
                  </button>
                  <button className="p-2 bg-slate-900/90 rounded-lg hover:bg-indigo-600 text-white transition-all hover:scale-105 active:scale-95">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="p-4 flex-1 flex flex-col justify-between">
                <p className="text-xs font-bold truncate text-slate-300 mb-2">{photo.name}</p>
                <div className="flex flex-wrap gap-1.5">
                  {photo.tags.map((t, idx) => (
                    <span key={idx} className="text-[9px] font-black uppercase tracking-wider text-slate-500 bg-slate-850 px-1.5 py-0.5 rounded">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
