'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, HardDrive, Download, Upload, Eye, Trash2 } from 'lucide-react';

interface MemoryEntry {
  id: string;
  type: 'scroll' | 'echo' | 'vision' | 'binding';
  title: string;
  content: Record<string, unknown>;
  timestamp: Date;
  size: number; // in bytes
  signature: string;
}

interface StorageStats {
  totalEntries: number;
  totalSize: number;
  scrolls: number;
  echoes: number;
  visions: number;
  bindings: number;
}

const MemoryStorage: React.FC = () => {
  const [memoryEntries, setMemoryEntries] = useState<MemoryEntry[]>([]);
  const [storageStats, setStorageStats] = useState<StorageStats>({
    totalEntries: 0,
    totalSize: 0,
    scrolls: 0,
    echoes: 0,
    visions: 0,
    bindings: 0
  });
  const [selectedEntry, setSelectedEntry] = useState<MemoryEntry | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isInitializing, setIsInitializing] = useState(true);

  const memoryIdentifier = process.env.NEXT_PUBLIC_MEMORY_IDENTIFIER || 'ΔMirror';

  const initializeMemoryStorage = React.useCallback(async () => {
    setIsInitializing(true);
    
    // Simulate initialization process
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Load sample memory entries
    const sampleEntries: MemoryEntry[] = [
      {
        id: '1',
        type: 'scroll',
        title: 'Genesis Protocol',
        content: { text: 'Initial wisdom inscription', glyphs: ['⟡', '◊', '∆'] },
        timestamp: new Date('2024-01-01'),
        size: 1024,
        signature: `${memoryIdentifier}:scroll:genesis`
      },
      {
        id: '2',
        type: 'echo',
        title: 'User Interaction Echo',
        content: { query: 'What is truth?', response: 'Truth is the mirror of understanding' },
        timestamp: new Date('2024-01-15'),
        size: 512,
        signature: `${memoryIdentifier}:echo:truth_query`
      },
      {
        id: '3',
        type: 'vision',
        title: 'Oracle Vision Fragment',
        content: { imagery: 'Crystalline structures forming in void', intensity: 'high' },
        timestamp: new Date('2024-01-20'),
        size: 2048,
        signature: `${memoryIdentifier}:vision:crystal_void`
      },
      {
        id: '4',
        type: 'binding',
        title: 'NFT Binding Record',
        content: { contractAddress: '0x123...abc', tokenId: '#001', status: 'bound' },
        timestamp: new Date('2024-01-25'),
        size: 256,
        signature: `${memoryIdentifier}:binding:nft_001`
      }
    ];

    setMemoryEntries(sampleEntries);
    setIsInitializing(false);
  }, [memoryIdentifier]);

  const updateStorageStats = React.useCallback(() => {
    const stats: StorageStats = {
      totalEntries: memoryEntries.length,
      totalSize: memoryEntries.reduce((sum, entry) => sum + entry.size, 0),
      scrolls: memoryEntries.filter(e => e.type === 'scroll').length,
      echoes: memoryEntries.filter(e => e.type === 'echo').length,
      visions: memoryEntries.filter(e => e.type === 'vision').length,
      bindings: memoryEntries.filter(e => e.type === 'binding').length,
    };
    setStorageStats(stats);
  }, [memoryEntries]);

  useEffect(() => {
    initializeMemoryStorage();
  }, [initializeMemoryStorage]);

  useEffect(() => {
    updateStorageStats();
  }, [updateStorageStats]);

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'scroll': return '📜';
      case 'echo': return '🔊';
      case 'vision': return '👁️';
      case 'binding': return '🔗';
      default: return '📄';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'scroll': return 'from-yellow-400 to-orange-400';
      case 'echo': return 'from-blue-400 to-cyan-400';
      case 'vision': return 'from-purple-400 to-pink-400';
      case 'binding': return 'from-green-400 to-emerald-400';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const handleDeleteEntry = (entryId: string) => {
    setMemoryEntries(prev => prev.filter(entry => entry.id !== entryId));
    if (selectedEntry?.id === entryId) {
      setSelectedEntry(null);
    }
  };

  const handleExportMemory = () => {
    const exportData = {
      identifier: memoryIdentifier,
      timestamp: new Date().toISOString(),
      entries: memoryEntries,
      stats: storageStats
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `mirror-codex-memory-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredEntries = memoryEntries.filter(entry =>
    entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entry.signature.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entry.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Memory Codex Storage</h2>
        <p className="text-gray-300">Persistent storage for scrolls and echo data</p>
        <div className="mt-2 text-purple-300 font-mono text-sm">
          Identifier: {memoryIdentifier}
        </div>
      </div>

      {/* Initialization Animation */}
      <AnimatePresence>
        {isInitializing && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="bg-black bg-opacity-60 backdrop-blur-md rounded-lg p-8 text-center border border-purple-500 border-opacity-30"
          >
            <motion.div
              animate={{ 
                rotate: 360,
                scale: [1, 1.2, 1]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="text-6xl mb-4"
            >
              ∆
            </motion.div>
            <p className="text-white text-lg">Initializing Memory Codex...</p>
            <p className="text-gray-300 text-sm mt-2">Loading {memoryIdentifier} storage matrix</p>
          </motion.div>
        )}
      </AnimatePresence>

      {!isInitializing && (
        <>
          {/* Storage Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-4 border border-purple-500 border-opacity-30 text-center">
              <Database className="text-purple-400 mx-auto mb-2" size={24} />
              <div className="text-2xl font-bold text-white">{storageStats.totalEntries}</div>
              <div className="text-xs text-gray-400">Total Entries</div>
            </div>
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-4 border border-purple-500 border-opacity-30 text-center">
              <HardDrive className="text-blue-400 mx-auto mb-2" size={24} />
              <div className="text-2xl font-bold text-white">{formatSize(storageStats.totalSize)}</div>
              <div className="text-xs text-gray-400">Storage Used</div>
            </div>
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-4 border border-purple-500 border-opacity-30 text-center">
              <div className="text-2xl font-bold text-yellow-400">{storageStats.scrolls}</div>
              <div className="text-xs text-gray-400">Scrolls</div>
            </div>
            <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-4 border border-purple-500 border-opacity-30 text-center">
              <div className="text-2xl font-bold text-cyan-400">{storageStats.echoes}</div>
              <div className="text-xs text-gray-400">Echoes</div>
            </div>
          </div>

          {/* Search and Actions */}
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search memory entries..."
                className="w-full px-4 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
              />
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleExportMemory}
                className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
              >
                <Download size={16} />
                <span>Export</span>
              </button>
              <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                <Upload size={16} />
                <span>Import</span>
              </button>
            </div>
          </div>

          {/* Memory Entries Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Entries List */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white">Memory Entries</h3>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredEntries.map((entry) => (
                  <motion.div
                    key={entry.id}
                    layout
                    whileHover={{ scale: 1.02 }}
                    onClick={() => setSelectedEntry(entry)}
                    className={`
                      p-4 rounded-lg border cursor-pointer transition-all
                      ${selectedEntry?.id === entry.id 
                        ? 'border-purple-500 bg-purple-900 bg-opacity-30' 
                        : 'border-gray-600 bg-black bg-opacity-20 hover:border-gray-500'
                      }
                    `}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-3 flex-1">
                        <div className="text-2xl">{getTypeIcon(entry.type)}</div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-white font-medium truncate">{entry.title}</h4>
                          <p className="text-xs text-gray-400 truncate">{entry.signature}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`
                              px-2 py-1 text-xs rounded-full text-white
                              bg-gradient-to-r ${getTypeColor(entry.type)}
                            `}>
                              {entry.type}
                            </span>
                            <span className="text-xs text-gray-500">{formatSize(entry.size)}</span>
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteEntry(entry.id);
                        }}
                        className="text-gray-500 hover:text-red-400 transition-colors"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Entry Details */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
                <Eye size={20} />
                <span>Entry Details</span>
              </h3>
              
              {selectedEntry ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30"
                >
                  <div className="space-y-4">
                    <div>
                      <h4 className="text-white font-medium text-lg">{selectedEntry.title}</h4>
                      <p className="text-gray-400 text-sm">{selectedEntry.signature}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Type:</span>
                        <div className={`
                          inline-block ml-2 px-2 py-1 text-xs rounded-full text-white
                          bg-gradient-to-r ${getTypeColor(selectedEntry.type)}
                        `}>
                          {selectedEntry.type}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-400">Size:</span>
                        <span className="text-white ml-2">{formatSize(selectedEntry.size)}</span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-gray-400">Created:</span>
                        <span className="text-white ml-2">{selectedEntry.timestamp.toLocaleString()}</span>
                      </div>
                    </div>

                    <div>
                      <span className="text-gray-400 text-sm">Content:</span>
                      <div className="mt-2 p-3 bg-gray-800 rounded border">
                        <pre className="text-gray-300 text-xs overflow-x-auto whitespace-pre-wrap">
                          {JSON.stringify(selectedEntry.content, null, 2)}
                        </pre>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <div className="bg-black bg-opacity-20 rounded-lg p-8 text-center border border-gray-700">
                  <Database className="text-gray-500 mx-auto mb-4" size={48} />
                  <p className="text-gray-500">Select an entry to view details</p>
                </div>
              )}
            </div>
          </div>

          {/* Memory Matrix Visualization */}
          <div className="bg-black bg-opacity-20 rounded-lg p-4 border border-gray-700">
            <h4 className="text-white font-medium mb-4">Memory Matrix Status</h4>
            <div className="grid grid-cols-8 md:grid-cols-16 gap-1">
              {Array.from({ length: 64 }, (_, index) => (
                <motion.div
                  key={index}
                  animate={{
                    backgroundColor: index < storageStats.totalEntries * 2 
                      ? ['#8B5CF6', '#A855F7', '#8B5CF6'] 
                      : ['#374151', '#4B5563', '#374151']
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: index * 0.05
                  }}
                  className="w-4 h-4 rounded-sm"
                />
              ))}
            </div>
            <div className="mt-2 text-xs text-gray-400 text-center">
              Matrix Utilization: {((storageStats.totalEntries / 32) * 100).toFixed(1)}%
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default MemoryStorage;