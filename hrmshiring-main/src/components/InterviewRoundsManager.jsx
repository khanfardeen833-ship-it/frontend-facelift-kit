import React, { useState, useEffect } from 'react';
import {
  Plus,
  Trash2,
  Edit,
  Save,
  X,
  Calendar,
  Clock,
  Users,
  Settings,
  CheckCircle,
  AlertCircle,
  Info,
  Zap,
  Play
} from 'lucide-react';
import QuickInterviewSetup from './QuickInterviewSetup';
import ExistingRoundsView from './ExistingRoundsView';

const InterviewRoundsManager = ({ ticketId, onRoundsCreated }) => {
  const [rounds, setRounds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingRound, setEditingRound] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [showQuickSetup, setShowQuickSetup] = useState(false);
  const [showExistingRounds, setShowExistingRounds] = useState(false);

  const roundTypes = [
    { value: 'technical', label: 'Technical Interview' },
    { value: 'hr', label: 'HR Interview' },
    { value: 'final', label: 'Final Interview' },
    { value: 'cultural', label: 'Cultural Fit' },
    { value: 'case_study', label: 'Case Study' },
    { value: 'presentation', label: 'Presentation' },
    { value: 'other', label: 'Other' }
  ];

  const defaultRound = {
    round_name: '',
    round_type: 'technical',
    duration_minutes: 60,
    description: '',
    requirements: '',
    is_required: true,
    can_skip: false
  };

  const [newRound, setNewRound] = useState(defaultRound);

  useEffect(() => {
    if (ticketId) {
      fetchRounds();
    }
  }, [ticketId]);

  useEffect(() => {
    // Show existing rounds if they exist
    if (rounds.length > 0 && !showForm && !showQuickSetup) {
      setShowExistingRounds(true);
    }
  }, [rounds, showForm, showQuickSetup]);

  const fetchRounds = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}`, {
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRounds(data.data?.rounds || []);
      } else {
        setError('Failed to fetch interview rounds');
      }
    } catch (err) {
      setError('Error fetching interview rounds');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRounds = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/interviews/rounds', {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ticket_id: ticketId,
          rounds: rounds
        })
      });

      if (response.ok) {
        const data = await response.json();
        setShowForm(false);
        setRounds([]);
        setNewRound(defaultRound);
        if (onRoundsCreated) {
          onRoundsCreated(data.data?.rounds || []);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to create interview rounds');
      }
    } catch (err) {
      setError('Error creating interview rounds');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSetupComplete = (data) => {
    fetchRounds();
    setShowQuickSetup(false);
    if (onRoundsCreated) {
      onRoundsCreated(data);
    }
  };

  const handleScheduleInterview = (rounds) => {
    // This will be handled by the parent component
    if (onRoundsCreated) {
      onRoundsCreated({ rounds, action: 'schedule' });
    }
  };

  const addRound = () => {
    if (newRound.round_name.trim()) {
      setRounds([...rounds, { ...newRound, id: Date.now() }]);
      setNewRound(defaultRound);
    }
  };

  const removeRound = (index) => {
    setRounds(rounds.filter((_, i) => i !== index));
  };

  const updateRound = (index, field, value) => {
    const updatedRounds = [...rounds];
    updatedRounds[index] = { ...updatedRounds[index], [field]: value };
    setRounds(updatedRounds);
  };

  const moveRound = (index, direction) => {
    if ((direction === 'up' && index === 0) || (direction === 'down' && index === rounds.length - 1)) {
      return;
    }

    const updatedRounds = [...rounds];
    const newIndex = direction === 'up' ? index - 1 : index + 1;
    [updatedRounds[index], updatedRounds[newIndex]] = [updatedRounds[newIndex], updatedRounds[index]];
    setRounds(updatedRounds);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Interview Rounds</h3>
          <p className="text-sm text-gray-600">Configure interview rounds for this position</p>
        </div>
                 {!showForm && !showQuickSetup && !showExistingRounds && (
           <div className="flex space-x-3">
             <button
               onClick={() => setShowQuickSetup(true)}
               className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
             >
               <Zap className="w-4 h-4 mr-2" />
               Quick Setup
             </button>
             <button
               onClick={() => setShowForm(true)}
               className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
             >
               <Plus className="w-4 h-4 mr-2" />
               Custom Setup
             </button>
           </div>
         )}
         {showExistingRounds && (
           <div className="flex space-x-3">
             <button
               onClick={() => setShowQuickSetup(true)}
               className="flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
             >
               <Zap className="w-4 h-4 mr-2" />
               Reconfigure
             </button>
             <button
               onClick={() => setShowForm(true)}
               className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
             >
               <Plus className="w-4 h-4 mr-2" />
               Add More
             </button>
           </div>
         )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
            <span className="text-red-800">{error}</span>
          </div>
        </div>
      )}

      {showQuickSetup ? (
        <QuickInterviewSetup 
          ticketId={ticketId} 
          onSetupComplete={handleQuickSetupComplete}
        />
      ) : showExistingRounds ? (
        <ExistingRoundsView 
          ticketId={ticketId} 
          onScheduleInterview={handleScheduleInterview}
        />
      ) : showForm ? (
        <div className="space-y-6">
          {/* Add New Round Form */}
          <div className="bg-gray-50 p-4 rounded-md">
            <h4 className="font-medium text-gray-900 mb-4">Add New Round</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Round Name *
                </label>
                <input
                  type="text"
                  value={newRound.round_name}
                  onChange={(e) => setNewRound({ ...newRound, round_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="e.g., Technical Screening"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Round Type
                </label>
                <select
                  value={newRound.round_type}
                  onChange={(e) => setNewRound({ ...newRound, round_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {roundTypes.map(type => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  value={newRound.duration_minutes}
                  onChange={(e) => setNewRound({ ...newRound, duration_minutes: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  min="15"
                  max="480"
                />
              </div>
              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newRound.is_required}
                    onChange={(e) => setNewRound({ ...newRound, is_required: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Required</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newRound.can_skip}
                    onChange={(e) => setNewRound({ ...newRound, can_skip: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Can Skip</span>
                </label>
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={newRound.description}
                onChange={(e) => setNewRound({ ...newRound, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="2"
                placeholder="Brief description of this round..."
              />
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Requirements
              </label>
              <textarea
                value={newRound.requirements}
                onChange={(e) => setNewRound({ ...newRound, requirements: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="2"
                placeholder="Specific requirements or preparation needed..."
              />
            </div>
            <div className="mt-4 flex justify-end">
              <button
                onClick={addRound}
                disabled={!newRound.round_name.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Round
              </button>
            </div>
          </div>

          {/* Rounds List */}
          {rounds.length > 0 && (
            <div>
              <h4 className="font-medium text-gray-900 mb-4">Configured Rounds ({rounds.length})</h4>
              <div className="space-y-3">
                {rounds.map((round, index) => (
                  <div key={round.id} className="bg-white border border-gray-200 rounded-md p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="flex items-center justify-center w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full text-sm font-medium">
                          {index + 1}
                        </span>
                        <div>
                          <h5 className="font-medium text-gray-900">{round.round_name}</h5>
                          <p className="text-sm text-gray-600">
                            {roundTypes.find(t => t.value === round.round_type)?.label}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => moveRound(index, 'up')}
                          disabled={index === 0}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          ↑
                        </button>
                        <button
                          onClick={() => moveRound(index, 'down')}
                          disabled={index === rounds.length - 1}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          ↓
                        </button>
                        <button
                          onClick={() => removeRound(index)}
                          className="p-1 text-red-400 hover:text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    {round.description && (
                      <p className="mt-2 text-sm text-gray-600">{round.description}</p>
                    )}
                    <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                      {round.is_required && (
                        <span className="flex items-center">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Required
                        </span>
                      )}
                      {round.can_skip && (
                        <span className="flex items-center">
                          <Info className="w-3 h-3 mr-1" />
                          Can Skip
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setShowForm(false);
                setRounds([]);
                setNewRound(defaultRound);
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleCreateRounds}
              disabled={rounds.length === 0 || loading}
              className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : `Create ${rounds.length} Round${rounds.length !== 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No interview rounds configured yet.</p>
          <p className="text-sm text-gray-500 mt-1">Click "Add Rounds" to get started.</p>
        </div>
      )}
    </div>
  );
};

export default InterviewRoundsManager;
