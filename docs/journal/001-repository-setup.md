# Lesson 1: Repository setup

## Completed

- Initialized the local Git repository.
- Renamed the default branch to main.
- Configured SSH authentication for Azure DevOps and GitHub.
- Committed the README and ignore rules.
- Pushed main to Azure Repos.
- Created a public GitHub repository and pushed the same history.

## Repository responsibilities

- origin points to Azure Repos, the source of truth.
- github points to the GitHub portfolio mirror.
- Local main tracks origin/main.
- Mirroring is currently manual.

## Lessons learned

Write your own explanation of:

1. Why SSH authentication works without interactive shell access.
2. The difference between staging, committing, and pushing.
3. Why pushing to origin does not update github.
4. Why we use --ff-only when updating local main.

## Next steps

Configure branch protection and complete the first pull request.
Automated build validation will follow once a CI pipeline exists.

## Solo-review exception

This lab allows the pull request author to approve their own changes
because only one person is working on the project.

This demonstrates the approval workflow but does not provide
independent review. In a team environment, another person should
review and approve the changes.

## Next steps

Link this documentation change to Azure Boards Task #2.
Implement automated pull request validation through Azure Pipelines.