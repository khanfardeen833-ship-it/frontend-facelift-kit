import React, { useState, useEffect } from 'react';
import {
  Star,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  User,
  Calendar,
  Clock,
  Award,
  Target,
  CheckCircle,
  AlertCircle,
  Send,
  X,
  Eye,
  TrendingUp,
  TrendingDown,
  Zap,
  Shield,
  Heart,
  Brain,
  Users,
  Briefcase,
  Lightbulb,
  ArrowRight,
  Sparkles
} from 'lucide-react';

const ManagerFeedbackForm = ({ 
  interviewId, 
  candidateId, 
  candidateName, 
  candidateEmail, 
  jobTitle, 
  roundName,
  onClose,
  onSuccess 
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    overallRating: 5,
    decision: 'hire',
    technicalSkills: 5,
    communicationSkills: 5,
    problemSolving: 5,
    culturalFit: 5,
    leadershipPotential: 5,
    strengths: '',
    areasForImprovement: '',
    detailedFeedback: '',
    recommendation: '',
    wouldHireAgain: true,
    teamFit: 'excellent',
    salaryExpectation: 'within_budget',
    startDate: 'immediate'
  });

  const [currentStep, setCurrentStep] = useState(1);
  const totalSteps = 4;

  const ratingLabels = {
    1: 'Poor',
    2: 'Below Average', 
    3: 'Average',
    4: 'Good',
    5: 'Excellent'
  };

  const decisionOptions = [
    { value: 'strong_hire', label: 'Strong Hire', icon: ThumbsUp, color: 'text-green-600', bgColor: 'bg-green-50', borderColor: 'border-green-200' },
    { value: 'hire', label: 'Hire', icon: ThumbsUp, color: 'text-green-500', bgColor: 'bg-green-50', borderColor: 'border-green-200' },
    { value: 'maybe', label: 'Maybe', icon: MessageSquare, color: 'text-yellow-600', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' },
    { value: 'no_hire', label: 'No Hire', icon: ThumbsDown, color: 'text-red-500', bgColor: 'bg-red-50', borderColor: 'border-red-200' }
  ];

  const teamFitOptions = [
    { value: 'excellent', label: 'Excellent Fit', description: 'Would be a great addition to the team' },
    { value: 'good', label: 'Good Fit', description: 'Would work well with the team' },
    { value: 'average', label: 'Average Fit', description: 'Neutral team dynamics' },
    { value: 'poor', label: 'Poor Fit', description: 'May not work well with the team' }
  ];

  const salaryOptions = [
    { value: 'within_budget', label: 'Within Budget', description: 'Salary expectations are reasonable' },
    { value: 'above_budget', label: 'Above Budget', description: 'Salary expectations are high but negotiable' },
    { value: 'significantly_above', label: 'Significantly Above', description: 'Salary expectations are too high' }
  ];

  const startDateOptions = [
    { value: 'immediate', label: 'Immediate', description: 'Can start right away' },
    { value: '2_weeks', label: '2 Weeks', description: 'Can start in 2 weeks' },
    { value: '1_month', label: '1 Month', description: 'Can start in 1 month' },
    { value: 'negotiable', label: 'Negotiable', description: 'Start date is flexible' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:5000/api/manager-feedback', {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          interview_id: interviewId,
          candidate_id: candidateId,
          candidate_name: candidateName,
          candidate_email: candidateEmail,
          job_title: jobTitle,
          round_name: roundName,
          ...formData,
          submitted_at: new Date().toISOString()
        })
      });

      if (response.ok) {
        setSuccess(true);
        if (onSuccess) onSuccess();
        setTimeout(() => {
          if (onClose) onClose();
        }, 2000);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to submit feedback');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStars = (rating, onChange, size = 'text-2xl') => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className={`${size} transition-colors ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            } hover:text-yellow-400`}
          >
            ★
          </button>
        ))}
        <span className="ml-2 text-sm text-gray-600">{ratingLabels[rating]}</span>
      </div>
    );
  };

  const renderStep1 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <Star className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Overall Assessment</h3>
        <p className="text-gray-600">Rate the candidate's overall performance</p>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
        <div className="text-center mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Overall Rating</h4>
          {renderStars(formData.overallRating, (rating) => handleInputChange('overallRating', rating), 'text-4xl')}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h5 className="font-medium text-gray-900 flex items-center">
              <Brain className="w-5 h-5 mr-2 text-blue-600" />
              Technical Skills
            </h5>
            {renderStars(formData.technicalSkills, (rating) => handleInputChange('technicalSkills', rating))}
          </div>

          <div className="space-y-4">
            <h5 className="font-medium text-gray-900 flex items-center">
              <MessageSquare className="w-5 h-5 mr-2 text-green-600" />
              Communication
            </h5>
            {renderStars(formData.communicationSkills, (rating) => handleInputChange('communicationSkills', rating))}
          </div>

          <div className="space-y-4">
            <h5 className="font-medium text-gray-900 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
              Problem Solving
            </h5>
            {renderStars(formData.problemSolving, (rating) => handleInputChange('problemSolving', rating))}
          </div>

          <div className="space-y-4">
            <h5 className="font-medium text-gray-900 flex items-center">
              <Users className="w-5 h-5 mr-2 text-purple-600" />
              Cultural Fit
            </h5>
            {renderStars(formData.culturalFit, (rating) => handleInputChange('culturalFit', rating))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <Target className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Hiring Decision</h3>
        <p className="text-gray-600">Make your recommendation</p>
      </div>

      <div className="space-y-6">
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Recommendation</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {decisionOptions.map((option) => {
              const Icon = option.icon;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleInputChange('decision', option.value)}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    formData.decision === option.value
                      ? `${option.bgColor} ${option.borderColor} ring-2 ring-offset-2 ring-blue-500`
                      : 'bg-white border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <Icon className={`w-6 h-6 ${formData.decision === option.value ? option.color : 'text-gray-400'}`} />
                    <span className={`font-medium ${formData.decision === option.value ? option.color : 'text-gray-700'}`}>
                      {option.label}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="font-medium text-gray-900 mb-3 flex items-center">
              <Users className="w-5 h-5 mr-2 text-blue-600" />
              Team Fit
            </h5>
            <div className="space-y-2">
              {teamFitOptions.map((option) => (
                <label key={option.value} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="teamFit"
                    value={option.value}
                    checked={formData.teamFit === option.value}
                    onChange={(e) => handleInputChange('teamFit', e.target.value)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <div>
                    <div className="font-medium text-gray-900">{option.label}</div>
                    <div className="text-sm text-gray-600">{option.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <h5 className="font-medium text-gray-900 mb-3 flex items-center">
              <Briefcase className="w-5 h-5 mr-2 text-green-600" />
              Salary Expectations
            </h5>
            <div className="space-y-2">
              {salaryOptions.map((option) => (
                <label key={option.value} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="salaryExpectation"
                    value={option.value}
                    checked={formData.salaryExpectation === option.value}
                    onChange={(e) => handleInputChange('salaryExpectation', e.target.value)}
                    className="w-4 h-4 text-green-600"
                  />
                  <div>
                    <div className="font-medium text-gray-900">{option.label}</div>
                    <div className="text-sm text-gray-600">{option.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <MessageSquare className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Detailed Feedback</h3>
        <p className="text-gray-600">Provide comprehensive feedback</p>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Sparkles className="w-4 h-4 inline mr-1 text-yellow-500" />
            Key Strengths
          </label>
          <textarea
            value={formData.strengths}
            onChange={(e) => handleInputChange('strengths', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="4"
            placeholder="What did the candidate excel at? What impressed you most?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <TrendingUp className="w-4 h-4 inline mr-1 text-green-500" />
            Areas for Improvement
          </label>
          <textarea
            value={formData.areasForImprovement}
            onChange={(e) => handleInputChange('areasForImprovement', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="4"
            placeholder="What areas could the candidate improve? Any concerns?"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <MessageSquare className="w-4 h-4 inline mr-1 text-blue-500" />
            Detailed Assessment
          </label>
          <textarea
            value={formData.detailedFeedback}
            onChange={(e) => handleInputChange('detailedFeedback', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="6"
            placeholder="Provide a comprehensive assessment of the candidate's performance, including specific examples and observations..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Award className="w-4 h-4 inline mr-1 text-purple-500" />
            Final Recommendation
          </label>
          <textarea
            value={formData.recommendation}
            onChange={(e) => handleInputChange('recommendation', e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="3"
            placeholder="Summarize your final recommendation and any additional notes..."
          />
        </div>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-8">
      <div className="text-center">
        <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Final Review</h3>
        <p className="text-gray-600">Review your feedback before submitting</p>
      </div>

      <div className="bg-gray-50 rounded-xl p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Candidate Information</h4>
            <div className="space-y-2 text-sm">
              <div><span className="font-medium">Name:</span> {candidateName}</div>
              <div><span className="font-medium">Email:</span> {candidateEmail}</div>
              <div><span className="font-medium">Position:</span> {jobTitle}</div>
              <div><span className="font-medium">Round:</span> {roundName}</div>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Overall Assessment</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span>Overall Rating:</span>
                <div className="flex items-center">
                  {renderStars(formData.overallRating, () => {}, 'text-lg')}
                </div>
              </div>
              <div><span className="font-medium">Decision:</span> {decisionOptions.find(d => d.value === formData.decision)?.label}</div>
              <div><span className="font-medium">Team Fit:</span> {teamFitOptions.find(t => t.value === formData.teamFit)?.label}</div>
            </div>
          </div>
        </div>

        {formData.strengths && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Key Strengths</h4>
            <p className="text-sm text-gray-700 bg-white p-3 rounded-lg">{formData.strengths}</p>
          </div>
        )}

        {formData.areasForImprovement && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Areas for Improvement</h4>
            <p className="text-sm text-gray-700 bg-white p-3 rounded-lg">{formData.areasForImprovement}</p>
          </div>
        )}

        {formData.recommendation && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Final Recommendation</h4>
            <p className="text-sm text-gray-700 bg-white p-3 rounded-lg">{formData.recommendation}</p>
          </div>
        )}
      </div>
    </div>
  );

  if (success) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4 text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Feedback Submitted!</h3>
          <p className="text-gray-600 mb-4">Thank you for providing your feedback. The candidate will be notified.</p>
          <div className="animate-pulse">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">Manager Feedback</h2>
              <p className="text-blue-100 mt-1">{candidateName} - {jobTitle}</p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm text-blue-100 mb-2">
              <span>Step {currentStep} of {totalSteps}</span>
              <span>{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
            </div>
            <div className="w-full bg-blue-500 rounded-full h-2">
              <div 
                className="bg-white h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-700">{error}</span>
              </div>
            </div>
          )}

          {currentStep === 1 && renderStep1()}
          {currentStep === 2 && renderStep2()}
          {currentStep === 3 && renderStep3()}
          {currentStep === 4 && renderStep4()}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
          <button
            onClick={prevStep}
            disabled={currentStep === 1}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Previous
          </button>

          <div className="flex space-x-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`w-3 h-3 rounded-full transition-colors ${
                  step <= currentStep ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          {currentStep < totalSteps ? (
            <button
              onClick={nextStep}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center"
            >
              Next
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Submit Feedback
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ManagerFeedbackForm;
