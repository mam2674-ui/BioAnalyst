"""
Curated seed dataset for BioAnalyst -- a unified market-intelligence
platform covering two sectors:

- **biotech_als**: amyotrophic lateral sclerosis (ALS), five public
  biotech companies with SEC-filed financials.
- **neurotech_bci**: brain-computer interfaces (BCI) for assistive
  communication/computer control, seven mostly-private companies with
  venture funding disclosures instead of quarterly filings.

Every fact below was retrieved via web search and, where noted, direct SEC
/ ClinicalTrials.gov fetches (see SOURCE_DOCUMENTS for exact URLs,
publishers, and dates -- biotech data retrieved 2026-10-27, neurotech data
originally retrieved 2026-10-23 as a separate project before being merged
here). This is NOT synthetic placeholder data -- it reflects real
companies, trials/studies, and financial/funding disclosures -- but it is
a small number of research passes, not a maintained feed. Fields that
could not be confidently resolved are marked "not found" or carry an
explicit discrepancy note; see docs/DATA_DICTIONARY.md section 4 for the
full verification checklist before citing any flagged field externally.

Why these two sectors together: they were originally two separate student
projects (NeuroScope for neurotech, BioSignal for biotech) unified into
one platform. Combining them surfaces a real, useful contrast: biotech_als
has public companies with the orderly but slow SEC-filing cadence, while
neurotech_bci has mostly-private companies with faster-moving but far
less standardized venture-funding disclosures -- and the two sectors'
financial data genuinely cannot be compared apples-to-apples, which is
exactly why `financial_periods` and `funding_rounds` are two separate
tables rather than one awkwardly-overloaded one.
"""

RETRIEVED = "2026-10-27"
RETRIEVED_NEUROTECH = "2026-10-23"  # neurotech data's original research pass date

# ---------------------------------------------------------------------------
# Sectors
# ---------------------------------------------------------------------------
SECTORS = {
    "biotech_als": dict(
        name="Biotechnology -- Amyotrophic Lateral Sclerosis (ALS)",
        central_question="How do companies pursuing ALS treatments compare scientifically "
                          "and commercially, and what evidence or milestones could change the assessment?",
        scope_note="Five public companies, ten tracked clinical trials, SEC-filed quarterly financials.",
    ),
    "neurotech_bci": dict(
        name="Neurotechnology -- Brain-Computer Interfaces (BCI)",
        central_question="Which brain-computer interface companies address similar needs, how "
                          "strong is their supporting evidence, and what business questions remain unresolved?",
        scope_note="Seven companies (six direct, one adjacent) in assistive communication/computer "
                    "control; mostly privately held, so venture funding rounds substitute for "
                    "quarterly SEC filings.",
    ),
}

# ---------------------------------------------------------------------------
# Source documents (cited by key from trials / financial_periods / claims)
# ---------------------------------------------------------------------------
SOURCE_DOCUMENTS = {
    "ionis_qalsody_approval": dict(
        title="FDA Approves Qalsody (tofersen), First Treatment Targeting a Genetic Cause of ALS",
        url="https://ir.ionis.com/news-releases/news-release-details/fda-approves-qalsodytm-tofersen-first-treatment-targeting",
        publisher="Ionis Pharmaceuticals (investor relations)", document_type="press_release",
        published_date="2023-04-25", retrieved_date=RETRIEVED,
    ),
    "als_today_qalsody": dict(
        title="FDA approves tofersen, now Qalsody, as treatment for SOD1-ALS",
        url="https://alsnewstoday.com/news/fda-approves-tofersen-now-qalsody-treatment-adults-sod1-als/",
        publisher="ALS News Today", document_type="news",
        published_date="2023-04-25", retrieved_date=RETRIEVED,
    ),
    "biib_10q_q2_2026": dict(
        title="Biogen Inc. Form 10-Q, quarter ended June 30, 2026",
        url="https://www.sec.gov/Archives/edgar/data/0000875045/000087504526000075/biib-20260630.htm",
        publisher="SEC EDGAR", document_type="sec_10q",
        published_date="2026-08", retrieved_date=RETRIEVED,
    ),
    "als_today_phoenix_fail": dict(
        title="Relyvrio withdrawn from US, Canada after Phase 3 trial results",
        url="https://alsnewstoday.com/news/relyvrio-withdrawn-from-us-canada-after-phase-3-trial-results/",
        publisher="ALS News Today", document_type="news",
        published_date="2024-04-04", retrieved_date=RETRIEVED,
    ),
    "biospace_amylyx_pull": dict(
        title="Amylyx to Pull ALS Drug Relyvrio From US, Canada Markets After Phase III Fail",
        url="https://www.biospace.com/amylyx-to-pull-als-drug-relyvrio-from-us-canada-markets-after-phase-iii-fail",
        publisher="BioSpace", document_type="news",
        published_date="2024-04-04", retrieved_date=RETRIEVED,
    ),
    "amlx_10q_q2_2026": dict(
        title="Amylyx Pharmaceuticals, Inc. Form 10-Q, quarter ended June 30, 2026",
        url="https://www.sec.gov/Archives/edgar/data/0001658551/000119312526336682/amlx-20260630.htm",
        publisher="SEC EDGAR", document_type="sec_10q",
        published_date="2026-08", retrieved_date=RETRIEVED,
    ),
    "geneonline_brainstorm_rtf": dict(
        title="FDA Rejects BrainStorm Cell Therapeutics' BLA For ALS Drug",
        url="https://www.geneonline.com/?p=25213",
        publisher="GeneOnline", document_type="news",
        published_date="2022-11", retrieved_date=RETRIEVED,
    ),
    "ctarena_brainstorm_spa": dict(
        title="BrainStorm, new trial agreed with FDA after failure",
        url="https://www.clinicaltrialsarena.com/news/brainstorm-new-trial-agree-fda-after-failure/",
        publisher="Clinical Trials Arena", document_type="news",
        published_date="2025-05", retrieved_date=RETRIEVED,
    ),
    "brainstorm_ir_fy2025": dict(
        title="BrainStorm Cell Therapeutics Announces Full Year 2025 Financial Results and Provides Corporate Update",
        url="https://ir.brainstorm-cell.com/2026-03-31-BrainStorm-Cell-Therapeutics-Announces-Full-Year-2025-Financial-Results-and-Provides-Corporate-Update",
        publisher="BrainStorm Cell Therapeutics (investor relations)", document_type="ir_page",
        published_date="2026-03-31", retrieved_date=RETRIEVED,
    ),
    "brainstorm_q2_2026_release": dict(
        title="BrainStorm Cell Therapeutics Announces Second Quarter 2026 Financial Results and Provides Corporate Update",
        url="https://www.placera.se/pressmeddelanden/brainstorm-cell-therapeutics-announces-second-quarter-2026-financial-results-and-provides-corporate-update-20260814",
        publisher="Placera (press release syndication)", document_type="press_release",
        published_date="2026-08-14", retrieved_date=RETRIEVED,
    ),
    "bcli_10q_q2_2026": dict(
        title="BrainStorm Cell Therapeutics Inc. Form 10-Q, quarter ended June 30, 2026",
        url="https://www.sec.gov/Archives/edgar/data/0001137883/000110465926097275/bcli-20260630x10q.htm",
        publisher="SEC EDGAR", document_type="sec_10q",
        published_date="2026-08", retrieved_date=RETRIEVED,
    ),
    "panabee_bcli_q2_2026": dict(
        title="Brainstorm Cell Therapeutics Faces Liquidity Crisis Despite FDA Regulatory Alignment",
        url="https://www.panabee.com/news/brainstorm-cell-therapeutics-earnings-q2-2026-report",
        publisher="Panabee (third-party filings aggregator)", document_type="news",
        published_date="2026-08", retrieved_date=RETRIEVED,
    ),
    "equibles_bcli": dict(
        title="BrainStorm Cell Therapeutics (BCLI) financial summary",
        url="https://equibles.com/stocks/bcli",
        publisher="Equibles (third-party filings aggregator)", document_type="news",
        published_date="2026-08", retrieved_date=RETRIEVED,
    ),
    "patsnap_brainstorm_petition": dict(
        title="BrainStorm Seeks FDA Approval for Advanced ALS Trial",
        url="https://synapse.patsnap.com/article/brainstorm-seeks-fda-approval-for-advanced-als-trial",
        publisher="Patsnap Synapse", document_type="news",
        published_date="2025-07", retrieved_date=RETRIEVED,
    ),
    "clene_nda_filing": dict(
        title="Clene moves toward accelerated approval NDA filing for CNM-Au8 in ALS",
        url="https://www.neurologylive.com/view/clene-moves-toward-accelerated-approval-nda-filing-cnm-au8-als",
        publisher="NeurologyLive", document_type="news",
        published_date="2026-10-19", retrieved_date=RETRIEVED,
    ),
    "biospace_healey_topline": dict(
        title="Clene Reports Topline Results for CNM-Au8 in HEALEY ALS Platform Trial",
        url="https://www.biospace.com/clene-s-cnm-au8-shows-statistically-significant-difference-in-plasma-neurofilament-light-nfl-levels-in-the-healey-als-platform-trial",
        publisher="BioSpace", document_type="press_release",
        published_date="2024-03", retrieved_date=RETRIEVED,
    ),
    "biospace_healey_survival": dict(
        title="Clene Demonstrates Strengthened ALS Survival Benefit with CNM-Au8 Treatment",
        url="https://www.biospace.com/press-releases/clene-demonstrates-strengthened-als-survival-benefit-with-cnm-au8-treatment",
        publisher="BioSpace", document_type="press_release",
        published_date="2025", retrieved_date=RETRIEVED,
    ),
    "clinicaltrials_healey": dict(
        title="ClinicalTrials.gov record NCT04297683 (HEALEY ALS Platform Trial)",
        url="https://clinicaltrials.gov/study/NCT04297683",
        publisher="ClinicalTrials.gov", document_type="registry",
        published_date=None, retrieved_date=RETRIEVED,
    ),
    "clnn_10q_q2_2026": dict(
        title="Clene Inc. Form 10-Q, quarter ended June 30, 2026",
        url="https://www.sec.gov/Archives/edgar/data/0001822791/000143774926027828/clnn20260630_10q.htm",
        publisher="SEC EDGAR", document_type="sec_10q",
        published_date="2026-08-11", retrieved_date=RETRIEVED,
    ),
    "barchart_combat_als": dict(
        title="MediciNova Announces Update on Phase 2/3 Clinical Trial of MN-166 (Ibudilast) in ALS (COMBAT-ALS)",
        url="https://www.barchart.com/story/news/36503569/medicinova-announces-update-and-basic-characteristic-randomized-patients-of-phase-2-3-clinical-trial-of-mn-166-ibudilast-in-als-combat-als-clinical-trial-presented-at-the-36th-international-symposium-on-als-mnd",
        publisher="Barchart (press release syndication)", document_type="press_release",
        published_date="2025-12", retrieved_date=RETRIEVED,
    ),
    "mnov_10q_q2_2026": dict(
        title="MediciNova, Inc. Form 10-Q, quarter ended June 30, 2026",
        url="https://www.sec.gov/Archives/edgar/data/0001226616/000119312526349323/mnov-20260630.htm",
        publisher="SEC EDGAR", document_type="sec_10q",
        published_date="2026-08", retrieved_date=RETRIEVED,
    ),
    "sec_xbrl_api": dict(
        title="SEC EDGAR XBRL company facts API, CIK 0001137883 (BrainStorm Cell Therapeutics)",
        url="https://data.sec.gov/api/xbrl/companyfacts/CIK0001137883.json",
        publisher="SEC EDGAR (XBRL structured data API)", document_type="sec_xbrl_api",
        published_date=None, retrieved_date=RETRIEVED,
    ),
    "clinicaltrials_combat_als": dict(
        title="ClinicalTrials.gov record NCT04057898 (COMBAT-ALS)",
        url="https://clinicaltrials.gov/study/NCT04057898",
        publisher="ClinicalTrials.gov", document_type="registry",
        published_date="2026-03-06", retrieved_date=RETRIEVED,
    ),
}

# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------
COMPANIES = [
    dict(company_id="biogen", name="Biogen Inc.", ticker="BIIB", cik="0000875045", sector_id="biotech_als", is_publicly_traded=1,
         website="https://www.biogen.com", relationship_to_use_case="direct",
         company_notes="Large diversified biotech (multiple sclerosis, Alzheimer's, "
                        "rare disease, ALS). Qalsody/tofersen is one product among many -- "
                        "company-wide financials below are NOT ALS-program-specific burn rate; "
                        "treat the runway calculator here as illustrative of Biogen's total "
                        "business, not its ALS program alone."),
    dict(company_id="amylyx", name="Amylyx Pharmaceuticals, Inc.", ticker="AMLX", cik="0001658551", sector_id="biotech_als", is_publicly_traded=1,
         website="https://www.amylyx.com", relationship_to_use_case="direct",
         company_notes="Originally an ALS pure-play; now also developing avexitide "
                        "(hypoglycemia) and AMX0035 in other indications after Relyvrio's "
                        "ALS withdrawal. AMX0114 is the current ALS-specific candidate."),
    dict(company_id="brainstorm", name="BrainStorm Cell Therapeutics Inc.", ticker="BCLI", cik="0001137883", sector_id="biotech_als", is_publicly_traded=1,
         website="https://www.brainstorm-cell.com", relationship_to_use_case="direct",
         company_notes="ALS pure-play (autologous MSC-NTF cell therapy, NurOwn). "
                        "Shares trade on OTCQB. Going-concern doubt disclosed in 2026 filings."),
    dict(company_id="clene", name="Clene Inc.", ticker="CLNN", cik="0001822791", sector_id="biotech_als", is_publicly_traded=1,
         website="https://www.clene.com", relationship_to_use_case="direct",
         company_notes="ALS-focused (CNM-Au8), also developing the same compound in "
                        "multiple sclerosis and Parkinson's disease. Going-concern doubt "
                        "disclosed in 2026 filings; debt covenant requires minimum cash."),
    dict(company_id="medicinova", name="MediciNova, Inc.", ticker="MNOV", cik="0001226616", sector_id="biotech_als", is_publicly_traded=1,
         website="https://www.medicinova.com", relationship_to_use_case="direct",
         company_notes="Multi-indication biotech (MN-166/ibudilast is also studied in "
                        "progressive MS and other conditions); COMBAT-ALS is its lead ALS program."),
]

# ---------------------------------------------------------------------------
# Programs
# ---------------------------------------------------------------------------
PROGRAMS = [
    dict(company_id="biogen", program_name="Qalsody (tofersen)",
         mechanism="Antisense oligonucleotide reducing SOD1 protein production",
         modality="Antisense oligonucleotide (intrathecal injection)",
         target_indication="SOD1-mutation ALS (genetically defined subset)"),
    dict(company_id="amylyx", program_name="AMX0114",
         mechanism="Antisense oligonucleotide targeting calpain-2 to reduce axonal degeneration",
         modality="Antisense oligonucleotide",
         target_indication="ALS (broad, not genetically restricted in public disclosures found)"),
    dict(company_id="brainstorm", program_name="NurOwn (debamestrocel)",
         mechanism="Autologous mesenchymal stem cells induced to secrete neurotrophic factors (MSC-NTF), administered intrathecally",
         modality="Autologous cell therapy",
         target_indication="ALS"),
    dict(company_id="clene", program_name="CNM-Au8",
         mechanism="Catalytically active gold nanocrystal suspension intended to support neuronal energy metabolism and reduce oxidative stress",
         modality="Oral suspension, small molecule/nanocrystal",
         target_indication="ALS (also studied in multiple sclerosis and Parkinson's disease)"),
    dict(company_id="medicinova", program_name="MN-166 (ibudilast)",
         mechanism="Phosphodiesterase inhibitor with anti-neuroinflammatory, macrophage migration inhibitory factor (MIF)-inhibiting activity",
         modality="Oral small molecule",
         target_indication="ALS (also studied in progressive multiple sclerosis)"),
]

