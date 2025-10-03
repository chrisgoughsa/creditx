"use client";

import clsx from "clsx";
import type { ButtonHTMLAttributes, DetailedHTMLProps } from "react";

const baseStyles =
  "inline-flex items-center justify-center rounded-full px-5 py-2 text-sm font-semibold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2";

const variantStyles: Record<ButtonVariant, string> = {
  primary: "bg-brand-500 text-white hover:bg-brand-600 focus-visible:outline-brand-500 disabled:bg-slate-300 disabled:text-slate-500",
  secondary:
    "bg-white text-brand-600 ring-1 ring-inset ring-brand-500 hover:bg-brand-50 focus-visible:outline-brand-500",
  ghost: "bg-transparent text-brand-600 hover:bg-brand-50 focus-visible:outline-brand-500",
};

export type ButtonVariant = "primary" | "secondary" | "ghost";

export type ButtonProps = DetailedHTMLProps<ButtonHTMLAttributes<HTMLButtonElement>, HTMLButtonElement> & {
  variant?: ButtonVariant;
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return <button className={clsx(baseStyles, variantStyles[variant], className)} {...props} />;
}
