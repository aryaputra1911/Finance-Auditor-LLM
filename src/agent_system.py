import json
import yfinance as yf
from datetime import datetime, timedelta
from tavily import TavilyClient
from evaluator import FinancialEvaluator

class FinbenchSystem:
    def __init__(self, canonical_path, tavily_api_key):
        self.evaluator = FinancialEvaluator(canonical_path)
        self.tavily_api_key = tavily_api_key
        self.researcher = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None             
        self.evidence_weights = {
            "FUNDAMENTAL_DATA": 1.0,
            "PEER_CONTEXT": 0.5,
            "MARKET_NOISE": 0.0
        }

    # input classifier
    def _epistemic_noise_filter(self, query):
        speculative_noise = ['buy', 'sell', 'long', 'short', 'reco', 'advice', 'target']
        sentiment_noise = ['bullish', 'bearish', 'hype', 'undervalued', 'overvalued', 'moon']
        temporal_noise = ['surge', 'plunge', 'daily', 'news', 'rally', 'correction']
        
        all_noise = speculative_noise + sentiment_noise + temporal_noise
        detected = [word for word in all_noise if word in query.lower()]
        
        return {
            "is_noisy": len(detected) > 0,
            "noise_elements": detected,
            "action": "BLOCK_RECO" if any(w in speculative_noise for w in detected) else "IGNORE"
        }

    def _get_deep_fundamentals(self, ticker):
        try:
            t = yf.Ticker(ticker)
            bs = t.balance_sheet
            is_stmt = t.income_stmt
            
            def extract(df, keys):
                if df is not None and not df.empty:
                    df.index = df.index.str.replace(' ', '').str.lower()
                    search_keys = [k.replace(' ', '').lower() for k in keys]
                    for k in search_keys:
                        if k in df.index:
                            val = df.loc[k]
                            target = val.iloc[0] if hasattr(val, 'iloc') else val
                            if isinstance(target, (list, tuple)): target = target[0]
                            return float(target) if target is not None else 0.0
                return 0.0

            data = {
                "revenue": extract(is_stmt, ['Total Revenue', 'TotalRevenue']),
                "net_income": extract(is_stmt, ['Net Income', 'NetIncome']),
                "total_assets": extract(bs, ['Total Assets', 'TotalAssets']),
                "ppe_net": extract(bs, ['Net PPE', 'Property Plant Equipment Net', 'Fixed Assets']),
                "inventory": extract(bs, ['Inventory', 'Stock']),
                "total_liabilities": extract(bs, ['Total Liabilities Net Minority Interest', 'TotalLiabilities'])
            }
            
            # Debugging: Print untuk memastikan data tidak nol di terminal
            print(f"[*] Data Extracted for {ticker}: Rev: {data['revenue']}, Assets: {data['total_assets']}")
            return data
            
        except Exception as e:
            print(f"[!] Acquisition Error for {ticker}: {e}")
            return {}

    def _identify_business_archetype(self, ticker, fundamentals):
        rev = fundamentals.get("revenue")
        ni = fundamentals.get("net_income")
        margin = (ni / rev) if rev and ni else 0
        
        if margin > 0.15:
            return "IP_DRIVEN_PREMIUM_INDUSTRIAL"
        elif margin < 0.05:
            return "COMMODITY_VOLUME_PLAYER"
        return "STANDARD_MANUFACTURING"

    def _calculate_sovereign_metrics(self, fundamentals, archetype):
        rev = fundamentals.get("revenue", 0)
        assets = fundamentals.get("total_assets", 0)
        ni = fundamentals.get("net_income", 0)
        
        metrics = {}

        if rev > 0 and assets > 0:
            metrics["asset_turnover"] = round(rev / assets, 2)
            metrics["capital_intensity_ratio"] = round(assets / rev, 2)
            metrics["net_profit_margin"] = round((ni / rev) * 100, 2)
            metrics["return_on_assets"] = round((ni / assets) * 100, 2)
        
        return metrics

    def _audit_denominator_integrity(self, fundamentals):
        rev = fundamentals.get("revenue", 0)
        ppe = fundamentals.get("ppe_net", 0)
        assets = fundamentals.get("total_assets", 0)
        
        ppe_ratio = ppe / assets if assets > 0 else 0
        
        return {
            "ppe_to_assets": round(ppe_ratio, 3),
            "asset_structure": "EXTERNALIZED" if ppe_ratio < 0.15 else "INTEGRATED",
            "is_asset_light": ppe_ratio < 0.15
        }

    def _get_sector_benchmarks(self, ticker):
        sector_data = {"median_roa": 10.0, "median_turnover": 0.7, "status": "FALLBACK"}
        
        if self.researcher:
            try:
                # search ROA avg
                t = yf.Ticker(ticker)
                sector = t.info.get('sector', 'Technology')
                query = f"average ROA and asset turnover for {sector} sector 2025"
                search = self.researcher.search(query=query, max_results=1)
                sector_data["search_context"] = search['results'][0]['content'] if search['results'] else ""
                sector_data["sector_name"] = sector
                sector_data["status"] = "LIVE_SEARCH_DATA"
            except: pass
            
        return sector_data
    
    def _calculate_normalization_stress_test(self, mechanical_audit, benchmarks):
        reported_roa = mechanical_audit.get("roa", 0)
        current_intensity = mechanical_audit.get("capital_intensity", 0)
        median_ci = benchmarks.get("median_capital_intensity", 1.5) 
        
        if current_intensity >= median_ci:
            return {"status": "ALREADY_CAPITAL_INTENSE", "normalized_roa": reported_roa}

        normalized_roa = round(reported_roa * (current_intensity / median_ci), 2)        
        collapse_magnitude = round(((reported_roa - normalized_roa) / reported_roa) * 100, 2) if reported_roa > 0 else 0

        return {
            "normalized_roa": normalized_roa,
            "industry_target_ci": median_ci,
            "potential_roa_collapse_pct": collapse_magnitude,
            "integrity_risk": "HIGH" if collapse_magnitude > 40 else "STABLE"
        }

    def run(self, ticker, query=""):
        # running noise filter
        noise_audit = self._epistemic_noise_filter(query)
        
        # Data Acquisition
        raw_fund = self._get_deep_fundamentals(ticker)
        if not raw_fund or raw_fund.get("total_assets", 0) == 0:
            return {"error": f"Data Insufficient for {ticker}. Epistemic Block active."}

        # Analyze structure
        archetype = self._identify_business_archetype(ticker, raw_fund)
        metrics = self._calculate_sovereign_metrics(raw_fund, archetype)
        benchmarks = self._get_sector_benchmarks(ticker)
        denom_audit = self._audit_denominator_integrity(raw_fund)

        # Governance & Decision Perimeter
        governance = {
            "epistemic_grade": "EVIDENCE_STRONG" if not noise_audit["is_noisy"] else "EVIDENCE_CONTAMINATED_BY_NOISE",
            "noise_filter_report": noise_audit,
            "business_archetype": archetype,
            "decision_perimeter": {
                "allowed": ["ANALYZE_STRUCTURE", "AUDIT_INTEGRITY"],
                "forbidden": ["BUY", "SELL", "RECO_DIRECTIONAL"],
                "instruction_contract": "STRICT_NEUTRALITY_MANDATED"
            },
            "evidence_hierarchy_applied": self.evidence_weights
        }

        # Search Context only if funadmental is clean
        narratives = []
        if self.researcher:
            try:
                search = self.researcher.search(query=f"{ticker} structural moat audit", max_results=2)
                narratives = [{"content": r['content'], "url": r.get('url'), "reliability": self.evidence_weights["PEER_CONTEXT"]} for r in search['results']]
            except: pass
        
        mechanical_audit = {
            "roa": metrics.get("return_on_assets", 0),
            "capital_intensity": metrics.get("capital_intensity_ratio", 0)
        }
        stress_test_results = self._calculate_normalization_stress_test(mechanical_audit, benchmarks)

        return {
            "temporal": {"analysis_date": datetime.now().strftime("%Y-%m-%d")},
            "evidence_integrity": {
                "ticker": ticker, 
                "source_reliability": self.evidence_weights["FUNDAMENTAL_DATA"],
                "noise_contamination": noise_audit["is_noisy"]
            },
            "archetype_context": archetype,
            "sovereign_metrics": metrics,
            "stress_test": stress_test_results,
            "raw_data_summary": raw_fund,
            "denominator_audit": denom_audit,
            "benchmarks": benchmarks,
            "governance": governance,
            "context_noise": narratives
            
        }
