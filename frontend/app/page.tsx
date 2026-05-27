import Link from "next/link";
import Image from "next/image";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="px-6 py-4 flex items-center justify-between border-b border-border/40 glass-panel sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-xl">
            A
          </div>
          <span className="text-xl font-semibold tracking-tight text-foreground">AlbumAI Studio</span>
        </div>
        <nav className="hidden md:flex gap-6 text-sm font-medium text-slate-600">
          <Link href="#features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-primary transition-colors">How it Works</Link>
          <Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link>
        </nav>
        <div className="flex gap-4">
          <Link href="/login" className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-foreground">Log in</Link>
          <Link href="/upload" className="px-4 py-2 text-sm font-medium bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors shadow-sm">
            Get Started
          </Link>
        </div>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="py-24 px-6 text-center max-w-5xl mx-auto flex flex-col items-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-8">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse-slow"></span>
            AlbumAI Studio v2.0 is Live
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-6 leading-[1.1]">
            Scan. Upload. <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Auto-Crop.</span>
          </h1>
          
          <p className="text-xl text-slate-600 mb-10 max-w-2xl">
            Stop manually cropping your scanned photos. Our Grounding DINO AI instantly detects, splits, rotates, and restores your family archives with a single click.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 mb-16">
            <Link href="/upload" className="px-8 py-4 text-lg font-semibold bg-primary text-white rounded-xl hover:bg-primary-hover transition-all hover:-translate-y-1 shadow-lg shadow-primary/25">
              Start Free Trial
            </Link>
            <Link href="#demo" className="px-8 py-4 text-lg font-semibold bg-white text-slate-700 border border-border rounded-xl hover:bg-slate-50 transition-all hover:-translate-y-1 shadow-sm">
              Watch Demo
            </Link>
          </div>

          {/* Abstract Hero Illustration */}
          <div className="w-full h-80 md:h-[500px] bg-slate-100 rounded-2xl border border-border relative overflow-hidden flex items-center justify-center glass-panel">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-purple-50 opacity-50"></div>
            <div className="relative flex items-center gap-8">
              <div className="w-48 h-64 bg-white shadow-xl rounded-lg p-2 rotate-[-5deg] animate-float transform transition-transform border border-border/50">
                <div className="w-full h-full bg-slate-200 rounded animate-pulse-slow"></div>
              </div>
              <div className="w-56 h-72 bg-white shadow-2xl rounded-lg p-2 z-10 border border-primary/20">
                <div className="w-full h-full bg-gradient-to-tr from-primary/80 to-accent/80 rounded relative">
                   <div className="absolute inset-0 border-2 border-review-frame m-4 dashed"></div>
                </div>
              </div>
              <div className="w-48 h-64 bg-white shadow-xl rounded-lg p-2 rotate-[5deg] animate-float border border-border/50" style={{ animationDelay: '1s' }}>
                <div className="w-full h-full bg-slate-200 rounded animate-pulse-slow"></div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="py-24 bg-slate-50 border-t border-border/50 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-slate-900 mb-4">Everything you need to digitize faster</h2>
              <p className="text-lg text-slate-600">Powerful AI tools designed for archivists and families.</p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {/* Feature 1 */}
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-border/50 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6 text-primary text-2xl">✂️</div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Auto-Cropping</h3>
                <p className="text-slate-600">Scan 4 photos on a single flatbed. We instantly detect and split them into individual files.</p>
              </div>
              
              {/* Feature 2 */}
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-border/50 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-accent/10 rounded-xl flex items-center justify-center mb-6 text-accent text-2xl">🎨</div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Color Revitalization</h3>
                <p className="text-slate-600">Remove yellowing and orange casts from old 70s photos automatically with AI.</p>
              </div>
              
              {/* Feature 3 */}
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-border/50 hover:shadow-md transition-shadow">
                <div className="w-12 h-12 bg-success/10 rounded-xl flex items-center justify-center mb-6 text-success text-2xl">👤</div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">Face Grouping</h3>
                <p className="text-slate-600">Organize thousands of photos automatically by recognizing who is in them.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-12 border-t border-border/50 bg-white px-6 text-center text-slate-500">
        <p>© 2026 AlbumAI Studio. All rights reserved.</p>
      </footer>
    </div>
  );
}
