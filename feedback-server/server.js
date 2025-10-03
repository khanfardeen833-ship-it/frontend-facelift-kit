const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Database setup
const dbPath = path.join(__dirname, 'feedback.db');
const db = new sqlite3.Database(dbPath);

// Initialize database
db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS manager_feedback (
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
      feedback_token TEXT UNIQUE
    )
  `);
});

// Main feedback form page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API endpoint to submit feedback
app.post('/api/submit-feedback', async (req, res) => {
  try {
    const {
      interview_id,
      candidate_id,
      candidate_name,
      candidate_email,
      job_title,
      round_name,
      overall_rating,
      decision,
      technical_skills,
      communication_skills,
      problem_solving,
      cultural_fit,
      leadership_potential,
      strengths,
      areas_for_improvement,
      detailed_feedback,
      recommendation,
      would_hire_again,
      team_fit,
      salary_expectation,
      start_date,
      submitted_by
    } = req.body;

    // Validate required fields
    if (!overall_rating || !decision) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: overall_rating and decision are required'
      });
    }

    // Generate unique feedback token
    const feedback_token = `feedback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Insert feedback into database
    const stmt = db.prepare(`
      INSERT INTO manager_feedback (
        interview_id, candidate_id, candidate_name, candidate_email, job_title, round_name,
        overall_rating, decision, technical_skills, communication_skills, problem_solving,
        cultural_fit, leadership_potential, strengths, areas_for_improvement, detailed_feedback,
        recommendation, would_hire_again, team_fit, salary_expectation, start_date,
        submitted_by, feedback_token
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    stmt.run([
      interview_id, candidate_id, candidate_name, candidate_email, job_title, round_name,
      overall_rating, decision, technical_skills, communication_skills, problem_solving,
      cultural_fit, leadership_potential, strengths, areas_for_improvement, detailed_feedback,
      recommendation, would_hire_again, team_fit, salary_expectation, start_date,
      submitted_by, feedback_token
    ], function(err) {
      if (err) {
        console.error('Database error:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to save feedback'
        });
      }

      // Send feedback to main HRMS backend (async, don't wait for it)
      sendFeedbackToHRMS({
        id: this.lastID,
        interview_id,
        candidate_id,
        candidate_name,
        candidate_email,
        job_title,
        round_name,
        overall_rating,
        decision,
        technical_skills,
        communication_skills,
        problem_solving,
        cultural_fit,
        leadership_potential,
        strengths,
        areas_for_improvement,
        detailed_feedback,
        recommendation,
        would_hire_again,
        team_fit,
        salary_expectation,
        start_date,
        submitted_by,
        feedback_token,
        submitted_at: new Date().toISOString()
      }).catch(error => {
        console.error('Background sync to HRMS failed:', error.message);
        // Don't fail the main request if background sync fails
      });

      res.json({
        success: true,
        message: 'Feedback submitted successfully',
        feedback_id: this.lastID,
        feedback_token
      });
    });

    stmt.finalize();

  } catch (error) {
    console.error('Error submitting feedback:', error);
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
});

// Function to send feedback to main HRMS backend
async function sendFeedbackToHRMS(feedbackData) {
  try {
    console.log('Sending feedback to HRMS backend:', feedbackData);
    const response = await axios.post('http://localhost:5000/api/manager-feedback', feedbackData, {
      headers: {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
      }
    });
    console.log('Feedback sent to HRMS backend successfully:', response.data);
  } catch (error) {
    console.error('Failed to send feedback to HRMS backend:', error.message);
    console.error('Error details:', error.response?.data || error.message);
    // Don't fail the main request if this fails
  }
}

// API endpoint to get feedback by candidate
app.get('/api/feedback/:candidate_id', (req, res) => {
  const { candidate_id } = req.params;
  
  db.all(
    'SELECT * FROM manager_feedback WHERE candidate_id = ? ORDER BY submitted_at DESC',
    [candidate_id],
    (err, rows) => {
      if (err) {
        console.error('Database error:', err);
        return res.status(500).json({
          success: false,
          error: 'Failed to fetch feedback'
        });
      }

      res.json({
        success: true,
        data: { feedback: rows }
      });
    }
  );
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'Manager Feedback Server is running',
    timestamp: new Date().toISOString(),
    port: PORT
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Manager Feedback Server running on http://localhost:${PORT}`);
  console.log(`📝 Feedback form available at: http://localhost:${PORT}`);
  console.log(`🔗 API endpoints:`);
  console.log(`   - POST /api/submit-feedback`);
  console.log(`   - GET /api/feedback/:candidate_id`);
  console.log(`   - GET /api/health`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down Manager Feedback Server...');
  db.close((err) => {
    if (err) {
      console.error('Error closing database:', err);
    } else {
      console.log('✅ Database connection closed');
    }
    process.exit(0);
  });
});
