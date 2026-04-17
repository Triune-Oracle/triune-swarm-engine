import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import {
  Activity,
  AlertTriangle,
  Check,
  Terminal,
  RefreshCw,
  Clock,
  Zap,
  Eye,
} from 'lucide-react';

interface PerformanceEntry {
  time: string;
  oracle: number;
  gemini: number;
  aria: number;
  capri: number;
}

type TaskStatus = 'active' | 'complete' | 'pending' | 'warning' | 'error';

interface TaskItem {
  id: number;
  component: string;
  description: string;
  status: TaskStatus;
  startTime: string;
  duration: string;
}

interface AlertItem {
  id: number;
  component: string;
  severity: 'info' | 'warning' | 'error';
  message: string;
  timestamp: string;
}

interface LogItem {
  id: number;
  component: string;
  message: string;
  timestamp: string;
}

interface SystemAgentState {
  status: string;
  load: number;
}

interface SystemState {
  oracle: SystemAgentState;
  gemini: SystemAgentState;
  aria: SystemAgentState;
  capri: SystemAgentState;
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

const mockTasks: TaskItem[] = [
  {
    id: 1,
    component: 'Oracle',
    description: 'Processing inference directives',
    status: 'active',
    startTime: '12:30:05',
    duration: '00:05:22',
  },
  {
    id: 3,
    component: 'Gemini',
    description: 'Resource orchestration for batch FPVAE_PHASE2_001',
    status: 'active',
    startTime: '12:32:45',
    duration: '00:02:42',
  },
  {
    id: 4,
    component: 'Aria',
    description: 'IPFS metadata indexing',
    status: 'complete',
    startTime: '12:29:10',
    duration: '00:03:55',
  },
  {
    id: 5,
    component: 'Capri',
    description: 'Decision audit logging — batch 12',
    status: 'active',
    startTime: '12:33:22',
    duration: '00:01:05',
  },
  {
    id: 6,
    component: 'Capri',
    description: 'Allocate inference resources',
    status: 'pending',
    startTime: '-',
    duration: '-',
  },
  {
    id: 7,
    component: 'Capri',
    description: 'Flush audit log to IPFS',
    status: 'pending',
    startTime: '-',
    duration: '-',
  },
];

const mockAlerts: AlertItem[] = [
  {
    id: 1,
    component: 'Oracle',
    severity: 'info',
    message: 'New inference batch received',
    timestamp: '12:30:00',
  },
  {
    id: 2,
    component: 'Aria',
    severity: 'warning',
    message: 'IPFS metadata sync slower than threshold',
    timestamp: '12:31:23',
  },
  {
    id: 3,
    component: 'Capri',
    severity: 'info',
    message: 'Audit task #5 started',
    timestamp: '12:33:22',
  },
];

const mockLogs: LogItem[] = [
  {
    id: 1,
    component: 'System',
    message: 'FractalPrior Clinical View initialized',
    timestamp: '12:29:00',
  },
  {
    id: 2,
    component: 'Oracle',
    message: 'Inference batch FPVAE_PHASE2_001 received',
    timestamp: '12:30:00',
  },
  {
    id: 3,
    component: 'Aria',
    message: 'IPFS metadata sync rate: 85%',
    timestamp: '12:31:23',
  },
  {
    id: 4,
    component: 'Gemini',
    message: 'Resource orchestration complete',
    timestamp: '12:32:45',
  },
  {
    id: 5,
    component: 'Capri',
    message: 'Audit log entries 1–12 written',
    timestamp: '12:33:22',
  },
];

const componentColors = {
  oracle: '#8884d8',
  gemini: '#ffc658',
  aria: '#ff8042',
  capri: '#0088fe',
};

const statusIcons: Record<TaskStatus, React.ReactNode> = {
  active: <Activity className="text-green-500" size={16} />,
  complete: <Check className="text-blue-500" size={16} />,
  pending: <Clock className="text-gray-500" size={16} />,
  warning: <AlertTriangle className="text-yellow-500" size={16} />,
  error: <AlertTriangle className="text-red-500" size={16} />,
};

export default function TriumvirateMonitor() {
  const [performanceData, setPerformanceData] = useState<PerformanceEntry[]>(generateMockData(60));
  const [tasks, setTasks] = useState<TaskItem[]>(mockTasks);
  const [alerts, setAlerts] = useState<AlertItem[]>(mockAlerts);
  const [logs, setLogs] = useState<LogItem[]>(mockLogs);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'tasks' | 'alerts' | 'logs' | 'console'>('dashboard');
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [systemState, setSystemState] = useState<SystemState>({
    oracle: { status: 'active', load: 65 },
    gemini: { status: 'active', load: 42 },
    aria: { status: 'active', load: 51 },
    capri: { status: 'active', load: 89 },
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setPerformanceData((prev) => {
        const last = prev[prev.length - 1] ?? {
          time: '00:00',
          oracle: 50,
          gemini: 50,
          aria: 50,
          capri: 50,
        };

        const newEntry: PerformanceEntry = {
          time: new Date().toTimeString().slice(0, 8),
          oracle: Math.max(20, Math.min(95, last.oracle + (Math.random() * 10 - 5))),
          gemini: Math.max(20, Math.min(95, last.gemini + (Math.random() * 10 - 5))),
          aria: Math.max(20, Math.min(95, last.aria + (Math.random() * 10 - 5))),
          capri: Math.max(20, Math.min(95, last.capri + (Math.random() * 10 - 5))),
        };

        return [...prev.slice(1), newEntry];
      });

      setSystemState((prev) => ({
        oracle: {
          ...prev.oracle,
          load: Math.max(20, Math.min(95, prev.oracle.load + (Math.random() * 10 - 5))),
        },
        gemini: {
          ...prev.gemini,
          load: Math.max(20, Math.min(95, prev.gemini.load + (Math.random() * 10 - 5))),
        },
        aria: {
          ...prev.aria,
          load: Math.max(20, Math.min(95, prev.aria.load + (Math.random() * 10 - 5))),
        },
        capri: {
          ...prev.capri,
          load: Math.max(20, Math.min(95, prev.capri.load + (Math.random() * 10 - 5))),
        },
      }));

      if (Math.random() > 0.8) {
        setTasks((prev) => {
          const next = [...prev];
          const randomIndex = Math.floor(Math.random() * next.length);
          const item = next[randomIndex];

          if (!item) return prev;

          if (item.status === 'active') {
            next[randomIndex] = { ...item, status: 'complete' };
          } else if (item.status === 'pending') {
            next[randomIndex] = {
              ...item,
              status: 'active',
              startTime: new Date().toTimeString().slice(0, 8),
              duration: '00:00:01',
            };
          }

          return next;
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

        const randomComponent = components[Math.floor(Math.random() * components.length)] ?? 'System';
        const randomMessage = messages[Math.floor(Math.random() * messages.length)] ?? 'System update';

        setLogs((prev) => [
          ...prev,
          {
            id: prev.length + 1,
            component: randomComponent,
            message: randomMessage,
            timestamp: new Date().toTimeString().slice(0, 8),
          },
        ]);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleCommandSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!command.trim()) return;

    const newLogEntry: LogItem = {
      id: logs.length + 1,
      component: 'User',
      message: `Command: ${command}`,
      timestamp: new Date().toTimeString().slice(0, 8),
    };

    setLogs((prev) => [...prev, newLogEntry]);

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

    const responseEntry: LogItem = {
      id: logs.length + 2,
      component: 'System',
      message: responseMessage,
      timestamp: new Date().toTimeString().slice(0, 8),
    };

    setLogs((prev) => [...prev, responseEntry]);
    setCommandHistory((prev) => [...prev, command]);
    setCommand('');
  };

  const renderDashboard = () => (
    <>
      <div className="mb-8 rounded bg-white p-4 shadow">
        <h2 className="mb-2 text-xl font-semibold">Live Agent Throughput</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            {(Object.keys(componentColors) as Array<keyof typeof componentColors>).map((key) => (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={componentColors[key]}
                strokeWidth={2}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        {Object.entries(systemState).map(([name, state]) => (
          <div key={name} className="rounded bg-white p-4 shadow">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="font-semibold capitalize">{name}</h3>
              <Zap size={16} className="text-blue-500" />
            </div>
            <p className="text-sm text-gray-600">Status: {state.status}</p>
            <p className="text-sm text-gray-600">Load: {Math.round(state.load)}%</p>
          </div>
        ))}
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center gap-3">
          <Activity className="text-blue-600" size={28} />
          <div>
            <h1 className="text-2xl font-bold">Triumvirate Monitor</h1>
            <p className="text-sm text-gray-600">Swarm state, alerts, logs, and command console</p>
          </div>
        </div>

        <div className="mb-6 flex flex-wrap gap-2">
          <button className="rounded bg-blue-600 px-4 py-2 text-white" onClick={() => setActiveTab('dashboard')}>
            Dashboard
          </button>
          <button className="rounded bg-gray-700 px-4 py-2 text-white" onClick={() => setActiveTab('tasks')}>
            Tasks
          </button>
          <button className="rounded bg-gray-700 px-4 py-2 text-white" onClick={() => setActiveTab('alerts')}>
            Alerts
          </button>
          <button className="rounded bg-gray-700 px-4 py-2 text-white" onClick={() => setActiveTab('logs')}>
            Logs
          </button>
          <button className="rounded bg-gray-700 px-4 py-2 text-white" onClick={() => setActiveTab('console')}>
            Console
          </button>
        </div>

        {activeTab === 'dashboard' && renderDashboard()}

        {activeTab === 'tasks' && (
          <div className="rounded bg-white p-4 shadow">
            <h2 className="mb-4 text-xl font-semibold">Tasks</h2>
            <div className="space-y-3">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-start justify-between rounded border p-3">
                  <div>
                    <div className="font-medium">{task.component}</div>
                    <div className="text-sm text-gray-700">{task.description}</div>
                    <div className="text-xs text-gray-500">
                      Start: {task.startTime} · Duration: {task.duration}
                    </div>
                  </div>
                  <div>{statusIcons[task.status]}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'alerts' && (
          <div className="rounded bg-white p-4 shadow">
            <h2 className="mb-4 text-xl font-semibold">Alerts</h2>
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div key={alert.id} className="rounded border p-3">
                  <div className="font-medium">
                    {alert.component} · <span className="capitalize">{alert.severity}</span>
                  </div>
                  <div className="text-sm text-gray-700">{alert.message}</div>
                  <div className="text-xs text-gray-500">{alert.timestamp}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="rounded bg-white p-4 shadow">
            <h2 className="mb-4 text-xl font-semibold">Logs</h2>
            <div className="space-y-2">
              {logs.map((log) => (
                <div key={log.id} className="rounded border p-3 text-sm">
                  <span className="font-medium">{log.timestamp}</span> · <span>{log.component}</span> ·{' '}
                  <span>{log.message}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'console' && (
          <div className="rounded bg-white p-4 shadow">
            <div className="mb-4 flex items-center gap-2">
              <Terminal size={18} />
              <h2 className="text-xl font-semibold">Command Console</h2>
            </div>

            <form onSubmit={handleCommandSubmit} className="mb-4 flex gap-2">
              <input
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                className="flex-1 rounded border px-3 py-2"
                placeholder="Enter command..."
              />
              <button type="submit" className="rounded bg-blue-600 px-4 py-2 text-white">
                Run
              </button>
            </form>

            <div className="mb-4 text-sm text-gray-600">
              History: {commandHistory.length ? commandHistory.join(', ') : 'No commands yet'}
            </div>

            <div className="flex gap-2 text-sm text-gray-500">
              <RefreshCw size={16} />
              <Eye size={16} />
              <AlertTriangle size={16} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
