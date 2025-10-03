import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, CheckCircle, Shield, RefreshCw, Loader, Mail } from 'lucide-react';
import { Job } from '../App';

interface ApplicationFormProps {
  jobs: Job[];
}

interface ApplicationData {
  applicant_name: string;
  applicant_email: string;
  phone: string;
  cover_letter: string;
  resume: File | null;
}

interface FormErrors {
  applicant_name?: string;
  applicant_email?: string;
  phone?: string;
  cover_letter?: string;
  resume?: string;
}

const ApplicationForm: React.FC<ApplicationFormProps> = ({ jobs }) => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  // React hooks must be called at the top level
  const [formData, setFormData] = useState<ApplicationData>({
    applicant_name: '',
    applicant_email: '',
    phone: '',
    cover_letter: '',
    resume: null
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [success, setSuccess] = useState(false);
  
  // CAPTCHA states
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [captchaSession, setCaptchaSession] = useState<string | null>(null);
  const [captchaText, setCaptchaText] = useState<string | null>(null);
  const [showCaptcha, setShowCaptcha] = useState(false);
  const [captchaData, setCaptchaData] = useState<any>(null);
  const [captchaLoading, setCaptchaLoading] = useState(false);
  const [captchaError, setCaptchaError] = useState<string>('');
  
  // Application details for success message
  const [applicationDetails, setApplicationDetails] = useState<{
    applicationId?: string;
    jobTitle?: string;
    emailSent?: boolean;
  }>({});
  
  // Duplicate application prevention
  const [duplicateCheck, setDuplicateCheck] = useState<{
    isChecking: boolean;
    hasApplied: boolean;
    existingApplication?: any;
  }>({
    isChecking: false,
    hasApplied: false
  });
  
  // Check for duplicate applications when email is entered
  const checkDuplicateApplication = async (email: string) => {
    if (!email || !jobId) return;
    
    setDuplicateCheck(prev => ({ ...prev, isChecking: true }));
    
    try {
      const response = await fetch(`http://localhost:5000/api/tickets/${jobId}/resumes`, {
        method: 'GET',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const existingApplication = data.data?.resumes?.find((app: any) => 
          app.applicant_email?.toLowerCase() === email.toLowerCase()
        );
        
        setDuplicateCheck({
          isChecking: false,
          hasApplied: !!existingApplication,
          existingApplication
        });
      }
    } catch (error) {
      console.error('Error checking duplicate application:', error);
      setDuplicateCheck(prev => ({ ...prev, isChecking: false }));
    }
  };

  // Auto-show CAPTCHA when form is ready - must be before any conditional returns
  useEffect(() => {
    if (formData.applicant_name && formData.applicant_email && formData.resume) {
      setShowCaptcha(true);
      generateCaptcha();
    }
  }, [formData.applicant_name, formData.applicant_email, formData.resume]);
  
  // Check for duplicates when email changes
  useEffect(() => {
    if (formData.applicant_email && formData.applicant_email.includes('@')) {
      const timeoutId = setTimeout(() => {
        checkDuplicateApplication(formData.applicant_email);
      }, 1000); // Debounce for 1 second
      
      return () => clearTimeout(timeoutId);
    }
  }, [formData.applicant_email, jobId]);
  
  // Handle case where jobId might be undefined
  if (!jobId) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <p className="text-lg font-medium">Invalid job ID</p>
        </div>
        <Link
          to="/"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
        >
          Back to Jobs
        </Link>
      </div>
    );
  }
  
  const job = jobs.find(j => j.id === jobId);

  if (!job) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">
          <p className="text-lg font-medium">Job not found</p>
        </div>
        <Link
          to="/"
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
        >
          Back to Jobs
        </Link>
      </div>
    );
  }

  const validateForm = () => {
    const newErrors: FormErrors = {};

    // Full name validation
    if (!formData.applicant_name.trim()) {
      newErrors.applicant_name = 'Full name is required';
    } else if (formData.applicant_name.trim().length < 2) {
      newErrors.applicant_name = 'Full name must be at least 2 characters long';
    } else if (!/^[a-zA-Z\s'-]+$/.test(formData.applicant_name.trim())) {
      newErrors.applicant_name = 'Full name can only contain letters, spaces, hyphens, and apostrophes';
    } else if (formData.applicant_name.trim().length > 100) {
      newErrors.applicant_name = 'Full name is too long (maximum 100 characters)';
    }

    // Email validation
    if (!formData.applicant_email.trim()) {
      newErrors.applicant_email = 'Email address is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.applicant_email.trim())) {
      newErrors.applicant_email = 'Please enter a valid email address';
    } else if (formData.applicant_email.trim().length > 254) {
      newErrors.applicant_email = 'Email address is too long';
    }

    // Phone validation
    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else {
      // Remove all non-digit characters except + for validation
      const cleanPhone = formData.phone.replace(/[^\d+]/g, '');
      
      // Check if phone contains only digits and optional + at the beginning
      if (!/^[\+]?[1-9][\d]{7,14}$/.test(cleanPhone)) {
        newErrors.phone = 'Please enter a valid phone number (8-15 digits, optionally starting with +)';
      }
    }

    // Cover letter validation
    if (!formData.cover_letter.trim()) {
      newErrors.cover_letter = 'Please tell us why you want to join our company';
    } else if (formData.cover_letter.trim().length < 10) {
      newErrors.cover_letter = 'Please provide at least 10 characters explaining why you want to join';
    } else if (formData.cover_letter.trim().length > 2000) {
      newErrors.cover_letter = 'Cover letter is too long (maximum 2000 characters)';
    }

    // Resume validation
    if (!formData.resume) {
      newErrors.resume = 'Resume is required';
    } else {
      // Check file size (10MB limit)
      if (formData.resume.size > 10 * 1024 * 1024) {
        newErrors.resume = 'File size must be less than 10MB';
      }
      
      // Check file type
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(formData.resume.type)) {
        newErrors.resume = 'Please upload a PDF, DOC, or DOCX file';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    // Special handling for phone number input
    if (name === 'phone') {
      // Allow only digits, +, spaces, hyphens, and parentheses for formatting
      const filteredValue = value.replace(/[^\d+\s\-\(\)]/g, '');
      setFormData(prev => ({
        ...prev,
        [name]: filteredValue
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }

    // Real-time validation
    if (name === 'applicant_name' && value.trim()) {
      if (value.trim().length < 2) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Full name must be at least 2 characters long'
        }));
      } else if (!/^[a-zA-Z\s'-]+$/.test(value.trim())) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Full name can only contain letters, spaces, hyphens, and apostrophes'
        }));
      } else if (value.trim().length > 100) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Full name is too long (maximum 100 characters)'
        }));
      } else {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    } else if (name === 'applicant_email' && value.trim()) {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Please enter a valid email address'
        }));
      } else if (value.trim().length > 254) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Email address is too long'
        }));
      } else {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    } else if (name === 'phone' && value.trim()) {
      const cleanPhone = value.replace(/[^\d+]/g, '');
      if (!/^[\+]?[1-9][\d]{7,14}$/.test(cleanPhone)) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Please enter a valid phone number (8-15 digits, optionally starting with +)'
        }));
      } else {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    } else if (name === 'cover_letter' && value.trim()) {
      if (value.trim().length < 10) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Please provide at least 10 characters explaining why you want to join'
        }));
      } else if (value.trim().length > 2000) {
        setErrors(prev => ({
          ...prev,
          [name]: 'Cover letter is too long (maximum 2000 characters)'
        }));
      } else {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    } else {
      // Clear error when user starts typing for other fields
      if (errors[name as keyof FormErrors]) {
        setErrors(prev => ({
          ...prev,
          [name]: ''
        }));
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setErrors(prev => ({
          ...prev,
          resume: 'File size must be less than 10MB'
        }));
        return;
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(file.type)) {
        setErrors(prev => ({
          ...prev,
          resume: 'Please upload a PDF, DOC, or DOCX file'
        }));
        return;
      }

      setFormData(prev => ({
        ...prev,
        resume: file
      }));

      // Clear any existing resume errors
      setErrors(prev => ({
        ...prev,
        resume: ''
      }));
      
      // Show CAPTCHA when form is complete
      if (formData.applicant_name && formData.applicant_email) {
        setShowCaptcha(true);
      }
    }
  };

  // CAPTCHA functions
  const generateCaptcha = async () => {
    setCaptchaLoading(true);
    setCaptchaError('');
    setCaptchaVerified(false);

    try {
      const response = await fetch('http://localhost:5000/api/captcha/generate', {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to generate CAPTCHA');
      }

      const result = await response.json();
      if (result.success) {
        setCaptchaData(result.data);
      } else {
        throw new Error(result.error || 'Failed to generate CAPTCHA');
      }
    } catch (err: any) {
      setCaptchaError('Failed to load CAPTCHA. Please try again.');
      console.error('CAPTCHA error:', err);
    } finally {
      setCaptchaLoading(false);
    }
  };

  const handleCaptchaVerify = async (userInput: string) => {
    if (!userInput.trim()) {
      setCaptchaError('Please enter the CAPTCHA text');
      return;
    }

    setCaptchaLoading(true);
    setCaptchaError('');

    try {
      const response = await fetch('http://localhost:5000/api/captcha/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: captchaData.session_id,
          captcha_text: userInput
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setCaptchaVerified(true);
        setCaptchaSession(captchaData.session_id);
        setCaptchaText(userInput);
        setCaptchaError('');
      } else {
        setCaptchaError(result.message || 'Incorrect CAPTCHA. Please try again.');
        generateCaptcha(); // Generate new CAPTCHA on failure
      }
    } catch (err: any) {
      setCaptchaError('Failed to verify CAPTCHA. Please try again.');
      generateCaptcha();
    } finally {
      setCaptchaLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Prevent submission if duplicate application detected
    if (duplicateCheck.hasApplied) {
      setErrors({ 
        applicant_email: 'You have already applied to this position. Each candidate can only apply once per job posting.' 
      });
      return;
    }

    if (!captchaVerified) {
      setErrors({ 
        applicant_email: 'Please complete the CAPTCHA verification' 
      });
      setShowCaptcha(true);
      return;
    }

    setIsSubmitting(true);

    try {
      // Create FormData for file upload
      const formDataToSend = new FormData();
      formDataToSend.append('resume', formData.resume!);
      formDataToSend.append('applicant_name', formData.applicant_name);
      formDataToSend.append('applicant_email', formData.applicant_email);
      formDataToSend.append('applicant_phone', formData.phone);
      formDataToSend.append('cover_letter', formData.cover_letter);
      formDataToSend.append('captcha_session', captchaSession!);
      formDataToSend.append('captcha_text', captchaText!);

      // Make real API call to backend
      const response = await fetch(`http://localhost:5000/api/tickets/${jobId}/resumes`, {
        method: 'POST',
        headers: {
          'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789'
        },
        body: formDataToSend
      });

      const result = await response.json();

      if (result.success) {
        console.log('Application submitted successfully:', result);
        setSuccess(true);
        
        // Store application details for success message
        setApplicationDetails({
          applicationId: result.data.application_id,
          jobTitle: result.data.job_title,
          emailSent: result.data.email_sent
        });
        
        // Redirect to home page after 5 seconds (longer to read email info)
        setTimeout(() => {
          navigate('/');
        }, 5000);

      } else {
        throw new Error(result.error || 'Failed to submit application');
      }

    } catch (error: any) {
      console.error('Application error:', error);
      setErrors({ 
        applicant_email: `Application failed: ${error.message}` 
      });
      // Reset CAPTCHA on error
      setCaptchaVerified(false);
      setShowCaptcha(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="bg-green-50 rounded-lg p-8">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Application Submitted Successfully! 🎉
          </h2>
          <p className="text-gray-600 mb-6">
            Thank you for applying to the <strong>{applicationDetails.jobTitle || job.title}</strong> position. 
            Your application has been received and will be reviewed by our team.
          </p>
          
          {/* Email Confirmation Section */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6 border border-blue-200">
            <div className="flex items-center justify-center mb-3">
              <Mail className="w-6 h-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-blue-800">Email Confirmation Sent!</h3>
            </div>
            <p className="text-sm text-blue-800 mb-3">
              ✅ A confirmation email has been sent to <strong>{formData.applicant_email}</strong>
            </p>
            <p className="text-sm text-blue-700">
              Please check your inbox (and spam folder) for the confirmation email containing your application details.
            </p>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
            <p className="text-sm text-gray-800">
              <strong>Application Details:</strong><br/>
              • Position: {applicationDetails.jobTitle || job.title}<br/>
              • Applicant: {formData.applicant_name}<br/>
              • Email: {formData.applicant_email}<br/>
              {applicationDetails.applicationId && `• Application ID: ${applicationDetails.applicationId}<br/>`}
              • CAPTCHA Verified: ✅ Yes<br/>
              • Email Sent: {applicationDetails.emailSent ? '✅ Yes' : '❌ No'}
            </p>
          </div>
          
          <div className="bg-yellow-50 rounded-lg p-4 mb-6 border border-yellow-200">
            <h4 className="font-semibold text-yellow-800 mb-2">What happens next?</h4>
            <ul className="text-sm text-yellow-700 text-left space-y-1">
              <li>• Our HR team will review your application</li>
              <li>• AI screening will match your skills with job requirements</li>
              <li>• We'll contact qualified candidates within 5-7 business days</li>
              <li>• Keep the confirmation email for your records</li>
            </ul>
          </div>
          
          <p className="text-sm text-gray-500 mb-6">
            You will be redirected to the job listings in a few seconds...
          </p>
          <Link
            to="/"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            Browse More Jobs
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Back Button */}
      <div className="mb-6">
        <Link
          to={`/job/${jobId}`}
          className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors duration-200"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Job Details</span>
        </Link>
      </div>

      {/* Job Summary */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h2>
        <p className="text-gray-600">{job.location}</p>
      </div>

      {/* Application Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Submit Your Application</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Full Name */}
          <div>
            <label htmlFor="applicant_name" className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              id="applicant_name"
              name="applicant_name"
              value={formData.applicant_name}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.applicant_name ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter your full name"
            />
            {errors.applicant_name && (
              <p className="mt-1 text-sm text-red-600">{errors.applicant_name}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label htmlFor="applicant_email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              id="applicant_email"
              name="applicant_email"
              value={formData.applicant_email}
              onChange={handleInputChange}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.applicant_email ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Enter your email address"
            />
            {errors.applicant_email && (
              <p className="mt-1 text-sm text-red-600">{errors.applicant_email}</p>
            )}
            
            {/* Duplicate Application Warning */}
            {duplicateCheck.isChecking && (
              <p className="mt-1 text-sm text-blue-600">Checking for existing applications...</p>
            )}
            {duplicateCheck.hasApplied && !duplicateCheck.isChecking && (
              <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">
                      You have already applied to this position
                    </h3>
                    <div className="mt-1 text-sm text-yellow-700">
                      <p>Each candidate can only apply once per job posting.</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Phone */}
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number *
            </label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleInputChange}
              pattern="[\+]?[1-9][\d\s\-\(\)]{7,20}"
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.phone ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="e.g., +1 (555) 123-4567 or 5551234567"
            />
            {errors.phone && (
              <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Enter a valid phone number (8-15 digits). International format accepted.
            </p>
          </div>

          {/* Why Join Company */}
          <div>
            <label htmlFor="cover_letter" className="block text-sm font-medium text-gray-700 mb-2">
              Why do you want to join our company? *
            </label>
            <textarea
              id="cover_letter"
              name="cover_letter"
              value={formData.cover_letter}
              onChange={handleInputChange}
              rows={6}
              className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.cover_letter ? 'border-red-300' : 'border-gray-300'
              }`}
              placeholder="Tell us why you want to join our company and what makes you excited about this opportunity..."
            />
            {errors.cover_letter && (
              <p className="mt-1 text-sm text-red-600">{errors.cover_letter}</p>
            )}
          </div>

          {/* Resume Upload */}
          <div>
            <label htmlFor="resume" className="block text-sm font-medium text-gray-700 mb-2">
              Resume/CV *
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-gray-400 transition-colors duration-200">
              <div className="space-y-1 text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="resume"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
                  >
                    <span>Upload a file</span>
                    <input
                      id="resume"
                      name="resume"
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileChange}
                      className="sr-only"
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">PDF, DOC, or DOCX up to 10MB</p>
                {formData.resume && (
                  <p className="text-sm text-green-600 font-medium">
                    ✓ {formData.resume.name}
                  </p>
                )}
              </div>
            </div>
            {errors.resume && (
              <p className="mt-1 text-sm text-red-600">{errors.resume}</p>
            )}
          </div>

          {/* CAPTCHA Verification */}
          {showCaptcha && (
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-gray-800 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-purple-600" />
                  Security Verification
                </h4>
                <button
                  onClick={generateCaptcha}
                  disabled={captchaLoading}
                  className="text-purple-600 hover:text-purple-700 disabled:text-purple-400"
                >
                  <RefreshCw className={`w-4 h-4 ${captchaLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>
              
              {!captchaVerified ? (
                <>
                  {/* CAPTCHA Image */}
                  <div className="bg-white rounded-lg p-2 mb-3 text-center">
                    {captchaData ? (
                      <img 
                        src={captchaData.image} 
                        alt="CAPTCHA" 
                        className="mx-auto"
                        style={{ imageRendering: 'crisp-edges' }}
                      />
                    ) : (
                      <div className="h-20 flex items-center justify-center">
                        <Loader className="w-6 h-6 animate-spin text-purple-600" />
                      </div>
                    )}
                  </div>
                  
                  {/* Input and Verify Button */}
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      placeholder="Enter the text above"
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      onKeyPress={(e) => e.key === 'Enter' && handleCaptchaVerify((e.target as HTMLInputElement).value)}
                      disabled={captchaLoading || !captchaData}
                      maxLength={8}
                    />
                    <button
                      onClick={() => {
                        const input = document.querySelector('input[placeholder="Enter the text above"]') as HTMLInputElement;
                        if (input) handleCaptchaVerify(input.value);
                      }}
                      disabled={captchaLoading || !captchaData}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-purple-400"
                    >
                      {captchaLoading ? (
                        <Loader className="w-5 h-5 animate-spin" />
                      ) : (
                        'Verify'
                      )}
                    </button>
                  </div>
                  
                  {/* Error Message */}
                  {captchaError && (
                    <p className="text-red-600 text-sm mt-2">{captchaError}</p>
                  )}
                  
                  {/* Help Text */}
                  <p className="text-xs text-gray-500 mt-2">
                    Type the characters you see in the image above. Letters are not case-sensitive.
                  </p>
                </>
              ) : (
                <div className="flex items-center text-green-600">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  <span className="font-medium">Verified successfully!</span>
                </div>
              )}
            </div>
          )}

          {/* Submit Button */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isSubmitting || (showCaptcha && !captchaVerified)}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Submitting Application...
                </div>
              ) : (
                'Submit Application'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApplicationForm;
