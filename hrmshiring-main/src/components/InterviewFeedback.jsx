import React, { useState, useEffect } from 'react';
import { formatDateForDisplay } from '../utils/dateUtils';
import {
  Star,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  User,
  Calendar,
  Clock,
  Save,
  Send,
  ThumbsUp,
  ThumbsDown,
  Minus
} from 'lucide-react';

const InterviewFeedback = ({ interviewId, interviewerId, onFeedbackSubmitted }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [interview, setInterview] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const [feedback, setFeedback] = useState({
    technical_skills_rating: 0,
    communication_skills_rating: 0,
    problem_solving_rating: 0,
    cultural_fit_rating: 0,
    overall_rating: 0,
    strengths: '',
    areas_of_improvement: '',
    technical_assessment: '',
    behavioral_assessment: '',
    decision: '',
    recommendation_notes: ''
  });

  const decisionOptions = [
    { value: 'strong_hire', label: 'Strong Hire', icon: ThumbsUp, color: 'text-green-600' },
    { value: 'hire', label: 'Hire', icon: CheckCircle, color: 'text-green-500' },
    { value: 'maybe', label: 'Maybe', icon: Minus, color: 'text-yellow-500' },
    { value: 'reject', label: 'Reject', icon: ThumbsDown, color: 'text-red-500' },
    { value: 'strong_reject', label: 'Strong Reject', icon: AlertCircle, color: 'text-red-600' }
  ];

  useEffect(() => {
    if (interviewId) {
      fetchInterviewDetails();
    }
  }, [interviewId]);

  const fetchInterviewDetails = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/interviews/schedule/${interviewId}`, {
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const interviewData = data.data?.interviews?.find(i => i.id === interviewId);
        if (interviewData) {
          setInterview(interviewData);
        }
      }
    } catch (err) {
      console.error('Error fetching interview details:', err);
    }
  };

  const handleSubmitFeedback = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:5000/api/interviews/feedback', {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          interview_id: interviewId,
          interviewer_id: interviewerId,
          candidate_id: interview?.candidate_id,
          round_id: interview?.round_id,
          ...feedback
        })
      });

      if (response.ok) {
        setShowForm(false);
        setFeedback({
          technical_skills_rating: 0,
          communication_skills_rating: 0,
          problem_solving_rating: 0,
          cultural_fit_rating: 0,
          overall_rating: 0,
          strengths: '',
          areas_of_improvement: '',
          technical_assessment: '',
          behavioral_assessment: '',
          decision: '',
          recommendation_notes: ''
        });
        if (onFeedbackSubmitted) {
          onFeedbackSubmitted();
        }
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to submit feedback');
      }
    } catch (err) {
      setError('Error submitting feedback');
    } finally {
      setLoading(false);
    }
  };

  const RatingStars = ({ rating, onRatingChange, label }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <div className="flex items-center space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onRatingChange(star)}
            className={`p-1 rounded ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            } hover:text-yellow-400 transition-colors`}
          >
            <Star className="w-5 h-5 fill-current" />
          </button>
        ))}
        <span className="ml-2 text-sm text-gray-600">{rating}/5</span>
      </div>
    </div>
  );

  const updateRating = (field, value) => {
    setFeedback({ ...feedback, [field]: value });
    
    // Auto-calculate overall rating as average of all ratings
    const ratings = ['technical_skills_rating', 'communication_skills_rating', 'problem_solving_rating', 'cultural_fit_rating'];
    const newRatings = ratings.map(r => r === field ? value : feedback[r]);
    const average = newRatings.reduce((sum, rating) => sum + rating, 0) / newRatings.length;
    setFeedback(prev => ({ ...prev, overall_rating: Math.round(average) }));
  };

  if (!interview) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading interview details...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Interview Feedback</h3>
          <p className="text-sm text-gray-600">
            Submit feedback for {interview.applicant_name} - {interview.round_name}
          </p>
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Submit Feedback
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

      {/* Interview Details */}
      <div className="mb-6 p-4 bg-gray-50 rounded-md">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">{interview.applicant_name}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">
              {formatDateForDisplay(interview.scheduled_date)}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">{interview.scheduled_time}</span>
          </div>
        </div>
      </div>

      {showForm ? (
        <div className="space-y-6">
          {/* Rating Section */}
          <div>
            <h4 className="font-medium text-gray-900 mb-4">Candidate Ratings</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <RatingStars
                rating={feedback.technical_skills_rating}
                onRatingChange={(value) => updateRating('technical_skills_rating', value)}
                label="Technical Skills"
              />
              <RatingStars
                rating={feedback.communication_skills_rating}
                onRatingChange={(value) => updateRating('communication_skills_rating', value)}
                label="Communication Skills"
              />
              <RatingStars
                rating={feedback.problem_solving_rating}
                onRatingChange={(value) => updateRating('problem_solving_rating', value)}
                label="Problem Solving"
              />
              <RatingStars
                rating={feedback.cultural_fit_rating}
                onRatingChange={(value) => updateRating('cultural_fit_rating', value)}
                label="Cultural Fit"
              />
            </div>
            
            <div className="mt-4 p-3 bg-blue-50 rounded-md">
              <RatingStars
                rating={feedback.overall_rating}
                onRatingChange={(value) => setFeedback({ ...feedback, overall_rating: value })}
                label="Overall Rating"
              />
            </div>
          </div>

          {/* Assessment Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Technical Assessment
              </label>
              <textarea
                value={feedback.technical_assessment}
                onChange={(e) => setFeedback({ ...feedback, technical_assessment: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="4"
                placeholder="Describe the candidate's technical performance, skills demonstrated, and any technical challenges..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Behavioral Assessment
              </label>
              <textarea
                value={feedback.behavioral_assessment}
                onChange={(e) => setFeedback({ ...feedback, behavioral_assessment: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="4"
                placeholder="Describe the candidate's behavior, communication style, and how they handled questions..."
              />
            </div>
          </div>

          {/* Strengths and Areas of Improvement */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Strengths
              </label>
              <textarea
                value={feedback.strengths}
                onChange={(e) => setFeedback({ ...feedback, strengths: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="3"
                placeholder="What are the candidate's main strengths and positive qualities?"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Areas of Improvement
              </label>
              <textarea
                value={feedback.areas_of_improvement}
                onChange={(e) => setFeedback({ ...feedback, areas_of_improvement: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows="3"
                placeholder="What areas could the candidate improve upon?"
              />
            </div>
          </div>

          {/* Decision Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Hiring Decision *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {decisionOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setFeedback({ ...feedback, decision: option.value })}
                    className={`p-3 border-2 rounded-md text-center transition-colors ${
                      feedback.decision === option.value
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className={`w-6 h-6 mx-auto mb-2 ${option.color}`} />
                    <span className="text-sm font-medium text-gray-700">{option.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Recommendation Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recommendation Notes
            </label>
            <textarea
              value={feedback.recommendation_notes}
              onChange={(e) => setFeedback({ ...feedback, recommendation_notes: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows="3"
              placeholder="Additional notes, recommendations, or final thoughts about the candidate..."
            />
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setShowForm(false);
                setFeedback({
                  technical_skills_rating: 0,
                  communication_skills_rating: 0,
                  problem_solving_rating: 0,
                  cultural_fit_rating: 0,
                  overall_rating: 0,
                  strengths: '',
                  areas_of_improvement: '',
                  technical_assessment: '',
                  behavioral_assessment: '',
                  decision: '',
                  recommendation_notes: ''
                });
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmitFeedback}
              disabled={
                !feedback.decision ||
                feedback.overall_rating === 0 ||
                loading
              }
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
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
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No feedback submitted yet.</p>
          <p className="text-sm text-gray-500 mt-1">Click "Submit Feedback" to provide your assessment.</p>
        </div>
      )}
    </div>
  );
};

export default InterviewFeedback;
