// Stub page honesty: Repository overview remains a non-functional shell.
// Ask is functional (AskPage.test.tsx). Search is functional (SearchPage.test.tsx).
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RepositoryOverviewPage } from "../pages/RepositoryOverviewPage";

describe("stub pages", () => {
  it("Repository overview remains a shell", () => {
    render(<RepositoryOverviewPage />);
    expect(screen.getByRole("heading", { name: "Repository overview" })).toBeInTheDocument();
  });
});
