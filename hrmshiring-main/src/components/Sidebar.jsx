import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import InterviewCalendar from './InterviewCalendar';
import { 
  Grid3X3,
  Briefcase,
  Users,
  Settings,
  LogOut,
  User,
  ChevronLeft,
  Sparkles,
  Menu,
  X,
  Calendar,
  Star
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab, userRole, setUserRole, isOpen, setIsOpen }) => {
  const { user, logout } = useAuth();
  const [showCalendar, setShowCalendar] = useState(false);
  
  const menuItems = [
    { id: 'dashboard', icon: Grid3X3, label: 'Dashboard' },
    { id: 'career', icon: Briefcase, label: 'Jobs' },
    { id: 'applications', icon: Users, label: 'Candidates' },
  ];

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <motion.div
      initial={false}
      animate={{ 
        width: isOpen ? 240 : 72
      }}
      transition={{ 
        duration: 0.3, 
        ease: [0.4, 0, 0.2, 1]
      }}
      className="fixed left-0 top-0 h-full sidebar-modern z-50 flex flex-col"
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-surface-200 bg-white">
        <motion.div
          className={`flex items-center space-x-3 ${!isOpen ? 'cursor-pointer hover:bg-secondary-50 rounded-xl p-2 -m-2 transition-colors' : ''}`}
          animate={{ justifyContent: isOpen ? 'flex-start' : 'center' }}
          onClick={!isOpen ? toggleSidebar : undefined}
          whileHover={!isOpen ? { scale: 1.05 } : {}}
          whileTap={!isOpen ? { scale: 0.95 } : {}}
        >
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center shadow-soft">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <AnimatePresence>
            {isOpen && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="font-display font-semibold text-secondary-900"
              >
                Workforce
              </motion.span>
            )}
          </AnimatePresence>
        </motion.div>
        
        <AnimatePresence>
          {isOpen && (
            <motion.button
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              onClick={toggleSidebar}
              className="w-8 h-8 flex items-center justify-center text-secondary-400 hover:text-secondary-600 hover:bg-secondary-50 rounded-lg transition-all duration-200 focus-ring"
            >
              <ChevronLeft className="w-4 h-4" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* User Section */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="p-4 border-b border-surface-200 bg-surface-50"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-primary-600" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-secondary-900 truncate">
                  {user ? (user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.name || user.email || 'User') : 'User'}
                </p>
                <p className="text-xs text-secondary-500 truncate">
                  HR Manager
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-2">
        {menuItems.map((item, index) => (
          <motion.button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full group relative flex items-center rounded-xl transition-all duration-200 ${
              activeTab === item.id
                ? 'bg-primary-50 text-primary-700 shadow-soft'
                : 'text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900'
            } ${isOpen ? 'px-3 py-3' : 'px-2 py-3 justify-center'}`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className={`w-5 h-5 flex-shrink-0 flex items-center justify-center ${
              activeTab === item.id ? 'text-primary-600' : 'text-secondary-500'
            }`}>
              <item.icon className="w-5 h-5" />
            </div>
            
            <AnimatePresence>
              {isOpen && (
                <motion.span
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={{ duration: 0.2 }}
                  className="ml-3 text-sm font-medium truncate"
                >
                  {item.label}
                </motion.span>
              )}
            </AnimatePresence>

            {/* Active indicator */}
            {activeTab === item.id && (
              <motion.div
                layoutId="activeIndicator"
                className="absolute right-2 w-2 h-2 bg-primary-600 rounded-full"
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
              />
            )}

            {/* Tooltip for collapsed state */}
            {!isOpen && (
              <div className="absolute left-full ml-2 px-3 py-2 bg-secondary-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none whitespace-nowrap z-50 shadow-large">
                {item.label}
                <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-secondary-900 rotate-45"></div>
              </div>
            )}
          </motion.button>
        ))}

        {/* Interview Calendar Button */}
        <motion.button
          onClick={() => setShowCalendar(true)}
          className={`w-full group relative flex items-center rounded-xl transition-all duration-200 text-blue-600 hover:bg-blue-50 hover:text-blue-800 bg-gradient-to-r from-blue-50/50 to-purple-50/50 ${
            isOpen ? 'px-3 py-3' : 'px-2 py-3 justify-center'
          }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: menuItems.length * 0.1 }}
        >
          <div className="relative">
            <Calendar className="w-5 h-5 text-blue-600" />
            <Star className="w-3 h-3 text-yellow-500 absolute -top-1 -right-1" />
          </div>
          
          <AnimatePresence>
            {isOpen && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="ml-3 flex-1"
              >
                <div className="text-sm font-medium truncate">Interview Calendar</div>
                <div className="text-xs text-blue-500 truncate">Premium Feature</div>
              </motion.div>
            )}
          </AnimatePresence>

          {!isOpen && (
            <div className="absolute left-full ml-2 px-3 py-2 bg-secondary-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none whitespace-nowrap z-50 shadow-large">
              Interview Calendar
              <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-secondary-900 rotate-45"></div>
            </div>
          )}
        </motion.button>
      </nav>

      {/* Bottom Section */}
      <div className="p-3 space-y-2 border-t border-surface-200 bg-surface-50">
        {/* Settings */}
        <motion.button
          onClick={() => setActiveTab('settings')}
          className={`w-full group relative flex items-center rounded-xl transition-all duration-200 text-secondary-600 hover:bg-secondary-50 hover:text-secondary-900 ${
            activeTab === 'settings' ? 'bg-secondary-100 text-secondary-900' : ''
          } ${isOpen ? 'px-3 py-3' : 'px-2 py-3 justify-center'}`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Settings className="w-5 h-5 text-secondary-500" />
          
          <AnimatePresence>
            {isOpen && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="ml-3 text-sm font-medium truncate"
              >
                Settings
              </motion.span>
            )}
          </AnimatePresence>

          {!isOpen && (
            <div className="absolute left-full ml-2 px-3 py-2 bg-secondary-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none whitespace-nowrap z-50 shadow-large">
              Settings
              <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-secondary-900 rotate-45"></div>
            </div>
          )}
        </motion.button>

        {/* Logout */}
        <motion.button
          onClick={logout}
          className={`w-full group relative flex items-center rounded-xl transition-all duration-200 text-secondary-600 hover:bg-error-50 hover:text-error-600 ${
            isOpen ? 'px-3 py-3' : 'px-2 py-3 justify-center'
          }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <LogOut className="w-5 h-5 text-secondary-500 group-hover:text-error-500" />
          
          <AnimatePresence>
            {isOpen && (
              <motion.span
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.2 }}
                className="ml-3 text-sm font-medium truncate group-hover:text-error-600"
              >
                Logout
              </motion.span>
            )}
          </AnimatePresence>

          {!isOpen && (
            <div className="absolute left-full ml-2 px-3 py-2 bg-secondary-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none whitespace-nowrap z-50 shadow-large">
              Logout
              <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1 w-2 h-2 bg-secondary-900 rotate-45"></div>
            </div>
          )}
        </motion.button>
      </div>

      {/* Interview Calendar Modal */}
      <InterviewCalendar 
        isOpen={showCalendar} 
        onClose={() => setShowCalendar(false)} 
      />
    </motion.div>
  );
};

export default Sidebar;