import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Terminal, 
  CheckSquare, 
  BookOpen, 
  Cpu, 
  Code2, 
  Briefcase, 
  Database, 
  BarChart3, 
  Settings, 
  Send, 
  Mic, 
  Sparkles,
  Zap,
  Clock,
  ShieldCheck
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [health, setHealth] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'jarvis',
      text: "Greetings. I am Tamizh JARVIS, your personal agentic assistant. Systems are operational and ready. How may I assist your productivity, study, or coding today?",
      time: 'Just now',
      intent: 'SYSTEM_READY'
    }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [aiState, setAiState] = useState('Online');

  useEffect(() => {
    // Poll backend health
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
          setAiState('Online');
        } else {
          setAiState('Degraded');
        }
      } catch (err) {
        setAiState('Backend Connecting');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: inputVal,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    const currentInput = inputVal;
    setInputVal('');

    // Simulate Agentic Loop Transition
    setAiState('Thinking');
    setTimeout(() => {
      setAiState('Planning');
      setTimeout(() => {
        setAiState('Online');
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'jarvis',
            text: `Received: "${currentInput}". JARVIS Core pipeline is established and preparing next-generation tool integration.`,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            intent: 'GENERAL_CHAT'
          }
        ]);
      }, 700);
    }, 500);
  };

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'chat', label: 'JARVIS Chat', icon: Bot },
    { id: 'tasks', label: 'Task Engine', icon: CheckSquare },
    { id: 'study', label: 'Study & GATE', icon: BookOpen },
    { id: 'dsa', label: 'DSA Practice', icon: Code2 },
    { id: 'career', label: 'Career Roadmap', icon: Briefcase },
    { id: 'memory', label: 'Long-Term Memory', icon: Database },
    { id: 'settings', label: 'Settings & Security', icon: Settings },
  ];

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <Zap size={20} />
          </div>
          <div className="brand-title">
            <span className="brand-name">TAMIZH JARVIS</span>
            <span className="brand-tagline">AGENTIC AI ASSISTANT</span>
          </div>
        </div>

        <nav className="nav-section">
          <div className="nav-label">Core Modules</div>
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon size={17} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main Viewport */}
      <div className="main-viewport">
        {/* Top Header */}
        <header className="top-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Mode: <strong style={{ color: 'var(--text-primary)' }}>Autonomous Agent</strong>
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="status-badge">
              <span className="status-dot"></span>
              <span>{aiState}</span>
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Provider: {health?.ai_provider || 'Initializing'}
            </div>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="dashboard-grid">
          {/* Chat Pane */}
          <section className="chat-pane">
            <div className="chat-messages">
              {messages.map(msg => (
                <div key={msg.id} className={`message ${msg.sender}`}>
                  <div className="message-avatar">
                    {msg.sender === 'jarvis' ? <Bot size={18} /> : 'U'}
                  </div>
                  <div className="message-content">
                    <div className="message-body">
                      {msg.text}
                    </div>
                    <div className="message-meta">
                      <span>{msg.time}</span>
                      {msg.intent && (
                        <>
                          <span>•</span>
                          <span style={{ color: 'var(--accent-cyan)' }}>{msg.intent}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendMessage} className="chat-input-bar">
              <div className="input-container">
                <button type="button" className="action-btn" title="Voice Command">
                  <Mic size={18} />
                </button>
                <input
                  type="text"
                  className="chat-input"
                  placeholder="Message JARVIS... (e.g., 'What is my next best action?')"
                  value={inputVal}
                  onChange={e => setInputVal(e.target.value)}
                />
                <button type="submit" className="action-btn send" title="Send Message">
                  <Send size={16} />
                </button>
              </div>
            </form>
          </section>

          {/* Right Telemetry Pane */}
          <aside className="telemetry-pane">
            {/* Next Best Action Card */}
            <div className="widget-card">
              <div className="widget-title">
                <Sparkles size={14} />
                <span>Next Best Action</span>
              </div>
              <div className="nba-title">Revise DBMS Transactions</div>
              <div className="nba-desc">
                Revision interval is due based on recent quiz scores and your GATE CS 2026 roadmap.
              </div>
              <div className="nba-meta">
                <span className="badge badge-priority-high">HIGH PRIORITY</span>
                <span className="badge badge-duration">45 MIN</span>
              </div>
            </div>

            {/* Quick Telemetry */}
            <div className="widget-card">
              <div className="widget-title">
                <ShieldCheck size={14} />
                <span>System Security</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Permission Gate</span>
                <span className="stat-val" style={{ color: 'var(--accent-emerald)' }}>STRICT</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">OS Shell Access</span>
                <span className="stat-val" style={{ color: 'var(--accent-rose)' }}>RESTRICTED</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Memory Store</span>
                <span className="stat-val">SQLite Async</span>
              </div>
            </div>

            {/* Today's Focus */}
            <div className="widget-card">
              <div className="widget-title">
                <Clock size={14} />
                <span>Daily Briefing</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Pending Tasks</span>
                <span className="stat-val">3 active</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Target Study</span>
                <span className="stat-val">3.5 hrs</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Completed</span>
                <span className="stat-val" style={{ color: 'var(--accent-cyan)' }}>1.5 hrs (42%)</span>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
