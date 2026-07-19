from app.models import IndexingJob, Repository, RepositorySnapshot, User


def test_core_tables_registered() -> None:
    table_names = set(User.metadata.tables.keys())
    assert {
        "users",
        "repositories",
        "repository_snapshots",
        "indexing_jobs",
    }.issubset(table_names)


def test_indexing_job_default_status() -> None:
    assert IndexingJob.__table__.c.status.nullable is False
    assert RepositorySnapshot.__table__.c.commit_sha.type.length == 64


def test_repository_identity_unique() -> None:
    constraint_names = {constraint.name for constraint in Repository.__table__.constraints}
    assert "uq_repositories_identity" in constraint_names
