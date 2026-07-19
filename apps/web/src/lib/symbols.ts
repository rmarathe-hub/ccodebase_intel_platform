export type SymbolKind =
  | "class"
  | "function"
  | "method"
  | "import"
  | "export"
  | "interface"
  | "type_alias";

export type FrameworkRole =
  | "fastapi_route"
  | "flask_route"
  | "django_view"
  | "sqlalchemy_model"
  | "celery_task"
  | "pydantic_model"
  | "react_component";

export interface SymbolParameter {
  name: string;
  annotation: string | null;
  kind: string;
}

export interface SymbolItem {
  id: string;
  snapshot_id: string;
  source_file_id: string;
  path: string;
  kind: SymbolKind | string;
  name: string;
  qualified_name: string;
  language: string;
  start_line: number;
  end_line: number;
  signature: string | null;
  docstring: string | null;
  decorators: string[];
  parameters: SymbolParameter[];
  return_annotation: string | null;
  is_async: boolean;
  framework_role: FrameworkRole | string | null;
  framework_detail: string | null;
  resolved_module: string | null;
  import_style: string | null;
  is_local_import: boolean | null;
  import_alias: string | null;
  created_at: string;
}

export interface SymbolListResponse {
  repository_id: string;
  snapshot_id: string | null;
  total: number;
  limit: number;
  offset: number;
  symbols: SymbolItem[];
}

export function symbolKindLabel(kind: string): string {
  switch (kind) {
    case "class":
      return "Class";
    case "function":
      return "Function";
    case "method":
      return "Method";
    case "import":
      return "Import";
    case "export":
      return "Export";
    case "interface":
      return "Interface";
    case "type_alias":
      return "Type alias";
    default:
      return kind;
  }
}

export function frameworkRoleLabel(role: string | null | undefined): string {
  if (!role) return "";
  switch (role) {
    case "fastapi_route":
      return "FastAPI route";
    case "flask_route":
      return "Flask route";
    case "django_view":
      return "Django view";
    case "sqlalchemy_model":
      return "SQLAlchemy model";
    case "celery_task":
      return "Celery task";
    case "pydantic_model":
      return "Pydantic model";
    case "react_component":
      return "React component";
    default:
      return role;
  }
}
