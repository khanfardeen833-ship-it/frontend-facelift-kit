import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  User, 
  Video, 
  Phone,
  MapPin,
  ChevronRight,
  ExternalLink,
  Star,
  Sparkles
} from 'lucide-react';
import { API_CONFIG } from '../config/api';

const UpcomingInterviewsWidget = () => {
  const [upcomingInterviews, setUpcomingInterviews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUpcomingInterviews();
  }, []);

  const fetchUpcomingInterviews = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/calendar`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          // Filter to get only today's and tomorrow's interviews
          const today = new Date();
          const tomorrow = new Date(today);
          tomorrow.setDate(tomorrow.getDate() + 1);
          
          const todayStr = today.toISOString().split('T')[0];
          const tomorrowStr = tomorrow.toISOString().split('T')[0];
          
          const upcoming = data.events
            .filter(interview => {
              // Handle different date formats from API
              let interviewDate;
              if (interview.start.includes(' ')) {
                // Format: "2025-08-26 10:00"
                interviewDate = interview.start.split(' ')[0];
              } else {
                interviewDate = new Date(interview.start).toISOString().split('T')[0];
              }
              return interviewDate === todayStr || interviewDate === tomorrowStr;
            })
            .sort((a, b) => new Date(a.start) - new Date(b.start))
            .slice(0, 5); // Show only next 5 interviews
          
          setUpcomingInterviews(upcoming);
        }
      }
    } catch (error) {
      console.error('Error fetching upcoming interviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  const getInterviewTypeIcon = (type) => {
    switch (type) {
      case 'video_call': return <Video className="w-4 h-4" />;
      case 'phone_call': return <Phone className="w-4 h-4" />;
      case 'in_person': return <MapPin className="w-4 h-4" />;
      default: return <Calendar className="w-4 h-4" />;
    }
  };

  const getRelativeDate = (dateStr) => {
    const today = new Date();
    const interviewDate = new Date(dateStr);
    const diffTime = interviewDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    return interviewDate.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-soft border border-gray-100 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded w-full"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-soft border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-blue-600 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
              <Calendar className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Upcoming Interviews</h3>
              <p className="text-blue-100 text-sm">
                {upcomingInterviews.length} interview{upcomingInterviews.length !== 1 ? 's' : ''} scheduled
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-1">
            <Star className="w-4 h-4 text-yellow-300" />
            <span className="text-xs text-yellow-100 font-medium">Premium</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {upcomingInterviews.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">No upcoming interviews</p>
            <p className="text-gray-400 text-xs mt-1">Check back later for scheduled interviews</p>
          </div>
        ) : (
          <div className="space-y-4">
            {upcomingInterviews.map((interview, index) => (
              <motion.div
                key={interview.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="group p-4 bg-gray-50 rounded-xl hover:bg-blue-50 transition-all duration-200 border border-gray-100"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-6 h-6 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                        {getInterviewTypeIcon(interview.interview_type)}
                      </div>
                      <h4 className="font-medium text-gray-900 truncate">
                        {interview.candidate_name}
                      </h4>
                    </div>
                    
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <Clock className="w-3 h-3" />
                         <span>{getRelativeDate(interview.start)} at {interview.start.includes(' ') ? formatTime(interview.start.split(' ')[1]) : formatTime(interview.start)}</span>
                      </div>
                      
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <User className="w-3 h-3" />
                        <span className="truncate">{interview.round_name}</span>
                      </div>
                      
                      {interview.job_title && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Sparkles className="w-3 h-3" />
                          <span className="truncate">{interview.job_title}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-col items-end space-y-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
                      {interview.duration}min
                    </span>
                    
                    {interview.meeting_link && (
                      <a
                        href={interview.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-1 text-blue-600 hover:text-blue-800 transition-colors opacity-0 group-hover:opacity-100"
                        title="Join Meeting"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
            
            {upcomingInterviews.length >= 5 && (
              <div className="pt-4 border-t border-gray-100">
                <button className="w-full text-center text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors">
                  View All Interviews
                  <ChevronRight className="w-4 h-4 inline ml-1" />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UpcomingInterviewsWidget;
