const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type UploadResult = {
  id: string;
  filename: string;
  width: number;
  height: number;
  size_bytes: number;
};

export type BBox = { x1: number; y1: number; x2: number; y2: number; score?: number; label?: string };

export async function uploadFiles(files: File[]): Promise<UploadResult[]> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));

  const res = await fetch(`${API_URL}/api/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: await res.text() }));
    throw new Error(err?.message || `Upload failed: ${res.status}`);
  }

  return res.json();
}

export async function detectImage(image_id: string) {
  const payload = {
    image_id,
  };
  const res = await fetch(`${API_URL}/api/detect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Detect failed: ${res.status}`);
  return res.json();
}

export default { uploadFiles, detectImage };