# ---------------------------------------------------------------------------
# Trials (10 total)
# ---------------------------------------------------------------------------
TRIALS = [
    dict(company_id="biogen", program_name="Qalsody (tofersen)", nct_id="not captured in this pass",
         trial_name="VALOR", phase="Phase 1/2/3", status="Completed (open-label extension ongoing)",
         study_design="Randomized, placebo-controlled, with open-label extension",
         population="SOD1-ALS patients", comparator="Placebo", enrollment=108,
         primary_endpoint="Change in ALSFRS-R total score at week 28",
         key_secondary_endpoints="Plasma neurofilament light chain (NfL) reduction; respiratory and muscle strength measures",
         outcome_timing="Primary analysis reported 2022", results_status="reported_mixed",
         reported_outcome="Missed the primary clinical endpoint (ALSFRS-R), but showed a reduction in "
                           "plasma NfL (a biomarker of neuronal injury); this biomarker result was the basis "
                           "for FDA accelerated approval, not a demonstrated clinical benefit on its own.",
         source_key="ionis_qalsody_approval", claim_type="independently-supported"),
    dict(company_id="biogen", program_name="Qalsody (tofersen)", nct_id="not captured in this pass",
         trial_name="ATLAS", phase="Phase 3", status="Ongoing (confirmatory trial for accelerated approval)",
         study_design="Randomized, placebo-controlled, presymptomatic initiation",
         population="~150 adults with SOD1 mutations associated with rapidly progressing ALS, "
                     "presymptomatic but with biomarker evidence of nerve damage",
         comparator="Placebo", enrollment=150,
         primary_endpoint="Not confirmed in this search pass",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Not yet reported as of 2026-10-27", results_status="planned_not_reported",
         reported_outcome="This is the confirmatory trial the FDA required for Qalsody's continued "
                           "accelerated approval. No results found in this search pass.",
         source_key="als_today_qalsody", claim_type="company-reported"),
    dict(company_id="amylyx", program_name="AMX0035 (Relyvrio, discontinued)", nct_id="not captured in this pass",
         trial_name="CENTAUR", phase="Phase 2", status="Completed",
         study_design="Randomized, placebo-controlled",
         population="ALS patients", comparator="Placebo", enrollment=137,
         primary_endpoint="Change in ALSFRS-R total score over 24 weeks",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Reported 2020", results_status="reported_positive",
         reported_outcome="Met its primary endpoint; this Phase 2 result was the basis for the original "
                           "2022 FDA approval of Relyvrio, later withdrawn (see PHOENIX below).",
         source_key="als_today_phoenix_fail", claim_type="independently-supported"),
    dict(company_id="amylyx", program_name="AMX0035 (Relyvrio, discontinued)", nct_id="not captured in this pass",
         trial_name="PHOENIX", phase="Phase 3", status="Completed -- confirmatory trial failed",
         study_design="Randomized, placebo-controlled confirmatory trial",
         population="ALS patients", comparator="Placebo", enrollment=664,
         primary_endpoint="48-week change on the revised ALS Functional Rating Scale (ALSFRS-R)",
         key_secondary_endpoints="Multiple functional/survival secondary endpoints (none met)",
         outcome_timing="Reported March 2024", results_status="reported_negative",
         reported_outcome="Missed the primary endpoint and all secondary endpoints. This confirmatory "
                           "failure directly led Amylyx to voluntarily withdraw Relyvrio from the US "
                           "and Canadian markets in April 2024 -- the clearest example in this dataset "
                           "of why a prior approval does not guarantee durable evidence.",
         source_key="biospace_amylyx_pull", claim_type="independently-supported"),
    dict(company_id="amylyx", program_name="AMX0114", nct_id="not captured in this pass",
         trial_name="LUMINA", phase="Phase 1", status="Ongoing",
         study_design="Not confirmed in this search pass",
         population="ALS patients", comparator="Not confirmed in this search pass", enrollment=None,
         primary_endpoint="Not confirmed in this search pass (early-phase, likely safety/tolerability)",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Not yet reported", results_status="planned_not_reported",
         reported_outcome="Early-stage program; no efficacy data expected yet at Phase 1.",
         source_key="amlx_10q_q2_2026", claim_type="company-reported"),
    dict(company_id="brainstorm", program_name="NurOwn (debamestrocel)", nct_id="not captured in this pass",
         trial_name="Phase 3 NurOwn trial (2020)", phase="Phase 3", status="Completed -- missed primary endpoint",
         study_design="Randomized, placebo-controlled", population="ALS patients (mild-to-moderate)",
         comparator="Placebo", enrollment=None,
         primary_endpoint="Proportion of ALSFRS-R responders at 28 weeks",
         key_secondary_endpoints="ALS severity measures (met after a post-hoc statistical correction, per company)",
         outcome_timing="Topline reported November 2020", results_status="reported_negative",
         reported_outcome="Missed its primary endpoint. BrainStorm later identified and corrected a "
                           "statistical error, after which a secondary endpoint was reported as met -- "
                           "but the FDA still declined to accept the resulting BLA (refuse-to-file, "
                           "November 2022), and a March 2023 advisory committee voted 17-1 against "
                           "NurOwn's efficacy for mild-to-moderate ALS.",
         source_key="geneonline_brainstorm_rtf", claim_type="independently-supported"),
    dict(company_id="brainstorm", program_name="NurOwn (debamestrocel)", nct_id="not captured in this pass",
         trial_name="ENDURANCE (Phase 3b)", phase="Phase 3b", status="Not yet started -- pending funding",
         study_design="Special Protocol Assessment (SPA)-agreed design: 24-week placebo-controlled "
                       "portion plus 24-week open-label extension",
         population="~200 ALS patients at leading ALS centers", comparator="Placebo", enrollment=200,
         primary_endpoint="Not confirmed in this search pass",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Not started as of 2026-10-27 (company states it is still preparing to begin)",
         results_status="not_yet_started",
         reported_outcome="FDA cleared this trial design under an SPA in May 2025, following a 2025 "
                           "citizen petition asking the FDA to reconsider NurOwn. As of BrainStorm's "
                           "August 2026 release, the trial has not begun -- it is still pending financing.",
         source_key="ctarena_brainstorm_spa", claim_type="company-reported"),
    dict(company_id="clene", program_name="CNM-Au8", nct_id="NCT04297683",
         trial_name="HEALEY ALS Platform Trial (CNM-Au8 regimen)", phase="Phase 2/3",
         status="Completed enrollment for this regimen; platform trial overall still recruiting other arms",
         study_design="Multi-arm, multi-sponsor platform trial with a shared placebo group; "
                       "161 participants randomized to 30mg CNM-Au8, 60mg CNM-Au8, or placebo for 24 weeks",
         population="ALS patients", comparator="Shared placebo arm", enrollment=161,
         primary_endpoint="Slope of change in ALSFRS-R score (mortality-adjusted) at 24 weeks",
         key_secondary_endpoints="Combined Assessment of Function and Survival (CAFS); "
                                  "slow vital capacity (SVC)",
         outcome_timing="Topline reported 2024; post-hoc survival analysis reported 2025",
         results_status="reported_mixed",
         reported_outcome="Primary endpoint NOT statistically significant at 24 weeks; CAFS and SVC "
                           "secondary endpoints also NOT met at 24 weeks. A separate, POST-HOC long-term "
                           "survival analysis (not a pre-registered endpoint) reported a 49% decreased "
                           "risk of death versus PRO-ACT historical controls -- a materially weaker form "
                           "of evidence than a randomized, concurrent comparison. This mixed result is the "
                           "basis of Clene's 2026 accelerated-approval NDA filing, which relies on a "
                           "neurofilament light chain (NfL) biomarker as a surrogate endpoint; the FDA's "
                           "own language on whether NfL can support that pathway here is tentative "
                           "('may be capable of supporting' / 'could potentially serve').",
         source_key="biospace_healey_topline", claim_type="independently-supported"),
    dict(company_id="clene", program_name="CNM-Au8", nct_id="not registered as of this search pass",
         trial_name="RESTORE-ALS (planned Phase 3 confirmatory trial)", phase="Phase 3",
         status="Planned, not yet started",
         study_design="Double-blind, placebo-controlled; intended to assess survival and clinical "
                       "worsening events", population="ALS patients", comparator="Placebo", enrollment=None,
         primary_endpoint="Not confirmed in this search pass",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Company guidance (Q1 2026 update) targets start in Q1 2027",
         results_status="not_yet_started",
         reported_outcome="Planned confirmatory trial for the accelerated-approval pathway, contingent "
                           "on the NDA submitted October 2026; not yet begun.",
         source_key="clene_nda_filing", claim_type="company-reported"),
    dict(company_id="medicinova", program_name="MN-166 (ibudilast)", nct_id="NCT04057898",
         trial_name="COMBAT-ALS", phase="Phase 2/3", status="Active, not recruiting (fully enrolled)",
         study_design="Randomized, double-blind, placebo-controlled 12-month treatment period "
                       "followed by a 6-month open-label extension",
         population="ALS patients at US and Canadian sites", comparator="Placebo", enrollment=234,
         primary_endpoint="Not confirmed in this search pass (registry record exists but exact endpoint text not captured)",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Topline data expected by end of 2026 per company guidance",
         results_status="planned_not_reported",
         reported_outcome="Enrollment completed September 2025 (234 patients). No results reported yet; "
                           "this is a live, near-term catalyst that could materially change this company's "
                           "evidence assessment within the life of this project.",
         source_key="clinicaltrials_combat_als", claim_type="registry-entry"),
]

