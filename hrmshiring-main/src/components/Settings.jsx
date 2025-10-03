import React, { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon,
  Mail,
  Lock,
  Save,
  CheckCircle,
  AlertCircle,
  Eye,
  EyeOff,
  RefreshCw,
  Server,
  Globe,
  User,
  Building,
  Phone,
  Loader
} from 'lucide-react';

// API Configuration
const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',
  API_KEY: 'sk-hiring-bot-2024-secret-key-xyz789'
};

const Settings = () => {
  const [emailConfig, setEmailConfig] = useState({
    smtp_server: 'smtp.gmail.com',
    smtp_port: 587,
    email_address: '',
    email_password: '',
    use_tls: true,
    from_name: 'HR Team - Your Company',
    company_name: 'Your Company Name',
    company_website: 'https://yourcompany.com',
    hr_email: '',
    send_emails: true
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  // Load current email configuration
  useEffect(() => {
    loadEmailConfig();
  }, []);

  const loadEmailConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/settings/email`, {
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setEmailConfig(data.data);
          setMessage('Email configuration loaded successfully');
          setMessageType('success');
        }
      } else {
        setMessage('Failed to load email configuration');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error loading email config:', error);
      setMessage('Error loading email configuration');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const saveEmailConfig = async () => {
    setSaving(true);
    setMessage('');

    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/api/settings/email`, {
        method: 'PUT',
        headers: {
          'X-API-Key': API_CONFIG.API_KEY,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(emailConfig)
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage('Email configuration saved successfully!');
        setMessageType('success');
      } else {
        setMessage(data.error || 'Failed to save email configuration');
        setMessageType('error');
      }
    } catch (error) {
      console.error('Error saving email config:', error);
      setMessage('Error saving email configuration');
      setMessageType('error');
    } finally {
      setSaving(false);
    }
  };


  const handleInputChange = (field, value) => {
    setEmailConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleToggle = (field) => {
    setEmailConfig(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-xl shadow-lg">
      {/* Header */}
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
          <SettingsIcon className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Email Settings</h1>
          <p className="text-gray-600">Configure email settings for sending rejection and hiring emails to candidates</p>
        </div>
      </div>

      {/* Message Display */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
          messageType === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-800' 
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          {messageType === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span>{message}</span>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-gray-600">Loading email configuration...</span>
        </div>
      ) : (
        <div className="space-y-8">
          {/* SMTP Configuration */}
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Server className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-800">SMTP Configuration</h2>
                <p className="text-gray-600">Configure your email server settings</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SMTP Server
                </label>
                <input
                  type="text"
                  value={emailConfig.smtp_server}
                  onChange={(e) => handleInputChange('smtp_server', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="smtp.gmail.com"
                />
                <p className="text-xs text-gray-500 mt-1">e.g., smtp.gmail.com, smtp.outlook.com</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  SMTP Port
                </label>
                <input
                  type="number"
                  value={emailConfig.smtp_port}
                  onChange={(e) => handleInputChange('smtp_port', parseInt(e.target.value))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="587"
                />
                <p className="text-xs text-gray-500 mt-1">Common ports: 587 (TLS), 465 (SSL), 25</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={emailConfig.email_address}
                    onChange={(e) => handleInputChange('email_address', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="your-email@company.com"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Email address to send from</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={emailConfig.email_password}
                    onChange={(e) => handleInputChange('email_password', e.target.value)}
                    className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="App password or regular password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">Use app password for Gmail</p>
              </div>
            </div>

            <div className="mt-6">
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={emailConfig.use_tls}
                  onChange={() => handleToggle('use_tls')}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Use TLS Encryption</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">Enable TLS encryption for secure email transmission</p>
            </div>
          </div>

          {/* Company Information */}
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Building className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-800">Company Information</h2>
                <p className="text-gray-600">Company details for email templates</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  From Name
                </label>
                <input
                  type="text"
                  value={emailConfig.from_name}
                  onChange={(e) => handleInputChange('from_name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="HR Team - Your Company"
                />
                <p className="text-xs text-gray-500 mt-1">Display name in emails</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name
                </label>
                <input
                  type="text"
                  value={emailConfig.company_name}
                  onChange={(e) => handleInputChange('company_name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Your Company Name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Website
                </label>
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="url"
                    value={emailConfig.company_website}
                    onChange={(e) => handleInputChange('company_website', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="https://yourcompany.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  HR Contact Email
                </label>
                <div className="relative">
                  <User className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                  <input
                    type="email"
                    value={emailConfig.hr_email}
                    onChange={(e) => handleInputChange('hr_email', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="hr@yourcompany.com"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Email Settings */}
          <div className="bg-gray-50 rounded-xl p-6">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <Mail className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-800">Email Settings</h2>
                <p className="text-gray-600">Control email sending behavior</p>
              </div>
            </div>

            <div>
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={emailConfig.send_emails}
                  onChange={() => handleToggle('send_emails')}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">Enable Email Sending</span>
              </label>
              <p className="text-xs text-gray-500 mt-1">When disabled, emails will not be sent to candidates</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-4 pt-6 border-t border-gray-200">
            <button
              onClick={saveEmailConfig}
              disabled={saving}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-colors shadow-md"
            >
              {saving ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <Save className="w-5 h-5" />
              )}
              <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
            </button>


            <button
              onClick={loadEmailConfig}
              disabled={loading}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-semibold flex items-center space-x-2 transition-colors shadow-md"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>

          {/* Help Section */}
          <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-800 mb-4">📧 Email Configuration Help</h3>
            <div className="space-y-3 text-sm text-blue-700">
              <div>
                <strong>Gmail Setup:</strong>
                <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                  <li>Enable 2-factor authentication</li>
                  <li>Generate an App Password (not your regular password)</li>
                  <li>Use smtp.gmail.com and port 587</li>
                  <li>Enable TLS encryption</li>
                </ul>
              </div>
              <div>
                <strong>Outlook/Hotmail Setup:</strong>
                <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                  <li>Use smtp-mail.outlook.com and port 587</li>
                  <li>Enable TLS encryption</li>
                  <li>Use your regular email password</li>
                </ul>
              </div>
              <div>
                <strong>Custom SMTP:</strong>
                <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                  <li>Contact your email provider for SMTP settings</li>
                  <li>Common ports: 587 (TLS), 465 (SSL), 25 (unencrypted)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;
