import React, { useState, useEffect } from 'react';
import {
  Users,
  Filter,
  Search,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  Calendar,
  TrendingUp,
  TrendingDown,
  Eye,
  Star,
  Award,
  Target,
  BarChart3,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  User,
  Mail,
  Phone,
  MapPin,
  Briefcase,
  ThumbsUp,
  Minus,
  Play,
  Pause,
  Download,
  Trash2,
  MessageSquare,
  Loader,
  FileText,
  X
} from 'lucide-react';
import { API_CONFIG } from '../config/api';
import InterviewScheduler from './InterviewScheduler';
import CandidateInterviewStatus from './CandidateInterviewStatus';

const RoundBasedCandidateFilter = ({ ticketId, onCandidateSelect, onOpenManagerFeedback, jobApplications }) => {
  const [candidates, setCandidates] = useState([]);
  const [overallStats, setOverallStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRound, setSelectedRound] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedJob, setSelectedJob] = useState('all');
  const [expandedCandidates, setExpandedCandidates] = useState(new Set());
  const [refreshing, setRefreshing] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [viewStatusLoading, setViewStatusLoading] = useState({});
  const [currentResume, setCurrentResume] = useState(null);
  const [showResumePreview, setShowResumePreview] = useState(false);
  const [showCandidateStatus, setShowCandidateStatus] = useState(false);
  const [showInterviewScheduler, setShowInterviewScheduler] = useState(false);
  const [selectedCandidateForInterview, setSelectedCandidateForInterview] = useState(null);
  const [selectedJobForInterviews, setSelectedJobForInterviews] = useState(null);

  const roundOptions = [
    { value: 'all', label: 'All Rounds' },
    { value: '1', label: 'Round 1' },
    { value: '2', label: 'Round 2' },
    { value: '3', label: 'Round 3' }
  ];

  const statusOptions = [
    { value: 'all', label: 'All Status' },
    { value: 'passed', label: 'Passed' },
    { value: 'failed', label: 'Failed' },
    { value: 'pending', label: 'Pending' }
  ];

  // Create job options from available candidates
  const jobOptions = React.useMemo(() => {
    const uniqueJobs = [...new Set(candidates.map(candidate => candidate.job_title).filter(Boolean))];
    return [
      { value: 'all', label: 'All Jobs' },
      ...uniqueJobs.map(job => ({ value: job, label: job }))
    ];
  }, [candidates]);

  useEffect(() => {
    fetchCandidates();
  }, [ticketId, selectedRound, selectedStatus, selectedJob]);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      
      console.log('🔍 fetchCandidates called with ticketId:', ticketId);
      
      if (ticketId) {
        // Use the EXACT same approach as CareerPortal
        const response = await fetch(`http://localhost:5000/api/tickets/${ticketId}/resumes`, {
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('🔍 Fetched candidates data from /api/tickets/resumes (CareerPortal approach):', data);
          
          // Use the EXACT same data structure as CareerPortal - no transformation needed!
          const resumes = data.data?.resumes || [];
          console.log('🔍 Raw resumes from API (CareerPortal format):', resumes);
          console.log('🔍 First resume structure:', resumes[0]);
          
          // Store the raw resume data directly (same as CareerPortal)
          setCandidates(resumes);
        } else {
          throw new Error('Failed to fetch candidates');
        }
      } else {
        // For null ticketId, use the filter-by-round endpoint to get all candidates
        const params = new URLSearchParams({
          round: selectedRound,
          status: selectedStatus
        });

        const response = await fetch(`http://localhost:5000/api/candidates/filter-by-round?${params}`, {
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const data = await response.json();
          console.log('🔍 Fetched candidates data from /api/candidates/filter-by-round:', data);
          
          // For the filter-by-round endpoint, we need to convert database IDs to frontend indices
          // because the backend status update API expects frontend indices for this endpoint
          const rawCandidates = data.data?.candidates || [];
          const candidates = rawCandidates.map((candidate, index) => ({
            ...candidate,
            // Use frontend index + 1 as candidate_id for backend OFFSET compatibility
            candidate_id: index + 1,
            id: index + 1,
            // Keep the original database ID for reference
            original_database_id: candidate.candidate_id
          }));
          
          console.log('🔍 Transformed candidates data (filter-by-round format):', candidates);
          setCandidates(candidates);
        } else {
          throw new Error('Failed to fetch candidates');
        }
      }
    } catch (err) {
      console.error('❌ Error in fetchCandidates:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchCandidates();
    setRefreshing(false);
  };

  const toggleCandidateExpansion = (candidateId) => {
    const newExpanded = new Set(expandedCandidates);
    if (newExpanded.has(candidateId)) {
      newExpanded.delete(candidateId);
    } else {
      newExpanded.add(candidateId);
    }
    setExpandedCandidates(newExpanded);
  };

  // Action button functions
  const previewResume = async (candidateTicketId, filename, applicant) => {
    console.log('🔍 Preview Resume called with:', { candidateTicketId, filename, applicant });
    
    if (!filename) {
      console.error('❌ No filename provided for preview');
      alert('No resume file found for this candidate. Please check if the resume was uploaded properly.');
      return;
    }
    
    if (!candidateTicketId) {
      console.error('❌ No ticket ID provided for preview');
      alert('No ticket ID found for this candidate. Please check the candidate data.');
      return;
    }
    
    setResumeLoading(true);
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${candidateTicketId}/resumes/${filename}`, {
        method: 'GET',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Resume fetch response:', response.status, response.statusText);

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setCurrentResume({
          url,
          filename,
          applicant,
          type: response.headers.get('content-type')
        });
        setShowResumePreview(true);
        console.log('✅ Resume preview opened successfully');
      } else {
        throw new Error(`Failed to load resume: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Error previewing resume:', error);
      alert(`Failed to preview resume: ${error.message}. Please check if the file exists.`);
    } finally {
      setResumeLoading(false);
    }
  };

  const downloadResume = async (candidateTicketId, filename) => {
    console.log('🔍 Download Resume called with:', { candidateTicketId, filename });
    
    if (!filename) {
      console.error('❌ No filename provided for download');
      alert('No resume file found for this candidate. Please check if the resume was uploaded properly.');
      return;
    }
    
    if (!candidateTicketId) {
      console.error('❌ No ticket ID provided for download');
      alert('No ticket ID found for this candidate. Please check the candidate data.');
      return;
    }
    
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${candidateTicketId}/resumes/${filename}`, {
        method: 'GET',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Download response:', response.status, response.statusText);

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log('✅ Resume downloaded successfully');
      } else {
        throw new Error(`Failed to download resume: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      console.error('❌ Error downloading resume:', error);
      alert(`Failed to download resume: ${error.message}. Please check if the file exists.`);
    }
  };

  const deleteCandidate = async (candidateTicketId, candidate) => {
    try {
      console.log('🚀 DELETE CANDIDATE CALLED');
      console.log('🔍 Candidate to delete:', candidate);
      console.log('🔍 Ticket ID:', candidateTicketId);
      
      if (!window.confirm(`Are you sure you want to delete ${candidate.applicant_name}? This action cannot be undone.`)) {
        return;
      }

      if (!candidateTicketId) {
        console.error('❌ No ticket ID provided for delete');
        alert('No ticket ID found for this candidate. Please check the candidate data.');
        return;
      }

      // Use the same delete endpoint as CareerPortal for consistency
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/candidates/delete`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_id: candidate.candidate_id || candidate.id || 0,
          ticket_id: candidateTicketId,
          candidate_email: candidate.applicant_email,
          candidate_name: candidate.applicant_name
        })
      });

      console.log('🌐 API Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ API Error:', errorData);
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ API Response:', result);
      
      if (result.success) {
        // Show success message from the delete endpoint
        const message = result.message || `${candidate.applicant_name} deleted successfully`;
        console.log('✅ Success message:', message);
        alert(`✅ ${message}`);
        
        // Refresh the candidates list
        console.log('🔄 Refreshing candidates list...');
        await fetchCandidates();
        
        console.log('✅ DELETION COMPLETED SUCCESSFULLY');
      } else {
        throw new Error(result.error || 'Unknown error occurred');
      }
      
    } catch (error) {
      console.error('❌ Error in deleteCandidate:', error);
      alert(`Failed to delete candidate: ${error.message}`);
    }
  };

  const handleScheduleInterview = async (candidate) => {
    try {
      // We need to map the database candidate_id to the 1-based index expected by the interview scheduling API
      // The backend expects candidate_id to be a 1-based index (1, 2, 3, etc.) that corresponds to the position in metadata.json
      
      // First, let's get the resumes to find the correct 1-based index
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${candidate.ticket_id}/resumes`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const resumes = data.data?.resumes || [];
        
        // Find the index of this candidate in the metadata
        const candidateIndex = resumes.findIndex(resume => 
          resume.applicant_email === candidate.applicant_email && 
          resume.applicant_name === candidate.applicant_name
        );
        
        if (candidateIndex !== -1) {
          // Convert 0-based index to 1-based index for the API
          const frontendCandidateId = candidateIndex + 1;
          
          // Transform candidate data to match the expected format for InterviewScheduler
          const transformedCandidate = {
            id: frontendCandidateId, // Use 1-based index as expected by the API
            candidate_id: frontendCandidateId, // Also include this for the API call
            applicant_name: candidate.applicant_name,
            applicant_email: candidate.applicant_email,
            ticket_id: candidate.ticket_id,
            job_title: candidate.job_title,
            filename: candidate.filename,
            // Include all other candidate properties for compatibility
            ...candidate
          };
          
          console.log('🔍 Schedule Interview - Mapped candidate:', {
            original_candidate_id: candidate.candidate_id,
            frontend_candidate_id: frontendCandidateId,
            candidate_name: candidate.applicant_name,
            candidate_email: candidate.applicant_email,
            ticket_id: candidate.ticket_id
          });
          
          setSelectedCandidateForInterview(transformedCandidate);
          setSelectedJobForInterviews({ 
            ticket_id: candidate.ticket_id,
            job_title: candidate.job_title 
          });
          setShowInterviewScheduler(true);
        } else {
          console.error('❌ Could not find candidate in resumes:', candidate);
          alert('Could not find candidate in job resumes. Please try refreshing the page.');
        }
      } else {
        console.error('❌ Failed to fetch resumes for ticket:', candidate.ticket_id);
        alert('Failed to load job resumes. Please try again.');
      }
    } catch (error) {
      console.error('❌ Error in handleScheduleInterview:', error);
      alert('Error preparing interview scheduling. Please try again.');
    }
  };

  const handleViewStatus = async (candidate) => {
    const candidateKey = `${candidate.applicant_name}-${candidate.applicant_email}`;
    setViewStatusLoading(prev => ({ ...prev, [candidateKey]: true }));
    
    try {
      console.log('🔍 View Status - Full candidate data:', candidate);
      console.log('🔍 View Status - Candidate ID:', candidate.candidate_id);
      console.log('🔍 View Status - ID:', candidate.id);
      console.log('🔍 View Status - Raw candidate data (CareerPortal format):', candidate);
      console.log('🔍 View Status - Ticket ID:', candidate.ticket_id);
      console.log('🔍 View Status - Applicant Name:', candidate.applicant_name);
      console.log('🔍 View Status - Applicant Email:', candidate.applicant_email);
      console.log('🔍 View Status - Job Title:', candidate.job_title);
      console.log('🔍 View Status - Overall Status:', candidate.overall_status);
      console.log('🔍 View Status - Rounds Completed:', candidate.rounds_completed);
      console.log('🔍 View Status - Total Rounds:', candidate.total_rounds);
      
      // Use the SAME approach as CareerPortal - get the raw resume data with ID from jobApplications for proper ID mapping
      let candidateToUse = candidate;
      
      if (jobApplications && candidate.ticket_id) {
        console.log('🔍 Looking for matching application in jobApplications for ticket:', candidate.ticket_id);
        const rawApplications = jobApplications[candidate.ticket_id] || [];
        console.log('🔍 Raw applications for ticket:', rawApplications.length);
        
        // Find matching application by name and email
        const matchingApplication = rawApplications.find(app => 
          app.applicant_name === candidate.applicant_name && 
          app.applicant_email === candidate.applicant_email
        );
        
        if (matchingApplication) {
          console.log('✅ Found matching application in jobApplications:', matchingApplication);
          candidateToUse = matchingApplication;
        } else {
          console.log('⚠️ No matching application found in jobApplications, using original candidate data');
        }
      } else {
        console.log('⚠️ No jobApplications data available, using original candidate data');
      }
      
      // Check if candidate has a valid ID
      if (!candidateToUse.id) {
        console.error('❌ Candidate does not have a valid ID:', candidateToUse);
        alert('Error: Candidate data is missing required ID. Please try again.');
        setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
        return;
      }
      
      // Use original_database_id if available, otherwise use the frontend ID
      const candidateIdToUse = candidateToUse.original_database_id || candidateToUse.id;
      
      console.log('🔍 Final candidate data being passed to modal:', candidateToUse);
      console.log('🔍 Frontend Candidate ID:', candidateToUse.id);
      console.log('🔍 Database Candidate ID:', candidateToUse.original_database_id);
      console.log('🔍 Candidate ID being sent to backend:', candidateIdToUse);
      console.log('🔍 Ticket ID being sent to backend:', candidate.ticket_id);
      
      // Update the candidate data with the correct ID for the modal
      const candidateWithCorrectId = {
        ...candidateToUse,
        id: candidateIdToUse
      };
      
      setSelectedCandidateForInterview(candidateWithCorrectId);
      setSelectedJobForInterviews({ 
        ticket_id: candidate.ticket_id,
        job_title: candidate.job_title 
      });
      setShowCandidateStatus(true);
    } catch (error) {
      console.error('Error opening candidate status:', error);
      alert('Error loading candidate status. Please try again.');
    } finally {
      setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
    }
  };


  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
      case 'hire':
      case 'strong_hire':
      case 'selected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
      case 'reject':
      case 'strong_reject':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
      case 'in_progress':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'scheduled':
        return <Calendar className="w-4 h-4 text-blue-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed':
      case 'hire':
      case 'strong_hire':
      case 'selected':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
      case 'reject':
      case 'strong_reject':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'pending':
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'scheduled':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'hire':
      case 'strong_hire':
      case 'selected':
        return <ThumbsUp className="w-4 h-4 text-green-500" />;
      case 'reject':
      case 'strong_reject':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'maybe':
      case 'on_hold':
        return <Minus className="w-4 h-4 text-yellow-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-400" />;
    }
  };

  const filteredCandidates = candidates.filter(candidate => {
    // Search term filter
    const matchesSearch = candidate.applicant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         candidate.applicant_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         candidate.job_title.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Job filter
    const matchesJob = selectedJob === 'all' || candidate.job_title === selectedJob;
    
    return matchesSearch && matchesJob;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading candidates...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Round-Based Candidate Filter</h2>
          <p className="text-gray-600">Filter candidates by interview rounds and status</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <div className="flex items-center mb-4">
          <Filter className="w-5 h-5 text-indigo-600 mr-2" />
          <h3 className="text-lg font-semibold text-gray-900">Filters & Search</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Candidates
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name, email, or job..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 shadow-sm"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Round
            </label>
            <select
              value={selectedRound}
              onChange={(e) => setSelectedRound(e.target.value)}
              className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 shadow-sm"
            >
              {roundOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 shadow-sm"
            >
              {statusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Job
            </label>
            <select
              value={selectedJob}
              onChange={(e) => setSelectedJob(e.target.value)}
              className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 shadow-sm"
            >
              {jobOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

        </div>
      </div>



      {/* Overall Statistics */}
      {overallStats && Object.keys(overallStats).length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
            <Target className="w-5 h-5 mr-2 text-green-600" />
            Overall Statistics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center p-4 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg border border-indigo-200">
              <div className="text-3xl font-bold text-indigo-600 mb-1">{overallStats.total_candidates || 0}</div>
              <div className="text-sm font-medium text-indigo-700">Total Candidates</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200">
              <div className="text-3xl font-bold text-green-600 mb-1">{overallStats.hired || 0}</div>
              <div className="text-sm font-medium text-green-700">Hired</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-red-50 to-red-100 rounded-lg border border-red-200">
              <div className="text-3xl font-bold text-red-600 mb-1">{overallStats.rejected || 0}</div>
              <div className="text-sm font-medium text-red-700">Rejected</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg border border-yellow-200">
              <div className="text-3xl font-bold text-yellow-600 mb-1">{overallStats.in_progress || 0}</div>
              <div className="text-sm font-medium text-yellow-700">In Progress</div>
            </div>
            <div className="text-center p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200">
              <div className="text-3xl font-bold text-gray-600 mb-1">{overallStats.not_started || 0}</div>
              <div className="text-sm font-medium text-gray-700">Not Started</div>
            </div>
          </div>
        </div>
      )}

      {/* Candidates List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
          <h3 className="text-xl font-semibold text-gray-900 flex items-center">
            <Users className="w-6 h-6 mr-3 text-indigo-600" />
            Candidates ({filteredCandidates.length})
          </h3>
          <p className="text-sm text-gray-600 mt-1">Manage and track candidate progress through interview rounds</p>
        </div>

        {error && (
          <div className="p-6">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          </div>
        )}

        {filteredCandidates.length === 0 ? (
          <div className="p-6 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-600 mb-2">No candidates found</h4>
            <p className="text-gray-500">
              {searchTerm ? 'Try adjusting your search terms' : 'No candidates match the current filters'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredCandidates.map((candidate) => (
              <div key={candidate.candidate_id} className="p-6 hover:bg-gray-50 transition-colors duration-200">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  {/* Candidate Info Section */}
                  <div className="flex items-center space-x-4 flex-1">
                    <div className="w-14 h-14 bg-gradient-to-br from-indigo-100 to-indigo-200 rounded-full flex items-center justify-center shadow-sm">
                      <User className="w-7 h-7 text-indigo-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-lg font-semibold text-gray-900 truncate">{candidate.applicant_name}</h4>
                      <p className="text-gray-600 truncate">{candidate.applicant_email}</p>
                      <p className="text-sm text-gray-500 truncate">{candidate.job_title}</p>
                    </div>
                  </div>
                  
                  {/* Status and Progress Section */}
                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                    <div className="text-center sm:text-right">
                      <div className={`inline-flex items-center px-3 py-1.5 rounded-full border text-sm font-medium shadow-sm ${getStatusColor(candidate.overall_status)}`}>
                        {getStatusIcon(candidate.overall_status)}
                        <span className="ml-1">{candidate.overall_status?.replace('_', ' ').toUpperCase() || 'NOT STARTED'}</span>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {(() => {
                          // Calculate correct round counts from the rounds data
                          const totalRounds = candidate.rounds?.length || candidate.total_rounds || 0;
                          const completedRounds = candidate.rounds?.filter(round => 
                            round.round_decision || round.overall_rating || round.status === 'completed'
                          ).length || candidate.rounds_completed || 0;
                          return `${completedRounds}/${totalRounds} rounds completed`;
                        })()}
                      </div>
                    </div>
                    
                    {/* Action Buttons Section */}
                    <div className="flex flex-col gap-3">
                      {/* Primary Action Buttons */}
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => previewResume(candidate.ticket_id, candidate.filename, candidate)}
                          disabled={resumeLoading}
                          className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-all duration-200 text-sm shadow-sm hover:shadow-md"
                        >
                          {resumeLoading ? (
                            <Loader className="w-4 h-4 animate-spin" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                          <span>Preview</span>
                        </button>
                        
                        <button
                          onClick={() => downloadResume(candidate.ticket_id, candidate.filename)}
                          className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-all duration-200 text-sm shadow-sm hover:shadow-md"
                        >
                          <Download className="w-4 h-4" />
                          <span>Download</span>
                        </button>
                        
                        <button
                          onClick={() => handleScheduleInterview(candidate)}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-all duration-200 text-sm shadow-sm hover:shadow-md"
                        >
                          <Calendar className="w-4 h-4" />
                          <span>Schedule</span>
                        </button>
                        
                        <button
                          onClick={() => handleViewStatus(candidate)}
                          disabled={viewStatusLoading[`${candidate.applicant_name}-${candidate.applicant_email}`]}
                          className={`px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-all duration-200 text-sm shadow-sm hover:shadow-md ${
                            viewStatusLoading[`${candidate.applicant_name}-${candidate.applicant_email}`]
                              ? 'bg-indigo-400 cursor-not-allowed' 
                              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                          }`}
                        >
                          {viewStatusLoading[`${candidate.applicant_name}-${candidate.applicant_email}`] ? (
                            <>
                              <Loader className="w-4 h-4 animate-spin" />
                              <span>Loading...</span>
                            </>
                          ) : (
                            <>
                              <MessageSquare className="w-4 h-4" />
                              <span>Status</span>
                            </>
                          )}
                        </button>
                        
                        <button
                          onClick={() => deleteCandidate(candidate.ticket_id, candidate)}
                          className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-all duration-200 text-sm shadow-sm hover:shadow-md"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Delete</span>
                        </button>
                      </div>
                      
                      {/* Toggle Details Button */}
                      <button
                        onClick={() => toggleCandidateExpansion(candidate.candidate_id)}
                        className="flex items-center justify-center px-3 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg border border-indigo-200 transition-all duration-200 text-sm font-medium"
                      >
                        {expandedCandidates.has(candidate.candidate_id) ? (
                          <>
                            <ChevronUp className="w-4 h-4 mr-1" />
                            Hide Details
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4 mr-1" />
                            Show Details
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedCandidates.has(candidate.candidate_id) && (
                  <div className="mt-6 p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl border border-gray-200">
                    {/* Round Progress */}
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-4 flex items-center">
                        <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" />
                        Round Progress
                      </h5>
                      <div className="grid gap-4">
                        {candidate.rounds.map((round, index) => (
                          <div key={round.round_id} className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200">
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                              <div className="flex items-center space-x-4">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold shadow-sm ${
                                round.round_decision ? 
                                    (round.round_decision === 'hire' || round.round_decision === 'strong_hire' ? 
                                      'bg-gradient-to-br from-green-100 to-green-200 text-green-700 border-2 border-green-300' : 
                                      'bg-gradient-to-br from-red-100 to-red-200 text-red-700 border-2 border-red-300') :
                                    'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-600 border-2 border-gray-300'
                              }`}>
                                {round.round_order}
                              </div>
                                <div className="flex-1 min-w-0">
                                  <h6 className="font-semibold text-gray-900 text-lg">{round.round_name}</h6>
                                  <p className="text-sm text-gray-600 mt-1">{round.round_description}</p>
                                  <div className="flex items-center gap-4 mt-2">
                                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
                                      <Briefcase className="w-3 h-3 mr-1" />
                                      {round.interview_type}
                                    </span>
                                    <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
                                      <Clock className="w-3 h-3 mr-1" />
                                      {round.duration_minutes} min
                                    </span>
                                  </div>
                              </div>
                            </div>
                            
                              <div className="flex flex-col sm:items-end gap-2">
                              {round.round_decision ? (
                                  <div className={`flex items-center px-3 py-2 rounded-full text-sm font-medium shadow-sm ${getStatusColor(round.round_decision)}`}>
                                  {getDecisionIcon(round.round_decision)}
                                    <span className="ml-2">{round.round_decision.replace('_', ' ').toUpperCase()}</span>
                                </div>
                              ) : (
                                  <div className="flex items-center px-3 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-600 shadow-sm">
                                  {round.interview_status === 'scheduled' ? (
                                    <>
                                        <Calendar className="w-4 h-4 mr-2" />
                                      SCHEDULED
                                    </>
                                  ) : (
                                    <>
                                        <Clock className="w-4 h-4 mr-2" />
                                      PENDING
                                    </>
                                  )}
                                </div>
                              )}
                              
                              {round.overall_rating && (
                                  <div className="flex items-center text-sm bg-yellow-50 px-3 py-1 rounded-full border border-yellow-200">
                                    <Star className="w-4 h-4 text-yellow-500 mr-1" />
                                    <span className="font-medium text-yellow-700">{round.overall_rating}/5</span>
                                </div>
                              )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Resume Preview Modal */}
      {showResumePreview && currentResume && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowResumePreview(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">
                      Resume Preview
                    </h3>
                    <p className="text-sm text-gray-600">
                      {currentResume.applicant?.applicant_name} - {currentResume.filename}
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => downloadResume(currentResume.applicant?.ticket_id, currentResume.filename)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      <span>Download</span>
                    </button>
                    <button
                      onClick={() => setShowResumePreview(false)}
                      className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </div>
                <div className="mt-4">
                  {currentResume.type?.includes('pdf') ? (
                    <iframe
                      src={currentResume.url}
                      className="w-full h-[70vh] border border-gray-200 rounded-lg"
                      title="Resume Preview"
                    />
                  ) : currentResume.type?.includes('image') ? (
                    <img
                      src={currentResume.url}
                      alt="Resume Preview"
                      className="max-w-full h-auto mx-auto border border-gray-200 rounded-lg"
                    />
                  ) : (
                    <div className="text-center py-12">
                      <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                      <h4 className="text-lg font-semibold text-gray-600 mb-2">
                        Preview Not Available
                      </h4>
                      <p className="text-gray-500 mb-4">
                        This file type cannot be previewed in the browser.
                      </p>
                      <button
                        onClick={() => downloadResume(currentResume.applicant?.ticket_id, currentResume.filename)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                      >
                        Download Resume
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

       {/* Candidate Status Modal */}
       {showCandidateStatus && selectedCandidateForInterview && selectedJobForInterviews && (
         <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]" style={{ zIndex: 9999 }}>
           <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden m-4">
             <div className="flex items-center justify-between p-6 border-b border-gray-200">
               <div className="flex items-center gap-3">
                 <div className="p-2 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg">
                   <MessageSquare className="w-6 h-6 text-white" />
                 </div>
                 <div>
                   <h3 className="text-xl font-semibold text-gray-800">Interview Status</h3>
                   <p className="text-sm text-gray-600">
                     {selectedCandidateForInterview.applicant_name || selectedCandidateForInterview.candidateName} • {selectedJobForInterviews.job_title}
                   </p>
                 </div>
               </div>
               <button
                 onClick={() => {
                   setShowCandidateStatus(false);
                   setSelectedCandidateForInterview(null);
                   setSelectedJobForInterviews(null);
                 }}
                 className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
               >
                 <X className="w-5 h-5 text-gray-500" />
               </button>
             </div>
             
             <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
               <CandidateInterviewStatus 
                 ticketId={selectedJobForInterviews.ticket_id}
                 candidateId={selectedCandidateForInterview.candidate_id || selectedCandidateForInterview.id}
                 candidateData={selectedCandidateForInterview}
                 isEmbedded={true}
                 onClose={() => {
                   setShowCandidateStatus(false);
                   setSelectedCandidateForInterview(null);
                   setSelectedJobForInterviews(null);
                 }}
                 onLoadComplete={() => {
                   const candidateKey = `${selectedCandidateForInterview.applicant_name}-${selectedCandidateForInterview.applicant_email}`;
                   setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
                 }}
               />
             </div>
           </div>
         </div>
       )}

      {/* Interview Scheduler Modal */}
      {showInterviewScheduler && selectedCandidateForInterview && selectedJobForInterviews && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowInterviewScheduler(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">
                      Schedule Interview
                    </h3>
                    <p className="text-sm text-gray-600">
                      {selectedCandidateForInterview.applicant_name} - {selectedCandidateForInterview.applicant_email}
                    </p>
                  </div>
                  <button
                    onClick={() => setShowInterviewScheduler(false)}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Close
                  </button>
                </div>
                 <div className="mt-4">
                   <InterviewScheduler 
                     key={`${selectedJobForInterviews.ticket_id}-${selectedCandidateForInterview.candidate_id || selectedCandidateForInterview.id}`}
                     ticketId={selectedJobForInterviews.ticket_id}
                     candidateId={selectedCandidateForInterview.candidate_id || selectedCandidateForInterview.id}
                     candidateData={selectedCandidateForInterview}
                     onInterviewScheduled={(interviewId) => {
                       setShowInterviewScheduler(false);
                       setSelectedCandidateForInterview(null);
                       setSelectedJobForInterviews(null);
                     }}
                     onOpenManagerFeedback={onOpenManagerFeedback}
                   />
                 </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoundBasedCandidateFilter;
