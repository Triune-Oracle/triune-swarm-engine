import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Activity, AlertTriangle, Check, Terminal, RefreshCw, Clock, Zap, Eye } from 'lucide-react';

type OperationalMode = 'CLINICAL' | 'RESONANCE';

interface PerformanceDataPoint {
  time: string;
  oracle: number;
  conjuror: number;
  gemini: number;
  aria: number;
  capri: number;
}

interface ResonanceMetrics {
  echoDepth: Record<string, number>;
  resonantDrift: Record<string, number>;
  affectFootprint: Record<string, string>;
  scrollAuditLog: Array<{ timestamp: string; event: string; agent: string }>;
}

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

export default function TriumvirateMonitor() { 
  const [performanceData, setPerformanceData] = useState<PerformanceDataPoint[]>([]);
  const [tasks, setTasks] = useState(mockTasks);
  const [alerts, setAlerts] = useState(mockAlerts);
  const [logs, setLogs] = useState(mockLogs);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [simSpeed, setSimSpeed] = useState(1);
  const [operationalMode, setOperationalMode] = useState<OperationalMode>('CLINICAL');
  const [resonanceMetrics, setResonanceMetrics] = useState<ResonanceMetrics>({
    echoDepth: { oracle: 1, conjuror: 1, gemini: 1, aria: 1, capri: 1 },
    resonantDrift: { oracle: 0, conjuror: 0, gemini: 0, aria: 0, capri: 0 },
    affectFootprint: { oracle: 'amethyst', conjuror: 'citrine', gemini: 'obsidian', aria: 'amethyst', capri: 'citrine' },
    scrollAuditLog: [],
  });
  const [systemState, setSystemState] = useState({
    oracle: { status: 'active', load: 65 },
    conjuror: { status: 'active', load: 78 },
    gemini: { status: 'active', load: 42 },
    aria: { status: 'active', load: 51 },
    capri: { status: 'active', load: 89 },
  });

  useEffect(() => {
    setPerformanceData(generateMockData(60));
    
    // In RESONANCE mode the effective tick rate is 0.75x slower
    const tickInterval = operationalMode === 'RESONANCE' ? 2000 / simSpeed / 0.75 : 2000 / simSpeed;

    const interval = setInterval(() => {
      // Update performance data with smoother transitions
      setPerformanceData(prev => {
        const newEntry: PerformanceDataPoint = {
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
          newState[key as keyof typeof newState].load = Math.max(20, Math.min(95, newState[key as keyof typeof newState].load + (Math.random() * 10 - 5)));
        });
        return newState;
      });

      // Update resonance metrics when in RESONANCE mode
      if (operationalMode === 'RESONANCE') {
        setResonanceMetrics(prev => {
          const agents = ['oracle', 'conjuror', 'gemini', 'aria', 'capri'] as const;
          const newEchoDepth = { ...prev.echoDepth };
          const newDrift = { ...prev.resonantDrift };
          agents.forEach(agent => {
            newEchoDepth[agent] = Math.max(1, Math.min(5, (newEchoDepth[agent] ?? 1) + (Math.random() > 0.7 ? 1 : Math.random() > 0.7 ? -1 : 0)));
            newDrift[agent] = Math.round(((newDrift[agent] ?? 0) + (Math.random() * 2 - 1)) * 10) / 10;
          });
          const newAuditEntry = Math.random() > 0.6 ? [{
            timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
            event: ['scroll-invoked', 'echo-bloom', 'drift-detected'][Math.floor(Math.random() * 3)],
            agent: agents[Math.floor(Math.random() * agents.length)],
          }] : [];
          return {
            ...prev,
            echoDepth: newEchoDepth,
            resonantDrift: newDrift,
            scrollAuditLog: [...prev.scrollAuditLog.slice(-19), ...newAuditEntry],
          };
        });
      }
      
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
          ...prev,
          {
            id: prev.length + 1,
            component: randomComponent,
            message: randomMessage,
            timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8)
          }
        ]);
      }
    }, tickInterval);
    
    return () => clearInterval(interval);
  }, [simSpeed, operationalMode]);

  const handleCommandSubmit = (e) => {
    e.preventDefault();
    if (!command.trim()) return;
    
    const newLogEntry = {
      id: logs.length + 1,
      component: 'User',
      message: `Command: ${command}`,
      timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8)
    };
    
    setLogs(prev => [...prev, newLogEntry]);
    
    // Process command
    let responseMessage = '';
    
    if (command.toLowerCase().includes('status')) {
      responseMessage = 'All systems operational. Oracle: 65%, Conjuror: 78%, Gemini: 42%, Aria: 51%, Capri: 89%';
    } else if (command.toLowerCase().includes('help')) {
      responseMessage = 'Available commands: status, help, clear, reset, speed [1-5]';
    } else if (command.toLowerCase().includes('clear')) {
      setLogs([]);
      responseMessage = 'Log cleared';
    } else if (command.toLowerCase().includes('reset')) {
      setTasks(mockTasks);
      setAlerts(mockAlerts);
      responseMessage = 'System state reset to baseline';
    } else if (command.toLowerCase().includes('speed')) {
      const speedMatch = command.match(/speed\s+(\d+)/);
      if (speedMatch && speedMatch[1]) {
        const newSpeed = Math.max(1, Math.min(5, parseInt(speedMatch[1])));
        setSimSpeed(newSpeed);
        responseMessage = `Simulation speed set to ${newSpeed}x`;
      } else {
        responseMessage = 'Invalid speed setting. Use: speed [1-5]';
      }
    } else {
      responseMessage = `Unknown command: ${command}`;
    }
    
    // Add response
    const responseEntry = {
      id: logs.length + 2,
      component: 'System',
      message: responseMessage,
      timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8)
    };
    
    setLogs(prev => [...prev, responseEntry]);
    setCommandHistory(prev => [...prev, command]);
    setCommand('');
  };

  const renderDashboard = () => (
    <>
      <div className="mb-8 p-4 bg-white shadow rounded">
        <h2 className="text-xl font-semibold mb-2">Live Component Performance</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(componentColors).map(key => (
              <Line 
                key={key} 
                type="monotone" 
                dataKey={key} 
                stroke={componentColors[key]} 
                activeDot={{ r: 6 }} 
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <div className="bg-white p-4 shadow rounded">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="grid grid-cols-2 gap-4">
            {Object.keys(systemState).map(key => (
              <div key={key} className="p-3 border rounded">
                <div className="flex justify-between items-center">
                  <h3 className="font-medium capitalize">{key}</h3>
                  {statusIcons[systemState[key].status]}
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-blue-600 h-2.5 rounded-full" 
                    style={{ width: `${systemState[key].load}%` }}
                  ></div>
                </div>
                <div className="mt-1 text-sm text-gray-500 flex justify-between">
                  <span>Load</span>
                  <span>{systemState[key].load.toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white p-4 shadow rounded">
          <h2 className="text-xl font-semibold mb-2">System Alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-gray-500 italic">No active alerts</p>
          ) : (
            alerts.map(alert => (
              <div key={alert.id} className="mb-3 p-3 border-l-4 rounded bg-blue-50 border-blue-400">
                <div className="flex justify-between">
                  <div className="font-medium">{alert.component}: {alert.message}</div>
                  <div className="text-sm text-gray-500">{alert.timestamp}</div>
                </div>
                <div className="text-sm mt-1">
                  <span className={`inline-block px-2 py-1 rounded ${
                    alert.severity === 'warning' ? 'bg-yellow-200 text-yellow-800' : 'bg-blue-200 text-blue-800'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );

  const renderTasks = () => (
    <div className="bg-white p-4 shadow rounded">
      <h2 className="text-xl font-semibold mb-4">Active Tasks</h2>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Time</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {tasks.map(task => (
            <tr key={task.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.id}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{task.component}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.description}</td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  {statusIcons[task.status]}
                  <span className="ml-1 text-sm capitalize">{task.status}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.startTime}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{task.duration}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderLogs = () => (
    <div className="bg-white p-4 shadow rounded">
      <h2 className="text-xl font-semibold mb-4">System Logs</h2>
      <div className="bg-gray-900 text-green-500 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
        {logs.map(log => (
          <div key={log.id} className="mb-1">
            <span className="text-gray-400">[{log.timestamp}]</span>{' '}
            <span className="text-yellow-400">{log.component}:</span>{' '}
            <span>{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCommandConsole = () => (
    <div className="bg-white p-4 shadow rounded">
      <h2 className="text-xl font-semibold mb-2">Command Console</h2>
      <div className="bg-gray-900 text-green-500 p-4 rounded font-mono text-sm h-80 overflow-y-auto mb-4">
        {logs.slice(-15).map(log => (
          <div key={log.id} className="mb-1">
            <span className="text-gray-400">[{log.timestamp}]</span>{' '}
            <span className="text-yellow-400">{log.component}:</span>{' '}
            <span>{log.message}</span>
          </div>
        ))}
      </div>
      <form onSubmit={handleCommandSubmit} className="flex">
        <span className="bg-gray-900 text-green-500 px-2 py-2 rounded-l font-mono">$</span>
        <input
          type="text"
          value={command}
          onChange={e => setCommand(e.target.value)}
          className="flex-1 bg-gray-900 text-green-500 px-2 py-2 font-mono focus:outline-none"
          placeholder="Type command (try 'help')"
        />
        <button 
          type="submit" 
          className="bg-blue-600 text-white px-4 py-2 rounded-r hover:bg-blue-700"
        >
          Execute
        </button>
      </form>
      <div className="mt-2 text-sm text-gray-500">
        Simulation Speed: 
        <div className="flex space-x-1 mt-1">
          {[1, 2, 3, 4, 5].map(speed => (
            <button
              key={speed}
              onClick={() => setSimSpeed(speed)}
              className={`px-3 py-1 rounded ${
                simSpeed === speed ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className={`p-4 min-h-screen ${operationalMode === 'RESONANCE' ? 'bg-gray-950' : 'bg-gray-100'}`}>
      <div className="flex justify-between items-center mb-6">
        <h1 className={`text-3xl font-bold ${operationalMode === 'RESONANCE' ? 'text-purple-300' : ''}`}>
          Triumvirate System Monitor
        </h1>
        <div className="flex items-center gap-4">
          {/* Operational mode toggle */}
          <button
            onClick={() => setOperationalMode(m => m === 'CLINICAL' ? 'RESONANCE' : 'CLINICAL')}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              operationalMode === 'RESONANCE'
                ? 'bg-purple-700 text-purple-100 hover:bg-purple-600'
                : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }`}
          >
            {operationalMode === 'RESONANCE' ? <Eye size={15} /> : <Zap size={15} />}
            {operationalMode === 'CLINICAL' ? 'Clinical Mode' : 'Resonance Mode'}
          </button>
          <div className="flex items-center">
            <RefreshCw className={`mr-2 ${operationalMode === 'RESONANCE' ? 'text-purple-400' : 'text-blue-600'}`} size={20} />
            <span className={`text-sm ${operationalMode === 'RESONANCE' ? 'text-gray-400' : 'text-gray-600'}`}>
              Last updated: {new Date().toTimeString().split(' ')[0]}
            </span>
          </div>
        </div>
      </div>

      {/* Resonance metrics panel — only in RESONANCE mode */}
      {operationalMode === 'RESONANCE' && (
        <div className="mb-6 p-4 bg-gray-900 rounded border border-purple-800">
          <h2 className="text-lg font-semibold text-purple-300 mb-3">Scroll Echo Metrics</h2>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
            {Object.entries(resonanceMetrics.echoDepth).map(([agent, depth]) => (
              <div key={agent} className="bg-gray-800 p-3 rounded">
                <div className="text-xs text-gray-400 capitalize mb-1">{agent}</div>
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }, (_, i) => (
                    <span key={i} className={`text-lg ${i < depth ? 'text-purple-400' : 'text-gray-700'}`}>◆</span>
                  ))}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  echo depth: {depth} &nbsp;|&nbsp; drift: {(resonanceMetrics.resonantDrift[agent] ?? 0).toFixed(1)}
                </div>
                <div className={`mt-1 text-xs px-2 py-0.5 rounded inline-block ${
                  resonanceMetrics.affectFootprint[agent] === 'amethyst' ? 'bg-purple-900 text-purple-300' :
                  resonanceMetrics.affectFootprint[agent] === 'citrine' ? 'bg-yellow-900 text-yellow-300' :
                  'bg-gray-700 text-gray-300'
                }`}>
                  {resonanceMetrics.affectFootprint[agent]}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-2">
            <div className="text-xs text-gray-400 mb-1">Scroll Audit Log</div>
            <div className="bg-gray-950 rounded p-2 h-20 overflow-y-auto font-mono text-xs text-purple-300">
              {resonanceMetrics.scrollAuditLog.length === 0
                ? <span className="text-gray-600">No scroll events yet…</span>
                : resonanceMetrics.scrollAuditLog.map((entry, i) => (
                    <div key={i}>[{entry.timestamp}] <span className="text-yellow-400">{entry.agent}</span> — {entry.event}</div>
                  ))
              }
            </div>
          </div>
        </div>
      )}
      
      <div className="mb-6">
        <div className={`border-b ${operationalMode === 'RESONANCE' ? 'border-gray-700' : 'border-gray-200'}`}>
          <nav className="flex -mb-px">
            {(['dashboard', 'tasks', 'logs', 'command'] as const).map((tab, idx) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`${idx < 3 ? 'mr-2' : ''} py-2 px-4 capitalize ${
                  activeTab === tab
                    ? `border-b-2 ${operationalMode === 'RESONANCE' ? 'border-purple-500 text-purple-400' : 'border-blue-500 text-blue-600'}`
                    : `${operationalMode === 'RESONANCE' ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-gray-800'}`
                }`}
              >
                {tab === 'command' ? 'Command Console' : tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </div>
      
      {activeTab === 'dashboard' && renderDashboard()}
      {activeTab === 'tasks' && renderTasks()}
      {activeTab === 'logs' && renderLogs()}
      {activeTab === 'command' && renderCommandConsole()}
    </div>
  );
}