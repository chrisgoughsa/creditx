"use client";

import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { PricingCard } from "../../../components/pricing-card";
import { SubmissionForm } from "../../../components/submission-form";
import type { SubmissionInput } from "../../../lib/api";
import { fetchPricingSuggestions, type PricingResults } from "../../../lib/api";

import { DataGrid } from "../../../components/data-grid";
import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import { usePersistentState } from "../../../hooks/usePersistentState";

const defaultSubmission: SubmissionInput = {
  submission_id: "SUB-002",
  broker: "DEF Brokers",
  sector: "Logistics",
  exposure_limit: 500_000,
  debtor_days: 60,
  financials_attached: true,
  years_trading: 8,
  broker_hit_rate: 0.92,
  requested_cov_pct: 0.9,
  has_judgements: false,
};

export default function PricingPage() {
  const [submissions, setSubmissions, hydrated] = usePersistentState<SubmissionInput[]>(
    "creditx/pricing-submissions",
    [defaultSubmission],
  );
  const [results, setResults] = useState<PricingResults | null>(null);

  const mutation = useMutation({
    mutationFn: fetchPricingSuggestions,
    onSuccess: (data) => setResults(data),
  });

  function handleAdd(submission: SubmissionInput) {
    setSubmissions((prev) => {
      const index = prev.findIndex((item) => item.submission_id === submission.submission_id);
      if (index >= 0) {
        const updated = [...prev];
        updated[index] = submission;
        return updated;
      }
      return [...prev, submission];
    });
  }

  function handleRemove(submissionId: string) {
    setSubmissions((prev) => prev.filter((item) => item.submission_id !== submissionId));
  }

  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold text-slate-900">Pricing studio</h1>
        <p className="max-w-3xl text-sm text-slate-600">
          Combine base sector rates with risk adjustments to generate indicative pricing suggestions for each
          submission.
        </p>
        <p className="text-xs text-slate-500">
          {hydrated ? "Workspace autosaves locally." : "Restoring saved submissions…"}
        </p>
      </header>

      <SubmissionForm onAdd={handleAdd} />

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <DataGrid
          columns={[
            { key: "submission_id", label: "Submission" },
            { key: "sector", label: "Sector" },
            {
              key: "exposure_limit",
              label: "Exposure",
              render: (item: SubmissionInput) => item.exposure_limit.toLocaleString(),
            },
            {
              key: "broker_hit_rate",
              label: "Hit Rate",
              render: (item: SubmissionInput) => `${Math.round(item.broker_hit_rate * 100)}%`,
            },
            {
              key: "requested_cov_pct",
              label: "Coverage",
              render: (item: SubmissionInput) => `${Math.round(item.requested_cov_pct * 100)}%`,
            },
            {
              key: "actions",
              label: "",
              render: (item: SubmissionInput) => (
                <button
                  type="button"
                  onClick={() => handleRemove(item.submission_id)}
                  className="text-xs font-semibold text-red-500 hover:underline"
                >
                  Remove
                </button>
              ),
            },
          ] as never}
          data={submissions}
          emptyMessage="Add at least one submission to get pricing suggestions."
        />
        <div className="space-y-4">
          <Button
            type="button"
            onClick={() => mutation.mutate(submissions)}
            disabled={submissions.length === 0 || mutation.isPending}
            className="w-full"
          >
            {mutation.isPending ? "Calculating…" : "Generate pricing"}
          </Button>
          {mutation.isError ? (
            <p className="text-sm text-red-500">{(mutation.error as Error).message}</p>
          ) : null}
        </div>
      </div>

      {results ? (
        <div className="space-y-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <h2 className="text-xl font-semibold text-slate-900">Pricing suggestions</h2>
            <span className="text-xs text-slate-500">Weights version: {results.weights_version}</span>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {results.suggestions.map((suggestion) => (
              <PricingCard key={suggestion.id} suggestion={suggestion} />
            ))}
          </div>
          {Object.keys(results.feature_importance).length ? (
            <Card className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-800">Most common adjustments</h3>
              <ul className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                {Object.entries(results.feature_importance).map(([adjustment, count]) => (
                  <li key={adjustment} className="flex items-center justify-between rounded-2xl bg-slate-50 px-3 py-2">
                    <span>{adjustment}</span>
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
