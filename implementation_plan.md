# Comprehensive Data Quality Assessment Tool Plan

This plan details the steps to elevate the existing Luminia Data Quality tool into a comprehensive assessment and remediation suite, complete with advanced issue detection, detailed impact validation, and a premium "WOW" frontend.

## User Review Required

> [!IMPORTANT]
> The plan introduces near-duplicate detection and text inconsistency checks. 
> Please review the proposed column-level impact validation in the frontend before I proceed.

## Proposed Changes

### Backend (FastAPI, Pandas)

#### [MODIFY] analysis.py
We will enhance the `assess_dataframe` logic to detect a wider array of inconsistencies and integrity issues:
1. **Text Inconsistencies:** For string columns, detect trailing/leading whitespaces, empty strings representing missing data, and casing anomalies.
2. **Advanced Integrity Checks:** 
   - Detect "constant" columns containing only a single unique value.
   - Detect "near duplicates" by excluding obvious unique identifiers (like `ID` or columns where unique count == row count) when checking for duplicated rows.
3. **Suggestions Engine:** Provide strategies like `standardize_text` (stripping whitespace, consistent casing) or `drop_constant_column`.

#### [MODIFY] remediation.py
Upgrade the application of rules to handle new transformations and provide column-level validation:
1. **New Strategies:** Implement `standardize_text` and `drop_near_duplicates`.
2. **Column-Level Impact Analysis:** Instead of returning just a global "rows dropped" metric, we will capture and return the before/after state for each targeted column (e.g., missing values before/after, unique count before/after). This establishes true validation.

---

### Frontend (React, Vite, CSS)

#### [MODIFY] src/components/Dashboard.jsx
Enhance the Dashboard to support comprehensive remediation reporting and handle new issue types:
1. **New Issue Badges:** Add UI indicators for Text Inconsistencies, Constant Columns, and Near Duplicates.
2. **Detailed Validation Report:** Refactor the Impact Report view. Instead of just "Rows Dropped" and "Retention", display a detailed grid showing exactly what changed *per column* (e.g., "Age: Imputed 5 missing values" or "Name: Standardized casing for 3 rows").

#### [MODIFY] src/index.css
Elevate the "WOW" factor to ensure a premium look:
1. **Impact Validation Styling:** Create specialized visual cards for the before/after validation metrics, utilizing smooth transitions and gradient borders.
2. **Micro-animations:** Add hover effects and staggered fade-ins for table rows and stat cards to make the data feel dynamic and alive.

## Open Questions

> [!QUESTION]
> For text standardisation (e.g., fixing casing), should we default to converting everything to Title Case globally, or Lowercase?

## Verification Plan

### Automated/Manual Verification
1. I will start the React Vite server and run the FastAPI server locally.
2. I will upload `sample_data.csv` (which contains near-duplicates, outliers, and missing values).
3. Verify that the new discrepancies (e.g., the near-duplicate "Jane Smith" entries with different IDs) are correctly identified in the UI.
4. Apply remediation rules and verify that the column-level "Impact Report" visually demonstrates exactly how the columns were fixed.
