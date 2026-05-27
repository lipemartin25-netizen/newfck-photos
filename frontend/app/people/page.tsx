"use client";

import React from "react";
import { User, Users, Search, Edit3, Grid, Image as ImageIcon, Camera } from "lucide-react";

interface FaceCluster {
  id: string;
  name: string;
  count: number;
  coverUrl: string;
  averageAge: number;
}

export default function PeoplePage() {
  const [clusters, setClusters] = React.useState<FaceCluster[]>([
    { id: "1", name: "Felipe (Vovô)", count: 24, coverUrl: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150", averageAge: 62 },
    { id: "2", name: "Maria (Vovó)", count: 18, coverUrl: "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150", averageAge: 58 },
    { id: "3", name: "Person Cluster #12", count: 7, coverUrl: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150", averageAge: 28 }
  ]);
  const [search, setSearch] = React.useState("");

  const filtered = clusters.filter(c => c.name.toLowerCase().includes(search.toLowerCase()));

  const handleRename = (id: string, current: string) => {
    const val = prompt("Enter a name for this identity profile:", current);
    if (val === null) return;
    setClusters(prev => prev.map(c => c.id === id ? { ...c, name: val } : c));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-2">
            <Users className="w-8 h-8 text-indigo-500" />
            AI Face Profiles
          </h1>
          <p className="text-sm text-slate-500 font-semibold mt-1">Manage identified identities grouped by InsightFace & HDBSCAN</p>
        </div>

        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input 
            type="text" 
            placeholder="Search profiles..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs font-semibold text-slate-300 focus:outline-none focus:border-indigo-500 w-60"
          />
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="text-center py-20 bg-slate-900/40 rounded-3xl border border-slate-900/80">
          <User className="w-12 h-12 text-slate-700 mx-auto mb-4" />
          <h3 className="text-lg font-bold mb-1">No profiles detected</h3>
          <p className="text-sm text-slate-500 font-semibold">Make sure to scan photos containing clear faces to trigger InsightFace clustering.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {filtered.map((c) => (
            <div key={c.id} className="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all flex flex-col relative shadow-sm">
              <div className="aspect-square bg-slate-850 relative overflow-hidden flex items-center justify-center border-b border-slate-800/80">
                <img src={c.coverUrl} alt={c.name} className="object-cover w-32 h-32 rounded-full border-2 border-indigo-500/50 group-hover:scale-105 transition-transform" />
                <span className="absolute bottom-3 right-3 px-2 py-0.5 rounded-full bg-slate-950/80 text-indigo-400 text-[10px] font-black">
                  {c.count} photos
                </span>
              </div>
              
              <div className="p-4 flex flex-col gap-2">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-sm font-bold truncate text-slate-200">{c.name}</h3>
                  <button onClick={() => handleRename(c.id, c.name)} className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-white transition-all">
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-wider text-slate-500 mt-1">
                  <span>Est. Age</span>
                  <span>~{c.averageAge} y/o</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
