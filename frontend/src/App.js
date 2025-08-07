import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [userId] = useState('user_' + Math.random().toString(36).substr(2, 9));
  const [aiConfig, setAiConfig] = useState(null);
  const [availableModels, setAvailableModels] = useState({});
  const [analyses, setAnalyses] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    loadAvailableModels();
    loadUserConfig();
    loadUserAnalyses();
  }, []);

  const loadAvailableModels = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/ai-models`);
      const models = await response.json();
      setAvailableModels(models);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const loadUserConfig = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/ai-config/${userId}`);
      const config = await response.json();
      setAiConfig(config);
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const loadUserAnalyses = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/user-analyses/${userId}`);
      const data = await response.json();
      setAnalyses(data.analyses || []);
    } catch (error) {
      console.error('Failed to load analyses:', error);
    }
  };

  const AIConfigView = () => {
    const [selectedProvider, setSelectedProvider] = useState('openai');
    const [selectedModel, setSelectedModel] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [saving, setSaving] = useState(false);

    useEffect(() => {
      if (availableModels[selectedProvider]) {
        const firstModel = Object.keys(availableModels[selectedProvider])[0];
        setSelectedModel(firstModel);
      }
    }, [selectedProvider, availableModels]);

    const saveConfiguration = async () => {
      if (!apiKey.trim()) {
        alert('Please enter your API key');
        return;
      }

      setSaving(true);
      try {
        const response = await fetch(`${backendUrl}/api/ai-config`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            provider: selectedProvider,
            model: selectedModel,
            api_key: apiKey,
            user_id: userId
          })
        });

        if (response.ok) {
          alert('Configuration saved successfully!');
          loadUserConfig();
          setCurrentView('home');
        } else {
          throw new Error('Failed to save configuration');
        }
      } catch (error) {
        alert('Failed to save configuration: ' + error.message);
      } finally {
        setSaving(false);
      }
    };

    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Configure AI Model</h2>
          
          <div className="space-y-6">
            {/* Provider Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Select AI Provider</label>
              <div className="grid grid-cols-3 gap-4">
                {Object.keys(availableModels).map(provider => (
                  <button
                    key={provider}
                    onClick={() => setSelectedProvider(provider)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      selectedProvider === provider
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <div className="font-semibold capitalize">{provider}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        {provider === 'openai' && '🤖 GPT Models'}
                        {provider === 'anthropic' && '🧠 Claude Models'}
                        {provider === 'gemini' && '💎 Gemini Models'}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Model Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">Select Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {availableModels[selectedProvider] && Object.entries(availableModels[selectedProvider]).map(([key, name]) => (
                  <option key={key} value={key}>{name}</option>
                ))}
              </select>
            </div>

            {/* API Key Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder={`Enter your ${selectedProvider} API key`}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="mt-2 text-sm text-gray-500">
                Get your API key from:
                {selectedProvider === 'openai' && <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline ml-1">OpenAI Platform</a>}
                {selectedProvider === 'anthropic' && <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline ml-1">Anthropic Console</a>}
                {selectedProvider === 'gemini' && <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline ml-1">Google Cloud Console</a>}
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentView('home')}
                className="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={saveConfiguration}
                disabled={saving}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const RepoAnalysisView = () => {
    const [repoUrl, setRepoUrl] = useState('');
    const [analyzing, setAnalyzing] = useState(false);

    const startAnalysis = async () => {
      if (!repoUrl.trim()) {
        alert('Please enter a GitHub repository URL');
        return;
      }

      if (!aiConfig?.configured) {
        alert('Please configure AI model first');
        setCurrentView('config');
        return;
      }

      setAnalyzing(true);
      try {
        const response = await fetch(`${backendUrl}/api/analyze-repository`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            repo_url: repoUrl,
            user_id: userId
          })
        });

        const result = await response.json();
        
        if (response.ok) {
          alert('Analysis started! Check the "My Analyses" section for progress.');
          setRepoUrl('');
          loadUserAnalyses();
        } else {
          throw new Error(result.detail || 'Failed to start analysis');
        }
      } catch (error) {
        alert('Failed to start analysis: ' + error.message);
      } finally {
        setAnalyzing(false);
      }
    };

    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Analyze Repository</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">GitHub Repository URL</label>
              <input
                type="url"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                placeholder="https://github.com/username/repository"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="mt-2 text-sm text-gray-500">
                Enter any public GitHub repository URL to generate AI-powered flashcards
              </div>
            </div>

            {aiConfig?.configured && (
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-green-800">
                  <strong>AI Model:</strong> {aiConfig.model_name} ({aiConfig.provider})
                </div>
              </div>
            )}

            <button
              onClick={startAnalysis}
              disabled={analyzing || !repoUrl.trim()}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {analyzing ? 'Starting Analysis...' : 'Analyze Repository'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  const FlashcardsView = ({ analysis }) => {
    const [currentCard, setCurrentCard] = useState(0);
    const [showBack, setShowBack] = useState(false);

    const flashcards = analysis?.flashcards || [];

    if (!flashcards.length) {
      return (
        <div className="text-center py-8">
          <div className="text-gray-500">No flashcards generated yet.</div>
        </div>
      );
    }

    const card = flashcards[currentCard];

    return (
      <div className="max-w-2xl mx-auto">
        <div className="mb-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Flashcards</h2>
          <div className="text-sm text-gray-500">
            {currentCard + 1} of {flashcards.length}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 min-h-96">
          <div className="text-center">
            <div className="mb-4">
              <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {card.category}
              </span>
              <span className={`inline-block px-3 py-1 rounded-full text-sm ml-2 ${
                card.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                card.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {card.difficulty}
              </span>
            </div>

            <div className="mb-6">
              {!showBack ? (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">
                    {card.front}
                  </h3>
                  <button
                    onClick={() => setShowBack(true)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Show Answer
                  </button>
                </div>
              ) : (
                <div>
                  <h3 className="text-lg font-medium text-gray-600 mb-4">
                    {card.front}
                  </h3>
                  <div className="text-gray-800 mb-4 text-left">
                    {card.back}
                  </div>
                  
                  {card.code_snippet && (
                    <div className="bg-gray-100 p-4 rounded-lg text-left mb-4">
                      <pre className="text-sm text-gray-700 overflow-x-auto">
                        <code>{card.code_snippet}</code>
                      </pre>
                      {card.file_path && (
                        <div className="text-xs text-gray-500 mt-2">
                          File: {card.file_path}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => {
                  setCurrentCard(Math.max(0, currentCard - 1));
                  setShowBack(false);
                }}
                disabled={currentCard === 0}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
              >
                Previous
              </button>
              
              <button
                onClick={() => setShowBack(false)}
                className="px-4 py-2 text-blue-600 hover:text-blue-800 transition-colors"
              >
                Reset Card
              </button>

              <button
                onClick={() => {
                  setCurrentCard(Math.min(flashcards.length - 1, currentCard + 1));
                  setShowBack(false);
                }}
                disabled={currentCard === flashcards.length - 1}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const HomeView = () => {
    return (
      <div className="space-y-8">
        {/* Hero Section */}
        <div className="text-center py-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            AI-Powered Code Learning System
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform any GitHub repository into personalized flashcards and mind maps. 
            Let AI analyze codebases and create the perfect study materials for mastering new technologies.
          </p>
        </div>

        {/* Status Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">AI Configuration</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {aiConfig?.configured ? `${aiConfig.model_name}` : 'Not configured'}
                </p>
              </div>
              <div className={`w-3 h-3 rounded-full ${aiConfig?.configured ? 'bg-green-500' : 'bg-red-500'}`}></div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">Total Analyses</h3>
                <p className="text-2xl font-bold text-blue-600 mt-1">{analyses.length}</p>
              </div>
              <div className="text-blue-500">📊</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-800">Flashcards Generated</h3>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {analyses.reduce((total, analysis) => total + (analysis.flashcards?.length || 0), 0)}
                </p>
              </div>
              <div className="text-green-500">🎯</div>
            </div>
          </div>
        </div>

        {/* Recent Analyses */}
        {analyses.length > 0 && (
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-800">Recent Analyses</h3>
            </div>
            <div className="divide-y">
              {analyses.slice(0, 3).map(analysis => (
                <div key={analysis.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-800">
                        {analysis.repo_url.split('/').slice(-2).join('/')}
                      </h4>
                      <div className="text-sm text-gray-600 mt-1">
                        {analysis.languages?.join(', ')} • {analysis.flashcards?.length || 0} flashcards
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        analysis.status === 'completed' ? 'bg-green-100 text-green-800' :
                        analysis.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        analysis.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {analysis.status}
                      </span>
                      {analysis.status === 'completed' && (
                        <button
                          onClick={() => {
                            setCurrentAnalysis(analysis);
                            setCurrentView('flashcards');
                          }}
                          className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                        >
                          Study
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="text-center space-y-4">
          {!aiConfig?.configured ? (
            <button
              onClick={() => setCurrentView('config')}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium"
            >
              Configure AI Model
            </button>
          ) : (
            <button
              onClick={() => setCurrentView('analyze')}
              className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-lg font-medium"
            >
              Analyze New Repository
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-800">CodeLearn AI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('home')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  currentView === 'home' 
                    ? 'text-blue-700 bg-blue-100' 
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentView('config')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  currentView === 'config' 
                    ? 'text-blue-700 bg-blue-100' 
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                AI Config
              </button>
              <button
                onClick={() => setCurrentView('analyze')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  currentView === 'analyze' 
                    ? 'text-blue-700 bg-blue-100' 
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Analyze Repo
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'home' && <HomeView />}
        {currentView === 'config' && <AIConfigView />}
        {currentView === 'analyze' && <RepoAnalysisView />}
        {currentView === 'flashcards' && <FlashcardsView analysis={currentAnalysis} />}
      </main>
    </div>
  );
}

export default App;