import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Activity, AlertTriangle, Check, Terminal, RefreshCw, Clock } from 'lucide-react';

const generateMockData = (minutes) => { 
  return Array.from({ length: minutes }, (_, i) => ({ 
    time: `${String(Math.floor(i / 60)).padStart(2, '0')}:${String(i % 60).padStart(2, '0')}`, 
    oracle: Math.floor(Math.random() * 100), 
    conjuror: Math.floor(Math.random() * 100), 
    gemini: Math.floor(Math.random() * 100), 
    aria: Math.floor(Math.random() * 100), 
    capri: Math.floor(Math.random() * 100), 
  })); 
};

const mockTasks = [ 
  { id: 1, component: 'Oracle', description: 'Processing high-level directives', status: 'active', startTime: '12:30:05', duration: '00:05:22' }, 
  { id: 2, component: 'Conjuror', description: 'Interpreting Oracle vision #2853', status: 'active', startTime: '12:31:15', duration: '00:04:12' }, 
  { id: 3, component: 'Gemini', description: 'Strategic planning for Legio Alpha', status: 'active', startTime: '12:32:45', duration: '00:02:42' }, 
  { id: 4, component: 'Aria', description: 'Knowledge aggregation from sector 7', status: 'complete', startTime: '12:29:10', duration: '00:03:55' }, 
  { id: 5, component: 'Capri', description: 'Initialize Legio Alpha units', status: 'active', startTime: '12:33:22', duration: '00:01:05' }, 
  { id: 6, component: 'Capri', description: 'Allocate cloud resources', status: 'pending', startTime: '-', duration: '-' }, 
  { id: 7, component: 'Capri', description: 'Report status to Aria', status: 'pending', startTime: '-', duration: '-' }, 
];

const mockAlerts = [ 
  { id: 1, component: 'Oracle', severity: 'info', message: 'New directive received', timestamp: '12:30:00' }, 
  { id: 2, component: 'Aria', severity: 'warning', message: 'Knowledge synchronization slower than expected', timestamp: '12:31:23' }, 
  { id: 3, component: 'Capri', severity: 'info', message: 'Task #5 started', timestamp: '12:33:22' }, 
];

const mockLogs = [
  { id: 1, component: 'System', message: 'Triumvirate system initialized', timestamp: '12:29:00' },
  { id: 2, component: 'Oracle', message: 'Directive #458 received from command', timestamp: '12:30:00' },
  { id: 3, component: 'Conjuror', message: 'Parsing vision data streams', timestamp: '12:31:15' },
  { id: 4, component: 'Aria', message: 'Knowledge sync rate: 85%', timestamp: '12:31:23' },
  { id: 5, component: 'Gemini', message: 'Legio Alpha strategy computation complete', timestamp: '12:32:45' },
  { id: 6, component: 'Capri', message: 'Initializing Legio Alpha units 1-12', timestamp: '12:33:22' },
];

const componentColors = { 
  oracle: '#8884d8', 
  conjuror: '#82ca9d', 
  gemini: '#ffc658', 
  aria: '#ff8042', 
  capri: '#0088fe', 
};

const statusIcons = {
  active: <Activity className="text-green-500" size={16} />,
  complete: <Check className="text-blue-500" size={16} />,
  pending: <Clock className="text-gray-500" size={16} />,
  warning: <AlertTriangle className="text-yellow-500" size={16} />,
  error: <AlertTriangle className="text-red-500" size={16} />,
};

