# Contributing Guidelines

Thank you for contributing to this repository.

This project maintains constituent snapshots and historical composition records for stock indices. Data quality matters more than update speed, so every proposed change must be traceable to a reliable source.

## What to Include

For any change that adds, removes, or updates index constituent information, include:

- the affected index name
- the affected file or files
- the effective date of the change
- the original data source
- enough evidence for reviewers to verify the update

Acceptable evidence usually includes one or more of the following:

- official index provider announcements
- exchange notices
- official constituent lists published by the provider or exchange
- other authoritative public disclosures

## Source Requirement

If you change index data, you must provide source evidence.

At minimum, include:

- a source link
- the publication date or effective date
- a short note describing how the source supports the proposed change

Contributions without verifiable source evidence may be closed or left unmerged.

## Recommended Workflow

1. Open an issue with the proposed update.
2. Attach the source link and a short evidence summary.
3. Submit a pull request that references the issue.
4. Keep the data change limited to the relevant files.

## Pull Request Notes

In your pull request description, include:

- what changed
- why it changed
- which source was used
- any assumptions or normalization applied to the raw data