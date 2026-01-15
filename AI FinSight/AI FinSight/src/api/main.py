from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os

from src.core.data import get_analysis_data, get_market_news
from src.core.analysis import MarketClassifier, GenAIAnalyst

app = FastAPI(title="FinSight API", version="1.0.0")

# Initialize models
classifier = MarketClassifier()
analyst = GenAIAnalyst()

class AnalyzeRequest(BaseModel):
    ticker: str

class AnalyzeResponse(BaseModel):
    ticker: str
    current_price: float
    signal: str
    confidence: float
    report: str
    history: dict  # New field for Candlestick Chart data

@app.get("/")
def read_root():
    return {"status": "online", "service": "FinSight AI Agent"}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_market(request: AnalyzeRequest):
    try:
        ticker = request.ticker
        
        # 1. Fetch Data
        df = get_analysis_data(ticker)
        current_price = df['Close'].iloc[-1]
        
        # Serialize last 60 days for Charting
        history_df = df.tail(60).reset_index()
        # Handle string/timestamp conversion for JSON
        history_df['Date'] = history_df['Date'].astype(str) 
        history_data = history_df[['Date', 'Open', 'High', 'Low', 'Close']].to_dict(orient='list')
        
        # 2. Quantitative Analysis (ML)
        # In a real prod environment, we would load a pre-trained model.
        # Here, we simulate "Continuous Learning" by retraining on the latest history.
        signal, confidence = classifier.train_and_predict(df)
        
        if current_price < df['SMA_50'].iloc[-1]:
            # Simple override logic: if below 50 SMA, lean towards selling
            pass
            
        # 3. News Sentiment Analysis
        news = get_market_news(ticker)

        # 4. Generate Report (Qualitative)
        report = analyst.generate_report(ticker, df, signal, confidence, news)
        
        return AnalyzeResponse(
            ticker=ticker,
            current_price=current_price,
            signal=signal,
            confidence=confidence,
            report=report,
            history=history_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    query: str
    context: str

@app.post("/chat")
def chat_participant(request: ChatRequest):
    try:
        response = analyst.chat_with_analyst(request.query, request.context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