export default function OracleMonitoringDashboard() { 
  const [performanceData, setPerformanceData] = useState([]);
  const [tasks, setTasks] = useState(mockTasks);
  const [alerts, setAlerts] = useState(mockAlerts);
  const [logs, setLogs] = useState(mockLogs);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState([]);
  const [simSpeed, setSimSpeed] = useState(1);
  const [systemState, setSystemState] = useState({
    oracle: { status: 'active', load: 65 },
    conjuror: { status: 'active', load: 78 },
    gemini: { status: 'active', load: 42 },
    aria: { status: 'active', load: 51 },
    capri: { status: 'active', load: 89 },
  });

  useEffect(() => {
    setPerformanceData(generateMockData(60));
    
    const interval = setInterval(() => {
      // Update performance data with smoother transitions
      setPerformanceData(prev => {
        if (prev.length === 0) return generateMockData(60);
        
        const newEntry = {
          time: new Date().toTimeString().split(' ')[0].substring(3),
          oracle: Math.max(20, Math.min(95, prev[prev.length - 1].oracle + (Math.random() * 10 - 5))),
          conjuror: Math.max(20, Math.min(95, prev[prev.length - 1].conjuror + (Math.random() * 10 - 5))),
          gemini: Math.max(20, Math.min(95, prev[prev.length - 1].gemini + (Math.random() * 10 - 5))),
          aria: Math.max(20, Math.min(95, prev[prev.length - 1].aria + (Math.random() * 10 - 5))),
          capri: Math.max(20, Math.min(95, prev[prev.length - 1].capri + (Math.random() * 10 - 5))),
        };
        return [...prev.slice(1), newEntry];
      });
      
      // Update system state
      setSystemState(prev => {
        const newState = {...prev};
        Object.keys(newState).forEach(key => {
          newState[key].load = Math.max(20, Math.min(95, newState[key].load + (Math.random() * 10 - 5)));
        });
        return newState;
      });
      
      // Randomly update tasks
      if (Math.random() > 0.8) {
        setTasks(prev => {
          const newTasks = [...prev];
          const randomIndex = Math.floor(Math.random() * newTasks.length);
          if (newTasks[randomIndex].status === 'active') {
            newTasks[randomIndex].status = 'complete';
          } else if (newTasks[randomIndex].status === 'pending') {
            newTasks[randomIndex].status = 'active';
            newTasks[randomIndex].startTime = new Date().toTimeString().split(' ')[0].substring(0, 8);
            newTasks[randomIndex].duration = '00:00:01';
          }
          return newTasks;
        });
      }
      
      // Randomly add new logs
      if (Math.random() > 0.7) {
        const components = ['Oracle', 'Conjuror', 'Gemini', 'Aria', 'Capri', 'System'];
        const messages = [
          'Processing data stream',
          'Analyzing strategic options',
          'Reallocating resources',
          'Synchronizing knowledge base',
          'Executing command sequence',
          'Optimizing system performance'
        ];
        const randomComponent = components[Math.floor(Math.random() * components.length)];
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        
        setLogs(prev => [
          ...prev.slice(-20), // Keep only last 20 logs
          {
            id: prev.length + 1,
            component: randomComponent,
            message: randomMessage,
            timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8)
          }
        ]);
      }
    }, 2000 / simSpeed);
    
    return () => clearInterval(interval);
  }, [simSpeed]);

  const handleCommandSubmit = (e) => {
    e.preventDefault();
    if (!command.trim()) return;
    
    const newLogEntry = {
      id: logs.length + 1,
      component: 'Console',
      message: `Command executed: ${command}`,
      timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8)
    };
    
    setLogs(prev => [...prev, newLogEntry]);
    setCommandHistory(prev => [command, ...prev.slice(0, 9)]); // Keep last 10 commands
    setCommand('');
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* System Status Cards */}
      <div className="monitoring-grid">
        {Object.entries(systemState).map(([component, state]) => (
          <div key={component} className="metric-card">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-lg font-semibold capitalize">{component}</h3>
              {statusIcons[state.status]}
            </div>
            <div className="text-2xl font-bold mb-2">{state.load}%</div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${state.load}%`,
                  backgroundColor: componentColors[component] 
                }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Performance Chart */}
      <div className="dashboard-card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="section-title">Performance Metrics</h2>
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">Speed:</label>
            <select 
              value={simSpeed} 
              onChange={(e) => setSimSpeed(Number(e.target.value))}
              className="border rounded px-2 py-1"
            >
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={2}>2x</option>
              <option value={5}>5x</option>
            </select>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="oracle" stroke={componentColors.oracle} strokeWidth={2} />
            <Line type="monotone" dataKey="conjuror" stroke={componentColors.conjuror} strokeWidth={2} />
            <Line type="monotone" dataKey="gemini" stroke={componentColors.gemini} strokeWidth={2} />
            <Line type="monotone" dataKey="aria" stroke={componentColors.aria} strokeWidth={2} />
            <Line type="monotone" dataKey="capri" stroke={componentColors.capri} strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Alerts */}
      <div className="dashboard-card">
        <h2 className="section-title">Recent Alerts</h2>
        <div className="space-y-3">
          {alerts.length === 0 ? (
            <p className="text-gray-500">No active alerts</p>
          ) : (
            alerts.map(alert => (
              <div key={alert.id} className="flex items-start justify-between p-3 border-l-4 rounded bg-blue-50 border-blue-400">
                <div className="flex-1">
                  <div className="font-medium">{alert.component}: {alert.message}</div>
                  <div className="text-sm mt-1">
                    <span className={`status-indicator status-${alert.severity}`}>
                      {alert.severity}
                    </span>
                  </div>
                </div>
                <div className="text-sm text-gray-500">{alert.timestamp}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );

  const renderTasks = () => (
    <div className="dashboard-card">
      <h2 className="section-title">Active Tasks</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2">Component</th>
              <th className="text-left py-2">Description</th>
              <th className="text-left py-2">Status</th>
              <th className="text-left py-2">Start Time</th>
              <th className="text-left py-2">Duration</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(task => (
              <tr key={task.id} className="border-b hover:bg-gray-50">
                <td className="py-2 font-medium">{task.component}</td>
                <td className="py-2">{task.description}</td>
                <td className="py-2">
                  <div className="flex items-center space-x-2">
                    {statusIcons[task.status]}
                    <span className={`status-indicator status-${task.status}`}>
                      {task.status}
                    </span>
                  </div>
                </td>
                <td className="py-2">{task.startTime}</td>
                <td className="py-2">{task.duration}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderLogs = () => (
    <div className="dashboard-card">
      <h2 className="section-title">System Logs</h2>
      <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
        {logs.slice(-20).reverse().map(log => (
          <div key={log.id} className="mb-1">
            <span className="text-gray-500">[{log.timestamp}]</span>{' '}
            <span className="text-blue-400">{log.component}:</span>{' '}
            {log.message}
          </div>
        ))}
      </div>
    </div>
  );

  const renderCommandConsole = () => (
    <div className="dashboard-card">
      <h2 className="section-title flex items-center">
        <Terminal className="mr-2" size={20} />
        Command Console
      </h2>
      <div className="space-y-4">
        <form onSubmit={handleCommandSubmit} className="flex space-x-2">
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Enter command..."
            className="flex-1 px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Execute
          </button>
        </form>
        
        {commandHistory.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-2">Command History</h3>
            <div className="bg-gray-100 rounded p-2 max-h-32 overflow-y-auto">
              {commandHistory.map((cmd, index) => (
                <div 
                  key={index} 
                  className="text-sm font-mono cursor-pointer hover:bg-gray-200 p-1 rounded"
                  onClick={() => setCommand(cmd)}
                >
                  {cmd}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="dashboard-title">🔮 Oracle Monitoring Dashboard</h1>
          <div className="flex items-center space-x-4">
            <RefreshCw className="text-gray-500" size={20} />
            <span className="text-sm text-gray-600">Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
        
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {[
                { key: 'dashboard', label: 'Dashboard' },
                { key: 'tasks', label: 'Tasks' },
                { key: 'logs', label: 'Logs' },
                { key: 'command', label: 'Command Console' }
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`mr-2 py-2 px-4 ${
                    activeTab === tab.key
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
        
        <div className="fade-in">
          {activeTab === 'dashboard' && renderDashboard()}
          {activeTab === 'tasks' && renderTasks()}
          {activeTab === 'logs' && renderLogs()}
          {activeTab === 'command' && renderCommandConsole()}
        </div>
      </div>
    </div>
  );
}