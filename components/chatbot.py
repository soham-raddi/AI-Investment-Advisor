import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from data import queries

class InvestmentChatbot:
    """Chatbot helper for providing contextual investment advice using Databricks Foundation Models."""
    
    def __init__(self):
        # Explicitly initialize WorkspaceClient with token/host configuration from environment
        host = os.environ.get("DATABRICKS_HOST")
        token = os.environ.get("DATABRICKS_TOKEN")
        self.w = WorkspaceClient(host=host, token=token)
        self.endpoint_name = "databricks-meta-llama-3-3-70b-instruct"
        
    def get_stock_context(self, ticker=None) -> str:
        """Fetch stock-specific recommendation or a general market summary."""
        try:
            if ticker and ticker != "None - General Questions":
                rec_df = queries.get_stock_recommendation(ticker)
                if rec_df is not None and not rec_df.empty:
                    row = rec_df.iloc[0]
                    # Volatility displays as decimal ratio
                    vol_dec = float(row.get('Volatility', 0.0)) / 100
                    return (
                        f"Stock in Focus: {row.get('Ticker')} ({row.get('Sector')})\n"
                        f"- Current Price: ${float(row.get('Close', 0.0)):.2f}\n"
                        f"- Predicted Return: {float(row.get('Predicted_Return', 0.0)):.2%}\n"
                        f"- Volatility: {vol_dec:.4f}\n"
                        f"- Risk Level: {row.get('Risk_Level')}\n"
                        f"- Recommendation: {row.get('Recommendation')}\n"
                        f"- Confidence Score: {row.get('Confidence_Score', 0)}/10\n"
                        f"- Explanation: {row.get('Explanation')}"
                    )
                return f"Ticker '{ticker}' not found in the database."
            else:
                summary_df = queries.get_recommendation_summary()
                if summary_df is not None and not summary_df.empty:
                    r = summary_df.iloc[0]
                    return (
                        "Current Market Summary:\n"
                        f"- Total Stocks Covered: {int(r.get('total_stocks', 0))}\n"
                        f"- BUY Signals: {int(r.get('buy_count', 0))}\n"
                        f"- HOLD Signals: {int(r.get('hold_count', 0))}\n"
                        f"- AVOID Signals: {int(r.get('avoid_count', 0))}\n"
                        f"- Average Predicted Return: {float(r.get('avg_predicted_return', 0.0)):.2%}"
                    )
                return "No recommendation summary available."
        except Exception as e:
            return f"Error retrieving stock context: {str(e)}"
            
    def generate_response(self, user_message: str, conversation_history: list, current_ticker=None) -> str:
        """Generate response content using Databricks Foundation Model endpoint."""
        try:
            # Build system prompt containing the live data context
            stock_context = self.get_stock_context(current_ticker)
            system_prompt = (
                "You are an expert conversational AI investment advisor. Your goal is to guide the user with "
                "clear, structured, and insightful advice about risk/return trade-offs.\n"
                "You must reference specific metrics provided below when answering queries.\n\n"
                f"{stock_context}\n\n"
                "Guidelines:\n"
                "1. Always focus on risk vs return profiles.\n"
                "2. When mentioning volatility, represent it as a decimal (e.g. 0.0150) and explain what that implies.\n"
                "3. Ensure your suggestions remain objective and references the data points directly.\n"
                "4. Always include the standard disclaimer at the end: 'Disclaimer: This dashboard is for educational "
                "and informational purposes only, and does not constitute professional financial advice.'\n"
            )
            
            # Convert system prompt & conversation history to ChatMessage lists
            messages = [
                ChatMessage(role=ChatMessageRole.SYSTEM, content=system_prompt)
            ]
            
            for msg in conversation_history:
                role = ChatMessageRole.USER if msg["role"] == "user" else ChatMessageRole.ASSISTANT
                messages.append(ChatMessage(role=role, content=msg["content"]))
                
            messages.append(ChatMessage(role=ChatMessageRole.USER, content=user_message))
            
            # Query the endpoint using serve client
            response = self.w.serving_endpoints.query(
                name=self.endpoint_name,
                messages=messages,
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract content text from serving response object
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            return "No response content generated by the endpoint."
            
        except Exception as e:
            return f"An error occurred while calling the AI model: {str(e)}"
