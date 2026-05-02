import { useState, useCallback } from 'react';
import { searchProducts } from '../services/api';
import type { SearchResult } from '../types';

export function useSearch() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string, imageData?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await searchProducts(query, imageData);
      setResults(response.results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
  }, []);

  return { results, loading, error, search, clearResults };
}