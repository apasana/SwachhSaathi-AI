import { useEffect, useMemo, useRef, useState } from 'react';
import { NavLink, Navigate, Route, Routes } from 'react-router-dom';

import {
  classifyImage,
  createComplaint,
  fetchComplaintList,
  fetchDashboardSummary,
  formatApiError,
  uploadComplaint
} from './api';

const initialFormState = {
  description: '',
  location: '',
  citizen_name: '',
  contact_number: ''
};

const citizenNavItems = [
  { key: 'overview', label: 'Dashboard' },
  { key: 'chatbot', label: 'Chatbot' },
  { key: 'report', label: 'Report Waste' },
  { key: 'leaderboard', label: 'Leaderboard' }
];

const adminNavItems = [
  { key: 'overview', label: 'Dashboard' },
  { key: 'risk', label: 'Risk Mapping' },
  { key: 'upload', label: 'Upload Waste' },
  { key: 'routes', label: 'Route Optimization' },
  { key: 'users', label: 'Users' },
  { key: 'complaints', label: 'Complaints' },
  { key: 'insights', label: 'Admin Panel' }
];

function formatStatusLabel(status) {
  return String(status || 'unknown').replace(/_/g, ' ');
}

function countBy(records, getKey) {
  const counts = new Map();
  records.forEach((record) => {
    const key = getKey(record);
    if (!key) {
      return;
    }
    counts.set(key, (counts.get(key) || 0) + 1);
  });

  return [...counts.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((left, right) => right.value - left.value);
}

function useSectionNavigator(defaultSection) {
  const [activeSection, setActiveSection] = useState(defaultSection);
  const sectionRefs = useRef({});

  const registerSection = (sectionKey) => (node) => {
    if (node) {
      sectionRefs.current[sectionKey] = node;
    }
  };

  const scrollToSection = (sectionKey) => {
    const target = sectionRefs.current[sectionKey];
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveSection(sectionKey);
    }
  };

  return {
    activeSection,
    registerSection,
    scrollToSection,
    setActiveSection
  };
}

function SectionNav({ items, activeSection, onNavigate }) {
  return (
    <nav className="sidebar-nav">
      {items.map((item) => (
        <button
          key={item.key}
          type="button"
          className={`nav-item ${activeSection === item.key ? 'current' : ''}`}
          onClick={() => onNavigate(item.key)}
          aria-pressed={activeSection === item.key}
        >
          {item.label}
        </button>
      ))}
    </nav>
  );
}

function buildAssistantReply(message, complaints, form) {
  const lowerMessage = message.toLowerCase();
  const resolvedCount = complaints.filter((item) => item.status === 'resolved').length;
  const recentTicket = complaints[0]?.ticket_id;
  const topLocation = countBy(complaints, (item) => item.location)[0]?.label;

  if (lowerMessage.includes('track') || lowerMessage.includes('ticket')) {
    return recentTicket
      ? `Latest ticket is ${recentTicket}. Open Complaints, enter the ticket ID, and check its status.`
      : 'No ticket is available yet. Submit one complaint first and then track it from the Complaints panel.';
  }

  if (lowerMessage.includes('report') || lowerMessage.includes('complaint')) {
    return 'Use the Report Waste section. Fill description and location, attach a photo if available, and submit the form.';
  }

  if (lowerMessage.includes('image') || lowerMessage.includes('photo')) {
    return 'Upload the waste image in the Upload Waste section, then run image classification before submitting the complaint.';
  }

  if (lowerMessage.includes('status') || lowerMessage.includes('resolved')) {
    return `There are currently ${resolvedCount} resolved complaints. ${topLocation ? `Most activity is in ${topLocation}.` : 'The dashboard will update as new complaints arrive.'}`;
  }

  if (form.location || form.description) {
    return `I can help with the current report draft for ${form.location || 'your chosen location'}. Add a clear description, then submit the complaint.`;
  }

  return topLocation
    ? `I am monitoring ${complaints.length} complaints. The busiest area right now is ${topLocation}.`
    : 'Ask me how to report waste, classify an image, or track a complaint ticket.';
}

