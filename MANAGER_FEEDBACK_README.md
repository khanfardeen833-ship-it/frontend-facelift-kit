# Manager Feedback System

A premium SaaS-style manager feedback system for interview assessments with comprehensive rating, detailed feedback, and professional presentation.

## 🚀 Features

### Premium UI/UX
- **Multi-step feedback form** with progress indicators
- **Comprehensive rating system** (Technical, Communication, Problem Solving, Cultural Fit)
- **Professional design** with gradients, animations, and modern styling
- **Responsive layout** that works on all devices
- **Real-time validation** and form status indicators

### Comprehensive Assessment
- **Overall rating** (1-5 stars)
- **Detailed skill ratings** for each competency area
- **Hiring decision** (Strong Hire, Hire, Maybe, No Hire)
- **Team fit assessment** with detailed options
- **Salary expectation evaluation**
- **Start date availability**
- **Detailed feedback sections**:
  - Key strengths
  - Areas for improvement
  - Comprehensive assessment
  - Final recommendation

### Email Integration
- **Automatic email notifications** to managers with feedback links
- **Professional email templates** with clear instructions
- **Direct links** to the feedback form
- **Interview details** included in emails

### Candidate Visibility
- **Professional feedback display** in candidate status view
- **Rating breakdowns** with visual indicators
- **Detailed feedback sections** with color-coded categories
- **Manager assessment cards** with timestamps
- **Transparent feedback** visible to candidates

## 🏗️ Architecture

### Frontend Components
- `ManagerFeedbackForm.jsx` - Main feedback submission form
- `ManagerFeedbackPage.jsx` - Standalone feedback page
- `CandidateInterviewStatus.jsx` - Updated to show manager feedback
- `InterviewScheduler.jsx` - Updated with feedback integration

### Backend API
- `manager_feedback_api.py` - Complete REST API for feedback management
- `interview_email_service.py` - Updated with manager feedback links
- `server.py` - Updated to register manager feedback endpoints

### Database Schema
```sql
CREATE TABLE manager_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interview_id INTEGER,
    candidate_id TEXT,
    candidate_name TEXT,
    candidate_email TEXT,
    job_title TEXT,
    round_name TEXT,
    
    -- Overall Assessment
    overall_rating INTEGER,
    decision TEXT,
    
    -- Detailed Ratings
    technical_skills INTEGER,
    communication_skills INTEGER,
    problem_solving INTEGER,
    cultural_fit INTEGER,
    leadership_potential INTEGER,
    
    -- Feedback Text
    strengths TEXT,
    areas_for_improvement TEXT,
    detailed_feedback TEXT,
    recommendation TEXT,
    
    -- Additional Info
    would_hire_again BOOLEAN,
    team_fit TEXT,
    salary_expectation TEXT,
    start_date TEXT,
    
    -- Metadata
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_by TEXT,
    feedback_token TEXT UNIQUE,
    
    FOREIGN KEY (interview_id) REFERENCES interview_schedules (id)
);
```

## 🚀 Getting Started

### 1. Backend Setup
```bash
cd Backend
python server.py
```

### 2. Frontend Setup
```bash
cd hrmshiring-main
npm start
```

### 3. Test the System
```bash
cd Backend
python test_manager_feedback.py
```

## 📧 Email Flow

1. **Interview Scheduled** → Email sent to managers with feedback link
2. **Manager Clicks Link** → Opens premium feedback form
3. **Feedback Submitted** → Stored in database with unique token
4. **Candidate Views Status** → Sees professional feedback display

## 🎨 UI Components

### Manager Feedback Form
- **Step 1**: Overall Assessment with star ratings
- **Step 2**: Hiring Decision with team fit evaluation
- **Step 3**: Detailed Feedback with text areas
- **Step 4**: Final Review with summary

### Candidate Status View
- **Manager Feedback Section** with gradient background
- **Rating Breakdown** with color-coded metrics
- **Feedback Cards** with professional styling
- **Additional Info** with team fit, salary, and start date

## 🔧 API Endpoints

