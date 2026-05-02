# Clinical Recommendation & Prognosis Design Blueprint

This document outlines a unified data model, preprocessing strategy, modeling approaches, evaluation, and serving guidelines for a nutrition-supplement recommendation and prognosis system driven by clinical data.

## 1. Data Collection & Schema

All tables share a stable, privacy-preserving `patient_id` and are joinable by encounter or observation dates.

| Domain | Table | Key Columns | Notes |
| --- | --- | --- | --- |
| Patients | `patients` | `patient_id` (PK), `birth_date`, `sex`, `baseline_conditions` | Static demographics and chronic conditions (JSON/array). |
| Encounters | `encounters` | `encounter_id` (PK), `patient_id` (FK), `encounter_date`, `encounter_type` | Links event-centric tables. |
| Labs/Vitals | `lab_results` | `(patient_id, observation_date, test_code)`, `value`, `unit`, `reference_range` | Include normalized code system (LOINC) and flag for abnormality. |
| Diagnoses | `diagnoses` | `(patient_id, encounter_id, diagnosis_code)`, `diagnosis_date`, `diagnosis_type` | ICD/SNOMED codes; store chronicity indicator. |
| Prescriptions | `prescriptions` | `(patient_id, encounter_id, order_datetime)`, `drug_code`, `dose`, `route`, `days_supply`, `refills` | Map to RxNorm; include intent (acute/chronic). |
| Medication Administration | `med_admin` | `(patient_id, admin_datetime, drug_code)`, `dose`, `route` | Captures actual administration in facility. |
| Supplement Purchases | `supplement_purchases` | `(patient_id, purchase_datetime, product_id)`, `quantity`, `price`, `channel` | `product_id` maps to curated supplement catalog. |
| Supplement Intake | `supplement_intake` | `(patient_id, intake_datetime, product_id)`, `amount`, `frequency`, `self_reported` | Optional EMA/app-logged adherence. |
| Product Catalog | `supplement_catalog` | `product_id` (PK), `brand`, `ingredients` (array), `dosage_form`, `tags` (benefit/effect), `contraindications` | Content features for cold-start and safety. |

### Join Strategy
- Primary join keys: `patient_id` and time (`encounter_date` or `observation_date`).
- Snapshots: build patient-time cohorts using index date (e.g., exam date) with look-back windows for history and forward windows for labels.

## 2. Preprocessing & Feature Engineering

### For Recommendation
- Build a user–item matrix `R` where rows = `patient_id`, columns = `product_id`.
- Implicit feedback score example: `score = freq_weight * log(1 + count) + recency_weight * exp(-Δt / τ)`, combining purchase and intake events.
- Normalize by user activity (e.g., BM25 or TF-IDF style) to reduce popularity bias.
- Mask items contraindicated for the user (allergies, interacting drugs) before training and inference.

### For Prognosis
- Align clinical variables on an index date (e.g., health checkup). Create rolling windows (e.g., 3, 6, 12 months) for labs, vitals, diagnoses, prescriptions, and supplement intake.
- Aggregate statistics: mean, median, slope (trend), last value, min/max, variability (std/IQR), count of abnormal flags.
- Event label: binary (e.g., incident condition within 1 year) or time-to-event (event_date − index_date, censored if none).
- Encode time-varying sequences with lightweight models (TCN/Transformer encoder) or summary statistics when data is sparse.
- One-hot or embedding representations for diagnoses, drugs, and supplement tags; apply dimensionality reduction (e.g., truncated SVD) to control sparsity.

## 3. SLIM-Based Recommendation Model
- Optimize item–item similarity matrix `W` with L1/L2 penalties via ADMM or coordinate descent.
- Loss: `min_W ||R - RW||_F^2 + λ1 * ||W||_1 + λ2 * ||W||_2^2` subject to `diag(W)=0` and `W ≥ 0` for interpretability.
- Prediction: `
\hat{r}_{u,i} = \sum_{j \neq i} R_{u,j} W_{j,i}`.
- Cold-start/backoff:
  - Content-based similarity using `supplement_catalog.ingredients` and `tags` (TF-IDF + cosine or a learned encoder).
  - Popularity/time-decay fallback: `pop(i) = decay(sum_events_i, Δt)`, blended with SLIM scores when user/item data is sparse.
  - Boost or filter via clinical rules (contraindications, age restrictions).

## 4. Prognosis Modeling
- If event time is available: CoxPH, Random Survival Forests, or DeepSurv with `time` and `event` indicators; evaluate proportional hazards assumptions where applicable.
- If only binary outcomes: gradient boosting (XGBoost/LightGBM) or TabNet with class weighting; consider calibrated probabilities (Platt/Isotonic).
- Sequence-aware option: TCN/Transformer encoder over ordered lab/vital sequences with positional encodings; pool outputs for downstream survival/classification head.

## 5. Evaluation
- Recommendation: MAP@K, NDCG@K, Hit@K; coverage/diversity/novelty (intra-list distance, catalog coverage, popularity-weighted novelty).
- Prognosis: AUROC, AUPRC, Brier score, calibration (reliability plots/ECE). For survival: C-index and integrated Brier score with patient-level splits.
- Split by patient (no leakage), using time-based or grouped cross-validation; maintain a hold-out temporal test set.

## 6. Integrated Output Strategy
- Combine recommendation score `s_rec` and predicted risk `s_risk` to prioritize high-risk patients: e.g., `score = α * s_rec + β * s_risk` with clinician-defined thresholds.
- Safety layer: remove items conflicting with `contraindications`, `current_prescriptions`, or recorded allergies; flag potential drug–supplement interactions for review.
- Provide explanation snippets: top contributing historical items for SLIM and key risk drivers from prognosis model (e.g., SHAP summaries).

## 7. Serving & Batch Pipeline
- ETL: scheduled ingestion from EHR/pharmacy/apps into the above schema; apply de-identification and audit logging.
- Model refresh: nightly/weekly retraining with drift checks; cache latest item similarities and risk scores.
- Delivery: REST/gRPC endpoints for real-time recommendations; batch reports for care managers. Log impressions, clicks, acceptance, and adverse events for monitoring.
- Monitoring: track latency, error rates, coverage, calibration drift, user response rates, and re-admission/visit rates.

## 8. Governance & Risk Management
- Enforce de-identification, PHI minimization, and role-based access; keep a data processing register.
- Bias/drift monitoring by demographic slices; retrain or recalibrate when performance degrades.
- Clinical oversight: maintain change logs, contraindication rule reviews, and periodic expert validation of recommendations.