function PortalSwitch() {
  return (
    <div className="portal-switch">
      <NavLink to="/citizen" className={({ isActive }) => `switch-pill ${isActive ? 'active' : ''}`}>
        Citizen Panel
      </NavLink>
      <NavLink to="/admin" className={({ isActive }) => `switch-pill admin ${isActive ? 'active' : ''}`}>
        Admin Panel
      </NavLink>
    </div>
  );
}

function CitizenPanel() {
  const [form, setForm] = useState(initialFormState);
  const [imageFile, setImageFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [complaints, setComplaints] = useState([]);
  const [chatPrompt, setChatPrompt] = useState('');
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      text: 'Ask me how to report waste, classify an image, or track a complaint ticket.'
    }
  ]);

  const { activeSection, registerSection, scrollToSection, setActiveSection } = useSectionNavigator('overview');

  const loadComplaints = async () => {
    try {
      const records = await fetchComplaintList();
      setComplaints(records);
    } catch (error) {
      setStatusMessage(formatApiError(error));
    }
  };

  useEffect(() => {
    loadComplaints();
  }, []);

  const citizenStats = useMemo(() => {
    const resolved = complaints.filter((item) => item.status === 'resolved').length;
    const pending = complaints.filter((item) => item.status !== 'resolved').length;
    return [
      { label: 'Submitted Complaints', value: String(complaints.length).padStart(2, '0'), tag: 'Live' },
      { label: 'Resolved', value: String(resolved).padStart(2, '0'), tag: 'Updated' },
      { label: 'Pending', value: String(pending).padStart(2, '0'), tag: 'In queue' },
      { label: 'Hotspots', value: String(countBy(complaints, (item) => item.location).length).padStart(2, '0'), tag: 'Mapped' }
    ];
  }, [complaints]);

  const recentActivity = useMemo(
    () =>
      complaints.slice(0, 5).map((item) => {
        return `${item.ticket_id}: ${item.description} (${formatStatusLabel(item.status)})`;
      }),
    [complaints]
  );

  const locationLeaderboard = useMemo(
    () => countBy(complaints, (item) => item.location).slice(0, 5),
    [complaints]
  );

  const assistantQuickActions = [
    'How do I file a complaint?',
    'How to report waste quickly?',
    'Which area has the most waste issues?'
  ];

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatusMessage('');
    setSubmitting(true);
    try {
      if (imageFile) {
        await uploadComplaint({ ...form, image: imageFile });
      } else {
        await createComplaint(form);
      }
      setStatusMessage('Complaint submitted successfully.');
      setForm(initialFormState);
      setImageFile(null);
      await loadComplaints();
    } catch (error) {
      setStatusMessage(formatApiError(error));
    } finally {
      setSubmitting(false);
    }
  };

  const handleAskAssistant = (event) => {
    event.preventDefault();
    const message = chatPrompt.trim();
    if (!message) {
      return;
    }

    const assistantReply = buildAssistantReply(message, complaints, form);
    setChatMessages((previous) => [
      ...previous,
      { role: 'user', text: message },
      { role: 'assistant', text: assistantReply }
    ]);
    setChatPrompt('');
    setActiveSection('chatbot');
  };

  return (
    <section className="board citizen-theme">
      <aside className="sidebar">
        <div className="brand">SwachhSaathi AI</div>
        <p className="sidebar-note">Citizen portal for filing, tracking, and analysing waste issues.</p>
        <SectionNav items={citizenNavItems} activeSection={activeSection} onNavigate={scrollToSection} />
        <div className="upload-card">
          <h4>Quick Reporting</h4>
          <p>Just upload a photo inside Report Waste and submit. Admin handles classification and verification.</p>
        </div>
      </aside>

      <main className="content">
        <header className="content-head">
          <div>
            <h1>Welcome to SwachhSaathi AI</h1>
            <p>Manage complaints, preview AI waste classification, and track live updates from the same screen.</p>
          </div>
          <span>User View</span>
        </header>

        <section ref={registerSection('overview')} className="section-card" data-section="overview">
          <div className="section-heading">
            <div>
              <h2>Citizen Overview</h2>
              <p>Live complaint counts and hotspot coverage from the backend.</p>
            </div>
          </div>

          <div className="stat-grid">
            {citizenStats.map((card) => (
              <article key={card.label} className="stat-card">
                <small>{card.label}</small>
                <strong>{card.value}</strong>
                <span>{card.tag}</span>
              </article>
            ))}
          </div>

          <div className="dual-grid">
            <article className="panel-list soft-panel">
              <h3>Recent Activity</h3>
              {recentActivity.length === 0 ? <p>No complaints yet.</p> : null}
              {recentActivity.map((item) => (
                <p key={item}>{item}</p>
              ))}
            </article>

            <article className="panel-list soft-panel">
              <h3>Top Complaint Areas</h3>
              {locationLeaderboard.length === 0 ? <p>No location data yet.</p> : null}
              {locationLeaderboard.map((item, index) => (
                <div key={item.label} className="leader-row">
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <div>
                    <strong>{item.label}</strong>
                    <p>{item.value} complaint{item.value === 1 ? '' : 's'}</p>
                  </div>
                </div>
              ))}
            </article>
          </div>
        </section>

        <section ref={registerSection('chatbot')} className="section-card" data-section="chatbot">
          <div className="section-heading">
            <div>
              <h2>Chatbot</h2>
              <p>Simple guided assistant for complaint filing and ticket tracking.</p>
            </div>
            <div className="quick-actions">
              {assistantQuickActions.map((prompt) => (
                <button key={prompt} type="button" className="chip" onClick={() => setChatPrompt(prompt)}>
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          <div className="assistant-shell">
            <div className="assistant-feed">
              {chatMessages.map((message, index) => (
                <div key={`${message.role}-${index}-${message.text}`} className={`chat-bubble ${message.role}`}>
                  {message.text}
                </div>
              ))}
            </div>

            <form className="assistant-form" onSubmit={handleAskAssistant}>
              <input
                value={chatPrompt}
                onChange={(event) => setChatPrompt(event.target.value)}
                placeholder="Ask about reporting, tracking, or waste classification"
              />
              <button type="submit">Send</button>
            </form>
          </div>
        </section>

        <section ref={registerSection('report')} className="section-card" data-section="report">
          <div className="section-heading">
            <div>
              <h2>Report Waste Issue</h2>
              <p>Submit location details with optional image. Authority panel will classify and verify the waste image.</p>
            </div>
          </div>

          <form className="report-form" onSubmit={handleSubmit}>
            <input
              name="description"
              placeholder="Description"
              value={form.description}
              onChange={handleChange}
              required
              minLength={3}
            />
            <input name="location" placeholder="Location" value={form.location} onChange={handleChange} required minLength={2} />
            <input name="citizen_name" placeholder="Citizen Name (optional)" value={form.citizen_name} onChange={handleChange} />
            <input
              name="contact_number"
              placeholder="Contact Number (optional)"
              value={form.contact_number}
              onChange={handleChange}
            />
            <input
              type="file"
              accept="image/*"
              onChange={(event) => {
                const file = event.target.files?.[0] || null;
                setImageFile(file);
              }}
            />
            <button type="submit" disabled={submitting}>
              {submitting ? 'Submitting...' : 'Submit Complaint'}
            </button>
          </form>
        </section>

        <section ref={registerSection('leaderboard')} className="section-card" data-section="leaderboard">
          <div className="section-heading">
            <div>
              <h2>Leaderboard</h2>
              <p>Locations with the highest complaint volume.</p>
            </div>
          </div>

          <div className="leaderboard-grid">
            {locationLeaderboard.length === 0 ? <p>No leaderboard data yet.</p> : null}
            {locationLeaderboard.map((item, index) => (
              <article key={item.label} className="leaderboard-card">
                <span>{String(index + 1).padStart(2, '0')}</span>
                <strong>{item.label}</strong>
                <p>{item.value} complaint{item.value === 1 ? '' : 's'}</p>
              </article>
            ))}
          </div>
        </section>

        {statusMessage ? <p className="status-line">{statusMessage}</p> : null}
      </main>
    </section>
  );
}

function AdminPanel() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [adminImageFile, setAdminImageFile] = useState(null);
  const [adminClassifying, setAdminClassifying] = useState(false);
  const [adminClassifyResult, setAdminClassifyResult] = useState(null);
  const { activeSection, registerSection, scrollToSection, setActiveSection } = useSectionNavigator('overview');

  const loadDashboard = async () => {
    setErrorMessage('');
    setLoading(true);
    try {
      const payload = await fetchDashboardSummary();
      setSummary(payload);
    } catch (error) {
      setErrorMessage(formatApiError(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const adminCards = useMemo(() => {
    if (!summary?.metrics) {
      return [
        { label: 'Active Bins', value: 0, tone: 'good' },
        { label: 'High Risk', value: 0, tone: 'warn' },
        { label: 'Pending', value: 0, tone: 'info' },
        { label: 'Complaints', value: 0, tone: 'danger' }
      ];
    }

    return [
      {
        label: 'Active Bins',
        value: Math.max(summary.metrics.total_complaints - summary.metrics.high_risk_complaints, 0),
        tone: 'good'
      },
      { label: 'High Risk', value: summary.metrics.high_risk_complaints, tone: 'warn' },
      { label: 'Pending', value: summary.metrics.pending_complaints, tone: 'info' },
      { label: 'Complaints', value: summary.metrics.total_complaints, tone: 'danger' }
    ];
  }, [summary]);

  const adminTable = summary?.recent_complaints || [];
  const alertItems = summary?.predicted_alerts || [];

  const routePlan = useMemo(() => {
    return countBy(adminTable, (item) => item.location).slice(0, 5);
  }, [adminTable]);

  const reporterStats = useMemo(() => {
    return countBy(adminTable, (item) => item.citizen_name || item.contact_number || 'Anonymous').slice(0, 5);
  }, [adminTable]);

  const statusBreakdown = useMemo(() => {
    const breakdown = summary?.status_distribution || {};
    return Object.entries(breakdown)
      .map(([label, value]) => ({ label, value }))
      .sort((left, right) => right.value - left.value);
  }, [summary]);

  const riskBreakdown = useMemo(() => {
    const breakdown = summary?.risk_distribution || {};
    return Object.entries(breakdown)
      .map(([label, value]) => ({ label, value }))
      .sort((left, right) => right.value - left.value);
  }, [summary]);

  const refreshDashboard = () => {
    setActiveSection('overview');
    loadDashboard();
  };

  const handleAdminClassify = async () => {
    if (!adminImageFile) {
      setErrorMessage('Please choose an image first in Upload Waste section.');
      scrollToSection('upload');
      return;
    }

    setErrorMessage('');
    setAdminClassifying(true);
    try {
      const result = await classifyImage(adminImageFile);
      setAdminClassifyResult(result);
    } catch (error) {
      setErrorMessage(formatApiError(error));
    } finally {
      setAdminClassifying(false);
    }
  };

  return (
    <section className="board admin-theme">
      <aside className="sidebar">
        <div className="brand">SwachhSaathi AI</div>
        <p className="sidebar-note">Authority portal for risks, routes, users, and complaint monitoring.</p>
        <SectionNav items={adminNavItems} activeSection={activeSection} onNavigate={scrollToSection} />
        <div className="legend">
          <h4>Smart Map</h4>
          <p>Low</p>
          <p>Medium</p>
          <p>High</p>
          <button type="button" className="small-btn" onClick={handleAdminClassify} disabled={adminClassifying}>
            {adminClassifying ? 'Classifying...' : 'Classify Image'}
          </button>
          <button type="button" className="small-btn" onClick={refreshDashboard} disabled={loading}>
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </aside>

      <main className="content">
        <header className="content-head">
          <div>
            <h1>Dashboard</h1>
            <p>Monitor complaint flow, routing hotspots, and live authority metrics.</p>
          </div>
          <span>Authority View</span>
        </header>

        <section ref={registerSection('overview')} className="section-card" data-section="overview">
          <div className="section-heading">
            <div>
              <h2>Overview</h2>
              <p>Current metrics from the dashboard summary endpoint.</p>
            </div>
            <button type="button" className="small-btn" onClick={refreshDashboard} disabled={loading}>
              {loading ? 'Refreshing...' : 'Refresh Data'}
            </button>
          </div>

          <div className="admin-kpi-grid">
            {adminCards.map((kpi) => (
              <article key={kpi.label} className={`kpi ${kpi.tone}`}>
                <small>{kpi.label}</small>
                <strong>{kpi.value}</strong>
              </article>
            ))}
          </div>
        </section>

        <section ref={registerSection('risk')} className="section-card" data-section="risk">
          <div className="section-heading">
            <div>
              <h2>Risk Mapping</h2>
              <p>Visual cues for the current complaint heatmap and risk alerts.</p>
            </div>
          </div>

          <article className="smart-map">
            <div className="dot yellow" />
            <div className="dot green" />
            <div className="dot red" />
            <div className="dot green two" />
            <div className="dot yellow two" />
          </article>

          <div className="dual-grid">
            <article className="panel-list soft-panel">
              <h3>Predicted Alerts</h3>
              {alertItems.length === 0 ? <p>No alerts right now.</p> : null}
              {alertItems.map((item) => (
                <div key={`${item.ticket_id}-${item.location}`} className="alert-row">
                  <strong>{item.location}</strong>
                  <p>{item.alert}</p>
                  <span>{item.risk_level}</span>
                </div>
              ))}
            </article>

            <article className="panel-list soft-panel">
              <h3>Status Breakdown</h3>
              {statusBreakdown.length === 0 ? <p>No status breakdown yet.</p> : null}
              {statusBreakdown.map((item) => (
                <div key={item.label} className="leader-row">
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
              <h3 style={{ marginTop: '18px' }}>Risk Breakdown</h3>
              {riskBreakdown.length === 0 ? <p>No risk data yet.</p> : null}
              {riskBreakdown.map((item) => (
                <div key={item.label} className="leader-row">
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </article>
          </div>
        </section>

        <section ref={registerSection('upload')} className="section-card" data-section="upload">
          <div className="section-heading">
            <div>
              <h2>Upload Waste</h2>
              <p>Admins can classify waste images directly for verification and monitoring.</p>
            </div>
            <button className="cta" type="button" onClick={handleAdminClassify} disabled={adminClassifying}>
              {adminClassifying ? 'Analyzing...' : 'Analyze Image'}
            </button>
          </div>

          <div className="upload-preview">
            <div>
              <h3>Selected File</h3>
              <p>{adminImageFile ? adminImageFile.name : 'No image selected yet.'}</p>
            </div>
          </div>

          <form className="report-form" onSubmit={(event) => event.preventDefault()}>
            <input
              type="file"
              accept="image/*"
              onChange={(event) => {
                const file = event.target.files?.[0] || null;
                setAdminImageFile(file);
              }}
            />
            <button type="button" onClick={handleAdminClassify} disabled={adminClassifying}>
              {adminClassifying ? 'Classifying...' : 'Classify Image'}
            </button>
          </form>

          {adminClassifyResult ? (
            <article className="panel-list result-panel">
              <h3>AI Classification</h3>
              <p>Type: {adminClassifyResult.waste_type}</p>
              <p>Confidence: {Number(adminClassifyResult.confidence || 0).toFixed(2)}</p>
              <p>Source: {adminClassifyResult.source}</p>
            </article>
          ) : null}
        </section>

        <section ref={registerSection('routes')} className="section-card" data-section="routes">
          <div className="section-heading">
            <div>
              <h2>Route Optimization</h2>
              <p>Top pickup zones derived from recent complaint locations.</p>
            </div>
          </div>

          <div className="route-grid">
            {routePlan.length === 0 ? <p>No route suggestions yet.</p> : null}
            {routePlan.map((item, index) => (
              <article key={item.label} className="route-card">
                <span>Stop {index + 1}</span>
                <strong>{item.label}</strong>
                <p>{item.value} scheduled pickup{item.value === 1 ? '' : 's'}</p>
              </article>
            ))}
          </div>
        </section>

        <section ref={registerSection('users')} className="section-card" data-section="users">
          <div className="section-heading">
            <div>
              <h2>Users</h2>
              <p>Most active reporters from the current complaint stream.</p>
            </div>
          </div>

          <div className="route-grid">
            {reporterStats.length === 0 ? <p>No reporter data yet.</p> : null}
            {reporterStats.map((item) => (
              <article key={item.label} className="route-card">
                <span>Reporter</span>
                <strong>{item.label}</strong>
                <p>{item.value} complaint{item.value === 1 ? '' : 's'}</p>
              </article>
            ))}
          </div>
        </section>

        <section ref={registerSection('complaints')} className="section-card" data-section="complaints">
          <div className="section-heading">
            <div>
              <h2>Complaints</h2>
              <p>Full complaint table for operational review.</p>
            </div>
          </div>

          <article className="table-shell">
            <h3>Detailed Complaints</h3>
            <div className="table-head">
              <span>Reporter</span>
              <span>Detail</span>
              <span>Location</span>
              <span>Status</span>
            </div>
            {adminTable.length === 0 ? <p>No complaints found.</p> : null}
            {adminTable.map((row) => (
              <div className="table-row" key={`${row.ticket_id}-${row.location}`}>
                <span>{row.citizen_name || 'Citizen'}</span>
                <span>{row.description}</span>
                <span>{row.location}</span>
                <span className={`status ${String(row.status).replace('_', '-').toLowerCase()}`}>{row.status}</span>
              </div>
            ))}
          </article>
        </section>

        <section ref={registerSection('insights')} className="section-card" data-section="insights">
          <div className="section-heading">
            <div>
              <h2>Admin Panel</h2>
              <p>Quick operational summary and reload controls.</p>
            </div>
          </div>

          <div className="dual-grid">
            <article className="panel-list soft-panel">
              <h3>Summary Notes</h3>
              <p>Total complaints: {summary?.metrics?.total_complaints || 0}</p>
              <p>Average fill time: {Number(summary?.metrics?.average_fill_time_hours || 0).toFixed(2)} hours</p>
              <p>Resolved: {summary?.metrics?.resolved_complaints || 0}</p>
            </article>

            <article className="panel-list soft-panel">
              <h3>Action</h3>
              <p>Use refresh to fetch the latest backend summary after new complaints are submitted.</p>
              <button type="button" className="small-btn" onClick={refreshDashboard} disabled={loading}>
                {loading ? 'Refreshing...' : 'Refresh Data'}
              </button>
            </article>
          </div>
        </section>

        {errorMessage ? <p className="status-line error">{errorMessage}</p> : null}
      </main>
    </section>
  );
}

export default function App() {
  return (
    <div className="app-shell">
      <PortalSwitch />
      <Routes>
        <Route path="/" element={<Navigate to="/citizen" replace />} />
        <Route path="/citizen" element={<CitizenPanel />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </div>
  );
}
