# Data Model Overview

```mermaid
graph TD
  Organization -->|has many| Project
  Project -->|has many| Environment
  Project -->|has many| Secret
  Project -->|has many| Locator
  Project -->|has many| TestCase
  TestCase -->|has many| TestStep
  Project -->|has many| Suite
  Suite -->|has many| SuiteTestCase
  SuiteTestCase --> TestCase
  Suite -->|has many| Schedule
  Suite -->|creates| Run
  Run -->|has many| RunStep
  Run -->|has many| RunArtifact
  Run -->|has many| RunLog
  RunStep --> TestCase
  Run --> Environment
  Run --> Dataset
  Dataset --> Project
```
