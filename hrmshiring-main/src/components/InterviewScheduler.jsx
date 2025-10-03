import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Users,
  Video,
  Phone,
  MapPin,
  Plus,
  Trash2,
  CheckCircle,
  AlertCircle,
  Info,
  User,
  Mail,
  Phone as PhoneIcon,
  MessageSquare
} from 'lucide-react';
import { API_CONFIG } from '../config/api';
import { formatDateForInput, formatDateForStorage, getMinDateForInput, formatDateTimeForDisplay } from '../utils/dateUtils';
import CustomDateInput from './CustomDateInput';

const InterviewScheduler = ({ ticketId, candidateId, candidateData, onInterviewScheduled, onOpenManagerFeedback }) => {
  console.log('InterviewScheduler: Component received props:', { ticketId, candidateId });
  console.log('InterviewScheduler: ticketId type:', typeof ticketId, 'value:', ticketId);
  console.log('InterviewScheduler: candidateId type:', typeof candidateId, 'value:', candidateId);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const [rounds, setRounds] = useState([]);
  const [interviewers, setInterviewers] = useState([]);
  const [candidate, setCandidate] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [scheduleData, setScheduleData] = useState({
    round_id: '',
    scheduled_date: '',
    scheduled_time: '',
    duration_minutes: 60,
    interview_type: 'video_call',
    meeting_link: '',
    location: '',
    notes: '',
    participants: []
  });
  


  const interviewTypes = [
    { value: 'video_call', label: 'Video Call', icon: Video },
    { value: 'phone_call', label: 'Phone Call', icon: Phone },
    { value: 'in_person', label: 'In Person', icon: MapPin },
    { value: 'online_test', label: 'Online Test', icon: CheckCircle }
  ];

  useEffect(() => {
    console.log('InterviewScheduler: useEffect triggered');
    console.log('InterviewScheduler: ticketId:', ticketId, 'type:', typeof ticketId);
    console.log('InterviewScheduler: candidateId:', candidateId, 'type:', typeof candidateId);
    console.log('InterviewScheduler: candidateId truthy check:', !!candidateId);
    console.log('InterviewScheduler: candidateId !== null:', candidateId !== null);
    console.log('InterviewScheduler: candidateId !== undefined:', candidateId !== undefined);
    console.log('InterviewScheduler: candidateData:', candidateData);
    
    if (ticketId) {
      console.log('InterviewScheduler: Fetching rounds and interviewers for ticketId:', ticketId);
      fetchRounds();
      fetchInterviewers();
    } else {
      console.log('InterviewScheduler: No ticketId provided');
    }
    
    if (candidateId && candidateId !== null && candidateId !== undefined) {
      console.log('InterviewScheduler: Fetching candidate with ID:', candidateId);
      fetchCandidate();
    } else {
      console.log('InterviewScheduler: No valid candidateId provided, cannot fetch candidate');
      console.log('InterviewScheduler: Setting error: No candidate ID provided');
      setError('No candidate ID provided');
    }
  }, [ticketId, candidateId, candidateData]);

  // Debug useEffect to monitor participants state changes
  useEffect(() => {
    console.log('Participants state changed:', scheduleData.participants);
    console.log('Participants length:', scheduleData.participants.length);
  }, [scheduleData.participants]);

  // Debug useEffect to monitor rounds state changes
  useEffect(() => {
    console.log('Rounds state changed:', rounds);
    console.log('Rounds length:', rounds.length);
  }, [rounds]);

  // Auto-generate meeting link when date and time are selected for video calls
  useEffect(() => {
    if (
      scheduleData.interview_type === 'video_call' &&
      scheduleData.scheduled_date &&
      scheduleData.scheduled_time &&
      !scheduleData.meeting_link
    ) {
      // Auto-generate meeting link after a short delay
      const timer = setTimeout(() => {
        generateMeetingLink();
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [scheduleData.scheduled_date, scheduleData.scheduled_time, scheduleData.interview_type]);



  const fetchRounds = async () => {
    try {
      console.log('Fetching rounds for ticketId:', ticketId);
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/rounds/${ticketId}`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      console.log('Rounds response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Rounds data:', data);
        const roundsData = data.data?.rounds || [];
        console.log('Setting rounds:', roundsData);
        console.log('Rounds count:', roundsData.length);
        setRounds(roundsData);
      } else {
        console.error('Error fetching rounds:', response.status, response.statusText);
        const errorText = await response.text();
        console.error('Error response:', errorText);
      }
    } catch (err) {
      console.error('Error fetching rounds:', err);
    }
  };

  const fetchInterviewers = async () => {
    try {
      console.log('Fetching interviewers...');
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/interviewers`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      console.log('Interviewers response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Interviewers data:', data);
        setInterviewers(data.data?.interviewers || []);
      } else {
        console.error('Error fetching interviewers:', response.status, response.statusText);
      }
    } catch (err) {
      console.error('Error fetching interviewers:', err);
    }
  };

  const fetchCandidate = async () => {
    try {
      // If we have candidate data passed as prop, use it directly
      if (candidateData && Object.keys(candidateData).length > 0) {
        console.log('Using provided candidate data:', candidateData);
        setCandidate(candidateData);
        setLoading(false);
        return;
      }

      const candidateIdInt = parseInt(candidateId, 10);
      console.log('Fetching candidate with ID:', candidateId, 'converted to:', candidateIdInt);
      console.log('Ticket ID:', ticketId);
      
      // Use the new dedicated candidate endpoint
      const apiUrl = `${API_CONFIG.BASE_URL}/api/interviews/candidate/${candidateIdInt}`;
      console.log('API URL:', apiUrl);
      setLoading(true);
      setError(null);
      
      const response = await fetch(apiUrl, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (response.ok) {
        const data = await response.json();
        console.log('Candidate data:', data);
        if (data.success && data.data?.candidate) {
          setCandidate(data.data.candidate);
          console.log('Candidate set successfully:', data.data.candidate);
        } else {
          console.error('Invalid response format:', data);
          setError('Invalid response format from server');
        }
      } else {
        const errorText = await response.text();
        console.error('Error fetching candidate:', response.status, response.statusText, errorText);
        
        // Check if it's a "Candidate not found" error and create demo candidate
        if (response.status === 404) {
          console.log('Creating demo candidate for testing...');
          const demoCandidate = {
            id: candidateIdInt,
            applicant_name: 'Demo Candidate',
            applicant_email: 'demo@example.com',
            applicant_phone: '+1-555-0123',
            job_title: 'Software Developer',
            interview_status: 'not_started',
            rounds_completed: 0,
            total_rounds: 3,
            final_decision: null,
            created_at: new Date().toISOString()
          };
          setCandidate(demoCandidate);
          console.log('Demo candidate set successfully:', demoCandidate);
        } else {
          setError(`Failed to load candidate information: ${response.status} ${response.statusText}`);
        }
      }
    } catch (err) {
      console.error('Error fetching candidate:', err);
      setError(`Error loading candidate information: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleInterview = async () => {
    try {
      setLoading(true);
      setError(null);

      // Map the candidate ID to the 1-based index expected by the API
      let mappedCandidateId = candidateId;
      
      // If candidateData is available, try to get the correct 1-based index
      if (candidateData && candidateData.applicant_email && candidateData.applicant_name) {
        try {
          // Fetch resumes to find the correct 1-based index
          const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${ticketId}/resumes`, {
            headers: {
              'X-API-Key': API_CONFIG.API_KEY,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            const resumes = data.data?.resumes || [];
            
            // Find the index of this candidate in the resumes
            const candidateIndex = resumes.findIndex(resume => 
              resume.applicant_email === candidateData.applicant_email && 
              resume.applicant_name === candidateData.applicant_name
            );
            
            if (candidateIndex !== -1) {
              // Convert 0-based index to 1-based index for the API
              mappedCandidateId = candidateIndex + 1;
              console.log('🔍 InterviewScheduler - Mapped candidate ID:', {
                original_candidate_id: candidateId,
                mapped_candidate_id: mappedCandidateId,
                candidate_name: candidateData.applicant_name,
                candidate_email: candidateData.applicant_email,
                total_resumes: resumes.length
              });
            } else {
              console.warn('⚠️ Could not find candidate in resumes, using original ID:', candidateId);
            }
          } else {
            console.warn('⚠️ Failed to fetch resumes, using original ID:', candidateId);
          }
        } catch (error) {
          console.warn('⚠️ Error fetching resumes, using original ID:', candidateId, error);
        }
      }

      // Debug: Log the date conversion
      const originalDate = scheduleData.scheduled_date;
      const convertedDate = formatDateForStorage(scheduleData.scheduled_date);
      console.log('Date conversion debug:', {
        original: originalDate,
        converted: convertedDate,
        type: typeof originalDate
      });

      const requestData = {
        ticket_id: ticketId,
        candidate_id: mappedCandidateId,
        round_id: scheduleData.round_id,
        scheduled_date: convertedDate,
        scheduled_time: scheduleData.scheduled_time,
        duration_minutes: scheduleData.duration_minutes,
        interview_type: scheduleData.interview_type,
        meeting_link: scheduleData.meeting_link,
        location: scheduleData.location,
        notes: scheduleData.notes,
        participants: scheduleData.participants,
        created_by: 'hr_user' // This should come from auth context
      };

      console.log('Scheduling interview with data:', requestData);

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/schedule`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      console.log('Schedule interview response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Schedule interview response data:', data);
        setShowForm(false);
        setScheduleData({
          round_id: '',
          scheduled_date: '',
          scheduled_time: '',
          duration_minutes: 60,
          interview_type: 'video_call',
          meeting_link: '',
          location: '',
          notes: '',
          participants: []
        });
        if (onInterviewScheduled) {
          onInterviewScheduled(data.data?.interview_id);
        }
        
        // Show success message with option to open manager feedback
        setSuccessMessage('✅ Interview scheduled successfully! Managers will receive email notifications with feedback links.');
      } else {
        const errorData = await response.json();
        console.error('Schedule interview error:', errorData);
        setError(errorData.error || 'Failed to schedule interview');
      }
    } catch (err) {
      console.error('Schedule interview exception:', err);
      setError('Error scheduling interview');
    } finally {
      setLoading(false);
    }
  };

       // Simplified add participant function
  const addParticipant = () => {
    const newParticipant = {
      id: Date.now(), // Add unique ID for React key
      interviewer_id: '',
      interviewer_name: '', // Add field for manual name entry
      interviewer_email: '',
      participant_type: 'interviewer',
      is_primary: scheduleData.participants.length === 0, // First participant is primary
      is_manager_feedback: false // Premium feature: manager feedback selection
    };
    
    setScheduleData(prev => ({
      ...prev,
      participants: [...prev.participants, newParticipant]
    }));
  };

  // Simplified remove participant function
  const removeParticipant = (participantId) => {
    setScheduleData(prev => ({
      ...prev,
      participants: prev.participants.filter(p => p.id !== participantId)
    }));
  };

  // Simplified update participant function
  const updateParticipant = (participantId, field, value) => {
    setScheduleData(prev => {
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

  const getRoundInterviewers = (roundId) => {
    // This would typically fetch from the round_interviewers table
    // For now, return all interviewers
    return interviewers;
  };

  const createDefaultRounds = async () => {
    try {
      console.log('Creating default rounds for ticketId:', ticketId);
      setLoading(true);
      setError(null);

      // Use the backend endpoint that creates the proper 3-round system
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/rounds/${ticketId}/setup-default`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.success) {
        setSuccessMessage('✅ Default 3-round interview process created successfully!');
        setTimeout(() => setSuccessMessage(null), 3000);
        
        // Refresh the rounds list
        await fetchRounds();
      } else {
        if (data.error && data.error.includes('already exist')) {
          setError('Interview rounds already exist for this job. You can use the existing rounds for scheduling interviews.');
        } else {
          setError(data.error || 'Failed to create default rounds');
        }
      }
    } catch (err) {
      console.error('Error creating default rounds:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateMeetingLink = async () => {
    try {
      if (!scheduleData.scheduled_date || !scheduleData.scheduled_time) {
        setError('Please select date and time first');
        return;
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/generate-meet-link`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          scheduled_date: scheduleData.scheduled_date,
          scheduled_time: scheduleData.scheduled_time,
          duration_minutes: scheduleData.duration_minutes,
          interview_title: `Interview with ${candidate.applicant_name}`
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setScheduleData(prev => ({
            ...prev,
            meeting_link: data.data.meeting_link
          }));
          setSuccessMessage('Google Meet link generated successfully!');
          setTimeout(() => setSuccessMessage(null), 3000);
        } else {
          setError(data.error || 'Failed to generate meeting link');
        }
      } else {
        setError('Failed to generate meeting link');
      }
    } catch (err) {
      console.error('Error generating meeting link:', err);
      setError('Error generating meeting link');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading candidate...</span>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Candidate Not Found</h3>
          <p className="text-gray-600">Unable to load candidate information.</p>
          {error && <p className="text-red-600 mt-2">{error}</p>}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Debug Information:</p>
            <p className="text-xs text-gray-500">Candidate ID: {candidateId}</p>
            <p className="text-xs text-gray-500">Ticket ID: {ticketId}</p>
            <p className="text-xs text-gray-500">Error: {error}</p>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Demo Mode Indicator - Only show if using demo data and no real candidate data provided */}
      {candidate.applicant_name === 'Demo Candidate' && !candidateData && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex items-center">
            <Info className="w-5 h-5 text-blue-500 mr-2" />
            <div>
              <p className="text-blue-800 font-medium text-sm">Demo Mode Active</p>
              <p className="text-blue-600 text-xs">This is sample data for demonstration. Create a real candidate to see actual data.</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Schedule Interview</h3>
          <p className="text-sm text-gray-600">
            Schedule interview for {candidate.applicant_name}
          </p>
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            <Calendar className="w-4 h-4 mr-2" />
            Schedule Interview
          </button>
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

       {successMessage && (
         <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
           <div className="flex items-center">
             <CheckCircle className="w-5 h-5 text-green-400 mr-2" />
             <span className="text-green-800">{successMessage}</span>
           </div>
         </div>
       )}

             {/* Candidate Info */}
       <div className="mb-6 p-4 bg-gray-50 rounded-md">
         <div className="flex items-center space-x-4">
           <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
             <User className="w-6 h-6 text-indigo-600" />
           </div>
           <div>
             <h4 className="font-medium text-gray-900">{candidate.applicant_name}</h4>
             <div className="flex items-center space-x-4 text-sm text-gray-600">
               <span className="flex items-center">
                 <Mail className="w-4 h-4 mr-1" />
                 {candidate.applicant_email}
               </span>
               {candidate.applicant_phone && (
                 <span className="flex items-center">
                   <PhoneIcon className="w-4 h-4 mr-1" />
                   {candidate.applicant_phone}
                 </span>
               )}
             </div>
           </div>
         </div>
       </div>


      {/* Debug Info - Rounds */}
      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
         <h5 className="font-medium text-yellow-800 mb-2">Debug: Available Rounds</h5>
         <div className="text-sm text-yellow-700">
           <p><strong>Ticket ID:</strong> {ticketId}</p>
           <p><strong>Rounds Count:</strong> {rounds.length}</p>
           {rounds.length > 0 ? (
             <div className="mt-2">
               <p><strong>Available Rounds:</strong></p>
               <ul className="list-disc list-inside ml-2">
                 {rounds.map(round => (
                   <li key={round.id}>
                     {round.round_name} (ID: {round.id})
                   </li>
                 ))}
               </ul>
             </div>
           ) : (
             <div className="mt-2">
               <p className="text-red-600 mb-2">No rounds found for this ticket!</p>
               <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-md">
                 <p className="text-blue-800 font-medium mb-2">🎯 Default 3-Round Interview Process:</p>
                 <ol className="list-decimal list-inside ml-2 text-blue-700">
                   <li><strong>HR Round</strong> - 45 min - Initial screening & cultural fit</li>
                   <li><strong>Technical Round</strong> - 90 min - Skills assessment & problem-solving</li>
                   <li><strong>HR Final Round</strong> - 60 min - Final discussion & offer negotiation</li>
                 </ol>
               </div>
               <button
                 onClick={createDefaultRounds}
                 disabled={loading}
                 className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
               >
                 {loading ? (
                   <>
                     <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                     <span>Creating Rounds...</span>
                   </>
                 ) : (
                   <>
                     <span>🚀</span>
                     <span>Create Default 3 Rounds</span>
                   </>
                 )}
               </button>
             </div>
           )}
         </div>
       </div>

      {showForm ? (
        <div className="space-y-6">
          {/* Interview Details Form */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interview Round *
              </label>
              <select
                value={scheduleData.round_id}
                onChange={(e) => setScheduleData({ ...scheduleData, round_id: e.target.value })}
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
                Interview Type
              </label>
              <select
                value={scheduleData.interview_type}
                onChange={(e) => setScheduleData({ ...scheduleData, interview_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {interviewTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date *
              </label>
              <CustomDateInput
                value={scheduleData.scheduled_date}
                onChange={(value) => setScheduleData({ ...scheduleData, scheduled_date: value })}
                placeholder="dd/mm/yyyy"
                required={true}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time *
              </label>
              <input
                type="time"
                value={scheduleData.scheduled_time}
                onChange={(e) => setScheduleData({ ...scheduleData, scheduled_time: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (minutes)
              </label>
              <input
                type="number"
                value={scheduleData.duration_minutes}
                onChange={(e) => setScheduleData({ ...scheduleData, duration_minutes: parseInt(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                min="15"
                max="480"
              />
            </div>

            {scheduleData.interview_type === 'video_call' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Meeting Link
                </label>
                <div className="flex space-x-2">
                  <input
                    type="url"
                    value={scheduleData.meeting_link}
                    onChange={(e) => setScheduleData({ ...scheduleData, meeting_link: e.target.value })}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="https://meet.google.com/..."
                  />
                  <button
                    type="button"
                    onClick={generateMeetingLink}
                    disabled={!scheduleData.scheduled_date || !scheduleData.scheduled_time}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Generate Google Meet Link"
                  >
                    <Video className="w-4 h-4" />
                  </button>
                </div>
                {scheduleData.meeting_link && (
                  <p className="text-xs text-green-600 mt-1">
                    ✓ Meeting link generated for {scheduleData.scheduled_date} at {scheduleData.scheduled_time}
                  </p>
                )}
              </div>
            )}

            {scheduleData.interview_type === 'in_person' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  value={scheduleData.location}
                  onChange={(e) => setScheduleData({ ...scheduleData, location: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  placeholder="Office address or room number"
                />
              </div>
            )}
          </div>

                    {/* FIXED Participants Section */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="font-medium text-gray-900">
                  Interview Participants
                  {scheduleData.participants.length > 0 && (
                    <span className="ml-2 text-sm text-gray-500">
                      ({scheduleData.participants.length} added)
                    </span>
                  )}
                </h4>
                <p className="text-sm text-gray-500 mt-1">
                  Add interviewers who will conduct the interview
                </p>
              </div>
              <button
                type="button"
                onClick={addParticipant}
                disabled={scheduleData.participants.length >= 5}
                className="flex items-center px-3 py-1.5 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Participant
              </button>
            </div>

            {scheduleData.participants.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">No participants added yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Click "Add Participant" to add interviewers
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {scheduleData.participants.map((participant, index) => (
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
                      {/* Interviewer Selection - Now allows manual entry */}
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

                      {/* Email Input */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Email Address *
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

                      {/* Role Selection */}
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

                      {/* Primary Checkbox */}
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

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Notes
            </label>
            <textarea
              value={scheduleData.notes}
              onChange={(e) => setScheduleData({ ...scheduleData, notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows="3"
              placeholder="Any additional notes or instructions for the interview..."
            />
          </div>

          {/* Form Status Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
            <h4 className="font-medium text-blue-900 mb-2">Form Status</h4>
            <div className="space-y-1 text-sm text-blue-800">
              <div className="flex items-center">
                {scheduleData.round_id ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-500 mr-2" />
                )}
                Interview Round: {scheduleData.round_id ? 'Selected' : 'Required'}
              </div>
              <div className="flex items-center">
                {scheduleData.scheduled_date ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-500 mr-2" />
                )}
                Date: {scheduleData.scheduled_date || 'Required'}
              </div>
              <div className="flex items-center">
                {scheduleData.scheduled_time ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-500 mr-2" />
                )}
                Time: {scheduleData.scheduled_time || 'Required'}
              </div>
              <div className="flex items-center">
                {scheduleData.participants.length > 0 ? (
                  <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                ) : (
                  <AlertCircle className="w-4 h-4 text-red-500 mr-2" />
                )}
                                 Participants: {scheduleData.participants.length} added
                 {scheduleData.participants.some(p => !p.interviewer_email || !p.interviewer_email.trim()) && (
                   <span className="text-red-600 ml-2">(Email addresses required)</span>
                 )}
              </div>
            </div>
            
            {/* Manager Feedback Test Button */}
            {onOpenManagerFeedback && (
              <div className="mt-4 pt-3 border-t border-blue-200">
                <button
                  onClick={() => onOpenManagerFeedback({
                    interviewId: 'test-interview-123',
                    candidateId: candidateId,
                    candidateName: candidate?.applicant_name || 'Test Candidate',
                    candidateEmail: candidate?.applicant_email || 'test@example.com',
                    jobTitle: 'Test Position',
                    roundName: 'Test Round'
                  })}
                  className="px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors flex items-center"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Test Manager Feedback Form
                </button>
                <p className="text-xs text-blue-600 mt-1">Click to test the premium manager feedback system</p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setShowForm(false);
                setScheduleData({
                  round_id: '',
                  scheduled_date: '',
                  scheduled_time: '',
                  duration_minutes: 60,
                  interview_type: 'video_call',
                  meeting_link: '',
                  location: '',
                  notes: '',
                  participants: []
                });
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
                         <button
               onClick={handleScheduleInterview}
               disabled={
                 !scheduleData.round_id ||
                 !scheduleData.scheduled_date ||
                 !scheduleData.scheduled_time ||
                 scheduleData.participants.length === 0 ||
                 loading ||
                 scheduleData.participants.some(p => !p.interviewer_email || !p.interviewer_email.trim())
               }
               className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
             >
              {loading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Scheduling...
                </div>
              ) : (
                'Schedule Interview'
              )}
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No interview scheduled yet.</p>
          <p className="text-sm text-gray-500 mt-1">Click "Schedule Interview" to get started.</p>
        </div>
      )}
    </div>
  );
};

export default InterviewScheduler;
