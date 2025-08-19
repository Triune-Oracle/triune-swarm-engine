import React, { useState, useEffect, useRef } from 'react';
import { Activity, Zap, Shield, Upload, Archive, GitBranch, Users, Palette } from 'lucide-react';

interface TransmutationEvent {
  id: string;
  type: 'ci_cd' | 'contributor_onboarding' | 'artifact_bundling' | 'theme_rotation';
  status: 'pending' | 'active' | 'completed' | 'failed';
  timestamp: string;
  details: string;
  signature?: string;
  ipfsHash?: string;
}

interface RitualSchedule {
  id: string;
  name: string;
  type: 'glyph_rotation' | 'lineage_archival';
  schedule: string;
  lastRun?: string;
  nextRun: string;
  status: 'active' | 'paused';
}

const RitualNodeTransmutation: React.FC = () => {
  const [events, setEvents] = useState<TransmutationEvent[]>([]);
  const [rituals, setRituals] = useState<RitualSchedule[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const automationAdapterRef = useRef<any>(null);

  useEffect(() => {
    // Initialize automation adapter connection
    initializeAutomationAdapter();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize scheduled rituals
    initializeRituals();

    return () => {
      // Cleanup event listeners
      cleanupEventListeners();
    };
  }, []);

  const initializeAutomationAdapter = async () => {
    try {
      // Connect to backend automation systems
      const response = await fetch('/api/automation/connect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ component: 'RitualNodeTransmutation' })
      });
      
      if (response.ok) {
        setIsConnected(true);
        console.log('Automation adapter connected successfully');
      }
    } catch (error) {
      console.error('Failed to connect automation adapter:', error);
    }
  };

  const setupEventListeners = () => {
    // Listen for CI/CD pipeline events
    if (typeof window !== 'undefined') {
      window.addEventListener('ci-cd-success', handleCiCdEvent);
      window.addEventListener('contributor-onboarded', handleContributorEvent);
      window.addEventListener('artifact-bundled', handleArtifactEvent);
      window.addEventListener('theme-rotated', handleThemeEvent);
    }
  };

  const cleanupEventListeners = () => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('ci-cd-success', handleCiCdEvent);
      window.removeEventListener('contributor-onboarded', handleContributorEvent);
      window.removeEventListener('artifact-bundled', handleArtifactEvent);
      window.removeEventListener('theme-rotated', handleThemeEvent);
    }
  };

  const handleCiCdEvent = (event: any) => {
    const transmutationEvent: TransmutationEvent = {
      id: generateEventId(),
      type: 'ci_cd',
      status: 'active',
      timestamp: new Date().toISOString(),
      details: `CI/CD pipeline completed: ${event.detail.branch || 'main'}`,
    };
    
    addTransmutationEvent(transmutationEvent);
    triggerTransmutationLog(transmutationEvent);
  };

  const handleContributorEvent = (event: any) => {
    const transmutationEvent: TransmutationEvent = {
      id: generateEventId(),
      type: 'contributor_onboarding',
      status: 'active',
      timestamp: new Date().toISOString(),
      details: `New contributor onboarded: ${event.detail.username || 'Unknown'}`,
    };
    
    addTransmutationEvent(transmutationEvent);
    processContributorOnboarding(transmutationEvent);
  };

  const handleArtifactEvent = (event: any) => {
    const transmutationEvent: TransmutationEvent = {
      id: generateEventId(),
      type: 'artifact_bundling',
      status: 'active',
      timestamp: new Date().toISOString(),
      details: `Artifact bundled: ${event.detail.artifactName || 'Unnamed'}`,
    };
    
    addTransmutationEvent(transmutationEvent);
    bundleArtifactToIpfs(transmutationEvent);
  };

  const handleThemeEvent = (event: any) => {
    const transmutationEvent: TransmutationEvent = {
      id: generateEventId(),
      type: 'theme_rotation',
      status: 'active',
      timestamp: new Date().toISOString(),
      details: `Dashboard theme rotated: ${event.detail.theme || 'Default'}`,
    };
    
    addTransmutationEvent(transmutationEvent);
    processThemeRotation(transmutationEvent);
  };

  const addTransmutationEvent = (event: TransmutationEvent) => {
    setEvents(prev => [event, ...prev.slice(0, 9)]); // Keep last 10 events
  };

  const triggerTransmutationLog = async (event: TransmutationEvent) => {
    try {
      // Send to automation backend for logging
      await fetch('/api/transmutation/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
      });

      // Update event status
      updateEventStatus(event.id, 'completed');
    } catch (error) {
      console.error('Failed to log transmutation event:', error);
      updateEventStatus(event.id, 'failed');
    }
  };

  const processContributorOnboarding = async (event: TransmutationEvent) => {
    try {
      // Process contributor onboarding workflow
      const response = await fetch('/api/contributors/onboard', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ eventId: event.id, details: event.details })
      });

      if (response.ok) {
        updateEventStatus(event.id, 'completed');
      } else {
        updateEventStatus(event.id, 'failed');
      }
    } catch (error) {
      console.error('Contributor onboarding failed:', error);
      updateEventStatus(event.id, 'failed');
    }
  };

  const bundleArtifactToIpfs = async (event: TransmutationEvent) => {
    try {
      // Bundle artifact and upload to IPFS
      const response = await fetch('/api/artifacts/bundle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ eventId: event.id, details: event.details })
      });

      if (response.ok) {
        const data = await response.json();
        // Update event with IPFS hash
        setEvents(prev => prev.map(e => 
          e.id === event.id ? { ...e, ipfsHash: data.ipfsHash } : e
        ));
        updateEventStatus(event.id, 'completed');
      } else {
        updateEventStatus(event.id, 'failed');
      }
    } catch (error) {
      console.error('Artifact bundling failed:', error);
      updateEventStatus(event.id, 'failed');
    }
  };

  const processThemeRotation = async (event: TransmutationEvent) => {
    try {
      // Process theme rotation for dashboard
      await fetch('/api/dashboard/rotate-theme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ eventId: event.id, details: event.details })
      });

      updateEventStatus(event.id, 'completed');
    } catch (error) {
      console.error('Theme rotation failed:', error);
      updateEventStatus(event.id, 'failed');
    }
  };

  const updateEventStatus = (eventId: string, status: TransmutationEvent['status']) => {
    setEvents(prev => prev.map(event => 
      event.id === eventId ? { ...event, status } : event
    ));
  };

  const initializeRituals = () => {
    const defaultRituals: RitualSchedule[] = [
      {
        id: 'glyph-rotation',
        name: 'Glyph Constellation Rotation',
        type: 'glyph_rotation',
        schedule: '0 0 * * 0', // Weekly on Sunday
        nextRun: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active'
      },
      {
        id: 'lineage-archival',
        name: 'Lineage Log Archival',
        type: 'lineage_archival',
        schedule: '0 2 1 * *', // Monthly on 1st at 2 AM
        nextRun: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        status: 'active'
      }
    ];
    
    setRituals(defaultRituals);
  };

  const connectWallet = async () => {
    try {
      if (typeof window !== 'undefined' && (window as any).ethereum) {
        await (window as any).ethereum.request({ method: 'eth_requestAccounts' });
        setWalletConnected(true);
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
    }
  };

  const generateEventId = () => {
    return `transmutation-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  const getEventIcon = (type: TransmutationEvent['type']) => {
    switch (type) {
      case 'ci_cd':
        return <GitBranch className="w-4 h-4" />;
      case 'contributor_onboarding':
        return <Users className="w-4 h-4" />;
      case 'artifact_bundling':
        return <Archive className="w-4 h-4" />;
      case 'theme_rotation':
        return <Palette className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status: TransmutationEvent['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'active':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="p-6 bg-gray-900 text-white min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
              Ritual Node Transmutation
            </h1>
            <p className="text-gray-400 mt-2">Automation Framework Integration Hub</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${isConnected ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
              <Activity className="w-4 h-4" />
              <span className="text-sm font-medium">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            <button
              onClick={connectWallet}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
                walletConnected 
                  ? 'bg-green-900 text-green-300' 
                  : 'bg-purple-700 hover:bg-purple-600 text-white'
              }`}
            >
              <Shield className="w-4 h-4" />
              <span className="text-sm font-medium">
                {walletConnected ? 'Wallet Connected' : 'Connect Wallet'}
              </span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Transmutation Events */}
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-6">
              <Zap className="w-6 h-6 text-yellow-400" />
              <h2 className="text-xl font-semibold">Transmutation Events</h2>
            </div>
            
            <div className="space-y-4">
              {events.length > 0 ? (
                events.map((event) => (
                  <div key={event.id} className="bg-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getEventIcon(event.type)}
                        <div>
                          <p className="font-medium">{event.details}</p>
                          <p className="text-sm text-gray-400">
                            {new Date(event.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(event.status)}`}>
                        {event.status}
                      </span>
                    </div>
                    {event.ipfsHash && (
                      <div className="mt-2 flex items-center space-x-2 text-sm text-blue-400">
                        <Upload className="w-3 h-3" />
                        <span>IPFS: {event.ipfsHash.slice(0, 20)}...</span>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-400 py-8">
                  <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No transmutation events yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Scheduled Rituals */}
          <div className="bg-gray-800 rounded-lg p-6">
            <div className="flex items-center space-x-2 mb-6">
              <Archive className="w-6 h-6 text-purple-400" />
              <h2 className="text-xl font-semibold">Scheduled Rituals</h2>
            </div>
            
            <div className="space-y-4">
              {rituals.map((ritual) => (
                <div key={ritual.id} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{ritual.name}</p>
                      <p className="text-sm text-gray-400">
                        Next run: {new Date(ritual.nextRun).toLocaleString()}
                      </p>
                      {ritual.lastRun && (
                        <p className="text-xs text-gray-500">
                          Last run: {new Date(ritual.lastRun).toLocaleString()}
                        </p>
                      )}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      ritual.status === 'active' 
                        ? 'text-green-600 bg-green-100' 
                        : 'text-gray-600 bg-gray-100'
                    }`}>
                      {ritual.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RitualNodeTransmutation;