# ---------------------------------------------------------------------------
# Financial periods -- all as of the most recent filed 10-Q at research time
# (quarter ended 2026-06-30 for all five companies)
# ---------------------------------------------------------------------------
FINANCIAL_PERIODS = [
    dict(company_id="biogen", period_end_date="2026-06-30", filing_date="2026-08", period_type="10-Q",
         currency_units="USD millions",
         cash_and_equivalents=1285.0, marketable_securities=0.0, total_debt=None,
         revenue=2736.0, rd_expense=529.6, operating_cash_flow=None, shares_outstanding=148.7,
         going_concern_flag=0, source_key="biib_10q_q2_2026",
         note="Marketable securities shown as $0 at 6/30/2026 vs. $807.2M (current) + $431.9M "
              "(non-current) at 12/31/2025 per the filing -- a large apparent drawdown worth "
              "verifying directly rather than assuming a data error. Figures are company-wide, "
              "not ALS-program-specific (see company_notes). KNOWN ADAPTER LIMITATION: querying "
              "SEC EDGAR's live XBRL company-facts API for Biogen currently resolves only through "
              "Q1 2026 (3/31/2026), one quarter behind this manually-read Q2 2026 10-Q -- most "
              "likely because Biogen's Q2 filing reports this concept with a dimensional/member "
              "qualifier the API's top-level (non-dimensional) fact list doesn't surface, though this "
              "wasn't root-caused further. This is exactly the kind of staleness the refresh script "
              "is built to flag rather than hide: see scripts/refresh_live_data.py and the "
              "'last refreshed' banner on the Home page."),
    dict(company_id="amylyx", period_end_date="2026-06-30", filing_date="2026-08", period_type="10-Q",
         currency_units="USD millions",
         cash_and_equivalents=49.326, marketable_securities=201.434, total_debt=None,
         revenue=0.0, rd_expense=23.768, operating_cash_flow=-36.882, shares_outstanding=111.368283,
         going_concern_flag=0, source_key="amlx_10q_q2_2026",
         note="The 10-Q text (read directly) reported cash, cash equivalents AND marketable securities "
              "combined as $250.8M, not broken out. The live SEC EDGAR XBRL company-facts API supplied "
              "the split used here: cash_and_equivalents $49.326M + marketable_securities $201.434M = "
              "$250.76M, which reconciles with the combined figure (within rounding). Company states "
              "this funds operations into 2028. R&D figure is Q2-only ($23.768M, confirmed by both "
              "sources); six-month R&D was $51.4M. Revenue and operating cash flow are from the live "
              "XBRL feed (not independently read from the 10-Q text in this pass)."),
    dict(company_id="brainstorm", period_end_date="2026-06-30", filing_date="2026-08", period_type="10-Q",
         currency_units="USD millions",
         cash_and_equivalents=0.022, marketable_securities=0.196, total_debt=None,
         revenue=None, rd_expense=0.963, operating_cash_flow=-0.895, shares_outstanding=11.034775,
         going_concern_flag=1, source_key="sec_xbrl_api",
         note="RESOLVED DISCREPANCY: two secondary aggregators disagreed on BrainStorm's 6/30/2026 "
              "cash balance when this dataset was first built (Panabee reported ~$209,000; Equibles "
              "reported ~$29,000). Querying SEC EDGAR's XBRL company-facts API directly (the primary "
              "source, not an aggregator) resolved it: cash and cash equivalents were $22,000 -- "
              "neither aggregator figure was correct. This is a genuinely severe liquidity position "
              "(current liabilities were separately reported around $12.4M), not a units error. "
              "Lesson encoded in this app's architecture: prefer the live SEC adapter over any "
              "secondary aggregator when the two disagree."),
    dict(company_id="clene", period_end_date="2026-06-30", filing_date="2026-08-11", period_type="10-Q",
         currency_units="USD millions",
         cash_and_equivalents=9.671, marketable_securities=0.0, total_debt=17.604,
         revenue=0.09, rd_expense=3.471, operating_cash_flow=-4.528, shares_outstanding=12.778307,
         going_concern_flag=1, source_key="clnn_10q_q2_2026",
         note="Cash/debt/share-count directly verified from the filed 10-Q text (fetched 2026-10-27); "
              "marketable_securities/revenue/rd_expense/operating_cash_flow cross-checked against the "
              "live SEC EDGAR XBRL company-facts API (data_quality note: total_debt differs slightly "
              "between the two reads -- $47.8M total liabilities read from the filing's balance sheet "
              "vs. $17.6M under the XBRL 'LongTermDebtNoncurrent' tag specifically; the $47.8M is total "
              "liabilities, not debt alone, so these are not actually in conflict, but don't casually "
              "swap one for the other). Total liabilities ($47.8M) exceed total assets ($23.0M); total "
              "stockholders' deficit widened from -$17.6M (12/31/2025) to -$24.8M (6/30/2026) despite a "
              "capital raise that increased shares outstanding from ~10.85M to ~12.78M and cash from "
              "$5.2M to $9.7M over the same six months. A 2024 note covenant requires at least $2.0M "
              "unrestricted cash on hand. Filing states going-concern doubt and that cash will not last "
              "12 months without additional financing."),
    dict(company_id="medicinova", period_end_date="2026-06-30", filing_date="2026-08", period_type="10-Q",
         currency_units="USD millions",
         cash_and_equivalents=25.416, marketable_securities=39.982, total_debt=0.0,
         revenue=0.458, rd_expense=1.029, operating_cash_flow=-3.470, shares_outstanding=49.221246,
         going_concern_flag=0, source_key="mnov_10q_q2_2026",
         note="Cash/R&D/share-count directly verified from the filed 10-Q text (fetched 2026-10-27); "
              "marketable_securities/revenue/operating_cash_flow cross-checked against the live SEC "
              "EDGAR XBRL company-facts API, which also independently confirmed the R&D figure "
              "($1.029M for the quarter) and share count exactly. Company states cash plus marketable "
              "securities ($25.4M + $40.0M = ~$65.4M total liquidity) is sufficient for at least the "
              "next 12 months. R&D expense line is labeled 'research, development and patents' in the "
              "filing (a combined line item) -- notably lower than peers running comparably sized "
              "trials, which is itself worth asking about directly in diligence rather than assuming "
              "either under- or over-investment."),
]

