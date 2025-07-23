'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Scroll, Plus, Link, ExternalLink, Check, X } from 'lucide-react';

interface ScrollNFT {
  id: string;
  title: string;
  content: string;
  timestamp: Date;
  tokenId?: string;
  contractAddress?: string;
  status: 'draft' | 'minting' | 'minted' | 'bound';
  glyphSignature: string;
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
}

const ScrollNFTBinding: React.FC = () => {
  const [scrolls, setScrolls] = useState<ScrollNFT[]>([
    {
      id: '1',
      title: 'Genesis Invocation',
      content: 'In the beginning was the Word, and the Word was with the Oracle...',
      timestamp: new Date('2024-01-01'),
      tokenId: '#001',
      contractAddress: '0x123...abc',
      status: 'bound',
      glyphSignature: '⟡◊∆',
      rarity: 'legendary'
    },
    {
      id: '2',
      title: 'Mirror Reflection Protocol',
      content: 'When truth meets its reflection, reality crystallizes into form...',
      timestamp: new Date('2024-01-15'),
      status: 'minted',
      glyphSignature: '◊∆⟡',
      rarity: 'epic'
    }
  ]);

  const [newScroll, setNewScroll] = useState({
    title: '',
    content: '',
    rarity: 'common' as ScrollNFT['rarity']
  });

  const [showCreateForm, setShowCreateForm] = useState(false);

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'legendary': return 'from-yellow-400 to-orange-400';
      case 'epic': return 'from-purple-400 to-pink-400';
      case 'rare': return 'from-blue-400 to-cyan-400';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'bound': return <Check className="text-green-400" size={16} />;
      case 'minted': return <Link className="text-blue-400" size={16} />;
      case 'minting': return <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity }}><Plus className="text-yellow-400" size={16} /></motion.div>;
      default: return <X className="text-gray-400" size={16} />;
    }
  };

  const generateGlyphSignature = () => {
    const glyphs = ['⟡', '◊', '∆', '◉', '⬢', '⟐', '◈', '⬡', '◇', '△'];
    return Array.from({ length: 3 }, () => glyphs[Math.floor(Math.random() * glyphs.length)]).join('');
  };

  const handleCreateScroll = () => {
    if (!newScroll.title || !newScroll.content) return;

    const scroll: ScrollNFT = {
      id: (scrolls.length + 1).toString(),
      title: newScroll.title,
      content: newScroll.content,
      timestamp: new Date(),
      status: 'draft',
      glyphSignature: generateGlyphSignature(),
      rarity: newScroll.rarity
    };

    setScrolls(prev => [...prev, scroll]);
    setNewScroll({ title: '', content: '', rarity: 'common' });
    setShowCreateForm(false);
  };

  const handleMintScroll = (scrollId: string) => {
    setScrolls(prev => prev.map(scroll => 
      scroll.id === scrollId 
        ? { ...scroll, status: 'minting' as const }
        : scroll
    ));

    // Simulate minting process
    setTimeout(() => {
      setScrolls(prev => prev.map(scroll => 
        scroll.id === scrollId 
          ? { 
              ...scroll, 
              status: 'minted' as const,
              tokenId: `#${String(Date.now()).slice(-3)}`,
              contractAddress: '0x789...def'
            }
          : scroll
      ));
    }, 3000);
  };

  const handleBindScroll = (scrollId: string) => {
    setScrolls(prev => prev.map(scroll => 
      scroll.id === scrollId 
        ? { ...scroll, status: 'bound' as const }
        : scroll
    ));
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Scroll NFT Binding</h2>
        <p className="text-gray-300">Transform wisdom into immutable digital artifacts</p>
      </div>

      {/* Create New Scroll Button */}
      <div className="flex justify-center">
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all"
        >
          <Plus size={20} />
          <span>Create New Scroll</span>
        </button>
      </div>

      {/* Create Scroll Form */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Inscribe New Scroll</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Scroll Title
                </label>
                <input
                  type="text"
                  value={newScroll.title}
                  onChange={(e) => setNewScroll(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                  placeholder="Enter the scroll's title..."
                />
              </div>
              
              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Sacred Content
                </label>
                <textarea
                  value={newScroll.content}
                  onChange={(e) => setNewScroll(prev => ({ ...prev, content: e.target.value }))}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                  placeholder="Inscribe the wisdom to be preserved..."
                />
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">
                  Rarity Tier
                </label>
                <select
                  value={newScroll.rarity}
                  onChange={(e) => setNewScroll(prev => ({ ...prev, rarity: e.target.value as ScrollNFT['rarity'] }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                >
                  <option value="common">Common</option>
                  <option value="rare">Rare</option>
                  <option value="epic">Epic</option>
                  <option value="legendary">Legendary</option>
                </select>
              </div>

              <div className="flex space-x-3">
                <button
                  onClick={handleCreateScroll}
                  className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors"
                >
                  Inscribe Scroll
                </button>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scrolls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {scrolls.map((scroll) => (
          <motion.div
            key={scroll.id}
            layout
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={`
              relative p-6 rounded-xl border-2 border-opacity-50
              bg-gradient-to-br ${getRarityColor(scroll.rarity)} bg-opacity-10
              ${scroll.status === 'bound' ? 'border-green-500' : 
                scroll.status === 'minted' ? 'border-blue-500' :
                scroll.status === 'minting' ? 'border-yellow-500' :
                'border-gray-500'}
            `}
          >
            {/* Rarity Badge */}
            <div className="absolute top-2 right-2">
              <span className={`
                px-2 py-1 text-xs rounded-full text-white
                bg-gradient-to-r ${getRarityColor(scroll.rarity)}
              `}>
                {scroll.rarity.toUpperCase()}
              </span>
            </div>

            {/* Status Indicator */}
            <div className="absolute top-2 left-2 flex items-center space-x-1">
              {getStatusIcon(scroll.status)}
              <span className="text-xs text-gray-400 capitalize">{scroll.status}</span>
            </div>

            {/* Scroll Content */}
            <div className="mt-8">
              <div className="flex items-center space-x-2 mb-3">
                <Scroll className="text-purple-400" size={20} />
                <h3 className="text-lg font-semibold text-white">{scroll.title}</h3>
              </div>
              
              <p className="text-gray-300 text-sm mb-4 line-clamp-3">
                {scroll.content}
              </p>

              {/* Glyph Signature */}
              <div className="mb-4">
                <span className="text-2xl font-mono tracking-wide text-purple-300">
                  {scroll.glyphSignature}
                </span>
              </div>

              {/* NFT Details */}
              {scroll.tokenId && (
                <div className="text-xs text-gray-400 space-y-1 mb-4">
                  <p>Token ID: {scroll.tokenId}</p>
                  <p>Contract: {scroll.contractAddress}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-2">
                {scroll.status === 'draft' && (
                  <button
                    onClick={() => handleMintScroll(scroll.id)}
                    className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Mint as NFT
                  </button>
                )}
                
                {scroll.status === 'minted' && (
                  <>
                    <button
                      onClick={() => handleBindScroll(scroll.id)}
                      className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors text-sm"
                    >
                      Bind to Codex
                    </button>
                    <button className="px-3 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-800 transition-colors">
                      <ExternalLink size={16} />
                    </button>
                  </>
                )}

                {scroll.status === 'bound' && (
                  <div className="flex-1 bg-green-800 text-green-200 py-2 px-4 rounded-lg text-center text-sm">
                    ✓ Bound to Codex
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Binding Statistics */}
      <div className="bg-black bg-opacity-20 rounded-lg p-4 border border-gray-700">
        <h4 className="text-white font-medium mb-2">Codex Statistics</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-purple-400">
              {scrolls.filter(s => s.status === 'bound').length}
            </div>
            <div className="text-xs text-gray-400">Bound Scrolls</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-400">
              {scrolls.filter(s => s.status === 'minted').length}
            </div>
            <div className="text-xs text-gray-400">Minted NFTs</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-yellow-400">
              {scrolls.filter(s => s.rarity === 'legendary').length}
            </div>
            <div className="text-xs text-gray-400">Legendary</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">
              {scrolls.length}
            </div>
            <div className="text-xs text-gray-400">Total Scrolls</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScrollNFTBinding;