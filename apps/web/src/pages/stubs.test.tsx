// Stub page honesty: Ask / Repository overview remain non-functional shells.
// Search is functional as of Week 9 Day 6 (covered by SearchPage.test.tsx).
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AskPage } from "../pages/AskPage";
import { RepositoryOverviewPage } from "../pages/RepositoryOverviewPage";

describe("stub pages", () => {
  it("Ask page does not claim a working ask form", () => {
    render(<AskPage />);
    expect(screen.getByRole("heading", { name: "Ask" })).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /ask/i })).not.toBeInTheDocument();
  });

  it("Repository overview remains a shell", () => {
    render(<RepositoryOverviewPage />);
    expect(screen.getByRole("heading", { name: "Repository overview" })).toBeInTheDocument();
  });
});
