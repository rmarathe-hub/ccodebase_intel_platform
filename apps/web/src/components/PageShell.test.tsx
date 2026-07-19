import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageShell } from "../components/PageShell";

describe("PageShell", () => {
  it("renders title and description", () => {
    render(<PageShell title="Search" description="Find symbols and text." />);
    expect(screen.getByRole("heading", { name: "Search" })).toBeInTheDocument();
    expect(screen.getByText("Find symbols and text.")).toBeInTheDocument();
  });
});
