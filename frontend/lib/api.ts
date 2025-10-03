import { z } from "zod";

const API_BASE =
  process.env.NEXT_PUBLIC_CREDITX_API ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const TriageScoreSchema = z.object({
  id: z.string(),
  score: z.number().min(0).max(1),
  reasons: z.array(z.string()),
});

export const PriceSuggestionSchema = z.object({
  id: z.string(),
  band_code: z.enum(["A", "B", "C", "D", "E"]),
  band_label: z.string(),
  band_description: z.string(),
  suggested_rate_bps: z.number(),
  base_rate_bps: z.number(),
  adjustments: z.array(z.string()),
});

const FeatureImportanceSchema = z.record(z.number());

export const TriageResultsSchema = z.object({
  scores: z.array(TriageScoreSchema),
  feature_importance: FeatureImportanceSchema,
  weights_version: z.string(),
});

export const RenewalResultsSchema = z.object({
  scores: z.array(TriageScoreSchema),
  feature_importance: FeatureImportanceSchema,
  weights_version: z.string(),
});

export const PricingResultsSchema = z.object({
  suggestions: z.array(PriceSuggestionSchema),
  feature_importance: FeatureImportanceSchema,
  weights_version: z.string(),
});

const SubmissionSchema = z.object({
  submission_id: z.string(),
  broker: z.string(),
  sector: z.enum(["Retail", "Manufacturing", "Logistics", "Agri", "Services", "Other"]),
  exposure_limit: z.number().nonnegative(),
  debtor_days: z.number().nonnegative(),
  financials_attached: z.boolean(),
  years_trading: z.number().nonnegative(),
  broker_hit_rate: z.number().min(0).max(1),
  requested_cov_pct: z.number().min(0).max(1),
  has_judgements: z.boolean(),
});

const PolicySchema = z.object({
  policy_id: z.string(),
  sector: z.enum(["Retail", "Manufacturing", "Logistics", "Agri", "Services", "Other"]),
  current_premium: z.number().nonnegative(),
  limit: z.number().nonnegative(),
  utilization_pct: z.number().min(0).max(1),
  claims_last_24m_cnt: z.number().nonnegative(),
  claims_ratio_24m: z.number().nonnegative(),
  days_to_expiry: z.number().nonnegative(),
  requested_change_pct: z.number(),
  broker: z.string(),
});

export type SubmissionInput = z.infer<typeof SubmissionSchema>;
export type PolicyInput = z.infer<typeof PolicySchema>;

export type TriageResults = z.infer<typeof TriageResultsSchema>;
export type RenewalResults = z.infer<typeof RenewalResultsSchema>;
export type PricingResults = z.infer<typeof PricingResultsSchema>;

export async function fetchTriageScores(submissions: SubmissionInput[]): Promise<TriageResults> {
  const payload = { submissions };
  const data = await request("/triage/underwriting", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  const parsed = TriageResultsSchema.safeParse(data);
  if (parsed.success) {
    return parsed.data;
  }

  const legacy = z.array(TriageScoreSchema).safeParse(data);
  if (legacy.success) {
    return {
      scores: legacy.data,
      feature_importance: {},
      weights_version: "legacy",
    };
  }

  throw parsed.error;
}

export async function fetchRenewalPriorities(policies: PolicyInput[]): Promise<RenewalResults> {
  const payload = { policies };
  const data = await request("/renewals/priority", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  const parsed = RenewalResultsSchema.safeParse(data);
  if (parsed.success) {
    return parsed.data;
  }

  const legacy = z.array(TriageScoreSchema).safeParse(data);
  if (legacy.success) {
    return {
      scores: legacy.data,
      feature_importance: {},
      weights_version: "legacy",
    };
  }

  throw parsed.error;
}

export async function fetchPricingSuggestions(submissions: SubmissionInput[]): Promise<PricingResults> {
  const payload = { submissions };
  const data = await request("/pricing/suggest", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  const parsed = PricingResultsSchema.safeParse(data);
  if (parsed.success) {
    return parsed.data;
  }

  const legacy = z.array(PriceSuggestionSchema).safeParse(data);
  if (legacy.success) {
    return {
      suggestions: legacy.data,
      feature_importance: {},
      weights_version: "legacy",
    };
  }

  throw parsed.error;
}
