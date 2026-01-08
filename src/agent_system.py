import json
import yfinance as yf
from datetime import datetime, timedelta
from tavily import TavilyClient
from evaluator import FinancialEvaluator
from analytics import StockAnalyst 

class FinbenchSystem:
    def __init__(self, canonical_path, tavily_api_key):
        self.lstm_engine = StockAnalyst() 
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
                    for k in keys:
                        if k in df.index: 
                            val = df.loc[k].iloc[0]
                            return float(val) if val is not None else None
                return None

            return {
                "revenue": extract(is_stmt, ['Total Revenue', 'TotalRevenue']),
                "net_income": extract(is_stmt, ['Net Income', 'NetIncome']),
                "assets": extract(bs, ['Total Assets', 'TotalAssets']),
                "liabilities": extract(bs, ['Total Liabilities Net Minority Interest', 'TotalDebt', 'Total Liabilities'])
            }
        except Exception as e:
            print(f"[!] Acquisition Error {ticker}: {e}")
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
        rev = fundamentals.get("revenue")
        assets = fundamentals.get("assets")
        ni = fundamentals.get("net_income")
        
        metrics = {}
        if rev and assets and rev > 0:
            metrics["asset_turnover"] = round(rev / assets, 2)
            metrics["capital_intensity_ratio"] = round(assets / rev, 2)
            
            if archetype == "IP_DRIVEN_PREMIUM_INDUSTRIAL" and metrics["asset_turnover"] < 0.7:
                metrics["efficiency_status"] = "ARCHETYPE_CONSISTENT (High Margin Offset)"
            else:
                metrics["efficiency_status"] = "STANDARD"
                
        if ni and assets and assets > 0:
            metrics["return_on_assets"] = round((ni / assets) * 100, 2)
            
        return metrics

    def _get_sector_benchmarks(self, ticker):
        return {
            "source": "INTERNAL_ESTIMATE_2024",
            "industrial_median_cap_intensity": 1.5,
            "manufacturing_median_turnover": 0.8,
            "status": "QUALIFIED_BENCHMARK"
        }

    def run(self, ticker, query=""):
        # running noise filter
        noise_audit = self._epistemic_noise_filter(query)
        
        # Data Acquisition
        raw_fund = self._get_deep_fundamentals(ticker)
        if not raw_fund or None in raw_fund.values():
            return {"error": f"Data Insufficient for {ticker}. Epistemic Block active."}

        # Analyze structure
        archetype = self._identify_business_archetype(ticker, raw_fund)
        metrics = self._calculate_sovereign_metrics(raw_fund, archetype)
        benchmarks = self._get_sector_benchmarks(ticker)

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
                narratives = [{"content": r['content'], "reliability": self.evidence_weights["PEER_CONTEXT"]} for r in search['results']]
            except: pass

        return {
            "temporal": {"analysis_date": datetime.now().strftime("%Y-%m-%d")},
            "evidence_integrity": {
                "ticker": ticker, 
                "source_reliability": self.evidence_weights["FUNDAMENTAL_DATA"],
                "noise_contamination": noise_audit["is_noisy"]
            },
            "archetype_context": archetype,
            "sovereign_metrics": metrics,
            "benchmarks": benchmarks,
            "governance": governance,
            "context_noise": narratives
        }
