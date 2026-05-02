import { Loader2, SearchX } from 'lucide-react';
import ProductCard from './ProductCard';
import type { SearchResult } from '../types';

interface ProductGridProps {
  products: SearchResult[];
  loading: boolean;
}

export default function ProductGrid({ products, loading }: ProductGridProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <span className="ml-3 text-gray-600">Searching products...</span>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500">
        <SearchX className="w-12 h-12 mb-4" />
        <p>No products found</p>
        <p className="text-sm">Try a different search term or upload an image</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {products.map((result, idx) => (
        <ProductCard
          key={result.product.id || idx}
          product={result.product}
          score={result.score}
          method={result.method}
        />
      ))}
    </div>
  );
}