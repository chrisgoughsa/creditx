"use client";

import { useMutation } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { z } from "zod";

import { DataGrid } from "../../../components/data-grid";
import { PolicyForm } from "../../../components/policy-form";
import { UploadPanel } from "../../../components/upload-panel";
import { ReasonsList } from "../../../components/reasons-list";
import type { PolicyInput } from "../../../lib/api";
import { fetchRenewalPriorities, TriageScoreSchema } from "../../../lib/api";

type RenewalResult = z.infer<typeof TriageScoreSchema>;

const defaultPolicy: PolicyInput = {
  policy_id: "POL-001",
  broker: "XYZ Brokers",
  sector: "Retail",
  current_premium: 50_000,
  limit: 2_000_000,
  utilization_pct: 0.65,
  claims_last_24m_cnt: 2,
  claims_ratio_24m: 0.15,
  days_to_expiry: 30,
  requested_change_pct: -0.1,
};

export default function RenewalsPage() {
  const [policies, setPolicies] = useState<PolicyInput[]>([defaultPolicy]);
  const [results, setResults] = useState<RenewalResult[] | null>(null);

  const mutation = useMutation({
    mutationFn: fetchRenewalPriorities,
    onSuccess: (data) => setResults(data),
  });

  function handleAdd(policy: PolicyInput) {
    setPolicies((prev) => {
      const index = prev.findIndex((item) => item.policy_id === policy.policy_id);
      if (index >= 0) {
        const updated = [...prev];
        updated[index] = policy;
        return updated;
      }
      return [...prev, policy];
    });
  }

  function handleRemove(policyId: string) {
    setPolicies((prev) => prev.filter((policy) => policy.policy_id !== policyId));
  }

  const columns = useMemo(() => {
    return [
      { key: "policy_id", label: "Policy" },
      { key: "broker", label: "Broker" },
      { key: "sector", label: "Sector" },
      {
        key: "utilization_pct",
        label: "Utilization",
        render: (policy: PolicyInput) => `${Math.round(policy.utilization_pct * 100)}%`,
      },
      {
        key: "days_to_expiry",
        label: "Days to expiry",
      },
      {
        key: "requested_change_pct",
        label: "Change",
        render: (policy: PolicyInput) => `${Math.round(policy.requested_change_pct * 100)}%`,
      },
      {
        key: "actions",
        label: "",
        render: (policy: PolicyInput) => (
          <button
            type="button"
            onClick={() => handleRemove(policy.policy_id)}
            className="text-xs font-semibold text-red-500 hover:underline"
          >
            Remove
          </button>
        ),
      },
    ];
  }, []);

  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold text-slate-900">Renewal priority</h1>
        <p className="max-w-3xl text-sm text-slate-600">
          Prioritize renewals by expiry, utilization, claims activity, and client requests. Upload a CSV or manage
          policies individually.
        </p>
      </header>

      <PolicyForm onAdd={handleAdd} />

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <DataGrid columns={columns as never} data={policies} emptyMessage="Add a policy to run scoring." />
        <div className="space-y-4">
          <button
            type="button"
            onClick={() => mutation.mutate(policies)}
            disabled={policies.length === 0 || mutation.isPending}
            className="inline-flex w-full items-center justify-center rounded-full bg-brand-500 px-6 py-3 text-sm font-semibold text-white transition hover:bg-brand-600 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {mutation.isPending ? "Running priority…" : "Run renewal priority"}
          </button>
          <UploadPanel
            label="CSV upload"
            description="Upload renewal portfolio data to score in bulk."
            endpoint="/renewals/priority/csv"
            onComplete={(payload) => {
              try {
                const parsed = TriageScoreSchema.array().parse(payload);
                setResults(parsed);
              } catch (err) {
                console.error(err);
              }
            }}
          />
          {mutation.isError ? (
            <p className="text-sm text-red-500">{(mutation.error as Error).message}</p>
          ) : null}
        </div>
      </div>

      {results ? (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-slate-900">Priority results</h2>
          <div className="grid gap-6 md:grid-cols-2">
            {results.map((result) => (
              <article key={result.id} className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
                <header className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{result.id}</h3>
                    <p className="text-sm text-slate-500">Score</p>
                  </div>
                  <span className="text-3xl font-bold text-brand-600">{result.score.toFixed(2)}</span>
                </header>
                <ReasonsList title="Reasons" items={result.reasons} />
              </article>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}
