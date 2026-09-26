import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("portal_workspace_smoke", () => {
  it("renders the Documentz Portal shell", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { level: 1, name: "Documentz" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Personal Context Service Portal"),
    ).toBeInTheDocument();
  });
});
