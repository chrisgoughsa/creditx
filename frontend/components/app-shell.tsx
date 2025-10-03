"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";
import clsx from "clsx";

const links = [
  { href: "/", label: "Overview" },
  { href: "/triage", label: "Underwriting Triage" },
  { href: "/renewals", label: "Renewal Priority" },
  { href: "/pricing", label: "Pricing Studio" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur">
        <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-lg font-semibold text-brand-600">
            CreditX Portal
          </Link>
          <ul className="flex gap-4 text-sm font-medium text-slate-600">
            {links.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={clsx(
                    "rounded-full px-4 py-2 transition-colors",
                    pathname === link.href
                      ? "bg-brand-500 text-white shadow-card"
                      : "hover:bg-slate-100"
                  )}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-10">
        {children}
      </main>
    </div>
  );
}
