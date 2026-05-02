import { useState } from 'react';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ImageUpload from './components/ImageUpload';
import ProductGrid from './components/ProductGrid';
import ChatInterface from './components/ChatInterface';
import { useSearch } from './hooks/useSearch';
import { useChat } from './hooks/useChat';

function App() {
  const [activeTab, setActiveTab] = useState<'search' | 'chat'>('search');
  const { results, loading, search } = useSearch();
  const { messages, loading: chatLoading, sendMessage } = useChat();
  const [imageData, setImageData] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    await search(query, imageData || undefined);
  };

  const handleImageUpload = (data: string) => {
    setImageData(data);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'search' && (
          <div className="space-y-8">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <SearchBar onSearch={handleSearch} loading={loading} />
              </div>
              <div className="w-full md:w-80">
                <ImageUpload onUpload={handleImageUpload} />
              </div>
            </div>

            {imageData && (
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>🔍 Visual search active</span>
                <button
                  onClick={() => setImageData(null)}
                  className="text-red-500 hover:underline"
                >
                  Clear
                </button>
              </div>
            )}

            <ProductGrid products={results} loading={loading} />
          </div>
        )}

        {activeTab === 'chat' && (
          <ChatInterface
            messages={messages}
            loading={chatLoading}
            onSend={sendMessage}
          />
        )}
      </main>

      <footer className="border-t bg-white mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-gray-500">
          E-Commerce Product Intelligence System | Multi-Modal RAG
        </div>
      </footer>
    </div>
  );
}

export default App;