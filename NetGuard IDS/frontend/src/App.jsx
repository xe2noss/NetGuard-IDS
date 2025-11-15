import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

// --- Configuration ---
// URLs are relative because Nginx will proxy them.
const API_URL = '/api'; 
// Construct WebSocket URL from window location.
const WS_URL = (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + 
               window.location.host + 
               '/api/ws';

const SEVERITY_COLORS = {
  CRITICAL: '#dc2626', // red-600
  HIGH: '#f97316',     // orange-500
  MEDIUM: '#eab308',   // yellow-500
  LOW: '#22c55e'      // green-500
};

// --- Main App Component ---
function App() {
  const [alerts, setAlerts] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [activeTab, setActiveTab] = useState('alerts');
  const [ws, setWs] = useState(null);
  const [systemStatus, setSystemStatus] = useState('Connecting...');

  useEffect(() => {
    fetchAlerts();
    fetchStatistics();
    connectWebSocket();

    const statsInterval = setInterval(fetchStatistics, 10000); // Refresh stats
    
    return () => {
      clearInterval(statsInterval);
      if (ws) ws.close();
    };
  }, []);

  const connectWebSocket = () => {
    const socket = new WebSocket(WS_URL);
    
    socket.onopen = () => setSystemStatus('Connected');
    
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'new_alert') {
        setAlerts(prev => [message.data, ...prev]);
        fetchStatistics(); // Refresh stats on new alert
      }
    };
    
    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setSystemStatus('Error');
    };

    socket.onclose = () => {
      setSystemStatus('Disconnected. Retrying...');
      setTimeout(connectWebSocket, 5000); // Auto-reconnect
    };
    
    setWs(socket);
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/alerts?limit=100`);
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_URL}/statistics`);
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const acknowledgeAlert = async (alertId) => {
    try {
      await fetch(`${API_URL}/alerts/${alertId}/acknowledge`, { method: 'POST' });
      setAlerts(prev => 
        prev.map(alert => 
          alert.id === alertId ? { ...alert, acknowledged: true } : alert
        )
      );
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
        
        <Header />
        <NavBar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main>
          {activeTab === 'alerts' && <AlertFeed alerts={alerts} onAcknowledge={acknowledgeAlert} />}
          {activeTab === 'dashboard' && <Dashboard statistics={statistics} />}
          {activeTab === 'status' && <SystemStatus status={systemStatus} />}
        </main>

      </div>
    </div>
  );
}

// --- Sub-Components ---

