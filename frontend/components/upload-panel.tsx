"use client";

import { useState } from "react";

interface UploadPanelProps {
  label: string;
  description: string;
  endpoint: string;
  onComplete(data: unknown): void;
  accept?: string;
}

export function UploadPanel({ label, description, endpoint, onComplete, accept = ".csv" }: UploadPanelProps) {
  const [isUploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }

    const apiBase =
      process.env.NEXT_PUBLIC_CREDITX_API ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    const url = `${apiBase}${endpoint}`;

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setError(null);

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Upload failed with status ${response.status}`);
      }

      const payload = await response.json();
      onComplete(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="rounded-3xl border border-dashed border-brand-400 bg-brand-50/60 p-6">
      <div className="flex flex-col gap-3 text-sm text-slate-600">
        <div>
          <strong className="block text-base text-brand-700">{label}</strong>
          <span>{description}</span>
        </div>
        <label className="inline-flex w-full cursor-pointer items-center justify-center rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white shadow transition hover:bg-brand-600">
          <input
            type="file"
            accept={accept}
            className="hidden"
            onChange={handleFileChange}
            disabled={isUploading}
          />
          {isUploading ? "Uploading…" : "Upload CSV"}
        </label>
        {error ? <span className="text-sm text-red-500">{error}</span> : null}
      </div>
    </div>
  );
}
