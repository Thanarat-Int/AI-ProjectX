import os
import google.generativeai as genai
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from dotenv import load_dotenv

load_dotenv()

class MarketClassifier:
    """
    Machine Learning Model to predict Buy (1) or Sell (0) signals.
    """
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
        
    def prepare_data(self, df: pd.DataFrame):
        """
        Prepares features (X) and target (y) for the model.
        Target: 1 if Close price rises tomorrow, else 0.
        """
        df = df.copy()
        
        # Features: RSI, MACD, etc.
        feature_cols = ['RSI', 'MACD', 'MACD_Signal', 'SMA_50', 'SMA_200', 'BB_High', 'BB_Low']
        X = df[feature_cols]
        
        # Target: Next day's close > Current close
        y = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # Drop last row (NaN target)
        X = X[:-1]
        y = y[:-1]
        
        return X, y
    
    def train_and_predict(self, df: pd.DataFrame):
        """
        Trains the model on historical data and predicts the signal for the LAST available day.
        """
        X, y = self.prepare_data(df)
        
        # Split data (Simple time-series split)
        train_size = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
        y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
        
        self.model.fit(X_train, y_train)
        
        # Evaluate (internal log)
        acc = accuracy_score(y_test, self.model.predict(X_test))
        print(f"Model Accuracy (Test Set): {acc:.2f}")
        
        # Predict for the MOST RECENT day (Today)
        # We use the latest features to predict tomorrow's movement
        latest_features = df[['RSI', 'MACD', 'MACD_Signal', 'SMA_50', 'SMA_200', 'BB_High', 'BB_Low']].iloc[[-1]]
        prediction = self.model.predict(latest_features)[0]
        probability = self.model.predict_proba(latest_features)[0][prediction]
        
        signal = "BUY" if prediction == 1 else "SELL"
        return signal, probability

class GenAIAnalyst:
    """
    Interface for Gemini 1.5 to generate qualitative analysis.
    """
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found. GenAI features will provide mock responses.")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
    def generate_report(self, ticker: str, df: pd.DataFrame, signal: str, confidence: float, news: list = []):
        """
        Generates a financial report based on technical data, ML signal, and NEWS.
        """
        # Summarize latest data
        latest = df.iloc[-1]
        
        # Format News for Prompt
        news_section = "\n".join([f"- {n['title']} ({n['published']})" for n in news])
        
        # Define the Mock Report (Offline Mode)
        mock_report = f"""
### 📉 AI Analyst Report (Offline Mode)

**Ticker:** {ticker}
**Trend Analysis:**
Market data indicates the price is currently at **{latest['Close']:.2f}** USD.
- **RSI:** {latest['RSI']:.2f} (Momentum check)
- **MACD:** {latest['MACD']:.2f} vs Signal {latest['MACD_Signal']:.2f}

**Recent Headlines:**
{news_section if news else "- No recent news fetched."}

**Model Verdict:**
The predictive model suggests a **{signal}** action with **{confidence:.1%}** confidence. 

*Note: This is a generated simulation because the Gemini API Key was invalid or missing.*
"""

        # If no model configured, return mock immediately
        if not self.model:
            return mock_report
        
        prompt = f"""
        Act as a Senior Financial Analyst at a top investment bank.
        
        Ticker: {ticker}
        
        Recent News Headlines:
        {news_section}
        
        Technical Indicators (Latest Data):
        - Close Price: {latest['Close']:.2f}
        - RSI (14): {latest['RSI']:.2f} (Overbought > 70, Oversold < 30)
        - MACD: {latest['MACD']:.2f}
        
        Quantitative Model Prediction:
        - Signal: {signal}
        - Model Confidence: {confidence:.2%}
        
        Task:
        Write a concise, professional daily investment report.
        1. Synthesize the Technical data with the Sentiment from the news headlines.
        2. Cross-reference with the ML model's prediction.
        3. Provide a clear recommendation.
        
        Format the output in Markdown. Keep it under 200 words.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"GenAI Connection Failed: {e}")
            return mock_report

    def chat_with_analyst(self, query: str, context: str) -> str:
        """
        Answering user questions based on the previous analysis context.
        """
        # Friendly Fallback if API is missing or invalid
        offline_msg = "ℹ️ **Offline Mode:** Chat is unavailable without a valid API Key. (Mock data only)"

        if not self.model:
            return offline_msg
            
        prompt = f"""
        You are FinSight AI, a professional financial assistant.
        
        Context Recommendation:
        {context}
        
        User Question:
        {query}
        
        Answer the user politely and professionally based on the provided context.
        Keep answer short (under 100 words).
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # If 400 or other API errors occur, fallback gracefully
            return offline_msg
