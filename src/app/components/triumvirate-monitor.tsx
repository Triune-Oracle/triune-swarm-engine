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

interface PerformanceEntry {
  time: string;
  oracle: number;
  gemini: number;
  aria: number;
  capri: number;
}

interface ReconstructionMetrics {
  echoDepth: number;
  affectFootprint: number;
  resonantDrift: number;
}

const generateMockData = (minutes: number): PerformanceEntry[] => {
  return Array.from({ length: minutes }, (_, i) => ({
    time: `${String(Math.floor(i / 60)).padStart(2, '0')}:${String(i % 60).padStart(2, '0')}`,
    oracle: Math.floor(Math.random() * 100),
    gemini: Math.floor(Math.random() * 100),
    aria: Math.floor(Math.random() * 100),
    capri: Math.floor(Math.random() * 100),
  }));
};

const mockTasks = [
  { id: 1, component: 'Oracle', description: 'Processing inference directives', status: 'active', startTime: '12:30:05', duration: '00:05:22' },
  { id: 3, component: 'Gemini', description: 'Resource orchestration for batch FPVAE_PHASE2_001', status: 'active', startTime: '12:32:45', duration: '00:02:42' },
  { id: 4, component: 'Aria', description: 'IPFS metadata indexing', status: 'complete', startTime: '12:29:10', duration: '00:03:55' },
  { id: 5, component: 'Capri', description: 'Decision audit logging — batch 12', status: 'active', startTime: '12:33:22', duration: '00:01:05' },
  { id: 6, component: 'Capri', description: 'Allocate inference resources', status: 'pending', startTime: '-', duration: '-' },
  { id: 7, component: 'Capri', description: 'Flush audit log to IPFS', status: 'pending', startTime: '-', duration: '-' },
];

const mockAlerts = [
  { id: 1, component: 'Oracle', severity: 'info', message: 'New inference batch received', timestamp: '12:30:00' },
  { id: 2, component: 'Aria', severity: 'warning', message: 'IPFS metadata sync slower than threshold', timestamp: '12:31:23' },
  { id: 3, component: 'Capri', severity: 'info', message: 'Audit task #5 started', timestamp: '12:33:22' },
];

const mockLogs = [
  { id: 1, component: 'System', message: 'FractalPrior Clinical View initialized', timestamp: '12:29:00' },
  { id: 2, component: 'Oracle', message: 'Inference batch FPVAE_PHASE2_001 received', timestamp: '12:30:00' },
  { id: 3, component: 'Aria', message: 'IPFS metadata sync rate: 85%', timestamp: '12:31:23' },
  { id: 4, component: 'Gemini', message: 'Resource orchestration complete', timestamp: '12:32:45' },
  { id: 5, component: 'Capri', message: 'Audit log entries 1–12 written', timestamp: '12:33:22' },
];

