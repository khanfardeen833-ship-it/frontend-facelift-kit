# Interview Calendar Feature - Premium HRMS Feature

## 🎯 Overview

The Interview Calendar is a premium feature that provides HR managers with a comprehensive view of all candidate interviews scheduled across the organization. This feature includes both a full calendar view and a dashboard widget for quick access to upcoming interviews.

## ✨ Features

### 1. **Full Calendar View**
- **Monthly Calendar Grid**: Interactive calendar showing all scheduled interviews
- **Interview Details**: Click on any interview to view comprehensive details
- **Status Indicators**: Visual status badges (Scheduled, In Progress, Completed)
- **Interview Types**: Icons for Video Call, Phone Call, and In-Person interviews
- **Navigation**: Easy month-to-month navigation with "Today" quick access
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### 2. **Dashboard Widget**
- **Upcoming Interviews**: Shows next 5 interviews for today and tomorrow
- **Quick Access**: Direct access to meeting links
- **Compact View**: Space-efficient display on the main dashboard
- **Real-time Updates**: Automatically refreshes with latest interview data

### 3. **Premium UI/UX**
- **Modern Design**: Gradient backgrounds and smooth animations
- **Premium Badge**: Star icon indicating premium feature status
- **Interactive Elements**: Hover effects and smooth transitions
- **Professional Color Scheme**: Blue and purple gradients for premium feel

## 🏗️ Technical Implementation

### Backend API Endpoint

**Endpoint**: `GET /api/interviews/calendar`

**Response Format**:
```json
{
  "success": true,
  "events": [
    {
      "id": 1,
      "title": "John Doe - Technical Round",
      "start": "2024-01-15 14:00",
      "duration": 60,
      "candidate_name": "John Doe",
      "candidate_email": "john@example.com",
      "round_name": "Technical Round",
      "interview_type": "video_call",
      "meeting_link": "https://meet.google.com/...",
      "status": "scheduled",
      "interviewer_names": "Sarah Johnson, Mike Wilson",
      "job_title": "Senior Developer",
      "ticket_id": "abc123"
    }
  ],
  "total": 5
}
```

### Database Schema

The feature uses the existing `interview_schedules` table with the following key fields:
- `scheduled_date`: Interview date
- `scheduled_time`: Interview time
- `candidate_name`: Candidate's full name
- `round_name`: Interview round (from `interview_rounds` table)
- `interview_type`: Type of interview (video_call, phone_call, in_person)
- `meeting_link`: Google Meet or other meeting URL
- `status`: Current status (scheduled, in_progress, completed)

### Frontend Components

1. **InterviewCalendar.jsx**: Main calendar component with full calendar view
2. **UpcomingInterviewsWidget.jsx**: Dashboard widget for upcoming interviews
3. **Sidebar.jsx**: Updated to include calendar access button

## 🚀 Installation & Setup

### 1. Backend Setup

The calendar API endpoint is already integrated into the main `server.py` file. No additional setup required.

### 2. Frontend Setup

The components are already integrated into the React application:

1. **InterviewCalendar.jsx** - Full calendar modal
2. **UpcomingInterviewsWidget.jsx** - Dashboard widget
3. **Updated Sidebar.jsx** - Calendar access button

### 3. Database Setup

Ensure your database has interview data by running:
```bash
cd Backend
python init_interview_db.py
```

## 🎨 UI/UX Features

### Premium Design Elements
- **Gradient Headers**: Blue to purple gradients for premium feel
- **Star Badges**: Gold star icons indicating premium features
- **Smooth Animations**: Framer Motion animations for interactions
- **Professional Typography**: Clean, modern font choices
- **Consistent Spacing**: Proper padding and margins throughout

### Interactive Elements
- **Hover Effects**: Subtle hover animations on calendar events
- **Click Interactions**: Detailed interview modals on event click
- **Responsive Grid**: Adapts to different screen sizes
- **Status Colors**: Color-coded status indicators
- **Meeting Links**: Direct access to video meeting rooms

## 📱 Responsive Design

The calendar feature is fully responsive:
- **Desktop**: Full calendar grid with detailed event information
- **Tablet**: Optimized grid layout with touch-friendly interactions
- **Mobile**: Stacked layout with simplified event display

## 🔧 Customization Options

### Calendar View
- **View Types**: Month, week, day views (extensible)
- **Filter Options**: Filter by status, interview type, or date range
- **Color Themes**: Easily customizable color schemes
- **Event Limits**: Configurable number of events per day

### Dashboard Widget
- **Event Count**: Configurable number of upcoming interviews to display
- **Time Range**: Adjustable time window (today, tomorrow, next week)
- **Display Options**: Show/hide different event details

## 🔒 Security & Permissions

- **API Authentication**: Requires valid API key for access
- **User Roles**: Calendar access limited to HR managers
- **Data Privacy**: Only displays necessary interview information
- **Secure Links**: Meeting links are validated and secure

## 📊 Performance Considerations

- **Lazy Loading**: Calendar events loaded on demand
- **Efficient Queries**: Optimized database queries for fast loading
- **Caching**: Client-side caching of interview data
- **Pagination**: Large datasets handled efficiently

## 🧪 Testing

### API Testing
Run the test script to verify the API endpoint:
```bash
python test_calendar_api.py
```

### Frontend Testing
The components include:
- **Loading States**: Proper loading indicators
- **Error Handling**: Graceful error messages
- **Empty States**: User-friendly empty state messages

## 🚀 Future Enhancements

### Planned Features
1. **Calendar Integration**: Sync with Google Calendar, Outlook
2. **Interview Scheduling**: Direct scheduling from calendar view
3. **Reminder System**: Email/SMS reminders for upcoming interviews
4. **Analytics**: Interview statistics and trends
5. **Bulk Operations**: Bulk interview management
6. **Recurring Interviews**: Support for recurring interview series
7. **Time Zone Support**: Multi-timezone interview scheduling
8. **Interview Templates**: Pre-configured interview types

### Advanced Features
- **AI-Powered Scheduling**: Smart scheduling suggestions
- **Conflict Detection**: Automatic conflict resolution
- **Resource Management**: Room and equipment booking
- **Interview Recording**: Integration with recording services
- **Feedback Integration**: Post-interview feedback collection

## 📝 Usage Examples

### Accessing the Calendar
1. Click the "Interview Calendar" button in the sidebar
2. The full calendar modal will open
3. Navigate between months using arrow buttons
4. Click on any interview event for details

### Dashboard Widget
1. The upcoming interviews widget appears on the main dashboard
2. Shows next 5 interviews for today and tomorrow
3. Click meeting links to join video calls directly
4. Widget updates automatically with new interviews

## 🐛 Troubleshooting

### Common Issues
1. **No Interviews Showing**: Check if interview data exists in database
2. **API Errors**: Verify backend server is running and accessible
3. **Styling Issues**: Ensure Tailwind CSS is properly configured
4. **Performance**: Check for large datasets causing slow loading

### Debug Steps
1. Check browser console for JavaScript errors
2. Verify API endpoint responses in Network tab
3. Confirm database has interview data
4. Test API endpoint directly with curl or Postman

## 📞 Support

For technical support or feature requests:
1. Check the main HRMS documentation
2. Review the API documentation
3. Contact the development team
4. Submit issues through the project repository

---

**Note**: This is a premium feature and requires proper licensing for production use. The feature demonstrates advanced HRMS capabilities and modern UI/UX design principles.
