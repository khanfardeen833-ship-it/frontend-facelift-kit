# Manager Feedback Server

A standalone, secure feedback server for HRMS manager interview assessments.

## 🚀 Features

- **Standalone Server**: Runs independently from the main HRMS application
- **Premium UI**: Beautiful, modern interface with multi-step feedback form
- **Secure**: Dedicated server with its own database
- **Professional**: Comprehensive rating system and detailed feedback forms
- **Responsive**: Works on desktop and mobile devices

## 📋 Requirements

- Node.js (v14 or higher)
- npm or yarn

## 🛠️ Installation

1. **Navigate to the feedback server directory:**
   ```bash
   cd feedback-server
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the server:**
   ```bash
   npm start
   ```

   Or for development with auto-reload:
   ```bash
   npm run dev
   ```

## 🌐 Access

- **Feedback Form**: http://localhost:3002
- **API Health Check**: http://localhost:3002/api/health

## 📧 Email Integration

The feedback server is designed to work with email links from the HRMS system. When managers receive interview emails, they'll get links like:

```
http://localhost:3002/?interview_id=123&candidate_id=456&candidate_name=John%20Doe&candidate_email=john@example.com&job_title=Software%20Engineer&round_name=Technical%20Interview
```

## 🔧 Configuration

### Environment Variables

- `PORT`: Server port (default: 3003)
- `HRMS_BACKEND_URL`: Main HRMS backend URL (default: http://localhost:5000)

### Database

The server uses SQLite database (`feedback.db`) that is automatically created on first run.

## 📊 API Endpoints

### POST /api/submit-feedback
Submit manager feedback for a candidate.

**Request Body:**
```json
{
  "interview_id": 123,
  "candidate_id": "456",
  "candidate_name": "John Doe",
  "candidate_email": "john@example.com",
  "job_title": "Software Engineer",
  "round_name": "Technical Interview",
  "overall_rating": 5,
  "decision": "hire",
  "technical_skills": 4,
  "communication_skills": 5,
  "problem_solving": 4,
  "cultural_fit": 5,
  "strengths": "Strong technical skills and good communication",
  "areas_for_improvement": "Could improve in system design",
  "detailed_feedback": "Overall excellent candidate...",
  "recommendation": "Strong hire recommendation"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback_id": 1,
  "feedback_token": "feedback_1234567890_abc123"
}
```

### GET /api/feedback/:candidate_id
Get all feedback for a specific candidate.

**Response:**
```json
{
  "success": true,
  "data": {
    "feedback": [
      {
        "id": 1,
        "interview_id": 123,
        "candidate_id": "456",
        "overall_rating": 5,
        "decision": "hire",
        "submitted_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "success": true,
  "message": "Manager Feedback Server is running",
  "timestamp": "2024-01-15T10:30:00Z",
  "port": 3003
}
```

## 🎨 UI Features

### Multi-Step Form
1. **Overall Assessment**: Overall rating and hiring decision
2. **Detailed Ratings**: Technical skills, communication, problem solving, cultural fit
3. **Written Feedback**: Strengths, areas for improvement, detailed feedback, recommendations
4. **Final Review**: Review all feedback before submission

### Premium Design
- Modern gradient backgrounds
- Smooth animations and transitions
- Star rating system
- Responsive design
- Professional color scheme

## 🔒 Security

- CORS enabled for cross-origin requests
- Input validation and sanitization
- Secure database operations
- Error handling and logging

## 🔄 Integration with HRMS

The feedback server automatically sends submitted feedback to the main HRMS backend at `http://localhost:5000/api/manager-feedback/submit` to keep both systems in sync.

## 🚀 Deployment

For production deployment:

1. Set environment variables
2. Use a process manager like PM2
3. Set up reverse proxy (nginx)
4. Configure SSL certificates
5. Set up monitoring and logging

## 📝 Development

To modify the feedback form:

1. Edit `public/index.html` for UI changes
2. Edit `server.js` for API changes
3. Restart the server to see changes

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**: Change the PORT environment variable
2. **Database errors**: Delete `feedback.db` to recreate the database
3. **CORS issues**: Check the CORS configuration in `server.js`

### Logs

Check the console output for error messages and debugging information.

## 📞 Support

For issues or questions, contact the HRMS development team.
