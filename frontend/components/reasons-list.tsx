interface ReasonsListProps {
  title: string;
  items: string[];
}

export function ReasonsList({ title, items }: ReasonsListProps) {
  if (items.length === 0) {
    return null;
  }
  return (
    <div className="rounded-2xl bg-slate-50 p-4">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</h4>
      <ul className="mt-2 space-y-1 text-sm text-slate-700">
        {items.map((reason) => (
          <li key={reason} className="flex items-start gap-2">
            <span className="mt-1 inline-block h-1.5 w-1.5 rounded-full bg-brand-500" aria-hidden />
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
