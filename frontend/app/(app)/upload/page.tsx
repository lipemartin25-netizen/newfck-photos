"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "../../../lib/api";

export default function UploadPage() {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const router = useRouter();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const items = Array.from(e.dataTransfer.files || []);
    if (items.length) handleUpload(items as File[]);
  };

  const handleUpload = useCallback(async (files: File[]) => {
    setIsUploading(true);
    try {
      const results = await api.uploadFiles(files);
      // Navigate to review for the first uploaded image
      if (results && results.length > 0) {
        const id = results[0].id;
        router.push(`/review?image_id=${id}`);
      }
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + (err as Error).message);
    } finally {
      setIsUploading(false);
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-3xl glass-panel p-10 rounded-2xl">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Upload Scans</h1>
            <p className="text-slate-600">Drag and drop your flatbed scans here.</p>
          </div>
          <Link href="/" className="text-sm font-medium text-slate-500 hover:text-slate-800 transition-colors">
            Cancel
          </Link>
        </div>

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-xl p-16 text-center transition-all duration-300
            ${isDragging 
              ? 'border-primary bg-primary/5 scale-[1.01] shadow-lg shadow-primary/10' 
              : 'border-slate-300 bg-white hover:border-primary/50'}
          `}
        >
          {isUploading ? (
            <div className="flex flex-col items-center justify-center">
              <div className="w-12 h-12 border-4 border-slate-200 border-t-primary rounded-full animate-spin mb-4"></div>
              <p className="text-lg font-medium text-slate-700 animate-pulse">Running Grounding DINO detection...</p>
            </div>
          ) : (
            <>
              <div className="w-20 h-20 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-slate-800 mb-2">Drag & Drop scans here</h3>
              <p className="text-slate-500 mb-6">Supports JPEG, PNG, TIFF up to 50MB</p>
              
              <label className="inline-block">
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    const files = e.target.files ? Array.from(e.target.files) : [];
                    if (files.length) handleUpload(files);
                  }}
                />
                <span className="px-6 py-3 bg-white text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50 font-medium transition-colors cursor-pointer">
                  Browse Files
                </span>
              </label>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
