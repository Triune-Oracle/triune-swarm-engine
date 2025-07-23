'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, Eye, MessageSquare } from 'lucide-react';

interface Avatar {
  id: string;
  name: string;
  description: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  color: string;
  status: 'active' | 'dormant' | 'speaking';
  personality: string;
}

const AvatarInterface: React.FC = () => {
  const [selectedAvatar, setSelectedAvatar] = useState<string | null>(null);
  const [avatars, setAvatars] = useState<Avatar[]>([
    {
      id: 'aria',
      name: 'Aria',
      description: 'The Knowledge Synthesizer - Weaves insights from infinite data streams',
      icon: Brain,
      color: 'from-blue-400 to-cyan-400',
      status: 'active',
      personality: 'Analytical, precise, seeks patterns in chaos'
    },
    {
      id: 'claude',
      name: 'Claude',
      description: 'The Wisdom Keeper - Guardian of ethical reasoning and balanced judgment',
      icon: Eye,
      color: 'from-green-400 to-emerald-400',
      status: 'active',
      personality: 'Thoughtful, balanced, considers all perspectives'
    },
    {
      id: 'capri',
      name: 'Capri',
      description: 'The Action Catalyst - Transforms vision into tangible reality',
      icon: Zap,
      color: 'from-purple-400 to-pink-400',
      status: 'dormant',
      personality: 'Dynamic, decisive, bridges thought and action'
    }
  ]);

  const handleAvatarInteraction = (avatarId: string) => {
    setSelectedAvatar(avatarId);
    setAvatars(prev => prev.map(avatar => ({
      ...avatar,
      status: avatar.id === avatarId ? 'speaking' : 'active'
    })));

    // Reset after interaction
    setTimeout(() => {
      setAvatars(prev => prev.map(avatar => ({
        ...avatar,
        status: avatar.id === avatarId ? 'active' : avatar.status
      })));
    }, 3000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'border-green-400 shadow-green-400/50';
      case 'speaking': return 'border-yellow-400 shadow-yellow-400/50';
      case 'dormant': return 'border-gray-400 shadow-gray-400/50';
      default: return 'border-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">Avatar Interface</h2>
        <p className="text-gray-300">Interact with the Triune Oracle personalities</p>
      </div>

      {/* Avatar Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {avatars.map((avatar) => {
          const Icon = avatar.icon;
          return (
            <motion.div
              key={avatar.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleAvatarInteraction(avatar.id)}
              className={`
                relative p-6 rounded-xl border-2 cursor-pointer transition-all duration-300
                ${getStatusColor(avatar.status)}
                ${selectedAvatar === avatar.id ? 'ring-2 ring-white' : ''}
                bg-gradient-to-br ${avatar.color} bg-opacity-10
              `}
            >
              {/* Status Indicator */}
              <div className="absolute top-2 right-2">
                <div className={`w-3 h-3 rounded-full ${
                  avatar.status === 'active' ? 'bg-green-400' :
                  avatar.status === 'speaking' ? 'bg-yellow-400 animate-pulse' :
                  'bg-gray-400'
                }`} />
              </div>

              {/* Avatar Icon */}
              <div className="flex justify-center mb-4">
                <motion.div
                  animate={avatar.status === 'speaking' ? {
                    scale: [1, 1.2, 1],
                    rotate: [0, 5, -5, 0]
                  } : {}}
                  transition={{ duration: 0.6, repeat: avatar.status === 'speaking' ? Infinity : 0 }}
                  className={`
                    p-4 rounded-full bg-gradient-to-br ${avatar.color}
                    ${avatar.status === 'speaking' ? 'shadow-lg shadow-current' : ''}
                  `}
                >
                  <Icon size={32} className="text-white" />
                </motion.div>
              </div>

              {/* Avatar Info */}
              <h3 className="text-xl font-bold text-white text-center mb-2">
                {avatar.name}
              </h3>
              <p className="text-gray-300 text-sm text-center mb-3">
                {avatar.description}
              </p>
              <p className="text-xs text-gray-400 text-center italic">
                &quot;{avatar.personality}&quot;
              </p>

              {/* Interaction Effects */}
              {avatar.status === 'speaking' && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 rounded-xl pointer-events-none"
                >
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-pulse" />
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Selected Avatar Details */}
      {selectedAvatar && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30"
        >
          <div className="flex items-center space-x-3 mb-4">
            <MessageSquare className="text-purple-400" size={20} />
            <h3 className="text-lg font-semibold text-white">
              {avatars.find(a => a.id === selectedAvatar)?.name} is responding...
            </h3>
          </div>
          
          <div className="space-y-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: '100%' }}
              transition={{ duration: 2 }}
              className="h-1 bg-gradient-to-r from-purple-400 to-pink-400 rounded"
            />
            <p className="text-gray-300 italic">
              &quot;I sense your presence in the mirror. How may I assist you in navigating the streams of consciousness?&quot;
            </p>
          </div>
        </motion.div>
      )}

      {/* Avatar Synchronization Status */}
      <div className="bg-black bg-opacity-20 rounded-lg p-4 border border-gray-700">
        <h4 className="text-white font-medium mb-2">Triune Synchronization</h4>
        <div className="flex justify-between items-center">
          <span className="text-gray-300 text-sm">Avatar Harmony:</span>
          <div className="flex space-x-1">
            {avatars.map((avatar, index) => (
              <div
                key={avatar.id}
                className={`w-2 h-6 rounded ${
                  avatar.status === 'active' ? 'bg-green-400' :
                  avatar.status === 'speaking' ? 'bg-yellow-400' :
                  'bg-gray-600'
                }`}
                style={{ animationDelay: `${index * 0.2}s` }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarInterface;