import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import CareerPortal from './components/CareerPortal';
import ApplicationStatus from './components/ApplicationStatus';
import HiringChatBot from './components/HiringChatBot';
import Auth from './components/Auth';
import ProtectedRoute from './components/ProtectedRoute';
import RoundBasedCandidateFilter from './components/RoundBasedCandidateFilter';
import ManagerFeedbackForm from './components/ManagerFeedbackForm';
// import { initModalScrollFix } from './utils/modalScrollFix'; // DISABLED to fix auto-scroll issue


function AppContent() {
  const [activeTab, setActiveTab] = useState('career'); // Start with career portal
  const [userRole, setUserRole] = useState('hr'); // Default to hr for HR manager interface
  const [showManagerFeedback, setShowManagerFeedback] = useState(false);
  const [feedbackData, setFeedbackData] = useState(null);
  
  // Initialize modal scroll fix - DISABLED to fix auto-scroll issue
  // useEffect(() => {
  //   const observer = initModalScrollFix();
  //   return () => {
  //     if (observer) {
  //       observer.disconnect();
  //     }
  //   };
  // }, []);

  // Check for manager feedback URL parameters
  useEffect(() => {
    const checkManagerFeedbackParams = () => {
      const hash = window.location.hash;
      if (hash.includes('manager-feedback')) {
        const urlParams = new URLSearchParams(hash.split('?')[1]);
        const interviewId = urlParams.get('interview_id');
        const candidateId = urlParams.get('candidate_id');
        const candidateName = urlParams.get('candidate_name');
        const candidateEmail = urlParams.get('candidate_email');
        const jobTitle = urlParams.get('job_title');
        const roundName = urlParams.get('round_name');

        if (interviewId && candidateId && candidateName && candidateEmail) {
          setFeedbackData({
            interviewId,
            candidateId,
            candidateName,
            candidateEmail,
            jobTitle: jobTitle || 'Position',
            roundName: roundName || 'Interview Round'
          });
          setShowManagerFeedback(true);
          
          // Clear the URL hash to clean up the browser history
          window.history.replaceState(null, null, window.location.pathname);
        }
      }
    };

    // Check on component mount
    checkManagerFeedbackParams();

    // Also check when hash changes
    const handleHashChange = () => {
      checkManagerFeedbackParams();
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => {
      window.removeEventListener('hashchange', handleHashChange);
    };
  }, []);
  
  // Legacy fake data for Dashboard and Applications (kept for compatibility)
  const [jobs, setJobs] = useState([
    {
      id: 1,
      title: 'Senior Frontend Developer',
      department: 'Engineering',
      location: 'San Francisco, CA',
      salary: '$120,000 - $150,000',
      type: 'Full-time',
      posted: '2025-06-15',
      applications: 12,
      status: 'active',
      description: 'We are looking for a Senior Frontend Developer to join our dynamic team. You will be responsible for developing user-facing applications using modern JavaScript frameworks and ensuring excellent user experience.'
    },
    {
      id: 2,
      title: 'UX Designer',
      department: 'Design',
      location: 'Remote',
      salary: '$90,000 - $110,000',
      type: 'Full-time',
      posted: '2025-06-10',
      applications: 8,
      status: 'active',
      description: 'Join our design team to create intuitive and beautiful user experiences. You will work closely with product managers and developers to bring designs to life.'
    },
    {
      id: 3,
      title: 'Marketing Manager',
      department: 'Marketing',
      location: 'New York, NY',
      salary: '$80,000 - $100,000',
      type: 'Full-time',
      posted: '2025-06-08',
      applications: 15,
      status: 'active',
      description: 'Lead our marketing initiatives and drive brand awareness. You will develop and execute marketing strategies across multiple channels.'
    },
    {
      id: 4,
      title: 'Product Manager',
      department: 'Product',
      location: 'Austin, TX',
      salary: '$110,000 - $140,000',
      type: 'Full-time',
      posted: '2025-06-05',
      applications: 20,
      status: 'active',
      description: 'Drive product strategy and roadmap execution. You will work with cross-functional teams to deliver innovative products that delight our customers.'
    }
  ]);

  const [applications, setApplications] = useState([
    {
      id: 1,
      jobId: 1,
      jobTitle: 'Senior Frontend Developer',
      candidateName: 'John Smith',
      email: 'john.smith@email.com',
      phone: '+1 (555) 123-4567',
      appliedDate: '2025-06-16',
      status: 'under_review',
      resume: 'john_smith_resume.pdf',
      experience: '5 years'
    },
    {
      id: 2,
      jobId: 1,
      jobTitle: 'Senior Frontend Developer',
      candidateName: 'Sarah Johnson',
      email: 'sarah.j@email.com',
      phone: '+1 (555) 234-5678',
      appliedDate: '2025-06-15',
      status: 'interview_scheduled',
      resume: 'sarah_johnson_resume.pdf',
      experience: '7 years'
    },
    {
      id: 3,
      jobId: 2,
      jobTitle: 'UX Designer',
      candidateName: 'Mike Chen',
      email: 'mike.chen@email.com',
      phone: '+1 (555) 345-6789',
      appliedDate: '2025-06-14',
      status: 'hired',
      resume: 'mike_chen_resume.pdf',
      experience: '4 years'
    },
    {
      id: 4,
      jobId: 3,
      jobTitle: 'Marketing Manager',
      candidateName: 'Emily Davis',
      email: 'emily.davis@email.com',
      phone: '+1 (555) 456-7890',
      appliedDate: '2025-06-13',
      status: 'under_review',
      resume: 'emily_davis_resume.pdf',
      experience: '6 years'
    },
    {
      id: 5,
      jobId: 4,
      jobTitle: 'Product Manager',
      candidateName: 'Alex Rodriguez',
      email: 'alex.r@email.com',
      phone: '+1 (555) 567-8901',
      appliedDate: '2025-06-12',
      status: 'rejected',
      resume: 'alex_rodriguez_resume.pdf',
      experience: '3 years'
    }
  ]);

  // Legacy job addition (for compatibility with Dashboard)
  const addJob = (jobData) => {
    const newJob = {
      ...jobData,
      id: jobs.length + 1,
      posted: new Date().toISOString().split('T')[0],
      applications: 0,
      status: 'active'
    };
    setJobs(prev => [...prev, newJob]);
  };

  // Handle job application (now supports both API job IDs and legacy IDs)
  const applyToJob = (jobId) => {
    console.log('Applying to job:', jobId);
    
    // For API jobs (string ticket_id)
    if (typeof jobId === 'string') {
      const newApplication = {
        id: applications.length + 1,
        jobId: 0, // API jobs don't use numeric IDs
        jobTitle: `API Job ${jobId}`,
        candidateName: 'Current User',
        email: 'user@email.com',
        phone: '+1 (555) 000-0000',
        appliedDate: new Date().toISOString().split('T')[0],
        status: 'under_review',
        resume: 'user_resume.pdf',
        experience: '3 years'
      };
      
      setApplications(prev => [...prev, newApplication]);
      
      // Show success message
      alert(`Successfully applied to job ${jobId}! Your application is now under review.`);
      return;
    }

    // For legacy jobs (numeric ID)
    const job = jobs.find(j => j.id === jobId);
    if (!job) return;

    const newApplication = {
      id: applications.length + 1,
      jobId: jobId,
      jobTitle: job.title,
      candidateName: 'Current User',
      email: 'user@email.com',
      phone: '+1 (555) 000-0000',
      appliedDate: new Date().toISOString().split('T')[0],
      status: 'under_review',
      resume: 'user_resume.pdf',
      experience: '3 years'
    };
    
    setApplications(prev => [...prev, newApplication]);
    setJobs(prev => prev.map(j => 
      j.id === jobId ? { ...j, applications: j.applications + 1 } : j
    ));
    
    alert(`Successfully applied to ${job.title}! Your application is now under review.`);
  };

  const updateApplicationStatus = (applicationId, newStatus) => {
    setApplications(prev => prev.map(app => 
      app.id === applicationId ? { ...app, status: newStatus } : app
    ));
  };

  // Handle when a job is posted via chat bot
  const handleJobPostedViaChat = (ticketId) => {
    // Switch to dashboard or career portal to show the new job
    setActiveTab('career');
    
    // You could also fetch the job details from the API and add it to the jobs list
    // For now, we'll just show a notification
    console.log('New job posted via chat:', ticketId);
  };

  const openManagerFeedback = (data) => {
    setFeedbackData(data);
    setShowManagerFeedback(true);
  };

  const closeManagerFeedback = () => {
    setShowManagerFeedback(false);
    setFeedbackData(null);
  };

  const { isAuthenticated, loading } = useAuth();

  // Show loading screen while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show authentication screen if not authenticated
  if (!isAuthenticated) {
    return <Auth />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard jobs={jobs} applications={applications} setActiveTab={setActiveTab} />;
      case 'career':
        return (
          <CareerPortal
            jobs={jobs} // Legacy jobs for fallback
            userRole={userRole}
            onAddJob={addJob}
            onApplyToJob={applyToJob}
          />
        );
      case 'applications':
        return (
          <RoundBasedCandidateFilter
            ticketId={null} // Show all candidates across all tickets
            onCandidateSelect={(candidate) => {
              console.log('Selected candidate:', candidate);
              // You can add additional logic here if needed
            }}
            onOpenManagerFeedback={openManagerFeedback}
            jobApplications={null} // No jobApplications data available in App.jsx
          />
        );
      case 'settings':
        // Import Settings component dynamically to avoid circular imports
        const SettingsComponent = React.lazy(() => import('./components/Settings'));
        return (
          <React.Suspense fallback={<div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>}>
            <SettingsComponent />
          </React.Suspense>
        );
      default:
        return <CareerPortal jobs={jobs} userRole={userRole} onAddJob={addJob} onApplyToJob={applyToJob} />;
    }
  };

  return (
    <ProtectedRoute>
      <Layout
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        userRole={userRole}
        setUserRole={setUserRole}
      >
        {renderContent()}
      </Layout>
      
      {/* Add the chat bot component - it will appear as a floating button */}
      <HiringChatBot onJobPosted={handleJobPostedViaChat} />
      
      {/* Manager Feedback Form Modal */}
      {showManagerFeedback && feedbackData && (
        <ManagerFeedbackForm
          interviewId={feedbackData.interviewId}
          candidateId={feedbackData.candidateId}
          candidateName={feedbackData.candidateName}
          candidateEmail={feedbackData.candidateEmail}
          jobTitle={feedbackData.jobTitle}
          roundName={feedbackData.roundName}
          onClose={closeManagerFeedback}
          onSuccess={() => {
            console.log('Manager feedback submitted successfully');
            closeManagerFeedback();
          }}
        />
      )}
    </ProtectedRoute>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;