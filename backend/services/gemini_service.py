"""
Google Gemini service for AI vision and text generation
"""

import google.generativeai as genai
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY must be set in environment variables")
        
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 2.5 Pro (Latest Stable High-Reasoning Model)
        self.vision_model = genai.GenerativeModel('gemini-2.5-pro')
        self.text_model = genai.GenerativeModel('gemini-2.5-pro')
    
    async def analyze_product_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze a product image and extract fashion attributes
        
        Returns:
            Dict with: style, colors, patterns, occasion, category, description
        """
        
        # Download image
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            image_data = response.content
        
        prompt = """Analyze this fashion item and extract the following information in JSON format:

{
  "category": "dress/top/pants/jacket/shoes/accessory",
  "style": "casual/formal/business/party/athletic",
  "colors": ["primary color", "secondary color"],
  "patterns": ["solid/floral/striped/polka-dot/geometric"],
  "occasion": "everyday/work/party/wedding/casual",
  "description": "Brief 1-sentence description",
  "search_keywords": ["keyword1", "keyword2", "keyword3"]
}

Be specific and accurate. Focus on visual attributes that would help match similar products."""

        response = self.vision_model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response
            text = response.text
            # Find JSON object in response
            start = text.find('{')
            end = text.rfind('}') + 1
            json_str = text[start:end]
            analysis = json.loads(json_str)
            return analysis
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            # Return default structure
            return {
                "category": "unknown",
                "style": "casual",
                "colors": ["unknown"],
                "patterns": ["solid"],
                "occasion": "everyday",
                "description": "Fashion item",
                "search_keywords": ["clothing"]
            }
    
    async def generate_product_search_query(self, image_analysis: Dict[str, Any]) -> str:
        """Generate a search query from image analysis"""
        keywords = image_analysis.get("search_keywords", [])
        category = image_analysis.get("category", "")
        style = image_analysis.get("style", "")
        
        # Combine into search query
        query_parts = [category, style] + keywords[:3]
        return " ".join([p for p in query_parts if p])
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate text content from a prompt
        
        Args:
            prompt: The prompt string
        
        Returns:
            Generated text response
        """
        response = self.text_model.generate_content(prompt)
        return response.text.strip()
    
    async def generate_conversational_response(
        self,
        customer_message: str,
        products: List[Dict[str, Any]],
        customer_name: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate a natural, conversational response for the customer
        
        Args:
            customer_message: The customer's message
            products: List of products to recommend
            customer_name: Customer's name if known
            conversation_history: Previous conversation for context
        """
        
        # Build context
        context = f"You are a friendly AI sales assistant for a fashion boutique in Kenya. "
        if customer_name:
            context += f"The customer's name is {customer_name}. "
        
        context += "\n\nCustomer message: " + customer_message
        
        if products:
            context += f"\n\nYou have found {len(products)} matching products:\n"
            for i, product in enumerate(products[:3], 1):
                context += f"{i}. {product['name']} - KES {product['price']}\n"
                if product.get('description'):
                    context += f"   {product['description']}\n"
        
        prompt = f"""{context}

Generate a warm, friendly response that:
1. Acknowledges what the customer is looking for
2. Presents the products naturally (don't just list them)
3. Highlights key features that match their request
4. Asks if they'd like to know more or see other options
5. Uses Kenyan English style (friendly, warm, professional)
6. Keep it concise (2-3 sentences max)

Response:"""

        response = self.text_model.generate_content(prompt)
        return response.text.strip()
    
    async def generate_size_recommendation(
        self,
        customer_history: Dict[str, Any],
        product: Dict[str, Any]
    ) -> Optional[str]:
        """Generate size recommendation based on customer's purchase history"""
        
        if not customer_history.get("size_history"):
            return None
        
        prompt = f"""Based on this customer's size history:
{customer_history.get('size_history')}

And this product:
{product.get('name')} - Available sizes: {product.get('sizes')}

Recommend the most likely size for this customer. Reply with just the size (S/M/L/XL) or "unknown" if uncertain."""

        response = self.text_model.generate_content(prompt)
        size = response.text.strip().upper()
        
        # Validate size is in available sizes
        available_sizes = product.get('sizes', [])
        if size in available_sizes:
            return size
        return None
    
    # =====================================================
    # FUNCTION CALLING SUPPORT
    # =====================================================
    
    async def chat_with_tools(
        self,
        message: str,
        tools: List[Dict[str, Any]],
        context: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Have a conversation with tool calling enabled.
        
        Args:
            message: User's message
            tools: List of tool schemas
            context: Context dict with boutique_id, customer_id, etc.
            conversation_history: Previous conversation turns
        
        Returns:
            Dict with response text, tool_calls, and updated history
        """
        from agents.tools import execute_tool
        
        # Create model with tools
        model_with_tools = genai.GenerativeModel(
            model_name='gemini-2.5-pro',
            tools=tools
        )
        
        # Build conversation history for Gemini
        history = []
        if conversation_history:
            for turn in conversation_history:
                history.append({
                    "role": turn.get("role", "user"),
                    "parts": [turn.get("content", "")]
                })
        
        # Start chat
        chat = model_with_tools.start_chat(history=history)
        
        # Send message
        response = chat.send_message(message)
        
        # Check if model wants to call functions
        tool_calls = []
        final_response = ""
        
        try:
            # Check for function calls in response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    # Check if this part is a function call
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        print(f"🔧 Tool call: {function_name}({function_args})")
                        
                        # Execute the tool
                        tool_result = await execute_tool(
                            tool_name=function_name,
                            tool_args=function_args,
                            context=context
                        )
                        
                        tool_calls.append({
                            "name": function_name,
                            "args": function_args,
                            "result": tool_result
                        })
                        
                        # Send result back to model
                        response = chat.send_message(
                            genai.protos.Content(
                                parts=[genai.protos.Part(
                                    function_response=genai.protos.FunctionResponse(
                                        name=function_name,
                                        response={"result": tool_result}
                                    )
                                )]
                            )
                        )
                    
                    # Get text response
                    if hasattr(part, 'text') and part.text:
                        final_response += part.text
            
            # If no text response yet, get it from the final response
            if not final_response and response.text:
                final_response = response.text
        
        except Exception as e:
            print(f"❌ Error in function calling: {str(e)}")
            # Fallback to simple response
            final_response = response.text if hasattr(response, 'text') else "I encountered an error processing your request."
        
        return {
            "response": final_response.strip(),
            "tool_calls": tool_calls,
            "conversation_history": history + [
                {"role": "user", "content": message},
                {"role": "model", "content": final_response}
            ]
        }

# Global instance
gemini_service = GeminiService()

