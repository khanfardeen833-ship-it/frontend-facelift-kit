import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import ManagerFeedbackForm from '../components/ManagerFeedbackForm';
import {
  User,
  Calendar,
  Clock,
  Briefcase,
  Mail,
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  Star,
  Sparkles
} from 'lucide-react';

const ManagerFeedbackPage = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  // Extract parameters from URL
  const interviewId = searchParams.get('interview_id');
  const candidateId = searchParams.get('candidate_id');
  const candidateName = searchParams.get('candidate_name');
  const candidateEmail = searchParams.get('candidate_email');
  const jobTitle = searchParams.get('job_title');
  const roundName = searchParams.get('round_name');

  useEffect(() => {
    // Validate required parameters
    if (!interviewId || !candidateId || !candidateName || !candidateEmail) {
      setError('Missing required parameters. Please use the link provided in your email.');
      setLoading(false);
      return;
    }

    // Simulate loading time for better UX
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  }, [interviewId, candidateId, candidateName, candidateEmail]);

  const handleFeedbackSuccess = () => {
    setShowFeedbackForm(false);
    // Could redirect or show success message
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Star className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading Feedback System</h2>
          <p className="text-gray-600">Preparing your premium feedback experience...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.history.back()}
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div className="flex items-center space-x-2">
                <Sparkles className="w-6 h-6 text-purple-600" />
                <h1 className="text-xl font-bold text-gray-900">Manager Feedback System</h1>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>Premium Feedback Portal</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!showFeedbackForm ? (
          <div className="space-y-8">
            {/* Welcome Section */}
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Star className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Welcome to Manager Feedback
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Thank you for participating in the interview process. Your feedback is crucial for making informed hiring decisions and helping candidates understand their performance.
              </p>
            </div>

            {/* Candidate Information Card */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white">Interview Details</h3>
                <p className="text-blue-100">Please review the candidate information before providing feedback</p>
              </div>
              
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Candidate Name</p>
                        <p className="font-semibold text-gray-900">{candidateName}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <Mail className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Email Address</p>
                        <p className="font-semibold text-gray-900">{candidateEmail}</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                        <Briefcase className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Position</p>
                        <p className="font-semibold text-gray-900">{jobTitle || 'Not specified'}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
                        <Calendar className="w-5 h-5 text-orange-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Interview Round</p>
                        <p className="font-semibold text-gray-900">{roundName || 'Not specified'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Features Section */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6">
              <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">
                Premium Feedback Features
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="text-center p-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Star className="w-6 h-6 text-blue-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Comprehensive Rating</h4>
                  <p className="text-sm text-gray-600">Rate technical skills, communication, problem-solving, and cultural fit</p>
                </div>

                <div className="text-center p-4">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Detailed Assessment</h4>
                  <p className="text-sm text-gray-600">Provide strengths, areas for improvement, and detailed feedback</p>
                </div>

                <div className="text-center p-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <User className="w-6 h-6 text-purple-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Team Fit Analysis</h4>
                  <p className="text-sm text-gray-600">Evaluate team compatibility and hiring recommendation</p>
                </div>

                <div className="text-center p-4">
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Briefcase className="w-6 h-6 text-yellow-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Salary Assessment</h4>
                  <p className="text-sm text-gray-600">Evaluate salary expectations and start date availability</p>
                </div>

                <div className="text-center p-4">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Clock className="w-6 h-6 text-red-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Quick & Easy</h4>
                  <p className="text-sm text-gray-600">Step-by-step process that takes just a few minutes</p>
                </div>

                <div className="text-center p-4">
                  <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Sparkles className="w-6 h-6 text-indigo-600" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">Professional</h4>
                  <p className="text-sm text-gray-600">Feedback visible to candidates for transparency</p>
                </div>
              </div>
            </div>

            {/* Start Feedback Button */}
            <div className="text-center">
              <button
                onClick={() => setShowFeedbackForm(true)}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
              >
                <Sparkles className="w-5 h-5 inline mr-2" />
                Start Feedback Process
              </button>
              <p className="text-sm text-gray-500 mt-3">
                This will take approximately 5-10 minutes to complete
              </p>
            </div>
          </div>
        ) : (
          <ManagerFeedbackForm
            interviewId={interviewId}
            candidateId={candidateId}
            candidateName={candidateName}
            candidateEmail={candidateEmail}
            jobTitle={jobTitle}
            roundName={roundName}
            onClose={() => setShowFeedbackForm(false)}
            onSuccess={handleFeedbackSuccess}
          />
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>© 2024 HR Management System. Premium feedback portal for professional interview assessment.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManagerFeedbackPage;
