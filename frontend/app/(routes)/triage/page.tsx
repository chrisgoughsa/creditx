"use client";

import { useMutation } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { DataGrid } from "../../../components/data-grid";
import { SubmissionForm } from "../../../components/submission-form";
import { UploadPanel } from "../../../components/upload-panel";
import { ReasonsList } from "../../../components/reasons-list";
import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import type { SubmissionInput } from "../../../lib/api";
import {
  fetchTriageScores,
  TriageResultsSchema,
  type TriageResults,
} from "../../../lib/api";
import { usePersistentState } from "../../../hooks/usePersistentState";

const defaultSubmission: SubmissionInput = {
  submission_id: "SUB-001",
  broker: "ABC Insurance",
  sector: "Manufacturing",
  exposure_limit: 1_000_000,
  debtor_days: 45,
  financials_attached: true,
  years_trading: 5,
  broker_hit_rate: 0.85,
  requested_cov_pct: 0.8,
  has_judgements: false,
};

export default function TriagePage() {
  const [submissions, setSubmissions, hydrated] = usePersistentState<SubmissionInput[]>(
    "creditx/triage-submissions",
    [defaultSubmission],
  );
  const [results, setResults] = useState<TriageResults | null>(null);

  const mutation = useMutation({
    mutationFn: fetchTriageScores,
    onSuccess: (data) => setResults(data),
  });

  function handleAdd(values: SubmissionInput) {
    setSubmissions((prev) => {
      const existingIndex = prev.findIndex((submission) => submission.submission_id === values.submission_id);
      if (existingIndex >= 0) {
        const updated = [...prev];
        updated[existingIndex] = values;
        return updated;
      }
      return [...prev, values];
    });
  }

  function handleRemove(submissionId: string) {
    setSubmissions((prev) => prev.filter((submission) => submission.submission_id !== submissionId));
  }

  const columns = useMemo(() => {
    return [
      {
        key: "submission_id",
        label: "Submission",
      },
      { key: "broker", label: "Broker" },
      { key: "sector", label: "Sector" },
      {
        key: "exposure_limit",
        label: "Exposure",
        render: (item: SubmissionInput) => item.exposure_limit.toLocaleString(),
      },
      { key: "debtor_days", label: "Debtor Days" },
      {
        key: "financials_attached",
        label: "Financials",
        render: (item: SubmissionInput) => (item.financials_attached ? "Yes" : "No"),
      },
      {
        key: "has_judgements",
        label: "Judgements",
        render: (item: SubmissionInput) => (item.has_judgements ? "Yes" : "No"),
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
    ];
  }, []);

  return (
    <section className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-2xl font-semibold text-slate-900">Underwriting triage</h1>
        <p className="max-w-3xl text-sm text-slate-600">
          Build a batch of submissions, run the triage model, and get a prioritized list with supporting
          reasoning. Upload a CSV or add submissions manually.
        </p>
        <p className="text-xs text-slate-500">
          {hydrated ? "Workspace autosaves locally." : "Restoring saved submissions…"}
        </p>
      </header>

      <SubmissionForm onAdd={handleAdd} />

      <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <DataGrid
          columns={columns as never}
          data={submissions}
          emptyMessage="Add at least one submission to run triage."
        />
        <div className="space-y-4">
          <Button
            type="button"
            onClick={() => mutation.mutate(submissions)}
            disabled={submissions.length === 0 || mutation.isPending}
            className="w-full"
          >
            {mutation.isPending ? "Running triage…" : "Run triage"}
          </Button>
          <UploadPanel
            label="CSV upload"
            description="Drag and drop a CSV of submissions for quick scoring."
            endpoint="/triage/underwriting/csv"
            onComplete={(payload) => {
              const parsed = TriageResultsSchema.safeParse(payload);
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
            <h2 className="text-xl font-semibold text-slate-900">Triage results</h2>
            <span className="text-xs text-slate-500">Weights version: {results.weights_version}</span>
          </div>
          <div className="grid gap-6 md:grid-cols-2">
            {results.scores.map((result) => (
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
          {Object.keys(results.feature_importance).length ? (
            <Card className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-800">Top signals in this batch</h3>
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
