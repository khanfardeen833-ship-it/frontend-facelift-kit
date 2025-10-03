import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, Clock, DollarSign, Building, Calendar, ArrowLeft } from 'lucide-react';
import { Job } from '../App';

// Date formatting utility for DD/MM/YYYY format
const formatDateForDisplay = (dateInput: string | Date) => {
  if (!dateInput) return 'Not specified';
  
  try {
    const date = new Date(dateInput);
    if (isNaN(date.getTime())) {
      return dateInput.toString();
    }
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    
    return `${day}/${month}/${year}`;
  } catch (error) {
    console.error('Error formatting date for display:', error);
    return dateInput.toString();
  }
};

interface JobDetailProps {
  jobs: Job[];
}

const JobDetail: React.FC<JobDetailProps> = ({ jobs }) => {
  const { id } = useParams<{ id: string }>();
  const job = jobs.find(j => j.id === id);

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

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <div className="mb-6">
        <Link
          to="/"
          className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors duration-200"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Jobs</span>
        </Link>
      </div>

      {/* Job Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center">
              <Building className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
            </div>
          </div>
          
          <Link
            to={`/apply/${job.id}`}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium text-lg"
          >
            Apply Now
          </Link>
        </div>

        {/* Job Meta */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="flex items-center space-x-3">
            <MapPin className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Location</p>
              <p className="font-medium text-gray-900">{job.location}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Job Type</p>
              <p className="font-medium text-gray-900">{job.type}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <DollarSign className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Salary</p>
              <p className="font-medium text-gray-900">{job.salary}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Calendar className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm text-gray-500">Posted</p>
              <p className="font-medium text-gray-900">
                {formatDateForDisplay(job.created_at)}
              </p>
            </div>
          </div>
        </div>

        {/* Experience */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Experience Required</h3>
          <p className="text-gray-700">{job.experience}</p>
        </div>
      </div>

      {/* Job Description */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Job Description</h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {job.description}
          </p>
        </div>
      </div>


      {/* Skills */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Required Skills</h2>
        <div className="flex flex-wrap gap-3">
          {job.skills.map((skill, index) => (
            <span
              key={index}
              className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>

      {/* Apply CTA */}
      <div className="bg-blue-50 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Ready to Apply?
        </h2>
        <p className="text-gray-600 mb-6">
          Submit your application for the {job.title} position
        </p>
        <Link
          to={`/apply/${job.id}`}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium text-lg inline-block"
        >
          Apply for this Position
        </Link>
      </div>
    </div>
  );
};

export default JobDetail;
