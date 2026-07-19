// Stub page honesty: Search / Ask / Repository overview remain non-functional shells.
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AskPage } from "../pages/AskPage";
import { RepositoryOverviewPage } from "../pages/RepositoryOverviewPage";
import { SearchPage } from "../pages/SearchPage";

describe("stub pages", () => {
  it("Search page does not claim a working search form", () => {
    render(<SearchPage />);
    expect(screen.getByRole("heading", { name: "Search" })).toBeInTheDocument();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /search/i })).not.toBeInTheDocument();
  });

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
