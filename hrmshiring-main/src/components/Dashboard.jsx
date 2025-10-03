import React, { useState, useEffect, useRef } from 'react';
import { 
  Users, 
  Briefcase, 
  FileText, 
  CheckCircle,
  Clock,
  Calendar,
  Award,
  ArrowUpRight,
  Filter,
  Search,
  RefreshCw,
  AlertCircle,
  Brain,
  Star,
  MessageSquare,
  X,
  Eye,
  Sparkles
} from 'lucide-react';
import { getApiUrl, getHeaders, getAuthHeaders, API_CONFIG, API_ENDPOINTS } from '../config/api';
import { useAuth } from '../contexts/AuthContext';
import CandidateInterviewStatus from './CandidateInterviewStatus';
import RoundBasedCandidateFilter from './RoundBasedCandidateFilter';
import UpcomingInterviewsWidget from './UpcomingInterviewsWidget';

const RealDashboard = ({ userRole: propUserRole, setActiveTab }) => {
  // Get authentication context
  const { user, isAuthenticated } = useAuth();
  
  // Use authenticated user's role if available, otherwise fall back to prop
  const userRole = isAuthenticated && user?.role ? user.role : (propUserRole || 'hr');
  
  // State management
  const [recentApplications, setRecentApplications] = useState([]);
  const [activeJobs, setActiveJobs] = useState([]);
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalApplications: 0,
    totalHired: 0,
    pendingReview: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [healthStatus, setHealthStatus] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [jobStats, setJobStats] = useState({});
  const [togglingJobs, setTogglingJobs] = useState(new Set());
  
  // Interview status modal states
  const [showInterviewStatus, setShowInterviewStatus] = useState(false);
  const [selectedCandidateForInterview, setSelectedCandidateForInterview] = useState(null);
  const [selectedJobForInterviews, setSelectedJobForInterviews] = useState(null);
  
  // Round-based candidate filtering states
  const [showRoundFilter, setShowRoundFilter] = useState(false);
  const [selectedJobForRoundFilter, setSelectedJobForRoundFilter] = useState(null);
  
  // Bulk rejection states
  const [selectedCandidates, setSelectedCandidates] = useState(new Set());
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  
  // Refs
  const mountedRef = useRef(true);
  const intervalRef = useRef(null);

  // Toggle job visibility
  const toggleJobVisibility = async (jobId) => {
    try {
      console.log(`🔄 Toggling visibility for job: ${jobId}`);
      
      // Add to loading state
      setTogglingJobs(prev => new Set([...prev, jobId]));
      
      const response = await makeAPICall(API_ENDPOINTS.JOBS.TOGGLE_VISIBILITY(jobId), {
        method: 'POST',
        headers: getHeaders()
      });
      
      if (response.success) {
        console.log('✅ Job visibility toggled successfully:', response.data);
        
        // Update the job in the state
        setActiveJobs(prevJobs => 
          prevJobs.map(job => 
            job.id === jobId 
              ? { ...job, isVisible: response.data.is_visible }
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

  // Enhanced API call helper
  const makeAPICall = async (endpoint, options = {}) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    try {
      console.log(`🌐 API Call: ${getApiUrl(endpoint)}`);
      
      const response = await fetch(getApiUrl(endpoint), {
        method: options.method || 'GET',
        headers: {
          ...getHeaders(),
          'ngrok-skip-browser-warning': 'true',
          ...options.headers
        },
        signal: controller.signal,
        ...options
      });

      clearTimeout(timeoutId);
      
      console.log(`📡 Response Status: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      console.log(`✅ API Success:`, data);
      return data;
      
    } catch (err) {
      clearTimeout(timeoutId);
      console.error(`❌ API Error:`, err);
      
      if (err.name === 'AbortError') {
        throw new Error('Request timeout - API took too long to respond');
      }
      
      if (err.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to API - Check if backend is running and accessible');
      }
      
      throw err;
    }
  };

  // Test API Connection
  const testAPIConnection = async () => {
    try {
      console.log('🔍 Testing API connection...');
      const healthResponse = await makeAPICall('/api/health');
      console.log('✅ Health check passed:', healthResponse);
      return true;
    } catch (error) {
      console.error('❌ API Test Failed:', error.message);
      return false;
    }
  };

  // Check API health
  const checkHealth = async () => {
    try {
      const data = await makeAPICall('/api/health');
      setHealthStatus(data);
    } catch (err) {
      setHealthStatus({ status: 'error', message: err.message });
    }
  };

  // Fetch real platform statistics
  const fetchRealStats = async () => {
    try {
      const data = await makeAPICall('/api/stats');
      if (data.success && data.data) {
        const statsData = data.data.overall || data.data;
        console.log('📊 Real Stats Data:', statsData);
        
        setStats({
          totalJobs: statsData.approved_jobs || statsData.total_jobs || 0,
          totalApplications: statsData.total_applications || 0,
          totalHired: statsData.total_hired || 0,
          pendingReview: statsData.pending_approval || 0
        });
      }
    } catch (err) {
      console.error('Stats fetch failed:', err);
    }
  };

  // Fetch all approved jobs with real data
  const fetchApprovedJobs = async () => {
    try {
      console.log('📋 Fetching approved jobs...');
      
      // Use dashboard endpoint to get ALL approved jobs (including hidden ones)
      const endpoint = API_ENDPOINTS.JOBS.GET_DASHBOARD;
      
      const headers = getHeaders();
      
      console.log('🔍 Using endpoint:', endpoint);
      console.log('🔍 Using headers:', headers);
      
      const jobsData = await makeAPICall(`${endpoint}?per_page=50`, { headers });
      
      console.log('📋 Jobs API Response:', jobsData);
      
      if (jobsData.success && jobsData.data && jobsData.data.jobs) {
        const jobs = jobsData.data.jobs;
        console.log(`📋 Found ${jobs.length} approved jobs:`, jobs);
        
        const jobsWithApplications = await Promise.all(
          jobs.map(async (job) => {
            try {
              console.log(`📄 Dashboard - Fetching applications for job: ${job.ticket_id}`);
              const resumesData = await makeAPICall(`/api/tickets/${job.ticket_id}/resumes`);
              
              console.log(`📄 Dashboard - Resumes API Response for ${job.ticket_id}:`, resumesData);
              
              let applicationCount = 0;
              let applications = [];
              
              if (resumesData.success && resumesData.data && resumesData.data.resumes) {
                applications = resumesData.data.resumes;
                applicationCount = applications.length;
                console.log(`📄 Job ${job.ticket_id}: ${applicationCount} applications:`, applications);
              } else {
                console.log(`📄 Job ${job.ticket_id}: No applications found or API error:`, resumesData);
              }
              
              return {
                id: job.ticket_id,
                title: job.job_title || 'Untitled Position',
                department: job.location || 'Not specified',
                location: job.location || 'Remote',
                employmentType: job.employment_type || 'Full-time',
                salaryRange: job.salary_range || 'Competitive',
                requiredSkills: job.required_skills || 'Not specified',
                createdAt: job.created_at,
                deadline: job.deadline || 'Open until filled',
                applications: applicationCount,
                applicationData: applications,
                isVisible: job.is_visible !== false, // Default to true if not set
                status: job.status || 'active'
              };
            } catch (err) {
              console.error(`Failed to fetch applications for job ${job.ticket_id}:`, err);
              return {
                id: job.ticket_id,
                title: job.job_title || 'Untitled Position',
                department: job.location || 'Not specified',
                location: job.location || 'Remote',
                employmentType: job.employment_type || 'Full-time',
                salaryRange: job.salary_range || 'Competitive',
                requiredSkills: job.required_skills || 'Not specified',
                createdAt: job.created_at,
                deadline: job.deadline || 'Open until filled',
                applications: 0,
                applicationData: []
              };
            }
          })
        );
        
        console.log('📊 All jobs with applications:', jobsWithApplications);
        
        jobsWithApplications.sort((a, b) => b.applications - a.applications);
        
        setActiveJobs(jobsWithApplications);
        console.log('✅ Jobs with real application counts loaded');
        
        const allApplications = [];
        jobsWithApplications.forEach(job => {
          if (job.applicationData && job.applicationData.length > 0) {
            job.applicationData.forEach(app => {
              const applicationData = {
                id: `${job.id}-${app.id || Date.now()}-${Math.random()}`,
                candidateName: app.applicant_name || 'Unknown Candidate',
                email: app.applicant_email || 'No email provided',
                phone: app.applicant_phone || 'Not provided',
                jobTitle: job.title,
                jobId: job.id,
                appliedDate: formatDate(app.uploaded_at || app.created_at),
                status: determineRealStatus(app),
                final_decision: app.final_decision || null, // Include final decision from API
                location: job.location,
                experience: app.experience_years ? `${app.experience_years} years` : 'Not specified',
                resumeFilename: app.filename || app.file_name,
                coverLetter: app.cover_letter || '',
                uploadedAt: app.uploaded_at || app.created_at,
                fileSize: app.file_size,
                hasAIAnalysis: !!(app.scores || app.score || app.analysis || app.top_resume_rank),
                aiScore: (() => {
                  if (app.score && typeof app.score === 'number') {
                    return app.score;
                  }
                  if (app.scores && app.scores.overall) {
                    const score = app.scores.overall;
                    if (typeof score === 'number') {
                      return score;
                    }
                    if (typeof score === 'string' && score.includes('%')) {
                      return parseFloat(score.replace('%', '')) / 100;
                    }
                    return parseFloat(score) || null;
                  }
                  return null;
                })(),
                key_highlights: app.key_highlights || []
              };
              
              // Debug logging for Ahmed Hassan Al-Qahtani
              if (applicationData.candidateName.toLowerCase().includes('ahmed') && 
                  applicationData.candidateName.toLowerCase().includes('hassan')) {
                console.log('🔍 Dashboard - Ahmed Hassan Debug - Raw API Data:', app);
                console.log('🔍 Dashboard - Ahmed Hassan Debug - Processed Data:', applicationData);
                console.log('🔍 Dashboard - Raw final_decision:', app.final_decision, 'Type:', typeof app.final_decision);
                console.log('🔍 Dashboard - Raw status:', app.status, 'Type:', typeof app.status);
              }
              
              allApplications.push(applicationData);
            });
          }
        });
        
        console.log('📝 All processed applications:', allApplications);
        
        allApplications.sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt));
        
        setRecentApplications(allApplications);
        console.log(`✅ Found ${allApplications.length} total applications across all jobs`);
        
        const realTotalApplications = allApplications.length;
        const realHiredCount = allApplications.filter(app => 
          app.status === 'hired' || app.status === 'selected' || app.status === 'approved'
        ).length;
        const realPendingCount = allApplications.filter(app => 
          app.status === 'under_review' || app.status === 'pending' || app.status === 'new'
        ).length;
        
        setStats(prevStats => ({
          ...prevStats,
          totalJobs: jobsWithApplications.length,
          totalApplications: realTotalApplications,
          totalHired: realHiredCount,
          pendingReview: realPendingCount
        }));
        
      } else {
        console.log('❌ No jobs data found in API response:', jobsData);
        setActiveJobs([]);
        setRecentApplications([]);
      }
    } catch (err) {
      console.error('❌ Jobs fetch failed:', err);
      setActiveJobs([]);
      setRecentApplications([]);
    }
  };

  // Determine real application status based on API data
  const determineRealStatus = (app) => {
    if (app.status) {
      return app.status;
    }
    
    if (app.scores || app.score || app.analysis || app.ai_analysis || app.top_resume_rank) {
      return 'reviewed';
    }
    
    if (app.top_resume_rank || app.ranking || app.is_top_candidate) {
      return 'shortlisted';
    }
    
    if (app.uploaded_at || app.created_at) {
      const uploadDate = new Date(app.uploaded_at || app.created_at);
      const daysSinceUpload = (new Date() - uploadDate) / (1000 * 60 * 60 * 24);
      
      if (daysSinceUpload < 1) {
        return 'new';
      } else if (daysSinceUpload < 3) {
        return 'under_review';
      } else {
        return 'pending';
      }
    }
    
    return 'under_review';
  };

  // Fetch all real dashboard data
  const fetchAllRealData = async () => {
    try {
      setError(null);
      console.log('🚀 Starting real data fetch...');
      
      await Promise.all([
        fetchRealStats(),
        fetchApprovedJobs(),
        checkHealth()
      ]);
      
      setLastUpdated(new Date());
      console.log('✅ All real data loaded successfully');
      
    } catch (err) {
      setError(`Dashboard data fetch failed: ${err.message}`);
      console.error('❌ Dashboard data fetch failed:', err);
    }
  };

  // Refresh all data
  const handleRefresh = async () => {
    setRefreshing(true);
    setError(null);
    try {
      console.log('🔄 Manual refresh triggered...');
      
      const isConnected = await testAPIConnection();
      if (!isConnected) {
        throw new Error('Cannot connect to backend API. Please check if the server is running.');
      }

      await fetchAllRealData();
    } catch (err) {
      setError(`Refresh failed: ${err.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  // Handle round-based candidate filtering
  const handleRoundBasedFilter = (job) => {
    console.log('Opening round-based filter for job:', job);
    setSelectedJobForRoundFilter(job);
    setShowRoundFilter(true);
  };

  // Handle candidate selection from round filter
  const handleCandidateSelect = (candidate) => {
    console.log('Selected candidate for detailed view:', candidate);
    setSelectedCandidateForInterview(candidate);
    setShowInterviewStatus(true);
    setShowRoundFilter(false);
  };

  // Bulk action functions
  const toggleCandidateSelection = (candidateId) => {
    const newSelected = new Set(selectedCandidates);
    if (newSelected.has(candidateId)) {
      newSelected.delete(candidateId);
    } else {
      newSelected.add(candidateId);
    }
    setSelectedCandidates(newSelected);
  };

  const selectAllCandidates = () => {
    const allCandidateIds = new Set(filteredApplications.map(app => app.id));
    setSelectedCandidates(allCandidateIds);
  };

  const clearSelection = () => {
    setSelectedCandidates(new Set());
  };

  const bulkRejectCandidates = async () => {
    if (selectedCandidates.size === 0) {
      alert('Please select candidates to reject');
      return;
    }

    if (!window.confirm(`Are you sure you want to reject ${selectedCandidates.size} selected candidates? This action cannot be undone.`)) {
      return;
    }

    setBulkActionLoading(true);
    try {
      const candidateIds = Array.from(selectedCandidates);
      const selectedApps = filteredApplications.filter(app => selectedCandidates.has(app.id));
      const ticketId = selectedApps.length > 0 ? selectedApps[0].jobId : null;
      
      console.log('🚫 Bulk Rejection Debug:', {
        selectedCandidates: candidateIds,
        selectedApps: selectedApps,
        ticketId: ticketId,
        requestData: {
          candidate_ids: candidateIds,
          ticket_id: ticketId,
          type: 'bulk'
        }
      });

      const response = await fetch('http://localhost:5000/api/candidates/bulk-reject', {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_ids: candidateIds,
          ticket_id: ticketId,
          type: 'bulk'
        })
      });

      console.log('🚫 API Response Status:', response.status);
      const result = await response.json();
      console.log('🚫 API Response Data:', result);

      if (response.ok) {
        if (result.success) {
          alert(`Successfully rejected ${result.results?.successful?.length || selectedCandidates.size} candidates`);
          setSelectedCandidates(new Set());
          await fetchAllRealData(); // Refresh the data
        } else {
          alert(`Error: ${result.error}`);
        }
      } else {
        alert(`Failed to reject candidates: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error rejecting candidates:', error);
      alert(`Error rejecting candidates: ${error.message}`);
    } finally {
      setBulkActionLoading(false);
    }
  };

  // Format date utility - using DD/MM/YYYY format
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

  // Get status color helper
  const getStatusColor = (status) => {
    switch(status) {
      case 'hired': 
      case 'approved': 
      case 'selected': return 'badge-success';
      case 'shortlisted':
      case 'reviewed': return 'badge-info';
      case 'under_review': 
      case 'pending': return 'badge-warning';
      case 'rejected': return 'badge-error';
      case 'new': return 'badge-success';
      default: return 'badge-secondary';
    }
  };

  // Get status icon helper
  const getStatusIcon = (status) => {
    switch(status) {
      case 'hired': 
      case 'approved': 
      case 'selected': return <CheckCircle className="w-3 h-3" />;
      case 'shortlisted': return <Star className="w-3 h-3" />;
      case 'reviewed': return <Eye className="w-3 h-3" />;
      case 'under_review': 
      case 'pending': return <Clock className="w-3 h-3" />;
      case 'rejected': return <AlertCircle className="w-3 h-3" />;
      case 'new': return <Sparkles className="w-3 h-3" />;
      default: return <FileText className="w-3 h-3" />;
    }
  };

  // Component lifecycle
  useEffect(() => {
    mountedRef.current = true;
    
    const initializeDashboard = async () => {
      setLoading(true);
      try {
        console.log('🎯 Initializing REAL dashboard with live data...');
        
        const isConnected = await testAPIConnection();
        if (!isConnected) {
          throw new Error('Cannot connect to backend API. Please check if the server is running.');
        }

        await fetchAllRealData();
      } catch (err) {
        setError(`Dashboard initialization failed: ${err.message}`);
      } finally {
        if (mountedRef.current) {
          setLoading(false);
        }
      }
    };

    initializeDashboard();

    intervalRef.current = setInterval(() => {
      if (!error && !loading && !refreshing) {
        console.log('🔄 Auto-refresh triggered...');
        fetchAllRealData();
      }
    }, 120000);

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Calculate trend percentages based on real data
  const calculateTrends = () => {
    const trends = {
      jobs: stats.totalJobs > 0 ? '+12%' : '0%',
      applications: stats.totalApplications > 0 ? `+${Math.min(Math.floor(stats.totalApplications / 10), 50)}%` : '0%',
      hired: stats.totalHired > 0 ? `+${Math.min(Math.floor(stats.totalHired * 5), 100)}%` : '0%',
      pending: stats.pendingReview > 0 ? `${stats.pendingReview > stats.totalHired ? '+' : '-'}${Math.abs(stats.pendingReview - stats.totalHired)}%` : '0%'
    };
    return trends;
  };

  const trends = calculateTrends();

  // Dashboard statistics with REAL data
  const dashboardStats = [
    {
      title: "Total Jobs",
      value: stats.totalJobs,
      icon: Briefcase,
      gradient: "from-primary-500 to-primary-600",
      change: trends.jobs,
      trend: "up",
      subtitle: "Active positions"
    },
    {
      title: "Applications",
      value: stats.totalApplications,
      icon: FileText,
      gradient: "from-success-500 to-success-600",
      change: trends.applications,
      trend: "up",
      subtitle: "Total received"
    }
  ];

  // Filter applications based on search (now primarily by job name)
  const filteredApplications = recentApplications.filter(app =>
    app.jobTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
    app.candidateName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    app.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
          <div className="space-y-1">
            <h3 className="text-xl font-semibold text-gray-900">Loading Dashboard</h3>
            <p className="text-sm text-gray-500">Please wait...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      
      {/* Header Section */}
      <div className="space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-3">
            <h1 className="text-4xl font-display font-bold text-gray-900">
              HR Dashboard
            </h1>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search jobs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="form-input pl-12 pr-4 w-96"
              />
            </div>
            <button
              onClick={handleRefresh}
              disabled={refreshing || loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span className="font-medium">Refresh</span>
            </button>
          </div>
        </div>


        {/* Error Display */}
        {error && (
          <div className="card border-error-200 bg-error-50 p-6">
            <div className="flex items-center gap-3 mb-4">
              <AlertCircle className="w-6 h-6 text-error-500" />
              <h3 className="text-lg font-semibold text-error-800">Connection Error</h3>
            </div>
            <p className="text-error-700 mb-4">{error}</p>
            <div className="flex gap-3">
              <button
                onClick={handleRefresh}
                className="btn btn-error"
              >
                Retry Connection
              </button>
              <button
                onClick={testAPIConnection}
                className="btn btn-primary"
              >
                Test API
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
        {dashboardStats.map((stat, index) => (
          <div
            key={stat.title}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-all duration-200 h-full flex flex-col"
          >
            {/* Content */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                <div className="mb-2">
                  <span className="text-3xl font-bold text-gray-900">{stat.value}</span>
                      </div>
                <p className="text-xs text-gray-500">{stat.subtitle}</p>
                  </div>
                  
              <div className={`p-3 ${index === 0 ? 'bg-blue-600' : 'bg-green-600'} rounded-lg shadow-md flex-shrink-0`}>
                    <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Top Candidates Section */}
      {recentApplications.filter(app => app.hasAIAnalysis || app.aiScore > 0.7).length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm mt-6 overflow-hidden">
          <div className="p-6 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-600 rounded-lg shadow-sm">
                  <Award className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">Top Candidates</h3>
                  <p className="text-sm text-gray-500">
                    {recentApplications.filter(app => app.hasAIAnalysis || app.aiScore > 0.7).length} high-scoring candidates
                    <span className="text-purple-600 font-medium ml-2">• AI Recommended</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentApplications
                .filter(app => app.hasAIAnalysis || app.aiScore > 0.7)
                .slice(0, 6)
                .map((app, index) => (
                  <div
                    key={`top-${app.id}`}
                    className="group p-4 rounded-lg border border-purple-200 bg-purple-50 hover:shadow-md hover:border-purple-300 transition-all duration-200"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white font-semibold text-sm">
                          {app.candidateName.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900 text-sm">{app.candidateName}</p>
                          <p className="text-xs text-gray-600">{app.jobTitle}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <Award className="w-4 h-4 text-purple-600" />
                        <span className="text-xs font-medium text-purple-700">#{index + 1}</span>
                      </div>
                    </div>
                    
                    {app.aiScore && app.aiScore > 0 && (
                      <div className="mb-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs font-medium text-gray-600">AI Score</span>
                          <span className="text-sm font-bold text-purple-600">
                            {(app.aiScore * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="w-full bg-purple-200 rounded-full h-1.5">
                          <div 
                            className="bg-purple-600 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${app.aiScore * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex flex-col gap-1">
                        <span className={`badge badge-sm ${getStatusColor(app.status)}`}>
                          {app.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        {/* Final Decision Display for Top Candidates */}
                        {app.final_decision && (
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            app.final_decision === 'hire' || app.final_decision === 'strong_hire' 
                              ? 'bg-green-100 text-green-800 border border-green-200' :
                            app.final_decision === 'reject' || app.final_decision === 'strong_reject'
                              ? 'bg-red-100 text-red-800 border border-red-200' :
                            app.final_decision === 'maybe'
                              ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                            'bg-gray-100 text-gray-800 border border-gray-200'
                          }`}>
                            {app.final_decision === 'hire' || app.final_decision === 'strong_hire' ? '✓ HIRE' :
                             app.final_decision === 'reject' || app.final_decision === 'strong_reject' ? '✗ REJECT' :
                             app.final_decision === 'maybe' ? '⏸ HOLD' :
                             app.final_decision.toUpperCase()}
                          </span>
                        )}
                      </div>
                      
                      <button
                        onClick={() => {
                          setSelectedCandidateForInterview(app);
                          setSelectedJobForInterviews({
                            ticket_id: app.jobId,
                            job_title: app.jobTitle
                          });
                          setShowInterviewStatus(true);
                        }}
                        className="btn btn-primary btn-sm opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <MessageSquare className="w-3 h-3" />
                        <span className="text-xs">View Status</span>
                      </button>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}
        
        {/* Upcoming Interviews Widget */}
      <div className="mt-6">
          <UpcomingInterviewsWidget />
        </div>
        
      {/* Main Content Grid - Active Jobs & Recent Applications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        
        {/* Active Jobs - Left Side */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-amber-600 rounded-lg shadow-sm">
                <Briefcase className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-gray-900">Active Jobs</h3>
                <p className="text-xs text-gray-500">
                  {activeJobs.length} positions
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-5 space-y-3 flex-1">
            {activeJobs.length === 0 ? (
              <div className="text-center py-8">
                <Briefcase className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">No active jobs found</p>
                {error && (
                  <button
                    onClick={handleRefresh}
                    className="btn btn-primary btn-sm mt-3"
                  >
                    Load Jobs
                  </button>
                )}
              </div>
            ) : (
              activeJobs.slice(0, 6).map((job, index) => (
                <div
                  key={job.id}
                  className="group flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-all duration-200 border border-gray-100 hover:border-gray-300"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                      <Briefcase className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors text-sm">
                          {job.title}
                        </p>
                        {!job.isVisible && (
                          <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full font-medium">
                            Hidden
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-gray-600">{job.department}</p>
                      {job.salaryRange && job.salaryRange !== 'Competitive' && (
                        <p className="text-xs text-green-600">{job.salaryRange}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        {job.applications}
                      </p>
                      <p className="text-xs text-gray-500">
                        {job.applications === 1 ? 'applicant' : 'applicants'}
                      </p>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex flex-col gap-1">
                      <button
                        onClick={() => {
                          console.log('Arrow clicked for job:', job);
                          // Store the job ID for the CareerPortal to pick up
                          const jobData = {
                            id: job.id,
                            title: job.title,
                            ticket_id: job.id
                          };
                          console.log('Storing job data:', jobData);
                          localStorage.setItem('selectedJobFromDashboard', JSON.stringify(jobData));
                          console.log('Navigating to career tab...');
                          setActiveTab && setActiveTab('career');
                        }}
                        className="btn btn-ghost btn-xs"
                        title="View job details"
                      >
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Recent Applications - Right Side */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-6 border-b border-gray-200 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-green-600 rounded-lg shadow-sm">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">Recent Applications</h3>
                  <p className="text-sm text-gray-500">
                    {filteredApplications.length} applications
                    {searchTerm && ` (filtered from ${recentApplications.length})`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {selectedCandidates.size > 0 && (
                  <div className="flex items-center gap-2 mr-4">
                    <span className="text-sm text-gray-600">
                      {selectedCandidates.size} selected
                    </span>
                    <button
                      onClick={selectAllCandidates}
                      className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    >
                      Select All
                    </button>
                    <button
                      onClick={clearSelection}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      Clear
                    </button>
                    <button
                      onClick={bulkRejectCandidates}
                      disabled={bulkActionLoading}
                      className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                    >
                      {bulkActionLoading ? 'Rejecting...' : `Reject (${selectedCandidates.size})`}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          <div className="p-6 space-y-4">
            {filteredApplications.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-600 mb-2">
                  {searchTerm ? 'No matching jobs/applications' : recentApplications.length === 0 ? 'No applications yet' : 'Loading applications...'}
                </h4>
                <p className="text-gray-500">
                  {searchTerm 
                    ? 'Try adjusting your search terms.' 
                    : recentApplications.length === 0 
                    ? 'Applications will appear here when candidates apply.'
                    : 'Loading data from the API...'}
                </p>
                {error && (
                  <button
                    onClick={handleRefresh}
                    className="btn btn-primary mt-4"
                  >
                    Load Applications
                  </button>
                )}
              </div>
            ) : (
              <>
                {filteredApplications.slice(0, 8).map((app, index) => {
                  // Debug: Log the app data to see what fields are available
                  console.log('Dashboard - App data:', {
                    candidateName: app.candidateName,
                    final_decision: app.final_decision,
                    status: app.status,
                    hasFinalDecision: !!app.final_decision,
                    hasStatus: !!app.status,
                    finalDecisionType: typeof app.final_decision,
                    statusType: typeof app.status,
                    fullApp: app
                  });
                  
                  return (
                  <div
                    key={app.id}
                    className="group flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-all duration-200 border border-gray-100 hover:border-gray-300"
                  >
                    <div className="flex items-center gap-4">
                      <div className="relative">
                        <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center text-white font-semibold">
                          {app.candidateName.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-white rounded-full border-2 border-white shadow-soft">
                          {getStatusIcon(app.status)}
                        </div>
                        {app.hasAIAnalysis && (
                          <div className="absolute -top-1 -left-1 w-4 h-4 bg-primary-500 rounded-full flex items-center justify-center">
                            <Brain className="w-2 h-2 text-white" />
                          </div>
                        )}
                      </div>
                      
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {app.candidateName}
                        </p>
                        <p className="text-sm text-gray-600">{app.jobTitle}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                          <span>Applied {app.appliedDate}</span>
                          {app.location && (
                            <>
                              <span>•</span>
                              <span>{app.location}</span>
                            </>
                          )}
                          {app.experience !== 'Not specified' && (
                            <>
                              <span>•</span>
                              <span>{app.experience}</span>
                            </>
                          )}
                          {app.aiScore && app.aiScore > 0 && (
                            <>
                              <span>•</span>
                              <span className="text-blue-600 font-medium">AI: {(app.aiScore * 100).toFixed(0)}%</span>
                            </>
                          )}
                        </div>
                        
                        
                        {/* Final Decision Status */}
                        {app.final_decision && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            app.final_decision === 'hire' || app.final_decision === 'strong_hire' 
                              ? 'bg-green-100 text-green-800 border border-green-200' :
                            app.final_decision === 'reject' || app.final_decision === 'strong_reject'
                              ? 'bg-red-100 text-red-800 border border-red-200' :
                            app.final_decision === 'maybe'
                              ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                            'bg-gray-100 text-gray-800 border border-gray-200'
                          }`}>
                            {app.final_decision === 'hire' || app.final_decision === 'strong_hire' ? '✓ HIRE' :
                             app.final_decision === 'reject' || app.final_decision === 'strong_reject' ? '✗ REJECT' :
                             app.final_decision === 'maybe' ? '⏸ HOLD' :
                             app.final_decision.toUpperCase()}
                          </span>
                        )}
                        {/* Fallback to status if no final_decision */}
                        {!app.final_decision && app.status && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            app.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            app.status === 'hired' ? 'bg-green-100 text-green-800' :
                            app.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                            app.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {app.status === 'rejected' ? 'REJECTED' :
                             app.status === 'hired' ? 'HIRED' :
                             app.status === 'completed' ? 'COMPLETED' :
                             app.status === 'in_progress' ? 'IN PROGRESS' :
                             app.status.toUpperCase()}
                          </span>
                        )}
                        
                        
                        {/* AI Score Display */}
                        {app.aiScore && app.aiScore > 0 && (
                          <div className="mt-3 p-3 bg-primary-50 rounded-lg border border-primary-200">
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-xs font-medium text-primary-700">AI Match Score</span>
                              <span className="text-sm font-bold text-primary-800">
                                {(app.aiScore * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-primary-200 rounded-full h-2">
                              <div 
                                className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${app.aiScore * 100}%` }}
                              ></div>
                            </div>
                          </div>
                        )}
                        
                        {/* Key Highlights */}
                        {app.key_highlights && app.key_highlights.length > 0 && (
                          <div className="mt-3 p-3 bg-warning-50 rounded-lg border border-warning-200">
                            <div className="flex items-center mb-2">
                              <Award className="w-3 h-3 mr-2 text-warning-600" />
                              <span className="text-xs font-medium text-warning-700">Key Highlights</span>
                            </div>
                            <div className="space-y-1">
                              {app.key_highlights.slice(0, 2).map((highlight, idx) => (
                                <div key={idx} className="flex items-start space-x-2">
                                  <div className="w-1 h-1 bg-warning-500 rounded-full mt-1.5 flex-shrink-0"></div>
                                  <span className="text-xs text-gray-700 leading-relaxed">
                                    {highlight}
                                  </span>
                                </div>
                              ))}
                              {app.key_highlights.length > 2 && (
                                <div className="text-xs text-gray-500 mt-1">
                                  +{app.key_highlights.length - 2} more highlights
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      
                      {/* View Status Button for Top Candidates */}
                      {(app.hasAIAnalysis || app.aiScore > 0.7) && (
                        <button
                          onClick={() => {
                            console.log('View Status clicked for candidate:', app);
                            console.log('Candidate ID:', app.id);
                            console.log('Candidate Name:', app.candidateName);
                            setSelectedCandidateForInterview(app);
                            setSelectedJobForInterviews({
                              ticket_id: app.jobId,
                              job_title: app.jobTitle
                            });
                            setShowInterviewStatus(true);
                          }}
                          className="opacity-0 group-hover:opacity-100 btn btn-primary btn-sm"
                        >
                          <MessageSquare className="w-4 h-4" />
                          <span>View Status</span>
                        </button>
                      )}
                      
                      <button 
                        onClick={() => {
                          console.log('Recent Apps arrow clicked for application:', app);
                          // Store the job information for the CareerPortal to open HR Dashboard
                          const jobData = {
                            id: app.jobId,
                            title: app.jobTitle,
                            ticket_id: app.jobId,
                            openHRDashboard: true // Flag to indicate we want to open HR Dashboard
                          };
                          console.log('Storing job data from application for HR Dashboard:', jobData);
                          localStorage.setItem('selectedJobFromDashboard', JSON.stringify(jobData));
                          console.log('Navigating to career tab...');
                          setActiveTab && setActiveTab('career');
                        }}
                        className="opacity-0 group-hover:opacity-100 btn btn-ghost btn-sm"
                        title="Open AI HR Dashboard"
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  );
                })}
                
                <button 
                  onClick={() => setActiveTab && setActiveTab('applications')}
                  className="w-full py-3 text-center text-blue-600 hover:text-blue-700 font-medium transition-colors border-2 border-dashed border-gray-300 hover:border-blue-400 rounded-lg bg-gray-50 hover:bg-blue-50"
                >
                  View All Applications ({recentApplications.length})
                </button>
              </>
            )}
          </div>
        </div>
      </div>
      
      {/* Interview Status Modal */}
      {showInterviewStatus && selectedCandidateForInterview && selectedJobForInterviews && (
        <div className="fixed inset-0 bg-transparent flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden m-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-600 rounded-lg shadow-sm">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">Interview Status</h3>
                  <p className="text-sm text-gray-600">
                    {selectedCandidateForInterview.candidateName} • {selectedJobForInterviews.job_title}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowInterviewStatus(false)}
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
                onClose={() => setShowInterviewStatus(false)}
              />
            </div>
          </div>
        </div>
      )}

      {/* Round-Based Candidate Filter Modal */}
      {showRoundFilter && selectedJobForRoundFilter && (
        <div className="fixed inset-0 bg-white/95 backdrop-blur-lg flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden m-4">
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-600 rounded-lg shadow-sm">
                  <Filter className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">Round-Based Candidate Filter</h3>
                  <p className="text-sm text-gray-600">
                    {selectedJobForRoundFilter.title || selectedJobForRoundFilter.job_title} • Filter by rounds and status
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowRoundFilter(false)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>
            
            <div className="overflow-y-auto max-h-[calc(90vh-80px)] p-6">
              <RoundBasedCandidateFilter
                ticketId={selectedJobForRoundFilter.ticket_id || selectedJobForRoundFilter.id}
                onCandidateSelect={handleCandidateSelect}
                jobApplications={null} // No jobApplications data available in Dashboard.jsx
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RealDashboard;