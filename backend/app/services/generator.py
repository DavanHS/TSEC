import logging
from typing import List, Optional
from app.models.product import Product, SearchResult

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self, api_key: str, model_name: str = "gemini-pro-latest"):
        self.client = None
        self.model_name = model_name
        self.api_key = api_key
        if api_key and api_key != "your_gemini_api_key_here":
            try:
                from google.genai import Client
                self.client = Client(api_key=api_key)
                logger.info(f"Initialized Gemini client with model: {model_name}")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini: {e}")
                logger.warning("Using fallback responses")
        else:
            logger.info("No valid API key, using fallback responses")

    def generate_response(
        self,
        query: str,
        search_results: List[SearchResult],
        system_prompt: Optional[str] = None
    ) -> str:
        if not self.client:
            return self._fallback_response(query, search_results)

        context = self._build_context(search_results)

        prompt = f"""You are a helpful e-commerce assistant. Based on the user's query and retrieved products, provide a helpful answer.

User Query: {query}

Retrieved Products:
{context}

Instructions:
- Provide a clear, helpful answer to the user's query
- Reference specific products when relevant
- Keep the response concise but informative
- If no relevant products found, say so politely

Response:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._fallback_response(query, search_results)

    def _build_context(self, search_results: List[SearchResult]) -> str:
        context_parts = []

        for i, result in enumerate(search_results[:5], 1):
            product = result.product
            context_parts.append(f"""
{i}. {product.name}
   Category: {product.category}
   Brand: {product.brand}
   Price: ₹{product.price}
   Rating: {product.rating}/5
   Description: {product.description}
   Features: {', '.join(product.features)}
""")

        return "\n".join(context_parts)

    def _fallback_response(
        self,
        query: str,
        search_results: List[SearchResult]
    ) -> str:
        if not search_results:
            return "I couldn't find any products matching your query. Please try a different search term."

        top_3 = search_results[:3]
        response_parts = [
            f"Based on your query about '{query}', here are some recommendations:",
            ""
        ]

        for i, result in enumerate(top_3, 1):
            product = result.product
            response_parts.append(
                f"{i}. **{product.name}** by {product.brand} - ₹{product.price:,} "
                f"(⭐ {product.rating}/5)"
            )
            if product.features:
                response_parts.append(f"   Features: {', '.join(product.features[:3])}")

        response_parts.append("")
        response_parts.append(
            f"Found {len(search_results)} matching products. "
            "Configure GEMINI_API_KEY in .env for AI-generated responses."
        )

        return "\n".join(response_parts)

    def generate_recommendation_response(
        self,
        product: Product,
        recommendations: List[Product]
    ) -> str:
        if not self.client:
            return self._fallback_recommendation(product, recommendations)

        context = f"""
Original Product: {product.name}
Category: {product.category}
Brand: {product.brand}
Price: ₹{product.price}

Recommended Products:
"""

        for i, rec in enumerate(recommendations[:5], 1):
            context += f"""
{i}. {rec.name} - ₹{rec.price} ({rec.rating}/5)
"""

        prompt = f"""You are a helpful e-commerce assistant. Provide a recommendation explanation.

{context}

Provide a brief, helpful explanation of why these products are recommended.
Response:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return self._fallback_recommendation(product, recommendations)

    def _fallback_recommendation(
        self,
        product: Product,
        recommendations: List[Product]
    ) -> str:
        if not recommendations:
            return f"Because you viewed '{product.name}', we have more products in the {product.category} category that you might like."

        response = f"Based on your interest in **{product.name}** (₹{product.price:,}), you might also like:\n\n"
        
        for i, rec in enumerate(recommendations[:5], 1):
            response += f"{i}. **{rec.name}** - ₹{rec.price:,} ({rec.rating}⭐)\n"
        
        response += "\nThese products are similar based on category and features."
        
        return response


def create_generator(api_key: str) -> ResponseGenerator:
    return ResponseGenerator(api_key)