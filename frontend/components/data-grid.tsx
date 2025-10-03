"use client";

import clsx from "clsx";

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataGridProps<T extends { id?: string }>
  extends React.TableHTMLAttributes<HTMLTableElement> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
}

export function DataGrid<T extends { id?: string }>({
  columns,
  data,
  emptyMessage = "No records",
  className,
  ...tableProps
}: DataGridProps<T>) {
  return (
    <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-card">
      <table className={clsx("min-w-full divide-y divide-slate-200", className)} {...tableProps}>
        <thead className="bg-slate-50">
          <tr>
            {columns.map((column) => (
              <th
                key={String(column.key)}
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {data.length === 0 ? (
            <tr>
              <td className="px-4 py-6 text-center text-sm text-slate-500" colSpan={columns.length}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item, rowIndex) => (
              <tr key={item.id ?? rowIndex} className="hover:bg-slate-50/50">
                {columns.map((column) => (
                  <td key={String(column.key)} className="px-4 py-3 text-sm text-slate-700">
                    {column.render ? column.render(item) : String(item[column.key])}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
