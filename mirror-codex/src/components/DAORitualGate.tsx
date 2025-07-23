'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Key, Shield, Users, Vote, Lock, Unlock, CheckCircle, XCircle } from 'lucide-react';

interface DAOMember {
  id: string;
  address: string;
  votingPower: number;
  status: 'active' | 'pending' | 'revoked';
  joinedAt: Date;
}

interface Proposal {
  id: string;
  title: string;
  description: string;
  type: 'governance' | 'ritual' | 'treasury' | 'codex';
  status: 'pending' | 'active' | 'passed' | 'rejected';
  votesFor: number;
  votesAgainst: number;
  quorumRequired: number;
  deadline: Date;
  creator: string;
}

interface QuorumStatus {
  current: number;
  required: number;
  percentage: number;
  isReached: boolean;
}

const DAORitualGate: React.FC = () => {
  const [isSealed, setIsSealed] = useState(true);
  const [members, setMembers] = useState<DAOMember[]>([]);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [quorumStatus, setQuorumStatus] = useState<QuorumStatus>({
    current: 0,
    required: 3,
    percentage: 0,
    isReached: false
  });
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [userAddress, setUserAddress] = useState('');
  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    type: 'governance' as Proposal['type']
  });
  const [showCreateProposal, setShowCreateProposal] = useState(false);

  const updateQuorumStatus = React.useCallback(() => {
    const activeMembers = members.filter(m => m.status === 'active');
    const totalVotingPower = activeMembers.reduce((sum, member) => sum + member.votingPower, 0);
    const requiredQuorum = Math.ceil(totalVotingPower * 0.51); // 51% quorum
    
    setQuorumStatus({
      current: totalVotingPower,
      required: requiredQuorum,
      percentage: totalVotingPower > 0 ? (totalVotingPower / requiredQuorum) * 100 : 0,
      isReached: totalVotingPower >= requiredQuorum
    });
  }, [members]);

  useEffect(() => {
    initializeDAO();
  }, []);

  useEffect(() => {
    updateQuorumStatus();
  }, [updateQuorumStatus]);

  const initializeDAO = () => {
    // Initialize sample DAO members
    const sampleMembers: DAOMember[] = [
      {
        id: '1',
        address: '0x1234...abcd',
        votingPower: 100,
        status: 'active',
        joinedAt: new Date('2024-01-01')
      },
      {
        id: '2',
        address: '0x5678...efgh',
        votingPower: 150,
        status: 'active',
        joinedAt: new Date('2024-01-15')
      },
      {
        id: '3',
        address: '0x9abc...ijkl',
        votingPower: 75,
        status: 'pending',
        joinedAt: new Date('2024-01-20')
      }
    ];

    // Initialize sample proposals
    const sampleProposals: Proposal[] = [
      {
        id: '1',
        title: 'Codex Access Protocol',
        description: 'Establish protocols for accessing sacred codex functions',
        type: 'codex',
        status: 'active',
        votesFor: 200,
        votesAgainst: 50,
        quorumRequired: 250,
        deadline: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days from now
        creator: '0x1234...abcd'
      },
      {
        id: '2',
        title: 'Ritual Gate Seal Amendment',
        description: 'Update the conditions for unsealing the ritual gate',
        type: 'ritual',
        status: 'pending',
        votesFor: 0,
        votesAgainst: 0,
        quorumRequired: 200,
        deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000), // 14 days from now
        creator: '0x5678...efgh'
      }
    ];

    setMembers(sampleMembers);
    setProposals(sampleProposals);
  };

  const handleUnsealGate = () => {
    if (quorumStatus.isReached) {
      setIsSealed(false);
    }
  };

  const handleSealGate = () => {
    setIsSealed(true);
  };

  const handleVote = (proposalId: string, voteFor: boolean) => {
    if (!userAddress) return;

    setProposals(prev => prev.map(proposal => {
      if (proposal.id === proposalId) {
        const votePower = 100; // Assume user has 100 voting power
        return {
          ...proposal,
          votesFor: voteFor ? proposal.votesFor + votePower : proposal.votesFor,
          votesAgainst: !voteFor ? proposal.votesAgainst + votePower : proposal.votesAgainst
        };
      }
      return proposal;
    }));
  };

  const handleCreateProposal = () => {
    if (!newProposal.title || !newProposal.description || !userAddress) return;

    const proposal: Proposal = {
      id: (proposals.length + 1).toString(),
      title: newProposal.title,
      description: newProposal.description,
      type: newProposal.type,
      status: 'pending',
      votesFor: 0,
      votesAgainst: 0,
      quorumRequired: 200,
      deadline: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
      creator: userAddress
    };

    setProposals(prev => [...prev, proposal]);
    setNewProposal({ title: '', description: '', type: 'governance' });
    setShowCreateProposal(false);
  };

  const getProposalStatusColor = (status: string) => {
    switch (status) {
      case 'passed': return 'text-green-400';
      case 'rejected': return 'text-red-400';
      case 'active': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getProposalTypeColor = (type: string) => {
    switch (type) {
      case 'ritual': return 'from-purple-400 to-pink-400';
      case 'codex': return 'from-blue-400 to-cyan-400';
      case 'treasury': return 'from-green-400 to-emerald-400';
      default: return 'from-gray-400 to-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-white mb-2">DAO Ritual Gate</h2>
        <p className="text-gray-300">Financial quorum and ritual gating mechanism</p>
      </div>

      {/* Gate Status */}
      <motion.div
        animate={isSealed ? { 
          boxShadow: ['0 0 20px rgba(239, 68, 68, 0.3)', '0 0 30px rgba(239, 68, 68, 0.5)', '0 0 20px rgba(239, 68, 68, 0.3)']
        } : {
          boxShadow: ['0 0 20px rgba(34, 197, 94, 0.3)', '0 0 30px rgba(34, 197, 94, 0.5)', '0 0 20px rgba(34, 197, 94, 0.3)']
        }}
        transition={{ duration: 2, repeat: Infinity }}
        className={`
          bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-8 text-center border-2
          ${isSealed ? 'border-red-500' : 'border-green-500'}
        `}
      >
        <motion.div
          animate={{ rotate: isSealed ? 0 : 360 }}
          transition={{ duration: 1 }}
          className="text-6xl mb-4"
        >
          {isSealed ? <Lock className="text-red-400 mx-auto" size={64} /> : <Unlock className="text-green-400 mx-auto" size={64} />}
        </motion.div>
        
        <h3 className={`text-2xl font-bold mb-2 ${isSealed ? 'text-red-400' : 'text-green-400'}`}>
          Gate Status: {isSealed ? 'SEALED' : 'UNSEALED'}
        </h3>
        
        <p className="text-gray-300 mb-4">
          {isSealed 
            ? 'The ritual gate requires quorum consensus to unseal' 
            : 'The codex is accessible through the unsealed gate'
          }
        </p>

        <div className="flex justify-center space-x-4">
          {isSealed && quorumStatus.isReached && (
            <button
              onClick={handleUnsealGate}
              className="flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Unlock size={20} />
              <span>Unseal Gate</span>
            </button>
          )}
          
          {!isSealed && (
            <button
              onClick={handleSealGate}
              className="flex items-center space-x-2 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
            >
              <Lock size={20} />
              <span>Seal Gate</span>
            </button>
          )}
        </div>
      </motion.div>

      {/* Quorum Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30">
          <div className="flex items-center space-x-2 mb-4">
            <Users className="text-purple-400" size={24} />
            <h3 className="text-lg font-semibold text-white">Quorum Status</h3>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-300">Current Power:</span>
              <span className="text-white font-medium">{quorumStatus.current}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">Required:</span>
              <span className="text-white font-medium">{quorumStatus.required}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(quorumStatus.percentage, 100)}%` }}
                className={`h-2 rounded-full ${
                  quorumStatus.isReached ? 'bg-green-500' : 'bg-purple-500'
                }`}
              />
            </div>
            <div className="text-center">
              {quorumStatus.isReached ? (
                <span className="text-green-400 flex items-center justify-center space-x-1">
                  <CheckCircle size={16} />
                  <span>Quorum Reached</span>
                </span>
              ) : (
                <span className="text-yellow-400 flex items-center justify-center space-x-1">
                  <XCircle size={16} />
                  <span>Insufficient Quorum</span>
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30">
          <div className="flex items-center space-x-2 mb-4">
            <Shield className="text-blue-400" size={24} />
            <h3 className="text-lg font-semibold text-white">DAO Members</h3>
          </div>
          
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {members.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-2 bg-gray-800 rounded">
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm truncate">{member.address}</p>
                  <p className="text-xs text-gray-400">Power: {member.votingPower}</p>
                </div>
                <div className={`
                  px-2 py-1 text-xs rounded-full
                  ${member.status === 'active' ? 'bg-green-600 text-green-100' :
                    member.status === 'pending' ? 'bg-yellow-600 text-yellow-100' :
                    'bg-red-600 text-red-100'}
                `}>
                  {member.status}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30">
          <div className="flex items-center space-x-2 mb-4">
            <Key className="text-yellow-400" size={24} />
            <h3 className="text-lg font-semibold text-white">Wallet Connection</h3>
          </div>
          
          <div className="space-y-3">
            <input
              type="text"
              value={userAddress}
              onChange={(e) => setUserAddress(e.target.value)}
              placeholder="0x1234...abcd"
              className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none text-sm"
            />
            <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm">
              Connect Wallet
            </button>
          </div>
        </div>
      </div>

      {/* Proposals Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white flex items-center space-x-2">
              <Vote size={20} />
              <span>Active Proposals</span>
            </h3>
            <button
              onClick={() => setShowCreateProposal(true)}
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors text-sm"
            >
              Create Proposal
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {proposals.map((proposal) => (
              <motion.div
                key={proposal.id}
                layout
                whileHover={{ scale: 1.02 }}
                onClick={() => setSelectedProposal(proposal)}
                className={`
                  p-4 rounded-lg border cursor-pointer transition-all
                  ${selectedProposal?.id === proposal.id 
                    ? 'border-purple-500 bg-purple-900 bg-opacity-30' 
                    : 'border-gray-600 bg-black bg-opacity-20 hover:border-gray-500'
                  }
                `}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="text-white font-medium text-sm">{proposal.title}</h4>
                  <span className={`text-xs ${getProposalStatusColor(proposal.status)}`}>
                    {proposal.status.toUpperCase()}
                  </span>
                </div>
                
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`
                    px-2 py-1 text-xs rounded-full text-white
                    bg-gradient-to-r ${getProposalTypeColor(proposal.type)}
                  `}>
                    {proposal.type}
                  </span>
                  <span className="text-xs text-gray-400">
                    Deadline: {proposal.deadline.toLocaleDateString()}
                  </span>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">For: {proposal.votesFor}</span>
                    <span className="text-gray-400">Against: {proposal.votesAgainst}</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1">
                    <div
                      className="h-1 bg-green-500 rounded-full"
                      style={{ 
                        width: `${Math.min((proposal.votesFor / proposal.quorumRequired) * 100, 100)}%` 
                      }}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Proposal Details */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-white">Proposal Details</h3>
          
          {selectedProposal ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-black bg-opacity-40 backdrop-blur-md rounded-lg p-6 border border-purple-500 border-opacity-30"
            >
              <div className="space-y-4">
                <div>
                  <h4 className="text-white font-medium text-lg">{selectedProposal.title}</h4>
                  <p className="text-gray-300 text-sm mt-2">{selectedProposal.description}</p>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <div className={`
                      inline-block ml-2 px-2 py-1 text-xs rounded-full text-white
                      bg-gradient-to-r ${getProposalTypeColor(selectedProposal.type)}
                    `}>
                      {selectedProposal.type}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-400">Status:</span>
                    <span className={`ml-2 ${getProposalStatusColor(selectedProposal.status)}`}>
                      {selectedProposal.status}
                    </span>
                  </div>
                  <div className="col-span-2">
                    <span className="text-gray-400">Creator:</span>
                    <span className="text-white ml-2 font-mono text-xs">{selectedProposal.creator}</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">Voting Progress</span>
                    <span className="text-gray-400">
                      {selectedProposal.votesFor + selectedProposal.votesAgainst} / {selectedProposal.quorumRequired}
                    </span>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-green-400 text-sm">For: {selectedProposal.votesFor}</span>
                      <span className="text-red-400 text-sm">Against: {selectedProposal.votesAgainst}</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className="flex h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-green-500"
                          style={{ 
                            width: `${(selectedProposal.votesFor / selectedProposal.quorumRequired) * 100}%` 
                          }}
                        />
                        <div
                          className="bg-red-500"
                          style={{ 
                            width: `${(selectedProposal.votesAgainst / selectedProposal.quorumRequired) * 100}%` 
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {userAddress && selectedProposal.status === 'active' && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleVote(selectedProposal.id, true)}
                      className="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Vote For
                    </button>
                    <button
                      onClick={() => handleVote(selectedProposal.id, false)}
                      className="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Vote Against
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          ) : (
            <div className="bg-black bg-opacity-20 rounded-lg p-8 text-center border border-gray-700">
              <Vote className="text-gray-500 mx-auto mb-4" size={48} />
              <p className="text-gray-500">Select a proposal to view details</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Proposal Modal */}
      <AnimatePresence>
        {showCreateProposal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-900 rounded-lg p-6 max-w-md w-full mx-4 border border-purple-500"
            >
              <h3 className="text-lg font-semibold text-white mb-4">Create New Proposal</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    value={newProposal.title}
                    onChange={(e) => setNewProposal(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                    placeholder="Proposal title..."
                  />
                </div>
                
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Description
                  </label>
                  <textarea
                    value={newProposal.description}
                    onChange={(e) => setNewProposal(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                    placeholder="Proposal description..."
                  />
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Type
                  </label>
                  <select
                    value={newProposal.type}
                    onChange={(e) => setNewProposal(prev => ({ ...prev, type: e.target.value as Proposal['type'] }))}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:border-purple-500 focus:outline-none"
                  >
                    <option value="governance">Governance</option>
                    <option value="ritual">Ritual</option>
                    <option value="treasury">Treasury</option>
                    <option value="codex">Codex</option>
                  </select>
                </div>

                <div className="flex space-x-3">
                  <button
                    onClick={handleCreateProposal}
                    disabled={!newProposal.title || !newProposal.description || !userAddress}
                    className="flex-1 bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Create
                  </button>
                  <button
                    onClick={() => setShowCreateProposal(false)}
                    className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DAORitualGate;