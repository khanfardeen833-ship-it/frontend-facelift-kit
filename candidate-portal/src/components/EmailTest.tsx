import React, { useState } from 'react';
import { Mail, CheckCircle, AlertCircle, Loader } from 'lucide-react';

const EmailTest: React.FC = () => {
  const [testEmail, setTestEmail] = useState('');
  const [isTesting, setIsTesting] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    details?: any;
  } | null>(null);

  const testEmailConfig = async () => {
    if (!testEmail.trim()) {
      setResult({
        success: false,
        message: 'Please enter a test email address'
      });
      return;
    }

    setIsTesting(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/api/email/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789'
        },
        body: JSON.stringify({
          test_email: testEmail
        })
      });

      const data = await response.json();
      setResult({
        success: data.success,
        message: data.message || data.error,
        details: data
      });
    } catch (error: any) {
      setResult({
        success: false,
        message: `Test failed: ${error.message}`
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center mb-4">
        <Mail className="w-6 h-6 text-blue-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-800">Email Configuration Test</h2>
      </div>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Test Email Address
          </label>
          <input
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="Enter email to test"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <button
          onClick={testEmailConfig}
          disabled={isTesting}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-2 px-4 rounded-lg font-medium flex items-center justify-center space-x-2 transition-colors"
        >
          {isTesting ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              <span>Testing...</span>
            </>
          ) : (
            <>
              <Mail className="w-4 h-4" />
              <span>Test Email Configuration</span>
            </>
          )}
        </button>
        
        {result && (
          <div className={`p-4 rounded-lg border ${
            result.success 
              ? 'bg-green-50 border-green-200 text-green-800' 
              : 'bg-red-50 border-red-200 text-red-800'
          }`}>
            <div className="flex items-center space-x-2 mb-2">
              {result.success ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-600" />
              )}
              <span className="font-medium">
                {result.success ? 'Test Successful!' : 'Test Failed'}
              </span>
            </div>
            <p className="text-sm">{result.message}</p>
            {result.details && (
              <details className="mt-2">
                <summary className="text-sm cursor-pointer">View Details</summary>
                <pre className="text-xs mt-2 bg-gray-100 p-2 rounded overflow-auto">
                  {JSON.stringify(result.details, null, 2)}
                </pre>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EmailTest;
