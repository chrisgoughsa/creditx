"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { PolicyInput } from "../lib/api";
import { Card } from "./ui/card";
import { Button } from "./ui/button";

const PolicyFormSchema = z.object({
  policy_id: z.string().min(1, "Required"),
  broker: z.string().min(1, "Required"),
  sector: z.enum(["Retail", "Manufacturing", "Logistics", "Agri", "Services", "Other"]),
  current_premium: z.coerce.number().nonnegative(),
  limit: z.coerce.number().nonnegative(),
  utilization_pct: z.coerce.number().min(0).max(1),
  claims_last_24m_cnt: z.coerce.number().nonnegative(),
  claims_ratio_24m: z.coerce.number().nonnegative(),
  days_to_expiry: z.coerce.number().nonnegative(),
  requested_change_pct: z.coerce.number(),
});

export type PolicyFormValues = z.infer<typeof PolicyFormSchema>;

const sectorOptions = [
  "Retail",
  "Manufacturing",
  "Logistics",
  "Agri",
  "Services",
  "Other",
] as const;

export function PolicyForm({ onAdd }: { onAdd(policy: PolicyInput): void }) {
  const form = useForm<PolicyFormValues>({
    resolver: zodResolver(PolicyFormSchema),
    defaultValues: {
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
    },
  });

  return (
    <Card>
      <form
        className="grid gap-4"
        onSubmit={form.handleSubmit((values) => {
          onAdd({
            ...values,
            current_premium: Number(values.current_premium),
            limit: Number(values.limit),
            utilization_pct: Number(values.utilization_pct),
            claims_last_24m_cnt: Number(values.claims_last_24m_cnt),
            claims_ratio_24m: Number(values.claims_ratio_24m),
            days_to_expiry: Number(values.days_to_expiry),
            requested_change_pct: Number(values.requested_change_pct),
          });
          form.reset();
        })}
      >
      <div className="grid gap-6 sm:grid-cols-2">
        <FormField label="Policy ID" error={form.formState.errors.policy_id?.message}>
          <input className="input" {...form.register("policy_id")} placeholder="POL-001" />
        </FormField>
        <FormField label="Broker" error={form.formState.errors.broker?.message}>
          <input className="input" {...form.register("broker")} />
        </FormField>
        <FormField label="Sector" error={form.formState.errors.sector?.message}>
          <select className="input" {...form.register("sector")}>
            {sectorOptions.map((sector) => (
              <option key={sector}>{sector}</option>
            ))}
          </select>
        </FormField>
        <FormField label="Current Premium" error={form.formState.errors.current_premium?.message}>
          <input className="input" type="number" step="100" {...form.register("current_premium")} />
        </FormField>
        <FormField label="Limit" error={form.formState.errors.limit?.message}>
          <input className="input" type="number" step="1000" {...form.register("limit")} />
        </FormField>
        <FormField label="Utilization %" error={form.formState.errors.utilization_pct?.message}>
          <input className="input" type="number" step="0.01" {...form.register("utilization_pct")} />
        </FormField>
        <FormField
          label="Claims Last 24m"
          error={form.formState.errors.claims_last_24m_cnt?.message}
        >
          <input className="input" type="number" {...form.register("claims_last_24m_cnt")} />
        </FormField>
        <FormField label="Claims Ratio 24m" error={form.formState.errors.claims_ratio_24m?.message}>
          <input className="input" type="number" step="0.01" {...form.register("claims_ratio_24m")} />
        </FormField>
        <FormField label="Days to Expiry" error={form.formState.errors.days_to_expiry?.message}>
          <input className="input" type="number" {...form.register("days_to_expiry")} />
        </FormField>
        <FormField label="Requested Change %" error={form.formState.errors.requested_change_pct?.message}>
          <input className="input" type="number" step="0.01" {...form.register("requested_change_pct")} />
        </FormField>
      </div>
        <Button type="submit" className="w-full">
          Add policy
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
