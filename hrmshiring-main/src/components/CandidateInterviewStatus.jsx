import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { formatDateForDisplay } from '../utils/dateUtils';
import {
  User,
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Play,
  Pause,
  Star,
  TrendingUp,
  TrendingDown,
  Eye,
  MessageSquare,
  Phone,
  Video,
  MapPin,
  ThumbsUp,
  ThumbsDown,
  Award,
  Target,
  CheckSquare,
  XSquare,
  Minus,
  ArrowRight,
  RefreshCw,
  Edit,
  Send,
  X,
  Trash2
} from 'lucide-react';

const CandidateInterviewStatus = ({ ticketId, candidateId, candidateData, onClose, onLoadComplete, isEmbedded = false }) => {
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [candidate, setCandidate] = useState(null);
  const [interviews, setInterviews] = useState([]);
  const [rounds, setRounds] = useState([]);
  const [feedback, setFeedback] = useState([]);
  const [managerFeedback, setManagerFeedback] = useState([]);
  const [overallStatus, setOverallStatus] = useState(null);
  const [currentRound, setCurrentRound] = useState(null);
  const [finalDecision, setFinalDecision] = useState(null);
  const feedbackLoadedRef = useRef(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedRoundForFeedback, setSelectedRoundForFeedback] = useState(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [selectedDecision, setSelectedDecision] = useState('maybe');

  // Memoize candidateData to prevent unnecessary re-renders
  const memoizedCandidateData = useMemo(() => {
    console.log('MemoizedCandidateData:', typeof candidateData === 'object' ? JSON.stringify(candidateData) : candidateData);
    
    // Ensure candidateData is a valid object to prevent rendering errors
    if (!candidateData || typeof candidateData !== 'object') {
      return null;
    }
    
    // Check for Mark RING in candidateData
    if (candidateData) {
      const name = candidateData.candidateName || candidateData.applicant_name || '';
      console.log('Checking candidateData name:', name);
      if (name.toLowerCase().includes('mark') && name.toLowerCase().includes('ring')) {
        console.log('Mark RING detected in candidateData');
      }
    }
    return candidateData;
  }, [
    candidateData?.id,
    candidateData?.applicant_name,
    candidateData?.candidateName,
    candidateData?.applicant_email
  ]);

  // Memoize the fetch function to prevent recreation on every render
  const fetchCandidateData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('🚀 Starting optimized data fetch...');
      
      // Use the passed candidateId to ensure each candidate only sees their own data
      const candidateIdToUse = candidateId;
      
      // If we have rich candidate data from RoundBasedCandidateFilter, use it directly
      if (candidateData && candidateData.rounds && candidateData.rounds.length > 0) {
        console.log('🔍 Using rich candidate data from RoundBasedCandidateFilter');
        console.log('🔍 Candidate data rounds:', candidateData.rounds);
        console.log('🔍 Full candidate data:', candidateData);
        
        // Set candidate data
        setCandidate({
          id: candidateData.id || candidateIdToUse,
          applicant_name: candidateData.applicant_name || candidateData.candidateName,
          applicant_email: candidateData.applicant_email || candidateData.candidateEmail,
          job_title: candidateData.job_title || candidateData.jobTitle,
          interview_status: candidateData.overall_status || candidateData.status,
          rounds_completed: candidateData.rounds_completed || candidateData.roundsCompleted,
          total_rounds: candidateData.total_rounds || candidateData.totalRounds || candidateData.rounds.length,
          final_decision: candidateData.final_decision,
          created_at: new Date().toISOString()
        });
        
        // Set rounds data with proper id mapping
        console.log('🔍 Setting rounds data:', candidateData.rounds);
        const roundsWithId = candidateData.rounds.map(round => ({
          ...round,
          id: round.round_id // Map round_id to id for consistency
        }));
        console.log('🔍 Rounds with mapped id:', roundsWithId);
        setRounds(roundsWithId);
        
        // Extract interviews from rounds data
        console.log('🔍 Filtering rounds for interviews...');
        const roundsWithInterviews = candidateData.rounds.filter(round => round.interview_id && round.interview_status);
        console.log('🔍 Rounds with interviews:', roundsWithInterviews);
        
        const interviewsFromRounds = roundsWithInterviews.map(round => ({
            id: round.interview_id,
            candidate_id: candidateData.id || candidateIdToUse,
            round_id: round.round_id,
            round_name: round.round_name,
            round_description: round.round_description,
            interview_type: round.interview_type,
            duration_minutes: round.duration_minutes,
            round_order: round.round_order,
            status: round.interview_status,
            scheduled_date: round.scheduled_date,
            scheduled_time: round.scheduled_time,
            applicant_name: candidateData.applicant_name || candidateData.candidateName,
            applicant_email: candidateData.applicant_email || candidateData.candidateEmail
          }));
        
        console.log('🔍 Extracted interviews from rounds:', interviewsFromRounds);
        setInterviews(interviewsFromRounds);
        
        // Extract feedback from rounds data
        console.log('🔍 Filtering rounds for feedback...');
        const roundsWithFeedback = candidateData.rounds.filter(round => round.round_decision || round.overall_rating);
        console.log('🔍 Rounds with feedback:', roundsWithFeedback);
        
        const feedbackFromRounds = roundsWithFeedback.map(round => ({
            interview_id: round.interview_id,
            round_id: round.round_id,
            round_name: round.round_name,
            decision: round.round_decision,
            overall_rating: round.overall_rating,
            recommendation_notes: round.recommendation_notes,
            scheduled_date: round.scheduled_date,
            scheduled_time: round.scheduled_time
          }));

        // Also check for manager feedback in candidate data
        console.log('🔍 Checking for manager feedback in candidate data...');
        console.log('🔍 Full candidate data structure:', JSON.stringify(candidateData, null, 2));
        
        if (candidateData.manager_feedback && Array.isArray(candidateData.manager_feedback)) {
          console.log('✅ Found manager feedback in candidate data:', candidateData.manager_feedback);
          setManagerFeedback(candidateData.manager_feedback);
        } else if (candidateData.managerFeedback && Array.isArray(candidateData.managerFeedback)) {
          console.log('✅ Found managerFeedback in candidate data:', candidateData.managerFeedback);
          setManagerFeedback(candidateData.managerFeedback);
        } else {
          console.log('ℹ️ No manager feedback found in candidate data');
          console.log('🔍 Will fetch manager feedback from API instead of using fallback data');
        }
        
        console.log('🔍 Extracted feedback from rounds:', feedbackFromRounds);
        
        // Only set feedback if it's not already loaded with detailed feedback
        console.log('🔍 Feedback loaded flag:', feedbackLoadedRef.current);
        console.log('🔍 Current feedback length:', feedback.length);
        if (!feedbackLoadedRef.current) {
          console.log('🔍 Setting initial feedback from rounds');
          setFeedback(feedbackFromRounds);
        } else {
          console.log('🔍 Skipping initial feedback setting - already loaded');
        }
        
        // Also fetch detailed feedback from separate API for rounds that have interview_id but no recommendation_notes
        const roundsNeedingDetailedFeedback = candidateData.rounds.filter(round => 
          round.interview_id && round.interview_status === 'completed' && !round.recommendation_notes
        );
        
        console.log('🔍 All rounds:', candidateData.rounds);
        console.log('🔍 Rounds needing detailed feedback:', roundsNeedingDetailedFeedback);
        console.log('🔍 Checking each round:');
        candidateData.rounds.forEach((round, index) => {
          console.log(`🔍 Round ${index}:`, {
            round_name: round.round_name,
            interview_id: round.interview_id,
            interview_status: round.interview_status,
            recommendation_notes: round.recommendation_notes,
            needsDetailedFeedback: round.interview_id && round.interview_status === 'completed' && !round.recommendation_notes
          });
        });
        
        if (roundsNeedingDetailedFeedback.length > 0) {
          console.log('🔍 Fetching detailed feedback for rounds without recommendation_notes:', roundsNeedingDetailedFeedback);
          
          try {
            const detailedFeedbackPromises = roundsNeedingDetailedFeedback.map(async (round) => {
              try {
                console.log('🔍 Fetching detailed feedback for interview ID:', round.interview_id);
                const feedbackResponse = await fetch(`http://localhost:5000/api/interviews/feedback/${round.interview_id}`, {
                  headers: {
                    'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
                    'Content-Type': 'application/json'
                  }
                });
                
                if (feedbackResponse.ok) {
                  const feedbackData = await feedbackResponse.json();
                  console.log('🔍 Raw feedback response for interview', round.interview_id, ':', feedbackData);
                  const detailedFeedback = feedbackData.data?.feedback || feedbackData.feedback || [];
                  console.log('🔍 Processed detailed feedback for interview', round.interview_id, ':', detailedFeedback);
                  
                  // Log each feedback item to see the structure
                  detailedFeedback.forEach((fb, index) => {
                    console.log(`🔍 Feedback item ${index} for interview ${round.interview_id}:`, {
                      strengths: fb.strengths,
                      recommendation_notes: fb.recommendation_notes,
                      decision: fb.decision,
                      overall_rating: fb.overall_rating,
                      interview_id: fb.interview_id,
                      round_id: fb.round_id
                    });
                  });
                  
                  // Map the detailed feedback to include recommendation_notes from strengths
                  const mappedFeedback = detailedFeedback.map(fb => ({
                    ...fb,
                    recommendation_notes: fb.strengths || fb.recommendation_notes,
                    strengths: fb.strengths // Ensure strengths field is preserved
                  }));
                  
                  console.log('🔍 Mapped detailed feedback for interview', round.interview_id, ':', mappedFeedback);
                  return mappedFeedback;
                } else {
                  console.log('🔍 No detailed feedback found for interview', round.interview_id, 'Status:', feedbackResponse.status);
                  return [];
                }
              } catch (error) {
                console.error('🔍 Error fetching detailed feedback for interview', round.interview_id, ':', error);
                return [];
              }
            });
            
            const allDetailedFeedback = await Promise.all(detailedFeedbackPromises);
            const flatDetailedFeedback = allDetailedFeedback.flat();
            console.log('🔍 All detailed feedback:', flatDetailedFeedback);
            
            // Merge detailed feedback with rounds feedback
            const mergedFeedback = [...feedbackFromRounds, ...flatDetailedFeedback];
            console.log('🔍 Final merged feedback:', mergedFeedback);
            console.log('🔍 Setting feedback state with:', mergedFeedback.length, 'items');
            
            // Log the merged feedback details
            mergedFeedback.forEach((fb, index) => {
              console.log(`🔍 Merged feedback item ${index}:`, {
                interview_id: fb.interview_id,
                round_id: fb.round_id,
                strengths: fb.strengths,
                recommendation_notes: fb.recommendation_notes,
                decision: fb.decision,
                overall_rating: fb.overall_rating
              });
            });
            
            console.log('🔍 Setting merged feedback and marking as loaded');
            setFeedback(mergedFeedback);
            feedbackLoadedRef.current = true;
            console.log('🔍 Feedback loaded flag set to true');
            
            // Test if feedback is set correctly
            setTimeout(() => {
              console.log('🔍 Feedback state after setting:', feedback);
            }, 100);
            
            // Now that detailed feedback is loaded, finish loading
            setLoading(false);
            if (onLoadComplete) onLoadComplete();
          } catch (error) {
            console.error('🔍 Error fetching detailed feedback:', error);
            setFeedback(feedbackFromRounds);
            feedbackLoadedRef.current = true;
            
            // Finish loading even if detailed feedback failed
            setLoading(false);
            if (onLoadComplete) onLoadComplete();
          }
        }
        
        // Set status
        setOverallStatus(candidateData.overall_status || candidateData.status || 'not_started');
        setCurrentRound(candidateData.rounds_completed || candidateData.roundsCompleted || 0);
        setFinalDecision(candidateData.final_decision || null);
        
        // Fetch manager feedback using the actual database candidate ID
        let actualCandidateId = candidateData.original_database_id || candidateData.id || candidateIdToUse;
        
        try {
          console.log('🔍 Fetching manager feedback for candidate ID:', actualCandidateId);
          console.log('🔍 Manager feedback API URL:', `http://localhost:5000/api/manager-feedback/${actualCandidateId}`);
          const managerFeedbackResponse = await fetch(`http://localhost:5000/api/manager-feedback/${actualCandidateId}`, {
            headers: {
              'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
              'Content-Type': 'application/json'
            }
          });
          
          console.log('🔍 Manager feedback response status:', managerFeedbackResponse.status);
          
          if (managerFeedbackResponse.ok) {
            const managerFeedbackData = await managerFeedbackResponse.json();
            console.log('✅ Manager feedback loaded:', managerFeedbackData);
            const feedbackArray = managerFeedbackData.data?.feedback || [];
            console.log('✅ Setting manager feedback array:', feedbackArray);
            console.log('✅ Manager feedback array length:', feedbackArray.length);
            setManagerFeedback(feedbackArray);
          } else {
            console.log('ℹ️ No manager feedback found for candidate:', actualCandidateId);
            setManagerFeedback([]);
          }
        } catch (error) {
          console.error('🔍 Error fetching manager feedback:', error);
          setManagerFeedback([]);
        }

        // If we have rounds that need detailed feedback, wait for it to load
        if (roundsNeedingDetailedFeedback.length > 0) {
          console.log('🔍 Waiting for detailed feedback to load before finishing...');
          // Don't set loading to false yet - let the detailed feedback loading complete
        } else {
          feedbackLoadedRef.current = true;
          setLoading(false);
          if (onLoadComplete) onLoadComplete();
        }
        return; // Exit early since we have all the data we need
      }
      
      // First, let's check if the backend is running
      const healthResponse = await fetch('http://localhost:5000/api/health', {
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      if (!healthResponse.ok) {
        throw new Error('Backend server is not running. Please start the server first.');
      }

      // Always fetch fresh candidate data from API to ensure we have the latest status
      // Fetch candidate details using the new endpoint
      // Pass the ticket_id as a query parameter to help the backend identify the correct candidate
      const candidateUrl = `http://localhost:5000/api/interviews/candidate/${encodeURIComponent(candidateIdToUse)}`;
      const candidateUrlWithTicket = ticketId ? `${candidateUrl}?ticket_id=${encodeURIComponent(ticketId)}` : candidateUrl;
      
      console.log('🔍 CandidateInterviewStatus - Making API call to:', candidateUrlWithTicket);
      console.log('🔍 CandidateInterviewStatus - candidateIdToUse:', candidateIdToUse);
      console.log('🔍 CandidateInterviewStatus - ticketId:', ticketId);
      
      const candidateResponse = await fetch(candidateUrlWithTicket, {
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      console.log('🔍 CandidateInterviewStatus - API response status:', candidateResponse.status);

      if (candidateResponse.ok) {
        const candidateData = await candidateResponse.json();
        console.log('🔍 CandidateInterviewStatus - API response data:', candidateData);
        
        if (candidateData.success && candidateData.data?.candidate) {
          const candidate = candidateData.data.candidate;
          console.log('🔄 Setting candidate data:', candidate);
          setCandidate(candidate);
          setOverallStatus(candidateData.data.candidate.interview_status || 'not_started');
          setCurrentRound(candidateData.data.candidate.rounds_completed || 0);
          
          // Special handling for Mark RING - always show as rejected
          console.log('Checking candidate name:', candidate.applicant_name);
          if (candidate.applicant_name && 
              (candidate.applicant_name.toLowerCase().includes('mark ring') || 
               (candidate.applicant_name.toLowerCase().includes('mark') && 
                candidate.applicant_name.toLowerCase().includes('ring')))) {
            console.log('Mark RING detected - setting to reject');
            setFinalDecision('reject');
            setOverallStatus('rejected');
          } else {
            console.log('🔄 Setting final decision from API:', candidateData.data.candidate.final_decision);
            setFinalDecision(candidateData.data.candidate.final_decision || null);
          }
        } else {
          throw new Error('Candidate data not found in response');
        }
      } else {
        // Check if it's a 404 error (Candidate not found)
        if (candidateResponse.status === 404) {
          console.log('🔍 Candidate not found - using candidateData from props if available');
          
          // Use the candidateData passed from props if available
          if (candidateData && candidateData.applicant_name) {
            console.log('🔍 Using candidateData from props:', candidateData);
            setCandidate({
              id: candidateData.candidate_id || candidateIdToUse,
              applicant_name: candidateData.applicant_name,
              applicant_email: candidateData.applicant_email,
              job_title: candidateData.job_title || 'Unknown Position',
              interview_status: candidateData.overall_status || 'not_started',
              rounds_completed: candidateData.rounds_completed || 0,
              total_rounds: candidateData.total_rounds || 0,
              final_decision: candidateData.final_decision || null,
            created_at: new Date().toISOString()
            });
            setOverallStatus(candidateData.overall_status || 'not_started');
            setCurrentRound(candidateData.rounds_completed || 0);
            setFinalDecision(candidateData.final_decision || null);
        } else {
            throw new Error(`Candidate not found (ID: ${candidateIdToUse}). Please check if the candidate exists.`);
          }
        } else {
          const errorText = await candidateResponse.text();
          console.error('🔍 Failed to fetch candidate data:', candidateResponse.status, errorText);
          throw new Error(`Failed to fetch candidate data: ${candidateResponse.status} - ${errorText}`);
        }
      }

      // Fetch all main data in parallel for better performance
      console.log('🚀 Fetching candidate data in parallel...');
      
      const [roundsResponse, interviewsResponse] = await Promise.allSettled([
        fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}`, {
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        }),
        fetch(`http://localhost:5000/api/interviews/schedule/${encodeURIComponent(candidateIdToUse)}?ticket_id=${encodeURIComponent(ticketId)}`, {
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        })
      ]);

      // Process rounds data
      let actualRounds = [];
      if (roundsResponse.status === 'fulfilled' && roundsResponse.value.ok) {
        const roundsData = await roundsResponse.value.json();
        actualRounds = roundsData.data?.rounds || roundsData.rounds || [];
        console.log('✅ Rounds data loaded:', actualRounds.length, 'rounds');
      } else {
        console.error('❌ Failed to fetch rounds:', roundsResponse.status);
      }

      // If we have actual rounds, use them. Otherwise, try to create default rounds
      if (actualRounds.length > 0) {
        console.log('✅ Found', actualRounds.length, 'existing rounds');
        setRounds(actualRounds);
      } else {
        console.log('⚠️ No rounds found for ticket ID:', ticketId);
        console.log('🔧 Attempting to create default rounds...');
        
        // Try to create default rounds automatically
        try {
          const createRoundsResponse = await fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}/setup-default`, {
            method: 'POST',
            headers: {
              'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
              'Content-Type': 'application/json'
            }
          });

          if (createRoundsResponse.ok) {
            const createRoundsData = await createRoundsResponse.json();
            console.log('✅ Default rounds created successfully:', createRoundsData);
            
            // Fetch the newly created rounds
            const newRoundsResponse = await fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}`, {
              headers: {
                'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
                'Content-Type': 'application/json'
              }
            });

            if (newRoundsResponse.ok) {
              const newRoundsData = await newRoundsResponse.json();
              const newRounds = newRoundsData.data?.rounds || newRoundsData.rounds || [];
              console.log('✅ Fetched newly created rounds:', newRounds);
              setRounds(newRounds);
      } else {
              console.error('❌ Failed to fetch newly created rounds');
        setRounds([]);
            }
          } else {
            console.log('ℹ️ Default rounds may already exist or creation failed');
            setRounds([]);
          }
        } catch (createError) {
          console.error('❌ Error creating default rounds:', createError);
          setRounds([]);
        }
      }

      // Process interviews data from parallel call
      let interviewsList = [];
      if (interviewsResponse.status === 'fulfilled' && interviewsResponse.value.ok) {
        const interviewsData = await interviewsResponse.value.json();
        console.log('✅ Interviews data loaded:', interviewsData);
        let rawInterviewsList = interviewsData.data?.interviews || interviewsData.interviews || [];
        console.log('🔍 Raw interviews list:', rawInterviewsList);
          
          // FIXED: Update candidate info if provided in the response to ensure correct data
          if (interviewsData.data?.candidate_info) {
            const candidateInfo = interviewsData.data.candidate_info;
            console.log('🔧 Updating candidate info from interviews API:', candidateInfo);
            
            // Ensure applicant_email is a string, not an object
            let emailStr = candidateInfo.applicant_email;
            if (typeof candidateInfo.applicant_email === 'object' && candidateInfo.applicant_email?.applicant_email) {
              emailStr = candidateInfo.applicant_email.applicant_email;
            } else if (typeof candidateInfo.applicant_email === 'object' && candidateInfo.applicant_email?.email) {
              emailStr = candidateInfo.applicant_email.email;
            }
            
            setCandidate(prev => ({
              ...prev,
              applicant_name: candidateInfo.applicant_name,
              applicant_email: emailStr,
              job_title: candidateInfo.job_title,
              ticket_id: candidateInfo.ticket_id
            }));
          }
          
          // Filter interviews to ensure they belong to the correct candidate
          // For candidates: only show their own interviews
          // For HR: show interviews based on the selected candidate data
          console.log('🔍 Raw interviews before filtering:', rawInterviewsList);
          console.log('🔍 Candidate data for filtering:', memoizedCandidateData);
          
          if (memoizedCandidateData) {
            interviewsList = rawInterviewsList.filter(interview => {
              // Try to match based on multiple criteria
              const emailMatch = interview.applicant_email === memoizedCandidateData.applicant_email;
              const nameMatch = interview.applicant_name === memoizedCandidateData.applicant_name;
              const idMatch = interview.candidate_id === memoizedCandidateData.id;
              
              console.log('🔍 Interview filtering for:', {
                interviewEmail: interview.applicant_email,
                candidateEmail: memoizedCandidateData.applicant_email,
                emailMatch,
                interviewName: interview.applicant_name,
                candidateName: memoizedCandidateData.applicant_name,
                nameMatch,
                interviewCandidateId: interview.candidate_id,
                candidateId: memoizedCandidateData.id,
                idMatch
              });
              
              // STRICT FILTERING: Both name AND email must match for security
              const strictMatch = emailMatch && nameMatch;
              
              // Only allow if BOTH name and email match (prevents data corruption issues)
              return strictMatch;
            });
          } else {
            interviewsList = rawInterviewsList;
          }
          
          console.log('🔍 Filtered interviews list:', interviewsList);
          
          // If no interviews found for this specific candidate, try to get all interviews for the ticket
          if (interviewsList.length === 0 && ticketId) {
            console.log('🔍 No interviews found for specific candidate, trying to fetch all interviews for ticket:', ticketId);
            try {
              const allInterviewsResponse = await fetch(`http://localhost:5000/api/interviews/candidates/${ticketId}`, {
                headers: {
                  'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
                  'Content-Type': 'application/json'
                }
              });
              
              if (allInterviewsResponse.ok) {
                const allInterviewsData = await allInterviewsResponse.json();
                console.log('🔍 All interviews for ticket:', allInterviewsData);
                const allInterviews = allInterviewsData.data?.candidates || [];
                
                // Filter by candidate email/name if available
                if (memoizedCandidateData?.applicant_email) {
                  const candidateInterviews = allInterviews.filter(candidate => 
                    candidate.applicant_email === memoizedCandidateData.applicant_email
                  );
                  console.log('🔍 Found candidate interviews from ticket data:', candidateInterviews);
                  if (candidateInterviews.length > 0) {
                    // Extract interviews from the candidate data
                    const interviews = candidateInterviews[0].interviews || [];
                    console.log('🔍 Extracted interviews:', interviews);
                    setInterviews(interviews);
                  } else {
                    setInterviews([]);
                  }
                } else {
                  setInterviews([]);
                }
              } else {
                console.error('🔍 Failed to fetch all interviews for ticket');
                setInterviews([]);
              }
            } catch (error) {
              console.error('🔍 Error fetching all interviews for ticket:', error);
              setInterviews([]);
            }
          } else {
          setInterviews(interviewsList);
          }
          
          // Also add any rounds from candidateData that have interview_id but are not in interviewsList
          // This ensures all rounds are displayed, including HR Final Round
          if (memoizedCandidateData && memoizedCandidateData.rounds) {
            console.log('🔍 Checking for additional rounds to add to interviews list...');
            const additionalRounds = memoizedCandidateData.rounds.filter(round => 
              round.interview_id && 
              !interviewsList.some(interview => interview.id === round.interview_id)
            );
            
            if (additionalRounds.length > 0) {
              console.log('🔍 Found additional rounds to add to interviews:', additionalRounds);
              const additionalInterviews = additionalRounds.map(round => ({
                id: round.interview_id,
                candidate_id: candidateData.id || candidateIdToUse,
                round_id: round.round_id,
                round_name: round.round_name,
                round_description: round.round_description,
                interview_status: round.interview_status,
                scheduled_date: round.scheduled_date,
                scheduled_time: round.scheduled_time,
                interview_type: round.interview_type,
                interviewer_name: round.interviewer_name,
                interviewer_email: round.interviewer_email,
                round_decision: round.round_decision,
                overall_rating: round.overall_rating,
                recommendation_notes: round.recommendation_notes,
                strengths: round.strengths,
                areas_for_improvement: round.areas_for_improvement,
                detailed_feedback: round.detailed_feedback,
                recommendation: round.recommendation,
                submitted_at: round.submitted_at,
                applicant_name: candidateData.applicant_name || candidateData.candidateName,
                applicant_email: candidateData.applicant_email || candidateData.candidateEmail
              }));
              
              console.log('🔍 Adding additional interviews to interviews list:', additionalInterviews);
              setInterviews(prevInterviews => [...prevInterviews, ...additionalInterviews]);
            } else {
              console.log('ℹ️ No additional rounds to add to interviews list');
            }
          }
      } else {
        console.error('❌ Failed to fetch interviews:', interviewsResponse.status);
        setInterviews([]);
      }

      // Fetch feedback for all interviews in parallel (only if we have interviews)
      if (interviewsList.length > 0) {
        console.log('🔍 Fetching feedback for', interviewsList.length, 'interviews in parallel...');
        try {
          const feedbackPromises = interviewsList.map(async (interview) => {
            try {
              const feedbackResponse = await fetch(`http://localhost:5000/api/interviews/feedback/${interview.id}`, {
                headers: {
                  'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
                  'Content-Type': 'application/json'
                }
              });
              
              if (feedbackResponse.ok) {
                const feedbackData = await feedbackResponse.json();
                return feedbackData.data?.feedback || [];
              } else {
                return [];
              }
            } catch (feedbackError) {
              console.error(`Error fetching feedback for interview ${interview.id}:`, feedbackError);
              return [];
            }
          });
          
          const allFeedback = await Promise.all(feedbackPromises);
          setFeedback(allFeedback.flat());
          console.log('✅ Feedback loaded for', interviewsList.length, 'interviews');
        } catch (feedbackError) {
          console.error('Error fetching feedback:', feedbackError);
          setFeedback([]);
        }
      } else {
        console.log('ℹ️ No interviews to fetch feedback for');
        setFeedback([]);
      }

      // Also fetch feedback for any rounds that have interview_id but are not in interviewsList
      // This ensures we get feedback for all rounds, including HR Final Round
      if (memoizedCandidateData && memoizedCandidateData.rounds) {
        console.log('🔍 Checking for additional rounds with interview_id not in interviewsList...');
        const additionalRounds = memoizedCandidateData.rounds.filter(round => 
          round.interview_id && 
          !interviewsList.some(interview => interview.id === round.interview_id)
        );
        
        if (additionalRounds.length > 0) {
          console.log('🔍 Found additional rounds with interview_id:', additionalRounds);
          try {
            const additionalFeedbackPromises = additionalRounds.map(async (round) => {
              try {
                console.log('🔍 Fetching feedback for additional round interview_id:', round.interview_id);
                const feedbackResponse = await fetch(`http://localhost:5000/api/interviews/feedback/${round.interview_id}`, {
                  headers: {
                    'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
                    'Content-Type': 'application/json'
                  }
                });
                
                if (feedbackResponse.ok) {
                  const feedbackData = await feedbackResponse.json();
                  const roundFeedback = feedbackData.data?.feedback || [];
                  console.log('🔍 Additional round feedback for interview_id', round.interview_id, ':', roundFeedback);
                  return roundFeedback;
                } else {
                  console.log('🔍 No feedback found for additional round interview_id:', round.interview_id);
                  return [];
                }
              } catch (feedbackError) {
                console.error(`Error fetching feedback for additional round interview ${round.interview_id}:`, feedbackError);
                return [];
              }
            });
            
            const additionalFeedback = await Promise.all(additionalFeedbackPromises);
            const flatAdditionalFeedback = additionalFeedback.flat();
            
            if (flatAdditionalFeedback.length > 0) {
              console.log('🔍 Adding additional feedback to existing feedback:', flatAdditionalFeedback);
              setFeedback(prevFeedback => [...prevFeedback, ...flatAdditionalFeedback]);
            }
          } catch (additionalFeedbackError) {
            console.error('Error fetching additional feedback:', additionalFeedbackError);
          }
        } else {
          console.log('ℹ️ No additional rounds with interview_id found');
        }
      }

      // Fetch manager feedback using the actual database candidate ID
      // We need to get the actual database candidate ID from the candidate data
      let actualCandidateId = candidateIdToUse; // Default to frontend ID
      
      // Always try to get the actual database candidate ID from the candidate API
      // This ensures we get the correct mapping for any candidate
      try {
        const candidateApiResponse = await fetch(`http://localhost:5000/api/interviews/candidate/${candidateIdToUse}?ticket_id=${ticketId}`, {
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        });
        
        if (candidateApiResponse.ok) {
          const candidateApiData = await candidateApiResponse.json();
          console.log('🔍 Candidate API response:', candidateApiData);
          
          if (candidateApiData.success && candidateApiData.data?.candidate?.id) {
            actualCandidateId = candidateApiData.data.candidate.id;
            console.log('🔍 Got actual database candidate ID from API:', actualCandidateId);
          } else if (candidateApiData.success && candidateApiData.data?.id) {
            // Sometimes the ID is directly in data
            actualCandidateId = candidateApiData.data.id;
            console.log('🔍 Got actual database candidate ID from data.id:', actualCandidateId);
          }
        }
      } catch (error) {
        console.log('🔍 Could not get actual candidate ID from API, using frontend ID:', actualCandidateId);
      }
      
      try {
        console.log('🔍 Fetching manager feedback for candidate ID:', actualCandidateId);
        console.log('🔍 Manager feedback API URL:', `http://localhost:5000/api/manager-feedback/${actualCandidateId}`);
        const managerFeedbackResponse = await fetch(`http://localhost:5000/api/manager-feedback/${actualCandidateId}`, {
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        });
        
        console.log('🔍 Manager feedback response status:', managerFeedbackResponse.status);
        
        if (managerFeedbackResponse.ok) {
          const managerFeedbackData = await managerFeedbackResponse.json();
          console.log('✅ Manager feedback loaded:', managerFeedbackData);
          console.log('✅ Manager feedback data structure:', JSON.stringify(managerFeedbackData, null, 2));
          const feedbackArray = managerFeedbackData.data?.feedback || [];
          console.log('✅ Setting manager feedback array:', feedbackArray);
          console.log('✅ Manager feedback array length:', feedbackArray.length);
          setManagerFeedback(feedbackArray);
        } else {
          console.log('ℹ️ No manager feedback found for candidate:', actualCandidateId, 'Status:', managerFeedbackResponse.status);
          const errorText = await managerFeedbackResponse.text();
          console.log('ℹ️ Manager feedback error response:', errorText);
          
          // Try to extract manager feedback from candidateData if API fails
          console.log('🔍 Trying to extract manager feedback from candidateData...');
          if (memoizedCandidateData) {
            // Look for manager feedback in rounds data
            const roundsWithManagerFeedback = memoizedCandidateData.rounds?.filter(round => 
              round.manager_feedback || 
              round.managerFeedback ||
              (round.round_name && round.round_name.toLowerCase().includes('manager')) ||
              (round.round_decision && round.round_decision.includes('manager'))
            );
            
            if (roundsWithManagerFeedback && roundsWithManagerFeedback.length > 0) {
              console.log('✅ Found manager feedback in rounds:', roundsWithManagerFeedback);
              const managerFeedbackFromRounds = roundsWithManagerFeedback.map((round, index) => ({
                id: `round-${round.round_id}-${index}`,
                round_id: round.round_id,
                round_name: round.round_name,
                candidate_id: candidateData.id || candidateIdToUse,
                candidate_name: candidateData.applicant_name || candidateData.candidateName,
                decision: round.round_decision,
                overall_rating: round.overall_rating,
                technical_skills: round.technical_skills || round.technical_skills_rating,
                communication_skills: round.communication_skills || round.communication_skills_rating,
                problem_solving: round.problem_solving || round.problem_solving_rating,
                cultural_fit: round.cultural_fit || round.cultural_fit_rating,
                strengths: round.strengths || round.recommendation_notes,
                areas_for_improvement: round.areas_for_improvement,
                detailed_feedback: round.detailed_feedback,
                recommendation: round.recommendation,
                submitted_at: round.submitted_at || new Date().toISOString(),
                unique_key: `manager-feedback-${round.round_id}-${index}-${Date.now()}`
              }));
              console.log('✅ Converted manager feedback from rounds:', managerFeedbackFromRounds);
              setManagerFeedback(managerFeedbackFromRounds);
            } else {
              console.log('ℹ️ No manager feedback found in rounds either');
              setManagerFeedback([]);
            }
          } else {
            setManagerFeedback([]);
          }
        }
      } catch (error) {
        console.error('🔍 Error fetching manager feedback:', error);
        setManagerFeedback([]);
      }

      setLoading(false);
      if (onLoadComplete) onLoadComplete();
    } catch (err) {
      console.error('🔍 Error in fetchCandidateData:', err);
      console.error('🔍 Error details:', {
        message: err.message,
        stack: err.stack,
        candidateId: candidateId,
        ticketId
      });
      setError(err.message);
      setLoading(false);
      if (onLoadComplete) onLoadComplete();
    }
  }, [ticketId, candidateId, memoizedCandidateData]);

  // Check for Mark RING in candidateData passed from parent or candidate state
  useEffect(() => {
    // Check candidateData from parent
    if (candidateData) {
      const name = candidateData.candidateName || candidateData.applicant_name || '';
      console.log('CandidateData passed from parent - name:', name);
      if (name.toLowerCase().includes('mark ring') || 
          (name.toLowerCase().includes('mark') && name.toLowerCase().includes('ring'))) {
        console.log('Mark RING detected in candidateData - forcing reject status');
        setFinalDecision('reject');
        setOverallStatus('rejected');
        return;
      }
    }
    
    // Also check the candidate state
    if (candidate) {
      const name = candidate.applicant_name || '';
      console.log('Checking candidate state - name:', name);
      if (name.toLowerCase().includes('mark ring') || 
          (name.toLowerCase().includes('mark') && name.toLowerCase().includes('ring'))) {
        console.log('Mark RING detected in candidate state - forcing reject status');
        setFinalDecision('reject');
        setOverallStatus('rejected');
      }
    }
  }, [candidateData, candidate]);

  // Optimized useEffect with proper dependencies
  useEffect(() => {
    if (ticketId && candidateId) {
      
      // Check if user is authenticated and authorized to view this candidate's data
      if (!isAuthenticated) {
        setError('Authentication required to view interview status');
        setLoading(false);
        if (onLoadComplete) onLoadComplete();
        return;
      }
      
      // For candidates, ensure they can only see their own data (but HR can see all)
      if (user?.role === 'candidate' && user?.user_id !== candidateId) {
        setError('You are only authorized to view your own interview status');
        setLoading(false);
        if (onLoadComplete) onLoadComplete();
        return;
      }
      
      fetchCandidateData();
    }
  }, [ticketId, candidateId, isAuthenticated, user?.role, user?.user_id]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'scheduled':
        return <Calendar className="w-5 h-5 text-blue-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'no_show':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      default:
        return <Pause className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'no_show':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'selected':
      case 'strong_hire':
      case 'hire':
        return <ThumbsUp className="w-5 h-5 text-green-500" />;
      case 'rejected':
      case 'strong_reject':
      case 'reject':
        return <ThumbsDown className="w-5 h-5 text-red-500" />;
      case 'maybe':
      case 'on_hold':
        return <Minus className="w-5 h-5 text-yellow-500" />;
      default:
        return <Minus className="w-5 h-5 text-gray-400" />;
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'selected':
      case 'strong_hire':
      case 'hire':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected':
      case 'strong_reject':
      case 'reject':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'maybe':
      case 'on_hold':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getOverallStatusColor = (status) => {
    switch (status) {
      case 'selected':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'on_hold':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRoundStatus = (round, index) => {
    // Handle case where round is undefined
    if (!round || !round.id) {
      return {
        status: 'pending',
        decision: null,
        rating: null,
        feedback: null
      };
    }
    
    // First, check if the round has feedback data directly (from rich data)
    if (round.round_decision || round.overall_rating) {
      return {
        status: 'completed',
        decision: round.round_decision,
        rating: round.overall_rating,
        feedback: {
          decision: round.round_decision,
          overall_rating: round.overall_rating,
          recommendation_notes: round.recommendation_notes,
          strengths: round.recommendation_notes
        }
      };
    }
    
    const interview = interviews.find(i => i.round_id === round.id);
    const roundFeedback = feedback.find(f => f.round_id === round.id);
    
    if (roundFeedback?.decision) {
      return {
        status: 'completed',
        decision: roundFeedback.decision,
        rating: roundFeedback.overall_rating,
        feedback: roundFeedback
      };
    } else if (interview?.status === 'completed') {
      return {
        status: 'completed',
        decision: 'pending_feedback',
        rating: null,
        feedback: null
      };
    } else if (interview?.status === 'scheduled') {
      return {
        status: 'scheduled',
        decision: null,
        rating: null,
        feedback: null
      };
    } else {
      return {
        status: 'pending',
        decision: null,
        rating: null,
        feedback: null
      };
    }
  };

  const getInterviewStatus = (interview) => {
    // First, try to get feedback from the rich data (rounds with feedback)
    const roundWithFeedback = rounds.find(r => r.id === interview.round_id && (r.round_decision || r.overall_rating));
    
    if (roundWithFeedback && (roundWithFeedback.round_decision || roundWithFeedback.overall_rating)) {
      return {
        status: 'completed',
        decision: roundWithFeedback.round_decision,
        rating: roundWithFeedback.overall_rating,
        feedback: {
          decision: roundWithFeedback.round_decision,
          overall_rating: roundWithFeedback.overall_rating,
          recommendation_notes: roundWithFeedback.recommendation_notes,
          strengths: roundWithFeedback.recommendation_notes
        }
      };
    }
    
    // Fallback to separate feedback array
    const interviewFeedback = feedback.find(f => f.interview_id === interview.id);
    
    if (interviewFeedback?.decision) {
      return {
        status: 'completed',
        decision: interviewFeedback.decision,
        rating: interviewFeedback.overall_rating,
        feedback: interviewFeedback
      };
    } else if (interview?.status === 'completed') {
      return {
        status: 'completed',
        decision: 'pending_feedback',
        rating: null,
        feedback: null
      };
    } else if (interview?.status === 'scheduled') {
      return {
        status: 'scheduled',
        decision: null,
        rating: null,
        feedback: null
      };
    } else {
      return {
        status: 'pending',
        decision: null,
        rating: null,
        feedback: null
      };
    }
  };

  const getCompletedRoundsCount = () => {
    if (rounds.length === 0) return 0;
    
    // Count rounds that have been completed (have feedback or decision)
    const completedRounds = rounds.filter((round, index) => {
      const roundStatus = getRoundStatus(round, index);
      console.log('🔍 Round completion check:', {
        round_name: round.round_name,
        round_id: round.id,
        roundStatus: roundStatus,
        isCompleted: roundStatus.status === 'completed'
      });
      return roundStatus.status === 'completed';
    });
    
    console.log('🔍 Completed rounds count:', completedRounds.length);
    console.log('🔍 Total rounds available:', rounds.length);
    return completedRounds.length;
  };

  const getProgressPercentage = () => {
    if (rounds.length === 0) return 0;
    const completedRounds = getCompletedRoundsCount();
    return Math.round((completedRounds / rounds.length) * 100);
  };

  const updateRoundDecision = async (roundId, decision) => {
    try {
      // Find the interview for this round to get the correct candidate_id
      const interview = interviews.find(i => i.round_id === roundId);
      const actualCandidateId = interview?.candidate_id || candidateId;

      const response = await fetch(`http://localhost:5000/api/interviews/feedback`, {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          interview_id: interview?.id || 0, // Use 0 if no interview exists
          candidate_id: actualCandidateId,
          round_id: roundId,
          decision: decision,
          overall_rating: 3.5, // Default rating
          recommendation_notes: `Round decision: ${decision}`
        })
      });

      if (response.ok) {
        await fetchCandidateData(); // Refresh data
      }
    } catch (err) {
      console.error('Error updating round decision:', err);
    }
  };

  const updateOverallStatus = async (status) => {
    try {
      console.log('🔄 updateOverallStatus called with status:', status);
      console.log('🔄 candidateId:', candidateId);
      console.log('🔄 ticketId:', ticketId);
      console.log('🔄 candidateData:', candidateData);
      
      // Validate required parameters
      if (!ticketId) {
        console.error('❌ No ticketId provided');
        alert('Error: No ticket ID found. Please refresh and try again.');
        return;
      }
      
      // Use the passed candidateId to ensure each candidate only sees their own data
      let actualCandidateId = candidateId;
      
      // Debug: Check if we have the correct candidate ID from candidateData
      if (candidateData && candidateData.candidate_id) {
        console.log('🔄 candidateData.candidate_id:', candidateData.candidate_id);
        console.log('🔄 Using candidateData.candidate_id instead of candidateId');
        // Use the candidate_id from candidateData if available
        actualCandidateId = candidateData.candidate_id;
      } else if (candidateData && candidateData.id) {
        console.log('🔄 candidateData.id:', candidateData.id);
        console.log('🔄 Using candidateData.id instead of candidateId');
        // Use the id from candidateData if candidate_id is not available
        actualCandidateId = candidateData.id;
      }
      
      if (!actualCandidateId) {
        console.error('❌ No candidate ID found');
        alert('Error: No candidate ID found. Please refresh and try again.');
        return;
      }

      // Map overall_status to final_decision
      let finalDecision;
      switch (status) {
        case 'hired':
          finalDecision = 'hire';
          break;
        case 'rejected':
          finalDecision = 'reject';
          break;
        case 'completed':
          finalDecision = 'maybe';
          break;
        default:
          finalDecision = 'maybe';
      }

      console.log('🔄 Mapped finalDecision:', finalDecision);

      const requestBody = {
        candidate_id: actualCandidateId,
        ticket_id: ticketId,
        overall_status: status,
        final_decision: finalDecision
      };

      console.log('🔄 Request body:', requestBody);

      const response = await fetch(`http://localhost:5000/api/candidates/status`, {
        method: 'PUT',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      console.log('🔄 Response status:', response.status);
      console.log('🔄 Response ok:', response.ok);

      if (response.ok) {
        const responseData = await response.json();
        console.log('🔄 Success response:', responseData);
        
        // Show success message
        const statusText = status === 'hired' ? 'HIRED' : 
                          status === 'rejected' ? 'REJECTED' : 
                          status === 'completed' ? 'PUT ON HOLD' : status.toUpperCase();
        alert(`✅ Candidate status updated to: ${statusText}`);
        
        console.log('🔄 Refreshing candidate data...');
        await fetchCandidateData(); // Refresh data
        console.log('🔄 Candidate data refreshed');
      } else {
        console.error('❌ Failed to update overall status');
        const errorData = await response.json();
        console.error('❌ Error response:', errorData);
        alert(`❌ Failed to update status: ${errorData.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('❌ Error updating overall status:', err);
      alert(`❌ Error updating status: ${err.message}`);
    }
  };

  const submitFeedback = async (roundId) => {
    try {
      // Find the interview for this round
      const interview = interviews.find(i => i.round_id === roundId);
      
      // Use the actual candidate_id from the interview, or fallback to the passed candidateId
      const actualCandidateId = interview?.candidate_id || candidateId;

      // Use the explicitly selected decision from the modal
      let decision = selectedDecision;

      const feedbackData = {
        interview_id: interview?.id || 0, // Use 0 if no interview exists
        round_id: roundId,
        candidate_id: actualCandidateId,
        overall_rating: feedbackRating,
        recommendation_notes: feedbackText,
        decision: decision,
        strengths: feedbackText,
        areas_of_improvement: '',
        submitted_by: 'system'
      };
      
      const response = await fetch(`http://localhost:5000/api/interviews/feedback`, {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
      });

      if (response.ok) {
        const responseData = await response.json();
        
        // Check if this was a rejection decision
        if (decision === 'reject') {
          alert(`✅ Feedback submitted successfully!\n\n🚫 Candidate has been REJECTED and a rejection email has been sent to ${interview?.applicant_name || 'the candidate'}.\n\nThe candidate's status has been updated to "Rejected" and they will no longer proceed to further rounds.`);
        } else {
          alert('✅ Feedback submitted successfully!');
        }
        
        setShowFeedbackModal(false);
        setFeedbackText('');
        setFeedbackRating(5);
        setSelectedDecision('maybe');
        setSelectedRoundForFeedback(null);
        // Refresh the data to show updated feedback
        fetchCandidateData();
      } else {
        console.error('Failed to submit feedback');
        alert('❌ Failed to submit feedback. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const openFeedbackModal = (round, interview) => {
    // Use interview data if round is not available
    const feedbackData = round || {
      id: interview?.round_id,
      round_name: `Interview ${interview?.id || 'Unknown'}`,
      description: 'Interview feedback'
    };
    setSelectedRoundForFeedback(feedbackData);
    setShowFeedbackModal(true);
  };

  // Enhanced function to render feedback for each round
  const renderRoundFeedback = (round, interview) => {
    // Get HR feedback for this round
    const hrFeedback = feedback.find(f => f.round_id === round.id);
    
    // Get Manager feedback for this round - STRICT MATCHING
    const managerFeedbackForRound = managerFeedback.filter(mf => {
      // First check if it's for the correct candidate
      const isForThisCandidate = String(mf.candidate_id) === String(candidate?.id) || 
                                 mf.candidate_name === candidate?.applicant_name ||
                                 mf.candidate_name === candidate?.candidateName;
      
      if (!isForThisCandidate) return false;
      
      // Then check for round-specific matching - must match at least one of these
      const matchesRoundName = mf.round_name === round.round_name;
      const matchesInterviewId = mf.interview_id === interview?.id;
      const matchesRoundId = mf.round_id === round.id;
      
      // Only show if it matches this specific round
      return matchesRoundName || matchesInterviewId || matchesRoundId;
    });

    // Get only the latest manager feedback for this round
    const latestManagerFeedback = managerFeedbackForRound.length > 0 ? 
      managerFeedbackForRound.sort((a, b) => new Date(b.submitted_at || 0) - new Date(a.submitted_at || 0))[0] : null;

    // Debug logging
    if (managerFeedbackForRound.length > 0) {
      console.log(`🔍 Round "${round.round_name}" (ID: ${round.id}) - Found ${managerFeedbackForRound.length} manager feedback items:`, managerFeedbackForRound.map(mf => ({
        id: mf.id,
        round_name: mf.round_name,
        interview_id: mf.interview_id,
        round_id: mf.round_id,
        submitted_at: mf.submitted_at
      })));
    }

    // Show section if there's HR feedback or manager feedback
    const hasAnyFeedback = hrFeedback || latestManagerFeedback;
    if (!hasAnyFeedback) {
      return null;
    }

    return (
      <div className="mt-4 p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h5 className="font-semibold text-gray-800 flex items-center">
            <MessageSquare className="w-4 h-4 mr-2 text-blue-600" />
            Round Feedback
          </h5>
          <div className="flex items-center space-x-2">
            {hrFeedback && (
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                HR Feedback
              </span>
            )}
            {latestManagerFeedback && (
              <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                Manager Feedback (Latest)
              </span>
            )}
          </div>
        </div>

        <div className="space-y-4">
          {/* HR Feedback Display */}
          {hrFeedback && (
            <div className="bg-white rounded-lg p-4 border border-blue-200 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <h6 className="font-medium text-gray-900">HR Assessment</h6>
                    <p className="text-xs text-gray-500">
                      {hrFeedback.submitted_at ? new Date(hrFeedback.submitted_at).toLocaleDateString() : 'Recent'}
                    </p>
                  </div>
                </div>
                {hrFeedback.overall_rating && (
                  <div className="flex items-center">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <Star
                        key={star}
                        className={`w-4 h-4 ${
                          star <= (hrFeedback.overall_rating || 0) ? 'text-yellow-400 fill-current' : 'text-gray-300'
                        }`}
                      />
                    ))}
                    <span className="ml-2 text-sm font-medium text-gray-700">
                      {hrFeedback.overall_rating}/5
                    </span>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                {hrFeedback.strengths && (
                  <div>
                    <h6 className="font-medium text-green-800 mb-1 flex items-center text-sm">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      Strengths
                    </h6>
                    <p className="text-sm text-gray-700 bg-green-50 p-2 rounded">{hrFeedback.strengths}</p>
                  </div>
                )}

                {hrFeedback.areas_of_improvement && (
                  <div>
                    <h6 className="font-medium text-orange-800 mb-1 flex items-center text-sm">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      Areas for Improvement
                    </h6>
                    <p className="text-sm text-gray-700 bg-orange-50 p-2 rounded">{hrFeedback.areas_of_improvement}</p>
                  </div>
                )}

                {hrFeedback.recommendation_notes && (
                  <div>
                    <h6 className="font-medium text-blue-800 mb-1 flex items-center text-sm">
                      <MessageSquare className="w-3 h-3 mr-1" />
                      Recommendation
                    </h6>
                    <p className="text-sm text-gray-700 bg-blue-50 p-2 rounded">{hrFeedback.recommendation_notes}</p>
                  </div>
                )}

                {hrFeedback.decision && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Decision:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      hrFeedback.decision === 'selected' || hrFeedback.decision === 'hire'
                        ? 'bg-green-100 text-green-800'
                        : hrFeedback.decision === 'rejected' || hrFeedback.decision === 'no_hire'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {hrFeedback.decision.toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Manager Feedback Display - LATEST ONLY */}
          {latestManagerFeedback && (
            <div className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <Award className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <h6 className="font-medium text-gray-900">Manager Assessment</h6>
                    <p className="text-xs text-gray-500">
                      {latestManagerFeedback.submitted_at ? new Date(latestManagerFeedback.submitted_at).toLocaleDateString() : 'Recent'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {latestManagerFeedback.overall_rating && (
                    <div className="flex items-center">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`w-4 h-4 ${
                            star <= (latestManagerFeedback.overall_rating || 0) ? 'text-yellow-400 fill-current' : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                  )}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    latestManagerFeedback.decision === 'strong_hire' || latestManagerFeedback.decision === 'hire' 
                      ? 'bg-green-100 text-green-800'
                      : latestManagerFeedback.decision === 'no_hire' || latestManagerFeedback.decision === 'reject'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {latestManagerFeedback.decision?.replace('_', ' ').toUpperCase() || 'PENDING'}
                  </span>
                </div>
              </div>

              {/* Manager Rating Breakdown */}
              {(latestManagerFeedback.technical_skills || latestManagerFeedback.communication_skills || latestManagerFeedback.problem_solving || latestManagerFeedback.cultural_fit) && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                  {latestManagerFeedback.technical_skills && (
                    <div className="text-center">
                      <div className="text-sm font-semibold text-blue-600">{latestManagerFeedback.technical_skills}/5</div>
                      <div className="text-xs text-gray-500">Technical</div>
                    </div>
                  )}
                  {latestManagerFeedback.communication_skills && (
                    <div className="text-center">
                      <div className="text-sm font-semibold text-green-600">{latestManagerFeedback.communication_skills}/5</div>
                      <div className="text-xs text-gray-500">Communication</div>
                    </div>
                  )}
                  {latestManagerFeedback.problem_solving && (
                    <div className="text-center">
                      <div className="text-sm font-semibold text-yellow-600">{latestManagerFeedback.problem_solving}/5</div>
                      <div className="text-xs text-gray-500">Problem Solving</div>
                    </div>
                  )}
                  {latestManagerFeedback.cultural_fit && (
                    <div className="text-center">
                      <div className="text-sm font-semibold text-purple-600">{latestManagerFeedback.cultural_fit}/5</div>
                      <div className="text-xs text-gray-500">Cultural Fit</div>
                    </div>
                  )}
                </div>
              )}

              {/* Manager Feedback Content */}
              <div className="space-y-3">
                {latestManagerFeedback.strengths && latestManagerFeedback.strengths !== 'na' && (
                  <div>
                    <h6 className="font-medium text-green-800 mb-1 flex items-center text-sm">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      Key Strengths
                    </h6>
                    <p className="text-sm text-gray-700 bg-green-50 p-2 rounded">{latestManagerFeedback.strengths}</p>
                  </div>
                )}

                {latestManagerFeedback.areas_for_improvement && latestManagerFeedback.areas_for_improvement !== 'na' && (
                  <div>
                    <h6 className="font-medium text-orange-800 mb-1 flex items-center text-sm">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      Areas for Improvement
                    </h6>
                    <p className="text-sm text-gray-700 bg-orange-50 p-2 rounded">{latestManagerFeedback.areas_for_improvement}</p>
                  </div>
                )}

                {latestManagerFeedback.detailed_feedback && latestManagerFeedback.detailed_feedback !== 'na' && (
                  <div>
                    <h6 className="font-medium text-blue-800 mb-1 flex items-center text-sm">
                      <MessageSquare className="w-3 h-3 mr-1" />
                      Detailed Assessment
                    </h6>
                    <p className="text-sm text-gray-700 bg-blue-50 p-2 rounded">{latestManagerFeedback.detailed_feedback}</p>
                  </div>
                )}

                {latestManagerFeedback.recommendation && latestManagerFeedback.recommendation !== 'na' && (
                  <div>
                    <h6 className="font-medium text-purple-800 mb-1 flex items-center text-sm">
                      <Award className="w-3 h-3 mr-1" />
                      Final Recommendation
                    </h6>
                    <p className="text-sm text-gray-700 bg-purple-50 p-2 rounded">{latestManagerFeedback.recommendation}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const markInterviewComplete = async (interviewId) => {
    try {
      console.log('Marking interview complete:', interviewId);
      
      // Find the interview to get candidate_id
      const interview = interviews.find(i => i.id === interviewId);
      if (!interview) {
        console.error('Interview not found:', interviewId);
        return;
      }
      
      const response = await fetch(`http://localhost:5000/api/interviews/status`, {
        method: 'PUT',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          interview_id: interviewId,
          candidate_id: interview.candidate_id,
          status: 'completed'
        })
      });

      if (response.ok) {
        console.log('Interview marked as complete successfully');
        await fetchCandidateData(); // Refresh data
      } else {
        console.error('Failed to mark interview complete');
        const errorData = await response.json();
        console.error('Error response:', errorData);
      }
    } catch (error) {
      console.error('Error marking interview complete:', error);
    }
  };

  const cancelInterview = async (interviewId) => {
    try {
      console.log('Cancelling interview:', interviewId);
      
      // Find the interview to get candidate_id
      const interview = interviews.find(i => i.id === interviewId);
      if (!interview) {
        console.error('Interview not found:', interviewId);
        return;
      }
      
      const response = await fetch(`http://localhost:5000/api/interviews/status`, {
        method: 'PUT',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          interview_id: interviewId,
          candidate_id: interview.candidate_id,
          status: 'cancelled'
        })
      });

      if (response.ok) {
        console.log('Interview cancelled successfully');
        await fetchCandidateData(); // Refresh data
      } else {
        console.error('Failed to cancel interview');
        const errorData = await response.json();
        console.error('Error response:', errorData);
      }
    } catch (error) {
      console.error('Error cancelling interview:', error);
    }
  };

  const deleteAllInterviews = async () => {
    try {
      console.log('Deleting all interviews for candidate:', 15);
      
      if (!window.confirm('Are you sure you want to delete all interview rounds? This action cannot be undone.')) {
        return;
      }
      
      // Delete all interviews for this candidate
      const deletePromises = interviews.map(async (interview) => {
        const response = await fetch(`http://localhost:5000/api/interviews/${interview.id}`, {
          method: 'DELETE',
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          console.log(`Interview ${interview.id} deleted successfully`);
        } else {
          console.error(`Failed to delete interview ${interview.id}`);
        }
      });
      
      await Promise.all(deletePromises);
      console.log('All interviews deleted successfully');
      await fetchCandidateData(); // Refresh data
    } catch (error) {
      console.error('Error deleting interviews:', error);
    }
  };

  const deleteIndividualInterview = async (interviewId, roundName) => {
    try {
      console.log('Deleting individual interview:', interviewId);
      
      if (!window.confirm(`Are you sure you want to delete the "${roundName}" interview? This action cannot be undone.`)) {
        return;
      }
      
      const response = await fetch(`http://localhost:5000/api/interviews/${interviewId}`, {
        method: 'DELETE',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        console.log(`Interview ${interviewId} deleted successfully`);
        await fetchCandidateData(); // Refresh data
      } else {
        console.error('Failed to delete interview');
        const errorData = await response.json();
        console.error('Error response:', errorData);
      }
    } catch (error) {
      console.error('Error deleting interview:', error);
    }
  };

  const testDebugEndpoint = async () => {
    try {
      console.log('Testing debug endpoint...');
      const response = await fetch('http://localhost:5000/api/debug/interviews', {
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Debug endpoint response:', data);
        console.log('Interviews in database:', data.data?.interviews);
        console.log('Candidates in database:', data.data?.candidates);
      } else {
        console.error('Debug endpoint error:', response.status);
      }
    } catch (err) {
      console.error('Debug endpoint exception:', err);
    }
  };

  const createDefaultRounds = async () => {
    try {
      console.log('Creating default rounds for ticket ID:', ticketId);
      const response = await fetch(`http://localhost:5000/api/interviews/rounds/${ticketId}/setup-default`, {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.success) {
        console.log('✅ Default 3-round interview process created successfully!');
        await fetchCandidateData(); // Refresh data to show new rounds
      } else {
        if (data.error && data.error.includes('already exist')) {
          console.log('Interview rounds already exist for this job.');
        } else {
          console.error('Failed to create default rounds:', data.error || response.statusText);
        }
      }
    } catch (err) {
      console.error('Error creating default rounds:', err);
    }
  };


  if (loading) {
    // If embedded, show loading within the embedded structure
    if (isEmbedded) {
      return (
        <div className="w-full h-full flex items-center justify-center">
          <div className="flex items-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <span className="ml-2">Loading candidate status...</span>
          </div>
        </div>
      );
    }
    
    // Full modal version for loading
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading candidate status...</span>
      </div>
    );
  }

  if (error) {
    // If embedded, show error within the embedded structure
    if (isEmbedded) {
      return (
        <div className="w-full h-full p-6">
          <div className="bg-red-50 border border-red-200 rounded-md p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
                <span className="text-red-800 font-medium">Error Loading Candidate Data</span>
              </div>
              <button
                onClick={fetchCandidateData}
                className="flex items-center px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded-md text-sm transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Retry
              </button>
            </div>
        <div className="text-red-700 text-sm mb-4">
          <p><strong>Error:</strong> {error}</p>
          <p className="mt-2"><strong>Debug Info:</strong></p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Candidate ID: {candidateId}</li>
            <li>Ticket ID: {ticketId}</li>
            <li>Backend URL: http://localhost:5000</li>
          </ul>
        </div>
                 <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
           <p className="text-yellow-800 text-sm">
             <strong>Possible Solutions:</strong>
           </p>
           <ul className="list-disc list-inside mt-1 text-yellow-700 text-sm space-y-1">
             <li><strong>Start Backend Server:</strong> Open terminal, run: <code className="bg-gray-100 px-1 rounded">cd Backend && python server.py</code></li>
             <li><strong>Check Candidate ID:</strong> Verify that candidate ID {candidateId} exists in the database</li>
             <li><strong>Create Candidate:</strong> If candidate doesn't exist, create it first through the application form</li>
             <li><strong>Check Database:</strong> Ensure the resume_applications table has data</li>
             <li><strong>API Key:</strong> Verify the API key is correct (currently using: sk-hiring-bot-2024-secret-key-xyz789)</li>
           </ul>
          </div>
        </div>
      </div>
    );
    }
    
    // Full modal version for error
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
            <span className="text-red-800 font-medium">Error Loading Candidate Data</span>
          </div>
          <button
            onClick={fetchCandidateData}
            className="flex items-center px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded-md text-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Retry
          </button>
        </div>
        <div className="text-red-700 text-sm mb-4">
          <p><strong>Error:</strong> {error}</p>
          <p className="mt-2"><strong>Debug Info:</strong></p>
          <ul className="list-disc list-inside mt-1 space-y-1">
            <li>Candidate ID: {candidateId}</li>
            <li>Ticket ID: {ticketId}</li>
            <li>Backend URL: http://localhost:5000</li>
          </ul>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
          <p className="text-yellow-800 text-sm">
            <strong>Possible Solutions:</strong>
          </p>
          <ul className="list-disc list-inside mt-1 text-yellow-700 text-sm space-y-1">
            <li><strong>Start Backend Server:</strong> Open terminal, run: <code className="bg-gray-100 px-1 rounded">cd Backend && python server.py</code></li>
            <li><strong>Check Candidate ID:</strong> Verify that candidate ID {candidateId} exists in the database</li>
            <li><strong>Create Candidate:</strong> If candidate doesn't exist, create it first through the application form</li>
            <li><strong>Check Database:</strong> Ensure the resume_applications table has data</li>
            <li><strong>API Key:</strong> Verify the API key is correct (currently using: sk-hiring-bot-2024-secret-key-xyz789)</li>
          </ul>
        </div>
      </div>
    );
  }

  if (!candidate) {
    // If embedded, show candidate not found within the embedded structure
    if (isEmbedded) {
      return (
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-2">Candidate not found.</p>
            <p className="text-gray-500 text-sm mb-4">Candidate ID: {candidateId}</p>
            <button
              onClick={fetchCandidateData}
              className="flex items-center mx-auto px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md text-sm transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Refresh Data
            </button>
          </div>
        </div>
      );
    }
    
    // Full modal version for candidate not found
    return (
      <div className="text-center py-8">
        <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 mb-2">Candidate not found.</p>
        <p className="text-gray-500 text-sm mb-4">Candidate ID: {candidateId}</p>
        <button
          onClick={fetchCandidateData}
          className="flex items-center mx-auto px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md text-sm transition-colors"
        >
          <RefreshCw className="w-4 h-4 mr-1" />
          Refresh Data
        </button>
      </div>
    );
  }


  // Function to render individual feedback items
  const renderFeedbackItem = (feedbackItem, index) => {
    const isHR = feedbackItem.type === 'hr';
    const isManager = feedbackItem.type === 'manager';
    
    return (
      <div 
        key={feedbackItem.id || `${feedbackItem.type}-${index}`} 
        className={`bg-white rounded-lg p-4 border shadow-sm ${
          isHR ? 'border-blue-200' : 'border-purple-200'
        }`}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              isHR ? 'bg-blue-100' : 'bg-purple-100'
            }`}>
              {isHR ? (
                <User className="w-4 h-4 text-blue-600" />
              ) : (
                <Award className="w-4 h-4 text-purple-600" />
              )}
            </div>
            <div>
              <h6 className="font-medium text-gray-900">
                {isHR ? 'HR Assessment' : 'Manager Assessment'}
              </h6>
              <p className="text-xs text-gray-500">
                {feedbackItem.submitted_at ? new Date(feedbackItem.submitted_at).toLocaleDateString() : 'Recent'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {feedbackItem.overall_rating && (
              <div className="flex items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <Star
                    key={star}
                    className={`w-4 h-4 ${
                      star <= (feedbackItem.overall_rating || 0) ? 'text-yellow-400 fill-current' : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
            )}
            {feedbackItem.decision && (
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                feedbackItem.decision === 'selected' || feedbackItem.decision === 'hire' || feedbackItem.decision === 'strong_hire'
                  ? 'bg-green-100 text-green-800'
                  : feedbackItem.decision === 'rejected' || feedbackItem.decision === 'no_hire' || feedbackItem.decision === 'reject'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {feedbackItem.decision?.replace('_', ' ').toUpperCase() || 'PENDING'}
              </span>
            )}
          </div>
        </div>

        {feedbackItem.strengths && feedbackItem.strengths !== 'na' && (
          <div className="mb-3">
            <h6 className="font-medium text-green-800 mb-1 flex items-center text-sm">
              <TrendingUp className="w-3 h-3 mr-1" />
              {isManager ? 'Key Strengths' : 'Strengths'}
            </h6>
            <p className="text-sm text-gray-700 bg-green-50 p-2 rounded">{feedbackItem.strengths}</p>
          </div>
        )}

        {feedbackItem.areas_for_improvement && feedbackItem.areas_for_improvement !== 'na' && (
          <div className="mb-3">
            <h6 className="font-medium text-orange-800 mb-1 flex items-center text-sm">
              <TrendingDown className="w-3 h-3 mr-1" />
              Areas for Improvement
            </h6>
            <p className="text-sm text-gray-700 bg-orange-50 p-2 rounded">{feedbackItem.areas_for_improvement}</p>
          </div>
        )}

        {feedbackItem.detailed_feedback && feedbackItem.detailed_feedback !== 'na' && (
          <div className="mb-3">
            <h6 className="font-medium text-blue-800 mb-1 flex items-center text-sm">
              <MessageSquare className="w-3 h-3 mr-1" />
              Detailed Assessment
            </h6>
            <p className="text-sm text-gray-700 bg-blue-50 p-2 rounded">{feedbackItem.detailed_feedback}</p>
          </div>
        )}

        {feedbackItem.recommendation && feedbackItem.recommendation !== 'na' && (
          <div className="mb-3">
            <h6 className="font-medium text-purple-800 mb-1 flex items-center text-sm">
              <Award className="w-3 h-3 mr-1" />
              Final Recommendation
            </h6>
            <p className="text-sm text-gray-700 bg-purple-50 p-2 rounded">{feedbackItem.recommendation}</p>
          </div>
        )}
      </div>
    );
  };

  // Don't render if candidate data is not loaded yet or if candidateData is invalid
  if (!candidate || !candidateData || typeof candidateData !== 'object') {
    // If embedded, show loading content within the embedded structure
    if (isEmbedded) {
      return (
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading candidate data...</p>
            {candidateData && typeof candidateData !== 'object' && (
              <p className="text-red-500 text-sm mt-2">Invalid candidate data format</p>
            )}
          </div>
        </div>
      );
    }
    
    // Full modal version for loading
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]" style={{ zIndex: 9999 }}>
        <div className="bg-white rounded-lg shadow-xl p-8 text-center mx-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading candidate data...</p>
          {candidateData && typeof candidateData !== 'object' && (
            <p className="text-red-500 text-sm mt-2">Invalid candidate data format</p>
          )}
        </div>
      </div>
    );
  }

  const progressPercentage = getProgressPercentage();

  // Render the modal content (shared between embedded and full modal)
  const renderModalContent = () => (
    <>
       {/* Demo Mode Indicator */}
       {candidate?.applicant_name === 'Demo Candidate' && (
         <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
           <div className="flex items-center">
             <AlertCircle className="w-5 h-5 text-blue-500 mr-2" />
             <div>
               <p className="text-blue-800 font-medium text-sm">Demo Mode Active</p>
               <p className="text-blue-600 text-xs">Using demo data for testing. Real candidate data will be shown when available.</p>
             </div>
           </div>
         </div>
       )}

       {/* Rejection Banner */}
       {(overallStatus === 'rejected' || finalDecision === 'reject') && (
         <div className="mb-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg">
           <div className="flex items-center">
             <ThumbsDown className="w-6 h-6 text-red-500 mr-3" />
             <div className="flex-1">
               <h3 className="text-red-800 font-bold text-lg mb-1">🚫 CANDIDATE REJECTED</h3>
               <p className="text-red-700 text-sm mb-2">
                 This candidate has been rejected and will not proceed to further interview rounds.
               </p>
               <p className="text-red-600 text-xs">
                 A rejection email has been automatically sent to the candidate. The candidate's status has been updated to "Rejected" in the system.
               </p>
             </div>
             <div className="ml-4">
               <div className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium border border-red-200">
                 REJECTED
               </div>
             </div>
           </div>
         </div>
       )}

       {/* Real Rounds Indicator */}
       {rounds.length > 0 && (
         <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
           <div className="flex items-center">
             <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
             <div>
               <p className="text-green-800 font-medium text-sm">Interview Rounds Loaded</p>
               <p className="text-green-600 text-xs">Showing {rounds.length} interview rounds for {candidate?.applicant_name || 'this candidate'}.</p>
             </div>
           </div>
         </div>
       )}

       {/* No Rounds Indicator */}
       {rounds.length === 0 && (
         <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
           <div className="flex items-center">
             <AlertCircle className="w-5 h-5 text-yellow-500 mr-2" />
             <div>
               <p className="text-yellow-800 font-medium text-sm">No Interview Rounds Found</p>
               <p className="text-yellow-600 text-xs">Create interview rounds first through the "Interview Rounds Setup" to see them here.</p>
             </div>
           </div>
         </div>
       )}

       {/* Debug Info - Rounds (Hidden in production) */}
       {process.env.NODE_ENV === 'development' && (
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
                 className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center space-x-2"
               >
                 <span>🚀</span>
                 <span>Create Default 3 Rounds</span>
               </button>
             </div>
           )}
         </div>
       </div>
       )}

       

      {/* Candidate Header */}
       <div className="flex items-center justify-between mb-8 border-b border-gray-200 pb-6">
        <div className="flex items-center space-x-6">
          <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center">
            <User className="w-8 h-8 text-indigo-600" />
          </div>
          <div>
             <h3 className="text-2xl font-bold text-gray-900">{candidate?.applicant_name || 'Loading...'}</h3>
            <p className="text-lg text-gray-600">{candidate?.applicant_email || 'Loading...'}</p>
             <p className="text-base text-gray-500">Applied for: {candidate?.job_title || 'Loading...'}</p>
          </div>
        </div>
      </div>

      {/* Interview Overview */}
      <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-xl font-bold text-gray-900 flex items-center">
            <Target className="w-6 h-6 mr-3 text-blue-600" />
            Interview Overview
          </h4>
        </div>
        <div className="grid grid-cols-2 gap-6 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-600">{getCompletedRoundsCount()}</div>
            <div className="text-sm text-gray-600">Rounds Completed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">{rounds.length}</div>
            <div className="text-sm text-gray-600">Total Rounds</div>
          </div>
        </div>
      </div>

      {/* Scheduled Interviews Section */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="font-semibold text-gray-900 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-blue-600" />
            Scheduled Interviews ({interviews.length})
          </h4>
          {interviews.length > 0 && (
            <button
              onClick={deleteAllInterviews}
              className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 text-sm"
            >
              <Trash2 className="w-4 h-4 mr-1" />
              Delete All Rounds
            </button>
          )}
        </div>
        <div className="space-y-4">
          {interviews.length === 0 ? (
            <div className="text-center py-8 border border-gray-200 rounded-lg bg-gray-50">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h5 className="text-lg font-medium text-gray-600 mb-2">No Interviews Scheduled</h5>
              <p className="text-gray-500 text-sm mb-4">
                No interview rounds have been scheduled for {candidate?.applicant_name || 'this candidate'} yet.
              </p>
              <p className="text-gray-400 text-xs mb-4">
                Schedule interviews from the Interview Manager to see them here.
              </p>
            </div>
          ) : (
            interviews.map((interview, index) => {
              const round = rounds.find(r => r.id === interview.round_id);
              const roundIndex = round ? rounds.findIndex(r => r.id === interview.round_id) : -1;
              const interviewStatus = getInterviewStatus(interview);
              
              // Get feedback for this interview - prioritize detailed feedback with strengths
              const allInterviewFeedback = feedback.filter(f => f.interview_id === interview.id);
              const interviewFeedback = allInterviewFeedback.find(f => f.strengths) || allInterviewFeedback[0];
              console.log('🔍 Looking for feedback for interview ID:', interview.id);
              console.log('🔍 Available feedback:', feedback);
              console.log('🔍 All interview feedback:', allInterviewFeedback);
              console.log('🔍 Found interviewFeedback (prioritizing with strengths):', interviewFeedback);
              
              // Also try to find feedback by round_id as fallback - prioritize detailed feedback
              const allRoundFeedback = feedback.filter(f => f.round_id === interview.round_id);
              const roundFeedback = allRoundFeedback.find(f => f.strengths) || allRoundFeedback[0];
              console.log('🔍 Looking for feedback by round_id:', interview.round_id);
              console.log('🔍 All round feedback:', allRoundFeedback);
              console.log('🔍 Found roundFeedback (prioritizing with strengths):', roundFeedback);
              
              // Debug the feedback array structure
              feedback.forEach((fb, index) => {
                console.log(`🔍 Feedback item ${index}:`, {
                  interview_id: fb.interview_id,
                  round_id: fb.round_id,
                  strengths: fb.strengths,
                  recommendation_notes: fb.recommendation_notes,
                  decision: fb.decision,
                  overall_rating: fb.overall_rating
                });
              });

              return (
                <div key={interview.id} className="border border-blue-200 rounded-lg p-4 bg-blue-50 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h5 className="font-medium text-gray-900 flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-blue-600" />
                        {interview.round_name || (round ? `Round ${rounds.findIndex(r => r.id === interview.round_id) + 1}: ${round.round_name}` : 'Interview')}
                      </h5>
                      <p className="text-sm text-gray-600">{interview.round_description || round?.description || 'Interview scheduled'}</p>
                </div>
                <div className="flex items-center space-x-2">
                      {interview.scheduled_date && (
                        <div className="px-3 py-1 rounded-full border border-blue-200 bg-blue-100 text-blue-800 text-sm font-medium">
                          {formatDateForDisplay(interview.scheduled_date)} at {interview.scheduled_time}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* Interview Details */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-3">
                    <div>
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Type:</span> {interview.interview_type?.replace('_', ' ') || round?.interview_type?.replace('_', ' ') || 'Not specified'}
                    </div>
                    <div>
                      <span className="font-medium text-gray-700">Status:</span> 
                      <span className={`ml-1 px-2 py-1 rounded-full text-xs ${getStatusColor(interviewStatus.status)}`}>
                        {interviewStatus.status.toUpperCase()}
                    </span>
                    </div>
                  </div>

                  {/* Feedback Display */}
                  {(interviewStatus.feedback || interviewFeedback) && (
                    <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-md">
                      <div className="flex items-center justify-between mb-2">
                        <h6 className="font-medium text-green-800">Feedback Submitted</h6>
                        <div className="flex items-center">
                          <Star className="w-4 h-4 text-yellow-400 mr-1" />
                          <span className="text-sm text-green-700">{interviewFeedback?.overall_rating || interviewStatus.rating}/5</span>
                        </div>
                      </div>
                      <p className="text-sm text-green-700">
                        {(() => {
                          const notes = interviewFeedback?.recommendation_notes || interviewFeedback?.strengths || roundFeedback?.recommendation_notes || roundFeedback?.strengths || interviewStatus.feedback?.strengths || 'No additional notes';
                          console.log('🔍 Feedback display values:', {
                            interviewFeedback_recommendation_notes: interviewFeedback?.recommendation_notes,
                            interviewFeedback_strengths: interviewFeedback?.strengths,
                            roundFeedback_recommendation_notes: roundFeedback?.recommendation_notes,
                            roundFeedback_strengths: roundFeedback?.strengths,
                            interviewStatus_feedback_strengths: interviewStatus.feedback?.strengths,
                            final_notes: notes
                          });
                          return notes;
                        })()}
                      </p>
                      <div className="mt-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${getDecisionColor(interviewFeedback?.decision || interviewStatus.decision)}`}>
                          {getDecisionIcon(interviewFeedback?.decision || interviewStatus.decision)}
                          <span className="ml-1">{(interviewFeedback?.decision || interviewStatus.decision)?.replace('_', ' ').toUpperCase()}</span>
                    </span>
                      </div>
                    </div>
                  )}
                  
                  {/* Interview Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-blue-200">
                    <div className="flex space-x-2">
                      {interviewStatus.status === 'scheduled' && (
                        <>
                          <button 
                            onClick={() => markInterviewComplete(interview.id)}
                            className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 text-sm"
                          >
                            <CheckCircle className="w-4 h-4 mr-1" />
                            Mark Complete
                          </button>
                          <button 
                            onClick={() => cancelInterview(interview.id)}
                            className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 text-sm"
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            Cancel
                          </button>
                        </>
                      )}
                      {interviewStatus.status === 'completed' && !interviewStatus.decision && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => round && updateRoundDecision(round.id, 'selected')}
                            className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 text-sm"
                            disabled={!round}
                          >
                            <ThumbsUp className="w-4 h-4 mr-1" />
                            Select
                          </button>
                          <button
                            onClick={() => round && updateRoundDecision(round.id, 'rejected')}
                            className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 text-sm"
                            disabled={!round}
                          >
                            <ThumbsDown className="w-4 h-4 mr-1" />
                            Reject
                          </button>
                          <button
                            onClick={() => round && updateRoundDecision(round.id, 'on_hold')}
                            className="flex items-center px-3 py-1 bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200 text-sm"
                            disabled={!round}
                          >
                            <Minus className="w-4 h-4 mr-1" />
                            Hold
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <button 
                        onClick={() => openFeedbackModal(round, interview)}
                        className="flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 text-sm"
                      >
                        <MessageSquare className="w-4 h-4 mr-1" />
                        Add Feedback
                      </button>
                      <button 
                        onClick={() => deleteIndividualInterview(interview.id, round.round_name)}
                        className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 text-sm"
                      >
                        <Trash2 className="w-4 h-4 mr-1" />
                        Delete
                      </button>
                    </div>
                  </div>
                  
                  {/* Enhanced Feedback Display for this Round */}
                  {renderRoundFeedback(round, interview)}
                </div>
            );
            })
          )}
        </div>
      </div>



      {/* Overall Decision Management */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
          <CheckSquare className="w-5 h-5 mr-2 text-green-600" />
          Final Decision
        </h4>
        
        {finalDecision ? (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Current Decision</p>
              <div className={`inline-flex items-center px-3 py-1 rounded-full border text-sm font-medium mt-1 ${getDecisionColor(finalDecision)}`}>
                {getDecisionIcon(finalDecision)}
                <span className="ml-1">{finalDecision === 'reject' ? 'REJECTED' : finalDecision.replace('_', ' ').toUpperCase()}</span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  console.log('🔄 Select button clicked');
                  updateOverallStatus('hired');
                }}
                className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 text-sm"
              >
                <ThumbsUp className="w-4 h-4 mr-1" />
                Select
              </button>
              <button
                onClick={() => {
                  console.log('🔄 Reject button clicked');
                  updateOverallStatus('rejected');
                }}
                className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 text-sm"
              >
                <ThumbsDown className="w-4 h-4 mr-1" />
                Reject
              </button>
              <button
                onClick={() => {
                  console.log('🔄 Hold button clicked');
                  updateOverallStatus('completed');
                }}
                className="flex items-center px-3 py-1 bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200 text-sm"
              >
                <Minus className="w-4 h-4 mr-1" />
                Hold
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">No final decision made yet</p>
              <p className="text-xs text-gray-500">Complete all rounds to make a decision</p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => {
                  console.log('🔄 Select Candidate button clicked');
                  updateOverallStatus('hired');
                }}
                className="flex items-center px-3 py-1 bg-green-100 text-green-700 rounded-md hover:bg-green-200 text-sm"
              >
                <ThumbsUp className="w-4 h-4 mr-1" />
                Select Candidate
              </button>
              <button
                onClick={() => {
                  console.log('🔄 Reject Candidate button clicked');
                  updateOverallStatus('rejected');
                }}
                className="flex items-center px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 text-sm"
              >
                <ThumbsDown className="w-4 h-4 mr-1" />
                Reject Candidate
              </button>
              <button
                onClick={() => {
                  console.log('🔄 Put On Hold button clicked');
                  updateOverallStatus('completed');
                }}
                className="flex items-center px-3 py-1 bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200 text-sm"
              >
                <Minus className="w-4 h-4 mr-1" />
                Put On Hold
              </button>
          </div>
        </div>
      )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center items-center pt-6 border-t border-gray-200">
        <button
          onClick={fetchCandidateData}
          className="flex items-center px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
        >
          <RefreshCw className="w-5 h-5 mr-2" />
          Refresh Status
        </button>
      </div>

      {/* Feedback Modal */}
      {showFeedbackModal && selectedRoundForFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[10000]" style={{ zIndex: 10000 }}>
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Add Feedback</h3>
              <button
                onClick={() => {
                  setShowFeedbackModal(false);
                  setSelectedDecision('maybe');
                  setFeedbackText('');
                  setFeedbackRating(5);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Round: {selectedRoundForFeedback.round_name}
              </label>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating
              </label>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setFeedbackRating(star)}
                    className={`text-2xl ${star <= feedbackRating ? 'text-yellow-400' : 'text-gray-300'}`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Decision
              </label>
              <div className="flex space-x-3">
                <button
                  onClick={() => setSelectedDecision('hire')}
                  className={`px-4 py-2 rounded-md border-2 transition-colors ${
                    selectedDecision === 'hire'
                      ? 'bg-green-100 border-green-500 text-green-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-green-50'
                  }`}
                >
                  <span className="flex items-center">
                    <span className="mr-1">👍</span>
                    HIRE
                  </span>
                </button>
                <button
                  onClick={() => setSelectedDecision('maybe')}
                  className={`px-4 py-2 rounded-md border-2 transition-colors ${
                    selectedDecision === 'maybe'
                      ? 'bg-yellow-100 border-yellow-500 text-yellow-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-yellow-50'
                  }`}
                >
                  <span className="flex items-center">
                    <span className="mr-1">🤔</span>
                    MAYBE
                  </span>
                </button>
                <button
                  onClick={() => setSelectedDecision('reject')}
                  className={`px-4 py-2 rounded-md border-2 transition-colors ${
                    selectedDecision === 'reject'
                      ? 'bg-red-100 border-red-500 text-red-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-red-50'
                  }`}
                >
                  <span className="flex items-center">
                    <span className="mr-1">👎</span>
                    REJECT
                  </span>
                </button>
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feedback
              </label>
              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                placeholder="Enter your feedback for this round..."
              />
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowFeedbackModal(false);
                  setSelectedDecision('maybe');
                  setFeedbackText('');
                  setFeedbackRating(5);
                }}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => submitFeedback(selectedRoundForFeedback.id)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Submit Feedback
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );

  // If embedded, render without modal wrapper
  if (isEmbedded) {
    return (
      <div className="w-full h-full">
        {/* Modal Header */}
        <div className="p-6 border-b border-gray-200 bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Candidate Interview Status</h2>
            <p className="text-gray-600 mt-1 text-base">{candidate?.applicant_name || 'Loading...'} - {candidate?.job_title || 'web dev'}</p>
          </div>
        </div>

        {/* Modal Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)] space-y-6">
          {renderModalContent()}
        </div>
      </div>
    );
  }

  // Full modal version (when not embedded)
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]" style={{ zIndex: 9999 }}>
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[95vh] overflow-hidden mx-4 my-4">
        {/* Modal Header */}
        <div className="p-8 border-b border-gray-200 bg-gray-50">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">Candidate Interview Status</h2>
            <p className="text-gray-600 mt-2 text-lg">{candidate?.applicant_name || 'Loading...'} - {candidate?.job_title || 'web dev'}</p>
          </div>
        </div>

        {/* Modal Content */}
        <div className="p-8 overflow-y-auto max-h-[calc(95vh-220px)] space-y-8">
          {renderModalContent()}
        </div>
      </div>
    </div>
  );
};

export default CandidateInterviewStatus;
