"use client";

import React from "react";
import { Sparkles, Calendar, Search, Map, ImageIcon, Compass, Star } from "lucide-react";

interface EventCluster {
  id: string;
  label: string;
  photosCount: number;
  dateRange: string;
  coverUrl: string;
  confidence: number;
}

export default function EventsPage() {
  const [events, setEvents] = React.useState<EventCluster[]>([
    { id: "1", label: "Wedding Ceremony", photosCount: 42, dateRange: "June 1982", coverUrl: "https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=300", confidence: 0.94 },
    { id: "2", label: "Beach Vacation", photosCount: 15, dateRange: "January 1978", coverUrl: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=300", confidence: 0.88 },
    { id: "3", label: "Christmas Celebration", photosCount: 29, dateRange: "December 1985", coverUrl: "https://images.unsplash.com/photo-1544816155-12df9643f363?w=300", confidence: 0.91 }
  ]);
  const [search, setSearch] = React.useState("");

  const filtered = events.filter(e => e.label.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <Compass className="w-8 h-8 text-indigo-500" />
            AI Events & Scene Parser
          </h1>
          <p className="text-sm text-slate-500 font-semibold mt-1">Automatic zero-shot event grouping powered by OpenCLIP embeddings</p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input 
            type="text" 
            placeholder="Search events, scenes..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold text-slate-300 focus:outline-none focus:border-indigo-500 w-60"
          />
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/40 rounded-3xl border border-slate-900/80">
          <Sparkles className="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <h3 className="text-lg font-bold mb-1">No events parsed</h3>
          <p className="text-sm text-slate-500 font-semibold">Verify if scans contain visual semantic elements matching CLIP triggers.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
          {filtered.map((e) => (
            <div key={e.id} className="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all flex flex-col relative shadow-sm">
              <div className="aspect-[16/9] bg-slate-855 relative overflow-hidden">
                <img src={e.coverUrl} alt={e.label} className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-300" />
                <span className="absolute top-3 left-3 px-2 py-0.5 rounded-full bg-slate-950/80 text-indigo-400 text-[10px] font-black uppercase tracking-wider flex items-center gap-1">
                  <Star className="w-3 h-3 text-indigo-400 fill-indigo-400" />
                  {(e.confidence * 100).toFixed(0)}% Match
                </span>
                
                <span className="absolute bottom-3 right-3 px-2.5 py-1 rounded-lg bg-slate-950/85 text-white text-[10px] font-bold">
                  {e.photosCount} photos
                </span>
              </div>
              
              <div className="p-5 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-200 mb-1">{e.label}</h3>
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 font-semibold mt-1">
                    <Calendar className="w-4 h-4 text-slate-655" />
                    <span>{e.dateRange}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
