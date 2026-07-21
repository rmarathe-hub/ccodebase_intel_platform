import { useCallback, useState } from "react";
import { useSearchParams } from "react-router-dom";

/** Keep repository selection in sync with `?repo=` for workspace deep-links. */
export function useRepoQueryParam(fallbackId = ""): {
  selectedId: string;
  selectRepository: (nextId: string) => void;
} {
  const [searchParams, setSearchParams] = useSearchParams();
  const repoFromUrl = searchParams.get("repo") ?? "";
  const [repositoryId, setRepositoryId] = useState(repoFromUrl);

  const selectedId = repositoryId || repoFromUrl || fallbackId;

  const selectRepository = useCallback(
    (nextId: string) => {
      setRepositoryId(nextId);
      const next = new URLSearchParams(searchParams);
      if (nextId) next.set("repo", nextId);
      else next.delete("repo");
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  return { selectedId, selectRepository };
}