const Header = () => (
  <header style={{ background: 'white', borderRadius: '12px', padding: '24px', marginBottom: '20px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
    <h1 style={{ margin: 0, fontSize: '32px', color: '#1f2937', fontWeight: 'bold' }}>
      🛡️ NetGuard IDS
    </h1>
    <p style={{ margin: '8px 0 0 0', color: '#6b7280' }}>
      Real-time Network Intrusion Detection System
    </p>
  </header>
);

const NavBar = ({ activeTab, setActiveTab }) => (
  <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
    {['alerts', 'dashboard', 'status'].map(tab => (
      <button
        key={tab}
        onClick={() => setActiveTab(tab)}
        style={{
          padding: '12px 24px',
          background: activeTab === tab ? 'white' : 'rgba(255,255,255,0.3)',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: activeTab === tab ? 'bold' : 'normal',
          color: activeTab === tab ? '#667eea' : 'white',
          fontSize: '16px',
          transition: 'all 0.3s'
        }}
      >
        {tab.charAt(0).toUpperCase() + tab.slice(1)}
      </button>
    ))}
  </div>
);

const AlertFeed = ({ alerts, onAcknowledge }) => (
  <div style={styles.card}>
    <h2 style={styles.cardTitle}>Live Alert Feed</h2>
    <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
      {alerts.length === 0 ? (
        <p style={{ color: '#6b7280', textAlign: 'center', padding: '40px' }}>
          No alerts detected. System is monitoring...
        </p>
      ) : (
        alerts.map(alert => <AlertItem key={alert.id} alert={alert} onAcknowledge={onAcknowledge} />)
      )}
    </div>
  </div>
);

const AlertItem = ({ alert, onAcknowledge }) => (
  <div
    style={{
      background: alert.acknowledged ? '#f9fafb' : '#fef2f2',
      border: `2px solid ${SEVERITY_COLORS[alert.severity] || '#e5e7eb'}`,
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '12px'
    }}
  >
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px', flexWrap: 'wrap' }}>
          <span
            style={{
              background: SEVERITY_COLORS[alert.severity],
              color: 'white',
              padding: '4px 12px',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
          >
            {alert.severity}
          </span>
          <span style={{ fontWeight: 'bold', fontSize: '18px', color: '#1f2937' }}>
            {alert.threat_type}
          </span>
          <span style={{ color: '#6b7280', fontSize: '14px' }}>
            {new Date(alert.timestamp).toLocaleString()}
          </span>
        </div>
        <p style={{ margin: '8px 0', color: '#374151' }}>{alert.description}</p>
        <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#6b7280', wordBreak: 'break-all' }}>
          <span>Source: <strong>{alert.source_ip}</strong></span>
          <span>→</span>
          <span>Destination: <strong>{alert.dest_ip}</strong></span>
        </div>
      </div>
      {!alert.acknowledged && (
        <button
          onClick={() => onAcknowledge(alert.id)}
          style={{
            padding: '8px 16px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Acknowledge
        </button>
      )}
    </div>
  </div>
);

const Dashboard = ({ statistics }) => (
  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
    {statistics ? (
      <>
        <StatSummary stats={statistics} />
        <ChartCard title="Top Attacking IPs">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={statistics.top_attackers}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ip" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Alerts by Type">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statistics.alerts_by_type}
                dataKey="count"
                nameKey="type"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {statistics.alerts_by_type.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={Object.values(SEVERITY_COLORS)[index % Object.values(SEVERITY_COLORS).length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </>
    ) : (
      <div style={styles.card}>Loading statistics...</div>
    )}
  </div>
);

const StatSummary = ({ stats }) => (
  <div style={{ ...styles.card, gridColumn: '1 / -1' }}>
    <h3 style={styles.cardTitle}>Statistics Summary (Last 24h)</h3>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '20px' }}>
      <StatBox label="Total Alerts" value={stats.total_alerts} color="#667eea" />
      <StatBox label="Unique Attackers" value={stats.top_attackers.length} color="#dc2626" />
      <StatBox label="Threat Types" value={stats.alerts_by_type.length} color="#22c55e" />
    </div>
  </div>
);

const StatBox = ({ label, value, color }) => (
  <div style={{ textAlign: 'center', padding: '20px', background: '#f9fafb', borderRadius: '8px' }}>
    <div style={{ fontSize: '36px', fontWeight: 'bold', color: color }}>
      {value}
    </div>
    <div style={{ color: '#6b7280', marginTop: '8px' }}>{label}</div>
  </div>
);

const ChartCard = ({ title, children }) => (
  <div style={styles.card}>
    <h3 style={styles.cardTitle}>{title}</h3>
    {children}
  </div>
);

const SystemStatus = ({ status }) => (
  <div style={styles.card}>
    <h2 style={styles.cardTitle}>System Status</h2>
    <div style={{ display: 'grid', gap: '16px' }}>
      <StatusItem label="Packet Capture" status="ACTIVE" color="#22c55e" />
      <StatusItem label="Detection Engine" status="RUNNING" color="#22c55e" />
      <StatusItem label="Database Connection" status="CONNECTED" color="#22c55e" />
      <StatusItem 
        label="WebSocket" 
        status={status} 
        color={status === 'Connected' ? '#22c55e' : '#dc2626'} 
      />
    </div>
  </div>
);

const StatusItem = ({ label, status, color }) => (
  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
    <span style={{ fontWeight: 'bold', color: '#1f2937' }}>{label}</span>
    <span style={{ color: color, fontWeight: 'bold' }}>● {status}</span>
  </div>
);

// --- Styling ---
const styles = {
  card: {
    background: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
  },
  cardTitle: {
    marginTop: 0,
    color: '#1f2937'
  }
};

export default App;