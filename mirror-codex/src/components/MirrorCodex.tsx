'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Shield, Scroll, Database, Key } from 'lucide-react';
import AvatarInterface from './AvatarInterface';
import ScrollNFTBinding from './ScrollNFTBinding';
import AnimatedGlyphChat from './AnimatedGlyphChat';
import MemoryStorage from './MemoryStorage';
import DAORitualGate from './DAORitualGate';

const MirrorCodex: React.FC = () => {
  const [activeTab, setActiveTab] = useState('mirror');
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Initialize the codex
    setTimeout(() => setIsInitialized(true), 1000);
  }, []);

  const tabs = [
    { id: 'mirror', label: 'Mirror', icon: Sparkles },
    { id: 'avatars', label: 'Avatars', icon: Shield },
    { id: 'scrolls', label: 'Scrolls', icon: Scroll },
    { id: 'memory', label: 'Memory', icon: Database },
    { id: 'dao', label: 'DAO Gate', icon: Key },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            🪞 Mirror Codex
          </h1>
          <p className="text-gray-300">
            The Triune Oracle Gateway - Where Reality Reflects Truth
          </p>
          <div className="mt-4 text-sm text-purple-300">
            Memory Identifier: {process.env.NEXT_PUBLIC_MEMORY_IDENTIFIER}
          </div>
        </motion.div>

        {/* Initialization Animation */}
        <AnimatePresence>
          {!isInitialized && (
            <motion.div
              initial={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50"
            >
              <motion.div
                animate={{ 
                  scale: [1, 1.2, 1],
                  rotate: [0, 180, 360]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="text-6xl"
              >
                🪞
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-full p-1">
            <div className="flex space-x-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all ${
                      activeTab === tab.id
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-300 hover:text-white hover:bg-white hover:bg-opacity-10'
                    }`}
                  >
                    <Icon size={16} />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="bg-black bg-opacity-20 backdrop-blur-md rounded-lg border border-purple-500 border-opacity-30 p-6"
        >
          {activeTab === 'mirror' && <AnimatedGlyphChat />}
          {activeTab === 'avatars' && <AvatarInterface />}
          {activeTab === 'scrolls' && <ScrollNFTBinding />}
          {activeTab === 'memory' && <MemoryStorage />}
          {activeTab === 'dao' && <DAORitualGate />}
        </motion.div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-400 text-sm">
          <p>Sealed by the Triune Oracle • Powered by Groq • Deployed on Vercel</p>
        </div>
      </div>
    </div>
  );
};

export default MirrorCodex;