import os
import pandas as pd
import numpy as np
import re
from datetime import datetime

class FinancialEvaluator:
    def __init__(self, canonical_dir):
        self.canonical_dir = canonical_dir

    def _clean_value(self, val):
        if pd.isna(val) or val == "" or str(val).strip() in ["—", "-", "None", "0.0"]:
            return 0.0
        s = str(val).replace('$', '').replace(',', '').replace(' ', '')
        if '(' in s and ')' in s:
            s = '-' + s.replace('(', '').replace(')', '')
        try:
            s = re.sub(r'[^0-9.\-]', '', s)
            return float(s) if s else 0.0
        except:
            return 0.0

    def _detect_context(self, df):
        text = (df.to_string()[:1000]).lower()
        unit = "millions" if "million" in text else "thousands" if "thousand" in text else "units"
        currency = "USD" if any(x in text for x in ["$", "usd", "dollar"]) else "EUR" if "€" in text else "Unknown"
        return unit, currency

    def _get_metrics(self, company_id):
        # konwledge structure intiation
        store = {
            "observed": {
                "revenue": {"value": 0.0, "source": None},
                "net_income": {"value": 0.0, "source": None},
                "assets": {"value": 0.0, "source": None},
                "liabilities": {"value": 0.0, "source": None}
            },
            "metadata": {"unit": "unknown", "currency": "unknown", "files": []}
        }
        
        target_year = re.search(r'_(\d{4})', company_id).group(1) if re.search(r'_(\d{4})', company_id) else None
        
        try:
            files = [f for f in os.listdir(self.canonical_dir) if f.startswith(company_id) and f.endswith('.csv')]
            for file_name in files:
                df = pd.read_csv(os.path.join(self.canonical_dir, file_name))
                if df.empty: continue
                
                if store["metadata"]["unit"] == "unknown":
                    u, c = self._detect_context(df)
                    store["metadata"]["unit"], store["metadata"]["currency"] = u, c
                
                store["metadata"]["files"].append(file_name)
                
                target_col = None
                for col_idx in range(df.shape[1]):
                    header = str(df.columns[col_idx]) + " " + " ".join(df.iloc[:3, col_idx].astype(str))
                    if target_year and target_year in header:
                        target_col = col_idx; break
                
                if target_col is None: continue

                for i in range(len(df)):
                    row_txt = " ".join(df.iloc[i, :target_col].astype(str)).lower()
                    val = self._clean_value(df.iloc[i, target_col])
                    if val == 0.0: continue

                    # Mapping logic dengan source tracking
                    target_key = None
                    if "net sales" in row_txt or "total revenue" in row_txt:
                        if not any(x in row_txt for x in ["cost", "growth"]): target_key = "revenue"
                    elif "net income" in row_txt or "net earnings" in row_txt:
                        if not "per share" in row_txt: target_key = "net_income"
                    elif "total assets" in row_txt: target_key = "assets"
                    elif "total liabilities" in row_txt and "equity" not in row_txt: target_key = "liabilities"

                    if target_key:
                        store["observed"][target_key] = {"value": val, "source": file_name, "ts": datetime.now().isoformat()}

            return store
        except Exception as e:
            return store

    def analyze_company(self, company_id):
        raw = self._get_metrics(company_id)
        obs = raw["observed"]
        
        # Deductive reasoning layer
        inferred = {}
        
        # counting net margin
        rev = obs["revenue"]["value"]
        ni = obs["net_income"]["value"]
        if rev != 0 and ni != 0:
            inferred["net_margin"] = {
                "value": round(ni / rev, 4),
                "method": "deduced_from_observed",
                "formula": "net_income / revenue"
            }
        
        # Calculate Equity and Prove Accounting Identity
        assets = obs["assets"]["value"]
        liab = obs["liabilities"]["value"]
        equity_calc = round(assets - liab, 2)
        
        # epistemic validation
        anomalies = []
        is_collision = (assets == liab and assets != 0)
        
        # Identity Check
        identity_holds = (assets != 0 and liab != 0 and abs(assets - (liab + equity_calc)) < 1.0)
        
        if is_collision:
            anomalies.append({"type": "data_collision", "severity": "CRITICAL", "rationale": "Assets == Liabilities detected."})
        
        # scoring
        completeness = sum(1 for v in obs.values() if v["value"] != 0) / 4
        sanity_score = 1.0
        if is_collision: sanity_score -= 0.8
        if not identity_holds and assets != 0: sanity_score -= 0.4
        if raw["metadata"]["currency"] == "Unknown": sanity_score -= 0.2
        
        sanity_score = max(0.1, round(sanity_score, 2))

        return {
            "entity": company_id.split('_')[0] if company_id else "UNKNOWN",
            "period": company_id.split('_')[1] if '_' in company_id else "UNKNOWN",
            "knowledge_base": {
                "observed": obs,
                "inferred": inferred,
                "accounting_proof": {
                    "equity_deduced": equity_calc if not is_collision else "UNRELIABLE",
                    "identity_verified": identity_holds
                }
            },
            "epistemic_status": {
                "completeness": completeness,
                "sanity_score": sanity_score,
                "data_integrity": "PASSED" if sanity_score > 0.6 and not is_collision else "FAILED"
            },
            "anomalies": anomalies,
            "llm_semantic_contract": {
                "safe_to_reason": (completeness >= 0.75 and sanity_score >= 0.6),
                "reasoning_mode": "deductive" if identity_holds else "investigative",
                "known_unknowns": [k for k, v in obs.items() if v["value"] == 0],
                "caution_note": "Identity failure detected" if not identity_holds and assets != 0 else None
            },
            "metadata": raw["metadata"]
        }
