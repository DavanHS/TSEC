import axios from 'axios';
import type { SearchResponse, QueryResponse, RecommendResponse, Product } from '../types';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

const client = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' }
});

export async function searchProducts(query?: string, imageData?: string): Promise<SearchResponse> {
  const response = await client.post('/search', {
    query: query || null,
    image_data: imageData || null
  });
  return response.data;
}

export async function queryProducts(query: string, imageData?: string): Promise<QueryResponse> {
  const response = await client.post('/query', {
    query,
    image_data: imageData || null
  });
  return response.data;
}

export async function getRecommendations(productId: string, topK: number = 10): Promise<RecommendResponse> {
  const response = await client.post('/recommend', {
    product_id: productId,
    top_k: topK
  });
  return response.data;
}

export async function ingestProducts(products: Product[]): Promise<{ status: string; message: string; count: number }> {
  const response = await client.post('/ingest', products);
  return response.data;
}

export async function ingestFromFile(filePath: string): Promise<{ status: string; message: string; count: number }> {
  const response = await client.post('/ingest/file', { file_path: filePath });
  return response.data;
}