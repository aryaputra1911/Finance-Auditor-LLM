import os
import json
import re
import streamlit as st
from datetime import datetime
from groq import Groq
from agent_system import FinbenchSystem
from sovereign_prompt import llama_prompt_constitution

DEFAULT_CONFIG = {
    "GROQ_API_KEY": st.secrets["GROQ_API_KEY"],
    "TAVILY_API_KEY": st.secrets["TAVILY_API_KEY"],
    "MODEL_NAME": "llama-3.3-70b-versatile",
    "CANONICAL_PATH": r"C:\Users\ARYA\My Learning\Finbench-LLM\data\processed\canonical"
}

class SovereignLlamaBridge:
    def __init__(self, engine: FinbenchSystem):
        self.engine = engine
        self.client = Groq(api_key=DEFAULT_CONFIG["GROQ_API_KEY"])
        self.model = DEFAULT_CONFIG["MODEL_NAME"]

    def _resolve_ticker_automatically(self, user_query: str) -> str:
        resolver_prompt = f"""
        Identify the stock ticker symbol for the company mentioned in this query: "{user_query}"
        Rules:
        1. Identify the primary company mentioned.
        2. Respond ONLY with the ticker symbol in uppercase (e.g., AAPL, TSLA).
        3. If no clear stock/company is mentioned, respond with 'NONE'.
        """
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": resolver_prompt}],
                temperature=0.0
            )
            ticker = completion.choices[0].message.content.strip().upper()
            ticker = re.sub(r'[^A-Z]', '', ticker) # Bersihkan karakter non-huruf
            return None if "NONE" in ticker or not ticker else ticker
        except:
            return None

    def _execute_inference(self, messages: list) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            error_msg = str(e).lower()
            if "rate_limit" in error_msg or "429" in error_msg:
                return "⚠️ **PRECISION LOCK**: High-capacity inference (70B model) is unavailable because the token limit has been reached."
            return f"[BRIDGE_ERROR] AI Failure: {str(e)}"
        
    def _prepare_audit_context(self, context_data: dict) -> str:
        audit = context_data.get("sovereign_metrics", {}) 
        raw = context_data.get("raw_data_summary", {})
        stress = context_data.get("stress_test", {})
        denom = context_data.get("denominator_audit", {})
        
        roa = audit.get('return_on_assets', 0)
        turnover = audit.get('asset_turnover', 0)
        ppe_net = raw.get('ppe_net', 0)
        assets = raw.get('total_assets', 0)
        ppe_ratio = denom.get('ppe_to_assets', 0)

        # DETERMINISTIC MECHANICAL CALCULATION
        # If turnover is high (Asset-Light), we calculate the drop if forced to Industry Parity (AT ~0.7)
        target_at = 0.7  # Industry Standard for Integrated Manufacturers
        implied_margin = (roa / 100) / turnover if turnover > 0 else 0
        projected_roa_at_parity = (implied_margin * target_at) * 100

        return f"""
        [AUDIT_EVIDENCE_DATA]
        
        [1. DUPONT DECOMPOSITION]
        - Reported ROA: {roa}%
        - Current Asset Turnover (AT): {turnover}
        - Implied Net Margin: {round(implied_margin * 100, 2)}%
        
        [2. DENOMINATOR INTEGRITY]
        - PPE to Total Assets (Ratio): {ppe_ratio}
        - Asset Structure: {denom.get('asset_structure', 'UNKNOWN')}
        - Raw PPE Net: ${ppe_net:,.0f}
        - Total Assets: ${assets:,.0f}

        [3. MECHANICAL STRESS TEST (DETERMINISTIC)]
        - Current Capital Intensity: {audit.get('capital_intensity_ratio', 'N/A')}
        - Normalized AT Target: {target_at} (Integrated Standard)
        - Projected ROA at Parity: {round(projected_roa_at_parity, 2)}%
        - Potential Mechanical Collapse: {stress.get('potential_roa_collapse_pct', 'N/A')}%
        - Integrity Risk: {stress.get('integrity_risk', 'UNKNOWN')}
        
        [4. PRIMARY ENGINE VS AMPLIFIER]
        - Primary Driver: {'PRICING_POWER (High Margin)' if implied_margin > 0.15 else 'OPERATIONAL_VELOCITY (High Turnover)'}
        - Amplifier Status: {'ASSET_LIGHT_LEVERAGE' if ppe_ratio < 0.2 else 'INTEGRATED_HEAVY'}
        """
  
    def smart_query(self, user_query: str) -> dict:
        try:
            ticker = self._resolve_ticker_automatically(user_query)
            
            if not ticker:
                return {
                    "answer": "SYSTEM_MESSAGE: No valid ticker identified. Provide a clear company for structural audit.",
                    "sources": [], "roa": "N/A"
                }

            context_data = self.engine.run(ticker, query=user_query)
            if "error" in context_data:
                return {"answer": context_data["error"], "sources": [], "roa": "N/A"}

            formatted_context = self._prepare_audit_context(context_data)
            
            # LOGGING FOR AUDITOR VERIFICATION
            print(f"--- [SOVEREIGN DEBUG: {ticker}] ---")
            print(formatted_context)
            print("-----------------------------------")

            noise_report = context_data.get("governance", {}).get("noise_filter_report", {})
            noise_warning = ""
            if noise_report.get("is_noisy"):
                noise_warning = f"\nSYSTEM_ALERT: Market noise detected ({noise_report.get('noise_elements')}). Filter active."

            # WRAPPING DATA IN THE EXACT TAG THE LLM IS TRAINED TO LOOK FOR
            messages = [
                {"role": "system", "content": llama_prompt_constitution + noise_warning},
                {
                    "role": "user", 
                    "content": f"ANALYSIS_MANDATE: Perform a clinical audit using the data below.\n\n{formatted_context}\n\nUSER_QUESTION: {user_query}"
                }
            ]
            
            ai_answer = self._execute_inference(messages)
            
            # Response formatting logic...
            audit_res = context_data.get("sovereign_metrics", {})
            denom_res = context_data.get("denominator_audit", {})
            
            return {
                "answer": ai_answer,
                "sources": [n.get("url") for n in context_data.get("context_noise", []) if n.get("url")],
                "roa": f"{audit_res.get('return_on_assets', 'N/A')}%",
                "turnover": audit_res.get("asset_turnover", "N/A"),
                "margin": f"{audit_res.get('net_profit_margin', 'N/A')}%",
                "ppe_ratio": denom_res.get("ppe_to_assets", "N/A")
            }

        except Exception as e:
            return {"answer": f"⚠️ **INTERNAL_SYSTEM_ERROR**: {str(e)}", "sources": [], "roa": "N/A"}

    
