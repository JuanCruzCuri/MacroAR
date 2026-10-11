import { useState } from 'react';
import Dashboard from './components/Dashboard';
import Feed from './components/Feed';
import Header from './components/Header';
import Footer from './components/Footer';
import { fetchStatus, useApi } from './api';
import { FALLBACK_STATUS } from './fallbackData';

function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'feed'>('dashboard');
  const { data: status, isOffline } = useApi(fetchStatus, FALLBACK_STATUS);

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Header status={status} />
      
      {/* Tab Navigation */}
      <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'dashboard' ? 'tab-active' : 'tab-inactive'
              }`}
            >
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Datos Actuales
              </span>
            </button>
            <button
              onClick={() => setActiveTab('feed')}
              className={`py-4 px-1 text-sm font-medium transition-colors ${
                activeTab === 'feed' ? 'tab-active' : 'tab-inactive'
              }`}
            >
              <span className="flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
                Publicaciones
              </span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {activeTab === 'dashboard' ? <Dashboard status={status} isOffline={isOffline} /> : <Feed isOffline={isOffline} />}
      </main>

      <Footer status={status} />
    </div>
  );
}

export default App;