# ---------------------------------------------------------------------------
# Uncertainties (scientific / operational / commercial), one set per company
# ---------------------------------------------------------------------------
UNCERTAINTIES = [
    dict(company_id="biogen", category="scientific",
         description="Qalsody's accelerated approval rests on a neurofilament light chain (NfL) "
                      "biomarker reduction, not a demonstrated clinical benefit in VALOR (which missed "
                      "its primary clinical endpoint); the confirmatory ATLAS trial's result is still pending."),
    dict(company_id="biogen", category="operational",
         description="ALS is a small part of a large, diversified pipeline; company-wide R&D and cash "
                      "figures mix many unrelated programs, so they say little about commitment or "
                      "constraint specific to the ALS franchise."),
    dict(company_id="biogen", category="commercial",
         description="Qalsody addresses only the SOD1-mutation subset of ALS (a small fraction of all "
                      "ALS patients), which caps its addressable population regardless of trial outcomes."),
    dict(company_id="amylyx", category="scientific",
         description="The PHOENIX confirmatory trial failure directly contradicts the earlier positive "
                      "CENTAUR Phase 2 result; this is a documented case of initial efficacy signal not "
                      "replicating in a larger trial, not merely regulatory caution."),
    dict(company_id="amylyx", category="operational",
         description="Company underwent a ~70% workforce reduction following Relyvrio's withdrawal; "
                      "AMX0114 is only in Phase 1, years from any approval decision."),
    dict(company_id="amylyx", category="commercial",
         description="No ALS product on the market as of this research pass; current ALS-specific "
                      "revenue is not disclosed/found and likely minimal or zero."),
    dict(company_id="brainstorm", category="scientific",
         description="Original Phase 3 missed its primary endpoint; a secondary-endpoint finding "
                      "(after a post-hoc statistical correction) was not sufficient for an FDA advisory "
                      "committee, which voted 17-1 against efficacy in 2023."),
    dict(company_id="brainstorm", category="operational",
         description="Going-concern doubt disclosed; the SPA-agreed Phase 3b (ENDURANCE) trial has not "
                      "started and is explicitly described by the company as pending financing."),
    dict(company_id="brainstorm", category="commercial",
         description="No approved product; trades on OTCQB (not a major exchange), which typically "
                      "signals reduced institutional investor access and liquidity."),
    dict(company_id="clene", category="scientific",
         description="The HEALEY trial's primary and secondary endpoints were not met; the survival "
                      "benefit cited in the NDA is a post-hoc comparison to historical (not concurrent, "
                      "not randomized) controls, a materially weaker evidence standard."),
    dict(company_id="clene", category="operational",
         description="Going-concern doubt disclosed; a debt covenant requires maintaining at least $2.0M "
                      "unrestricted cash, and total liabilities already exceed total assets."),
    dict(company_id="clene", category="commercial",
         description="An accelerated approval, if granted, would still require a confirmatory Phase 3 "
                      "(RESTORE-ALS) that has not started; FDA's own description of whether the NfL "
                      "biomarker can support this specific approval is tentative, not settled."),
    dict(company_id="medicinova", category="scientific",
         description="COMBAT-ALS has not yet reported results; MN-166's mechanism (anti-neuroinflammatory) "
                      "has not previously yielded an approved ALS therapy in this or related programs."),
    dict(company_id="medicinova", category="operational",
         description="R&D expense for the ALS program appears low relative to peers running similarly "
                      "sized trials, which was not explained in sources found in this pass -- worth "
                      "asking directly rather than assuming under- or over-investment."),
    dict(company_id="medicinova", category="commercial",
         description="No approved ALS product; MN-166 is also being developed for other indications, "
                      "so a negative COMBAT-ALS readout would not necessarily end the company's broader pipeline."),
]

# ---------------------------------------------------------------------------
# Neurotechnology (BCI) sector data
# Originally built as the standalone NeuroScope project (research pass
# 2026-10-23); merged here with sector_id="neurotech_bci". See the module
# docstring for why this sector uses `funding_rounds` instead of
# `financial_periods` -- these companies are almost all privately held.
# ---------------------------------------------------------------------------

