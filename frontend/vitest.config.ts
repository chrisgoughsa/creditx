import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./setupTests.ts"],
    include: ["__tests__/**/*.test.ts?(x)", "components/**/*.test.ts?(x)", "hooks/**/*.test.ts?(x)"],
  },
});
