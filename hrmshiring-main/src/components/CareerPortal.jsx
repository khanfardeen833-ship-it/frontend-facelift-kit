import React, { useState, useEffect, useRef, useCallback } from 'react';
import ModalPortal from './ModalPortal';
import { useAuth } from '../contexts/AuthContext';
import {
  Plus,
  Search,
  MapPin,
  DollarSign,
  Briefcase,
  Eye,
  Clock,
  Star,
  Calendar,
  Loader,
  RefreshCw,
  Upload,
  FileText,
  Send,
  CheckCircle,
  X,
  Download,
  Users,
  Mail,
  Phone,
  Filter,
  SortAsc,
  SortDesc,
  UserCheck,
  Target,
  TrendingUp,
  Award,
  Zap,
  FileSearch,
  Tag,
  Activity,
  BarChart3,
  History,
  Database,
  Wifi,
  AlertCircle,
  Brain,
  Sparkles,
  Settings,
  Play,
  Pause,
  CheckSquare,
  Shield,
  AlertTriangle,
  User,
  MessageSquare,
  Video,
  Phone as PhoneIcon,
  Trash2,
  Edit
} from 'lucide-react';

// Import interview components
import InterviewRoundsManager from './InterviewRoundsManager';
import InterviewScheduler from './InterviewScheduler';
import InterviewFeedback from './InterviewFeedback';
import CandidateInterviewStatus from './CandidateInterviewStatus';
import InterviewManager from './InterviewManager';
import JobCreationForm from './JobCreationForm';

// API Configuration
const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',
  API_KEY: 'sk-hiring-bot-2024-secret-key-xyz789',
  DEMO_MODE: false
};

// Helper function to get full URL
const getApiUrl = (endpoint) => `${API_CONFIG.BASE_URL}${endpoint}`;

// Helper function to get headers
const getHeaders = (contentType = 'application/json') => ({
  'X-API-Key': API_CONFIG.API_KEY,
  'Content-Type': contentType
});

