/// <reference types="vite/client" />

export interface Product {
  id: string;
  name: string;
  description: string;
  category: string;
  brand: string;
  price: number;
  rating: number;
  features: string[];
  image_path?: string;
}

export interface SearchResult {
  product: Product;
  score: number;
  method: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
}

export interface QueryResponse {
  answer: string;
  products: SearchResult[];
  sources: string[];
}

export interface RecommendResponse {
  original_product_id: string;
  recommendations: Product[];
  explanation: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  products?: Product[];
}