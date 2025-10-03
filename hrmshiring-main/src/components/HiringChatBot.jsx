import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, X, Minimize2, Maximize2 } from 'lucide-react';
import { getApiUrl, API_ENDPOINTS } from '../config/api';
import { useAuth } from '../contexts/AuthContext';

const HiringChatBot = ({ onJobPosted }) => {
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userId, setUserId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const savedScrollPosition = useRef(0);
  const shouldAutoScroll = useRef(true);

  // API configuration is now centralized in config/api.js

  // Initialize chat session when component mounts
  useEffect(() => {
    initializeChat();
  }, []);

  // Auto-scroll to bottom when messages change (only if should auto-scroll)
  useEffect(() => {
    if (shouldAutoScroll.current && messages.length > 0) {
      scrollToBottom();
    }
  }, [messages]);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (inputRef.current) {
      const textarea = inputRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'; // Max height of 120px
    }
  }, [inputMessage]);

  // Initial resize when component mounts
  useEffect(() => {
    if (inputRef.current) {
      const textarea = inputRef.current;
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [isOpen]);

  // Handle minimize/maximize scroll position
  useEffect(() => {
    if (!isMinimized && messagesContainerRef.current) {
      // Restore scroll position when maximizing
      messagesContainerRef.current.scrollTop = savedScrollPosition.current;
    }
  }, [isMinimized]);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  const initializeChat = async () => {
    try {
      // Use authenticated user ID if available, otherwise generate a temporary one
      const user_id = isAuthenticated && user?.user_id ? user.user_id : null;
      
      const response = await fetch(getApiUrl(API_ENDPOINTS.CHAT.START), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789'
        },
        body: JSON.stringify({ user_id })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setUserId(data.user_id);
      
      // Add welcome message - check for different possible response formats
      const welcomeMessage = data.message || data.response || 'Welcome to the Hiring Bot!';
      addMessage('assistant', welcomeMessage);
    } catch (error) {
      console.error('Error initializing chat:', error);
      addMessage('system', 'Failed to connect to the chat server. Please ensure the server is running.');
    }
  };

  const addMessage = (sender, content, metadata = null) => {
    const newMessage = {
      id: Date.now(),
      sender,
      content: content || '', // Ensure content is never undefined
      metadata,
      timestamp: new Date()
    };
    // Enable auto-scroll when adding new messages
    shouldAutoScroll.current = true;
    setMessages(prev => [...prev, newMessage]);
  };

  const sendMessage = async () => {
    const message = inputMessage.trim();
    
    if (!message || !sessionId) {
      if (!sessionId) {
        await initializeChat();
      }
      return;
    }

    // Add user message
    addMessage('user', message);
    setInputMessage('');
    setIsTyping(true);

    try {
      // Prepare headers with authentication if available
      const headers = {
        'Content-Type': 'application/json',
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789'
      };
      
      // Add authentication token if user is logged in
      if (isAuthenticated && user?.token) {
        headers['Authorization'] = `Bearer ${user.token}`;
      }

      const response = await fetch(getApiUrl(API_ENDPOINTS.CHAT.MESSAGE), {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          session_id: sessionId,
          user_id: isAuthenticated && user?.user_id ? user.user_id : userId,
          message: message
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      
      // Handle different response formats from the server
      const responseMessage = data.response || data.message || 'No response from server';
      const responseMetadata = data.metadata || null;
      
      // Add assistant response
      addMessage('assistant', responseMessage, responseMetadata);
      
      // Check if a job was posted and notify parent component
      if (responseMetadata?.action === 'ticket_created' && onJobPosted) {
        onJobPosted(responseMetadata.ticket_id);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage('system', 'Failed to send message. Please check your connection.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
    // Allow Shift+Enter for new lines in textarea
  };

  const sendQuickMessage = (message) => {
    setInputMessage(message);
    // Use setTimeout to ensure state is updated before sending
    setTimeout(() => {
      sendMessage();
    }, 0);
  };

  const formatMessage = (content) => {
    // Ensure content is a string
    if (!content || typeof content !== 'string') {
      return '';
    }
    
    // Simple formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>');
  };

  // Chat button (floating)
  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-purple-500 to-purple-700 text-white rounded-full p-4 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 z-50"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  // Chat window
  return (
    <div className={`fixed bottom-6 right-6 bg-white rounded-2xl shadow-2xl transition-all duration-300 z-50 ${
      isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
    } flex flex-col`}>
      
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-700 text-white p-4 rounded-t-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-lg font-bold">AI</span>
          </div>
          <div>
            <h3 className="font-semibold">Hiring Assistant</h3>
            <p className="text-xs opacity-90">Post jobs • Check status • Get help</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              if (!isMinimized && messagesContainerRef.current) {
                // Save scroll position before minimizing
                savedScrollPosition.current = messagesContainerRef.current.scrollTop;
              }
              setIsMinimized(!isMinimized);
            }}
            className="hover:bg-white/20 p-1 rounded transition-colors"
          >
            {isMinimized ? <Maximize2 size={18} /> : <Minimize2 size={18} />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-white/20 p-1 rounded transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div 
            ref={messagesContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50"
            onScroll={(e) => {
              // Disable auto-scroll if user manually scrolls up
              const container = e.target;
              const isAtBottom = container.scrollHeight - container.scrollTop === container.clientHeight;
              shouldAutoScroll.current = isAtBottom;
            }}
          >
            {messages.filter(msg => msg && msg.content).map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${
                  msg.sender === 'user' ? 'flex-row-reverse' : ''
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  msg.sender === 'user' 
                    ? 'bg-gray-200 text-gray-700' 
                    : msg.sender === 'assistant'
                    ? 'bg-gradient-to-r from-purple-500 to-purple-700 text-white'
                    : 'bg-red-100 text-red-600'
                }`}>
                  {msg.sender === 'user' ? 'U' : msg.sender === 'assistant' ? 'AI' : '!'}
                </div>
                <div className="max-w-[75%]">
                  <div className={`rounded-2xl px-4 py-2 ${
                    msg.sender === 'user'
                      ? 'bg-gradient-to-r from-purple-500 to-purple-700 text-white'
                      : 'bg-white border border-gray-200'
                  } ${msg.sender === 'user' ? 'rounded-br-sm' : 'rounded-bl-sm'}`}>
                    <div 
                      dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                      className="text-sm text-left"
                      style={{ direction: 'ltr', textAlign: 'left' }}
                    />
                  </div>
                  {msg.metadata?.ticket_id && (
                    <div className="mt-2">
                      <span className="inline-block bg-green-100 text-green-700 text-xs px-2 py-1 rounded">
                        Ticket: {msg.metadata.ticket_id}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-purple-700 text-white flex items-center justify-center">
                  AI
                </div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-2">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div className="p-3 bg-white border-t border-gray-200 flex gap-2 justify-center">
            <button
              onClick={() => {
                setInputMessage('I want to post a job');
                setTimeout(() => sendMessage(), 100);
              }}
              className="px-3 py-1.5 bg-gray-100 hover:bg-purple-100 text-gray-700 hover:text-purple-700 rounded-full text-xs font-medium transition-colors"
            >
              📝 Post a Job
            </button>
            <button
              onClick={() => {
                setInputMessage('Show my tickets');
                setTimeout(() => sendMessage(), 100);
              }}
              className="px-3 py-1.5 bg-gray-100 hover:bg-purple-100 text-gray-700 hover:text-purple-700 rounded-full text-xs font-medium transition-colors"
            >
              📋 My Tickets
            </button>
            <button
              onClick={() => {
                setInputMessage('I need help');
                setTimeout(() => sendMessage(), 100);
              }}
              className="px-3 py-1.5 bg-gray-100 hover:bg-purple-100 text-gray-700 hover:text-purple-700 rounded-full text-xs font-medium transition-colors"
            >
              💡 Get Help
            </button>
          </div>

          {/* Input */}
          <div className="p-4 bg-white border-t border-gray-200 rounded-b-2xl">
            <div className="flex gap-2 items-end">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-full focus:outline-none focus:border-purple-500 transition-colors text-sm text-left resize-none overflow-hidden"
                style={{ 
                  direction: 'ltr', 
                  textAlign: 'left',
                  minHeight: '40px',
                  maxHeight: '120px'
                }}
                disabled={!sessionId}
                rows={1}
              />
              <button
                onClick={sendMessage}
                disabled={!sessionId || !inputMessage.trim()}
                className="w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-700 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default HiringChatBot;