import { fireEvent, render, screen } from "@testing-library/react";

import { Button } from "../components/ui/button";

describe("Button", () => {
  it("calls onClick when pressed", () => {
    const handleClick = vi.fn();
    render(
      <Button onClick={handleClick} type="button">
        Click me
      </Button>,
    );

    fireEvent.click(screen.getByText(/click me/i));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
