import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Newspaper, ExternalLink, Activity, Clock3, Bookmark, Share2 } from 'lucide-react';
import './App.css';

const API_URL = "https://multi-source-news-digest-api-qoj2.onrender.com/digest";

// A simple utility to simulate relative dates from an article's illustrative ID
const getIllustrativeRelativeTime = (index) => {
  if (index < 1) return 'Just now';
  if (index < 3) return '1 hr ago';
  if (index < 6) return '3 hrs ago';
  if (index < 10) return '6 hrs ago';
  return 'Yesterday';
};

function App() {
  const [newsData, setNewsData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState('All');

  useEffect(() => {
    // Fetch data from FastAPI when the component mounts
    axios.get(API_URL)
      .then(response => {
        setNewsData(response.data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="loading-screen"><div className="spinner"></div><p>AI Engine syncing the latest clusters...</p></div>;
  if (error) return <div className="error-screen"><p>Error connecting to AI backend: {error}</p></div>;
  if (Object.keys(newsData).length === 0) return <div className="loading-screen"><p>No news processed yet. Wait for the AI backend!</p></div>;

  // Prepare data for the Chart
  const chartData = Object.keys(newsData).map(topic => ({
    topicName: topic,
    articleCount: newsData[topic].length
  }));

  // Prepare articles for the Grid
  let displayedArticles = [];
  if (selectedTopic === 'All') {
    Object.entries(newsData).forEach(([topic, articles]) => {
      articles.forEach(art => displayedArticles.push({ ...art, displayTopic: topic }));
    });
  } else {
    displayedArticles = newsData[selectedTopic].map(art => ({ ...art, displayTopic: selectedTopic }));
  }

  return (
    <div className="dashboard dark-mode">
      <header className="header">
        <h1><Activity className="icon-header" /> AI News Explorer</h1>
        <p>Real-time clustering & sentiment analysis dashboard powered by FastAPI & Gemini</p>
      </header>

      {/* Chart Section */}
      <section className="chart-section dashboard-panel">
        <h2>Topic Distribution Explorer</h2>
        <div className="chart-wrapper">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 30, left: -20, bottom: 10 }}>
              <XAxis dataKey="topicName" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13 }} />
              <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 13 }} />
              <Tooltip 
                cursor={{ fill: 'rgba(56, 189, 248, 0.05)' }} 
                contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.2)' }}
                labelStyle={{ color: '#f8fafc', fontWeight: 600, fontSize: '14px' }}
                itemStyle={{ color: '#e2e8f0', fontSize: '13px' }}
              />
              <Bar dataKey="articleCount" fill="#38bdf8" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Interactive Filters */}
      <section className="filter-section dashboard-panel">
        <button 
          className={`filter-btn ${selectedTopic === 'All' ? 'active' : ''}`}
          onClick={() => setSelectedTopic('All')}
        >
          All Clusters
        </button>
        {Object.keys(newsData).map(topic => (
          <button 
            key={topic}
            className={`filter-btn ${selectedTopic === topic ? 'active' : ''}`}
            onClick={() => setSelectedTopic(topic)}
          >
            {topic}
          </button>
        ))}
      </section>

      {/* News Grid */}
      <section className="news-grid">
        {displayedArticles.map((art, index) => (
          <div key={index} className="news-card">
            <div className="card-top">
              <span className="topic-tag">{art.displayTopic}</span>
              <span className={`sentiment-badge badge-${art.sentiment}`}>
                {art.sentiment}
              </span>
            </div>
            
            <h3 className="card-title">
              <a href={art.url} target="_blank" rel="noopener noreferrer">
                {art.title} <ExternalLink size={17} className="link-icon" />
              </a>
            </h3>
            
            <p className="card-summary">{art.summary}</p>
            
            <div className="card-details">
                <span className="source-info"><Newspaper size={16} /> {art.source}</span>
                <span className="date-info"><Clock3 size={15} /> {getIllustrativeRelativeTime(index)}</span>
            </div>

            <div className="card-actions">
              <button className="action-btn" title="Bookmark Article"><Bookmark size={18} /></button>
              <button className="action-btn" title="Share Article"><Share2 size={18} /></button>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

export default App;