import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Users,
  CheckCircle,
  AlertCircle,
  Play,
  ArrowRight,
  Info
} from 'lucide-react';

const ExistingRoundsView = ({ ticketId, onScheduleInterview }) => {
  const [rounds, setRounds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchExistingRounds();
  }, [ticketId]);

  const fetchExistingRounds = async () => {
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
        setError('Failed to fetch existing rounds');
      }
    } catch (err) {
      setError('Error fetching existing rounds');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading existing rounds...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <div className="flex items-center space-x-2 text-red-800">
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">{error}</span>
        </div>
      </div>
    );
  }

  if (rounds.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
        <div className="flex items-center space-x-2 text-yellow-800">
          <Info className="w-5 h-5" />
          <span className="font-medium">No interview rounds found</span>
        </div>
        <p className="text-yellow-700 text-sm mt-2">
          Please set up interview rounds first before scheduling interviews.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-6 max-h-full overflow-y-auto">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
          <CheckCircle className="w-6 h-6 text-green-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-green-800">Existing Interview Rounds</h3>
          <p className="text-green-700">{rounds.length} round(s) configured</p>
        </div>
      </div>
      
      <div className="space-y-3 mb-6">
        {rounds.map((round, index) => (
          <div key={round.id} className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-green-200">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
              {index + 1}
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{round.round_name}</h4>
              <p className="text-sm text-gray-600">{round.description || 'No description'}</p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="w-4 h-4" />
            </div>
            <div className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {round.round_type}
            </div>
          </div>
        ))}
      </div>
      
      <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center space-x-2 text-blue-800 text-sm mb-2">
          <Info className="w-4 h-4" />
          <span className="font-medium">Ready to schedule interviews!</span>
        </div>
        <p className="text-blue-700 text-sm mb-3">
          You can now schedule interviews for candidates using these existing rounds.
        </p>
        
        <div className="flex space-x-3">
          <button
            onClick={() => onScheduleInterview && onScheduleInterview(rounds)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm transition-colors flex items-center space-x-2"
          >
            <Calendar className="w-4 h-4" />
            <span>Schedule Interviews</span>
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium text-sm transition-colors flex items-center space-x-2"
          >
            <Play className="w-4 h-4" />
            <span>View Candidates</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExistingRoundsView;
