import { Star, Tag } from 'lucide-react';
import type { Product } from '../types';

interface ProductCardProps {
  product: Product;
  score?: number;
  method?: string;
}

export default function ProductCard({ product, score, method }: ProductCardProps) {
  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-3 h-3 ${i < Math.floor(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow p-4">
      <div className="flex gap-4">
        <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
          {product.image_path ? (
            <img src={product.image_path} alt={product.name} className="w-full h-full object-cover rounded-lg" />
          ) : (
            <Tag className="w-8 h-8 text-gray-400" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{product.name}</h3>
          <p className="text-sm text-gray-500">{product.brand}</p>

          <div className="flex items-center gap-1 mt-1">
            {renderStars(product.rating)}
            <span className="text-xs text-gray-500 ml-1">({product.rating})</span>
          </div>

          <div className="mt-2 flex items-center justify-between">
            <span className="text-lg font-bold text-blue-600">₹{product.price.toLocaleString()}</span>
            {score !== undefined && (
              <span className="text-xs text-gray-500">
                {method === 'vector' ? '🔍' : '📊'} {(score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>
      </div>

      {product.features.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1">
          {product.features.slice(0, 3).map((feature, idx) => (
            <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
              {feature}
            </span>
          ))}
          {product.features.length > 3 && (
            <span className="text-xs text-gray-400">+{product.features.length - 3} more</span>
          )}
        </div>
      )}
    </div>
  );
}