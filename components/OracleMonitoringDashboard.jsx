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
  active: React.createElement(Activity, { className: "text-green-500", size: 16 }),
  complete: React.createElement(Check, { className: "text-blue-500", size: 16 }),
  pending: React.createElement(Clock, { className: "text-gray-500", size: 16 }),
  warning: React.createElement(AlertTriangle, { className: "text-yellow-500", size: 16 }),
  error: React.createElement(AlertTriangle, { className: "text-red-500", size: 16 }),
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
          ...prev,
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
    <div className="p-4 bg-gray-100 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Triune Oracle Monitoring Dashboard</h1>
        <div className="flex items-center">
          <RefreshCw className="text-blue-600 mr-2" size={20} />
          <span className="text-sm text-gray-600">Last updated: {new Date().toTimeString().split(' ')[0]}</span>
        </div>
      </div>
      
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`mr-2 py-2 px-4 ${
                activeTab === 'dashboard'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('tasks')}
              className={`mr-2 py-2 px-4 ${
                activeTab === 'tasks'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Tasks
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`mr-2 py-2 px-4 ${
                activeTab === 'logs'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Logs
            </button>
            <button
              onClick={() => setActiveTab('command')}
              className={`py-2 px-4 ${
                activeTab === 'command'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Command Console
            </button>
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