const componentColors = {
  oracle: '#8884d8',
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

 main
  const [tasks, setTasks] = useState(mockTasks);
  const [alerts, setAlerts] = useState(mockAlerts);
  const [logs, setLogs] = useState(mockLogs);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);

  });
  const [systemState, setSystemState] = useState({
    oracle: { status: 'active', load: 65 },
    gemini: { status: 'active', load: 42 },
    aria: { status: 'active', load: 51 },
    capri: { status: 'active', load: 89 },
  });

  useEffect(() => {
    setPerformanceData(generateMockData(60));


    const interval = setInterval(() => {
      setPerformanceData(prev => {

          time: new Date().toTimeString().split(' ')[0].substring(3),
          oracle: Math.max(20, Math.min(95, last.oracle + (Math.random() * 10 - 5))),
          gemini: Math.max(20, Math.min(95, last.gemini + (Math.random() * 10 - 5))),
          aria: Math.max(20, Math.min(95, last.aria + (Math.random() * 10 - 5))),
          capri: Math.max(20, Math.min(95, last.capri + (Math.random() * 10 - 5))),
        };
        return [...prev.slice(1), newEntry];
      });

      setSystemState(prev => {

        });
        return newState;
      });


      if (Math.random() > 0.8) {
        setTasks(prev => {
          const newTasks = [...prev];
          const randomIndex = Math.floor(Math.random() * newTasks.length);
          if (newTasks[randomIndex].status === 'active') {
            newTasks[randomIndex] = { ...newTasks[randomIndex], status: 'complete' };
          } else if (newTasks[randomIndex].status === 'pending') {
            newTasks[randomIndex] = {
              ...newTasks[randomIndex],
              status: 'active',
              startTime: new Date().toTimeString().split(' ')[0].substring(0, 8),
              duration: '00:00:01',
            };
          }
          return newTasks;
        });
      }

      if (Math.random() > 0.7) {
        const components = ['Oracle', 'Gemini', 'Aria', 'Capri', 'System'];
        const messages = [
          'Processing inference batch',
          'Orchestrating resource allocation',
          'IPFS metadata sync in progress',
          'Audit log entry written',
          'Reconstruction confidence updated',
          'Model drift within threshold',
        ];
        const randomComponent = components[Math.floor(Math.random() * components.length)];
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        setLogs(prev => [
          ...prev,
          {
            id: prev.length + 1,
            component: randomComponent,
            message: randomMessage,
            timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
          },
        ]);
      }


  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;

    const newLogEntry = {
      id: logs.length + 1,
      component: 'User',
      message: `Command: ${command}`,
      timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
    };

    setLogs(prev => [...prev, newLogEntry]);

    let responseMessage = '';

    if (command.toLowerCase().includes('status')) {
      responseMessage = 'All namespaces operational. Oracle/A: 65%, Gemini/D: 42%, Aria/C: 51%, Capri/B: 89%';
    } else if (command.toLowerCase().includes('help')) {
      responseMessage = 'Available commands: status, help, clear, reset';
    } else if (command.toLowerCase().includes('clear')) {
      setLogs([]);
      responseMessage = 'Log cleared';
    } else if (command.toLowerCase().includes('reset')) {
      setTasks(mockTasks);
      setAlerts(mockAlerts);
      responseMessage = 'System state reset to baseline';
    } else {
      responseMessage = `Unknown command: ${command}`;
    }

    const responseEntry = {
      id: logs.length + 2,
      component: 'System',
      message: responseMessage,
      timestamp: new Date().toTimeString().split(' ')[0].substring(0, 8),
    };

    setLogs(prev => [...prev, responseEntry]);
    setCommandHistory(prev => [...prev, command]);
    setCommand('');
  };

  const renderDashboard = () => (
    <>
      <div className="mb-8 p-4 bg-white shadow rounded">
        <h2 className="text-xl font-semibold mb-2">Live Agent Throughput</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            {(Object.keys(componentColors) as Array<keyof typeof componentColors>).map(key => (
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
          <h2 className="text-xl font-semibold mb-4">Namespace Status</h2>
          <div className="grid grid-cols-2 gap-4">
            {(Object.keys(systemState) as Array<keyof typeof systemState>).map(key => (
              <div key={key} className="p-3 border rounded">
                <div className="flex justify-between items-center">
                  <h3 className="font-medium capitalize">{key}</h3>
                  {statusIcons[systemState[key].status as keyof typeof statusIcons]}
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

  const renderReconstruction = () => (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="bg-white p-4 shadow rounded">
        <h2 className="text-xl font-semibold mb-2">VAE Latent Traversal Depth</h2>
        <p className="text-xs text-gray-500 mb-4">echoDepth — how far the decoder probes the latent manifold</p>
        <div className="text-4xl font-mono font-bold text-indigo-600 mb-2">
          {reconstructionMetrics.echoDepth.toFixed(4)}
        </div>
        <div className="bg-gray-200 rounded-full h-3">
          <div
            className="bg-indigo-500 h-3 rounded-full transition-all"
            style={{ width: `${reconstructionMetrics.echoDepth * 100}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-400 mt-2">Range 0–1 · threshold &gt; 0.60 for clinical acceptance</p>
      </div>

      <div className="bg-white p-4 shadow rounded">
        <h2 className="text-xl font-semibold mb-2">Uncertainty Quantification</h2>
        <p className="text-xs text-gray-500 mb-4">affectFootprint — pixel-wise variance heatmap magnitude</p>
        <div className="text-4xl font-mono font-bold text-amber-600 mb-2">
          {reconstructionMetrics.affectFootprint.toFixed(4)}
        </div>
        <div className="bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${reconstructionMetrics.affectFootprint > 0.30 ? 'bg-red-500' : 'bg-amber-500'}`}
            style={{ width: `${reconstructionMetrics.affectFootprint * 100}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-400 mt-2">Range 0–1 · alert if &gt; 0.30 (high pixel uncertainty)</p>
      </div>

      <div className="bg-white p-4 shadow rounded">
        <h2 className="text-xl font-semibold mb-2">Model Drift Detection</h2>
        <p className="text-xs text-gray-500 mb-4">resonantDrift — distribution shift across inference batches</p>
        <div className="text-4xl font-mono font-bold text-teal-600 mb-2">
          {reconstructionMetrics.resonantDrift.toFixed(4)}
        </div>
        <div className="bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${reconstructionMetrics.resonantDrift > 0.10 ? 'bg-red-500' : 'bg-teal-500'}`}
            style={{ width: `${reconstructionMetrics.resonantDrift * 50 * 100}%` }}
          ></div>
        </div>
        <p className="text-xs text-gray-400 mt-2">Range 0–0.5 · alert if &gt; 0.10 (significant drift)</p>
      </div>
    </div>
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
    </div>
  );

  return (
    <div className={`p-4 min-h-screen ${operationalMode === 'RESONANCE' ? 'bg-gray-950' : 'bg-gray-100'}`}>
      <div className="flex justify-between items-center mb-6">