const CareerPortal = ({ userRole = 'hr' }) => {
  const { user, isAuthenticated } = useAuth();
  // Basic states
  const [apiJobs, setApiJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [showJobForm, setShowJobForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);
  const [editingJob, setEditingJob] = useState(null);
  const [showEditJobForm, setShowEditJobForm] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [showApplicationForm, setShowApplicationForm] = useState(false);
  const [applicationJob, setApplicationJob] = useState(null);
  const [applicationStatus, setApplicationStatus] = useState(null);

  // HR-specific states
  const [showHRDashboard, setShowHRDashboard] = useState(false);
  const [selectedJobApplications, setSelectedJobApplications] = useState(null);
  const [jobApplications, setJobApplications] = useState({});
  const [loadingApplications, setLoadingApplications] = useState(false);
  const [sortBy, setSortBy] = useState('date');
  const [dashboardJustOpened, setDashboardJustOpened] = useState(false);
  
  // Interview management states
  const [activeTab, setActiveTab] = useState('jobs'); // 'jobs', 'applications', 'interviews'
  const [selectedJobForInterviews, setSelectedJobForInterviews] = useState(null);
  const [selectedCandidateForInterview, setSelectedCandidateForInterview] = useState(null);
  const [showInterviewRounds, setShowInterviewRounds] = useState(false);
  const [showInterviewScheduler, setShowInterviewScheduler] = useState(false);
  const [showInterviewFeedback, setShowInterviewFeedback] = useState(false);
  const [showInterviewManager, setShowInterviewManager] = useState(false);
  const [showCandidateStatus, setShowCandidateStatus] = useState(false);
  
  const [viewStatusLoading, setViewStatusLoading] = useState({});
  const [togglingJobs, setTogglingJobs] = useState(new Set());
  const [sortOrder, setSortOrder] = useState('desc');

  // Enhanced Resume filtering states
  const [topResumes, setTopResumes] = useState({});
  const [loadingTopResumes, setLoadingTopResumes] = useState(false);
  const [filteringStatus, setFilterStatus] = useState({});
  const [filteringReport, setFilteringReport] = useState({});
  const [showTopResumes, setShowTopResumes] = useState(false);
  const [loadingFilteringReport, setLoadingFilteringReport] = useState(false);
  const [filteringProgress, setFilteringProgress] = useState({});
  const [aiAnalysisResults, setAiAnalysisResults] = useState({});

  // Advanced filtering states
  const [availableLocations, setAvailableLocations] = useState([]);
  const [availableSkills, setAvailableSkills] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loadingSearch, setLoadingSearch] = useState(false);
  
  // Job filter states
  const [selectedEmploymentType, setSelectedEmploymentType] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [sortField, setSortField] = useState('created_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [totalJobs, setTotalJobs] = useState(0);

  // Health monitoring
  const [healthStatus, setHealthStatus] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [jobHistory, setJobHistory] = useState({});
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Resume viewer states
  const [showResumeViewer, setShowResumeViewer] = useState(false);
  const [currentResume, setCurrentResume] = useState(null);
  const [resumeLoading, setResumeLoading] = useState(false);

  // Confirmation dialog state
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState({
    title: '',
    message: '',
    onConfirm: null,
    onCancel: null
  });

  // Bulk rejection states
  const [selectedCandidates, setSelectedCandidates] = useState(new Set());
  const [showBulkActions, setShowBulkActions] = useState(false);
  const [bulkRejectionProgress, setBulkRejectionProgress] = useState(null);
  const [bulkRejectionResults, setBulkRejectionResults] = useState(null);
  const [customThreshold, setCustomThreshold] = useState('');
  const [showCustomThreshold, setShowCustomThreshold] = useState(false);
  const customThresholdInputRef = useRef(null);

  // Memoized handler for custom threshold input
  const handleCustomThresholdChange = useCallback((e) => {
    const value = e.target.value;
    console.log('🔍 Input change - value:', value, 'type:', typeof value);
    
    // Allow empty string, numbers, and decimal points - more permissive
    if (value === '' || /^[\d.]*$/.test(value)) {
      console.log('✅ Valid input, allowing:', value);
      // Don't update state - let the input handle its own value
    } else {
      console.log('❌ Invalid input rejected:', value);
      // Revert to previous valid value by preventing the change
      e.preventDefault();
    }
  }, []);

  // Handle Enter key press in custom threshold input
  const handleCustomThresholdKeyPress = useCallback((e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleCustomThresholdSubmit();
    }
  }, [customThreshold]);

  // Effect to maintain focus on the custom threshold input
  useEffect(() => {
    if (showCustomThreshold && customThresholdInputRef.current) {
      const input = customThresholdInputRef.current;
      // Focus the input after a short delay to ensure it's rendered
      const focusTimeout = setTimeout(() => {
        input.focus({ preventScroll: true });
        input.select(); // Select all text for easy replacement
      }, 50);
      
      return () => clearTimeout(focusTimeout);
    }
  }, [showCustomThreshold, customThreshold]);

  // Delete job states
  const [deletingJob, setDeletingJob] = useState(false);
  const [jobToDelete, setJobToDelete] = useState(null);

  // Bulk selection functions
  const toggleCandidateSelection = (candidateIndex) => {
    const newSelected = new Set(selectedCandidates);
    if (newSelected.has(candidateIndex)) {
      newSelected.delete(candidateIndex);
    } else {
      newSelected.add(candidateIndex);
    }
    setSelectedCandidates(newSelected);
    setShowBulkActions(newSelected.size > 0);
  };

  const selectAllCandidates = () => {
    // Get current applications and top resumes data
    const currentApplications = (jobApplications && jobApplications[selectedJobApplications?.ticket_id]) || [];
    const currentTopResumes = (topResumes && topResumes[selectedJobApplications?.ticket_id]) || [];
    const currentList = showTopResumes ? currentTopResumes : currentApplications;
    const allIds = currentList.map((_, index) => index);
    setSelectedCandidates(new Set(allIds));
    setShowBulkActions(true);
  };

  const deselectAllCandidates = () => {
    setSelectedCandidates(new Set());
    setShowBulkActions(false);
  };

  const getSelectedCandidatesData = () => {
    // Get current applications and top resumes data
    const currentApplications = (jobApplications && jobApplications[selectedJobApplications?.ticket_id]) || [];
    const currentTopResumes = (topResumes && topResumes[selectedJobApplications?.ticket_id]) || [];
    const currentList = showTopResumes ? currentTopResumes : currentApplications;
    return Array.from(selectedCandidates).map(index => ({
      index,
      data: currentList[index],
      id: currentList[index].id || index
    }));
  };

  const getUnselectedCandidatesData = () => {
    // Get current applications and top resumes data
    const currentApplications = (jobApplications && jobApplications[selectedJobApplications?.ticket_id]) || [];
    const currentTopResumes = (topResumes && topResumes[selectedJobApplications?.ticket_id]) || [];
    const currentList = showTopResumes ? currentTopResumes : currentApplications;
    return currentList
      .map((candidate, index) => ({ index, data: candidate, id: candidate.id || index }))
      .filter(candidate => !selectedCandidates.has(candidate.index));
  };

  // Bulk rejection functions
  const handleBulkRejectSelected = async () => {
    const selectedData = getSelectedCandidatesData();
    if (selectedData.length === 0) return;

    setConfirmDialog({
      title: 'Reject Selected Candidates',
      message: `Are you sure you want to reject ${selectedData.length} selected candidate(s)? This will send rejection emails to all selected candidates.`,
      onConfirm: () => performBulkRejection(selectedData, 'selected'),
      onCancel: () => setShowConfirmDialog(false)
    });
    setShowConfirmDialog(true);
  };

  const handleBulkRejectUnselected = async () => {
    const unselectedData = getUnselectedCandidatesData();
    if (unselectedData.length === 0) return;

    setConfirmDialog({
      title: 'Reject Unselected Candidates',
      message: `Are you sure you want to reject ${unselectedData.length} unselected candidate(s)? This will send rejection emails to all candidates except the ones you've selected.`,
      onConfirm: () => performBulkRejection(unselectedData, 'unselected'),
      onCancel: () => setShowConfirmDialog(false)
    });
    setShowConfirmDialog(true);
  };

  const handleCustomThresholdSubmit = async () => {
    // Get value from input ref
    const inputValue = customThresholdInputRef.current?.value || '';
    const threshold = parseFloat(inputValue);
    console.log('🔍 Submit - inputValue:', inputValue, 'threshold:', threshold);
    
    if (isNaN(threshold) || threshold < 0 || threshold > 50) {
      alert('Please enter a valid percentage between 0 and 50');
      return;
    }
    
    // Execute the bulk rejection
    await handleBulkRejectBelowScore(threshold / 100);
    
    // Clear the input after successful operation
    if (customThresholdInputRef.current) {
      customThresholdInputRef.current.value = '';
    }
    
    // Ensure the input field stays visible and focused
    setTimeout(() => {
      if (customThresholdInputRef.current) {
        customThresholdInputRef.current.focus({ preventScroll: true });
      }
    }, 100);
  };

  const handleBulkRejectBelowScore = async (threshold) => {
    // Get current applications and top resumes data
    const currentApplications = (jobApplications && jobApplications[selectedJobApplications?.ticket_id]) || [];
    const currentTopResumes = (topResumes && topResumes[selectedJobApplications?.ticket_id]) || [];
    const currentList = showTopResumes ? currentTopResumes : currentApplications;
    
    // CRITICAL FIX: Use the original applications array to get correct indices that match backend metadata
    const originalApplications = (jobApplications && jobApplications[selectedJobApplications?.ticket_id]) || [];
    
    const candidatesBelowThreshold = currentList
      .map((candidate, index) => {
        // Find the original index in the metadata array by matching name and email
        const originalIndex = originalApplications.findIndex(orig => 
          orig.applicant_name === candidate.applicant_name && 
          orig.applicant_email === candidate.applicant_email
        );
        return { 
          index: originalIndex >= 0 ? originalIndex : index, // Use original index if found, fallback to current index
          data: candidate, 
          id: candidate.id || index 
        };
      })
      .filter(candidate => {
        // Get the score from various possible locations
        let score = 0;
        if (candidate.data.scores && candidate.data.scores.overall) {
          score = candidate.data.scores.overall;
        } else if (candidate.data.score) {
          score = candidate.data.score;
        } else if (candidate.data.ai_score) {
          score = candidate.data.ai_score;
        } else if (candidate.data.overall_score) {
          score = candidate.data.overall_score;
        }
        
        // Only reject if we have a valid score and it's below threshold
        // Include candidates with 0% scores as they should be rejected if threshold > 0
        const shouldReject = score >= 0 && score < threshold;
        
        // Log for debugging
        console.log(`Candidate ${candidate.data.applicant_name}: score=${score}, threshold=${threshold}, shouldReject=${shouldReject}`);
        console.log(`Candidate data:`, candidate.data);
        
        return shouldReject;
      });

    if (candidatesBelowThreshold.length === 0) {
      alert(`No candidates found with scores below ${(threshold * 100).toFixed(1)}%`);
      return;
    }

    // Additional safety check - log the candidates that will be rejected
    console.log(`Candidates to be rejected:`, candidatesBelowThreshold.map(c => ({
      name: c.data.applicant_name,
      score: c.data.scores?.overall || c.data.score || c.data.ai_score || c.data.overall_score || 0,
      index: c.index
    })));

    // Create detailed message showing which candidates will be rejected
    const candidateList = candidatesBelowThreshold.map(candidate => {
      const score = candidate.data.scores?.overall || candidate.data.score || candidate.data.ai_score || candidate.data.overall_score || 0;
      return `• ${candidate.data.applicant_name}: ${(score * 100).toFixed(1)}%`;
    }).join('\n');

    // Final safety check - ensure no high-scoring candidates are being rejected
    const highScoringCandidates = candidatesBelowThreshold.filter(candidate => {
      const score = candidate.data.scores?.overall || candidate.data.score || candidate.data.ai_score || candidate.data.overall_score || 0;
      return score >= 0.5; // 50% threshold - maximum allowed
    });

    if (highScoringCandidates.length > 0) {
      alert(`ERROR: High-scoring candidates detected in rejection list! This should not happen. Please refresh the page and try again.`);
      console.error('High-scoring candidates in rejection list:', highScoringCandidates);
      return;
    }

    setConfirmDialog({
      title: 'Reject Low-Scoring Candidates',
      message: `Are you sure you want to reject ${candidatesBelowThreshold.length} candidate(s) with scores below ${(threshold * 100).toFixed(1)}%?\n\nCandidates to be rejected:\n${candidateList}\n\nThis will send rejection emails to all these candidates.`,
      onConfirm: () => performBulkRejection(candidatesBelowThreshold, 'below_score'),
      onCancel: () => setShowConfirmDialog(false)
    });
    setShowConfirmDialog(true);
  };

  const performBulkRejection = async (candidatesToReject, type) => {
    setShowConfirmDialog(false);
    
    // Debug: Log exactly what we're sending to the backend
    console.log('=== BULK REJECTION DEBUG ===');
    console.log('Candidates to reject:', candidatesToReject);
    console.log('Candidate indices being sent:', candidatesToReject.map(c => c.index));
    console.log('Candidate names being sent:', candidatesToReject.map(c => c.data.applicant_name));
    console.log('Candidate scores being sent:', candidatesToReject.map(c => {
      const score = c.data.scores?.overall || c.data.score || c.data.ai_score || c.data.overall_score || 0;
      return `${c.data.applicant_name}: ${(score * 100).toFixed(1)}%`;
    }));
    console.log('=== END DEBUG ===');
    setBulkRejectionProgress({
      total: candidatesToReject.length,
      completed: 0,
      failed: 0,
      current: null,
      type
    });

    try {
      // Prepare candidate IDs for bulk API call
      // Send the actual array index (0-based) since backend expects array indices
      const candidateIds = candidatesToReject.map(candidate => candidate.index);
      
      // Final safety check before API call
      const highScoringCandidates = candidatesToReject.filter(candidate => {
        const score = candidate.data.scores?.overall || candidate.data.score || candidate.data.ai_score || candidate.data.overall_score || 0;
        return score >= 0.5; // 50% threshold - maximum allowed
      });

      if (highScoringCandidates.length > 0) {
        console.error('CRITICAL ERROR: High-scoring candidates detected in API call!', highScoringCandidates);
        alert('ERROR: High-scoring candidates detected in rejection list! Aborting to prevent incorrect rejections.');
        return;
      }
      
      // Show progress
      setBulkRejectionProgress(prev => ({
        ...prev,
        current: `Processing ${candidateIds.length} candidates...`
      }));

      // Call the bulk rejection API
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/candidates/bulk-reject`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_ids: candidateIds,
          ticket_id: selectedJobApplications?.ticket_id,
          type: type
        })
      });

      const responseData = await response.json();
      
      console.log('🚫 CareerPortal API Response:', {
        status: response.status,
        success: responseData.success,
        data: responseData
      });

      if (response.ok && responseData.success) {
        // Convert API results to our format
        const results = {
          successful: responseData.results.successful.map(success => ({
            data: { applicant_name: success.name, applicant_email: success.email },
            index: success.candidate_id - 1,
            id: success.candidate_id
          })),
          failed: responseData.results.failed.map(failure => ({
            data: { applicant_name: `Candidate ${failure.candidate_id}` },
            index: failure.candidate_id - 1,
            id: failure.candidate_id,
            error: failure.error
          })),
          total: responseData.results.total
        };

        setBulkRejectionProgress(prev => ({
          ...prev,
          completed: candidatesToReject.length
        }));

        // Close progress modal and show results
        setTimeout(() => {
          setBulkRejectionProgress(null);
          setBulkRejectionResults(results);
          
          // Refresh the data to show updated status
          console.log('🔄 Refreshing data after rejection...');
          fetchJobApplications();
        }, 500); // Small delay to show completion
      } else {
        // Handle API error
        setTimeout(() => {
          setBulkRejectionProgress(null);
          setBulkRejectionResults({
            successful: [],
            failed: candidatesToReject.map(candidate => ({
              ...candidate,
              error: responseData.error || 'API call failed'
            })),
            total: candidatesToReject.length
          });
        }, 500);
      }
    } catch (error) {
      // Handle network or other errors
      setTimeout(() => {
        setBulkRejectionProgress(null);
        setBulkRejectionResults({
          successful: [],
          failed: candidatesToReject.map(candidate => ({
            ...candidate,
            error: error.message
          })),
          total: candidatesToReject.length
        });
      }, 500);
    }
    
    // Clear selections and refresh data
    setSelectedCandidates(new Set());
    setShowBulkActions(false);
    
    // Refresh the applications list
    if (selectedJobApplications?.ticket_id) {
      fetchJobApplications(selectedJobApplications.ticket_id);
      fetchTopResumes(selectedJobApplications.ticket_id);
    }
  };

  // Refs
  const fetchingJobs = useRef(false);
  const fetchingStats = useRef(false);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);
  const pollIntervalRef = useRef(null);

  // Force reset dashboard state
  const forceResetDashboard = () => {
    // Reset dashboard state
    setShowHRDashboard(false);
    setSelectedJobApplications(null);
    setShowTopResumes(false);
    setFilterStatus(null);
    
    // Clear any stored state
    if (typeof window !== 'undefined') {
      window.localStorage.removeItem('hr_dashboard_state');
    }
  };

  // Make global functions available for debugging (production: remove or comment out)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.resetHRDashboard = forceResetDashboard;
      window.getDashboardState = () => ({
        showHRDashboard,
        selectedJobApplications: selectedJobApplications?.ticket_id,
        userRole,
        isAuthenticated
      });
    }
    
    return () => {
      if (typeof window !== 'undefined') {
        delete window.resetHRDashboard;
        delete window.getDashboardState;
      }
    };
  }, [showHRDashboard, selectedJobApplications, userRole, isAuthenticated]);

  // Toggle job visibility
  const toggleJobVisibility = async (jobId) => {
    try {
      console.log(`🔄 Toggling visibility for job: ${jobId}`);
      
      // Add to loading state
      setTogglingJobs(prev => new Set([...prev, jobId]));
      
      const response = await makeAPICall(`/api/jobs/${jobId}/toggle-visibility`, {
        method: 'POST',
        headers: getHeaders()
      });
      
      if (response.success) {
        console.log('✅ Job visibility toggled successfully:', response.data);
        
        // Update the job in the state
        setApiJobs(prevJobs => 
          prevJobs.map(job => 
            job.ticket_id === jobId 
              ? { ...job, is_visible: response.data.is_visible }
              : job
          )
        );
        
        // Show success message with better styling
        const message = response.data.is_visible 
          ? '🚀 Job started successfully! It\'s now visible on the career portal.' 
          : '⏸️ Job stopped successfully! It\'s now hidden from the career portal.';
        
        // Create a temporary success notification
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white font-semibold transform transition-all duration-300 ${
          response.data.is_visible 
            ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
            : 'bg-gradient-to-r from-orange-500 to-red-500'
        }`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Remove notification after 3 seconds
        setTimeout(() => {
          notification.style.transform = 'translateX(100%)';
          setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
        
      } else {
        throw new Error(response.error || 'Failed to toggle job visibility');
      }
    } catch (error) {
      console.error('❌ Error toggling job visibility:', error);
      
      // Show error notification
      const errorNotification = document.createElement('div');
      errorNotification.className = 'fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white font-semibold bg-gradient-to-r from-red-500 to-red-600 transform transition-all duration-300';
      errorNotification.textContent = `❌ Error: ${error.message}`;
      document.body.appendChild(errorNotification);
      
      setTimeout(() => {
        errorNotification.style.transform = 'translateX(100%)';
        setTimeout(() => document.body.removeChild(errorNotification), 300);
      }, 3000);
    } finally {
      // Remove from loading state
      setTogglingJobs(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobId);
        return newSet;
      });
    }
  };

  // Enhanced API calls with better error handling
  const makeAPICall = async (endpoint, options = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // Increased timeout to 30 seconds

    try {
      // Ensure API key is always included
      const headers = {
          'X-API-Key': API_CONFIG.API_KEY,
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          ...options.headers
      };

      const fullUrl = `${API_CONFIG.BASE_URL}${endpoint}`;

      const response = await fetch(fullUrl, {
        method: options.method || 'GET',
        headers,
        signal: controller.signal,
        body: options.body
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ HTTP Error ${response.status}:`, errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText || errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      console.error('💥 API call error:', err);
      console.error('🔍 Error details:', {
        endpoint: `${API_CONFIG.BASE_URL}${endpoint}`,
        method: options.method || 'GET',
        errorType: err.name,
        errorMessage: err.message,
        stack: err.stack
      });
      throw err;
    }
  };

  // Show confirmation dialog
  const showConfirmation = (title, message, onConfirm) => {
    setConfirmDialog({
      title,
      message,
      onConfirm: () => {
        onConfirm();
        setShowConfirmDialog(false);
      },
      onCancel: () => setShowConfirmDialog(false)
    });
    setShowConfirmDialog(true);
  };

  // Check API health
  const checkHealth = async () => {
    try {
      const data = await makeAPICall('/api/health');
      setHealthStatus(data);
    } catch (err) {
      console.error('❌ Health check error:', err);
      setHealthStatus({ 
        status: 'error', 
        message: err.message,
        database: 'Connection failed',
        tunnel: 'API unavailable'
      });
    }
  };

  // Enhanced job fetching
  const fetchJobs = async (isManualRefresh = false) => {
    if (fetchingJobs.current && !isManualRefresh) {
      return;
    }

    try {
      fetchingJobs.current = true;
      setLoading(true);
      if (isManualRefresh) setError(null);

      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: perPage.toString(),
        sort: sortField,
        order: sortDirection
      });

      if (selectedLocation) params.append('location', selectedLocation);
      if (selectedSkills.length > 0) params.append('skills', selectedSkills.join(','));

      // Use dashboard endpoint for HR users to see all jobs (including hidden ones)
      const endpoint = userRole === 'hr' ? `/api/jobs/dashboard?${params}` : `/api/jobs/approved?${params}`;
      const data = await makeAPICall(endpoint);

      if (data.success && data.data && data.data.jobs) {
        setApiJobs(data.data.jobs);
        setTotalJobs(data.data.total || data.data.jobs.length);
        setLastUpdated(new Date());
        setError(null);
      } else {
        setApiJobs([]);
        setError('No jobs found in API response');
      }
    } catch (err) {
      console.error('❌ Error fetching jobs:', err);
      if (isManualRefresh || apiJobs.length === 0) {
        setError(err.message);
      }
      if (!isManualRefresh && apiJobs.length === 0) {
        setApiJobs([]);
      }
    } finally {
      fetchingJobs.current = false;
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const data = await makeAPICall('/api/stats');
      if (data.success && data.data && data.data.overall) {
        setStats(data.data.overall);
      }
    } catch (err) {
      // Stats fetch failed silently
    }
  };

  // Fetch locations and skills
  const fetchLocations = async () => {
    try {
      const data = await makeAPICall('/api/locations');
      setAvailableLocations(data.success ? data.data || [] : Array.isArray(data) ? data : []);
    } catch (err) {
      setAvailableLocations([]);
    }
  };

  const fetchSkills = async () => {
    try {
      const data = await makeAPICall('/api/skills');
      setAvailableSkills(data.success ? data.data || [] : Array.isArray(data) ? data : []);
    } catch (err) {
      setAvailableSkills([]);
    }
  };

  // Advanced search
  const performAdvancedSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setLoadingSearch(true);
    try {
      const data = await makeAPICall(`/api/jobs/search?q=${encodeURIComponent(query)}`);
      if (data.success && data.data) {
        setSearchResults(data.data.jobs || []);
      }
    } catch (err) {
      // Search failed silently
    } finally {
      setLoadingSearch(false);
    }
  };

  // Enhanced filtering status with polling
  const fetchFilteringStatus = async (ticketId) => {
    const cleanId = cleanTicketId(ticketId);
    try {
      const data = await makeAPICall(`/api/tickets/${cleanId}/filtering-status`);
      if (data.success) {
        const statusData = data.data;

        setFilterStatus(prev => ({
          ...prev,
          [ticketId]: statusData
        }));

        const isRunning = statusData.status === 'running' ||
          (statusData.filtering_info && statusData.filtering_info.status === 'running') ||
          (!statusData.has_filtering_results && statusData.ready_for_filtering);

        const isCompleted = statusData.status === 'completed' ||
          (statusData.has_filtering_results && statusData.filtering_info?.status === 'completed');

        if (isRunning) {
          startFilteringPolling(ticketId);
        }

        if (isCompleted) {
          await Promise.all([
            fetchTopResumes(ticketId),
            fetchFilteringReport(ticketId)
          ]);
        }
      }
    } catch (err) {
      // Status fetch failed silently
    }
  };

  // Start polling for filtering progress
  const startFilteringPolling = (ticketId) => {
    const cleanId = cleanTicketId(ticketId);
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const data = await makeAPICall(`/api/tickets/${cleanId}/filtering-status`);
        if (data.success) {
          const statusData = data.data;

          setFilterStatus(prev => ({
            ...prev,
            [ticketId]: statusData
          }));

          const isCompleted = statusData.status === 'completed' ||
            (statusData.has_filtering_results && statusData.filtering_info?.status === 'completed') ||
            (statusData.has_filtering_results && statusData.resume_count > 0);

          const isFailed = statusData.status === 'failed' ||
            (statusData.filtering_info && statusData.filtering_info.status === 'failed');

          if (isCompleted || isFailed) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;

            if (isCompleted) {
              await Promise.all([
                fetchTopResumes(ticketId),
                fetchFilteringReport(ticketId)
              ]);
            }
          }
        }
      } catch (err) {
        // Polling failed silently
      }
    }, 2000);
  };

  // Fetch top resumes
  const fetchTopResumes = async (ticketId) => {
    const cleanId = cleanTicketId(ticketId);
    setLoadingTopResumes(true);
    try {
      const data = await makeAPICall(`/api/tickets/${cleanId}/top-resumes`);

      if (data.success) {
        let topResumesList = [];

        if (data.data) {
          if (Array.isArray(data.data)) {
            topResumesList = data.data;
          } else if (data.data.top_candidates && Array.isArray(data.data.top_candidates)) {
            topResumesList = data.data.top_candidates;
          } else if (data.data.top_resumes && Array.isArray(data.data.top_resumes)) {
            topResumesList = data.data.top_resumes;
          } else if (data.data.resumes && Array.isArray(data.data.resumes)) {
            topResumesList = data.data.resumes;
          } else if (data.data.filtered_resumes && Array.isArray(data.data.filtered_resumes)) {
            topResumesList = data.data.filtered_resumes;
          } else {
            const arrayProps = Object.values(data.data).filter(Array.isArray);
            if (arrayProps.length > 0) {
              topResumesList = arrayProps[0];
            }
          }
        }

        setTopResumes(prev => ({
          ...prev,
          [ticketId]: topResumesList
        }));
      } else {
        setTopResumes(prev => ({ ...prev, [ticketId]: [] }));
      }
    } catch (err) {
      setTopResumes(prev => ({ ...prev, [ticketId]: [] }));
    } finally {
      setLoadingTopResumes(false);
    }
  };

  // Enhanced filtering report fetch
  const fetchFilteringReport = async (ticketId) => {
    const cleanId = cleanTicketId(ticketId);
    setLoadingFilteringReport(true);
    try {
      const data = await makeAPICall(`/api/tickets/${cleanId}/filtering-report`);

      if (data.success) {
        setFilteringReport(prev => ({
          ...prev,
          [ticketId]: data.data
        }));
      }
    } catch (err) {
      setFilteringReport(prev => ({ ...prev, [ticketId]: null }));
    } finally {
      setLoadingFilteringReport(false);
    }
  };

  // Helper function to clean ticket ID (remove any suffix after underscore)
  const cleanTicketId = (ticketId) => {
    if (!ticketId) return ticketId;
    // Remove any suffix after underscore (e.g., "96842d6ce2_web-dev" -> "96842d6ce2")
    return ticketId.split('_')[0];
  };

  // Trigger resume filtering
  const triggerResumeFiltering = async (ticketId, forceRefilter = false) => {
    const cleanId = cleanTicketId(ticketId);

    try {
      const data = await makeAPICall(`/api/tickets/${cleanId}/filter-resumes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          force: forceRefilter,  // Only force re-filtering when explicitly requested
          incremental: true      // Use incremental mode by default
        })
      });

      if (data.success) {
        // Check if filtering was already completed
        if (data.status === 'completed' && !forceRefilter) {
          alert('✅ AI Resume Filtering has already been completed for this job!\n\n' + 
                `📊 Results: ${data.data?.total_resumes || 0} resumes processed, ${data.data?.top_candidates_count || 0} top candidates identified.\n` +
                `🕒 Filtered on: ${data.data?.filtered_at ? new Date(data.data.filtered_at).toLocaleString() : 'Recently'}\n\n` +
                'Use "Re-filter" button if you want to re-run the analysis.');
          
          // Update status to show completed state
          setFilterStatus(prev => ({
            ...prev,
            [ticketId]: {
              status: 'completed',
              message: 'Filtering completed',
              completed_at: data.data?.filtered_at,
              total_resumes: data.data?.total_resumes,
              top_candidates_count: data.data?.top_candidates_count
            }
          }));
          
          // Fetch the existing results
          await Promise.all([
            fetchTopResumes(ticketId),
            fetchFilteringReport(ticketId)
          ]);
        } else {
          alert('🤖 AI Resume Filtering has been triggered! The system will analyze ALL resumes (including newly uploaded ones) and rank candidates based on job requirements. Check back in a few minutes for results.');

          setFilterStatus(prev => ({
            ...prev,
            [ticketId]: {
              status: 'running',
              message: 'AI analysis in progress...',
              started_at: new Date().toISOString()
            }
          }));

          startFilteringPolling(ticketId);
          await fetchJobApplications(ticketId);
        }
      } else {
        console.error('❌ API returned error:', data.message || 'Unknown error');
        alert('Failed to trigger resume filtering: ' + (data.message || 'Unknown error'));
      }
    } catch (err) {
      console.error('💥 EXCEPTION occurred during API call:', err);
      console.error('Error details:', {
        message: err.message,
        stack: err.stack,
        name: err.name
      });
      alert('Failed to trigger resume filtering: ' + err.message);
    }
  };

  // Fetch applications for a job
  const fetchJobApplications = async (ticketId) => {
    const cleanId = cleanTicketId(ticketId);
    setLoadingApplications(true);
    try {
      const data = await makeAPICall(`/api/tickets/${cleanId}/resumes`);
      if (data.success) {
        const resumes = data.data.resumes || [];
        
        // Debug logging for Ahmed Hassan
        const ahmedResume = resumes.find(r => 
          r.applicant_name && r.applicant_name.toLowerCase().includes('ahmed') && 
          r.applicant_name.toLowerCase().includes('hassan')
        );
        if (ahmedResume) {
          console.log('🔍 Ahmed Hassan Resume Data from API:', ahmedResume);
        }
        
        setJobApplications(prev => ({
          ...prev,
          [ticketId]: resumes
        }));
      }
    } catch (err) {
      console.error('fetchJobApplications error:', err);
      setJobApplications(prev => ({ ...prev, [ticketId]: [] }));
    } finally {
      setLoadingApplications(false);
    }
  };

  // Send top resumes
  const sendTopResumes = async (ticketId) => {
    const cleanId = cleanTicketId(ticketId);
    try {
      const currentTopResumes = topResumes[ticketId] || [];
      if (currentTopResumes.length === 0) {
        alert('❌ No top candidates available to send. Please run AI filtering first.');
        return;
      }

      const data = await makeAPICall(`/api/tickets/${cleanId}/send-top-resumes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ticket_id: cleanId,
          candidate_count: currentTopResumes.length
        })
      });

      if (data.success) {
        alert(`✅ Top resumes sent successfully! 
        
📧 ${currentTopResumes.length} candidate${currentTopResumes.length !== 1 ? 's' : ''} forwarded to hiring manager.
        
The best candidates based on AI analysis have been sent for review.`);
      } else {
        alert(`❌ Failed to send top resumes: ${data.message || 'Unknown error'}`);
      }
    } catch (err) {
      let errorMessage = 'Failed to send top resumes.';

      if (err.message.includes('500')) {
        errorMessage = `Server Error (500): The backend encountered an internal error.`;
      } else if (err.message.includes('404')) {
        errorMessage = 'API endpoint not found. Check if the send-top-resumes endpoint exists in your backend.';
      } else if (err.message.includes('403')) {
        errorMessage = 'Access denied. Check your API key permissions.';
      } else {
        errorMessage = `Network error: ${err.message}`;
      }

      alert(`❌ ${errorMessage}`);
    }
  };

  // Preview and download resume functions
  const previewResume = async (ticketId, filename, applicant) => {
    setResumeLoading(true);
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${ticketId}/resumes/${filename}`, {
        method: 'GET',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'ngrok-skip-browser-warning': 'true'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to preview resume: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      setCurrentResume({ url, filename, applicant, type: blob.type });
      setShowResumeViewer(true);
    } catch (err) {
      alert('Failed to preview resume. Please try downloading instead.');
    } finally {
      setResumeLoading(false);
    }
  };

  const downloadResume = async (ticketId, filename) => {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${ticketId}/resumes/${filename}`, {
        method: 'GET',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'ngrok-skip-browser-warning': 'true'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to download resume: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Failed to download resume. Please try again.');
    }
  };

  const deleteCandidate = async (ticketId, application) => {
    try {
      console.log('🚀 DELETE CANDIDATE CALLED');
      console.log('🔍 Candidate to delete:', application);
      console.log('🔍 Ticket ID:', ticketId);
      
      if (!window.confirm(`Are you sure you want to delete ${application.applicant_name}? This action cannot be undone.`)) {
        return;
      }
      
      // ENHANCED APPROACH: Use the correct data source based on current view
      const currentApplications = (jobApplications && jobApplications[ticketId]) || [];
      const currentTopResumes = (topResumes && topResumes[ticketId]) || [];
      
      console.log('🔍 Current view - showTopResumes:', showTopResumes);
      console.log('🔍 Applications available:', currentApplications.length);
      console.log('🔍 Top resumes available:', currentTopResumes.length);
      
      // Determine which data source to use based on current view
      let searchList = currentApplications;
      let listType = 'applications';
      
      if (showTopResumes && currentTopResumes.length > 0) {
        searchList = currentTopResumes;
        listType = 'top_resumes';
        console.log('🔍 Using top resumes list for search');
      } else {
        console.log('🔍 Using applications list for search');
      }
      
      console.log('🔍 Total candidates in search list:', searchList.length);
      console.log('🔍 All candidates in search list:', searchList.map((app, idx) => ({
        index: idx,
        name: app.applicant_name,
        email: app.applicant_email,
        status: app.status
      })));
      
      // Find candidate in the search list by exact match
      const candidateIndex = searchList.findIndex(app => {
        const nameMatch = app.applicant_name === application.applicant_name;
        const emailMatch = app.applicant_email === application.applicant_email;
        console.log(`🔍 Checking candidate ${app.applicant_name}: nameMatch=${nameMatch}, emailMatch=${emailMatch}`);
        return nameMatch && emailMatch;
      });
      
      if (candidateIndex === -1) {
        console.error('❌ CANDIDATE NOT FOUND');
        console.error('🔍 Looking for:', { name: application.applicant_name, email: application.applicant_email });
        console.error('🔍 Available candidates:', searchList.map(app => ({ name: app.applicant_name, email: app.applicant_email })));
        console.error('🔍 Search list type:', listType);
        
        // Try name-only match as fallback
        const nameOnlyIndex = searchList.findIndex(app => app.applicant_name === application.applicant_name);
        if (nameOnlyIndex !== -1) {
          console.log('🔍 Found by name only at index:', nameOnlyIndex);
          const foundCandidate = searchList[nameOnlyIndex];
          if (window.confirm(`Found candidate "${foundCandidate.applicant_name}" but email doesn't match. Delete anyway?`)) {
            return await deleteByIndex(ticketId, nameOnlyIndex, foundCandidate);
          }
        }
        
        // If not found in current view, try the other list
        const alternativeList = listType === 'applications' ? currentTopResumes : currentApplications;
        const alternativeType = listType === 'applications' ? 'top_resumes' : 'applications';
        
        if (alternativeList.length > 0) {
          console.log('🔍 Trying alternative list:', alternativeType);
          const altIndex = alternativeList.findIndex(app => 
            app.applicant_name === application.applicant_name && 
            app.applicant_email === application.applicant_email
          );
          
          if (altIndex !== -1) {
            console.log('🔍 Found in alternative list at index:', altIndex);
            if (window.confirm(`Candidate found in ${alternativeType} list. Delete from there?`)) {
              return await deleteByIndex(ticketId, altIndex, alternativeList[altIndex]);
            }
          }
        }
        
        alert('❌ Candidate not found in any list. The data may be out of sync. Please refresh the page and try again.');
        return;
      }
      
      console.log(`🗑️ FOUND CANDIDATE AT INDEX: ${candidateIndex}`);
      console.log('🗑️ Candidate details:', searchList[candidateIndex]);
      console.log('🗑️ Found in list type:', listType);
      
      return await deleteByIndex(ticketId, candidateIndex, searchList[candidateIndex]);
      
    } catch (error) {
      console.error('❌ Error in deleteCandidate:', error);
      alert(`Failed to delete candidate: ${error.message}`);
    }
  };
  
  // Helper function to perform the actual deletion
  const deleteByIndex = async (ticketId, candidateIndex, candidateData) => {
    try {
      console.log(`🚀 DELETING CANDIDATE AT INDEX ${candidateIndex}:`, candidateData.applicant_name);
      
      // Use the new delete endpoint for proper deletion
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/candidates/delete`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_id: candidateIndex,
          ticket_id: ticketId,
          candidate_email: candidateData.applicant_email,
          candidate_name: candidateData.applicant_name
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
        // Show success message from the new delete endpoint
        const message = result.message || `${candidateData.applicant_name} deleted successfully`;
        console.log('✅ Success message:', message);
        alert(`✅ ${message}`);
        
        // Force refresh the applications list
        console.log('🔄 Refreshing applications list...');
        await fetchJobApplications(ticketId);
        
        // Also refresh top resumes if they exist
        if (topResumes[ticketId]) {
          console.log('🔄 Refreshing top resumes...');
          await fetchTopResumes(ticketId);
        }
        
        console.log('✅ DELETION COMPLETED SUCCESSFULLY');
      } else {
        throw new Error(result.error || 'Unknown error occurred');
      }
      
    } catch (error) {
      console.error('❌ Error in deleteByIndex:', error);
      throw error;
    }
  };

  // Application submission
  const handleApplicationSubmit = async (formData, ticketId) => {
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('resume', formData.resumeFile);
      formDataToSend.append('applicant_name', formData.name);
      formDataToSend.append('applicant_email', formData.email);
      formDataToSend.append('applicant_phone', formData.phone || '');
      formDataToSend.append('cover_letter', formData.coverLetter || '');

      const response = await fetch(`${API_CONFIG.BASE_URL}/api/tickets/${ticketId}/resumes`, {
        method: 'POST',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'ngrok-skip-browser-warning': 'true'
        },
        body: formDataToSend
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (result.success) {
        setApplicationStatus({
          type: 'success',
          message: 'Application submitted successfully! 🎉',
          applicationId: result.application_id || result.id || ticketId
        });
        return true;
      } else {
        throw new Error(result.message || 'Failed to submit application');
      }
    } catch (err) {
      throw err;
    }
  };

  // Utility functions
  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) {
        return dateString;
      }
      
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      
      return `${day}/${month}/${year}`;
    } catch {
      return dateString;
    }
  };

  const getDaysAgo = (dateString) => {
    if (!dateString) return '';
    try {
      const postDate = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - postDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays === 1 ? '1 day ago' : `${diffDays} days ago`;
    } catch {
      return '';
    }
  };

  const getFilteringStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100 border-green-200';
      case 'running': return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'failed': return 'text-red-600 bg-red-100 border-red-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  // Component lifecycle
  useEffect(() => {
    mountedRef.current = true;
    
    // Ensure HR dashboard is hidden on mount
    forceResetDashboard();
    
    // Double-check after a short delay to ensure state is reset
    setTimeout(() => {
      if (showHRDashboard) {
        forceResetDashboard();
      }
    }, 100);

    Promise.all([
      fetchJobs(true),
      fetchStats(),
      checkHealth(),
      fetchLocations(),
      fetchSkills()
    ]);

    // Auto-refresh interval
    intervalRef.current = setInterval(() => {
      if (!error && apiJobs.length > 0) {
        fetchJobs(false);
        fetchStats();
        checkHealth();
      }
      
      // Check dashboard state consistency every minute
      if (showHRDashboard && !selectedJobApplications) {
        forceResetDashboard();
      }
    }, 60000);

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Refetch jobs when filters change
  useEffect(() => {
    if (mountedRef.current && (selectedLocation || selectedSkills.length > 0 || currentPage !== 1 || sortField !== 'created_at' || sortDirection !== 'desc')) {
      fetchJobs(true);
    }
  }, [selectedLocation, selectedSkills, currentPage, sortField, sortDirection]);

  // Monitor interview state changes
  useEffect(() => {
    // State monitoring for debugging (removed console logs)
  }, [selectedCandidateForInterview, selectedJobForInterviews, showInterviewScheduler]);

  // Handle dashboard state changes
  useEffect(() => {
    if (showHRDashboard && !selectedJobApplications) {
      // Dashboard open without job - force close
      forceResetDashboard();
    }
  }, [showHRDashboard, selectedJobApplications]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && showHRDashboard) {
        forceResetDashboard();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [showHRDashboard]);

  // Handle click outside dashboard
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (!showHRDashboard) return;
      
      const dashboard = document.getElementById('hr-dashboard');
      if (!dashboard) return;
      
      // Check if click was on interactive elements
      const isInteractive = e.target.closest('button, input, select, textarea, a, [role="button"]');
      if (isInteractive) return;
      
      // Check if click was outside dashboard
      if (!dashboard.contains(e.target)) {
        // Close after a short delay to allow for other interactions
        setTimeout(() => {
          if (showHRDashboard) {
            forceResetDashboard();
          }
        }, 100);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showHRDashboard]);

  // Auto-select job from Dashboard navigation
  useEffect(() => {
    const checkForSelectedJob = () => {
      const storedJobData = localStorage.getItem('selectedJobFromDashboard');
      console.log('CareerPortal: Checking for stored job data:', storedJobData);
      if (storedJobData) {
        try {
          const jobData = JSON.parse(storedJobData);
          console.log('CareerPortal: Parsed job data:', jobData);
          console.log('CareerPortal: Available jobs:', apiJobs.map(job => ({ id: job.ticket_id, title: job.job_title })));
          
          // Find the matching job in the current jobs list
          const matchingJob = apiJobs.find(job => job.ticket_id === jobData.ticket_id);
          console.log('CareerPortal: Matching job found:', matchingJob);
          
          if (matchingJob) {
            // Check if we need to open HR Dashboard
            if (jobData.openHRDashboard) {
              console.log('CareerPortal: Opening HR Dashboard for job:', matchingJob);
              // Use the same logic as the AI HR Dashboard button
              handleViewApplications(matchingJob);
            } else {
              console.log('CareerPortal: Setting selected job:', matchingJob);
              setSelectedJob(matchingJob);
            }
            
            // Clear the stored data only after successful selection
            localStorage.removeItem('selectedJobFromDashboard');
          } else {
            console.log('CareerPortal: No matching job found for ticket_id:', jobData.ticket_id);
            // Don't clear the data yet, wait for jobs to load
          }
        } catch (error) {
          console.error('CareerPortal: Error parsing stored job data:', error);
          localStorage.removeItem('selectedJobFromDashboard');
        }
      }
    };

    // Check for selected job after jobs are loaded
    if (apiJobs.length > 0) {
      console.log('CareerPortal: Jobs loaded, checking for selected job...');
      checkForSelectedJob();
    }
  }, [apiJobs]);

  // Also check when component mounts in case jobs are already loaded
  useEffect(() => {
    const storedJobData = localStorage.getItem('selectedJobFromDashboard');
    if (storedJobData && apiJobs.length > 0) {
      console.log('CareerPortal: Component mounted, checking for stored job...');
      const jobData = JSON.parse(storedJobData);
      const matchingJob = apiJobs.find(job => job.ticket_id === jobData.ticket_id);
      if (matchingJob) {
        // Check if we need to open HR Dashboard
        if (jobData.openHRDashboard) {
          console.log('CareerPortal: Opening HR Dashboard on mount for job:', matchingJob);
          handleViewApplications(matchingJob);
        } else {
          console.log('CareerPortal: Setting selected job on mount:', matchingJob);
          setSelectedJob(matchingJob);
        }
        
        localStorage.removeItem('selectedJobFromDashboard');
      }
    }
  }, []);

  // Event handlers
  const handleRefresh = async () => {
    setError(null);
    // Force reset dashboard state on refresh
    setShowHRDashboard(false);
    setSelectedJobApplications(null);
    setShowTopResumes(false);
    
    await Promise.all([
      fetchJobs(true),
      fetchStats(),
      checkHealth(),
      fetchLocations(),
      fetchSkills()
    ]);
  };

  const handleDeleteJob = async (job) => {
    setJobToDelete(job);
    setConfirmDialog({
      title: 'Delete Job Posting',
      message: `Are you sure you want to delete "${job.job_title}"? This action cannot be undone and will remove all associated data including applications and resumes.`,
      onConfirm: async () => {
        try {
          setDeletingJob(true);
          const response = await makeAPICall(`/api/jobs/${job.ticket_id}`, {
            method: 'DELETE'
          });
          
          if (response.success) {
            // Remove the job from the local state
            setApiJobs(prevJobs => prevJobs.filter(j => j.ticket_id !== job.ticket_id));
            setStats(prevStats => ({
              ...prevStats,
              total_jobs: (prevStats?.total_jobs || 0) - 1
            }));
            alert(`✅ Job "${job.job_title}" has been deleted successfully.`);
          } else {
            alert(`❌ Failed to delete job: ${response.error || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Error deleting job:', error);
          alert(`❌ Error deleting job: ${error.message}`);
        } finally {
          setDeletingJob(false);
          setJobToDelete(null);
          setShowConfirmDialog(false);
        }
      },
      onCancel: () => {
        setJobToDelete(null);
        setShowConfirmDialog(false);
      }
    });
    setShowConfirmDialog(true);
  };

  const handleEditJob = (job) => {
    setEditingJob(job);
    setShowEditJobForm(true);
  };

  const handleApplyToJob = (jobId) => {
    const job = apiJobs.find(j => j.ticket_id === jobId);
    if (job) {
      setApplicationJob(job);
      setShowApplicationForm(true);
    }
  };

  const handleViewApplications = async (job) => {
    // Validate job data before opening dashboard
    if (!job || !job.ticket_id) {
      console.error('❌ Invalid job data for HR Dashboard:', job);
      alert('Cannot open HR Dashboard: Invalid job data');
      return;
    }
    
    // Set the job first
    setSelectedJobApplications(job);
    
    // Then open the dashboard
    setShowHRDashboard(true);
    
    // Fetch the data
    try {
      await Promise.all([
        fetchJobApplications(job.ticket_id),
        fetchFilteringStatus(job.ticket_id),
        fetchTopResumes(job.ticket_id)
      ]);
    } catch (error) {
      console.error('❌ Error fetching data for HR Dashboard:', error);
      // Don't close the dashboard on error, just show the error
    }
  };

  const handleSearchChange = (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      performAdvancedSearch(query);
    } else {
      setSearchResults([]);
    }
  };

  const handleSkillToggle = (skill) => {
    setSelectedSkills(prev =>
      prev.includes(skill)
        ? prev.filter(s => s !== skill)
        : [...prev, skill]
    );
  };

  // Determine display jobs
  const displayJobs = searchQuery.trim() ? searchResults : apiJobs;
  const filteredJobs = displayJobs.filter(job => {
    // Text search filter
    const matchesSearch = !searchTerm || 
      job.job_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.required_skills?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.employment_type?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Location filter - case insensitive match
    const matchesLocation = !selectedLocation || 
      job.location?.trim().toLowerCase() === selectedLocation.toLowerCase();
    
    // Employment Type filter - normalized match (spaces to hyphens, lowercase)
    const matchesEmploymentType = !selectedEmploymentType || 
      job.employment_type?.trim().toLowerCase().replace(/\s+/g, '-') === selectedEmploymentType;
    
    // Status filter (for HR users)
    const matchesStatus = !selectedStatus || 
      (selectedStatus === 'live' && job.is_visible !== false) ||
      (selectedStatus === 'stopped' && job.is_visible === false);
    
    return matchesSearch && matchesLocation && matchesEmploymentType && matchesStatus;
  });

  // ENHANCED HR DASHBOARD COMPONENT
  const EnhancedHRDashboard = () => {
    // Don't render if no job is selected
    if (!selectedJobApplications) {
      return null;
    }
    
    // Don't render if user is not authenticated or doesn't have HR role
    if (!isAuthenticated || (!user?.role && userRole !== 'hr')) {
      return null;
    }
    
    // Add null checks for state variables
    let applications = (jobApplications && jobApplications[selectedJobApplications?.ticket_id]) || [];
    let topResumesList = (topResumes && topResumes[selectedJobApplications?.ticket_id]) || [];
    const filterStatus = (filteringStatus && filteringStatus[selectedJobApplications?.ticket_id]) || null;
    const report = (filteringReport && filteringReport[selectedJobApplications?.ticket_id]) || null;
    
    // Debug: Check what data we have
    console.log('🔍 EnhancedHRDashboard - Raw jobApplications data:', jobApplications);
    console.log('🔍 EnhancedHRDashboard - Applications for ticket:', selectedJobApplications?.ticket_id, applications);
    console.log('🔍 EnhancedHRDashboard - TopResumesList for ticket:', selectedJobApplications?.ticket_id, topResumesList);
    console.log('🔍 EnhancedHRDashboard - showTopResumes:', showTopResumes);
    console.log('🔍 EnhancedHRDashboard - Current display list length:', (showTopResumes ? topResumesList : applications).length);
    console.log('🔍 EnhancedHRDashboard - Applications length:', applications.length, 'TopResumes length:', topResumesList.length);
    if (applications.length > 0) {
      const ahmedApp = applications.find(app => app.applicant_name && app.applicant_name.toLowerCase().includes('ahmed'));
      if (ahmedApp) {
        console.log('🔍 EnhancedHRDashboard - Ahmed app data:', ahmedApp);
      }
    }
    if (topResumesList.length > 0) {
      const ahmedTopResume = topResumesList.find(app => app.applicant_name && app.applicant_name.toLowerCase().includes('ahmed'));
      if (ahmedTopResume) {
        console.log('🔍 EnhancedHRDashboard - Ahmed top resume data:', ahmedTopResume);
      }
    }
    
    // Fix: Merge final_decision data from applications into topResumesList
    if (showTopResumes && topResumesList.length > 0 && applications.length > 0) {
      topResumesList = topResumesList.map(topResume => {
        const matchingApp = applications.find(app => 
          app.applicant_name === topResume.applicant_name && 
          app.applicant_email === topResume.applicant_email
        );
        if (matchingApp) {
          return {
            ...topResume,
            final_decision: matchingApp.final_decision,
            status: matchingApp.status
          };
        }
        return topResume;
      });
      console.log('🔍 EnhancedHRDashboard - Merged topResumesList with final_decision data:', topResumesList);
    }
    
    // Filter applications for candidates - they should only see their own applications
    if ((userRole === 'candidate' || user?.role === 'candidate') && user && isAuthenticated) {
      applications = applications.filter(app => 
        app.applicant_email === user.email || 
        app.email === user.email ||
        app.user_email === user.email
      );
    }
    
    // Also filter top resumes for candidates
    if ((userRole === 'candidate' || user?.role === 'candidate') && user && isAuthenticated) {
      topResumesList = topResumesList.filter(app => 
        app.applicant_email === user.email || 
        app.email === user.email ||
        app.user_email === user.email
      );
    }

    // Enhanced button handlers
    const handleStartFiltering = async () => {
      if (applications.length === 0) {
        alert('⚠️ No applications found to filter. Please wait for candidates to apply first.');
        return;
      }

      // Check if filtering is already completed
      if (filterStatus?.status === 'completed') {
        showConfirmation(
          '🔄 Re-filter Resumes',
          `AI filtering has already been completed for this job.\n\n` +
          `📊 Previous results: ${filterStatus.total_resumes || 0} resumes processed\n` +
          `🕒 Completed: ${filterStatus.completed_at ? new Date(filterStatus.completed_at).toLocaleString() : 'Recently'}\n\n` +
          `Do you want to re-run the analysis?\n\n` +
          `🆕 INCREMENTAL MODE: Only new resumes (like Sahil Khan) will be processed and added to existing results.\n` +
          `⚡ This is much faster and preserves existing rankings.`,
          () => triggerResumeFiltering(selectedJobApplications.ticket_id, true)
        );
      } else {
        showConfirmation(
          '🤖 Start AI Filtering',
          `Start AI filtering for ${applications.length} application${applications.length !== 1 ? 's' : ''}?\n\nThis will analyze ALL resumes and rank candidates based on job requirements.`,
          () => triggerResumeFiltering(selectedJobApplications.ticket_id, false)
        );
      }
    };

    const handleViewTopCandidates = async () => {
      const newShowTopResumes = !showTopResumes;
      console.log('🔄 Switching view mode:', { currentShowTopResumes: showTopResumes, newShowTopResumes });
      
      // Always fetch applications when switching to show all applications
      if (!newShowTopResumes) {
        console.log('🔄 Switching to All Applications - fetching applications');
        await fetchJobApplications(selectedJobApplications.ticket_id);
      } else {
        console.log('🔄 Switching to Top Candidates - ensuring top resumes are loaded');
        // When switching to top candidates, ensure we have top resumes data
        if (topResumesList.length === 0) {
          console.log('🔄 No top resumes found - fetching them');
          await fetchTopResumes(selectedJobApplications.ticket_id);
        }
      }
      
      setShowTopResumes(newShowTopResumes);
    };

    const handleSendTopResumes = async () => {
      if (topResumesList.length === 0) {
        alert('❌ No top candidates available to send. Please run AI filtering first.');
        return;
      }

      showConfirmation(
        '📧 Send Top Resumes',
        `Send ${topResumesList.length} top candidate${topResumesList.length !== 1 ? 's' : ''} to hiring manager?\n\nThis will forward the best resumes based on AI analysis.`,
        () => sendTopResumes(selectedJobApplications.ticket_id)
      );
    };

    // Calculate score statistics
    const getScoreStats = () => {
      if (topResumesList.length === 0) return null;

      const scores = topResumesList.map(resume => {
        // Try different score formats from backend
        if (resume.score && typeof resume.score === 'number') {
          return resume.score;
        }
        if (resume.scores && resume.scores.overall) {
          // Convert "85.2%" to 0.852
          const scoreStr = resume.scores.overall;
          if (typeof scoreStr === 'string' && scoreStr.includes('%')) {
            return parseFloat(scoreStr.replace('%', '')) / 100;
          }
          return parseFloat(scoreStr) || 0;
        }
        if (resume.final_score && typeof resume.final_score === 'number') {
          return resume.final_score;
        }
        return 0;
      });
      
      const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
      const maxScore = Math.max(...scores);
      const minScore = Math.min(...scores);

      return { avgScore, maxScore, minScore };
    };

    const scoreStats = getScoreStats();

    return (
      <div 
        className="fixed inset-0 bg-white z-[9999] overflow-hidden" 
        style={{ 
          position: 'fixed', 
          top: '0px', 
          left: '0px', 
          right: '0px', 
          bottom: '0px', 
          width: '100vw', 
          height: '100vh',
          zIndex: 9999,
          backgroundColor: 'white',
          margin: '0px',
          padding: '0px',
          border: 'none',
          outline: 'none',
          overflow: 'hidden'
        }}
      >
        <div className="w-full h-full flex flex-col hr-dashboard-content" style={{ overflow: 'hidden' }}>
          {/* Header - Fixed */}
          <div className="flex justify-between items-start p-8 pb-4 border-b border-gray-200">
            <div>
              <h3 className="text-3xl font-bold text-gray-800 mb-2 flex items-center">
                <Brain className="w-8 h-8 mr-3 text-purple-600" />
                AI-Powered HR Dashboard
              </h3>
              <p className="text-gray-600">{selectedJobApplications?.job_title}</p>
              <p className="text-blue-600 text-sm font-medium">
                {applications.length} application{applications.length !== 1 ? 's' : ''} received
                {topResumesList.length > 0 && ` • ${topResumesList.length} top candidates identified`}
                {scoreStats && ` • Avg Score: ${(scoreStats.avgScore * 100).toFixed(1)}%`}
                {filterStatus?.status === 'completed' && filterStatus?.total_resumes && applications.length > filterStatus.total_resumes && (
                  <span className="text-orange-600 font-bold"> • NEW RESUMES DETECTED!</span>
                )}
                {topResumes?.data?.summary?.duplicate_groups_found > 0 && (
                  <span className="text-red-600 font-bold"> • DUPLICATE RESUME DETECTED!</span>
                )}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500 mb-2">Press ESC or click X to close</p>
              <button
                onClick={() => {
                  setShowHRDashboard(false);
                  setSelectedJobApplications(null);
                  setShowTopResumes(false);
                }}
                className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-full transition-colors"
                title="Close Dashboard"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-scroll p-8 pt-4" style={{ 
            height: 'calc(100vh - 140px)', 
            minHeight: '0',
            scrollbarWidth: 'auto', 
            scrollbarColor: '#475569 #e2e8f0',
            overflowY: 'scroll',
            WebkitOverflowScrolling: 'touch'
          }}>

          {/* New Resumes Notification Banner */}
          {filterStatus?.status === 'completed' && filterStatus?.total_resumes && applications.length > filterStatus.total_resumes && (
            <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-xl p-4 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                    <AlertTriangle className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-orange-800">New Resumes Detected!</h4>
                    <p className="text-orange-700 text-sm">
                      {applications.length - filterStatus.total_resumes} new resume{applications.length - filterStatus.total_resumes !== 1 ? 's' : ''} uploaded since last filtering. 
                      Click "Re-run AI Filtering" to include them in the analysis.
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleStartFiltering}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                >
                  Re-run Filtering
                </button>
              </div>
            </div>
          )}

          {/* AI Resume Filtering Control Panel */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 mb-6 border border-purple-200">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h4 className="text-xl font-semibold text-gray-800 flex items-center">
                  <Sparkles className="w-6 h-6 mr-2 text-purple-600" />
                  AI Resume Filtering Engine
                </h4>
                <p className="text-gray-600 text-sm">Advanced AI analysis to identify the best candidates automatically</p>
                {filterStatus?.status === 'running' && (
                  <div className="mt-2 flex items-center space-x-2">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                    </div>
                    <span className="text-xs text-blue-600">Analyzing resumes...</span>
                  </div>
                )}
              </div>
              {filterStatus && (
                <div className={`px-4 py-2 rounded-full text-sm font-medium border ${getFilteringStatusColor(filterStatus.status)}`}>
                  {filterStatus.status === 'completed' && <CheckCircle className="w-4 h-4 inline mr-1" />}
                  {filterStatus.status === 'running' && <Loader className="w-4 h-4 inline mr-1 animate-spin" />}
                  {filterStatus.status === 'failed' && <AlertCircle className="w-4 h-4 inline mr-1" />}
                  {filterStatus.status === 'ready' && <Clock className="w-4 h-4 inline mr-1" />}
                  Status: {filterStatus.status === 'completed' ? 'FILTERED' : 
                          filterStatus.status === 'running' ? 'FILTERING...' :
                          filterStatus.status === 'failed' ? 'FILTERING FAILED' :
                          filterStatus.status === 'ready' ? 'READY TO FILTER' :
                          filterStatus.status || 'Not started'}
                  {filterStatus.message && (
                    <div className="text-xs mt-1">{filterStatus.message}</div>
                  )}
                  {filterStatus.status === 'completed' && filterStatus.completed_at && (
                    <div className="text-xs mt-1">
                      Completed: {new Date(filterStatus.completed_at).toLocaleString()}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Duplicate Detection Banner */}
            {topResumes?.data?.summary?.duplicate_groups_found > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <div>
                    <h5 className="text-red-800 font-semibold">Duplicate Resume Detected</h5>
                    <p className="text-red-700 text-sm">
                      {topResumes.data.summary.duplicate_groups_found} duplicate group(s) found. 
                      Duplicate candidates have been assigned the same rank for fair evaluation.
                    </p>
                    {topResumes.data.summary.duplicate_banner_message && (
                      <p className="text-red-600 text-xs mt-1">
                        {topResumes.data.summary.duplicate_banner_message}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-white rounded-lg p-4 border shadow-sm">
                <div className="text-2xl font-bold text-blue-600">{applications.length}</div>
                <div className="text-sm text-gray-600">Total Applications</div>
              </div>
              <div className="bg-white rounded-lg p-4 border shadow-sm">
                <div className="text-2xl font-bold text-green-600">{topResumesList.length}</div>
                <div className="text-sm text-gray-600">Top Candidates</div>
              </div>
              <div className="bg-white rounded-lg p-4 border shadow-sm">
                <div className="text-2xl font-bold text-purple-600">
                  {scoreStats ? `${(scoreStats.maxScore * 100).toFixed(1)}%` : '--'}
                </div>
                <div className="text-sm text-gray-600">Best Match</div>
              </div>
              <div className="bg-white rounded-lg p-4 border shadow-sm">
                <div className="text-2xl font-bold text-orange-600">
                  {scoreStats ? `${(scoreStats.avgScore * 100).toFixed(1)}%` : '--'}
                </div>
                <div className="text-sm text-gray-600">Avg Score</div>
              </div>
            </div>
            
            {/* Scoring Criteria Explanation */}
            {topResumesList.length > 0 && (
              <div className="bg-white rounded-lg p-4 border shadow-sm mb-4">
                <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <Brain className="w-4 h-4 mr-2 text-purple-600" />
                  AI Scoring Criteria
                </h5>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-600">Skills Match (40%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-gray-600">Experience (30%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                    <span className="text-gray-600">Location (10%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                    <span className="text-gray-600">Professional Dev (20%)</span>
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Action Buttons */}
            <div className="flex flex-wrap gap-3">
              <button
                onClick={handleStartFiltering}
                disabled={filterStatus?.status === 'running' || applications.length === 0}
                className={`px-6 py-3 rounded-xl font-semibold flex items-center space-x-2 transition-all shadow-md ${filterStatus?.status === 'running'
                    ? 'bg-purple-400 text-white cursor-not-allowed'
                    : applications.length === 0
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : filterStatus?.status === 'completed'
                        ? 'bg-orange-600 hover:bg-orange-700 text-white hover:shadow-lg transform hover:scale-105'
                        : 'bg-purple-600 hover:bg-purple-700 text-white hover:shadow-lg transform hover:scale-105'
                  }`}
              >
                {filterStatus?.status === 'running' ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    <span>AI Analysis Running...</span>
                  </>
                ) : filterStatus?.status === 'completed' ? (
                  <>
                    <RefreshCw className="w-5 h-5" />
                    <span>Re-filter Resumes</span>
                  </>
                ) : (
                  <>
                    <Brain className="w-5 h-5" />
                    <span>Start AI Filtering</span>
                  </>
                )}
              </button>

              <button
                onClick={handleViewTopCandidates}
                className={`px-6 py-3 rounded-xl font-semibold flex items-center space-x-2 transition-all shadow-md ${showTopResumes
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : topResumesList.length > 0
                      ? 'bg-blue-100 hover:bg-blue-200 text-blue-800 hover:shadow-lg transform hover:scale-105'
                      : 'bg-gray-200 text-gray-500'
                  }`}
              >
                <Award className="w-5 h-5" />
                <span>
                  {showTopResumes
                    ? 'Show All Applications'
                    : `View Top Candidates (${topResumesList.length})`
                  }
                </span>
                {topResumesList.length > 0 && !showTopResumes && (
                  <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full ml-1">
                    NEW
                  </span>
                )}
              </button>

              <button
                onClick={() => {
                  fetchJobApplications(selectedJobApplications.ticket_id);
                  fetchFilteringStatus(selectedJobApplications.ticket_id);
                  fetchTopResumes(selectedJobApplications.ticket_id);
                }}
                disabled={loadingApplications}
                className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-xl font-semibold flex items-center space-x-2 transition-colors shadow-md"
              >
                <RefreshCw className={`w-5 h-5 ${loadingApplications ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>

            {/* Bulk Actions Section */}
            {(showTopResumes ? topResumesList : applications).length > 0 && (
              <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-6 border border-red-200 mt-6">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-800 flex items-center">
                      <Users className="w-5 h-5 mr-2 text-red-600" />
                      Bulk Candidate Management
                    </h4>
                    <p className="text-gray-600 text-sm">Select candidates and perform bulk actions</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">
                      {selectedCandidates.size} of {(showTopResumes ? topResumesList : applications).length} selected
                    </span>
                    <button
                      onClick={selectedCandidates.size === (showTopResumes ? topResumesList : applications).length ? deselectAllCandidates : selectAllCandidates}
                      className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md text-sm font-medium transition-colors"
                    >
                      {selectedCandidates.size === (showTopResumes ? topResumesList : applications).length ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>
                </div>

                {/* Bulk Action Buttons */}
                <div className="flex flex-wrap gap-3">
                  {selectedCandidates.size > 0 && (
                    <button
                      onClick={handleBulkRejectSelected}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold flex items-center space-x-2 transition-colors shadow-md"
                    >
                      <X className="w-4 h-4" />
                      <span>Reject Selected ({selectedCandidates.size})</span>
                    </button>
                  )}

                  {selectedCandidates.size < (showTopResumes ? topResumesList : applications).length && (
                    <button
                      onClick={handleBulkRejectUnselected}
                      className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold flex items-center space-x-2 transition-colors shadow-md"
                    >
                      <X className="w-4 h-4" />
                      <span>Reject Unselected ({(showTopResumes ? topResumesList : applications).length - selectedCandidates.size})</span>
                    </button>
                  )}

                  {/* Custom Score Threshold */}
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-600">Reject below score:</span>
                    {!showCustomThreshold ? (
                      <button
                        onClick={() => {
                          setShowCustomThreshold(true);
                          // Focus the input after it appears
                          setTimeout(() => {
                            if (customThresholdInputRef.current) {
                              customThresholdInputRef.current.focus({ preventScroll: true });
                            }
                          }, 50);
                        }}
                        className="px-3 py-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-700 rounded-md text-sm font-medium transition-colors"
                      >
                        Custom %
                      </button>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <input
                          key="custom-threshold-input"
                          ref={customThresholdInputRef}
                          type="text"
                          onChange={handleCustomThresholdChange}
                          onKeyPress={handleCustomThresholdKeyPress}
                          placeholder="Enter %"
                          autoComplete="off"
                          autoFocus={showCustomThreshold}
                          className="w-20 px-2 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                        />
                        <button
                          onClick={handleCustomThresholdSubmit}
                          className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded-md text-sm font-medium transition-colors"
                        >
                          Apply
                        </button>
                        <button
                          onClick={() => {
                            setShowCustomThreshold(false);
                            if (customThresholdInputRef.current) {
                              customThresholdInputRef.current.value = '';
                            }
                          }}
                          className="px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-md text-sm font-medium transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Applications List */}
          {loadingApplications ? (
            <div className="text-center py-12">
              <Loader className="w-8 h-8 animate-spin mx-auto text-blue-600" />
              <p className="text-gray-600 mt-4">Loading applications...</p>
            </div>
          ) : (showTopResumes ? topResumesList : applications).length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h4 className="text-lg font-semibold text-gray-600 mb-2">
                {showTopResumes ? 'No Top Candidates Yet' : 'No Applications Yet'}
              </h4>
              <p className="text-gray-500">
                {showTopResumes
                  ? 'Run AI filtering to identify the best candidates for this position.'
                  : 'Applications will appear here when candidates apply for this position.'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-4" style={{ minHeight: '200px', paddingBottom: '2rem' }}>
                             {(showTopResumes ? topResumesList : applications).map((application, index) => {
                 // Extract scores for display - now show for both top candidates and all applications
                 const getScoreDisplay = (app) => {
                   if (app.scores) {
                     return {
                       overall: app.scores.overall || app.score || 0,
                       skills: app.scores.skills || 0,
                       experience: app.scores.experience || 0,
                       location: app.scores.location || 0,
                       professional_development: app.scores.professional_development || 0
                     };
                   }
                   return null;
                 };

                 const scores = getScoreDisplay(application);
                 const isTopCandidate = showTopResumes && scores;
                 const showDetailedView = showTopResumes || scores; // Show detailed view for both top candidates and applications with scores

                 return (
                   <div key={index} className={`rounded-xl p-6 border hover:shadow-md transition-shadow ${showDetailedView ? 'bg-gradient-to-r from-blue-50 to-green-50 border-blue-200' : 'bg-gray-50 border-gray-200'} ${application.is_duplicate_group ? 'border-red-300 bg-red-50' : ''}`}>
                  {/* Duplicate Warning for Individual Candidates */}
                  {application.is_duplicate_group && (
                    <div className="bg-red-100 border border-red-300 rounded-lg p-3 mb-4">
                      <div className="flex items-center">
                        <AlertCircle className="w-4 h-4 text-red-600 mr-2" />
                        <span className="text-red-800 font-medium text-sm">
                          ⚠️ DUPLICATE RESUME: This candidate has {application.duplicate_count + 1} submission(s)
                        </span>
                      </div>
                      {application.duplicates && application.duplicates.length > 0 && (
                        <p className="text-red-700 text-xs mt-1">
                          Duplicate files: {application.duplicates.join(', ')}
                        </p>
                      )}
                    </div>
                  )}
                  
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <input
                          type="checkbox"
                          checked={selectedCandidates.has(index)}
                          onChange={() => toggleCandidateSelection(index)}
                          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
                        />
                        <UserCheck className="w-5 h-5 text-blue-600" />
                        <h4 className="text-lg font-semibold text-gray-800">
                          {application.applicant_name || application.name || 'Unknown Applicant'}
                        </h4>
                        
                        {/* Final Decision Status */}
                        {console.log('Debug - Application data:', application.applicant_name, 'final_decision:', application.final_decision, 'status:', application.status, 'Raw application object:', application)}
                        {application.final_decision && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            application.final_decision === 'hire' || application.final_decision === 'strong_hire' 
                              ? 'bg-green-100 text-green-800 border border-green-200' :
                            application.final_decision === 'reject' || application.final_decision === 'strong_reject'
                              ? 'bg-red-100 text-red-800 border border-red-200' :
                            application.final_decision === 'maybe'
                              ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                            'bg-gray-100 text-gray-800 border border-gray-200'
                          }`}>
                            {application.final_decision === 'hire' || application.final_decision === 'strong_hire' ? '✓ HIRE' :
                             application.final_decision === 'reject' || application.final_decision === 'strong_reject' ? '✗ REJECT' :
                             application.final_decision === 'maybe' ? '⏸ HOLD' :
                             application.final_decision.toUpperCase()}
                          </span>
                        )}
                        {/* Fallback to status if no final_decision */}
                        {!application.final_decision && application.status && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            application.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            application.status === 'hired' ? 'bg-green-100 text-green-800' :
                            application.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                            application.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {application.status === 'rejected' ? 'REJECTED' :
                             application.status === 'hired' ? 'HIRED' :
                             application.status === 'completed' ? 'COMPLETED' :
                             application.status === 'in_progress' ? 'IN PROGRESS' :
                             application.status.toUpperCase()}
                          </span>
                        )}
                        
                        {/* AI Filtering Status Indicator - Only show if candidate was actually filtered */}
                        {(() => {
                          // Check if this candidate was actually processed during the last filtering
                          const candidateUploadDate = new Date(application.uploaded_at || application.upload_date || application.created_at);
                          const filteringCompletedDate = filterStatus?.completed_at ? new Date(filterStatus.completed_at) : 
                                                       filterStatus?.filtering_info?.filtered_at ? new Date(filterStatus.filtering_info.filtered_at) : null;
                          
                          // Only show "FILTERED" if:
                          // 1. Filtering is completed
                          // 2. Candidate was uploaded before or at the time of filtering
                          const wasFiltered = filterStatus?.status === 'completed' && 
                                            filteringCompletedDate && 
                                            candidateUploadDate <= filteringCompletedDate;
                          
                          // Show "NEW" if candidate was uploaded after filtering
                          const isNewAfterFiltering = filterStatus?.status === 'completed' && 
                                                     filteringCompletedDate && 
                                                     candidateUploadDate > filteringCompletedDate;
                          
                          if (wasFiltered) {
                            return (
                              <span className="px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 bg-green-100 text-green-800 border border-green-200">
                                <CheckCircle className="w-3 h-3" />
                                <span>FILTERED</span>
                              </span>
                            );
                          } else if (isNewAfterFiltering) {
                            return (
                              <span className="px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 bg-orange-100 text-orange-800 border border-orange-200">
                                <Clock className="w-3 h-3" />
                                <span>NEW</span>
                              </span>
                            );
                          } else if (filterStatus?.status === 'running') {
                            return (
                              <span className="px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 bg-blue-100 text-blue-800 border border-blue-200">
                                <Loader className="w-3 h-3 animate-spin" />
                                <span>FILTERING</span>
                              </span>
                            );
                          } else if (filterStatus?.status === 'failed') {
                            return (
                              <span className="px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 bg-red-100 text-red-800 border border-red-200">
                                <AlertCircle className="w-3 h-3" />
                                <span>FILTER FAILED</span>
                              </span>
                            );
                          } else if (filterStatus?.status === 'ready') {
                            return (
                              <span className="px-2 py-1 rounded-full text-xs font-medium flex items-center space-x-1 bg-yellow-100 text-yellow-800 border border-yellow-200">
                                <Clock className="w-3 h-3" />
                                <span>READY</span>
                              </span>
                            );
                          }
                          return null;
                        })()}
                        
                           {showDetailedView && (
                             <span className={`px-2 py-1 rounded-full text-xs font-medium ${application.is_duplicate_group ? 'bg-red-100 text-red-800' : 'bg-purple-100 text-purple-800'}`}>
                               {showTopResumes ? `Rank #${application.rank || application.duplicate_group_rank || index + 1}${application.is_duplicate_group ? ' (DUPLICATE)' : ''}` : `Application #${index + 1}`}
                             </span>
                           )}
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                          {formatDate(application.uploaded_at || application.upload_date || application.created_at)}
                        </span>
                      </div>
                         
                         {/* Score Breakdown for Applications with Scores */}
                         {showDetailedView && scores && (
                           <div className="mt-4 p-4 bg-white rounded-lg border border-gray-200">
                             <h5 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                               <Target className="w-4 h-4 mr-2 text-purple-600" />
                               AI Analysis Results
                             </h5>
                             
                             {/* Overall Score */}
                             <div className="mb-4">
                               <div className="flex justify-between items-center mb-2">
                                 <span className="text-sm font-medium text-gray-600">Overall Match Score</span>
                                 <span className="text-lg font-bold text-purple-600">
                                   {(scores.overall * 100).toFixed(1)}%
                                 </span>
                    </div>
                               <div className="w-full bg-gray-200 rounded-full h-2">
                                 <div 
                                   className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
                                   style={{ width: `${scores.overall * 100}%` }}
                                 ></div>
                  </div>
                      </div>
                             
                             {/* Detailed Scores Grid */}
                             <div className="grid grid-cols-2 gap-3">
                               <div className="bg-blue-50 p-3 rounded-lg">
                                 <div className="flex justify-between items-center mb-1">
                                   <span className="text-xs font-medium text-blue-700">Skills Match</span>
                                   <span className="text-sm font-bold text-blue-800">
                                     {(scores.skills * 100).toFixed(0)}%
                                   </span>
                    </div>
                                 <div className="w-full bg-blue-200 rounded-full h-1.5">
                                   <div 
                                     className="bg-blue-500 h-1.5 rounded-full"
                                     style={{ width: `${scores.skills * 100}%` }}
                                   ></div>
                                 </div>
                               </div>
                               
                               <div className="bg-green-50 p-3 rounded-lg">
                                 <div className="flex justify-between items-center mb-1">
                                   <span className="text-xs font-medium text-green-700">Experience</span>
                                   <span className="text-sm font-bold text-green-800">
                                     {(scores.experience * 100).toFixed(0)}%
                                   </span>
                                 </div>
                                 <div className="w-full bg-green-200 rounded-full h-1.5">
                                   <div 
                                     className="bg-green-500 h-1.5 rounded-full"
                                     style={{ width: `${scores.experience * 100}%` }}
                                   ></div>
                                 </div>
                               </div>
                               
                               <div className="bg-orange-50 p-3 rounded-lg">
                                 <div className="flex justify-between items-center mb-1">
                                   <span className="text-xs font-medium text-orange-700">Location</span>
                                   <span className="text-sm font-bold text-orange-800">
                                     {(scores.location * 100).toFixed(0)}%
                                   </span>
                                 </div>
                                 <div className="w-full bg-orange-200 rounded-full h-1.5">
                                   <div 
                                     className="bg-orange-500 h-1.5 rounded-full"
                                     style={{ width: `${scores.location * 100}%` }}
                                   ></div>
                                 </div>
                               </div>
                               
                               <div className="bg-purple-50 p-3 rounded-lg">
                                 <div className="flex justify-between items-center mb-1">
                                   <span className="text-xs font-medium text-purple-700">Professional Dev</span>
                                   <span className="text-sm font-bold text-purple-800">
                                     {(scores.professional_development * 100).toFixed(0)}%
                                   </span>
                                 </div>
                                 <div className="w-full bg-purple-200 rounded-full h-1.5">
                                   <div 
                                     className="bg-purple-500 h-1.5 rounded-full"
                                     style={{ width: `${scores.professional_development * 100}%` }}
                                   ></div>
                                 </div>
                               </div>
                             </div>
                             
                             {/* Detailed Skill Matches with Similarity Algorithm */}
                             {application.detailed_skill_matches && Object.keys(application.detailed_skill_matches).length > 0 && (
                               <div className="mt-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                                 <div className="flex items-center gap-2 mb-3">
                                   <Brain className="w-4 h-4 text-indigo-600" />
                                   <span className="text-sm font-semibold text-indigo-800">Similarity Algorithm Details</span>
                                 </div>
                                 <div className="space-y-2">
                                   {Object.entries(application.detailed_skill_matches).map(([skill, variations], skillIndex) => (
                                     <div key={skillIndex} className="text-xs">
                                       <span className="font-medium text-indigo-700">{skill}:</span>
                                       <div className="ml-2 mt-1">
                                         {variations.map((variation, varIndex) => (
                                           <span key={varIndex} className="inline-block bg-indigo-100 text-indigo-700 px-2 py-1 rounded mr-1 mb-1 text-xs">
                                             {variation}
                                           </span>
                                         ))}
                                       </div>
                                     </div>
                                   ))}
                                 </div>
                               </div>
                             )}
                             
                             {/* Key Highlights */}
                              {application.key_highlights && application.key_highlights.length > 0 && (
                                <div className="mt-3 pt-3 border-t border-gray-200">
                                  <div className="flex items-center mb-2">
                                    <Award className="w-4 h-4 mr-2 text-yellow-600" />
                                    <span className="text-xs font-medium text-gray-600">Key Highlights</span>
                                  </div>
                                  <div className="space-y-1">
                                    {application.key_highlights.slice(0, 3).map((highlight, idx) => (
                                      <div key={idx} className="flex items-start space-x-2">
                                        <div className="w-1.5 h-1.5 bg-yellow-500 rounded-full mt-2 flex-shrink-0"></div>
                                        <span className="text-xs text-gray-700 leading-relaxed">
                                          {highlight}
                                        </span>
                                      </div>
                                    ))}
                                    {application.key_highlights.length > 3 && (
                                      <div className="text-xs text-gray-500 mt-1">
                                        +{application.key_highlights.length - 3} more highlights
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                             
                             {application.experience_years && (
                               <div className="mt-2 text-xs text-gray-500">
                                 <span className="font-medium">Experience:</span> {application.experience_years} years
                               </div>
                             )}
                           </div>
                         )}
                       </div>
                     </div>
                     
                    <div className="flex space-x-2">
                      <button
                        onClick={() => previewResume(selectedJobApplications.ticket_id, application.filename || application.file_name, application)}
                        disabled={resumeLoading}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-colors text-sm shadow-sm"
                      >
                        {resumeLoading ? (
                          <Loader className="w-4 h-4 animate-spin" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                        <span>Preview</span>
                      </button>
                      <button
                        onClick={() => downloadResume(selectedJobApplications.ticket_id, application.filename || application.file_name)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-colors text-sm shadow-sm"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>
                      
                      {/* Interview Management Buttons */}
                      <button
                        onClick={() => {
                          // Get the raw resume data with ID from jobApplications
                          const rawApplications = jobApplications[selectedJobApplications?.ticket_id] || [];
                          
                          // Find the matching application by applicant_name and applicant_email
                          const matchingApplication = rawApplications.find(app => 
                            app.applicant_name === application.applicant_name && 
                            app.applicant_email === application.applicant_email
                          );
                          
                          if (matchingApplication && matchingApplication.id) {
                            setSelectedCandidateForInterview(matchingApplication);
                          } else {
                            setSelectedCandidateForInterview(application);
                          }
                          
                          setSelectedJobForInterviews(selectedJobApplications);
                          setShowInterviewScheduler(true);
                        }}
                        className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-colors text-sm shadow-sm"
                      >
                        <Calendar className="w-4 h-4" />
                        <span>Schedule Interview</span>
                      </button>
                      
                      <button
                        onClick={async () => {
                          const candidateKey = `${application.applicant_name}-${application.applicant_email}`;
                          console.log('🔍 View Status clicked for:', candidateKey);
                          setViewStatusLoading(prev => ({ ...prev, [candidateKey]: true }));
                          
                          try {
                            // Get the raw resume data with ID from jobApplications for proper ID mapping
                            const rawApplications = jobApplications[selectedJobApplications?.ticket_id] || [];
                            
                            // Find matching application by name and email
                            const matchingApplication = rawApplications.find(app => 
                              app.applicant_name === application.applicant_name && 
                              app.applicant_email === application.applicant_email
                            );
                            
                            // For top candidates view, we need to ensure we have the correct ID
                            let candidateToUse = application;
                            
                            if (showTopResumes) {
                              // In top candidates view, use the matching application from raw data to get correct ID
                              if (matchingApplication) {
                                candidateToUse = matchingApplication;
                              }
                            } else {
                              // In all applications view, use matching application if found
                              candidateToUse = matchingApplication || application;
                            }
                            
                            // Check if candidate has a valid ID
                            if (!candidateToUse.id) {
                              console.error('Candidate does not have a valid ID:', candidateToUse);
                              alert('Error: Candidate data is missing required ID. Please try again.');
                              setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
                              return;
                            }
                            
                            setSelectedCandidateForInterview(candidateToUse);
                            setSelectedJobForInterviews(selectedJobApplications);
                            setShowCandidateStatus(true);
                            console.log('🔍 Modal should be opening now for:', candidateToUse.applicant_name);
                            console.log('🔍 Modal state set to true, selectedCandidate:', candidateToUse);
                            console.log('🔍 selectedJobApplications:', selectedJobApplications);
                            
                            // Fallback: Clear loading state after 5 seconds if modal doesn't open
                            setTimeout(() => {
                              setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
                            }, 5000);
                            
                            // The loading state will be stopped by the modal's onLoadComplete callback
                            
                          } catch (error) {
                            console.error('Error opening candidate status:', error);
                            alert('Error loading candidate status. Please try again.');
                            setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
                          }
                        }}
                        disabled={viewStatusLoading[`${application.applicant_name}-${application.applicant_email}`]}
                        className={`px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-colors text-sm shadow-sm ${
                          viewStatusLoading[`${application.applicant_name}-${application.applicant_email}`]
                            ? 'bg-indigo-400 cursor-not-allowed' 
                            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        }`}
                      >
                        {viewStatusLoading[`${application.applicant_name}-${application.applicant_email}`] ? (
                          <>
                            <Loader className="w-4 h-4 animate-spin" />
                            <span>Loading...</span>
                          </>
                        ) : (
                          <>
                        <MessageSquare className="w-4 h-4" />
                        <span>View Status</span>
                          </>
                        )}
                      </button>
                      
                      <button
                        onClick={() => deleteCandidate(selectedJobApplications.ticket_id, application)}
                        className="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg font-medium flex items-center space-x-1 transition-colors text-sm shadow-sm"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                 );
               })}
            </div>
          )}
          </div>
        </div>
      </div>
    );
  };

  // MAIN RENDER
  
  // Emergency dashboard state check - run on every render
  if (showHRDashboard && !selectedJobApplications) {
    console.log('🚨 EMERGENCY: Dashboard open without job - forcing close');
    // Use setTimeout to avoid state update during render
    setTimeout(() => forceResetDashboard(), 0);
  }
  
  return (
    <div className="space-y-8 p-6 bg-gray-50 min-h-screen">
      {/* Debug: User Role Display */}
      {/* <div className="fixed top-4 right-4 z-50 bg-yellow-400 text-black px-3 py-1 rounded-lg text-sm font-bold">
        Current UserRole: {userRole}
      </div> */}
      
      {/* Debug: Job Selection Status */}
      {/* <div className="fixed top-4 left-4 z-50 bg-blue-400 text-white px-3 py-1 rounded-lg text-sm font-bold">
        Selected Job: {selectedJob ? 'YES' : 'NO'}
      </div> */}
      
      {/* Debug: Current View Status */}
      {/* <div className="fixed top-12 left-4 z-50 bg-green-400 text-white px-3 py-1 rounded-lg text-sm font-bold">
        Current View: {showTopResumes ? 'Top Candidates' : 'All Applications'}
      </div> */}
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            HR Dashboard
          </h1>
        </div>
        <div className="flex space-x-3 items-end">
          <div className="relative">
            <input
              type="text"
              placeholder="Search jobs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-3 w-96 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-3 rounded-xl font-medium flex items-center space-x-2 transition-colors disabled:opacity-50 shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          {userRole === 'hr' && (
            <button
              onClick={() => setShowJobForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold flex items-center space-x-2 transition-colors shadow-md whitespace-nowrap min-w-fit"
            >
              <Plus className="w-5 h-5" />
              <span>Post Job</span>
            </button>
          )}
        </div>
      </div>

      {/* Filter Section */}
      <div className="mb-6">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
        >
          <Filter className="w-4 h-4" />
          <span className="font-medium">Filters</span>
          {(selectedLocation || selectedEmploymentType || selectedStatus) && (
            <span className="ml-2 px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
              {[selectedLocation, selectedEmploymentType, selectedStatus].filter(Boolean).length}
            </span>
          )}
        </button>

        {showFilters && (
          <div className="mt-4 p-6 bg-white border border-gray-200 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Location Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                <select
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Locations</option>
                  {(() => {
                    const uniqueLocations = new Set();
                    apiJobs.forEach(job => {
                      if (job.location) {
                        uniqueLocations.add(job.location.trim().toLowerCase());
                      }
                    });
                    return Array.from(uniqueLocations).sort().map((location) => {
                      // Capitalize first letter for display
                      const displayLocation = location.charAt(0).toUpperCase() + location.slice(1);
                      return (
                        <option key={location} value={location}>{displayLocation}</option>
                      );
                    });
                  })()}
                </select>
              </div>

              {/* Employment Type Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Employment Type</label>
                <select
                  value={selectedEmploymentType}
                  onChange={(e) => setSelectedEmploymentType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  {(() => {
                    // Collect all employment types and log them
                    const allTypes = apiJobs.map(job => job.employment_type).filter(Boolean);
                    console.log('All employment types before dedup:', allTypes);
                    
                    const uniqueTypes = new Set();
                    apiJobs.forEach(job => {
                      if (job.employment_type) {
                        const normalized = job.employment_type.trim().toLowerCase().replace(/\s+/g, '-');
                        uniqueTypes.add(normalized);
                      }
                    });
                    
                    const finalTypes = Array.from(uniqueTypes).sort();
                    console.log('Unique employment types after dedup:', finalTypes);
                    
                    return finalTypes.map((type) => {
                      // Capitalize first letter of each word for display
                      const displayType = type.split('-').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                      ).join('-');
                      return (
                        <option key={type} value={type}>{displayType}</option>
                      );
                    });
                  })()}
                </select>
              </div>

              {/* Status Filter (HR Only) */}
              {userRole === 'hr' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">All Status</option>
                    <option value="live">🟢 Live</option>
                    <option value="stopped">🔴 Stopped</option>
                  </select>
                </div>
              )}
            </div>

            {/* Clear Filters Button */}
            {(selectedLocation || selectedEmploymentType || selectedStatus) && (
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => {
                    setSelectedLocation('');
                    setSelectedEmploymentType('');
                    setSelectedStatus('');
                  }}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  Clear All Filters
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* HR Dashboard Debug and Reset Section - REMOVED FOR PRODUCTION */}

      {/* Health Status Dashboard - REMOVED FOR PRODUCTION */}

                      {/* Real Data Fetch Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-red-800">Real Data Fetch Error</h3>
              <p className="text-red-700">Dashboard initialization failed: Cannot connect to backend API. Please check if the server is running.</p>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleRefresh}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Connection</span>
            </button>
            <button
              onClick={() => {
                const testUrl = `${API_CONFIG.BASE_URL}/api/health`;
                window.open(testUrl, '_blank');
              }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors"
            >
              <Wifi className="w-4 h-4" />
              <span>Test API</span>
            </button>
          </div>
        </div>
      )}


      {/* Jobs Grid */}
      {activeTab === 'jobs' && !loading && (
        <div className="space-y-6">
          {/* Results Count */}
          <div className="flex items-center justify-between px-2">
            <p className="text-sm text-gray-600">
              Showing <span className="font-semibold text-gray-900">{filteredJobs.length}</span> of {apiJobs.length} jobs
            </p>
            {filteredJobs.length !== apiJobs.length && (
              <p className="text-xs text-blue-600">Filters applied</p>
            )}
          </div>

          {filteredJobs.length > 0 ? (
            <>
              {filteredJobs.map((job) => (
                <div key={job.ticket_id} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-2xl font-bold text-gray-800 hover:text-blue-600 transition-colors">
                          {job.job_title || 'Unknown Position'}
                        </h3>
                        <Star className="w-5 h-5 text-yellow-400" />
                        {userRole === 'hr' && (
                          <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-xs font-medium flex items-center border border-purple-300">
                            <Brain className="w-3 h-3 mr-1" />
                            AI ENHANCED
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Clock className="w-4 h-4" />
                          <span>{getDaysAgo(job.created_at) || 'Recently posted'}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-4 h-4" />
                          <span>Deadline: {job.deadline || 'Not specified'}</span>
                        </div>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium border ${
                      job.is_visible !== false 
                        ? 'bg-green-100 text-green-800 border-green-300' 
                        : 'bg-orange-100 text-orange-800 border-orange-300'
                    }`}>
                      {job.is_visible !== false ? '🟢 LIVE' : '🔴 STOPPED'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-xl border border-blue-100">
                      <MapPin className="w-5 h-5 text-blue-600" />
                      <span className="font-medium text-gray-700">{job.location || 'Remote'}</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-xl border border-green-100">
                      <span className="font-medium text-gray-700">{job.salary_range || 'Competitive'}</span>
                    </div>
                    <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-xl border border-purple-100">
                      <Briefcase className="w-5 h-5 text-purple-600" />
                      <span className="font-medium text-gray-700">{job.employment_type || 'Full-time'}</span>
                    </div>
                  </div>

                  {job.experience_required && (
                    <div className="mb-4 p-3 bg-yellow-50 rounded-xl border border-yellow-100">
                      <span className="text-yellow-800 font-medium">Experience: {job.experience_required}</span>
                    </div>
                  )}

                  {job.required_skills && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-xl border border-gray-200">
                      <span className="text-gray-700"><strong>Skills:</strong> {job.required_skills}</span>
                    </div>
                  )}

                  <div className="flex justify-between items-center">
                    <div className="text-sm text-gray-500">
                      Job ID: {job.ticket_id}
                    </div>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => setSelectedJob(job)}
                        className="bg-gray-100 hover:bg-gray-200 text-gray-800 px-4 py-2 rounded-xl font-medium flex items-center space-x-2 transition-colors shadow-sm"
                      >
                        <Eye className="w-4 h-4" />
                        <span>View Details</span>
                      </button>
                      {userRole === 'hr' && (
                        <>
                          <button
                            onClick={() => toggleJobVisibility(job.ticket_id)}
                            disabled={togglingJobs.has(job.ticket_id)}
                            className={`px-4 py-2 rounded-xl font-medium flex items-center space-x-2 transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed ${
                              job.is_visible !== false 
                                ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-red-500 hover:to-red-600 text-white' 
                                : 'bg-gradient-to-r from-green-500 to-emerald-500 hover:from-emerald-500 hover:to-teal-500 text-white'
                            }`}
                            title={job.is_visible !== false ? 'Stop job posting - Hide from career portal' : 'Start job posting - Show on career portal'}
                          >
                            {togglingJobs.has(job.ticket_id) ? (
                              <>
                                <Loader className="w-4 h-4 animate-spin" />
                                <span>...</span>
                              </>
                            ) : job.is_visible !== false ? (
                              <>
                                <X className="w-4 h-4 animate-pulse" />
                                <span>Stop</span>
                              </>
                            ) : (
                              <>
                                <CheckCircle className="w-4 h-4 animate-bounce" />
                                <span>Start</span>
                              </>
                            )}
                          </button>
                          <button
                            onClick={() => handleEditJob(job)}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-medium flex items-center space-x-2 transition-colors shadow-sm"
                          >
                            <Edit className="w-4 h-4" />
                            <span>Modify</span>
                          </button>
                          <button
                            onClick={() => handleDeleteJob(job)}
                            disabled={deletingJob && jobToDelete?.ticket_id === job.ticket_id}
                            className="bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white px-4 py-2 rounded-xl font-medium flex items-center space-x-2 transition-colors shadow-sm"
                          >
                            <Trash2 className="w-4 h-4" />
                            <span>{deletingJob && jobToDelete?.ticket_id === job.ticket_id ? 'Deleting...' : 'Delete'}</span>
                          </button>
                        </>
                      )}
                      {userRole === 'hr' ? (
                        <button
                          onClick={() => {
                            console.log('👆 User clicked AI HR Dashboard button for job:', job.ticket_id);
                            handleViewApplications(job);
                          }}
                          className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-6 py-2 rounded-xl font-medium flex items-center space-x-2 transition-colors shadow-md"
                        >
                          <Brain className="w-4 h-4" />
                          <span>AI HR Dashboard</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleApplyToJob(job.ticket_id)}
                          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-medium transition-colors shadow-md"
                        >
                          Apply Now
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">
                {userRole === 'hr' ? '🤖' : '💼'}
              </div>
              <h3 className="text-xl font-semibold text-gray-600 mb-2">
                {searchQuery ? 'No jobs match your search' : 'No jobs available'}
              </h3>
              <p className="text-gray-500">
                {searchQuery
                  ? 'Try adjusting your search terms or browse all available positions.'
                  : 'Jobs will appear here when your API is connected.'}
              </p>
              {!loading && (
                <button
                  onClick={handleRefresh}
                  className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-medium shadow-md"
                >
                  Refresh Platform
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-20">
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
            </div>
            <div className="space-y-1">
              <h3 className="text-xl font-semibold text-gray-900">Loading Jobs</h3>
              <p className="text-sm text-gray-500">Please wait...</p>
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      {showHRDashboard && selectedJobApplications && isAuthenticated && (user?.role === 'hr' || userRole === 'hr') && (
        <div>
          {console.log('🎯 Rendering HR Dashboard with:', { showHRDashboard, selectedJobApplications: selectedJobApplications?.ticket_id, userRole, isAuthenticated })}
          <EnhancedHRDashboard />
        </div>
      )}

      {/* Resume Viewer Modal */}
      {showResumeViewer && currentResume && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
          <div className="bg-white rounded-2xl w-full max-w-6xl m-4 max-h-[90vh] overflow-hidden shadow-2xl">
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <div>
                <h3 className="text-xl font-bold text-gray-800">
                  Resume Preview
                </h3>
                <p className="text-sm text-gray-600">
                  {currentResume.applicant?.applicant_name || currentResume.filename}
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => downloadResume(selectedJobApplications?.ticket_id, currentResume.filename)}
                  className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
                <button
                  onClick={() => {
                    setShowResumeViewer(false);
                    setCurrentResume(null);
                    if (currentResume.url) {
                      window.URL.revokeObjectURL(currentResume.url);
                    }
                  }}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            {/* Resume Content */}
            <div className="flex-1 overflow-auto p-6">
              {resumeLoading ? (
                <div className="flex items-center justify-center h-64">
                  <Loader className="w-8 h-8 animate-spin text-blue-600" />
                  <span className="ml-3 text-gray-600">Loading resume...</span>
                </div>
              ) : currentResume.type?.includes('pdf') ? (
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
                    This file type cannot be previewed. Please download the file to view it.
                  </p>
                  <button
                    onClick={() => downloadResume(selectedJobApplications?.ticket_id, currentResume.filename)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                  >
                    Download Resume
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}


      {/* Job Details Modal */}
      
           {selectedJob && (
  <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
    <div 
      className="rounded-2xl w-full max-w-6xl m-4 max-h-[95vh] overflow-hidden"
      style={{
        background: '#ffffff',
        backgroundImage: `
          radial-gradient(circle at top left, rgba(255, 255, 255, 1) 0%, rgba(251, 252, 253, 0.4) 50%),
          radial-gradient(circle at bottom right, rgba(248, 250, 252, 0.5) 0%, rgba(255, 255, 255, 0) 50%)
        `,
        boxShadow: `
          20px 20px 60px #d9d9d9,
          -20px -20px 60px #ffffff,
          inset 0 0 0 1px rgba(255, 255, 255, 0.1)
        `
      }}
    >
            {/* Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200 relative">
              <div>
                <h3 className="text-2xl font-bold text-gray-800">
                  {selectedJob.job_title || selectedJob.title}
                </h3>
                <p className="text-sm text-gray-600">
                  Job ID: {selectedJob.ticket_id}
                </p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            {/* Job Content */}
            <div className="flex-1 overflow-y-auto p-6" style={{ maxHeight: 'calc(95vh - 120px)' }}>
              <div className="space-y-6">
                {/* Job Status */}
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-secondary-500">
                    Posted {selectedJob.created_at ? new Date(selectedJob.created_at).toLocaleDateString() : 'Unknown'}
                  </span>
                </div>

                {/* Job Details Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Information */}
                  <div className="card p-6">
                    <h4 className="text-lg font-display font-semibold text-secondary-900 border-b border-surface-200 pb-3 mb-4">
                      Job Information
                    </h4>
                    
                    <div className="space-y-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center">
                          <MapPin className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <span className="text-sm font-medium text-secondary-600">Location</span>
                          <p className="text-secondary-900 font-medium">{selectedJob.location || 'Not specified'}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-success-50 rounded-xl flex items-center justify-center">
                        </div>
                        <div>
                          <span className="text-sm font-medium text-secondary-600">Salary Range</span>
                          <p className="text-secondary-900 font-medium">{selectedJob.salary_range || 'Not specified'}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-warning-50 rounded-xl flex items-center justify-center">
                          <Clock className="w-5 h-5 text-warning-600" />
                        </div>
                        <div>
                          <span className="text-sm font-medium text-secondary-600">Employment Type</span>
                          <p className="text-secondary-900 font-medium">{selectedJob.employment_type || 'Not specified'}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center">
                          <Calendar className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <span className="text-sm font-medium text-secondary-600">Application Deadline</span>
                          <p className="text-secondary-900 font-medium">{selectedJob.deadline || 'Not specified'}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-secondary-50 rounded-xl flex items-center justify-center">
                          <User className="w-5 h-5 text-secondary-600" />
                        </div>
                        <div>
                          <span className="text-sm font-medium text-secondary-600">Experience Required</span>
                          <p className="text-secondary-900 font-medium">{selectedJob.experience_required || 'Not specified'}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Additional Information */}
                  <div className="card p-6">
                    <h4 className="text-lg font-display font-semibold text-secondary-900 border-b border-surface-200 pb-3 mb-4">
                      Additional Details
                    </h4>
                    
                    <div className="space-y-4">
                      <div>
                        <span className="text-sm font-medium text-secondary-600">Required Skills</span>
                        <div className="mt-2">
                          {selectedJob.required_skills ? (
                            <div className="flex flex-wrap gap-2">
                              {selectedJob.required_skills.split(',').map((skill, index) => (
                                <span key={index} className="badge badge-info">
                                  {skill.trim()}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <p className="text-secondary-500 text-sm">Not specified</p>
                          )}
                        </div>
                      </div>
                      
                      <div>
                        <span className="text-sm font-medium text-secondary-600">Job Description</span>
                        <p className="text-secondary-900 mt-2 text-sm leading-relaxed">
                          {selectedJob.job_description || 'No description provided'}
                        </p>
                      </div>
                      
                    </div>
                  </div>
                </div>

                {/* Debug: Action buttons section */}
                {/* <div className="text-xs text-orange-500 bg-orange-100 px-2 py-1 rounded">
                  Action Buttons Section - About to render
                </div> */}
                
                {/* Scroll indicator */}
                {/* <div className="text-xs text-red-500 bg-red-100 px-2 py-1 rounded text-center">
                  ⬇️ SCROLL DOWN TO SEE ACTION BUTTONS ⬇️
                  <br />
                  <span className="text-xs">(Use mouse wheel, arrow keys, or Page Down)</span>
                </div> */}

                {/* Action Buttons */}
                <div className="flex space-x-3 pt-6 border-t border-surface-200">
                  {userRole === 'hr' ? (
                    <>
                      <button
                        onClick={() => {
                          
                          
                          
                          setSelectedJob(null);
                          setSelectedJobForInterviews(selectedJob);
                          setShowInterviewManager(true);
                          
                        }}
                        className="btn btn-success"
                      >
                        <Calendar className="w-5 h-5" />
                        <span>Manage Interviews</span>
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => {
                        setSelectedJob(null);
                        handleApplyToJob(selectedJob.ticket_id);
                      }}
                      className="btn btn-primary"
                    >
                      Apply Now
                    </button>
                  )}
                  
                  <button
                    onClick={() => setSelectedJob(null)}
                    className="btn btn-secondary"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interview Management Modal */}
      {showInterviewRounds && selectedJobForInterviews && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
          <div className="bg-white rounded-2xl w-full max-w-6xl m-4 max-h-[90vh] overflow-hidden shadow-2xl">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <div>
                <h3 className="text-2xl font-bold text-gray-800">Interview Rounds Setup</h3>
                <p className="text-sm text-gray-600">
                  {selectedJobForInterviews.job_title || selectedJobForInterviews.title}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowInterviewRounds(false);
                  setSelectedJobForInterviews(null);
                }}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-6">
              <InterviewRoundsManager 
                ticketId={selectedJobForInterviews.ticket_id}
                onRoundsCreated={(rounds) => {
                  
                  setShowInterviewRounds(false);
                  setSelectedJobForInterviews(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Interview Scheduler Modal */}
      
      {showInterviewScheduler && selectedCandidateForInterview && selectedJobForInterviews && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
          <div className="bg-white rounded-2xl w-full max-w-6xl max-h-[95vh] overflow-hidden shadow-2xl flex flex-col modal-enter m-4">
            {/* Modal Header - Fixed */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200 bg-white flex-shrink-0">
              <div>
                <h3 className="text-2xl font-bold text-gray-800">Schedule Interview</h3>
                <p className="text-sm text-gray-600">
                  {selectedJobForInterviews.job_title || selectedJobForInterviews.title}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowInterviewScheduler(false);
                  setSelectedCandidateForInterview(null);
                  setSelectedJobForInterviews(null);
                }}
                className="text-gray-400 hover:text-gray-600 text-2xl transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            {/* Scrollable Content Area */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50 modal-scroll">
              <div className="bg-white rounded-lg shadow-sm modal-content-enter">
                
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
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Debug Modal - Show when conditions are not met */}
      {showInterviewScheduler && (!selectedCandidateForInterview || !selectedJobForInterviews) && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
          <div className="bg-white rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h3 className="text-xl font-bold text-red-600 mb-4">Debug: Modal Conditions Not Met</h3>
            <div className="space-y-2 text-sm">
              <p><strong>showInterviewScheduler:</strong> {showInterviewScheduler ? 'true' : 'false'}</p>
              <p><strong>selectedCandidateForInterview:</strong> {selectedCandidateForInterview ? 'exists' : 'null/undefined'}</p>
              <p><strong>selectedJobForInterviews:</strong> {selectedJobForInterviews ? 'exists' : 'null/undefined'}</p>
              {selectedCandidateForInterview && (
                <div className="mt-4 p-3 bg-gray-100 rounded">
                  <p><strong>Candidate ID:</strong> {selectedCandidateForInterview.id}</p>
                  <p><strong>Candidate Name:</strong> {selectedCandidateForInterview.applicant_name}</p>
                  <p><strong>Candidate Keys:</strong> {Object.keys(selectedCandidateForInterview).join(', ')}</p>
                </div>
              )}
              {selectedJobForInterviews && (
                <div className="mt-4 p-3 bg-gray-100 rounded">
                  <p><strong>Job Ticket ID:</strong> {selectedJobForInterviews.ticket_id}</p>
                  <p><strong>Job Title:</strong> {selectedJobForInterviews.job_title}</p>
                  <p><strong>Job Keys:</strong> {Object.keys(selectedJobForInterviews).join(', ')}</p>
                </div>
              )}
            </div>
            <button
              onClick={() => {
                setShowInterviewScheduler(false);
                setSelectedCandidateForInterview(null);
                setSelectedJobForInterviews(null);
              }}
              className="mt-4 w-full bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg"
            >
              Close Debug Modal
            </button>
          </div>
        </div>
      )}

      {/* Interview Feedback Modal */}
      {showInterviewFeedback && selectedCandidateForInterview && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
          <div className="bg-white rounded-2xl w-full max-w-6xl m-4 max-h-[90vh] overflow-hidden shadow-2xl">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <div>
                <h3 className="text-2xl font-bold text-gray-800">Interview Feedback</h3>
                <p className="text-sm text-gray-600">
                  Submit feedback for {selectedCandidateForInterview.applicant_name}
                </p>
              </div>
              <button
                onClick={() => {
                  setShowInterviewFeedback(false);
                  setSelectedCandidateForInterview(null);
                }}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-6">
              <InterviewFeedback 
                interviewId={selectedCandidateForInterview.interview_id}
                interviewerId={1} // This should come from auth context
                onFeedbackSubmitted={() => {
                  
                  setShowInterviewFeedback(false);
                  setSelectedCandidateForInterview(null);
                }}
              />
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
                  const candidateKey = `${selectedCandidateForInterview.applicant_name || selectedCandidateForInterview.candidateName}-${selectedCandidateForInterview.applicant_email || selectedCandidateForInterview.email}`;
                  console.log('🔍 onLoadComplete called for:', candidateKey);
                  setViewStatusLoading(prev => ({ ...prev, [candidateKey]: false }));
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Interview Manager Modal */}

      {showInterviewManager && selectedJobForInterviews && (
        <InterviewManager
          ticketId={selectedJobForInterviews.ticket_id}
          jobTitle={selectedJobForInterviews.job_title || selectedJobForInterviews.title}
          onClose={() => {
            
            setShowInterviewManager(false);
            setSelectedJobForInterviews(null);
          }}
          onInterviewScheduled={(interviewId) => {
            
            setShowInterviewManager(false);
            setSelectedJobForInterviews(null);
          }}
        />
      )}

      {/* Job Creation Form Modal */}
      <ModalPortal isOpen={showJobForm}>
        <div 
          className="fixed z-[999999]" 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'transparent',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
            overflowY: 'hidden',
            zIndex: 999999
          }}
        >
          <div 
            className="bg-white rounded-2xl flex flex-col shadow-2xl job-creation-modal"
            style={{
              width: '100%',
              maxWidth: '1024px',
              height: 'auto',
              maxHeight: '80vh',
              marginTop: 0
            }}
          >
            {/* Header - Fixed */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200 flex-shrink-0">
              <div>
                <h3 className="text-2xl font-bold text-gray-800 flex items-center">
                  <Plus className="w-6 h-6 mr-2 text-blue-600" />
                  Create New Job Posting
                </h3>
                <p className="text-sm text-gray-600">Fill in the job details below to create a new job posting</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowJobForm(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            {/* Content - Full Height */}
            <div className="job-creation-content flex-1 overflow-y-auto">
              <JobCreationForm onJobCreated={() => {
                setShowJobForm(false);
                handleRefresh(); // Refresh the job list
              }} />
            </div>
          </div>
        </div>
      </ModalPortal>

      {/* Job Edit Form Modal */}
      <ModalPortal isOpen={showEditJobForm}>
        <div 
          className="fixed z-[999999]"
          style={{
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'transparent',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px'
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowEditJobForm(false);
              setEditingJob(null);
            }
          }}
        >
          <div 
            className="bg-white rounded-2xl flex flex-col shadow-2xl job-creation-modal"
            style={{
              width: '100%',
              maxWidth: '1024px',
              height: 'auto',
              maxHeight: '80vh',
              marginTop: 0
            }}
          >
            {/* Header - Fixed */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200 flex-shrink-0">
              <div>
                <h3 className="text-2xl font-bold text-gray-800 flex items-center">
                  <Edit className="w-6 h-6 mr-2 text-blue-600" />
                  Edit Job Posting
                </h3>
                <p className="text-sm text-gray-600">Modify the job details below</p>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => {
                    setShowEditJobForm(false);
                    setEditingJob(null);
                  }}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            {/* Content - Full Height */}
            <div className="job-creation-content flex-1 overflow-y-auto">
              <JobCreationForm 
                editingJob={editingJob}
                onJobCreated={() => {
                  setShowEditJobForm(false);
                  setEditingJob(null);
                  handleRefresh(); // Refresh the job list
                }} 
              />
            </div>
          </div>
        </div>
      </ModalPortal>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[10000]">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl">
            <h3 className="text-xl font-bold text-gray-800 mb-4">{confirmDialog.title}</h3>
            <p className="text-gray-600 mb-6 whitespace-pre-line">{confirmDialog.message}</p>
            <div className="flex space-x-3">
              <button
                onClick={confirmDialog.onConfirm}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-semibold transition-colors shadow-md"
              >
                Confirm
              </button>
              <button
                onClick={confirmDialog.onCancel}
                className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-xl font-semibold transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Rejection Progress Modal */}
      {bulkRejectionProgress && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[9999]">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Loader className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Processing Bulk Rejection
              </h3>
              <p className="text-gray-600 mb-4">
                Sending rejection emails to candidates...
              </p>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${(bulkRejectionProgress.completed / bulkRejectionProgress.total) * 100}%` }}
                ></div>
              </div>
              
              {/* Progress Text */}
              <div className="text-sm text-gray-600 mb-2">
                {bulkRejectionProgress.completed} of {bulkRejectionProgress.total} completed
              </div>
              
              {bulkRejectionProgress.current && (
                <div className="text-xs text-gray-500">
                  Currently processing: {bulkRejectionProgress.current}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Bulk Rejection Results Modal */}
      {bulkRejectionResults && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-[9999]">
          <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4 shadow-2xl">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Bulk Rejection Complete
              </h3>
              
              {/* Results Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{bulkRejectionResults.successful.length}</div>
                    <div className="text-gray-600">Successful</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600">{bulkRejectionResults.failed.length}</div>
                    <div className="text-gray-600">Failed</div>
                  </div>
                </div>
              </div>
              
              {/* Failed Candidates Details */}
              {bulkRejectionResults.failed.length > 0 && (
                <div className="text-left mb-4">
                  <h4 className="font-semibold text-red-600 mb-2">Failed Rejections:</h4>
                  <div className="max-h-32 overflow-y-auto bg-red-50 rounded p-2">
                    {bulkRejectionResults.failed.map((candidate, index) => (
                      <div key={index} className="text-xs text-red-700 mb-1">
                        • {candidate.data.applicant_name || candidate.data.name || `Candidate ${candidate.index + 1}`}: {candidate.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <button
                onClick={() => setBulkRejectionResults(null)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-semibold transition-colors shadow-md"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerPortal;
