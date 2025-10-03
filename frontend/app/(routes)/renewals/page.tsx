"use client";

import { useMutation } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { DataGrid } from "../../../components/data-grid";
import { PolicyForm } from "../../../components/policy-form";
import { UploadPanel } from "../../../components/upload-panel";
import { ReasonsList } from "../../../components/reasons-list";
import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import type { PolicyInput } from "../../../lib/api";
import {
  fetchRenewalPriorities,
  RenewalResultsSchema,
  type RenewalResults,
} from "../../../lib/api";
import { usePersistentState } from "../../../hooks/usePersistentState";

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
  const [policies, setPolicies, hydrated] = usePersistentState<PolicyInput[]>(
    "creditx/renewal-policies",
    [defaultPolicy],
  );
  const [results, setResults] = useState<RenewalResults | null>(null);

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
        <p className="text-xs text-slate-500">
          {hydrated ? "Workspace autosaves locally." : "Restoring saved policies…"}
        </p>
      </header>

      <PolicyForm onAdd={handleAdd} />

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <DataGrid columns={columns as never} data={policies} emptyMessage="Add a policy to run scoring." />
        <div className="space-y-4">
          <Button
            type="button"
            onClick={() => mutation.mutate(policies)}
            disabled={policies.length === 0 || mutation.isPending}
            className="w-full"
          >
            {mutation.isPending ? "Running priority…" : "Run renewal priority"}
          </Button>
          <UploadPanel
            label="CSV upload"
            description="Upload renewal portfolio data to score in bulk."
            endpoint="/renewals/priority/csv"
            onComplete={(payload) => {
              const parsed = RenewalResultsSchema.safeParse(payload);
              if (parsed.success) {
                setResults(parsed.data);
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
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Priority results</h2>
            <span className="text-xs text-slate-500">Weights version: {results.weights_version}</span>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {results.scores.map((result) => (
              <article key={result.id} className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-card">
                <header className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900">{result.id}</h3>
                    <p className="text-sm text-slate-500">Priority score</p>
                  </div>
                  <span className="text-3xl font-bold text-brand-600">{result.score.toFixed(2)}</span>
                </header>
                <ReasonsList title="Reasons" items={result.reasons} />
              </article>
            ))}
          </div>
          {Object.keys(results.feature_importance).length ? (
            <Card className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-800">Top drivers</h3>
              <ul className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                {Object.entries(results.feature_importance).map(([reason, count]) => (
                  <li key={reason} className="flex items-center justify-between rounded-2xl bg-slate-50 px-3 py-2">
                    <span>{reason}</span>
                    <span className="font-semibold text-slate-800">{count}</span>
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
