import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calendar as CalendarIcon, 
  Clock, 
  User, 
  MapPin, 
  Video, 
  Phone,
  ChevronLeft, 
  ChevronRight,
  Plus,
  RefreshCw,
  Eye,
  ExternalLink,
  Star,
  Award,
  Briefcase,
  Mail,
  PhoneCall,
  MapPin as LocationIcon,
  X,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { API_CONFIG } from '../config/api';

const InterviewCalendar = ({ isOpen, onClose }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [interviews, setInterviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [view, setView] = useState('month'); // month, week, day

  // Fetch interviews from API
  const fetchInterviews = async () => {
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
          console.log('Calendar API Response:', data.events);
          console.log('First interview data:', data.events[0]);
          setInterviews(data.events);
        }
      }
    } catch (error) {
      console.error('Error fetching interviews:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchInterviews();
    }
  }, [isOpen]);

  // Get calendar days for current month
  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const current = new Date(startDate);
    
    // Generate 42 days (6 weeks)
    for (let i = 0; i < 42; i++) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }
    
    return days;
  };

  // Get interviews for a specific date
  const getInterviewsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    const dayInterviews = interviews.filter(interview => {
      // Handle different date formats from API
      let interviewDateStr;
      
      if (interview.start.includes(' ')) {
        // Format: "2025-08-26 10:00"
        interviewDateStr = interview.start.split(' ')[0];
      } else {
        // Try to parse as Date object
        interviewDateStr = new Date(interview.start).toISOString().split('T')[0];
      }
      
      const matches = interviewDateStr === dateStr;
      return matches;
    });
    
    return dayInterviews;
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Check if date is in current month
  const isCurrentMonth = (date) => {
    return date.getMonth() === currentDate.getMonth();
  };

  // Navigate months
  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(newDate.getMonth() + direction);
      return newDate;
    });
  };

  // Format time
  const formatTime = (timeStr) => {
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'scheduled': return 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100';
      case 'in_progress': return 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100';
      case 'completed': return 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100';
      default: return 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100';
    }
  };

  // Get interview type icon
  const getInterviewTypeIcon = (type) => {
    switch (type) {
      case 'video_call': return <Video className="w-3 h-3" />;
      case 'phone_call': return <Phone className="w-3 h-3" />;
      case 'in_person': return <LocationIcon className="w-3 h-3" />;
      default: return <CalendarIcon className="w-3 h-3" />;
    }
  };

  const calendarDays = getCalendarDays();


  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <style jsx>{`
            .calendar-scrollbar::-webkit-scrollbar {
              width: 3px;
            }
            .calendar-scrollbar::-webkit-scrollbar-track {
              background: transparent;
            }
            .calendar-scrollbar::-webkit-scrollbar-thumb {
              background: #d1d5db;
              border-radius: 3px;
            }
            .calendar-scrollbar::-webkit-scrollbar-thumb:hover {
              background: #9ca3af;
            }
            .calendar-scrollbar {
              scrollbar-width: thin;
              scrollbar-color: #d1d5db transparent;
            }
          `}</style>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={onClose}
          >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl h-[90vh] flex flex-col overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                    <CalendarIcon className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold">Interview Calendar</h2>
                    <p className="text-blue-100 text-sm">Manage all candidate interviews</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <button
                    onClick={fetchInterviews}
                    disabled={loading}
                    className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-all duration-200"
                  >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                  </button>
                  
                  <button
                    onClick={onClose}
                    className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-all duration-200"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>


            {/* Controls */}
            <div className="bg-gray-50 p-4 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => navigateMonth(-1)}
                    className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  
                  <h3 className="text-xl font-semibold text-gray-800">
                    {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </h3>
                  
                  <button
                    onClick={() => navigateMonth(1)}
                    className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </button>
                  
                  <button
                    onClick={() => setCurrentDate(new Date())}
                    className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                  >
                    Today
                  </button>
                </div>
              </div>
            </div>

            {/* Calendar Grid */}
            <div className="flex-1 overflow-hidden">
              <div className="h-full flex flex-col">
                {/* Day headers */}
                <div className="grid grid-cols-7 bg-gradient-to-r from-gray-50 to-gray-100 border-b border-gray-200 sticky top-0 z-10">
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className="p-3 text-center text-sm font-semibold text-gray-700 border-r border-gray-200 last:border-r-0">
                      {day}
                    </div>
                  ))}
                </div>
                
                {/* Calendar days */}
                <div className="flex-1 overflow-y-auto">
                  <div className="grid grid-cols-7 gap-0 h-full">
                    {calendarDays.map((day, index) => {
                      const dayInterviews = getInterviewsForDate(day);
                      const isCurrentMonthDay = isCurrentMonth(day);
                      const isTodayDay = isToday(day);
                      
                      return (
                        <div
                          key={index}
                          className={`border-r border-b border-gray-200 p-3 min-h-[120px] flex flex-col transition-all duration-200 ${
                            !isCurrentMonthDay ? 'bg-gray-50' : 'bg-white hover:bg-gray-50 hover:shadow-sm'
                          }`}
                        >
                          <div className={`text-sm font-semibold mb-2 flex-shrink-0 ${
                            isTodayDay 
                              ? 'bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center shadow-md mx-auto' 
                              : isCurrentMonthDay 
                                ? 'text-gray-900 hover:text-blue-600 transition-colors text-center' 
                                : 'text-gray-400 text-center'
                          }`}>
                            {day.getDate()}
                          </div>
                          
                          <div className="space-y-1 flex-1 overflow-y-auto calendar-scrollbar">
                            {dayInterviews.map(interview => (
                              <motion.div
                                key={interview.id}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className={`p-1.5 rounded text-xs cursor-pointer hover:shadow-sm hover:scale-[1.01] transition-all duration-200 border ${getStatusColor(interview.status)}`}
                                onClick={() => {
                                  console.log('Selected interview data:', interview);
                                  setSelectedInterview(interview);
                                }}
                              >
                                <div className="flex items-center space-x-1 mb-0.5">
                                  <div className="flex-shrink-0">
                                    {getInterviewTypeIcon(interview.interview_type)}
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="truncate font-medium text-gray-800 text-xs">
                                      {interview.candidate_name}
                                    </div>
                                  </div>
                                </div>
                                <div className="text-xs text-gray-600 opacity-80 truncate">
                                  {interview.round_name}
                                </div>
                                <div className="text-xs opacity-70 text-gray-600 flex items-center space-x-1">
                                  <Clock className="w-2.5 h-2.5 flex-shrink-0" />
                                  <span className="truncate">{interview.start.includes(' ') ? formatTime(interview.start.split(' ')[1]) : formatTime(interview.start)}</span>
                                </div>
                              </motion.div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Interview Detail Modal */}
          <AnimatePresence>
            {selectedInterview && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60 p-4"
                onClick={() => setSelectedInterview(null)}
              >
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.95, opacity: 0 }}
                  className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Modal Header */}
                  <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-white bg-opacity-20 rounded-xl flex items-center justify-center">
                          <User className="w-6 h-6" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold">{selectedInterview.candidate_name}</h3>
                          <p className="text-green-100">{selectedInterview.round_name}</p>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => setSelectedInterview(null)}
                        className="p-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-all duration-200"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Modal Content */}
                  <div className="p-6 space-y-6">
                    {/* Status Badge */}
                    <div className="flex items-center justify-between">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(selectedInterview.status)}`}>
                        {selectedInterview.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <div className="flex items-center space-x-2">
                        {getInterviewTypeIcon(selectedInterview.interview_type)}
                        <span className="text-sm text-gray-600 capitalize">
                          {selectedInterview.interview_type.replace('_', ' ')}
                        </span>
                      </div>
                    </div>

                    {/* Interview Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                          <Clock className="w-5 h-5 text-blue-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">Date & Time</p>
                             <p className="text-sm text-gray-600">
                               {selectedInterview.start ? (
                                 selectedInterview.start.includes(' ') ? 
                                   `${selectedInterview.start.split(' ')[0]} at ${formatTime(selectedInterview.start.split(' ')[1])}` :
                                   `${new Date(selectedInterview.start).toLocaleDateString()} at ${formatTime(selectedInterview.start)}`
                               ) : 'Not specified'}
                             </p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3">
                          <Clock className="w-5 h-5 text-green-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">Duration</p>
                            <p className="text-sm text-gray-600">{selectedInterview.duration} minutes</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3">
                          <Mail className="w-5 h-5 text-purple-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">Email</p>
                            <p className="text-sm text-gray-600">{selectedInterview.candidate_email || 'Not provided'}</p>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="flex items-center space-x-3">
                          <User className="w-5 h-5 text-orange-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">Interviewer(s)</p>
                            <p className="text-sm text-gray-600">{selectedInterview.interviewer_names || 'Not assigned'}</p>
                          </div>
                        </div>

                        <div className="flex items-center space-x-3">
                          <Briefcase className="w-5 h-5 text-indigo-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">Job Title</p>
                            <p className="text-sm text-gray-600">{selectedInterview.job_title || 'Not specified'}</p>
                          </div>
                        </div>

                        {selectedInterview.meeting_link && (
                          <div className="flex items-center space-x-3">
                            <ExternalLink className="w-5 h-5 text-red-600" />
                            <div>
                              <p className="text-sm font-medium text-gray-900">Meeting Link</p>
                              <a 
                                href={selectedInterview.meeting_link} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-sm text-blue-600 hover:text-blue-800 underline"
                              >
                                Join Meeting
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Notes */}
                    {selectedInterview.notes && (
                      <div>
                        <p className="text-sm font-medium text-gray-900 mb-2">Notes</p>
                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-sm text-gray-600">{selectedInterview.notes}</p>
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center justify-end space-x-3 pt-4 border-t">
                      <button
                        onClick={() => setSelectedInterview(null)}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                      >
                        Close
                      </button>
                      
                      {selectedInterview.meeting_link && (
                        <a
                          href={selectedInterview.meeting_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center space-x-2"
                        >
                          <Video className="w-4 h-4" />
                          <span>Join Meeting</span>
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default InterviewCalendar;
