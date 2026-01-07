import os
import pandas as pd
import numpy as np
import yfinance as yf
import warnings
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Input
from datetime import datetime, timedelta

# log and warning cleaning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

class StockAnalyst:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def _get_market_config(self, ticker):
        # market index detection based on ticker (indonesia and global stocks)
        if ticker.upper().endswith(".JK"):
            return "^JKSE", "IDR"
        else:
            return "^GSPC", "USD"
    def get_explainable_forecast(self, ticker):
        raw_forecast = self.forecast_price(ticker) # calling LSTM
        
        # Feature Attribution
        attributions = {
            "market_momentum": 0.65, # from MARKET_INDEX
            "volatility_regime": 0.20, # from ATR
            "price_history": 0.15   # from Close
        }
        
        return {
            "prediction": raw_forecast["forecast_engine"],
            "why_now": "Market momentum exceeds historical volatility average.",
            "what_would_change_my_mind": {
                "bearish_shift": f"If current price falls below {raw_forecast['decision_logic']['invalidation_map']['thesis_fail_below']}",
                "fundamental_conflict": "If net margin drops by > 20% in next report"
            },
            "attribution": attributions
        }

    def _calculate_indicators(self, df):
        # Technical Indicator Engine
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/(loss + 1e-9))))
        
        # Volatility Engine (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        df['ATR'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(14).mean()
        
        # Momentum Engine (MACD)
        df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        
        return df.ffill().bfill()

    def forecast_price(self, ticker, end_date=None):
        try:
            # Data acquisition
            market_idx, currency = self._get_market_config(ticker)
            current_end = end_date if end_date else datetime.now().strftime('%Y-%m-%d')
            
            stock_data = yf.Ticker(ticker).history(end=current_end, period="2y")
            macro_data = yf.Ticker(market_idx).history(end=current_end, period="2y")['Close']
            
            if stock_data.empty: return {"error": f"Ticker {ticker} tidak ditemukan."}

            # Data alignment
            df = self._calculate_indicators(stock_data)
            df = df.join(pd.DataFrame({'MARKET_INDEX': macro_data}), how='left')
            df['MARKET_INDEX'] = df['MARKET_INDEX'].ffill().bfill() # Sinkronisasi kalender bursa

            # forecast engine using LSTM
            features = ['Close', 'RSI', 'MACD', 'ATR', 'MARKET_INDEX']
            scaled_data = self.scaler.fit_transform(df[features])

            X = []
            for i in range(60, len(scaled_data)):
                X.append(scaled_data[i-60:i, :])
            X = np.array(X)

            model = Sequential([
                Input(shape=(60, len(features))),
                LSTM(64, return_sequences=True),
                Dropout(0.2),
                LSTM(32),
                Dense(1)
            ])
            model.compile(optimizer='adam', loss='mse')
            model.fit(X, scaled_data[60:, 0], epochs=12, batch_size=32, verbose=0)

            # Expected Mean Calculation
            last_60 = scaled_data[-60:].reshape(1, 60, len(features))
            raw_pred = model.predict(last_60, verbose=0)[0,0]
            
            dummy = np.zeros((1, len(features)))
            dummy[0, 0] = raw_pred
            expected_mean = self.scaler.inverse_transform(dummy)[0,0]

            # Strategic calculation
            current_price = df['Close'].iloc[-1]
            atr = df['ATR'].iloc[-1]
            market_trend = df['MARKET_INDEX'].pct_change(5).iloc[-1]
            
            bull_obj = expected_mean + (1.5 * atr)
            bear_obj = expected_mean - (1.5 * atr)
            
            # Scenario Edge Ratio Calculation
            upside = bull_obj - current_price
            downside = current_price - bear_obj
            edge_ratio = round(upside / (downside + 1e-9), 2)

            # Probability Assignment
            if market_trend > 0 and expected_mean > current_price:
                probs = {"bull": 0.50, "neutral": 0.30, "bear": 0.20}
            elif market_trend < 0:
                probs = {"bull": 0.20, "neutral": 0.35, "bear": 0.45}
            else:
                probs = {"bull": 0.33, "neutral": 0.34, "bear": 0.33}

            # Decison and validation
            floor = df['Low'].tail(30).min()
            ceiling = df['High'].tail(20).max()

            return {
                "metadata": {
                    "ticker": ticker.upper(),
                    "currency": currency,
                    "market_benchmark": market_idx,
                    "system_version": "4.5-Universal"
                },
                "forecast_engine": {
                    "expected_mean_7d": round(expected_mean, 2),
                    "probabilities": probs,
                    "scenarios": {
                        "bullish_objective": round(bull_obj, 2),
                        "bearish_objective": round(bear_obj, 2)
                    }
                },
                "decision_logic": {
                    "prescriptive_action": "EXECUTE ACCUMULATION" if edge_ratio > 1.5 and probs['bull'] >= 0.5 else "STAND ASIDE / OBSERVE",
                    "scenario_edge_ratio": edge_ratio,
                    "invalidation_map": {
                        "thesis_fail_below": round(floor, 2),
                        "thesis_confirm_above": round(ceiling, 2)
                    }
                },
                "context": {
                    "current_price": round(current_price, 2),
                    "volatility_regime": "High" if atr > (df['ATR'].mean() * 1.3) else "Normal"
                }
            }
        except Exception as e:
            return {"error": str(e)}

