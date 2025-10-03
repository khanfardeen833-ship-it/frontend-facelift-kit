import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Users,
  Video,
  Phone,
  MapPin,
  Save,
  X,
  AlertCircle,
  CheckCircle,
  Trash2,
  Plus
} from 'lucide-react';
import { API_CONFIG } from '../config/api';
import { formatDateForInput, formatDateForStorage, getMinDateForInput } from '../utils/dateUtils';
import CustomDateInput from './CustomDateInput';

const EditInterviewModal = ({ interview, onClose, onUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [interviewers, setInterviewers] = useState([]);
  const [rounds, setRounds] = useState([]);
  
  // Helper function to format date for input field (using utility function)
  const formatDateForInputLocal = (dateString) => {
    return formatDateForInput(dateString);
  };

  // Helper function to format time for input field
  const formatTimeForInput = (timeString) => {
    if (!timeString) return '';
    try {
      // Handle HH:MM:SS format
      if (timeString.match(/^\d{1,2}:\d{2}:\d{2}$/)) {
        const [hours, minutes] = timeString.split(':');
        return `${hours.padStart(2, '0')}:${minutes}`;
      }
      // Handle HH:MM format
      if (timeString.match(/^\d{1,2}:\d{2}$/)) {
        const [hours, minutes] = timeString.split(':');
        return `${hours.padStart(2, '0')}:${minutes}`;
      }
      return '';
    } catch (error) {
      console.error('Error formatting time:', error);
      return '';
    }
  };

  const [formData, setFormData] = useState({
    round_id: interview?.round_id || '',
    scheduled_date: formatDateForInputLocal(interview?.scheduled_date) || '',
    scheduled_time: formatTimeForInput(interview?.scheduled_time) || '',
    duration_minutes: interview?.duration_minutes || 60,
    interview_type: interview?.interview_type || 'video_call',
    meeting_link: interview?.meeting_link || '',
    location: interview?.location || '',
    notes: interview?.notes || '',
    status: interview?.status || 'scheduled',
    participants: []
  });

  const interviewTypes = [
    { value: 'video_call', label: 'Video Call', icon: Video },
    { value: 'phone_call', label: 'Phone Call', icon: Phone },
    { value: 'in_person', label: 'In Person', icon: MapPin },
    { value: 'online_test', label: 'Online Test', icon: CheckCircle }
  ];

  const interviewStatuses = [
    { value: 'scheduled', label: 'Scheduled', color: 'text-blue-600' },
    { value: 'completed', label: 'Completed', color: 'text-green-600' },
    { value: 'cancelled', label: 'Cancelled', color: 'text-red-600' },
    { value: 'rescheduled', label: 'Rescheduled', color: 'text-yellow-600' },
    { value: 'no_show', label: 'No Show', color: 'text-gray-600' }
  ];

  useEffect(() => {
    fetchInterviewers();
    fetchRounds();
    fetchParticipants();
  }, []);

  // Auto-generate meeting link when date/time changes for video calls
  useEffect(() => {
    if (
      formData.interview_type === 'video_call' &&
      formData.scheduled_date &&
      formData.scheduled_time &&
      !formData.meeting_link
    ) {
      console.log('Auto-generating meeting link for video call');
      const timer = setTimeout(() => {
        generateMeetingLink();
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [formData.scheduled_date, formData.scheduled_time, formData.interview_type]);

  // Also generate meeting link when interview type changes to video_call
  useEffect(() => {
    if (
      formData.interview_type === 'video_call' &&
      formData.scheduled_date &&
      formData.scheduled_time &&
      !formData.meeting_link
    ) {
      console.log('Interview type changed to video_call, generating meeting link');
      const timer = setTimeout(() => {
        generateMeetingLink();
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [formData.interview_type]);

  const fetchInterviewers = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/interviewers`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setInterviewers(data.data?.interviewers || []);
      }
    } catch (err) {
      console.error('Error fetching interviewers:', err);
    }
  };

  const fetchRounds = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/rounds/${interview.ticket_id}`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRounds(data.data?.rounds || []);
      }
    } catch (err) {
      console.error('Error fetching rounds:', err);
    }
  };

  const fetchParticipants = async () => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${interview.id}/participants`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data?.participants) {
          setFormData(prev => ({
            ...prev,
            participants: data.data.participants.map(p => ({
              ...p,
              id: p.id || Date.now() + Math.random()
            }))
          }));
        }
      }
    } catch (err) {
      console.error('Error fetching participants:', err);
    }
  };

  const handleUpdate = async () => {
    try {
      setLoading(true);
      setError(null);

      const requestData = {
        ...formData,
        ticket_id: interview.ticket_id,
        candidate_id: interview.candidate_id
      };

      console.log('Sending update request with data:', requestData);
      console.log('Meeting link in formData:', formData.meeting_link);

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${interview.id}`, {
        method: 'PUT',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const data = await response.json();
        setSuccessMessage('Interview updated successfully!');
        setTimeout(() => {
          // Ensure we pass the complete interview object with the updated data
          const updatedInterview = {
            ...interview,
            ...formData,
            ...(data.data || {})
          };
          onUpdate(updatedInterview);
          onClose();
        }, 1500);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to update interview');
      }
    } catch (err) {
      setError('Error updating interview: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const addParticipant = () => {
    const newParticipant = {
      id: Date.now(),
      interviewer_id: '',
      interviewer_name: '', // Add field for manual name entry
      interviewer_email: '',
      participant_type: 'interviewer',
      is_primary: formData.participants.length === 0,
      is_manager_feedback: false // Premium feature: manager feedback selection
    };
    
    setFormData(prev => ({
      ...prev,
      participants: [...prev.participants, newParticipant]
    }));
  };

  const removeParticipant = (participantId) => {
    setFormData(prev => ({
      ...prev,
      participants: prev.participants.filter(p => p.id !== participantId)
    }));
  };

  const updateParticipant = (participantId, field, value) => {
    setFormData(prev => {
      // Premium feature: Ensure only one manager can be selected for feedback
      if (field === 'is_manager_feedback' && value === true) {
        return {
          ...prev,
          participants: prev.participants.map(p => ({
            ...p,
            is_manager_feedback: p.id === participantId ? true : false
          }))
        };
      }
      
      return {
        ...prev,
        participants: prev.participants.map(p => 
          p.id === participantId ? { ...p, [field]: value } : p
        )
      };
    });
  };

  const generateFallbackMeetingLink = () => {
    // Generate a simple meeting link locally
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let code = '';
    for (let i = 0; i < 3; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    code += '-';
    for (let i = 0; i < 4; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    code += '-';
    for (let i = 0; i < 3; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return `https://meet.google.com/${code}`;
  };

  const generateMeetingLink = async () => {
    try {
      console.log('generateMeetingLink called with:', {
        scheduled_date: formData.scheduled_date,
        scheduled_time: formData.scheduled_time,
        duration_minutes: formData.duration_minutes
      });

      if (!formData.scheduled_date || !formData.scheduled_time) {
        setError('Please select date and time first');
        return;
      }

      const requestBody = {
        scheduled_date: formData.scheduled_date,
        scheduled_time: formData.scheduled_time,
        duration_minutes: formData.duration_minutes,
        interview_title: `Interview with ${interview.applicant_name}`
      };

      console.log('Sending generate meeting link request:', requestBody);

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/generate-meet-link`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Generate meeting link response:', data);
        if (data.success) {
          console.log('Setting meeting link to:', data.data.meeting_link);
          setFormData(prev => ({
            ...prev,
            meeting_link: data.data.meeting_link
          }));
          setSuccessMessage('Google Meet link generated successfully!');
          setTimeout(() => setSuccessMessage(null), 3000);
        } else {
          setError(data.error || 'Failed to generate meeting link');
        }
      } else {
        const errorText = await response.text();
        console.error('Generate meeting link failed:', errorText);
        
        // Fallback: Generate a simple meeting link locally
        console.log('Using fallback meeting link generation');
        const fallbackLink = generateFallbackMeetingLink();
        setFormData(prev => ({
          ...prev,
          meeting_link: fallbackLink
        }));
        setSuccessMessage('Fallback meeting link generated!');
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    } catch (err) {
      console.error('Error generating meeting link:', err);
      
      // Fallback: Generate a simple meeting link locally
      console.log('Using fallback meeting link generation due to error');
      const fallbackLink = generateFallbackMeetingLink();
      setFormData(prev => ({
        ...prev,
        meeting_link: fallbackLink
      }));
      setSuccessMessage('Fallback meeting link generated!');
      setTimeout(() => setSuccessMessage(null), 3000);
    }
  };

  const getParticipantDisplayName = (participant) => {
    // If manually entered name exists, use it
    if (participant.interviewer_name) {
      return participant.interviewer_name;
    }
    
    // If interviewer_id exists, find the interviewer name
    if (participant.interviewer_id) {
      const interviewer = interviewers.find(i => i.id == participant.interviewer_id);
      if (interviewer) {
        return `${interviewer.first_name} ${interviewer.last_name}`;
      }
    }
    
    // Fallback to email or "Unknown"
    return participant.interviewer_email || 'Unknown Interviewer';
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        <div className="fixed inset-0 bg-white/95 backdrop-blur-lg" onClick={onClose} />
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-gray-800">Edit Interview</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {interview.applicant_name} - {interview.round_name}
                </p>
              </div>
              <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-4">
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
                  <span className="text-red-800">{error}</span>
                </div>
              </div>
            )}

            {successMessage && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <div className="flex items-center">
                  <CheckCircle className="w-5 h-5 text-green-400 mr-2" />
                  <span className="text-green-800">{successMessage}</span>
                </div>
              </div>
            )}

            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interview Round
                  </label>
                  <select
                    value={formData.round_id}
                    onChange={(e) => setFormData({ ...formData, round_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">Select a round</option>
                    {rounds.map(round => (
                      <option key={round.id} value={round.id}>
                        {round.round_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {interviewStatuses.map(status => (
                      <option key={status.value} value={status.value}>
                        {status.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interview Type
                  </label>
                  <select
                    value={formData.interview_type}
                    onChange={(e) => setFormData({ ...formData, interview_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  >
                    {interviewTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    value={formData.duration_minutes}
                    onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    min="15"
                    max="480"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date
                  </label>
                  <CustomDateInput
                    value={formData.scheduled_date}
                    onChange={(value) => setFormData({ ...formData, scheduled_date: value })}
                    placeholder="dd/mm/yyyy"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Time
                  </label>
                  <input
                    type="time"
                    value={formData.scheduled_time}
                    onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                                 {formData.interview_type === 'video_call' && (
                   <div className="md:col-span-2">
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                       Meeting Link
                     </label>
                     <div className="flex space-x-2">
                       <input
                         type="url"
                         value={formData.meeting_link}
                         onChange={(e) => setFormData({ ...formData, meeting_link: e.target.value })}
                         className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                         placeholder="https://meet.google.com/..."
                       />
                       <button
                         type="button"
                         onClick={generateMeetingLink}
                         disabled={!formData.scheduled_date || !formData.scheduled_time}
                         className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                         title="Generate Google Meet Link"
                       >
                         <Video className="w-4 h-4" />
                       </button>
                     </div>
                                           {formData.meeting_link && (
                        <div className="mt-1">
                          <p className="text-xs text-green-600">
                            ✓ Meeting link generated for {formData.scheduled_date} at {formData.scheduled_time}
                          </p>
                          <p className="text-xs text-yellow-600 mt-1">
                            ⚠️ This is a placeholder link. Please create an actual Google Meet meeting and update this link.
                          </p>
                        </div>
                      )}
                   </div>
                 )}

                {formData.interview_type === 'in_person' && (
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      placeholder="Office address or room number"
                    />
                  </div>
                )}
              </div>

              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="font-medium text-gray-900">
                    Interview Participants
                    {formData.participants.length > 0 && (
                      <span className="ml-2 text-sm text-gray-500">
                        ({formData.participants.length} added)
                      </span>
                    )}
                  </h4>
                  <button
                    type="button"
                    onClick={addParticipant}
                    disabled={formData.participants.length >= 5}
                    className="flex items-center px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Participant
                  </button>
                </div>

                {formData.participants.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-500">No participants added yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {formData.participants.map((participant, index) => (
                      <div key={participant.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                        <div className="flex items-center justify-between mb-3">
                          <h5 className="text-sm font-medium text-gray-900">
                            Participant {index + 1}
                            {participant.is_primary && (
                              <span className="ml-2 px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700 rounded">
                                Primary
                              </span>
                            )}
                          </h5>
                          <button
                            type="button"
                            onClick={() => removeParticipant(participant.id)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>

                        {/* Display current interviewer name */}
                        <div className="mb-3 p-2 bg-blue-50 rounded border border-blue-200">
                          <span className="text-sm text-blue-700">
                            <strong>Current Interviewer:</strong> {getParticipantDisplayName(participant)}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Interviewer
                            </label>
                            <div className="space-y-2">
                              {/* Manual entry option */}
                              <input
                                type="text"
                                value={participant.interviewer_name || ''}
                                onChange={(e) => {
                                  updateParticipant(participant.id, 'interviewer_name', e.target.value);
                                  // Clear interviewer_id when manually entering name
                                  updateParticipant(participant.id, 'interviewer_id', '');
                                }}
                                placeholder="Enter interviewer name manually"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              />
                              <div className="text-xs text-gray-500">
                                Or select from existing interviewers:
                              </div>
                              <select
                                value={participant.interviewer_id}
                                onChange={(e) => {
                                  const selectedInterviewer = interviewers.find(i => i.id == e.target.value);
                                  updateParticipant(participant.id, 'interviewer_id', e.target.value);
                                  if (selectedInterviewer) {
                                    updateParticipant(participant.id, 'interviewer_email', selectedInterviewer.email);
                                    // Clear manual name when selecting from dropdown
                                    updateParticipant(participant.id, 'interviewer_name', '');
                                  }
                                }}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              >
                                <option value="">Select interviewer</option>
                                {interviewers.map(interviewer => (
                                  <option key={interviewer.id} value={interviewer.id}>
                                    {interviewer.first_name} {interviewer.last_name} - {interviewer.role}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Email Address
                            </label>
                            <input
                              type="email"
                              value={participant.interviewer_email || ''}
                              onChange={(e) => updateParticipant(participant.id, 'interviewer_email', e.target.value)}
                              placeholder="interviewer@company.com"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              required
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                              Role
                            </label>
                            <select
                              value={participant.participant_type}
                              onChange={(e) => updateParticipant(participant.id, 'participant_type', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                              <option value="interviewer">Interviewer</option>
                              <option value="observer">Observer</option>
                              <option value="coordinator">Coordinator</option>
                            </select>
                          </div>

                          <div className="flex items-center">
                            <label className="flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={participant.is_primary || false}
                                onChange={(e) => updateParticipant(participant.id, 'is_primary', e.target.checked)}
                                className="mr-2 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                              />
                              <span className="text-sm text-gray-700">Set as Primary Interviewer</span>
                            </label>
                          </div>

                          {/* Premium Manager Feedback Selection */}
                          <div className="flex items-center bg-gradient-to-r from-purple-50 to-pink-50 p-3 rounded-lg border border-purple-200">
                            <div className="flex items-center">
                              <div className="relative">
                                <input
                                  type="checkbox"
                                  checked={participant.is_manager_feedback || false}
                                  onChange={(e) => updateParticipant(participant.id, 'is_manager_feedback', e.target.checked)}
                                  className="mr-2 h-4 w-4 text-purple-600 focus:ring-purple-500 border-purple-300 rounded"
                                />
                                {participant.is_manager_feedback && (
                                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                                    <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                    </svg>
                                  </div>
                                )}
                              </div>
                              <div className="flex items-center">
                                <span className="text-sm font-medium text-purple-800">Manager Feedback</span>
                                <div className="ml-2 flex items-center">
                                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 border border-purple-200">
                                    <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                                    </svg>
                                    Premium
                                  </span>
                                </div>
                              </div>
                            </div>
                            <div className="ml-3 text-xs text-purple-600">
                              {participant.is_manager_feedback ? (
                                <span className="flex items-center">
                                  <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                  </svg>
                                  Selected for feedback
                                </span>
                              ) : (
                                <span>Select to receive feedback form</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Additional Notes
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows="3"
                  placeholder="Any additional notes or instructions for the interview..."
                />
              </div>
            </div>
          </div>

          <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleUpdate}
              disabled={
                !formData.round_id ||
                !formData.scheduled_date ||
                !formData.scheduled_time ||
                loading
              }
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Updating...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Update Interview
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EditInterviewModal;