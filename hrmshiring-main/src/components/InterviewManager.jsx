import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Users, Video, Phone, MapPin, Edit, Trash2, Eye, Plus, X, CheckCircle, AlertCircle } from 'lucide-react';
import { API_CONFIG } from '../config/api';
import EditInterviewModal from './EditInterviewModal';
import DeleteConfirmationModal from './DeleteConfirmationModal';
import InterviewScheduler from './InterviewScheduler';

const InterviewManager = ({ ticketId, jobTitle, onClose, onInterviewScheduled }) => {
  console.log('InterviewManager: Component initialized with ticketId:', ticketId, 'jobTitle:', jobTitle);
  
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [editingInterview, setEditingInterview] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deletingInterview, setDeletingInterview] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loadingCandidates, setLoadingCandidates] = useState(false);

  useEffect(() => {
    fetchInterviews();
    fetchCandidates();
    
    // Add timeout to prevent infinite loading
    const timeout = setTimeout(() => {
      if (loading) {
        console.warn('InterviewManager loading timeout - forcing completion');
        setLoading(false);
        setError('Loading timeout - please refresh to try again');
      }
    }, 10000); // 10 second timeout
    
    // Force loading to false after 3 seconds for testing
    const forceTimeout = setTimeout(() => {
      console.log('InterviewManager: Force timeout - showing interface');
      setLoading(false);
    }, 3000);
    
    return () => {
      clearTimeout(timeout);
      clearTimeout(forceTimeout);
    };
  }, [ticketId]);

  const fetchCandidates = async () => {
    try {
      setLoadingCandidates(true);
      const url = `${API_CONFIG.BASE_URL}/api/interviews/candidates/${ticketId}?api_key=${API_CONFIG.API_KEY}`;
      console.log('InterviewManager: Fetching candidates from:', url);
      const response = await fetch(url);
      
      if (!response.ok) {
        console.warn(`Failed to fetch candidates: ${response.status}`);
        // Don't throw error, just set empty candidates
        setCandidates([]);
        return;
      }
      
      const data = await response.json();
      console.log('InterviewManager: Candidates response:', data);
      
      if (data.success) {
        setCandidates(data.data.candidates);
      } else {
        console.error('Failed to fetch candidates:', data.error);
        setCandidates([]);
      }
    } catch (err) {
      console.error('Error fetching candidates:', err);
      setCandidates([]);
    } finally {
      setLoadingCandidates(false);
    }
  };

  const fetchInterviews = async () => {
    try {
      setLoading(true);
      console.log('Fetching interviews for ticket:', ticketId);
      const url = `${API_CONFIG.BASE_URL}/api/interviews/ticket/${ticketId}?api_key=${API_CONFIG.API_KEY}`;
      console.log('InterviewManager: Fetching interviews from:', url);
      const response = await fetch(url);
      
      if (!response.ok) {
        console.warn(`Failed to fetch interviews: ${response.status}`);
        // Don't throw error, just set empty interviews
        setInterviews([]);
        return;
      }
      
      const data = await response.json();
      console.log('InterviewManager: Interviews response:', data);
      
      if (data.success) {
        console.log('Fetched interviews:', data.data.interviews);
        setInterviews(data.data.interviews);
      } else {
        console.error('Failed to fetch interviews:', data.error);
        setInterviews([]);
      }
    } catch (err) {
      console.error('Error fetching interviews:', err);
      setInterviews([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteInterview = async () => {
    if (!deletingInterview) return;
    
    setDeleteLoading(true);
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${deletingInterview.id}?api_key=${API_CONFIG.API_KEY}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        // Remove the deleted interview from the list
        setInterviews(prev => prev.filter(interview => interview.id !== deletingInterview.id));
        setSuccessMessage('Interview deleted successfully!');
        setShowDeleteModal(false);
        setDeletingInterview(null);
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000);
      } else {
        setError(data.error || 'Failed to delete interview');
      }
    } catch (err) {
      console.error('Error deleting interview:', err);
      setError('Error deleting interview: ' + err.message);
    } finally {
      setDeleteLoading(false);
    }
  };

  const initiateDeleteInterview = (interview) => {
    setDeletingInterview(interview);
    setShowDeleteModal(true);
  };

  const handleEditInterview = (interview) => {
    setEditingInterview(interview);
    setShowEditModal(true);
  };

  const handleUpdateInterview = (updatedInterview) => {
    // Defensive check to ensure updatedInterview exists and has an id
    if (!updatedInterview || !updatedInterview.id) {
      console.error('Invalid updatedInterview object:', updatedInterview);
      return;
    }
    
    setInterviews(prev => prev.map(interview => 
      interview.id === updatedInterview.id ? updatedInterview : interview
    ));
    setShowEditModal(false);
    setEditingInterview(null);
  };

  const formatDateTime = (date, time) => {
    try {
      // Handle different date formats
      let dateObj;
      
      // If date is a full HTTP date string (like "Wed, 12 Mar 2025 00:00:00 GMT")
      if (date && typeof date === 'string' && date.includes(',') && date.includes('GMT')) {
        // Parse the full date string directly
        dateObj = new Date(date);
        
        // If we have a separate time, we need to combine them
        if (time && typeof time === 'string') {
          // Extract just the time part (HH:MM or HH:MM:SS)
          let timeStr = time;
          if (timeStr.includes(':')) {
            // Keep only HH:MM part if seconds are included
            timeStr = timeStr.split(':').slice(0, 2).join(':');
          }
          
          // Create a new date by combining the date with the time
          const [hours, minutes] = timeStr.split(':').map(Number);
          dateObj.setHours(hours, minutes, 0, 0);
        }
      } else {
        // Handle ISO format or other date formats
        let dateStr = date;
        let timeStr = time;
        
        // If date is already in ISO format, extract just the date part
        if (date && date.includes('T')) {
          dateStr = date.split('T')[0];
        }
        
        // If time is already in ISO format, extract just the time part
        if (time && time.includes('T')) {
          timeStr = time.split('T')[1]?.split('.')[0] || time;
        }
        
        // Ensure we have valid date and time
        if (!dateStr || !timeStr) {
          return 'Date/Time not set';
        }
        
        // Handle time format - if it's just HH:MM:SS, ensure it's properly formatted
        if (timeStr && timeStr.includes(':') && timeStr.split(':').length >= 2) {
          // Keep only HH:MM part if seconds are included
          timeStr = timeStr.split(':').slice(0, 2).join(':');
        }
        
        // Create the date object
        dateObj = new Date(dateStr + 'T' + timeStr);
      }
      
      // Check if the date is valid
      if (isNaN(dateObj.getTime())) {
        console.warn('Invalid date/time:', { date, time });
        return 'Invalid Date/Time';
      }
      
      // Format date as DD/MM/YYYY HH:MM
      const day = String(dateObj.getDate()).padStart(2, '0');
      const month = String(dateObj.getMonth() + 1).padStart(2, '0');
      const year = dateObj.getFullYear();
      const hours = String(dateObj.getHours()).padStart(2, '0');
      const minutes = String(dateObj.getMinutes()).padStart(2, '0');
      
      return `${day}/${month}/${year} ${hours}:${minutes}`;
    } catch (error) {
      console.error('Error formatting date/time:', error, { date, time });
      return 'Date/Time Error';
    }
  };

  const getInterviewTypeIcon = (type) => {
    switch (type) {
      case 'video_call':
        return <Video className="w-4 h-4" />;
      case 'phone_call':
        return <Phone className="w-4 h-4" />;
      case 'in_person':
        return <MapPin className="w-4 h-4" />;
      default:
        return <Calendar className="w-4 h-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'rescheduled':
        return 'bg-yellow-100 text-yellow-800';
      case 'no_show':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-[10000] overflow-y-auto">
        <div className="flex min-h-screen items-center justify-center p-4">
          <div className="fixed inset-0 bg-white/95 backdrop-blur-lg" onClick={onClose} />
          <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-gray-800">Interview Manager</h3>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto px-6 py-4">
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <span className="ml-2 text-gray-600">Loading interviews...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-[10000] overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-white/95 backdrop-blur-lg" onClick={onClose} />
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-gray-800">Interview Manager</h3>
                <p className="text-gray-600 mt-1">{jobTitle}</p>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setShowScheduleModal(true)}
                  className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Schedule New Interview
                </button>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {error && (
              <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded flex items-center">
                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                {error}
              </div>
            )}
            
            {successMessage && (
              <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 flex-shrink-0" />
                {successMessage}
              </div>
            )}

            {interviews.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No interviews scheduled</h3>
                <p className="text-gray-500 mb-4">Get started by scheduling your first interview.</p>
                <button
                  onClick={() => setShowScheduleModal(true)}
                  className="flex items-center mx-auto px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Schedule Interview
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {interviews.map((interview) => (
                  <div key={interview.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-3">
                          <h4 className="text-lg font-semibold text-gray-900">
                            {interview.applicant_name}
                          </h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(interview.status)}`}>
                            {interview.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        
                                                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                           <div className="flex items-center space-x-2">
                             <Calendar className="w-4 h-4 text-gray-500" />
                             <span className="text-sm text-gray-600">
                               {formatDateTime(interview.scheduled_date, interview.scheduled_time)}
                             </span>
                           </div>
                          
                          <div className="flex items-center space-x-2">
                            {getInterviewTypeIcon(interview.interview_type)}
                            <span className="text-sm text-gray-600 capitalize">
                              {interview.interview_type.replace('_', ' ')}
                            </span>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <Clock className="w-4 h-4 text-gray-500" />
                            <span className="text-sm text-gray-600">
                              {interview.duration_minutes} minutes
                            </span>
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium text-gray-700">Round:</span>
                            <span className="text-sm text-gray-600">{interview.round_name}</span>
                          </div>
                          
                          {interview.interviewers && (
                            <div className="flex items-center space-x-2">
                              <Users className="w-4 h-4 text-gray-500" />
                              <span className="text-sm text-gray-600">{interview.interviewers}</span>
                            </div>
                          )}
                          
                          {interview.meeting_link && (
                            <div className="flex items-center space-x-2">
                              <Video className="w-4 h-4 text-gray-500" />
                              <a 
                                href={interview.meeting_link} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-sm text-indigo-600 hover:text-indigo-800"
                              >
                                Join Meeting
                              </a>
                            </div>
                          )}
                          
                          {interview.notes && (
                            <div className="mt-3 p-3 bg-gray-50 rounded">
                              <span className="text-sm text-gray-600">{interview.notes}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 ml-4">
                        <button
                          onClick={() => handleEditInterview(interview)}
                          className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                          title="Edit Interview"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={() => initiateDeleteInterview(interview)}
                          className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                          title="Delete Interview"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Edit Interview Modal */}
      {showEditModal && editingInterview && (
        <EditInterviewModal
          interview={editingInterview}
          onClose={() => {
            setShowEditModal(false);
            setEditingInterview(null);
          }}
          onUpdate={(updatedInterview) => {
            handleUpdateInterview(updatedInterview);
            setSuccessMessage('Interview updated successfully!');
            setTimeout(() => setSuccessMessage(null), 3000);
          }}
        />
      )}
      
      {/* Schedule Interview Modal */}
      {showScheduleModal && (
        <div className="fixed inset-0 z-[60] overflow-y-auto">
          <div className="flex min-h-screen items-center justify-center p-4">
            <div className="fixed inset-0 bg-white/95 backdrop-blur-lg" onClick={() => setShowScheduleModal(false)} />
            <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[95vh] overflow-hidden flex flex-col">
              {/* Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800">Schedule Interview</h3>
                    <p className="text-gray-600 mt-1">{jobTitle}</p>
                  </div>
                  <button 
                    onClick={() => {
                      setShowScheduleModal(false);
                      setSelectedCandidate(null);
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
              </div>
              
              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {!selectedCandidate ? (
                  <div>
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">Select a Candidate</h4>
                    {loadingCandidates ? (
                      <div className="flex items-center justify-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                        <span className="ml-2 text-gray-600">Loading candidates...</span>
                      </div>
                    ) : candidates.length === 0 ? (
                      <div className="text-center py-8">
                        <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600">No candidates available for this job.</p>
                        <p className="text-sm text-gray-500 mt-1">Candidates need to apply first before interviews can be scheduled.</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {candidates.map((candidate) => (
                          <div
                            key={candidate.id}
                            onClick={() => setSelectedCandidate(candidate)}
                            className="border border-gray-200 rounded-lg p-4 hover:border-indigo-300 hover:shadow-md cursor-pointer transition-all"
                          >
                            <div className="flex items-center space-x-3 mb-3">
                              <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center">
                                <span className="text-indigo-600 font-semibold">
                                  {candidate.applicant_name?.charAt(0) || '?'}
                                </span>
                              </div>
                              <div>
                                <h5 className="font-medium text-gray-900">{candidate.applicant_name || 'Unknown'}</h5>
                                <p className="text-sm text-gray-500">{candidate.applicant_email || 'No email'}</p>
                              </div>
                            </div>
                            <div className="text-sm text-gray-600">
                              <p>Status: <span className="font-medium">{candidate.interview_status}</span></p>
                              {candidate.rounds_completed > 0 && (
                                <p>Rounds: {candidate.rounds_completed}/{candidate.total_rounds}</p>
                              )}
                              {/* Final Decision Display */}
                              {candidate.final_decision && (
                                <div className="mt-2">
                                  <span className="text-xs font-medium text-gray-500">Final Decision:</span>
                                  <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ml-1 ${
                                    candidate.final_decision === 'hire' || candidate.final_decision === 'strong_hire' 
                                      ? 'bg-green-100 text-green-800 border border-green-200' :
                                    candidate.final_decision === 'reject' || candidate.final_decision === 'strong_reject'
                                      ? 'bg-red-100 text-red-800 border border-red-200' :
                                    candidate.final_decision === 'maybe'
                                      ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                                    'bg-gray-100 text-gray-800 border border-gray-200'
                                  }`}>
                                    {candidate.final_decision === 'hire' || candidate.final_decision === 'strong_hire' ? '✓ HIRE' :
                                     candidate.final_decision === 'reject' || candidate.final_decision === 'strong_reject' ? '✗ REJECT' :
                                     candidate.final_decision === 'maybe' ? '⏸ HOLD' :
                                     candidate.final_decision.toUpperCase()}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h4 className="text-lg font-semibold text-gray-800">Schedule Interview for {selectedCandidate.applicant_name}</h4>
                        <p className="text-sm text-gray-600">{selectedCandidate.applicant_email}</p>
                      </div>
                      <button
                        onClick={() => setSelectedCandidate(null)}
                        className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                      >
                        ← Back to candidates
                      </button>
                    </div>
                    <InterviewScheduler
                      ticketId={ticketId}
                      candidateId={selectedCandidate.id}
                      onInterviewScheduled={(interviewId) => {
                        console.log('Interview scheduled:', interviewId);
                        setShowScheduleModal(false);
                        setSelectedCandidate(null);
                        fetchInterviews(); // Refresh the interview list
                        if (onInterviewScheduled) {
                          onInterviewScheduled(interviewId);
                        }
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Delete Confirmation Modal */}
      {showDeleteModal && deletingInterview && (
        <DeleteConfirmationModal
          interview={deletingInterview}
          onConfirm={handleDeleteInterview}
          onCancel={() => {
            setShowDeleteModal(false);
            setDeletingInterview(null);
          }}
          loading={deleteLoading}
        />
      )}
    </div>
  );
};

export default InterviewManager;
