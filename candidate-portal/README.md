# Candidate Portal

A separate portal for job candidates to browse and apply for jobs without requiring login authentication.

## Features

- **No Login Required**: Candidates can browse and apply for jobs without creating accounts
- **Job Browsing**: Search and filter through available job positions
- **Detailed Job Views**: Comprehensive job descriptions with requirements and skills
- **Easy Application**: Simple application form with resume upload
- **Responsive Design**: Works on desktop and mobile devices

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   cd Frontend/candidate-portal
   npm install
   ```

2. **Start Development Server**:
   ```bash
   npm start
   ```

3. **Build for Production**:
   ```bash
   npm run build
   ```

## API Configuration

The candidate portal connects to the backend API. Make sure to update the API base URL in `src/App.tsx`:

```typescript
const API_BASE_URL = 'http://localhost:5000'; // Update this to match your backend
```

## Routes

- `/` - Job listing page with search and filters
- `/job/:id` - Detailed job view
- `/apply/:jobId` - Application form for a specific job

## Components

- **Header**: Navigation and branding
- **JobList**: Main job browsing interface with search and filters
- **JobDetail**: Comprehensive job information display
- **ApplicationForm**: Job application form with file upload
- **Footer**: Site footer with links and contact information

## Features

### Job Browsing
- Search jobs by title, company, or keywords
- Filter by location and job type
- Responsive job cards with key information

### Job Details
- Complete job description
- Requirements and skills lists
- Company information
- Easy application button

### Application Process
- Simple form with required fields
- Resume/CV upload support
- Cover letter submission
- Form validation and error handling

## Backend Integration

The candidate portal uses the following backend endpoints:

- `GET /api/jobs/approved` - Fetch available jobs
- `POST /api/tickets/:id/resumes` - Submit job application

## Styling

Built with Tailwind CSS for responsive and modern design.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
