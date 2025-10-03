import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import JobList from './components/JobList';
import JobDetail from './components/JobDetail';
import ApplicationForm from './components/ApplicationForm';
import TestSetup from './components/TestSetup';

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  type: string;
  salary: string;
  description: string;
  skills: string[];
  experience: string;
  created_at: string;
  status: string;
}

// Main App Component with Router
function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch jobs from backend API
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        setError(null);
        
        console.log('🔍 Fetching jobs from API...');
        console.log('📍 API URL:', 'http://localhost:5000/api/jobs/approved');
        console.log('🔑 API Key:', 'sk-hiring-bot-2024-secret-key-xyz789');
        
        const response = await fetch('http://localhost:5000/api/jobs/approved', {
          method: 'GET',
          headers: {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
          }
        });

        console.log('📡 API Response status:', response.status);
        console.log('📡 API Response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ API Error:', errorText);
          throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('📦 API Response data:', result);
        
        if (result.success && result.data && result.data.jobs) {
          console.log('✅ Jobs found:', result.data.jobs.length);
          // Transform backend job data to frontend format
          const transformedJobs: Job[] = result.data.jobs.map((job: any) => ({
            id: job.ticket_id,
            title: job.job_title || 'Software Engineer',
            company: job.sender || 'TechCorp',
            location: job.location || 'San Francisco, CA',
            type: job.employment_type || 'Full-time',
            salary: job.salary_range || '$80,000 - $120,000',
            description: job.job_description || 'We are looking for talented individuals to join our team.',
            skills: job.required_skills ? job.required_skills.split(',') : ['JavaScript', 'React', 'Node.js'],
            experience: job.experience_required || '2+ years',
            created_at: job.created_at || '2024-01-15',
            status: job.status || 'active'
          }));
          
          console.log('✅ Transformed jobs:', transformedJobs);
          setJobs(transformedJobs);
        } else {
          console.log('⚠️ No jobs found in response:', result);
          setJobs([]);
        }
      } catch (error) {
        console.error('💥 Error fetching jobs:', error);
        setError(error instanceof Error ? error.message : 'Failed to fetch jobs');
        setJobs([]);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setError(null);
    // Simulate refresh
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={
              <div>
                <div className="text-center mb-8">
                  {/* <h1 className="text-4xl font-bold text-gray-800 mb-4">Find Your Dream Job</h1> */}
                  {/* <p className="text-xl text-gray-600">Browse through our latest job opportunities and apply today!</p> */}
                </div>
                <JobList 
                  jobs={jobs} 
                  loading={loading} 
                  error={error} 
                  onRefresh={handleRefresh}
                />
              </div>
            } />
            
                         <Route path="/job/:id" element={<JobDetail jobs={jobs} />} />
             <Route path="/apply/:jobId" element={<ApplicationForm jobs={jobs} />} />
             <Route path="/test-setup" element={<TestSetup />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