### Submit Feedback
```http
POST /api/manager-feedback
Content-Type: application/json
X-API-Key: sk-hiring-bot-2024-secret-key-xyz789

{
  "interview_id": "123",
  "candidate_id": "456",
  "candidate_name": "John Doe",
  "candidate_email": "john@example.com",
  "job_title": "Software Engineer",
  "round_name": "Technical Interview",
  "overall_rating": 4,
  "decision": "hire",
  "technical_skills": 5,
  "communication_skills": 4,
  "problem_solving": 4,
  "cultural_fit": 5,
  "strengths": "Excellent technical skills...",
  "areas_for_improvement": "Could improve...",
  "detailed_feedback": "Comprehensive assessment...",
  "recommendation": "Strong recommendation...",
  "team_fit": "excellent",
  "salary_expectation": "within_budget",
  "start_date": "2_weeks"
}
```

### Get Feedback by Candidate
```http
GET /api/manager-feedback/{candidate_id}?ticket_id={ticket_id}
X-API-Key: sk-hiring-bot-2024-secret-key-xyz789
```

### Get Feedback by Token
```http
GET /api/manager-feedback/token/{feedback_token}
X-API-Key: sk-hiring-bot-2024-secret-key-xyz789
```

### Update Feedback
```http
PUT /api/manager-feedback/{feedback_id}
Content-Type: application/json
X-API-Key: sk-hiring-bot-2024-secret-key-xyz789

{
  "overall_rating": 5,
  "decision": "strong_hire",
  "recommendation": "Updated recommendation..."
}
```

### Get Statistics
```http
GET /api/manager-feedback/stats
X-API-Key: sk-hiring-bot-2024-secret-key-xyz789
```

## 🎯 Usage Examples

### 1. Schedule Interview with Manager Feedback
1. Go to Applications tab
2. Select a candidate
3. Click "Schedule Interview"
4. Add participants with email addresses
5. Schedule the interview
6. Managers receive emails with feedback links

### 2. Submit Manager Feedback
1. Manager receives email with feedback link
2. Clicks link to open feedback form
3. Completes 4-step feedback process
4. Submits comprehensive assessment
5. Feedback is stored and visible to candidate

### 3. View Manager Feedback
1. Go to candidate status view
2. See "Manager Feedback" section
3. View detailed ratings and feedback
4. See professional assessment cards

## 🔒 Security Features

- **API Key Authentication** for all endpoints
- **Unique Feedback Tokens** for secure access
- **Input Validation** on all form fields
- **SQL Injection Protection** with parameterized queries
- **XSS Protection** with proper escaping

## 📊 Analytics & Reporting

- **Feedback Statistics** endpoint for analytics
- **Decision Tracking** with counts by decision type
- **Average Ratings** across all competencies
- **Submission Timestamps** for tracking

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (#3B82F6 to #8B5CF6)
- **Success**: Green (#10B981)
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Info**: Blue (#3B82F6)

### Typography
- **Headings**: Inter, font-weight: 600-700
- **Body**: Inter, font-weight: 400-500
- **Code**: JetBrains Mono

### Components
- **Cards**: Rounded corners, subtle shadows
- **Buttons**: Gradient backgrounds, hover effects
- **Forms**: Clean inputs with focus states
- **Icons**: Lucide React icons

## 🚀 Future Enhancements

- **Feedback Templates** for different roles
- **Bulk Feedback** for multiple candidates
- **Feedback Analytics Dashboard**
- **Integration with HR Systems**
- **Mobile App** for feedback submission
- **Real-time Notifications**
- **Feedback Comparison Tools**

## 🐛 Troubleshooting

### Common Issues

1. **Feedback not appearing in candidate view**
   - Check if feedback was submitted successfully
   - Verify candidate ID matches
   - Check browser console for errors

2. **Email links not working**
   - Verify backend server is running
   - Check email configuration
   - Ensure correct URL format

3. **Form validation errors**
   - Check all required fields are filled
   - Verify email format
   - Ensure ratings are within 1-5 range

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG_MANAGER_FEEDBACK=true
```

## 📝 License

This project is part of the HR Management System and follows the same licensing terms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation
- Test with the provided test script
