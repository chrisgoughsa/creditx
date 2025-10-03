import { renderHook, act } from "@testing-library/react";

import { usePersistentState } from "./usePersistentState";

const KEY = "test/persistent";

describe("usePersistentState", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("hydrates with default value", () => {
    const { result } = renderHook(() => usePersistentState(KEY, ["foo"]));
    const [value, , hydrated] = result.current;
    expect(value).toEqual(["foo"]);
    expect(hydrated).toBe(true);
  });

  it("persists updates to localStorage", () => {
    const { result } = renderHook(() => usePersistentState(KEY, ["foo"]));

    act(() => {
      const [, setValue] = result.current;
      setValue(() => ["bar"]);
    });

    const [value] = result.current;
    expect(value).toEqual(["bar"]);
    expect(JSON.parse(window.localStorage.getItem(KEY) ?? "[]")).toEqual(["bar"]);
  });
});
