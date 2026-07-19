import { describe, expect, it } from "vitest";
import { frameworkRoleLabel, symbolKindLabel } from "./symbols";

describe("symbolKindLabel", () => {
  it("labels known kinds", () => {
    expect(symbolKindLabel("class")).toBe("Class");
    expect(symbolKindLabel("function")).toBe("Function");
    expect(symbolKindLabel("method")).toBe("Method");
    expect(symbolKindLabel("import")).toBe("Import");
    expect(symbolKindLabel("export")).toBe("Export");
    expect(symbolKindLabel("interface")).toBe("Interface");
    expect(symbolKindLabel("type_alias")).toBe("Type alias");
  });
});

describe("frameworkRoleLabel", () => {
  it("labels known roles", () => {
    expect(frameworkRoleLabel("fastapi_route")).toBe("FastAPI route");
    expect(frameworkRoleLabel("pydantic_model")).toBe("Pydantic model");
    expect(frameworkRoleLabel("react_component")).toBe("React component");
    expect(frameworkRoleLabel(null)).toBe("");
  });
});