SOURCE_DOCUMENTS.update({
    "nt_neuralink_breakthrough": dict(
        title="Neuralink wins FDA breakthrough tag for speech restoration",
        url="https://finance.yahoo.com/news/neuralink-wins-fda-breakthrough-tag-163317403.html",
        publisher="Yahoo Finance", document_type="news",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_neuralink_trials_2026": dict(
        title="Neuralink Human Trials 2026: Patient Progress, Telepathy App, and Blindsight Approval",
        url="https://press.farm/neuralink-human-trials-2026-patient-progress-telepathy-app/",
        publisher="Press Farm", document_type="news",
        published_date="2026", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_neuralink_funding_tracker": dict(
        title="Brain-Computer Interface Funding Tracker (72 deals)",
        url="https://newmarketpitch.com/blogs/news/brain-computer-interface-list-deals",
        publisher="NewMarketPitch (funding tracker)", document_type="funding_tracker",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_neuralink_registry": dict(
        title="ClinicalTrials.gov record NCT06429735 (PRIME Study)",
        url="https://clinicaltrials.gov/study/NCT06429735",
        publisher="ClinicalTrials.gov API v2", document_type="registry_api",
        published_date=None, retrieved_date=RETRIEVED,
    ),
    "nt_synchron_pivotal": dict(
        title="Synchron Brain Implant Targets 2026 Pivotal Trial for First FDA-Approved BCI",
        url="https://www.techtimes.com/articles/317929/20260606/synchron-brain-implant-targets-2026-pivotal-trial-first-fda-approved-bci.htm",
        publisher="Tech Times", document_type="news",
        published_date="2026-06-06", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_synchron_command_results": dict(
        title="Synchron Announces Positive Results from U.S. COMMAND Study of Endovascular Brain-Computer Interface",
        url="https://www.biospace.com/news/synchron-announces-positive-results-from-u-s-command-study-of-endovascular-brain-computer-interface",
        publisher="BioSpace", document_type="press_release",
        published_date="2026", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_synchron_funding": dict(
        title="Top 5 Brain-Computer Interface Companies to Watch in 2026",
        url="https://www.digitaljournal.com/pr/news/winston-news-wire/top-5-brain-computer-interface-companies-1365510538.html",
        publisher="Digital Journal", document_type="news",
        published_date="2026", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_synchron_registry": dict(
        title="ClinicalTrials.gov record NCT05035823 (COMMAND Early Feasibility Study)",
        url="https://clinicaltrials.gov/study/NCT05035823",
        publisher="ClinicalTrials.gov API v2", document_type="registry_api",
        published_date=None, retrieved_date=RETRIEVED,
    ),
    "nt_blackrock_tech": dict(
        title="Blackrock Neurotech -- Our Tech",
        url="https://blackrockneurotech.com/our-tech/",
        publisher="Blackrock Neurotech (company site)", document_type="company_site",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_blackrock_funding": dict(
        title="Blackrock Neurotech News, Articles and Coverage",
        url="https://aventure.vc/companies/blackrock-neurotech-salt-lake-city-ut-us/news",
        publisher="aVenture (funding tracker)", document_type="funding_tracker",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_precision_cleared": dict(
        title="Precision Neuroscience wins FDA clearance for BCI cortical interface",
        url="https://www.medtechdive.com/news/precision-neuroscience-brain-implant-fda-cleared/745913/",
        publisher="MedTech Dive", document_type="news",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_precision_clearance_detail": dict(
        title="Precision Neuroscience Receives FDA Clearance for High-Resolution Cortical Electrode Array",
        url="https://www.precisionneuro.io/articles/company-news/precision-neuroscience-receives-fda-clearance-for-high-resolution-cortical-electrode-array",
        publisher="Precision Neuroscience (company site)", document_type="press_release",
        published_date="2025-04-17", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_precision_funding": dict(
        title="Precision Neuroscience raises $250M for brain-computer interface",
        url="https://www.mobihealthnews.com/news/precision-neuroscience-raises-250m-brain-computer-interface",
        publisher="MobiHealthNews", document_type="news",
        published_date="2026-09", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_paradromics_funding": dict(
        title="Paradromics Raises $33 Million in Funding, Achieves Breakthrough Medical Device Designation from FDA",
        url="https://paradromics.com/news/paradromics-raises-33-million-in-funding-achieves-breakthrough-medical-device-designation-from-fda/",
        publisher="Paradromics (company site)", document_type="press_release",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_paradromics_speech": dict(
        title="Paradromics Achieves Real-Time Speech with Connexus Brain-Computer Interface",
        url="https://www.businesswire.com/news/home/20260914434545/en/Paradromics-Achieves-Real-Time-Speech-with-Connexus-Brain-Computer-Interface",
        publisher="Business Wire", document_type="press_release",
        published_date="2026-09-14", retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_paradromics_registry": dict(
        title="ClinicalTrials.gov record NCT07357428 (Connect-One Early Feasibility Study)",
        url="https://clinicaltrials.gov/study/NCT07357428",
        publisher="ClinicalTrials.gov API v2", document_type="registry_api",
        published_date="2026-04-14", retrieved_date=RETRIEVED,
    ),
    "nt_cognixion_als_news": dict(
        title="ALS News Today Spotlights Cognixion's Clinical Trial for Non-Invasive BCI Headset",
        url="https://www.cognixion.com/blog/alsnews",
        publisher="Cognixion (company site)", document_type="company_site",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_cognixion_site": dict(
        title="Cognixion",
        url="https://www.cognixion.com/",
        publisher="Cognixion (company site)", document_type="company_site",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_cognixion_registry": dict(
        title="ClinicalTrials.gov record NCT07871071 (BCI Communication Device for ALS)",
        url="https://clinicaltrials.gov/study/NCT07871071",
        publisher="ClinicalTrials.gov API v2", document_type="registry_api",
        published_date=None, retrieved_date=RETRIEVED,
    ),
    "nt_onward_breakthrough": dict(
        title="ONWARD Medical Awarded 10th Breakthrough Device Designation for Brain-Computer Interface (BCI) from US FDA",
        url="https://www.biospace.com/onward-medical-awarded-10th-breakthrough-device-designation-for-brain-computer-interface-bci-from-us-fda-award-gives-priority-us-regulatory-review-to-company-s-arc-bci-system",
        publisher="BioSpace", document_type="press_release",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
    "nt_onward_site": dict(
        title="ONWARD Medical -- Brain-Computer Interface",
        url="https://www.onwd.com/brain-computer-interface/",
        publisher="ONWARD Medical (company site)", document_type="company_site",
        published_date=None, retrieved_date=RETRIEVED_NEUROTECH,
    ),
})

COMPANIES += [
    dict(company_id="neuralink", name="Neuralink", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=0,
         website="https://neuralink.com", relationship_to_use_case="direct",
         company_notes="Privately held. N1 Implant / R1 Robot. FDA Breakthrough Device "
                        "Designation (speech restoration application); PRIME early feasibility "
                        "study operating under FDA IDE clearance; not approved for commercial sale. "
                        "No public pricing or reimbursement model disclosed."),
    dict(company_id="synchron", name="Synchron", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=0,
         website="https://synchron.com", relationship_to_use_case="direct",
         company_notes="Privately held. Stentrode / Home Edition. FDA Breakthrough Device "
                        "Designation (granted Aug 2020); FDA IDE approval for COMMAND study; "
                        "pivotal trial for potential PMA not yet completed as of original research "
                        "pass. A secondary source used the non-standard phrase 'conditional market "
                        "authorization' for the Home Edition -- flagged as unverified."),
    dict(company_id="blackrock", name="Blackrock Neurotech", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=0,
         website="https://blackrockneurotech.com", relationship_to_use_case="direct",
         company_notes="Privately held. MoveAgain BCI System. FDA Breakthrough Device Designation "
                        "(granted 2021); not yet commercially approved. Longest-running research "
                        "platform (cumulative implants reported in 40+ individuals across many "
                        "separate academic studies, not one controlled trial); no public pricing model."),
    dict(company_id="precision", name="Precision Neuroscience", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=0,
         website="https://precisionneuro.io", relationship_to_use_case="direct",
         company_notes="Privately held. Layer 7 Cortical Interface. FDA 510(k) clearance (clearance, "
                        "not full PMA approval; scope limited to temporary use up to 30 days). "
                        "Raised $250M Series D (Sept 2026), $430M total raised; no public pricing "
                        "or reimbursement model for a chronic product yet."),
    dict(company_id="paradromics", name="Paradromics", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=0,
         website="https://paradromics.com", relationship_to_use_case="direct",
         company_notes="Privately held. Connexus BCI. FDA Breakthrough Device Designation x2 "
                        "(speech restoration; computer control expanded Aug 2026); FDA IDE granted "
                        "Nov 2025; not approved for commercial sale. Earlier $33M Series A disclosed "
                        "alongside first breakthrough designation; current total funding not "
                        "reconciled in original research pass."),
    dict(company_id="cognixion", name="Cognixion", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=0,
         website="https://www.cognixion.com", relationship_to_use_case="direct",
         company_notes="Privately held. Cognixion ONE (Axon system), non-invasive scalp EEG plus "
                        "AR display. FDA Breakthrough Device Designation granted; not yet cleared/ "
                        "approved as a standalone commercial medical device for this use. Depends on "
                        "third-party AR hardware (Apple Vision Pro or XReal glasses)."),
    dict(company_id="onward", name="ONWARD Medical", ticker=None, cik=None,
         sector_id="neurotech_bci", is_publicly_traded=1,
         website="https://www.onwd.com", relationship_to_use_case="adjacent",
         company_notes="Publicly listed on Euronext (ticker and financials NOT independently "
                        "verified in this project's research pass -- Euronext filings are outside "
                        "the SEC EDGAR adapter's coverage, so this company has no financial_periods "
                        "rows here despite being public). ARC-BCI System paired with ARC-IM spinal "
                        "cord stimulation therapy -- restores limb movement after spinal cord injury, "
                        "NOT primarily assistive communication or computer control, which is why this "
                        "company is adjacent rather than direct for the neurotech sector's primary "
                        "use case. FDA Breakthrough Device Designation (10th awarded to ONWARD)."),
]

PROGRAMS += [
    dict(company_id="neuralink", program_name="N1 Implant / R1 Robot",
         mechanism="Intracortical microelectrode threads record single/multi-unit spike activity, "
                    "surgically placed by a purpose-built robot",
         modality="Invasive -- intracortical microelectrode threads",
         target_indication="Computer cursor and typing control; speech restoration for adults with "
                            "tetraplegia/tetraparesis (severe paralysis)"),
    dict(company_id="synchron", program_name="Stentrode / Home Edition",
         mechanism="Endovascular (stent-based) electrode array delivered via blood vessel, records "
                    "local field potentials from inside a vessel adjacent to motor cortex -- no open "
                    "brain surgery required",
         modality="Invasive -- endovascular stent-based array",
         target_indication="Computer/tablet/smart-home control via imagined movement for adults with "
                            "severe bilateral upper-limb paralysis"),
    dict(company_id="blackrock", program_name="MoveAgain BCI System",
         mechanism="Intracortical microelectrode array (Utah Array lineage) records spike activity",
         modality="Invasive -- intracortical microelectrode array",
         target_indication="Cursor/keyboard/wheelchair/prosthetic control via thought for adults "
                            "with paralysis from multiple etiologies"),
    dict(company_id="precision", program_name="Layer 7 Cortical Interface",
         mechanism="Thin-film surface (epicortical) electrode array conforms to the brain's surface "
                    "without penetrating tissue; 1024 microelectrodes record ECoG-like surface "
                    "potentials",
         modality="Invasive but non-penetrating -- thin-film surface array",
         target_indication="Measurement and stimulation of cortical activity; positioning toward "
                            "computer-control use cases; tested mainly in neurosurgical patients "
                            "undergoing unrelated procedures, not yet a chronic assistive-use population"),
    dict(company_id="paradromics", program_name="Connexus BCI",
         mechanism="High-channel-count intracortical microelectrode array records high-bandwidth "
                    "spike activity",
         modality="Invasive -- high-channel-count intracortical array",
         target_indication="Speech restoration and computer device control for adults with severe "
                            "motor deficits / speech impairment"),
    dict(company_id="cognixion", program_name="Cognixion ONE (Axon system)",
         mechanism="Medical-grade scalp EEG sensing assembly paired with an augmented-reality display "
                    "(Apple Vision Pro, XReal glasses, or external screen) and an AI-assisted "
                    "communication application",
         modality="Non-invasive -- scalp EEG plus AR display",
         target_indication="Assistive communication (typing/speaking) for adults with ALS and other "
                            "severe speech/motor impairment, positioned as an alternative/supplement "
                            "to eye-tracking AAC devices"),
    dict(company_id="onward", program_name="ARC-BCI System (paired with ARC-IM Therapy)",
         mechanism="Implanted BCI decodes cortical signals indicating movement intent; an AI model "
                    "translates those signals into stimulation instructions for an implanted spinal "
                    "cord stimulator (ARC-IM)",
         modality="Invasive -- cortical signal decoding paired with implanted spinal cord stimulator",
         target_indication="Restoring limb movement after spinal cord injury via spinal cord "
                            "stimulation (NOT assistive communication or direct computer control)"),
]

TRIALS += [
    dict(company_id="neuralink", program_name="N1 Implant / R1 Robot", nct_id="NCT06429735",
         trial_name="PRIME Study", phase="Early feasibility study",
         status="Recruiting (verified live via ClinicalTrials.gov API, 2026-10-27)",
         study_design="Open-label, unblinded, single-arm early feasibility study",
         population="Adults with tetraplegia/tetraparesis (severe paralysis)", comparator="None (single-arm)",
         enrollment="21 (as of Jan 2026, per company statements)",
         primary_endpoint="Device safety and functionality (not a registered efficacy endpoint in "
                           "sources found)",
         key_secondary_endpoints="Cursor/typing performance (bits per second)",
         outcome_timing="Ongoing; interim updates reported through October 2026",
         results_status="reported_mixed",
         reported_outcome="Zero serious device-related adverse events reported as of Jan 2026; "
                           "median ~10 bits/second on a company-run cursor task, record of 11.32 "
                           "bits/second. These are company-reported interim figures from an ongoing "
                           "early feasibility study, not a completed, independently-reviewed trial result.",
         source_document_id=None, source_key="nt_neuralink_trials_2026", claim_type="company-reported"),
    dict(company_id="synchron", program_name="Stentrode / Home Edition", nct_id="NCT05035823",
         trial_name="COMMAND Study", phase="Early feasibility study",
         status="Active, not recruiting (verified live via ClinicalTrials.gov API, 2026-10-27)",
         study_design="FDA-approved IDE early feasibility study, single-arm, 3 US sites, NIH BRAIN "
                       "Initiative-supported",
         population="Adults with severe bilateral upper-limb paralysis", comparator="None (single-arm)",
         enrollment="6",
         primary_endpoint="No device-related serious adverse events causing death or permanent "
                           "increased disability over a 1-year post-implant period",
         key_secondary_endpoints="Conversion of motor-intent brain signals into digital outputs",
         outcome_timing="12-month results reported", results_status="reported_positive",
         reported_outcome="All 6 participants met the primary safety endpoint; brain signals related "
                           "to motor intent were consistently captured and converted into digital "
                           "outputs, enabling participants to perform digital tasks. This was a "
                           "safety-focused early feasibility study, not an efficacy trial.",
         source_document_id=None, source_key="nt_synchron_command_results", claim_type="company-reported"),
    dict(company_id="blackrock", program_name="MoveAgain BCI System", nct_id="multiple (not consolidated in this pass)",
         trial_name="Cumulative research use (multiple independent academic studies, e.g. BrainGate consortium)",
         phase="Not a single trial -- aggregated across many academic protocols",
         status="Ongoing (research use)",
         study_design="Aggregated across many independent academic research protocols over ~15+ years",
         population="Adults with paralysis from multiple etiologies", comparator="Varies by individual academic study",
         enrollment="40+ individuals cumulative (company-stated aggregate, not one cohort)",
         primary_endpoint="Varies by individual academic study (not a single registered endpoint)",
         key_secondary_endpoints="Not applicable -- no single trial design",
         outcome_timing="Ongoing across many studies since ~2011", results_status="reported_mixed",
         reported_outcome="Device enables cursor, keyboard, wheelchair, and prosthetic control via "
                           "decoded intracortical signals across many published academic studies; "
                           "outcomes are not uniform across these studies and are not directly comparable.",
         source_document_id=None, source_key="nt_blackrock_tech", claim_type="company-reported"),
    dict(company_id="precision", program_name="Layer 7 Cortical Interface", nct_id="not found in this search pass",
         trial_name="Temporary intraoperative/short-term research implants",
         phase="Short-term (up to 30-day) recording", status="Completed (multiple research partnerships)",
         study_design="Short-term recording during research partnerships, largely in patients "
                       "already undergoing neurosurgery for unrelated reasons",
         population="Neurosurgical patients undergoing unrelated procedures, not a chronic "
                     "assistive-use population", comparator="None (observational)",
         enrollment="37",
         primary_endpoint="Device safety and recording/stimulation functionality during temporary use",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Reported through April 2025", results_status="reported_positive",
         reported_outcome="Device temporarily implanted and used for cortical recording/stimulation; "
                           "FDA 510(k) clearance covers this temporary use, not chronic assistive use. "
                           "Positive result is specific to the narrow temporary-use claim, not to "
                           "chronic assistive communication.",
         source_document_id=None, source_key="nt_precision_clearance_detail", claim_type="company-reported"),
    dict(company_id="paradromics", program_name="Connexus BCI", nct_id="NCT07357428",
         trial_name="Connect-One Study", phase="Early feasibility study",
         status="Recruiting (verified live via ClinicalTrials.gov API, 2026-10-27)",
         study_design="Early feasibility study; first-in-human; multi-site (incl. University of Michigan)",
         population="Adults with severe motor deficits / speech impairment", comparator="None (single-arm)",
         enrollment="Not disclosed beyond 'first implant' in original research pass",
         primary_endpoint="Preliminary device safety information",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="First human implant completed; 6-year follow-up planned per participant",
         results_status="reported_mixed",
         reported_outcome="Company reports 'real-time speech' achieved via Connexus BCI (Sept 2026 "
                           "press release); independent peer-reviewed confirmation not yet found. "
                           "Treat this as a company-reported claim, not an independently verified result.",
         source_document_id=None, source_key="nt_paradromics_speech", claim_type="company-reported"),
    dict(company_id="cognixion", program_name="Cognixion ONE (Axon system)", nct_id="NCT07871071",
         trial_name="Cognixion ONE vs. eye-tracking AAC comparison study", phase="Clinical comparison study",
         status="Recruiting (verified live via ClinicalTrials.gov API, 2026-10-27)",
         study_design="Clinical trial comparing wearable EEG-based BCI communication device against "
                       "existing eye-tracking speech-generating devices",
         population="Adults with ALS and other severe speech/motor impairment, including some with "
                     "limited eye-movement control", comparator="Existing eye-tracking AAC devices",
         enrollment="Not disclosed in this search pass",
         primary_endpoint="Comparative communication performance vs. eye-tracking AAC devices",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Ongoing; results not yet reported", results_status="planned_not_reported",
         reported_outcome="Study designed to evaluate whether a non-eye-movement-dependent BCI input "
                           "can serve ALS patients as eye-tracking performance declines; results not "
                           "yet reported in sources found.",
         source_document_id=None, source_key="nt_cognixion_als_news", claim_type="company-reported"),
    dict(company_id="onward", program_name="ARC-BCI System (paired with ARC-IM Therapy)",
         nct_id="not found in this search pass",
         trial_name="ARC-BCI investigational use (paired with ARC-IM Therapy)",
         phase="Investigational, case-level reporting", status="Investigational",
         study_design="Case-level reporting found in original research pass",
         population="Adults with paralysis from spinal cord injury", comparator="None (case report)",
         enrollment="At least 1 individual reported",
         primary_endpoint="Not confirmed in this search pass",
         key_secondary_endpoints="Not confirmed in this search pass",
         outcome_timing="Not confirmed in this search pass", results_status="reported_mixed",
         reported_outcome="One individual reported gaining augmented voluntary control over paralyzed "
                           "leg movement timing when BCI decoding was paired with spinal cord "
                           "stimulation. This is a single case report, not a controlled trial result.",
         source_document_id=None, source_key="nt_onward_site", claim_type="company-reported"),
]

# ---------------------------------------------------------------------------
# Funding rounds (neurotech sector -- mostly privately held companies, so
# venture funding disclosures substitute for financial_periods)
# ---------------------------------------------------------------------------
FUNDING_ROUNDS = [
    dict(company_id="neuralink", amount_usd=1300000000.0,
         raw_amount_text="$1,300,000,000 (cumulative, company/press aggregate)",
         round_name="Cumulative to date", announced_date="not a single date -- aggregate figure",
         source_key="nt_neuralink_funding_tracker",
         note="Funding is not revenue; figure is a cumulative total reported by a funding tracker, "
              "not a single verified primary-source filing."),
    dict(company_id="synchron", amount_usd=200000000.0, raw_amount_text="$200,000,000",
         round_name="Series D", announced_date="2025-11", source_key="nt_synchron_funding",
         note="Reported in secondary source; recommend confirming against Synchron's own press "
              "release before citing in external materials."),
    dict(company_id="precision", amount_usd=250000000.0, raw_amount_text="$250,000,000",
         round_name="Series D", announced_date="2026-09", source_key="nt_precision_funding",
         note="Brings total disclosed capital raised to $430M per same source."),
    dict(company_id="paradromics", amount_usd=33000000.0, raw_amount_text="$33,000,000",
         round_name="Series A",
         announced_date="not precisely dated (disclosed alongside first FDA breakthrough designation)",
         source_key="nt_paradromics_funding",
         note="This figure is likely outdated given 2026 clinical progress; total current funding "
              "not found in original research pass -- flagged for update."),
    dict(company_id="blackrock", amount_usd=None, raw_amount_text="not publicly disclosed in this pass",
         round_name="not found", announced_date="not found", source_key="nt_blackrock_funding",
         note="Funding history not reconciled in original research pass; flagged for manual follow-up."),
    dict(company_id="cognixion", amount_usd=None, raw_amount_text="not publicly disclosed in this pass",
         round_name="not found", announced_date="not found", source_key="nt_cognixion_site",
         note="No funding figure found in original research pass; flagged for manual follow-up."),
    dict(company_id="onward", amount_usd=None, raw_amount_text="not reconciled in this pass",
         round_name="not found", announced_date="not found", source_key="nt_onward_site",
         note="ONWARD Medical is publicly listed (Euronext); funding should be sourced from investor "
              "relations filings rather than press trackers -- flagged for follow-up."),
]

UNCERTAINTIES += [
    dict(company_id="neuralink", category="scientific", description="Long-term signal stability/durability of thread electrodes has not yet been shown in independently published, peer-reviewed literature at the scale of company blog/press updates; bits-per-second metric is self-reported."),
    dict(company_id="neuralink", category="operational", description="Scaling of robotic surgical implantation and revision/explant rates are not fully disclosed publicly."),
    dict(company_id="neuralink", category="commercial", description="No disclosed pricing, reimbursement pathway, or payer model; timeline from breakthrough designation to a marketable, approved product is undefined."),
    dict(company_id="synchron", category="scientific", description="COMMAND study enrolled only 6 participants and was designed to assess safety, not statistically powered to demonstrate efficacy for a specific task."),
    dict(company_id="synchron", category="operational", description="Secondary-source terminology ('conditional market authorization') for the Home Edition is not a standard FDA pathway term and should be verified against a primary FDA or company source before being treated as fact."),
    dict(company_id="synchron", category="commercial", description="No disclosed price or reimbursement strategy; unclear whether initial commercialization (if cleared) would be self-pay, research-use-only, or covered by payers."),
    dict(company_id="blackrock", category="scientific", description="The '40+ individuals' figure spans many separate, non-standardized academic protocols over roughly 15+ years, so outcomes are not uniformly comparable across that population."),
    dict(company_id="blackrock", category="operational", description="Company funding history and any prior financial/operational volatility were not verified in this research pass."),
    dict(company_id="blackrock", category="commercial", description="Public information does not clearly establish a near-term path from research-use device to a reimbursed consumer/clinical product."),
    dict(company_id="precision", category="scientific", description="All 37 documented implants were short-term (<=30 days), mostly in patients undergoing unrelated neurosurgery -- this evidence base does not yet address chronic, long-term assistive-communication use."),
    dict(company_id="precision", category="operational", description="Converting a 510(k) clearance for temporary recording into a chronic implantable product will likely require additional regulatory submissions and clinical evidence."),
    dict(company_id="precision", category="commercial", description="A large Series D round signals investor confidence but does not by itself establish a revenue or reimbursement model."),
    dict(company_id="paradromics", category="scientific", description="The 'real-time speech' claim (Sept 2026) comes from a company press release; independent or peer-reviewed validation was not found in this research pass."),
    dict(company_id="paradromics", category="operational", description="Company is at a very early clinical stage (first human implant in June 2026); operational scale-up is largely untested."),
    dict(company_id="paradromics", category="commercial", description="Disclosed funding figure ($33M Series A) appears outdated relative to 2026 trial progress; current total funding is uncertain."),
    dict(company_id="cognixion", category="scientific", description="Non-invasive EEG has historically carried lower information bandwidth than invasive approaches; head-to-head performance data against eye-tracking AAC devices (the trial's own comparator) was not found in this pass."),
    dict(company_id="cognixion", category="operational", description="Device depends on interchangeable third-party AR hardware (Apple Vision Pro or XReal glasses), creating a supply-chain and compatibility dependency outside the company's direct control."),
    dict(company_id="cognixion", category="commercial", description="Existing AAC/speech-generating-device reimbursement codes may or may not apply to this product; this was not resolved in available sources."),
    dict(company_id="onward", category="scientific", description="Safety and efficacy of the combined BCI-plus-spinal-stimulation system versus either component alone has not been clearly separated in available sources."),
    dict(company_id="onward", category="operational", description="System requires two separate surgical implant procedures (brain and spine), which is a materially higher operational/surgical burden than single-device competitors."),
    dict(company_id="onward", category="commercial", description="Likely reimbursement pathway (spinal cord injury rehabilitation) differs from assistive-communication/computer-access reimbursement codes used by the direct-competitor set."),
]
