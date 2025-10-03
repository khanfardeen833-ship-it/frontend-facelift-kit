import React, { useState } from 'react';
import { CheckCircle, AlertCircle, Loader, Database, RefreshCw } from 'lucide-react';

const TestSetup: React.FC = () => {
  const [isCreating, setIsCreating] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    message: string;
    details?: any;
  } | null>(null);

  const createSampleJobs = async () => {
    setIsCreating(true);
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/api/test/create-sample-jobs', {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (data.success) {
        setResult({
          success: true,
          message: data.message,
          details: data.data
        });
      } else {
        setResult({
          success: false,
          message: data.error || 'Failed to create sample jobs'
        });
      }
    } catch (error: any) {
      setResult({
        success: false,
        message: `Network error: ${error.message}`
      });
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-6">
          <Database className="w-8 h-8 text-blue-600 mr-3" />
          <h2 className="text-2xl font-bold text-gray-900">Test Setup</h2>
        </div>

        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            This will create sample jobs in the database for testing the application form. 
            These jobs will be available for candidates to apply to.
          </p>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-yellow-800 mb-2">Sample Jobs to be Created:</h3>
            <ul className="text-sm text-yellow-700 space-y-1">
              <li>• Senior Software Engineer at TechCorp</li>
              <li>• Product Manager at InnovateTech</li>
              <li>• UX Designer at DesignStudio</li>
            </ul>
          </div>
        </div>

        <button
          onClick={createSampleJobs}
          disabled={isCreating}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-blue-400 transition-colors duration-200 font-medium flex items-center justify-center"
        >
          {isCreating ? (
            <>
              <Loader className="w-5 h-5 animate-spin mr-2" />
              Creating Sample Jobs...
            </>
          ) : (
            <>
              <RefreshCw className="w-5 h-5 mr-2" />
              Create Sample Jobs
            </>
          )}
        </button>

        {result && (
          <div className={`mt-6 p-4 rounded-lg border ${
            result.success 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-center mb-2">
              {result.success ? (
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
              )}
              <span className={`font-medium ${
                result.success ? 'text-green-800' : 'text-red-800'
              }`}>
                {result.success ? 'Success!' : 'Error'}
              </span>
            </div>
            <p className={`text-sm ${
              result.success ? 'text-green-700' : 'text-red-700'
            }`}>
              {result.message}
            </p>
            
            {result.success && result.details && (
              <div className="mt-3">
                <h4 className="font-medium text-green-800 mb-2">Created Jobs:</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  {result.details.map((job: any, index: number) => (
                    <li key={index}>
                      • {job.job_title} (ID: {job.ticket_id})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Next Steps:</h3>
          <ol className="text-sm text-gray-600 space-y-1">
            <li>1. Click "Create Sample Jobs" above</li>
            <li>2. Go back to the main page to see the jobs</li>
            <li>3. Try applying to a job to test the form</li>
            <li>4. Check that the email confirmation works</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default TestSetup;
