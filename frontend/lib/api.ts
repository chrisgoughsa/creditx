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

export async function fetchTriageScores(submissions: SubmissionInput[]) {
  const payload = { submissions };
  const parsed = z.array(TriageScoreSchema).parse(
    await request("/triage/underwriting", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  );
  return parsed;
}

export async function fetchRenewalPriorities(policies: PolicyInput[]) {
  const payload = { policies };
  const parsed = z.array(TriageScoreSchema).parse(
    await request("/renewals/priority", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  );
  return parsed;
}

export async function fetchPricingSuggestions(submissions: SubmissionInput[]) {
  const payload = { submissions };
  const parsed = z.array(PriceSuggestionSchema).parse(
    await request("/pricing/suggest", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  );
  return parsed;
}
