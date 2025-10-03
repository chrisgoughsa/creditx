import type { Metadata } from "next";
import { ReactNode } from "react";

import "./globals.css";
import { Providers } from "../components/providers";
import { AppShell } from "../components/app-shell";

export const metadata: Metadata = {
  title: "CreditX Portal",
  description: "Modern underwriting and pricing workspace for CreditX.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
