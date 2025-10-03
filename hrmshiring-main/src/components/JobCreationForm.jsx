import React, { useState } from 'react';
import { 
  Briefcase, 
  MapPin, 
  DollarSign, 
  Clock, 
  User, 
  FileText, 
  Send,
  Loader,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { makeAPICall } from '../config/api';
import { formatDateForInput, formatDateForStorage, getMinDateForInput } from '../utils/dateUtils';
import CustomDateInput from './CustomDateInput';

const JobCreationForm = ({ onJobCreated, editingJob = null }) => {
  const [formData, setFormData] = useState({
    job_title: editingJob?.job_title || '',
    location: editingJob?.location || '',
    employment_type: editingJob?.employment_type || 'Full-time',
    experience_required: editingJob?.experience_required || '',
    salary_range: editingJob?.salary_range || '',
    job_description: editingJob?.job_description || '',
    skills_required: editingJob?.required_skills || editingJob?.skills_required || '',
    deadline: formatDateForInput(editingJob?.deadline) || '',
    contact_phone: editingJob?.contact_phone || ''
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Format the data similar to what the chatbot would send
      const jobData = {
        job_title: formData.job_title,
        company_name: 'Your Company', // Default company name
        location: formData.location,
        employment_type: formData.employment_type,
        experience_required: formData.experience_required,
        salary_range: formData.salary_range,
        job_description: formData.job_description,
        skills_required: formData.skills_required,
        deadline: formatDateForStorage(formData.deadline),
        contact_phone: formData.contact_phone,
        status: 'active'
      };

      const isEditing = editingJob && editingJob.ticket_id;
      const url = isEditing ? `/api/jobs/${editingJob.ticket_id}` : '/api/jobs';
      const method = isEditing ? 'PUT' : 'POST';

      console.log(`${isEditing ? 'Updating' : 'Creating'} job with data:`, jobData);

      const response = await makeAPICall(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(jobData)
      });

      console.log(`Job ${isEditing ? 'update' : 'creation'} response:`, response);

      if (response.success) {
        setSuccess(true);
        setTimeout(() => {
          onJobCreated();
        }, 2000);
      } else {
        setError(response.message || `Failed to ${isEditing ? 'update' : 'create'} job posting`);
      }
    } catch (err) {
      console.error(`Error ${editingJob ? 'updating' : 'creating'} job:`, err);
      setError(`Failed to ${editingJob ? 'update' : 'create'} job posting. Please try again.`);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    const isEditing = editingJob && editingJob.ticket_id;
    return (
      <div className="text-center py-12">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h3 className="text-2xl font-bold text-gray-800 mb-2">
          Job {isEditing ? 'Updated' : 'Created'} Successfully!
        </h3>
        <p className="text-gray-600">
          Your job posting has been {isEditing ? 'updated' : 'created'} and is now live.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Quick Navigation */}
      <div className="sticky top-0 bg-white p-4 border border-gray-200 rounded-lg shadow-sm z-10">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            <span className="font-medium">📝</span> Fill out all required fields below
          </div>
          <button
            type="button"
            onClick={() => {
              const submitButton = document.querySelector('button[type="submit"]');
              if (submitButton) {
                submitButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
              }
            }}
            className="text-xs text-blue-600 bg-blue-100 px-3 py-1 rounded-full border border-blue-300 hover:bg-blue-200 transition-colors"
          >
            🚀 Jump to Submit
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Basic Job Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Briefcase className="w-4 h-4 inline mr-1" />
            Job Title *
          </label>
          <input
            type="text"
            name="job_title"
            value={formData.job_title}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., Senior Software Engineer"
          />
        </div>


        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <MapPin className="w-4 h-4 inline mr-1" />
            Location *
          </label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., New York, NY or Remote"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="w-4 h-4 inline mr-1" />
            Employment Type *
          </label>
          <select
            name="employment_type"
            value={formData.employment_type}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
            <option value="Internship">Internship</option>
            <option value="Freelance">Freelance</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <User className="w-4 h-4 inline mr-1" />
            Experience Required *
          </label>
          <input
            type="text"
            name="experience_required"
            value={formData.experience_required}
            onChange={handleInputChange}
            required
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., 3-5 years or Entry Level"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <DollarSign className="w-4 h-4 inline mr-1" />
            Salary Range
          </label>
          <input
            type="text"
            name="salary_range"
            value={formData.salary_range}
            onChange={handleInputChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="e.g., $60,000 - $80,000 or Competitive"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="w-4 h-4 inline mr-1" />
            Application Deadline
          </label>
          <CustomDateInput
            value={formData.deadline}
            onChange={(value) => setFormData(prev => ({ ...prev, deadline: value }))}
            placeholder="dd/mm/yyyy"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

      </div>

      {/* Skills Required */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <FileText className="w-4 h-4 inline mr-1" />
          Skills Required *
        </label>
        <textarea
          name="skills_required"
          value={formData.skills_required}
          onChange={handleInputChange}
          required
          rows={3}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="e.g., JavaScript, React, Node.js, Python, SQL"
        />
        <p className="text-sm text-gray-500 mt-1">Separate skills with commas</p>
      </div>

      {/* Job Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <FileText className="w-4 h-4 inline mr-1" />
          Job Description *
        </label>
        <textarea
          name="job_description"
          value={formData.job_description}
          onChange={handleInputChange}
          required
          rows={6}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Describe the role, responsibilities, and what makes this position exciting..."
        />
      </div>


      {/* Submit Button */}
      <div className="sticky bottom-0 bg-white p-6 border-t border-gray-200 shadow-lg rounded-t-lg mt-8">
        <div className="flex justify-end items-center">
          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => onJobCreated()}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-semibold flex items-center space-x-2 transition-colors shadow-md hover:shadow-lg transform hover:scale-105"
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>{editingJob ? 'Updating Job...' : 'Creating Job...'}</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>{editingJob ? 'Update Job Posting' : 'Create Job Posting'}</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
};

export default JobCreationForm;
