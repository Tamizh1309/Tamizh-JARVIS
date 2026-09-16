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
  ShieldCheck,
  Plus,
  CheckCircle2
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

  // Dynamic Backend Data States
  const [nextBestAction, setNextBestAction] = useState({
    title: "Loading recommendation...",
    reason: "Connecting to JARVIS Decision Engine...",
    priority: "HIGH",
    duration_minutes: 45
  });

  const [dailyBriefing, setDailyBriefing] = useState({
    pending_tasks_count: 0,
    target_study_hours: 3.5,
    today_study_hours: 0,
    completion_percentage: 0
  });

  const [tasksList, setTasksList] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');

  // Fetch telemetry and tasks from backend
  const refreshTelemetry = async () => {
    try {
      // 1. Fetch Health
      const healthRes = await fetch('/api/health');
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHealth(healthData);
        setAiState('Online');
      }

      // 2. Fetch Next Best Action from Backend
      const nbaRes = await fetch('/api/study/next-action');
      if (nbaRes.ok) {
        const nbaData = await nbaRes.json();
        if (nbaData.success) {
          setNextBestAction({
            title: nbaData.title || "Revise Core Topic",
            reason: nbaData.reason || nbaData.description || "Calculated based on study priority.",
            priority: nbaData.priority || "HIGH",
            duration_minutes: nbaData.duration_minutes || 45
          });
        }
      }

      // 3. Fetch Daily Briefing from Backend
      const briefingRes = await fetch('/api/study/briefing');
      if (briefingRes.ok) {
        const briefingData = await briefingRes.json();
        if (briefingData.success) {
          setDailyBriefing({
            pending_tasks_count: briefingData.pending_tasks_count || 0,
            target_study_hours: briefingData.target_study_hours || 3.5,
            today_study_hours: briefingData.today_study_hours || 0,
            completion_percentage: briefingData.completion_percentage || 0
          });
        }
      }

      // 4. Fetch Tasks List
      const tasksRes = await fetch('/api/tasks');
      if (tasksRes.ok) {
        const tasksData = await tasksRes.json();
        if (tasksData.success) {
          setTasksList(tasksData.tasks || []);
        }
      }
    } catch (err) {
      setAiState('Live Web Demo');
    }
  };

  useEffect(() => {
    refreshTelemetry();
    const interval = setInterval(refreshTelemetry, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputVal.trim()) return;

    const userMessageText = inputVal;
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: userMessageText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputVal('');
    setAiState('Thinking');

    try {
      // Call Real Backend POST /api/chat
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessageText,
          context: {}
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const result = await response.json();
      setAiState('Responding');

      setTimeout(() => {
        setAiState('Online');
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'jarvis',
            text: result.response,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            intent: result.intent,
            toolUsed: result.toolUsed
          }
        ]);

        // If action updated tasks or study, refresh telemetry
        if (result.memoryUpdated || result.toolUsed !== 'none') {
          refreshTelemetry();
        }
      }, 300);

    } catch (error) {
      setAiState('Online');
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'jarvis',
          text: `I received your request: "${userMessageText}". Real backend connection: ${error.message}`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          intent: 'ERROR'
        }
      ]);
    }
  };

  const handleCreateTaskDirect = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    try {
      const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTaskTitle, priority: 'MEDIUM' })
      });
      if (res.ok) {
        setNewTaskTitle('');
        refreshTelemetry();
      }
    } catch (err) {
      console.error(err);
    }
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
              Provider: {health?.ai_provider || 'Active Engine'}
            </div>
          </div>
        </header>

        {/* Tab Content Rendering */}
        {activeTab === 'tasks' && (
          <div className="tab-view-container">
            <div>
              <h2 className="tab-header-title"><CheckSquare size={22} color="var(--accent-cyan)" /> Task Engine</h2>
              <p className="tab-header-desc">Manage pending assignments, deadlines, and completed milestones.</p>
            </div>

            <form onSubmit={handleCreateTaskDirect} className="task-form">
              <input 
                type="text" 
                className="form-input" 
                placeholder="Add a new task (e.g., 'Solve 3 Dynamic Programming problems')..."
                value={newTaskTitle}
                onChange={e => setNewTaskTitle(e.target.value)}
              />
              <button type="submit" className="form-btn">
                <Plus size={16} /> Add Task
              </button>
            </form>

            <div className="card-grid">
              {tasksList.map(task => (
                <div key={task.id} className="item-card">
                  <div className="item-card-title">
                    <span>{task.title}</span>
                    <span className={`badge ${task.priority === 'HIGH' ? 'badge-priority-high' : 'badge-duration'}`}>
                      {task.priority}
                    </span>
                  </div>
                  <div className="item-card-desc">{task.description || "Milestone task in backlog."}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 'auto', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    <span>Status: {task.status}</span>
                    <span>ID #{task.id}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'study' && (
          <div className="tab-view-container">
            <div>
              <h2 className="tab-header-title"><BookOpen size={22} color="var(--accent-cyan)" /> Study & GATE Preparation</h2>
              <p className="tab-header-desc">Target: GATE Computer Science 2026. Daily target: 3.5 study hours.</p>
            </div>
            <div className="card-grid">
              <div className="item-card">
                <div className="item-card-title">Priority Weak Topics</div>
                <div className="item-card-desc">
                  • DBMS Transactions & Concurrency Control<br />
                  • Dynamic Programming Algorithms<br />
                  • TCP Congestion Control & Sliding Window
                </div>
              </div>
              <div className="item-card">
                <div className="item-card-title">Target Subjects</div>
                <div className="item-card-desc">
                  • Database Management Systems<br />
                  • Operating Systems<br />
                  • Computer Networks<br />
                  • Theory of Computation
                </div>
              </div>
              <div className="item-card">
                <div className="item-card-title">Daily Progress</div>
                <div className="item-card-desc">
                  Completed: {dailyBriefing.today_study_hours} hrs / {dailyBriefing.target_study_hours} hrs target ({dailyBriefing.completion_percentage}%)
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'dsa' && (
          <div className="tab-view-container">
            <div>
              <h2 className="tab-header-title"><Code2 size={22} color="var(--accent-cyan)" /> DSA Practice Lab</h2>
              <p className="tab-header-desc">Master data structures, algorithmic complexity, and problem solving patterns.</p>
            </div>
            <div className="card-grid">
              <div className="item-card">
                <div className="item-card-title">Binary Search <span className="badge badge-duration">O(log N)</span></div>
                <div className="item-card-desc">Divide-and-conquer on sorted arrays. Optimal for search bounds and monotonic functions.</div>
              </div>
              <div className="item-card">
                <div className="item-card-title">Dynamic Programming <span className="badge badge-priority-high">Weak Topic</span></div>
                <div className="item-card-desc">Overlapping subproblems and optimal substructure. Focus on 0/1 Knapsack, LCS, and Matrix Chain.</div>
              </div>
              <div className="item-card">
                <div className="item-card-title">Graphs & Trees <span className="badge badge-duration">Core</span></div>
                <div className="item-card-desc">Dijkstra's shortest path, BFS/DFS traversals, and topological sorting.</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'career' && (
          <div className="tab-view-container">
            <div>
              <h2 className="tab-header-title"><Briefcase size={22} color="var(--accent-cyan)" /> Career Roadmap</h2>
              <p className="tab-header-desc">Primary Objective: GATE CS 2026 & Software Engineering Mastery.</p>
            </div>
            <div className="card-grid">
              <div className="item-card">
                <div className="item-card-title">Primary Milestone</div>
                <div className="item-card-desc">Top percentile in GATE CS 2026 with deep conceptual mastery across CS core subjects.</div>
              </div>
              <div className="item-card">
                <div className="item-card-title">Skill Targets</div>
                <div className="item-card-desc">Advanced Python, System Architecture, Distributed Concepts, Fast Problem Solving in LeetCode.</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'memory' && (
          <div className="tab-view-container">
            <div>
              <h2 className="tab-header-title"><Database size={22} color="var(--accent-cyan)" /> Long-Term Memory</h2>
              <p className="tab-header-desc">Persistent SQLite memory store for user facts, tasks, and study records.</p>
            </div>
            <div className="card-grid">
              <div className="item-card">
                <div className="item-card-title">Storage Driver</div>
                <div className="item-card-desc">SQLite Async via <code>aiosqlite</code>. Local file <code>jarvis.db</code>.</div>
              </div>
              <div className="item-card">
                <div className="item-card-title">Active Backlog</div>
                <div className="item-card-desc">{dailyBriefing.pending_tasks_count} pending tasks recorded in relational database.</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="tab-view-container">
            <div>
              <h2 className="tab-header-title"><Settings size={22} color="var(--accent-cyan)" /> Settings & Security</h2>
              <p className="tab-header-desc">System security, risk classifier policies, and AI provider configuration.</p>
            </div>
            <div className="card-grid">
              <div className="item-card">
                <div className="item-card-title">Risk Classifier Policy</div>
                <div className="item-card-desc">
                  • LOW: Auto-permitted (Read queries, NBA calculation)<br />
                  • MEDIUM: Auto-logged (Task create/update)<br />
                  • HIGH: Requires explicit confirmation<br />
                  • CRITICAL: Blocked (Shell / destructive OS execution)
                </div>
              </div>
              <div className="item-card">
                <div className="item-card-title">AI Provider Config</div>
                <div className="item-card-desc">
                  Active Provider: <strong>{health?.ai_provider || 'fallback'}</strong><br />
                  Supported: Gemini API, Ollama Local, Fallback Deterministic Engine.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Master Dashboard / Chat Grid */}
        {(activeTab === 'chat' || activeTab === 'dashboard') && (
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
                      <div className="message-body" style={{ whiteSpace: 'pre-wrap' }}>
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
                        {msg.toolUsed && msg.toolUsed !== 'none' && (
                          <>
                            <span>•</span>
                            <span style={{ color: 'var(--accent-purple)' }}>tool: {msg.toolUsed}</span>
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
                    placeholder="Message JARVIS... (e.g., 'What should I study now?' or 'Plan my GATE revision')"
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
              {/* Next Best Action Card (Populated by Backend) */}
              <div className="widget-card">
                <div className="widget-title">
                  <Sparkles size={14} />
                  <span>Next Best Action</span>
                </div>
                <div className="nba-title">{nextBestAction.title}</div>
                <div className="nba-desc">
                  {nextBestAction.reason}
                </div>
                <div className="nba-meta">
                  <span className={`badge ${nextBestAction.priority === 'HIGH' ? 'badge-priority-high' : 'badge-duration'}`}>
                    {nextBestAction.priority} PRIORITY
                  </span>
                  <span className="badge badge-duration">
                    {nextBestAction.duration_minutes} MIN
                  </span>
                </div>
              </div>

              {/* System Security */}
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

              {/* Daily Briefing (Populated by Backend) */}
              <div className="widget-card">
                <div className="widget-title">
                  <Clock size={14} />
                  <span>Daily Briefing</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Pending Tasks</span>
                  <span className="stat-val">{dailyBriefing.pending_tasks_count} active</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Target Study</span>
                  <span className="stat-val">{dailyBriefing.target_study_hours} hrs</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Completed</span>
                  <span className="stat-val" style={{ color: 'var(--accent-cyan)' }}>
                    {dailyBriefing.today_study_hours} hrs ({dailyBriefing.completion_percentage}%)
                  </span>
                </div>
              </div>
            </aside>
          </div>
        )}
      </div>
    </div>
  );
}
