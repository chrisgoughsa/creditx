import Link from "next/link";

const sections = [
  {
    title: "Underwriting Triage",
    description:
      "Score submissions instantly, surface key risk drivers, and align underwriting queues.",
    href: "/triage",
    cta: "Open triage workspace",
  },
  {
    title: "Renewal Priority",
    description:
      "Identify expiring portfolios that need attention using utilization and loss ratio signals.",
    href: "/renewals",
    cta: "Review renewals",
  },
  {
    title: "Pricing Studio",
    description:
      "Experiment with suggested rates, track adjustments, and export pricing recommendations.",
    href: "/pricing",
    cta: "Launch pricing tools",
  },
];

export default function HomePage() {
  return (
    <section className="space-y-10">
      <header className="space-y-4">
        <h1 className="text-3xl font-semibold text-slate-900">Welcome to CreditX</h1>
        <p className="max-w-2xl text-base text-slate-600">
          Run underwriting triage, renewal prioritization, and pricing suggestions through a
          single, modern workspace. Start with a JSON request, upload a CSV, or explore sample
          data.
        </p>
      </header>
      <div className="grid gap-6 sm:grid-cols-2">
        {sections.map((section) => (
          <article
            key={section.title}
            className="flex h-full flex-col justify-between rounded-3xl border border-slate-200 bg-white p-6 shadow-card"
          >
            <div className="space-y-3">
              <h2 className="text-xl font-semibold text-slate-900">{section.title}</h2>
              <p className="text-sm text-slate-600">{section.description}</p>
            </div>
            <div className="pt-6">
              <Link
                href={section.href}
                className="inline-flex items-center gap-2 rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-600"
              >
                {section.cta}
                <span aria-hidden>→</span>
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
