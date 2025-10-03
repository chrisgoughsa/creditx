import type { z } from "zod";

import { PriceSuggestionSchema } from "../lib/api";
import { ReasonsList } from "./reasons-list";

export type PriceSuggestion = z.infer<typeof PriceSuggestionSchema>;

export function PricingCard({ suggestion }: { suggestion: PriceSuggestion }) {
  return (
    <article className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
      <header className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{suggestion.id}</h3>
          <p className="text-sm text-slate-500">Base rate {suggestion.base_rate_bps} bps</p>
        </div>
        <span className="inline-flex flex-col items-end">
          <span className="text-xs font-semibold uppercase text-slate-500">Suggested Rate</span>
          <span className="text-2xl font-bold text-brand-600">{suggestion.suggested_rate_bps} bps</span>
        </span>
      </header>
      <div className="rounded-2xl bg-brand-50 px-4 py-3 text-sm text-brand-900">
        <span className="font-semibold">Band {suggestion.band_code}</span>
        <span className="mx-2">•</span>
        <span>{suggestion.band_label}</span>
        <p className="mt-1 text-xs text-brand-700">{suggestion.band_description}</p>
      </div>
      <ReasonsList title="Adjustments" items={suggestion.adjustments} />
    </article>
  );
}
