import { ShoppingBag, Search, MessageCircle } from 'lucide-react';

interface HeaderProps {
  activeTab: 'search' | 'chat';
  onTabChange: (tab: 'search' | 'chat') => void;
}

export default function Header({ activeTab, onTabChange }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <ShoppingBag className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">Product Intelligence</h1>
              <p className="text-xs text-gray-500">Multi-Modal RAG System</p>
            </div>
          </div>

          <nav className="flex gap-2">
            <button
              onClick={() => onTabChange('search')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'search'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Search className="w-4 h-4" />
              Search
            </button>
            <button
              onClick={() => onTabChange('chat')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === 'chat'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <MessageCircle className="w-4 h-4" />
              Q&A
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}