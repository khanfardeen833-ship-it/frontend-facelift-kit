import React, { useState } from 'react';
import {
  Play,
  CheckCircle,
  AlertCircle,
  Clock,
  Users,
  Zap,
  ArrowRight,
  Settings,
  Info
} from 'lucide-react';

const QuickInterviewSetup = ({ ticketId, onSetupComplete }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [existingRounds, setExistingRounds] = useState(null);
  const [deletingRounds, setDeletingRounds] = useState(false);

  const handleQuickSetup = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}/setup-default`, {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.success) {
        setSuccess(true);
        if (onSetupComplete) {
          onSetupComplete(data.data);
        }
      } else {
        if (data.error && data.error.includes('already exist')) {
          setExistingRounds(data.existing_rounds || 0);
        }
        setError(data.error || 'Failed to setup interview rounds');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRounds = async () => {
    try {
      setDeletingRounds(true);
      setError(null);
      
      const response = await fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}`, {
        method: 'DELETE',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.success) {
        setExistingRounds(null);
        setError(null);
        // Now try to setup the default rounds again
        await handleQuickSetup();
      } else {
        setError(data.error || 'Failed to delete existing rounds');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setDeletingRounds(false);
    }
  };

  if (success) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-6 h-6 text-green-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-green-800">Interview Rounds Created!</h3>
            <p className="text-green-700">3-round interview process is ready</p>
          </div>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-green-200">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
              1
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">HR Round</h4>
              <p className="text-sm text-gray-600">45 minutes • Initial screening</p>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400" />
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-green-200">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-semibold text-sm">
              2
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">Technical Round</h4>
              <p className="text-sm text-gray-600">90 minutes • Skills assessment</p>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-400" />
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-white rounded-lg border border-green-200">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-semibold text-sm">
              3
            </div>
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">HR Final Round</h4>
              <p className="text-sm text-gray-600">60 minutes • Final decision</p>
            </div>
            <CheckCircle className="w-4 h-4 text-green-500" />
          </div>
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center space-x-2 text-blue-800 text-sm">
            <Zap className="w-4 h-4" />
            <span className="font-medium">Ready to schedule interviews!</span>
          </div>
          <p className="text-blue-700 text-sm mt-1">
            You can now schedule interviews for candidates through the Interview Manager.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 max-h-full overflow-y-auto">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <Settings className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Quick Interview Setup</h3>
          <p className="text-gray-600">Set up standard 3-round interview process</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2 text-red-800 mb-3">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm font-medium">{error}</span>
          </div>
          
          {existingRounds && (
            <div className="space-y-3">
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2 text-blue-800 mb-2">
                  <Info className="w-4 h-4" />
                  <span className="font-medium">Options:</span>
                </div>
                <div className="space-y-2 text-sm text-blue-700">
                  <p>• <strong>Use existing rounds:</strong> You can schedule interviews using the current {existingRounds} round(s)</p>
                  <p>• <strong>Replace rounds:</strong> Delete existing rounds and create the standard 3-round system</p>
                </div>
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setError(null);
                    setExistingRounds(null);
                    if (onSetupComplete) {
                      onSetupComplete({ message: 'Using existing rounds' });
                    }
                  }}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm transition-colors"
                >
                  Use Existing Rounds
                </button>
                <button
                  onClick={handleDeleteRounds}
                  disabled={deletingRounds}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-lg font-medium text-sm transition-colors"
                >
                  {deletingRounds ? 'Deleting...' : 'Replace with 3-Round System'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mb-6">
        <h4 className="font-medium text-gray-900 mb-3">Interview Process Overview</h4>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">
              1
            </div>
            <div className="flex-1">
              <h5 className="font-medium text-gray-900">HR Round</h5>
              <p className="text-sm text-gray-600">Initial screening, experience review, salary discussion</p>
            </div>
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">45 min</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center text-purple-600 font-semibold text-sm">
              2
            </div>
            <div className="flex-1">
              <h5 className="font-medium text-gray-900">Technical Round</h5>
              <p className="text-sm text-gray-600">Technical skills, coding challenges, system design</p>
            </div>
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">90 min</span>
          </div>
          
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-600 font-semibold text-sm">
              3
            </div>
            <div className="flex-1">
              <h5 className="font-medium text-gray-900">HR Final Round</h5>
              <p className="text-sm text-gray-600">Cultural fit, final behavioral, offer discussion</p>
            </div>
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">60 min</span>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4" />
            <span>Standard 3-round process</span>
          </div>
        </div>
        
        <button
          onClick={handleQuickSetup}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-medium flex items-center space-x-2 transition-colors"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Setting up...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              <span>Setup Interview Rounds</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default QuickInterviewSetup;
