"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { SubmissionInput } from "../lib/api";
import { Card } from "./ui/card";
import { Button } from "./ui/button";

const SubmissionFormSchema = z.object({
  submission_id: z.string().min(1, "Required"),
  broker: z.string().min(1, "Required"),
  sector: z.enum(["Retail", "Manufacturing", "Logistics", "Agri", "Services", "Other"]),
  exposure_limit: z.coerce.number().nonnegative(),
  debtor_days: z.coerce.number().nonnegative(),
  financials_attached: z.boolean(),
  years_trading: z.coerce.number().nonnegative(),
  broker_hit_rate: z.coerce.number().min(0).max(1),
  requested_cov_pct: z.coerce.number().min(0).max(1),
  has_judgements: z.boolean(),
});

export type SubmissionFormValues = z.infer<typeof SubmissionFormSchema>;

const sectorOptions = [
  "Retail",
  "Manufacturing",
  "Logistics",
  "Agri",
  "Services",
  "Other",
] as const;

interface SubmissionFormProps {
  onAdd(values: SubmissionInput): void;
  defaultValues?: Partial<SubmissionFormValues>;
}

export function SubmissionForm({ onAdd, defaultValues }: SubmissionFormProps) {
  const form = useForm<SubmissionFormValues>({
    resolver: zodResolver(SubmissionFormSchema),
    defaultValues: {
      submission_id: "SUB-001",
      broker: "Example Broker",
      sector: "Retail",
      exposure_limit: 1_000_000,
      debtor_days: 45,
      financials_attached: true,
      years_trading: 5,
      broker_hit_rate: 0.75,
      requested_cov_pct: 0.8,
      has_judgements: false,
      ...defaultValues,
    },
  });

  return (
    <Card>
      <form
        className="grid gap-4"
        onSubmit={form.handleSubmit((values) => {
          onAdd({
            ...values,
            exposure_limit: Number(values.exposure_limit),
            debtor_days: Number(values.debtor_days),
            years_trading: Number(values.years_trading),
            broker_hit_rate: Number(values.broker_hit_rate),
            requested_cov_pct: Number(values.requested_cov_pct),
          });
          form.reset();
        })}
      >
      <div className="grid gap-6 sm:grid-cols-2">
        <FormField label="Submission ID" error={form.formState.errors.submission_id?.message}>
          <input
            className="input"
            {...form.register("submission_id")}
            placeholder="SUB-001"
          />
        </FormField>
        <FormField label="Broker" error={form.formState.errors.broker?.message}>
          <input className="input" {...form.register("broker")} placeholder="Broker name" />
        </FormField>
        <FormField label="Sector" error={form.formState.errors.sector?.message}>
          <select className="input" {...form.register("sector")}>
            {sectorOptions.map((sector) => (
              <option key={sector}>{sector}</option>
            ))}
          </select>
        </FormField>
        <FormField label="Exposure Limit" error={form.formState.errors.exposure_limit?.message}>
          <input className="input" type="number" step="1000" {...form.register("exposure_limit")} />
        </FormField>
        <FormField label="Debtor Days" error={form.formState.errors.debtor_days?.message}>
          <input className="input" type="number" {...form.register("debtor_days")} />
        </FormField>
        <FormField label="Years Trading" error={form.formState.errors.years_trading?.message}>
          <input className="input" type="number" step="0.1" {...form.register("years_trading")} />
        </FormField>
        <FormField label="Broker Hit Rate" error={form.formState.errors.broker_hit_rate?.message}>
          <input className="input" type="number" step="0.01" {...form.register("broker_hit_rate")} />
        </FormField>
        <FormField label="Requested Coverage %" error={form.formState.errors.requested_cov_pct?.message}>
          <input className="input" type="number" step="0.01" {...form.register("requested_cov_pct")} />
        </FormField>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <FormField label="Financials Attached">
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input type="checkbox" {...form.register("financials_attached")} />
            Yes
          </label>
        </FormField>
        <FormField label="Outstanding Judgements">
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input type="checkbox" {...form.register("has_judgements")} />
            Yes
          </label>
        </FormField>
      </div>
        <Button type="submit" className="w-full">
          Add submission
        </Button>
      </form>
    </Card>
  );
}

function FormField({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm font-medium text-slate-700">
      <span>{label}</span>
      {children}
      {error ? <span className="text-xs text-red-500">{error}</span> : null}
    </label>
  );
}

export const submissionColumns = [
  { key: "submission_id", label: "Submission" },
  { key: "broker", label: "Broker" },
  { key: "sector", label: "Sector" },
  { key: "exposure_limit", label: "Exposure" },
  { key: "debtor_days", label: "Debtor Days" },
  { key: "financials_attached", label: "Financials" },
  { key: "years_trading", label: "Years" },
  { key: "broker_hit_rate", label: "Hit Rate" },
];
