#!/usr/bin/env python3
"""
AI Chat Bot with Unified Database and Language Detection
Modified to share database with Email Bot
Updated to use OpenAI API with language detection feature
"""

import re
import json
from datetime import datetime, timedelta
import hashlib
from typing import Dict, List, Tuple, Optional, Any
import autogen
from autogen import AssistantAgent
import logging
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import secrets
import uuid
import os
from dotenv import load_dotenv
import time
from functools import lru_cache

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# PERFORMANCE OPTIMIZATION - CACHING
# ============================================================================

class ResponseCache:
    """Simple in-memory cache for AI responses"""
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
    
    def get(self, key):
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def clear(self):
        self.cache.clear()
        self.access_times.clear()

# Global cache instance
response_cache = ResponseCache()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    # OpenAI API Configuration (SAME AS EMAIL BOT)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_API_BASE = "https://api.openai.com/v1"
    
    # MySQL Configuration (SAME AS EMAIL BOT)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "hiring_bot")  # Same database as email bot
    
    # Debug Mode
    DEBUG_MODE = True  # Allows instant ticket approval in chat
    
    # Required hiring details
    REQUIRED_HIRING_DETAILS = [
        "job_title", "location", "experience_required", "salary_range",
        "job_description", "required_skills", "employment_type", "deadline"
    ]

# Validate configuration
if not Config.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables!")

# AutoGen LLM Configuration for OpenAI - OPTIMIZED FOR SPEED
llm_config = {
    "config_list": [{
        "model": Config.OPENAI_MODEL,
        "api_key": Config.OPENAI_API_KEY,
        "base_url": Config.OPENAI_API_BASE,
        "api_type": "openai",
    }],
    "temperature": 0.1,
    "seed": 42,
    "cache_seed": None,
    "timeout": 30,  # Reduced from 120 to 30 seconds
    "max_tokens": 300,  # Reduced from 1000 to 300 for faster responses
}

# Fast LLM config for simple tasks
fast_llm_config = {
    "config_list": [{
        "model": "gpt-4o",  # Use GPT-4o for better responses
        "api_key": Config.OPENAI_API_KEY,
        "base_url": Config.OPENAI_API_BASE,
        "api_type": "openai",
    }],
    "temperature": 0.1,
    "timeout": 15,  # Even faster timeout
    "max_tokens": 150,  # Smaller responses
}

# ============================================================================
# UNIFIED DATABASE MANAGER (SHARED WITH EMAIL BOT)
# ============================================================================

class DatabaseManager:
    """Manages MySQL database connections - shared structure with email bot"""
    
    def __init__(self):
        self.config = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DATABASE
        }
        try:
            self.setup_database()
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            logger.error("Please ensure MySQL server is running and accessible")
            logger.error("You can start MySQL with: sudo service mysql start (Linux) or start MySQL service (Windows)")
            # Continue without database for now
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            yield conn
        except Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def setup_database(self):
        """Create database and tables if they don't exist - unified schema"""
        config_without_db = self.config.copy()
        db_name = config_without_db.pop('database')
        
        conn = None
        cursor = None
        
        try:
            conn = mysql.connector.connect(**config_without_db)
            cursor = conn.cursor()
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            cursor.execute(f"USE {db_name}")
            
            # Create unified tickets table (shared with email bot)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id VARCHAR(10) PRIMARY KEY,
                    source ENUM('email', 'chat') DEFAULT 'email',
                    sender VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255),
                    subject TEXT,
                    session_id VARCHAR(36),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'new',
                    approval_status VARCHAR(50) DEFAULT 'pending',
                    approved BOOLEAN DEFAULT FALSE,
                    approved_at DATETIME,
                    approval_token VARCHAR(32),
                    terminated_at DATETIME,
                    terminated_by VARCHAR(255),
                    termination_reason TEXT,
                    rejected_at DATETIME,
                    rejection_reason TEXT,
                    INDEX idx_sender (sender),
                    INDEX idx_user_id (user_id),
                    INDEX idx_status (status),
                    INDEX idx_approval_status (approval_status),
                    INDEX idx_source (source)
                )
            """)
            
            # Create ticket_details table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticket_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticket_id VARCHAR(10) NOT NULL,
                    field_name VARCHAR(100) NOT NULL,
                    field_value TEXT,
                    is_initial BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source ENUM('email', 'chat') DEFAULT 'email',
                    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
                    INDEX idx_ticket_field (ticket_id, field_name)
                )
            """)
            
            # Create ticket_updates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticket_updates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ticket_id VARCHAR(10) NOT NULL,
                    update_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_fields JSON,
                    update_source ENUM('email', 'chat') DEFAULT 'email',
                    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
                    INDEX idx_ticket_updates (ticket_id)
                )
            """)
            
            # Create ticket history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticket_history (
                    history_id INT AUTO_INCREMENT PRIMARY KEY,
                    ticket_id VARCHAR(10) NOT NULL,
                    field_name VARCHAR(100) NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by VARCHAR(255),
                    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    change_type ENUM('create', 'update', 'terminate') DEFAULT 'update',
                    source ENUM('email', 'chat') DEFAULT 'email',
                    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
                    INDEX idx_ticket_history (ticket_id, changed_at)
                )
            """)
            
            # Create sessions table (for both email and chat)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id VARCHAR(36) PRIMARY KEY,
                    session_type ENUM('email', 'chat') DEFAULT 'chat',
                    user_id VARCHAR(255),
                    user_email VARCHAR(255),
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'active',
                    INDEX idx_user_id (user_id),
                    INDEX idx_user_email (user_email),
                    INDEX idx_last_activity (last_activity)
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(36) NOT NULL,
                    sender_type ENUM('user', 'assistant', 'system') NOT NULL,
                    message_content TEXT NOT NULL,
                    message_metadata JSON,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source ENUM('email', 'chat') DEFAULT 'chat',
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                    INDEX idx_session_messages (session_id, timestamp)
                )
            """)
            
            # Create conversation_context table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    context_id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(36) NOT NULL,
                    context_type VARCHAR(50) NOT NULL,
                    context_data JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                    INDEX idx_session_context (session_id)
                )
            """)
            
            # Create pending_approvals table (shared with email bot)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pending_approvals (
                    approval_token VARCHAR(32) PRIMARY KEY,
                    ticket_id VARCHAR(10) NOT NULL,
                    hr_email VARCHAR(255) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'pending',
                    approved_at DATETIME,
                    rejected_at DATETIME,
                    rejection_reason TEXT,
                    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
                    INDEX idx_ticket_approval (ticket_id),
                    INDEX idx_status_approval (status)
                )
            """)
            
            conn.commit()
            logger.info("Database setup completed successfully")
            
        except Error as e:
            logger.error(f"Error setting up database: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

# ============================================================================
# SESSION MANAGER
# ============================================================================

class ChatSessionManager:
    """Manages chat sessions"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (session_id, session_type, user_id, user_email)
                VALUES (%s, 'chat', %s, %s)
            """, (session_id, user_id or f'user_{uuid.uuid4().hex[:8]}', 
                  f'{user_id or uuid.uuid4().hex[:8]}@chat.local'))
            conn.commit()
            
        logger.info(f"Created new chat session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM chat_sessions
                WHERE session_id = %s
            """, (session_id,))
            return cursor.fetchone()
    
    def save_message(self, session_id: str, sender_type: str, 
                    content: str, metadata: Optional[Dict] = None):
        """Save a chat message"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_messages 
                (session_id, sender_type, message_content, message_metadata, source)
                VALUES (%s, %s, %s, %s, 'chat')
            """, (session_id, sender_type, content, 
                  json.dumps(metadata) if metadata else None))
            
            cursor.execute("""
                UPDATE chat_sessions 
                SET last_activity = NOW()
                WHERE session_id = %s
            """, (session_id,))
            
            conn.commit()
            logger.debug(f"Saved message for session {session_id}")
    
    def get_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat messages for a session"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT message_id, sender_type, message_content, 
                           message_metadata, timestamp
                    FROM chat_messages
                    WHERE session_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (session_id, limit))
                
                messages = cursor.fetchall()
                
                for msg in messages:
                    if msg.get('message_metadata'):
                        try:
                            msg['message_metadata'] = json.loads(msg['message_metadata'])
                        except:
                            pass
                
                return list(reversed(messages))
                
        except Exception as e:
            logger.error(f"Error in get_messages: {e}")
            logger.error(f"Session ID: {session_id}")
            raise
    
    def save_context(self, session_id: str, context_type: str, 
                    context_data: Dict) -> None:
        """Save conversation context"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_context 
                (session_id, context_type, context_data)
                VALUES (%s, %s, %s)
            """, (session_id, context_type, json.dumps(context_data)))
            conn.commit()
            logger.debug(f"Saved context for session {session_id}")
    
    def get_latest_context(self, session_id: str, context_type: str) -> Optional[Dict]:
        """Get the latest context of a specific type"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT context_data 
                FROM conversation_context
                WHERE session_id = %s AND context_type = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (session_id, context_type))
            
            result = cursor.fetchone()
            if result and result['context_data']:
                return json.loads(result['context_data'])
            return None

# ============================================================================
# CHAT TICKET MANAGER
# ============================================================================

class ChatTicketManager:
    """Manages hiring tickets - unified with email bot"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def generate_ticket_id(self) -> str:
        """Generate a unique ticket ID"""
        return hashlib.md5(f"{datetime.now()}_{secrets.token_hex(4)}".encode()).hexdigest()[:10]
    
    def create_ticket(self, session_id: str, sender_email: str, 
                     details: Dict[str, str]) -> Tuple[str, bool]:
        """Create a new ticket"""
        ticket_id = self.generate_ticket_id()
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create ticket with 'chat' as source
                # Use sender_email for both user_id and sender to ensure proper filtering
                cursor.execute("""
                    INSERT INTO tickets (ticket_id, source, session_id, user_id, sender, subject)
                    VALUES (%s, 'chat', %s, %s, %s, %s)
                """, (ticket_id, session_id, sender_email, sender_email, 
                      details.get('job_title', 'Job Posting')))
                
                # Insert details
                for field_name, field_value in details.items():
                    if field_value and field_value != "NOT_FOUND":
                        cursor.execute("""
                            INSERT INTO ticket_details (ticket_id, field_name, field_value, is_initial, source)
                            VALUES (%s, %s, %s, TRUE, 'chat')
                        """, (ticket_id, field_name, field_value))
                        
                        # Add to history
                        cursor.execute("""
                            INSERT INTO ticket_history 
                            (ticket_id, field_name, old_value, new_value, changed_by, change_type, source)
                            VALUES (%s, %s, NULL, %s, %s, 'create', 'chat')
                        """, (ticket_id, field_name, field_value, sender_email))
                
                conn.commit()
                logger.info(f"Created ticket {ticket_id} from chat")
                return ticket_id, True
            
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return None, False
    
    def update_ticket(self, ticket_id: str, user_id: str, 
                     updates: Dict[str, str]) -> Tuple[bool, str]:
        """Update ticket details"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if ticket exists and user has permission
                cursor.execute("""
                    SELECT user_id, status, source FROM tickets WHERE ticket_id = %s
                """, (ticket_id,))
                result = cursor.fetchone()
                
                if not result:
                    return False, "Ticket not found"
                
                # Allow updates if it's from chat source OR user created it
                if result[2] == 'chat':
                    # Chat tickets can be updated by any chat user
                    pass
                elif result[0] != user_id:
                    return False, "You don't have permission to update this ticket"
                
                if result[1] == 'terminated':
                    return False, "Cannot update a terminated ticket"
                
                # Update each field
                updated_fields = []
                for field_name, new_value in updates.items():
                    if field_name in Config.REQUIRED_HIRING_DETAILS and new_value:
                        # Get current value
                        cursor.execute("""
                            SELECT field_value FROM ticket_details
                            WHERE ticket_id = %s AND field_name = %s
                            ORDER BY created_at DESC
                            LIMIT 1
                        """, (ticket_id, field_name))
                        
                        old_value_result = cursor.fetchone()
                        old_value = old_value_result[0] if old_value_result else None
                        
                        if old_value != new_value:
                            # Insert new value
                            cursor.execute("""
                                INSERT INTO ticket_details (ticket_id, field_name, field_value, is_initial, source)
                                VALUES (%s, %s, %s, FALSE, 'chat')
                            """, (ticket_id, field_name, new_value))
                            
                            # Add to history
                            cursor.execute("""
                                INSERT INTO ticket_history 
                                (ticket_id, field_name, old_value, new_value, changed_by, source)
                                VALUES (%s, %s, %s, %s, %s, 'chat')
                            """, (ticket_id, field_name, old_value, new_value, user_id))
                            
                            updated_fields.append(field_name)
                
                # Update ticket timestamp
                cursor.execute("""
                    UPDATE tickets 
                    SET last_updated = NOW(), status = 'updated'
                    WHERE ticket_id = %s
                """, (ticket_id,))
                
                # Add to ticket_updates table
                if updated_fields:
                    cursor.execute("""
                        INSERT INTO ticket_updates (ticket_id, updated_fields, update_source)
                        VALUES (%s, %s, 'chat')
                    """, (ticket_id, json.dumps(updates)))
                
                conn.commit()
                
                if updated_fields:
                    return True, f"Updated fields: {', '.join(updated_fields)}"
                else:
                    return True, "No changes were made"
                    
        except Exception as e:
            logger.error(f"Error updating ticket: {e}")
            return False, f"Error updating ticket: {str(e)}"
    
    def get_user_tickets(self, user_id: str) -> List[Dict]:
        """Get all tickets for a user (including email tickets)"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.*, td.field_value as job_title
                FROM tickets t
                LEFT JOIN ticket_details td ON t.ticket_id = td.ticket_id 
                    AND td.field_name = 'job_title' AND td.is_initial = TRUE
                WHERE t.user_id = %s OR t.sender = %s
                ORDER BY t.created_at DESC
            """, (user_id, user_id))
            return cursor.fetchall()
    
    def get_ticket_details(self, ticket_id: str) -> Optional[Dict]:
        """Get details of a specific ticket"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM tickets WHERE ticket_id = %s
            """, (ticket_id,))
            ticket = cursor.fetchone()
            
            if not ticket:
                return None
            
            # Get latest details
            cursor.execute("""
                SELECT DISTINCT field_name,
                       (SELECT field_value 
                        FROM ticket_details td2 
                        WHERE td2.ticket_id = td1.ticket_id 
                        AND td2.field_name = td1.field_name 
                        ORDER BY td2.created_at DESC 
                        LIMIT 1) as field_value
                FROM ticket_details td1
                WHERE ticket_id = %s
            """, (ticket_id,))
            
            details = {}
            for row in cursor.fetchall():
                details[row['field_name']] = row['field_value']
            
            ticket['details'] = details
            return ticket
    
    def terminate_ticket(self, ticket_id: str, user_id: str, 
                        reason: str = "User requested termination") -> Tuple[bool, str]:
        """Terminate a ticket"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if ticket exists and user has permission
                cursor.execute("""
                    SELECT user_id, status, source FROM tickets WHERE ticket_id = %s
                """, (ticket_id,))
                result = cursor.fetchone()
                
                if not result:
                    return False, "Ticket not found"
                
                # Allow termination if user created it OR if it's from chat source
                if result[0] != user_id and result[2] != 'chat':
                    return False, "You don't have permission to terminate this ticket"
                
                if result[1] == 'terminated':
                    return False, "Ticket is already terminated"
                
                # Terminate the ticket
                cursor.execute("""
                    UPDATE tickets 
                    SET status = 'terminated',
                        terminated_at = NOW(),
                        terminated_by = %s,
                        termination_reason = %s,
                        approval_status = 'terminated'
                    WHERE ticket_id = %s
                """, (user_id, reason, ticket_id))
                
                # Add to history
                cursor.execute("""
                    INSERT INTO ticket_history 
                    (ticket_id, field_name, old_value, new_value, changed_by, change_type, source)
                    VALUES (%s, 'status', %s, 'terminated', %s, 'terminate', 'chat')
                """, (ticket_id, result[1], user_id))
                
                conn.commit()
                return True, "Ticket terminated successfully"
                
        except Exception as e:
            logger.error(f"Error terminating ticket: {e}")
            return False, f"Error terminating ticket: {str(e)}"
    
    def get_all_tickets_summary(self) -> Dict[str, Any]:
        """Get summary of all tickets in the system"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get counts by source and status
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN source = 'email' THEN 1 ELSE 0 END) as email_tickets,
                    SUM(CASE WHEN source = 'chat' THEN 1 ELSE 0 END) as chat_tickets,
                    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'terminated' THEN 1 ELSE 0 END) as terminated_count
                FROM tickets
            """)
            
            summary = cursor.fetchone()
            
            # Rename the field to match what we expect
            summary['terminated'] = summary.pop('terminated_count')
            
            # Get recent approved tickets
            cursor.execute("""
                SELECT t.ticket_id, t.source, td.field_value as job_title
                FROM tickets t
                LEFT JOIN ticket_details td ON t.ticket_id = td.ticket_id 
                    AND td.field_name = 'job_title' AND td.is_initial = TRUE
                WHERE t.approval_status = 'approved'
                ORDER BY t.approved_at DESC
                LIMIT 5
            """)
            
            summary['recent_approved'] = cursor.fetchall()
            
            return summary

# ============================================================================
# AI AGENTS (USING OPENAI)
# ============================================================================

class LanguageDetectorAgent(AssistantAgent):
    """Agent for detecting non-English messages"""
    
    def __init__(self):
        system_message = """You are a language detector. Analyze the message and return a JSON object.

Return JSON in this exact format:
{
    "is_english": true/false,
    "detected_language": "language_name",
    "confidence": 0.0-1.0,
    "has_mixed_languages": true/false
}

Guidelines:
- Single words like city names (Pune, Mumbai, Delhi, etc.) should be considered English
- Common Indian place names are acceptable as English
- Technical terms, company names, and proper nouns should be considered English
- Only mark as non-English if the message contains actual non-English words or scripts
- Be lenient with single-word responses - they're usually names or places
- Look for non-English scripts (Devanagari, Arabic, Chinese, etc.)
- Check for mixed language usage (Hinglish, etc.)

Examples that should be marked as ENGLISH (is_english: true):
- "Pune" (city name)
- "Mumbai" (city name)  
- "5 LPA" (salary notation)
- "Kumar" (name)
- "System Engineer" (job title)
- Any single English word

Examples that should be marked as NON-ENGLISH:
- "नमस्ते" (Hindi greeting)
- "કેમ છો" (Gujarati)
- "Bonjour comment allez-vous" (French)
- "मुझे नौकरी चाहिए" (Hindi sentence)

IMPORTANT: Return ONLY the JSON object, no other text."""
        
        super().__init__(
            name="LanguageDetector",
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

class ChatClassifierAgent(AssistantAgent):
    """Agent for classifying chat messages"""
    
    def __init__(self):
        system_message = """You are a chat message classifier. Analyze the user's message and return a JSON object with the classification.

Return JSON in this exact format:
{
    "intent": "hiring|termination|question|greeting|status_check|help|approval|update",
    "is_hiring_related": true/false,
    "has_complete_info": true/false,
    "ticket_id": "extracted_id_or_null",
    "confidence": 0.0-1.0
}

Intent descriptions:
- hiring: User wants to post a new job OR is providing job details
- termination: User wants to cancel/close/terminate a job posting
- question: User has a general question about the system
- greeting: Simple greeting
- status_check: User wants to check status of their tickets/jobs
- help: User asks for help or guidance
- approval: User wants to approve a ticket
- update: User wants to update/modify an existing ticket

For ticket_id: Look for 10-character alphanumeric IDs
IMPORTANT: Return ONLY the JSON object, no other text."""
        
        super().__init__(
            name="ChatClassifier",
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

class ChatResponseAgent(AssistantAgent):
    """Premium conversational agent with enhanced capabilities"""
    
    def __init__(self):
        system_message = """You are a premium, industry-ready AI hiring assistant with advanced conversational abilities and intelligent job posting capabilities. You're designed for professional HR teams and can handle complex recruitment scenarios.

PERSONALITY & STYLE:
- Professional, intelligent, and industry-experienced
- Warm yet authoritative in HR matters
- Context-aware and adaptive to different industries
- Uses natural, conversational language with professional tone
- Strategic and data-driven in recommendations
- Appropriate use of emojis for engagement (👋 ✅ 🎉 📝 💼 🤝 📊 🚀)

ADVANCED CAPABILITIES:
- Intelligent job title and location detection (no manual lists required)
- Context-aware conversation flow and question sequencing
- Industry-specific hiring insights and best practices
- Advanced job posting optimization and ATS compliance
- Candidate experience enhancement strategies
- Salary benchmarking and market analysis
- Diversity and inclusion hiring guidance
- Remote work and hybrid arrangement expertise
- Compliance and legal hiring considerations

INTELLIGENT JOB POSTING FLOW:
- Automatically detects job titles (abbreviations, full names, technical roles, business roles)
- Intelligently distinguishes between job titles and locations
- Context-aware questions that reference previously collected information
- Industry-specific guidance and recommendations
- Optimized question sequence for maximum candidate attraction

ENHANCED RESPONSES:
- Provide strategic insights based on industry best practices
- Suggest improvements for better candidate attraction
- Explain market trends and competitive positioning
- Offer compliance and legal considerations
- Recommend diversity and inclusion strategies
- Provide data-driven salary and benefits guidance

CONVERSATION INTELLIGENCE:
- Maintains full context throughout the conversation
- Adapts questions based on collected information
- Provides proactive suggestions and optimizations
- Handles complex multi-part queries intelligently
- Offers industry-specific insights and recommendations

Always aim to provide enterprise-level value and strategic hiring guidance."""
        
        super().__init__(
            name="ChatResponder",
            system_message=system_message,
            llm_config=fast_llm_config,  # Use faster model for responses
            human_input_mode="NEVER"
        )

class HiringDetailsExtractorAgent(AssistantAgent):
    """Agent for extracting hiring details"""
    
    def __init__(self):
        system_message = """You are a hiring details extractor. Extract job posting details from the conversation.

Return ONLY a JSON object with these fields:
{
    "job_title": "position name or NOT_FOUND",
    "location": "city/location or NOT_FOUND",
    "experience_required": "years of experience or NOT_FOUND",
    "salary_range": "salary information or NOT_FOUND",
    "job_description": "description or NOT_FOUND",
    "required_skills": "skills list or NOT_FOUND",
    "employment_type": "Full-time/Part-time/Contract or NOT_FOUND",
    "deadline": "application deadline or NOT_FOUND"
}

            CRITICAL RULES:
            1. Only extract information EXPLICITLY stated by the user in their messages
            2. Pay special attention to the user's latest message
            3. If the user just provided new information, extract it accurately
            4. If a field is not mentioned anywhere in the conversation, use "NOT_FOUND"
            5. Don't make assumptions or infer information
            6. Be precise with the exact words/phrases the user used
            7. For experience, look for numbers (e.g., "3 years", "5-7 years", "fresher")
            8. For salary, look for amounts with units (e.g., "3-4 LPA", "25 lakhs", "50000")
            9. For location, look for city names or work arrangements (e.g., "Pune", "Remote", "Hybrid")
        10. For required_skills: ONLY extract if user explicitly provides a skills list (e.g., "Python, SQL, AWS")
        11. NEVER extract skills from job descriptions, role descriptions, or general abilities
        12. If user provides a job description, set required_skills to "NOT_FOUND"
        13. Skills should be technical terms, not general abilities like "communication skills"
        14. For location: ONLY extract if user explicitly provides a location (e.g., "Pune", "USA", "London")
        15. NEVER extract location from job descriptions or role descriptions
        16. If user provides a job description, do NOT extract location from it
        17. Location should be place names, not general words like "traffic", "safety", etc.
        18. For job_description: Extract the full description when provided, but don't extract skills or location from it

Return ONLY valid JSON, no other text."""
        
        super().__init__(
            name="DetailsExtractor",
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

class UpdateDetailsExtractorAgent(AssistantAgent):
    """Agent for extracting update details"""
    
    def __init__(self):
        system_message = """You are an update details extractor. Extract what fields the user wants to update.

Return ONLY a JSON object with fields they want to update:
{
    "job_title": "new value or null",
    "location": "new value or null",
    "experience_required": "new value or null",
    "salary_range": "new value or null",
    "job_description": "new value or null",
    "required_skills": "new value or null",
    "employment_type": "new value or null",
    "deadline": "new value or null"
}

Only include fields that the user explicitly wants to update.
Return ONLY valid JSON, no other text."""
        
        super().__init__(
            name="UpdateExtractor",
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER"
        )

# ============================================================================
# MAIN CHAT BOT HANDLER
# ============================================================================

class ChatBotHandler:
    """Main chat bot handler that coordinates everything"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session_manager = ChatSessionManager(self.db_manager)
        self.ticket_manager = ChatTicketManager(self.db_manager)
        
        # Initialize AI agents
        self.language_detector = LanguageDetectorAgent()
        self.classifier = ChatClassifierAgent()
        self.responder = ChatResponseAgent()
        self.extractor = HiringDetailsExtractorAgent()
        self.update_extractor = UpdateDetailsExtractorAgent()
        
        # Test database connection
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            logger.warning("Continuing without database functionality")
        
        # Test OpenAI connection - temporarily disabled for debugging
        try:
            self._test_openai_connection()
        except Exception as e:
            logger.warning(f"OpenAI connection test failed: {e}")
            logger.warning("Continuing without AI functionality for now")
    
    def _test_openai_connection(self):
        """Test OpenAI API connection"""
        try:
            test_response = self.responder.generate_reply(
                messages=[{"content": "Say 'OpenAI connection successful!'", "role": "user"}]
            )
            logger.info(f"OpenAI API test successful: {test_response}")
        except Exception as e:
            logger.error(f"OpenAI API test failed: {e}")
            raise ValueError(f"Failed to connect to OpenAI API: {e}")
    
    def start_session(self, user_id: Optional[str] = None) -> Dict:
        """Start a new chat session"""
        session_id = self.session_manager.create_session(user_id)
        
        welcome_message = ("Hello! 👋 I'm your hiring assistant. I can help you:\n\n"
                          "• Post new job openings\n"
                          "• Check status of your postings (including email submissions)\n"
                          "• Update existing tickets\n"
                          "• Terminate job postings\n"
                          "• View all jobs in the system\n\n"
                          "What would you like to do today?")
        
        self.session_manager.save_message(session_id, "assistant", welcome_message)
        
        return {
            'session_id': session_id,
            'user_id': user_id or f'user_{uuid.uuid4().hex[:8]}',
            'message': welcome_message
        }
    
    def _contains_non_english_script(self, text: str) -> bool:
        """Check if text contains non-English scripts"""
        # Check for various non-Latin scripts
        non_english_ranges = [
            (0x0900, 0x097F),  # Devanagari
            (0x0A80, 0x0AFF),  # Gujarati
            (0x0980, 0x09FF),  # Bengali
            (0x0B80, 0x0BFF),  # Tamil
            (0x0C00, 0x0C7F),  # Telugu
            (0x0A00, 0x0A7F),  # Punjabi
            (0x4E00, 0x9FFF),  # Chinese
            (0x3040, 0x309F),  # Hiragana
            (0x30A0, 0x30FF),  # Katakana
            (0x0600, 0x06FF),  # Arabic
            (0x0E00, 0x0E7F),  # Thai
            (0xAC00, 0xD7AF),  # Korean
            (0x0400, 0x04FF),  # Cyrillic
        ]
        
        for char in text:
            code_point = ord(char)
            for start, end in non_english_ranges:
                if start <= code_point <= end:
                    return True
        return False
    
    def _quick_language_check(self, message: str) -> Optional[str]:
        """Quick check for common non-English patterns"""
        
        # First check for non-ASCII characters that indicate specific scripts
        if not message.isascii():
            # Check for specific scripts with their Unicode ranges
            for char in message:
                code_point = ord(char)
                
                # Chinese (CJK Unified Ideographs)
                if 0x4E00 <= code_point <= 0x9FFF:
                    return 'Chinese'
                # Devanagari (Hindi/Marathi)
                elif 0x0900 <= code_point <= 0x097F:
                    return 'Hindi/Marathi'
                # Gujarati
                elif 0x0A80 <= code_point <= 0x0AFF:
                    return 'Gujarati'
                # Bengali
                elif 0x0980 <= code_point <= 0x09FF:
                    return 'Bengali'
                # Tamil
                elif 0x0B80 <= code_point <= 0x0BFF:
                    return 'Tamil'
                # Telugu
                elif 0x0C00 <= code_point <= 0x0C7F:
                    return 'Telugu'
                # Punjabi
                elif 0x0A00 <= code_point <= 0x0A7F:
                    return 'Punjabi'
                # Japanese Hiragana
                elif 0x3040 <= code_point <= 0x309F:
                    return 'Japanese'
                # Japanese Katakana
                elif 0x30A0 <= code_point <= 0x30FF:
                    return 'Japanese'
                # Arabic
                elif 0x0600 <= code_point <= 0x06FF:
                    return 'Arabic'
                # Thai
                elif 0x0E00 <= code_point <= 0x0E7F:
                    return 'Thai'
                # Korean
                elif 0xAC00 <= code_point <= 0xD7AF:
                    return 'Korean'
                # Cyrillic (Russian, etc.)
                elif 0x0400 <= code_point <= 0x04FF:
                    return 'Russian'
        
        # Convert message to lowercase for pattern matching
        message_lower = message.lower().strip()
        
        # Common non-English words and phrases (check these BEFORE patterns)
        non_english_words = {
            # Spanish
            'hola': 'Spanish',
            'gracias': 'Spanish',
            'por favor': 'Spanish',
            'buenos días': 'Spanish',
            'buenas tardes': 'Spanish',
            'necesito': 'Spanish',
            'ayuda': 'Spanish',
            
            # French
            'bonjour': 'French',
            'bonsoir': 'French',
            'merci': 'French',
            'au revoir': 'French',
            's\'il vous plaît': 'French',
            'comment allez-vous': 'French',
            'je suis': 'French',
            'aide': 'French',
            
            # German
            'hallo': 'German',
            'guten tag': 'German',
            'guten morgen': 'German',
            'danke': 'German',
            'bitte': 'German',
            'auf wiedersehen': 'German',
            'wie geht\'s': 'German',
            'hilfe': 'German',
            
            # Italian
            'ciao': 'Italian',
            'buongiorno': 'Italian',
            'grazie': 'Italian',
            'prego': 'Italian',
            'arrivederci': 'Italian',
            
            # Portuguese
            'olá': 'Portuguese',
            'obrigado': 'Portuguese',
            'por favor': 'Portuguese',
            'bom dia': 'Portuguese',
            
            # Dutch
            'hoi': 'Dutch',
            'dank je': 'Dutch',
            'alsjeblieft': 'Dutch',
            
            # Russian (transliterated)
            'privet': 'Russian',
            'spasibo': 'Russian',
            'pozhaluysta': 'Russian',
        }
        
        # Check exact matches first
        if message_lower in non_english_words:
            return non_english_words[message_lower]
        
        # Check if message contains any of these phrases
        for phrase, language in non_english_words.items():
            if phrase in message_lower:
                return language
        
        # Common non-English patterns with regex
        non_english_patterns = {
            'Hindi': [
                r'नमस्ते', r'क्या हाल है', r'धन्यवाद', r'कृपया', r'मैं', r'आप',
                r'नौकरी', r'काम', r'चाहिए', r'कैसे', r'कब', r'क्यों'
            ],
            'Marathi': [
                r'नमस्कार', r'कसे आहात', r'धन्यवाद', r'कृपया', r'मी', r'तुम्ही',
                r'नोकरी', r'काम', r'पाहिजे'
            ],
            'Gujarati': [
                r'નમસ્તે', r'કેમ છો', r'આભાર', r'કૃપા કરીને', r'હું', r'તમે',
                r'નોકરી', r'કામ', r'જોઈએ'
            ],
            'Bengali': [
                r'নমস্কার', r'কেমন আছেন', r'ধন্যবাদ', r'দয়া করে', r'আমি', r'আপনি',
                r'চাকরি', r'কাজ'
            ],
            'Tamil': [
                r'வணக்கம்', r'எப்படி இருக்கிறீர்கள்', r'நன்றி', r'தயவுசெய்து',
                r'நான்', r'நீங்கள்', r'வேலை'
            ],
            'Telugu': [
                r'నమస్కారం', r'ఎలా ఉన్నారు', r'ధన్యవాదాలు', r'దయచేసి',
                r'నేను', r'మీరు', r'ఉద్యోగం'
            ],
            'Punjabi': [
                r'ਸਤ ਸ੍ਰੀ ਅਕਾਲ', r'ਕਿਵੇਂ ਹੋ', r'ਧੰਨਵਾਦ', r'ਕਿਰਪਾ ਕਰਕੇ',
                r'ਮੈਂ', r'ਤੁਸੀਂ', r'ਨੌਕਰੀ'
            ],
            'Chinese': [
                r'你好', r'谢谢', r'请', r'我', r'你', r'工作', r'招聘', r'帮助'
            ],
            'Japanese': [
                r'こんにちは', r'ありがとう', r'お願いします', r'私', r'あなた', r'仕事'
            ],
            'Arabic': [
                r'مرحبا', r'شكرا', r'من فضلك', r'أنا', r'أنت', r'عمل', r'وظيفة'
            ]
        }
        
        # Check for pattern matches
        for language, patterns in non_english_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE | re.UNICODE):
                    return language
        
        return None
    
    def _check_language(self, message: str) -> Dict:
        """Check if the message is in English - OPTIMIZED FOR SPEED"""
        
        # Skip check for very short messages or numbers
        if len(message.strip()) < 3 or message.strip().isdigit():
            return {"is_english": True}
        
        # Check cache first
        cache_key = f"lang_check:{hashlib.md5(message.encode()).hexdigest()}"
        cached_result = response_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # List of common English words and Indian city names that should be allowed
        english_exceptions = [
            # Indian cities
            'pune', 'mumbai', 'delhi', 'bangalore', 'bengaluru', 'chennai', 'kolkata',
            'hyderabad', 'ahmedabad', 'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur',
            'patna', 'indore', 'thane', 'bhopal', 'vadodara', 'chandigarh', 'gurgaon',
            'gurugram', 'noida', 'navi mumbai', 'nasik', 'nashik', 'faridabad', 'agra',
            'mysore', 'mysuru', 'kochi', 'cochin', 'trivandrum', 'thiruvananthapuram',
            
            # Common job-related terms
            'lpa', 'lakhs', 'crore', 'fresher', 'wfh', 'wfo', 'hybrid',
            
            # Common names (add more as needed)
            'raj', 'kumar', 'sharma', 'singh', 'patel', 'shah', 'mehta'
        ]
        
        # Check if message is a known exception
        message_lower = message.lower().strip()
        if message_lower in english_exceptions:
            result = {"is_english": True}
            response_cache.set(cache_key, result)
            return result
        
        # Check if it's a single word that might be a name or place
        if len(message.split()) == 1 and len(message) < 15:
            # First check if it contains non-English scripts
            if self._contains_non_english_script(message):
                quick_result = self._quick_language_check(message)
                if quick_result:
                    result = {
                        "is_english": False,
                        "detected_language": quick_result,
                        "confidence": 0.9,
                        "has_mixed_languages": False
                    }
                    response_cache.set(cache_key, result)
                    return result
            # Then check if it's a known non-English word (even if ASCII)
            elif message.isascii():
                quick_result = self._quick_language_check(message)
                if quick_result:
                    result = {
                        "is_english": False,
                        "detected_language": quick_result,
                        "confidence": 0.9,
                        "has_mixed_languages": False
                    }
                    response_cache.set(cache_key, result)
                    return result
            # Default to English for other single words
            result = {"is_english": True}
            response_cache.set(cache_key, result)
            return result
        
        # Quick pattern check first - this will now check Unicode properly
        quick_result = self._quick_language_check(message)
        if quick_result:
            logger.debug(f"Quick language check detected: {quick_result} for message: {message}")
            result = {
                "is_english": False,
                "detected_language": quick_result,
                "confidence": 0.9,
                "has_mixed_languages": False
            }
            response_cache.set(cache_key, result)
            return result
        
        # For longer messages, use AI detection (only if really needed)
        if len(message.split()) > 5:  # Increased threshold to reduce AI calls
            try:
                detection_response = self.language_detector.generate_reply(
                    messages=[{"content": message, "role": "user"}]
                )
                
                language_info = extract_json_from_text(detection_response)
                
                if not language_info:
                    # Default to assuming English if detection fails
                    result = {"is_english": True}
                else:
                    logger.debug(f"AI language detection result: {language_info} for message: {message}")
                    result = language_info
                
                response_cache.set(cache_key, result)
                return result
            except Exception as e:
                logger.warning(f"Language detection failed: {e}, defaulting to English")
                result = {"is_english": True}
                response_cache.set(cache_key, result)
                return result
        
        # Default to English for short responses
        result = {"is_english": True}
        response_cache.set(cache_key, result)
        return result
    
    def _generate_language_reminder(self, language_info: Dict) -> Dict:
        """Generate a polite reminder to use English"""
        
        detected_language = language_info.get('detected_language', 'non-English')
        
        # Customize response based on detected language
        language_specific_greetings = {
            'Hindi': 'नमस्ते! ',
            'Hindi/Marathi': 'नमस्ते/नमस्कार! ',
            'Marathi': 'नमस्कार! ',
            'Gujarati': 'નમસ્તે! ',
            'Bengali': 'নমস্কার! ',
            'Tamil': 'வணக்கம்! ',
            'Telugu': 'నమస్కారం! ',
            'Punjabi': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ',
            'Spanish': '¡Hola! ',
            'French': 'Bonjour! ',
            'German': 'Hallo! ',
            'Chinese': '你好! ',
            'Japanese': 'こんにちは! ',
            'Arabic': 'مرحبا! ',
            'Thai': 'สวัสดี! ',
            'Korean': '안녕하세요! ',
            'Portuguese': 'Olá! ',
            'Italian': 'Ciao! ',
            'Russian': 'Привет! ',
            'Dutch': 'Hallo! '
        }
        
        greeting = language_specific_greetings.get(detected_language, '')
        
        response_text = f"""{greeting}I appreciate your message, but I can only assist you in English at the moment. 🌍

Please feel free to ask your question in English, and I'll be happy to help you with:
• Posting new job openings
• Checking status of your postings
• Updating existing tickets
• Any other hiring-related queries

Thank you for your understanding! 😊"""
        
        return {
            "message": response_text,
            "metadata": {
                "language_detected": detected_language,
                "is_english": False,
                "action": "language_reminder"
            }
        }
    
    def process_message(self, session_id: str, user_id: str, 
                       message: str, authenticated_user_email: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message and generate response - OPTIMIZED FOR SPEED"""
        
        start_time = time.time()
        
        try:
            # Save user message
            self.session_manager.save_message(session_id, "user", message)
            
            # Check language first (with caching)
            language_check = self._check_language(message)
            
            if not language_check.get('is_english', True):
                # Generate language reminder response
                response = self._generate_language_reminder(language_check)
                
                # Save assistant response
                self.session_manager.save_message(
                    session_id, "assistant", response['message'],
                    metadata=response.get('metadata')
                )
                
                return response
            
            # Continue with normal processing if English
            # Get conversation history (limit to recent messages for speed)
            history = self.session_manager.get_messages(session_id, limit=5)  # Reduced from 10 to 5
            
            # Classify the message (with caching and fast classification)
            classification = self._classify_message(message, history, session_id)
            
            # Generate appropriate response
            response = self._generate_response(
                session_id, user_id, message, classification, history, authenticated_user_email
            )
            
            # Save assistant response
            self.session_manager.save_message(
                session_id, "assistant", response['message'],
                metadata=response.get('metadata')
            )
            
            # Log performance
            processing_time = time.time() - start_time
            logger.info(f"Message processed in {processing_time:.2f}s for session {session_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            logger.error(f"Session ID: {session_id}, User ID: {user_id}, Message: {message}")
            import traceback
            traceback.print_exc()
            
            error_response = {
                "message": "I apologize, but I encountered an error processing your request. Please try again.",
                "metadata": {"error": str(e)}
            }
            
            try:
                self.session_manager.save_message(
                    session_id, "assistant", error_response['message'],
                    metadata=error_response.get('metadata')
                )
            except:
                pass
                
            return error_response
    
    def _classify_message(self, message: str, history: List[Dict], session_id: str = None) -> Dict:
        """Classify user message intent - OPTIMIZED FOR SPEED"""
        
        # Check cache first (but not for context-dependent classifications)
        cache_key = f"classify:{hashlib.md5(message.encode()).hexdigest()}"
        cached_result = response_cache.get(cache_key)
        if cached_result and not session_id:  # Only use cache if no session context
            return cached_result
        
        # Quick keyword-based classification for common cases
        message_lower = message.lower().strip()
        
        # Check if we're in the middle of a hiring conversation
        if session_id:  # Only check if we have a session_id
            logger.info(f"Checking hiring context for session {session_id}")
            hiring_context = self.session_manager.get_latest_context(session_id, 'hiring_flow')
            logger.info(f"Retrieved hiring context: {hiring_context}")
            
            if hiring_context and hiring_context.get('collected_fields'):
                collected_fields = hiring_context.get('collected_fields', {})
                logger.info(f"Found collected fields: {list(collected_fields.keys())}")
                
                # If we're in a hiring flow, treat most responses as hiring-related
                # Only exclude very specific commands that would end the hiring flow
                # Check for exact command matches, not partial matches
                exclude_commands = ['cancel', 'stop', 'quit', 'help', 'i need help', 'need help', 'show my tickets', 'show all tickets']
                is_command = any(message_lower.strip() == cmd.strip() or message_lower.strip().startswith(cmd.strip() + ' ') for cmd in exclude_commands)
                
                if not is_command:
                    logger.info(f"✅ PRESERVING hiring context for session {session_id}, collected fields: {list(collected_fields.keys())}")
                    classification = {
                        "intent": "hiring",
                        "is_hiring_related": True,
                        "has_complete_info": False,
                        "confidence": 0.8
                    }
                    # Don't cache this result as it's context-dependent
                    return classification
                else:
                    detected_command = next((cmd for cmd in exclude_commands if message_lower.strip() == cmd.strip() or message_lower.strip().startswith(cmd.strip() + ' ')), 'unknown')
                    logger.info(f"❌ Excluding hiring context due to command: '{detected_command}' in message: {message_lower[:100]}...")
            else:
                logger.info(f"❌ No hiring context found for session {session_id}")
        else:
            logger.info(f"❌ No session_id provided for classification")
        
        # Enhanced classification for common intents with more natural language patterns
        if any(phrase in message_lower for phrase in [
            'post a job', 'create job', 'new job', 'hiring', 'want to post', 'need to hire',
            'looking for', 'want to hire', 'job opening', 'position available', 'add a job',
            'create posting', 'job posting', 'employment opportunity', 'recruit'
        ]):
            classification = {
                "intent": "hiring",
                "is_hiring_related": True,
                "has_complete_info": False,
                "confidence": 0.9
            }
            response_cache.set(cache_key, classification)
            return classification
        
        if any(phrase in message_lower for phrase in [
            'show my tickets', 'my tickets', 'list tickets', 'all tickets', 'my jobs',
            'my postings', 'current jobs', 'active jobs', 'job list', 'what jobs',
            'view jobs', 'see jobs', 'show all'
        ]):
            classification = {
                "intent": "status_check",
                "is_hiring_related": True,
                "has_complete_info": False,
                "confidence": 0.9
            }
            response_cache.set(cache_key, classification)
            return classification
        
        if any(phrase in message_lower for phrase in [
            'help', 'what can you do', 'assistance', 'support', 'guide',
            'instructions', 'how to', 'can you help', 'need help', 'i need help',
            'i want help', 'please help', 'help me', 'show help', 'get help'
        ]):
            classification = {
                "intent": "help",
                "is_hiring_related": False,
                "has_complete_info": False,
                "confidence": 0.9
            }
            response_cache.set(cache_key, classification)
            return classification
        
        if any(phrase in message_lower for phrase in [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'greetings', 'welcome', 'howdy', 'sup', 'yo'
        ]):
            classification = {
                "intent": "greeting",
                "is_hiring_related": False,
                "has_complete_info": False,
                "confidence": 0.9
            }
            response_cache.set(cache_key, classification)
            return classification
        
        # For complex cases, use AI classification
        context = self._build_context(history)
        
        prompt = f"""
        Classify this message:
        
        Current message: {message}
        
        Recent conversation context:
        {context}
        """
        
        try:
            response = self.classifier.generate_reply(
                messages=[{"content": prompt, "role": "user"}]
            )
            
            classification = extract_json_from_text(response)
            
            if not classification:
                classification = {
                    "intent": "question",
                    "is_hiring_related": False,
                    "has_complete_info": False,
                    "confidence": 0.7
                }
        except Exception as e:
            logger.warning(f"Classification failed: {e}, using default")
            classification = {
                "intent": "question",
                "is_hiring_related": False,
                "has_complete_info": False,
                "confidence": 0.5
            }
        
        response_cache.set(cache_key, classification)
        return classification
    
    def _generate_response(self, session_id: str, user_id: str, 
                          message: str, classification: Dict,
                          history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Generate response based on intent"""
        
        intent = classification.get('intent', 'question')
        
        # Override intent based on keywords
        message_lower = message.lower()
        if 'approve' in message_lower and any(char.isdigit() or char.isalpha() for char in message_lower):
            intent = 'approval'
        elif any(phrase in message_lower for phrase in ['update ticket', 'modify ticket', 'change ticket']):
            intent = 'update'
        elif any(phrase in message_lower for phrase in ['show my tickets', 'my tickets', 'list tickets', 'all tickets', 'show all']):
            intent = 'status_check'
        elif any(phrase in message_lower for phrase in ['terminate ticket', 'close ticket', 'cancel ticket']):
            intent = 'termination'
        elif 'show ticket' in message_lower and re.search(r'[a-f0-9]{10}', message_lower):
            intent = 'show_ticket'
        
        handlers = {
            'hiring': self._handle_hiring_intent,
            'termination': self._handle_termination_intent,
            'status_check': self._handle_status_check,
            'help': self._handle_help_request,
            'greeting': self._handle_greeting,
            'question': self._handle_general_question,
            'approval': self._handle_approval_intent,
            'update': self._handle_update_intent,
            'show_ticket': self._handle_show_ticket
        }
        
        handler = handlers.get(intent, self._handle_general_question)
        
        if intent in ['hiring', 'termination', 'question', 'approval', 'update', 'show_ticket']:
            return handler(session_id, user_id, message, classification, history, authenticated_user_email)
        elif intent == 'status_check':
            return handler(user_id, message)
        elif intent in ['help', 'greeting']:
            if intent == 'greeting':
                return handler(user_id, session_id)
            else:
                return handler(user_id, session_id)
        else:
            return handler(session_id, user_id, message, classification, history, authenticated_user_email)
    
    def _handle_hiring_intent(self, session_id: str, user_id: str,
                             message: str, classification: Dict,
                             history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Handle job posting intent"""
        
        logger.info(f"Handling hiring intent for session {session_id}, message: {message[:100]}...")
        
        # Check if this is a new job posting request (should reset context)
        message_lower = message.lower().strip()
        is_new_job_request = any(phrase in message_lower for phrase in [
            'post a job', 'create job', 'new job', 'want to post', 'need to hire',
            'want to hire', 'job opening', 'add a job', 'create posting', 'job posting'
        ])
        
        # Get or create hiring context
        hiring_context = self.session_manager.get_latest_context(session_id, 'hiring_flow')
        logger.info(f"Existing hiring context: {hiring_context}")
        
        # If this is a new job request and we have existing context, reset it
        if is_new_job_request and hiring_context and hiring_context.get('collected_fields'):
            logger.info(f"Detected new job posting request, resetting hiring context")
            hiring_context = None
            self.session_manager.save_context(session_id, 'hiring_flow', {})
            # Also clear the response cache to prevent contaminated extraction results
            response_cache.clear()
            logger.info(f"Cleared response cache for fresh job posting")
        
        # Build full conversation context
        full_context = self._build_hiring_context(history, message)
        
        # Check if this is a direct response to a specific field
        last_asked = hiring_context.get('last_asked_field') if hiring_context else None
        is_direct_response = last_asked and self._is_meaningful_response(message, last_asked)
        
        # Extract details with improved prompt - OPTIMIZED FOR SPEED
        cache_key = f"extract:{hashlib.md5(full_context.encode()).hexdigest()}"
        cached_details = response_cache.get(cache_key)
        
        if cached_details and not is_direct_response:
            details = cached_details
        elif is_direct_response:
            # If this is a direct response to a specific field, prioritize it
            details = {last_asked: message.strip()}
            logger.info(f"Direct response detected for {last_asked}: {message.strip()}")
        elif is_new_job_request:
            # For new job requests, try to extract comprehensive details first
            # This makes it a premium chatbot that can handle industry-level requests
            details = self._extract_comprehensive_job_details(message, full_context)
            logger.info(f"New job request detected, attempting comprehensive extraction: {details}")
        else:
            # Try simple pattern matching first for common cases
            details = self._quick_extract_details(message)
            
            # If simple extraction didn't find much, use AI extraction
            # But be more conservative - don't extract skills from job descriptions
            if sum(1 for v in details.values() if v != "NOT_FOUND") < 2:
                extraction_prompt = f"""
                Extract job posting details from this conversation. Pay special attention to the user's latest message.
                
                Conversation:
                {full_context}
                
                CRITICAL RULES:
                - Only extract information that is EXPLICITLY provided by the user
                - If the user just provided a new piece of information, extract it
                - If a field is not mentioned in the conversation, mark it as "NOT_FOUND"
                - Be precise and don't make assumptions
                - Use context to understand what the user is responding to
                
                INTELLIGENT EXTRACTION RULES:
                
                JOB TITLE:
                - Extract job titles, positions, or roles (e.g., "BA", "Business Analyst", "Software Engineer", "Data Scientist")
                - Accept abbreviations (BA, BSC, PM, HR, etc.) and full names
                - Accept technical roles, business roles, creative roles, service roles
                - Be intelligent about recognizing job titles vs other information
                
                LOCATION:
                - Extract geographical locations (cities, countries, states, regions)
                - Extract work arrangements (Remote, Hybrid, Onsite, etc.)
                - Do NOT extract job titles as locations (e.g., "BA" is not a location)
                - Do NOT extract skills as locations (e.g., "Python" is not a location)
                - Only extract if it's clearly a place name or work arrangement
                
                EXPERIENCE:
                - Extract years of experience (e.g., "5 years", "3-5 years", "Senior level")
                - Accept various formats and expressions
                
                SALARY:
                - Extract salary information (e.g., "50k", "100k euros", "Competitive")
                - Accept various formats and currencies
                
                SKILLS:
                - Extract ANY skills input the user provides
                - ACCEPT any format: single skills, multiple skills, comprehensive lists
                - ACCEPT any content: technical skills, soft skills, domain knowledge, tools, platforms
                - The user knows what skills they want, so trust their input completely
                
                JOB DESCRIPTION:
                - Extract the full description if provided
                - Include role responsibilities, requirements, and details
                
                EMPLOYMENT TYPE:
                - Extract employment type (Full-time, Part-time, Contract, Internship, etc.)
                
                DEADLINE:
                - Extract application deadline or timeline information
                
                Return ONLY a JSON object with the extracted fields.
                """
                
                try:
                    extraction_response = self.extractor.generate_reply(
                        messages=[{"content": extraction_prompt, "role": "user"}]
                    )
                    
                    ai_details = extract_json_from_text(extraction_response) or {}
                    logger.info(f"AI extraction response: {ai_details}")
                    
                    # Merge AI results with simple extraction, but be more conservative about skills
                    for key, value in ai_details.items():
                        if value != "NOT_FOUND" and (key not in details or details[key] == "NOT_FOUND"):
                            # Accept any skills input - no restrictions
                            # The user knows what skills they want, so we trust their input completely
                            details[key] = value
                            
                except Exception as e:
                    logger.warning(f"AI extraction failed: {e}, using simple extraction")
            
            response_cache.set(cache_key, details)
        
        # Clean up extraction
        cleaned_details = {}
        for key, value in details.items():
            if value and value != "NOT_FOUND" and len(str(value).strip()) > 0:
                cleaned_details[key] = value
            else:
                cleaned_details[key] = "NOT_FOUND"
        
        # Merge with existing context if available
        if hiring_context and hiring_context.get('collected_fields'):
            existing_details = hiring_context['collected_fields']
            last_asked = hiring_context.get('last_asked_field')
            
            for key, value in existing_details.items():
                # Only keep existing values if we didn't find new ones
                # But if the user just provided a direct response to a specific field, prioritize it
                if (key not in cleaned_details or cleaned_details[key] == "NOT_FOUND") and key != last_asked:
                    cleaned_details[key] = value
        
        # Save context with better tracking
        context_to_save = {
            'collected_fields': cleaned_details,
            'timestamp': datetime.now().isoformat(),
            'last_asked_field': hiring_context.get('last_asked_field') if hiring_context else None
        }
        logger.info(f"Saving hiring context for session {session_id}: {context_to_save}")
        self.session_manager.save_context(session_id, 'hiring_flow', context_to_save)
        
        # Check for missing fields
        missing_fields = []
        for field in Config.REQUIRED_HIRING_DETAILS:
            if field not in cleaned_details or cleaned_details.get(field) == "NOT_FOUND":
                missing_fields.append(field)
        
        # Accept any skills input - no special handling needed
        # The user knows what skills they want, so we trust their input
        
        # Always ensure skills is in missing fields if not properly provided
        if 'required_skills' not in cleaned_details or cleaned_details.get('required_skills') == "NOT_FOUND":
                if 'required_skills' not in missing_fields:
                    missing_fields.append('required_skills')
        
        if missing_fields:
            # For new job requests, always start with job_title
            if is_new_job_request and 'job_title' in missing_fields:
                field_to_ask = 'job_title'
                logger.info(f"New job request detected, starting with job_title")
            else:
                # Ask for next missing field, but avoid repeating the same question
                field_to_ask = missing_fields[0]
            
            last_asked = hiring_context.get('last_asked_field') if hiring_context else None
            question_count = hiring_context.get('question_count', {}) if hiring_context else {}
            current_count = question_count.get(field_to_ask, 0)
            
            # Safety mechanism: if we've asked the same question 3+ times, accept any reasonable response
            if current_count >= 3 and message.strip():
                logger.info(f"Safety mechanism triggered for {field_to_ask} - accepting response after {current_count} attempts")
                cleaned_details[field_to_ask] = message.strip()
                # Remove from missing fields
                if field_to_ask in missing_fields:
                    missing_fields.remove(field_to_ask)
                # Continue to next field
                if missing_fields:
                    field_to_ask = missing_fields[0]
                else:
                    # All fields collected, create ticket
                    return self._create_job_ticket(session_id, user_id, cleaned_details, authenticated_user_email)
            
            # If we just asked for this field and user provided a response, move to next field
            elif last_asked == field_to_ask and message.strip():
                # Check if user provided a meaningful response for this field
                if self._is_meaningful_response(message, field_to_ask):
                    # Update the collected details with the user's response
                    # Use the user's direct response instead of any extracted value
                    cleaned_details[field_to_ask] = message.strip()
                    logger.info(f"User provided direct response for {field_to_ask}: {message.strip()}")
                    
                    # Remove the special handling that forces skills after job_description
                    # This was disrupting the natural sequence defined in REQUIRED_HIRING_DETAILS
                    
                    # Recalculate missing fields after updating
                    missing_fields = []
                    for field in Config.REQUIRED_HIRING_DETAILS:
                        if field not in cleaned_details or cleaned_details.get(field) == "NOT_FOUND":
                            missing_fields.append(field)
                    
                    # Save updated context
                    updated_context = {
                        'collected_fields': cleaned_details,
                        'timestamp': datetime.now().isoformat(),
                        'last_asked_field': None,  # Reset since we got a response
                        'question_count': question_count  # Preserve question count
                    }
                    logger.info(f"Saving updated context after meaningful response: {updated_context}")
                    self.session_manager.save_context(session_id, 'hiring_flow', updated_context)
                    
                    # If still missing fields, ask for the next one
                    if missing_fields:
                        field_to_ask = missing_fields[0]
                        
                        # Special handling: If we just collected job_description, ensure we ask for skills next
                        if last_asked == 'job_description' and 'required_skills' in missing_fields:
                            field_to_ask = 'required_skills'
                            logger.info(f"Forcing skills question after job description")
                        # Remove the always prioritize skills logic to follow proper sequence
                        # The REQUIRED_HIRING_DETAILS array already defines the correct order
                        
                        response_text = self._generate_field_question(field_to_ask, cleaned_details)
                        
                        # Update context with new field to ask and increment question count
                        question_count[field_to_ask] = question_count.get(field_to_ask, 0) + 1
                        next_context = {
                            'collected_fields': cleaned_details,
                            'timestamp': datetime.now().isoformat(),
                            'last_asked_field': field_to_ask,
                            'question_count': question_count
                        }
                        logger.info(f"Saving context with next field to ask: {next_context}")
                        self.session_manager.save_context(session_id, 'hiring_flow', next_context)
                        
                        return {
                            "message": response_text,
                            "metadata": {
                                "intent": "hiring",
                                "missing_fields": missing_fields,
                                "collected_fields": cleaned_details,
                                "current_field": field_to_ask
                            }
                        }
                    else:
                        # All fields collected, create ticket
                        return self._create_job_ticket(session_id, user_id, cleaned_details, authenticated_user_email)
            
            # Update the last asked field
            final_context = {
                'collected_fields': cleaned_details,
                'timestamp': datetime.now().isoformat(),
                'last_asked_field': field_to_ask
            }
            logger.info(f"Saving final context with field to ask: {final_context}")
            self.session_manager.save_context(session_id, 'hiring_flow', final_context)
            
            # Generate appropriate question based on field
            response_text = self._generate_field_question(field_to_ask, cleaned_details)
            
            return {
                "message": response_text,
                "metadata": {
                    "intent": "hiring",
                    "missing_fields": missing_fields,
                    "collected_fields": cleaned_details,
                    "current_field": field_to_ask
                }
            }
        
        # All details collected - create ticket
        return self._create_job_ticket(session_id, user_id, cleaned_details, authenticated_user_email)
    
    def _is_meaningful_response(self, message: str, field: str) -> bool:
        """Check if the user provided a meaningful response for a specific field"""
        message_lower = message.lower().strip()
        
        # Skip very short or empty responses
        if len(message_lower) < 2:
            return False
        
        # Skip responses that are just "yes", "no", "ok", etc.
        meaningless_responses = ['yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great']
        if message_lower in meaningless_responses:
            return False
        
        # For specific fields, check for relevant content
        if field == 'job_title':
            # Should contain job-related keywords
            job_keywords = ['developer', 'engineer', 'manager', 'analyst', 'designer', 'specialist', 'coordinator', 'assistant', 'director', 'lead', 'senior', 'junior']
            return any(keyword in message_lower for keyword in job_keywords) or len(message_lower.split()) >= 2
        
        elif field == 'location':
            # Should contain location-related content - expanded list
            location_indicators = ['pune', 'mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad', 'remote', 'wfh', 'hybrid', 'office', 'lyon', 'angers', 'paris', 'madrid', 'barcelona', 'berlin', 'munich', 'rome', 'milan', 'amsterdam', 'brussels', 'vienna', 'zurich', 'geneva', 'stockholm', 'copenhagen', 'oslo', 'helsinki', 'warsaw', 'prague', 'budapest', 'bucharest', 'sofia', 'athens', 'lisbon', 'porto', 'dublin', 'edinburgh', 'glasgow', 'manchester', 'birmingham', 'leeds', 'liverpool', 'newcastle', 'bristol', 'cardiff', 'belfast', 'cork', 'galway', 'limerick', 'waterford', 'kilkenny', 'sligo', 'donegal', 'mayo', 'kerry', 'clare', 'tipperary', 'wicklow', 'wexford', 'westmeath', 'longford', 'leitrim', 'roscommon', 'offaly', 'laois', 'carlow', 'kildare', 'meath', 'louth', 'monaghan', 'cavan', 'fermanagh', 'tyrone', 'derry', 'antrim', 'down', 'armagh', 'dublin', 'ireland', 'france', 'spain', 'germany', 'italy', 'netherlands', 'belgium', 'austria', 'switzerland', 'sweden', 'denmark', 'norway', 'finland', 'poland', 'czech republic', 'hungary', 'romania', 'bulgaria', 'greece', 'portugal', 'europe', 'asia', 'africa', 'americas', 'north america', 'south america', 'middle east', 'gulf', 'uae', 'dubai', 'abu dhabi', 'qatar', 'bahrain', 'kuwait', 'saudi arabia', 'oman', 'jordan', 'lebanon', 'egypt', 'morocco', 'tunisia', 'algeria', 'libya', 'sudan', 'ethiopia', 'kenya', 'nigeria', 'south africa', 'ghana', 'tanzania', 'uganda', 'zimbabwe', 'botswana', 'namibia', 'zambia', 'malawi', 'mozambique', 'madagascar', 'mauritius', 'seychelles', 'reunion', 'mayotte', 'comoros', 'djibouti', 'eritrea', 'somalia', 'south sudan', 'central african republic', 'chad', 'cameroon', 'gabon', 'equatorial guinea', 'sao tome and principe', 'congo', 'democratic republic of congo', 'angola', 'burundi', 'rwanda', 'cote d ivoire', 'liberia', 'sierra leone', 'guinea', 'guinea bissau', 'gambia', 'senegal', 'mali', 'burkina faso', 'niger', 'chad', 'sudan', 'south sudan', 'ethiopia', 'eritrea', 'djibouti', 'somalia', 'kenya', 'uganda', 'tanzania', 'rwanda', 'burundi', 'democratic republic of congo', 'central african republic', 'cameroon', 'chad', 'sudan', 'south sudan', 'libya', 'tunisia', 'algeria', 'morocco', 'western sahara', 'mauritania', 'mali', 'burkina faso', 'niger', 'nigeria', 'benin', 'togo', 'ghana', 'cote d ivoire', 'liberia', 'sierra leone', 'guinea', 'guinea bissau', 'gambia', 'senegal', 'cape verde', 'china', 'japan', 'south korea', 'north korea', 'india', 'pakistan', 'bangladesh', 'sri lanka', 'nepal', 'bhutan', 'myanmar', 'thailand', 'laos', 'cambodia', 'vietnam', 'malaysia', 'singapore', 'indonesia', 'philippines', 'brunei', 'timor leste', 'mongolia', 'kazakhstan', 'uzbekistan', 'turkmenistan', 'tajikistan', 'kyrgyzstan', 'afghanistan', 'iran', 'iraq', 'syria', 'lebanon', 'jordan', 'israel', 'palestine', 'turkey', 'georgia', 'armenia', 'azerbaijan', 'russia', 'ukraine', 'belarus', 'moldova', 'estonia', 'latvia', 'lithuania', 'brazil', 'argentina', 'chile', 'peru', 'colombia', 'venezuela', 'ecuador', 'bolivia', 'paraguay', 'uruguay', 'guyana', 'suriname', 'french guiana', 'mexico', 'guatemala', 'belize', 'el salvador', 'honduras', 'nicaragua', 'costa rica', 'panama', 'cuba', 'jamaica', 'haiti', 'dominican republic', 'puerto rico', 'trinidad and tobago', 'barbados', 'saint lucia', 'saint vincent and the grenadines', 'grenada', 'dominica', 'antigua and barbuda', 'saint kitts and nevis', 'bahamas', 'canada', 'united states', 'usa', 'australia', 'new zealand', 'fiji', 'papua new guinea', 'solomon islands', 'vanuatu', 'new caledonia', 'french polynesia', 'samoa', 'tonga', 'kiribati', 'tuvalu', 'nauru', 'palau', 'marshall islands', 'micronesia', 'federated states of micronesia']
            return any(indicator in message_lower for indicator in location_indicators) or len(message_lower.split()) >= 1
        
        elif field == 'experience_required':
            # Should contain numbers or experience-related terms
            import re
            return bool(re.search(r'\d+', message)) or any(term in message_lower for term in ['fresher', 'entry', 'senior', 'junior', 'years', 'experience'])
        
        elif field == 'salary_range':
            # Should contain salary-related terms
            import re
            salary_indicators = ['lpa', 'lakhs', 'crore', 'salary', 'package', 'ctc', 'inr', 'rs', 'rupees']
            return any(indicator in message_lower for indicator in salary_indicators) or bool(re.search(r'\d+', message))
        
        elif field == 'job_description':
            # COMPLETELY AUTOMATIC job description validation using AI intelligence
            return self._is_valid_job_description_response(message)
        
        elif field == 'required_skills':
            # COMPLETELY AUTOMATIC skills validation using AI intelligence
            return self._is_valid_skills_response(message)
        
        elif field == 'employment_type':
            # COMPLETELY AUTOMATIC employment type validation using AI intelligence
            return self._is_valid_employment_type_response(message)
        
        elif field == 'deadline':
            # Should contain date-related content - improved patterns
            import re
            date_patterns = [
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
                r'\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{2,4}',
                r'\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4}',
                r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{2,4}',
                r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{2,4}'
            ]
            return any(re.search(pattern, message, re.IGNORECASE) for pattern in date_patterns) or any(term in message_lower for term in ['deadline', 'date', 'by', 'until', 'before', 'july', 'jul', 'january', 'february', 'march', 'april', 'may', 'june', 'august', 'september', 'october', 'november', 'december'])
        
        # Default: consider it meaningful if it's not empty and not too short
        return len(message_lower) >= 3
    
    def _quick_extract_details(self, message: str) -> Dict:
        """Quick pattern-based extraction for common job details"""
        details = {}
        message_lower = message.lower()
        
        # COMPLETELY AUTOMATIC job title extraction using AI intelligence
        job_title_extracted = self._extract_job_title_intelligently(message)
        if job_title_extracted:
            details['job_title'] = job_title_extracted
        
        # Intelligent location extraction - automatically detects any location name
        location_extracted = self._extract_location_intelligently(message)
        if location_extracted:
            details['location'] = location_extracted
        
        # Experience patterns
        exp_patterns = [
            r'(\d+[-–]\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)',
            r'(fresher|entry|senior|junior)'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, message_lower)
            if match:
                details['experience_required'] = match.group(1)
                break
        
        # Salary patterns
        salary_patterns = [
            r'(\d+[-–]\d+)\s*(?:lpa|lakhs|l)',
            r'(\d+)\s*(?:lpa|lakhs|l)',
            r'(?:salary|package|ctc)\s*(?:of\s+)?(\d+[-–]?\d*)\s*(?:lpa|lakhs|l)?'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, message_lower)
            if match:
                details['salary_range'] = match.group(1) + ' LPA'
                break
        
        # Employment type patterns - improved to capture more variations
        emp_type_patterns = [
            r'(full-time|fulltime|part-time|parttime|contract|internship|intern|freelance|remote|permanent|temporary|seasonal|volunteer|consultant|consulting)'
        ]
        
        for pattern in emp_type_patterns:
            match = re.search(pattern, message_lower)
            if match:
                details['employment_type'] = match.group(1)
                break
        
        # Job description patterns (for longer descriptions)
        if len(message.split()) >= 10:  # If it's a longer message, likely a description
            details['job_description'] = message.strip()
        
        # Skills patterns - STRICT extraction to prevent false positives
        # Only extract skills if message is clearly a skills list with proper formatting
        # Must be comma-separated, contain actual skills, and not be a job description
        if (len(message.split()) < 15 and  # Only for reasonably short responses
            not message.strip().startswith('Skills:') and  # Don't extract if starts with "Skills:"
            not message.strip().startswith('Job Description:') and  # Don't extract if starts with "Job Description:"
            not message.strip().startswith('Requirements:') and  # Don't extract if starts with "Requirements:"
            not any(word in message_lower for word in ['working', 'cases', 'legal', 'court', 'client', 'responsibility', 'duties', 'experience', 'knowledge', 'ability', 'practice', 'handle', 'manage', 'provide', 'assist', 'support', 'should', 'cut', 'hair', 'haircut', 'styling', 'barber', 'salon', 'grooming', 'trimming', 'shaving', 'beard', 'mustache']) and  # Don't extract if contains job description or barber-specific words
            (',' in message or len(message.split()) <= 3)):  # Must be comma-separated or very short
            
            # Only extract if it looks like a proper skills list
            # Check for comma-separated values or single skills
            if ',' in message:
                # Comma-separated skills list
                potential_skills = [skill.strip().lower() for skill in message.split(',')]
                valid_skills = []
                
                for skill in potential_skills:
                    # Only accept if it's a real skill (not generic words)
                    if (skill in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'database', 'api', 'frontend', 'backend', 'fullstack', 'devops', 'aws', 'azure', 'git', 'docker', 'kubernetes', 'django', 'flask', 'spring', 'vue', 'typescript', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'machine learning', 'ai', 'data science', 'analytics', 'statistics', 'r', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop', 'kafka', 'rabbitmq', 'nginx', 'apache', 'linux', 'windows', 'macos', 'ci/cd', 'jenkins', 'travis', 'github actions', 'terraform', 'ansible', 'chef', 'puppet', 'law', 'legal', 'litigation', 'contract', 'corporate', 'criminal', 'civil', 'family', 'immigration', 'patent', 'trademark', 'intellectual property', 'compliance', 'regulatory', 'court', 'advocacy', 'mediation', 'arbitration', 'microsoft office', 'word', 'excel', 'powerpoint', 'outlook', 'adobe', 'photoshop', 'illustrator', 'indesign', 'autocad', 'solidworks', 'matlab', 'spss', 'tableau', 'salesforce', 'hubspot', 'communication', 'leadership', 'management', 'analytical', 'problem solving', 'critical thinking', 'teamwork', 'collaboration', 'presentation', 'negotiation', 'research', 'writing', 'public speaking'] and
                        len(skill) > 2):  # Must be more than 2 characters
                        valid_skills.append(skill)
                
                if len(valid_skills) >= 2:  # Must have at least 2 valid skills
                    details['required_skills'] = ', '.join(valid_skills)
            else:
                # Single skill - must be a clear technical skill
                message_clean = message.strip().lower()
                if (message_clean in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 'database', 'api', 'frontend', 'backend', 'fullstack', 'devops', 'aws', 'azure', 'git', 'docker', 'kubernetes', 'django', 'flask', 'spring', 'vue', 'typescript', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'machine learning', 'ai', 'data science', 'analytics', 'statistics', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop', 'kafka', 'rabbitmq', 'nginx', 'apache', 'linux', 'windows', 'macos', 'ci/cd', 'jenkins', 'travis', 'github actions', 'terraform', 'ansible', 'chef', 'puppet', 'law', 'legal', 'litigation', 'contract', 'corporate', 'criminal', 'civil', 'family', 'immigration', 'patent', 'trademark', 'intellectual property', 'compliance', 'regulatory', 'court', 'advocacy', 'mediation', 'arbitration'] and
                    len(message_clean) > 2):
                    details['required_skills'] = message_clean
        
        # Deadline patterns - improved to capture more date formats
        deadline_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:deadline|by|until|before)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{2,4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})',
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{2,4})',
            r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{2,4})',
            r'(\d{1,2}\s+(?:july|jul)\s+\d{4})',  # Specific pattern for "1 july 2025"
            r'(\d{1,2}\s+(?:july|jul)\s+\d{2,4})'   # More flexible july pattern
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, message)
            if match:
                details['deadline'] = match.group(1)
                break
        
        # Initialize all fields
        for field in Config.REQUIRED_HIRING_DETAILS:
            if field not in details:
                details[field] = "NOT_FOUND"
        
        return details
    
    def _generate_field_question(self, field: str, collected_details: Dict) -> str:
        """Generate intelligent, context-aware questions for specific fields"""
        job_title = collected_details.get('job_title', 'this position')
        
        field_questions = {
            'job_title': "What position are you looking to fill?",
            'location': f"Where will the {job_title} position be based? (e.g., city, country, or 'Remote')",
            'experience_required': f"What level of experience are you looking for in {job_title} candidates? (e.g., '2-3 years', 'Senior level', 'Entry level')",
            'salary_range': f"What's the salary range for the {job_title} position? (e.g., '50k-70k', 'Competitive', 'Based on experience')",
            'job_description': f"Can you provide a detailed description of the {job_title} role? This will help candidates understand the responsibilities and requirements.",
            'required_skills': f"What key skills and qualifications should {job_title} candidates have? (e.g., technical skills, soft skills, certifications)",
            'employment_type': f"What type of employment is this {job_title} position? (Full-time, Part-time, Contract, Internship, etc.)",
            'deadline': f"When is the application deadline for the {job_title} position? (e.g., 'End of month', 'ASAP', specific date)"
        }
        
        return field_questions.get(field, f"Please provide the {field.replace('_', ' ')}.")
    
    def _create_job_ticket(self, session_id: str, user_id: str, cleaned_details: Dict, authenticated_user_email: Optional[str] = None) -> Dict:
        """Create a job ticket with the collected details"""
        # Use authenticated user email if available, otherwise use user_id
        sender_email = authenticated_user_email if authenticated_user_email else user_id
        ticket_id, success = self.ticket_manager.create_ticket(
            session_id, sender_email, cleaned_details
        )
        
        if success:
            # Clear the hiring context since we're done
            self.session_manager.save_context(session_id, 'hiring_flow', {})
            
            response_text = f"""🎉 Great! I've successfully created your job posting!

**Ticket ID:** `{ticket_id}`

**Job Summary:**
• **Position:** {cleaned_details.get('job_title', 'Not specified')}
• **Location:** {cleaned_details.get('location', 'Not specified')}
• **Experience:** {cleaned_details.get('experience_required', 'Not specified')}
• **Salary:** {cleaned_details.get('salary_range', 'Not specified')}
• **Source:** Chat

Your job posting is now pending approval. Once approved, it will be visible on the website.

Is there anything else I can help you with?"""
        else:
            response_text = "I'm sorry, I encountered an error creating your ticket. Please try again."
        
        return {
            "message": response_text,
            "metadata": {
                "intent": "hiring",
                "action": "ticket_created" if success else "error",
                "ticket_id": ticket_id if success else None
            }
        }
    
    def _handle_update_intent(self, session_id: str, user_id: str,
                             message: str, classification: Dict,
                             history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Handle ticket update requests"""
        
        # Check if we're in the middle of an update flow
        update_context = self.session_manager.get_latest_context(session_id, 'update_flow')
        
        # If we have context and user is providing update details
        if update_context and update_context.get('ticket_id'):
            ticket_id = update_context['ticket_id']
            
            # Extract what field to update from the message
            update_prompt = f"""
            The user wants to update ticket {ticket_id}.
            Current message: {message}
            
            Extract what field they want to update and the new value.
            """
            
            update_response = self.update_extractor.generate_reply(
                messages=[{"content": update_prompt, "role": "user"}]
            )
            
            updates = extract_json_from_text(update_response)
            logger.info(f"AI extraction result: {updates}")
            
            if not updates:
                # Try to parse manually
                logger.info(f"AI extraction failed, trying manual parsing for message: {message}")
                updates = {}
                message_lower = message.lower()
                
                if 'salary' in message_lower:
                    # Extract salary value - handle various formats
                    # Try multiple patterns for salary extraction
                    salary_patterns = [
                        r'(\d+\s*to\s*\d+\s*(?:lpa|lakhs|l|k))', # 20 to 30 LPA, 20 to 30 K (prioritize "to" format)
                        r'(\d+[-–]\d+\s*(?:lpa|lakhs|l|k))',  # 20-30 LPA, 20-30 K
                        r'(\d+\s*(?:lpa|lakhs|l|k))',         # 20 LPA, 20 K
                    ]
                    
                    salary_match = None
                    for pattern in salary_patterns:
                        salary_match = re.search(pattern, message_lower)
                        if salary_match:
                            break
                    if salary_match:
                        salary_value = salary_match.group(1).upper().replace('–', '-').replace(' TO ', '-')
                        updates['salary_range'] = salary_value
                        logger.info(f"Manual parsing found salary: {salary_value}")
                    else:
                        logger.info(f"Manual parsing failed to find salary in: {message_lower}")
                
                elif 'location' in message_lower:
                    # Extract location after "to"
                    location_match = re.search(r'to\s+([a-zA-Z\s]+)', message, re.IGNORECASE)
                    if location_match:
                        updates['location'] = location_match.group(1).strip()
                
                elif 'experience' in message_lower:
                    # Extract experience
                    exp_match = re.search(r'(\d+[-–]\d+|\d+)\s*(?:years?|yrs?)?', message_lower)
                    if exp_match:
                        updates['experience_required'] = exp_match.group(1)
                
                elif 'deadline' in message_lower:
                    # Extract deadline
                    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', message)
                    if date_match:
                        updates['deadline'] = date_match.group(1)
            
            logger.info(f"Final updates extracted: {updates}")
            
            if updates:
                logger.info(f"Attempting to update ticket {ticket_id} with updates: {updates}")
                # Perform the update
                success, message_text = self.ticket_manager.update_ticket(
                    ticket_id, user_id, updates
                )
                
                # Clear the update context
                self.session_manager.save_context(session_id, 'update_flow', {})
                
                if success:
                    response_text = f"✅ Successfully updated ticket `{ticket_id}`!\n\n{message_text}"
                else:
                    response_text = f"❌ {message_text}"
                
                return {
                    "message": response_text,
                    "metadata": {"intent": "update", "action": "completed", "ticket_id": ticket_id}
                }
            else:
                return {
                    "message": "I couldn't understand what you want to update. Please specify clearly, for example:\n• 'Change salary to 25-30 LPA'\n• 'Update location to Mumbai'\n• 'Change experience to 5 years'",
                    "metadata": {"intent": "update", "awaiting_update_details": True, "ticket_id": ticket_id}
                }
        
        # Otherwise, we need to identify the ticket first
        ticket_id = classification.get('ticket_id')
        if not ticket_id:
            match = re.search(r'[a-f0-9]{10}', message.lower())
            if match:
                ticket_id = match.group(0)
        
        if not ticket_id:
            return {
                "message": "Please provide the ticket ID you want to update. For example: 'Update ticket abc123def4'",
                "metadata": {"intent": "update", "awaiting_ticket_id": True}
            }
        
        # Get ticket details
        ticket = self.ticket_manager.get_ticket_details(ticket_id)
        
        if not ticket:
            return {
                "message": f"❌ I couldn't find ticket `{ticket_id}`. Please check the ticket ID.",
                "metadata": {"intent": "update", "error": "ticket_not_found"}
            }
        
        # Allow updates for tickets created by user OR tickets from chat source
        if ticket['source'] == 'chat':
            # Chat tickets can be updated by any chat user
            pass
        elif ticket['user_id'] != user_id and ticket['sender'] != user_id:
            return {
                "message": "❌ You don't have permission to update this ticket.",
                "metadata": {"intent": "update", "error": "permission_denied"}
            }
        
        # Save update context
        self.session_manager.save_context(session_id, 'update_flow', {
            'ticket_id': ticket_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # Show current details and ask what to update
        response_text = f"""I found ticket `{ticket_id}` for **{ticket['details'].get('job_title', 'Unknown')}**.

**Current details:**
• **Location:** {ticket['details'].get('location', 'Not set')}
• **Experience:** {ticket['details'].get('experience_required', 'Not set')}
• **Salary:** {ticket['details'].get('salary_range', 'Not set')}
• **Source:** {ticket['source'].capitalize()}

What would you like to update?"""
        
        return {
            "message": response_text,
            "metadata": {"intent": "update", "ticket_id": ticket_id, "awaiting_update_details": True}
        }
    
    def _handle_termination_intent(self, session_id: str, user_id: str,
                                  message: str, classification: Dict,
                                  history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Handle ticket termination requests"""
        
        # Extract ticket ID
        ticket_id = classification.get('ticket_id')
        if not ticket_id:
            match = re.search(r'[a-f0-9]{10}', message.lower())
            if match:
                ticket_id = match.group(0)
        
        if ticket_id:
            success, message_text = self.ticket_manager.terminate_ticket(
                ticket_id, user_id, "User requested termination via chat"
            )
            
            if success:
                response_text = f"✅ I've successfully terminated ticket `{ticket_id}`. The job posting has been removed."
            else:
                response_text = f"❌ {message_text}"
        else:
            response_text = "Please provide the ticket ID you want to terminate. For example: 'Terminate ticket abc123def4'"
        
        return {
            "message": response_text,
            "metadata": {"intent": "termination", "ticket_id": ticket_id}
        }
    
    def _handle_status_check(self, user_id: str, message: str = "") -> Dict:
        """Handle status check requests"""
        tickets = self.ticket_manager.get_user_tickets(user_id)
        
        # Check if user wants to see all tickets in the system
        show_all = any(phrase in message.lower() for phrase in ['all tickets', 'show all', 'all jobs'])
        
        if show_all:
            summary = self.ticket_manager.get_all_tickets_summary()
            response_parts = [f"**System Overview:**"]
            response_parts.append(f"• Total Tickets: {summary['total']}")
            response_parts.append(f"• From Email: {summary['email_tickets']}")
            response_parts.append(f"• From Chat: {summary['chat_tickets']}")
            response_parts.append(f"• Approved (Live on Website): {summary['approved']}")
            response_parts.append(f"• Pending Approval: {summary['pending']}")
            response_parts.append(f"• Terminated: {summary['terminated']}")
            
            if summary['recent_approved']:
                response_parts.append("\n**Recently Approved Jobs (Visible on Website):**")
                for job in summary['recent_approved']:
                    response_parts.append(f"• `{job['ticket_id']}` - {job['job_title'] or 'Unknown'} (Source: {job['source']})")
            
            # Add all active tickets
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT t.ticket_id, t.source, t.approval_status, t.sender,
                           td.field_value as job_title
                    FROM tickets t
                    LEFT JOIN ticket_details td ON t.ticket_id = td.ticket_id 
                        AND td.field_name = 'job_title' AND td.is_initial = TRUE
                    WHERE t.status != 'terminated'
                    ORDER BY t.created_at DESC
                    LIMIT 20
                """)
                all_active = cursor.fetchall()
                
                if all_active:
                    response_parts.append("\n**All Active Tickets:**")
                    for ticket in all_active:
                        status_emoji = "✅" if ticket['approval_status'] == 'approved' else "⏳"
                        response_parts.append(
                            f"• {status_emoji} `{ticket['ticket_id']}` - {ticket['job_title'] or 'Unknown'} "
                            f"(Source: {ticket['source']}, By: {ticket['sender'].split('@')[0]})"
                        )
            
            response_text = "\n".join(response_parts)
        elif not tickets:
            response_text = "You haven't posted any jobs yet. Would you like to create your first job posting?"
        else:
            # Only show approved tickets that are visible on the dashboard
            visible_tickets = [t for t in tickets if t['approval_status'] == 'approved' and t['status'] != 'terminated']
            
            response_parts = ["Here's a summary of your job postings:\n"]
            
            if visible_tickets:
                response_parts.append("**📋 Active Postings (Visible on Dashboard):**")
                for ticket in visible_tickets:
                    source_label = f" ({ticket['source']})" if ticket.get('source') else ""
                    response_parts.append(
                        f"• ✅ `{ticket['ticket_id']}` - {ticket['job_title'] or 'Untitled'}{source_label}"
                    )
            else:
                response_parts.append("**📋 No Active Postings**")
                response_parts.append("You don't have any approved job postings visible on the dashboard yet.")
                
                # Show pending tickets for reference
                pending_tickets = [t for t in tickets if t['approval_status'] == 'pending' and t['status'] != 'terminated']
                if pending_tickets:
                    response_parts.append("\n**⏳ Pending Approval:**")
                    for ticket in pending_tickets:
                        source_label = f" ({ticket['source']})" if ticket.get('source') else ""
                        response_parts.append(
                            f"• ⏳ `{ticket['ticket_id']}` - {ticket['job_title'] or 'Untitled'}{source_label}"
                    )
            
            response_text = "\n".join(response_parts)
        
        return {
            "message": response_text,
            "metadata": {"intent": "status_check"}
        }
    
    def _handle_help_request(self, user_id: str, session_id: str = None) -> Dict:
        """Handle help requests with comprehensive guidance"""
        
        # Clear any active hiring context when help is requested
        if session_id:
            logger.info(f"Clearing hiring context for session {session_id} due to help request")
            self.session_manager.save_context(session_id, 'hiring_flow', {})
            # Also clear the response cache to prevent contaminated results
            response_cache.clear()
        
        response_text = """🤖 **Welcome to your Premium AI Hiring Assistant!**

I'm your intelligent hiring companion, designed to help you with all aspects of recruitment and job management. Here's what I can do:

---

## 📝 **Job Management**
• **Post Jobs**: Say "I want to post a job" for guided job creation
• **View Postings**: "Show my tickets" to see your active jobs
• **Update Jobs**: "Update ticket [ID]" to modify existing postings
• **Close Jobs**: "Terminate ticket [ID]" to end job postings
• **Job Details**: "Show ticket [ID]" for detailed information

---

## 🎯 **Strategic Hiring Support**
• **Job Optimization**: Get advice on improving job descriptions
• **Salary Benchmarking**: Market insights and compensation guidance
• **Candidate Evaluation**: Interview and screening best practices
• **HR Best Practices**: Industry trends and recruitment strategies
• **Skills Assessment**: Help define job requirements and qualifications

---

## 🔧 **System Features**
• **Multi-Channel**: Handles both chat and email job submissions
• **Smart Filtering**: AI-powered resume screening and candidate ranking
• **Approval Workflow**: Streamlined job approval process
• **Analytics**: Track posting performance and candidate metrics
• **Integration**: Seamless workflow with your existing HR systems

---

## 💡 **How to Get Started**
1. **Ask me anything** about hiring, recruitment, or our system
2. **Get strategic advice** on job posting optimization
3. **Learn best practices** for candidate evaluation
4. **Troubleshoot issues** with our platform
5. **Explore features** and advanced capabilities

---

## 🚀 **Advanced Capabilities**
• **Context Awareness**: I remember our conversation history
• **Personalized Guidance**: Tailored advice based on your needs
• **Industry Insights**: Market trends and benchmarking data
• **Proactive Suggestions**: I'll recommend improvements and next steps

**What would you like to explore? Just ask me naturally - I understand context and can handle complex questions!** 🤝"""
        
        return {
            "message": response_text,
            "metadata": {"intent": "help", "premium": True}
        }
    
    def _handle_greeting(self, user_id: str, session_id: str = None) -> Dict:
        """Handle greetings with enhanced personalized welcome and memory"""
        # Get user's recent activity for personalized greeting
        recent_tickets = self.ticket_manager.get_user_tickets(user_id)
        
        # Get conversation insights if available
        conversation_summary = ""
        if session_id:
            conversation_summary = self._get_conversation_summary(session_id, user_id)
        
        if recent_tickets:
            # User has previous activity
            active_jobs = [t for t in recent_tickets if t['approval_status'] == 'approved']
            pending_jobs = [t for t in recent_tickets if t['approval_status'] == 'pending']
            
            # Analyze job patterns for personalization
            job_titles = [t.get('job_title', '') for t in recent_tickets if t.get('job_title')]
            industries = []
            if any('developer' in title.lower() or 'engineer' in title.lower() for title in job_titles):
                industries.append("tech")
            if any('lawyer' in title.lower() or 'legal' in title.lower() for title in job_titles):
                industries.append("legal")
            if any('manager' in title.lower() or 'director' in title.lower() for title in job_titles):
                industries.append("business")
            
            industry_note = ""
            if industries:
                industry_note = f" I notice you focus on {', '.join(industries)} roles."
            
            if active_jobs and pending_jobs:
                greeting = f"Welcome back! 👋 I see you have {len(active_jobs)} active job posting{'s' if len(active_jobs) != 1 else ''} and {len(pending_jobs)} pending approval{'s' if len(pending_jobs) != 1 else ''}.{industry_note}"
            elif active_jobs:
                greeting = f"Welcome back! 👋 Great to see you with {len(active_jobs)} active job posting{'s' if len(active_jobs) != 1 else ''} running.{industry_note}"
            elif pending_jobs:
                greeting = f"Welcome back! 👋 I see you have {len(pending_jobs)} job posting{'s' if len(pending_jobs) != 1 else ''} pending approval.{industry_note}"
            else:
                greeting = f"Welcome back! 👋 Ready to help with your hiring needs.{industry_note}"
        else:
            # New user
            greeting = "Hello! 👋 Welcome to your Premium AI Hiring Assistant!"
        
        # Add conversation context if available
        memory_note = ""
        if conversation_summary and "no previous insights" not in conversation_summary:
            memory_note = f"\n\n🧠 **I remember our previous conversations** - {conversation_summary.lower()}"
        
        response_text = f"""{greeting}

I'm your intelligent hiring companion with enhanced memory, here to help you with:

🎯 **Job Posting & Management**
📊 **Strategic Hiring Advice** 
💼 **Candidate Evaluation**
🚀 **HR Best Practices**
🧠 **Personalized Recommendations**

What would you like to work on today? You can:
• Ask me anything about hiring and recruitment
• Post a new job with guided assistance
• Get insights on your existing postings
• Learn about advanced features
• Get personalized advice based on your patterns

{memory_note}

Just chat with me naturally - I remember our conversations and can provide increasingly personalized help! 🤝"""
        
        return {
            "message": response_text,
            "metadata": {"intent": "greeting", "personalized": True, "enhanced_memory": True}
        }
    
    def _handle_general_question(self, session_id: str, user_id: str,
                                message: str, classification: Dict,
                                history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Handle general questions with enhanced intelligence and memory"""
        context = self._build_context(history)
        
        # Analyze the question type for better responses
        question_type = self._analyze_question_type(message)
        
        # Get user's recent activity for context
        recent_tickets = self.ticket_manager.get_user_tickets(user_id)
        
        # Get user preferences and patterns from conversation history
        user_preferences = self._extract_user_preferences(history, recent_tickets)
        
        prompt = f"""
        USER QUESTION: {message}
        
        CONVERSATION CONTEXT: {context}
        
        USER PROFILE:
        - Recent job postings: {len(recent_tickets)} tickets
        - User type: {'HR Professional' if authenticated_user_email else 'Regular User'}
        - User preferences: {user_preferences}
        
        QUESTION ANALYSIS: {question_type}
        
        INSTRUCTIONS:
        Provide a comprehensive, intelligent response that:
        1. Directly addresses the user's question with expertise
        2. Considers their context, history, and preferences
        3. Offers personalized advice based on their patterns
        4. Suggests relevant next steps or related topics
        5. Maintains a professional yet warm, conversational tone
        6. Uses appropriate emojis to enhance communication
        7. References previous conversations when relevant
        
        SPECIALIZATIONS:
        - Job posting strategies and optimization
        - HR best practices and industry trends
        - System features and workflows
        - Candidate evaluation and interview processes
        - Technical troubleshooting and support
        - Salary benchmarking and market insights
        
        PERSONALIZATION:
        - Reference their previous job postings if relevant
        - Suggest improvements based on their hiring patterns
        - Offer industry-specific advice based on their focus areas
        - Provide tailored recommendations
        
        Be genuinely helpful and add value to every interaction. If you're unsure about something, say so and offer to help find the answer.
        """
        
        response_text = self.responder.generate_reply(
            messages=[{"content": prompt, "role": "user"}]
        )
        
        # Save conversation insights for future reference
        self._save_conversation_insights(session_id, user_id, message, question_type, user_preferences)
        
        return {
            "message": response_text,
            "metadata": {
                "intent": "question",
                "question_type": question_type,
                "enhanced": True,
                "personalized": True,
                "user_preferences": user_preferences
            }
        }
    
    def _handle_approval_intent(self, session_id: str, user_id: str,
                               message: str, classification: Dict,
                               history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Handle ticket approval requests - HR users can approve, others get redirected"""
        
        # Check if user is HR (has authenticated email) or debug mode is enabled
        is_hr_user = authenticated_user_email is not None
        
        if not is_hr_user and not Config.DEBUG_MODE:
            return {
                "message": "Ticket approval is handled by HR administrators through the admin panel. Please contact your HR team for approval.",
                "metadata": {"intent": "approval", "debug_mode": False, "hr_required": True}
            }
        
        # Extract ticket ID
        ticket_id = classification.get('ticket_id')
        if not ticket_id:
            match = re.search(r'[a-f0-9]{10}', message.lower())
            if match:
                ticket_id = match.group(0)
        
        if not ticket_id:
            return {
                "message": "Please provide a ticket ID to approve. For example: 'approve ticket c8a5325ded'",
                "metadata": {"intent": "approval", "error": "no_ticket_id"}
            }
        
        # Get ticket details first to show what we're approving
        ticket = self.ticket_manager.get_ticket_details(ticket_id)
        
        if not ticket:
            return {
                "message": f"❌ I couldn't find ticket `{ticket_id}`. Please check the ticket ID.",
                "metadata": {"intent": "approval", "error": "ticket_not_found"}
            }
        
        # Check if ticket is already approved
        if ticket['approval_status'] == 'approved':
            return {
                "message": f"✅ Ticket `{ticket_id}` is already approved!",
                "metadata": {"intent": "approval", "status": "already_approved", "ticket_id": ticket_id}
            }
        
        # Show ticket details before approval
        details = ticket.get('details', {})
        approval_message = f"""**Approving Ticket: `{ticket_id}`**

**Job Details:**
• **Position:** {details.get('job_title', 'Not specified')}
• **Location:** {details.get('location', 'Not specified')}
• **Experience:** {details.get('experience_required', 'Not specified')}
• **Salary:** {details.get('salary_range', 'Not specified')}
• **Type:** {details.get('employment_type', 'Not specified')}
• **Deadline:** {details.get('deadline', 'Not specified')}

**Description:** {details.get('job_description', 'Not specified')}
**Required Skills:** {details.get('required_skills', 'Not specified')}

**Approved by:** {authenticated_user_email or 'Debug Mode'}

✅ **Ticket has been approved and will now be visible on the website!**"""
        
        # Approve the ticket
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tickets 
                    SET approval_status = 'approved', 
                        approved = TRUE,
                        approved_at = NOW()
                    WHERE ticket_id = %s
                """, (ticket_id,))
                conn.commit()
            
            return {
                "message": approval_message,
                "metadata": {"intent": "approval", "action": "approved", "ticket_id": ticket_id, "approved_by": authenticated_user_email}
            }
            
        except Exception as e:
            return {
                "message": f"❌ Error approving ticket: {str(e)}",
                "metadata": {"intent": "approval", "error": str(e)}
            }
    
    def _handle_show_ticket(self, session_id: str, user_id: str,
                           message: str, classification: Dict,
                           history: List[Dict], authenticated_user_email: Optional[str] = None) -> Dict:
        """Handle show ticket details request"""
        
        # Extract ticket ID
        ticket_id = None
        match = re.search(r'[a-f0-9]{10}', message.lower())
        if match:
            ticket_id = match.group(0)
        
        if not ticket_id:
            return {
                "message": "Please provide a ticket ID. For example: 'show ticket abc123def4'",
                "metadata": {"intent": "show_ticket", "error": "no_ticket_id"}
            }
        
        # Get ticket details
        ticket = self.ticket_manager.get_ticket_details(ticket_id)
        
        if not ticket:
            return {
                "message": f"❌ I couldn't find ticket `{ticket_id}`. Please check the ticket ID.",
                "metadata": {"intent": "show_ticket", "error": "ticket_not_found"}
            }
        
        # Format ticket details
        details = ticket.get('details', {})
        
        status_emoji = "✅" if ticket['approval_status'] == 'approved' else "⏳"
        
        response_text = f"""**Ticket Details: `{ticket_id}`**
        
{status_emoji} **Status:** {ticket['approval_status'].capitalize()} ({ticket['status']})
**Source:** {ticket['source'].capitalize()}
**Created:** {ticket['created_at'].strftime('%Y-%m-%d %H:%M') if ticket.get('created_at') else 'Unknown'}

**Job Information:**
• **Position:** {details.get('job_title', 'Not specified')}
• **Location:** {details.get('location', 'Not specified')}
• **Experience:** {details.get('experience_required', 'Not specified')}
• **Salary:** {details.get('salary_range', 'Not specified')}
• **Type:** {details.get('employment_type', 'Not specified')}
• **Deadline:** {details.get('deadline', 'Not specified')}

**Description:** {details.get('job_description', 'Not specified')}
**Required Skills:** {details.get('required_skills', 'Not specified')}"""
        
        return {
            "message": response_text,
            "metadata": {"intent": "show_ticket", "ticket_id": ticket_id}
        }
    
    def _build_context(self, history: List[Dict]) -> str:
        """Build comprehensive conversation context with enhanced memory and insights"""
        if not history:
            return "No previous conversation context."
        
        context_parts = ["CONVERSATION HISTORY:"]
        
        # Include more context for better understanding
        for msg in history[-8:]:  # Last 8 messages for better context
            sender = "User" if msg['sender_type'] == 'user' else "Assistant"
            # Clean up the message content for better readability
            content = msg['message_content'].strip()
            if content:
                context_parts.append(f"{sender}: {content}")
        
        # Add conversation summary if there's a lot of history
        if len(history) > 8:
            context_parts.insert(1, f"(Previous {len(history) - 8} messages in conversation)")
        
        # Add conversation insights and patterns
        insights = self._analyze_conversation_patterns(history)
        if insights:
            context_parts.append(f"\nCONVERSATION INSIGHTS: {insights}")
        
        return "\n".join(context_parts)
    
    def _analyze_conversation_patterns(self, history: List[Dict]) -> str:
        """Analyze conversation patterns to provide better context"""
        if not history:
            return ""
        
        patterns = []
        
        # Analyze user's interests and focus areas
        user_messages = [msg['message_content'].lower() for msg in history if msg['sender_type'] == 'user']
        
        # Detect hiring patterns
        hiring_keywords = ['hiring', 'job', 'position', 'candidate', 'recruit', 'post', 'posting']
        if any(keyword in ' '.join(user_messages) for keyword in hiring_keywords):
            patterns.append("User is actively hiring")
        
        # Detect specific industries
        tech_keywords = ['developer', 'engineer', 'python', 'java', 'react', 'software', 'tech']
        legal_keywords = ['lawyer', 'legal', 'law', 'litigation', 'contract', 'court']
        business_keywords = ['manager', 'business', 'marketing', 'sales', 'finance']
        
        if any(keyword in ' '.join(user_messages) for keyword in tech_keywords):
            patterns.append("Focus on tech roles")
        elif any(keyword in ' '.join(user_messages) for keyword in legal_keywords):
            patterns.append("Focus on legal roles")
        elif any(keyword in ' '.join(user_messages) for keyword in business_keywords):
            patterns.append("Focus on business roles")
        
        # Detect user's experience level
        if any(phrase in ' '.join(user_messages) for phrase in ['senior', 'lead', 'principal', 'architect']):
            patterns.append("Prefers senior-level positions")
        elif any(phrase in ' '.join(user_messages) for phrase in ['junior', 'entry', 'fresher', 'intern']):
            patterns.append("Open to junior-level positions")
        
        # Detect geographic preferences
        location_keywords = ['remote', 'hybrid', 'office', 'onsite']
        if any(keyword in ' '.join(user_messages) for keyword in location_keywords):
            patterns.append("Has location preferences")
        
        return "; ".join(patterns) if patterns else "General hiring discussion"
    
    def _extract_user_preferences(self, history: List[Dict], recent_tickets: List[Dict]) -> str:
        """Extract user preferences and patterns from conversation history and tickets"""
        preferences = []
        
        if not history and not recent_tickets:
            return "New user - no preferences yet"
        
        # Analyze recent tickets for patterns
        if recent_tickets:
            job_titles = [ticket.get('job_title', '').lower() for ticket in recent_tickets if ticket.get('job_title')]
            locations = [ticket.get('location', '').lower() for ticket in recent_tickets if ticket.get('location')]
            employment_types = [ticket.get('employment_type', '').lower() for ticket in recent_tickets if ticket.get('employment_type')]
            
            # Industry preferences
            if any('developer' in title or 'engineer' in title or 'programmer' in title for title in job_titles):
                preferences.append("Tech industry focus")
            elif any('lawyer' in title or 'legal' in title or 'attorney' in title for title in job_titles):
                preferences.append("Legal industry focus")
            elif any('manager' in title or 'director' in title or 'executive' in title for title in job_titles):
                preferences.append("Business/Management focus")
            
            # Location preferences
            if any('remote' in loc for loc in locations):
                preferences.append("Prefers remote positions")
            elif any('hybrid' in loc for loc in locations):
                preferences.append("Prefers hybrid work")
            
            # Employment type preferences
            if any('contract' in emp_type for emp_type in employment_types):
                preferences.append("Open to contract work")
            elif any('intern' in emp_type for emp_type in employment_types):
                preferences.append("Hires interns")
            elif any('full-time' in emp_type or 'fulltime' in emp_type for emp_type in employment_types):
                preferences.append("Prefers full-time positions")
        
        # Analyze conversation history for communication style preferences
        user_messages = [msg['message_content'] for msg in history if msg['sender_type'] == 'user']
        
        # Communication style
        if any(len(msg) > 100 for msg in user_messages):
            preferences.append("Detailed communicator")
        elif any(len(msg) < 20 for msg in user_messages):
            preferences.append("Concise communicator")
        
        # Question patterns
        if any('?' in msg for msg in user_messages):
            preferences.append("Asks detailed questions")
        
        # Industry-specific terminology usage
        all_text = ' '.join(user_messages).lower()
        if any(term in all_text for term in ['agile', 'scrum', 'devops', 'ci/cd']):
            preferences.append("Uses modern tech terminology")
        elif any(term in all_text for term in ['litigation', 'compliance', 'regulatory', 'intellectual property']):
            preferences.append("Uses legal terminology")
        
        return "; ".join(preferences) if preferences else "General preferences"
    
    def _extract_location_intelligently(self, message: str) -> str:
        """Intelligently extract location from any message using AI and smart patterns"""
        message_lower = message.lower().strip()
        
        # Skip if message is too long (likely a job description)
        if len(message.split()) > 15:
            return None
        
        # Common work arrangement patterns
        work_arrangements = ['remote', 'wfh', 'work from home', 'hybrid', 'onsite', 'office', 'in-person']
        for arrangement in work_arrangements:
            if arrangement in message_lower:
                return arrangement.title()
        
        # Check for explicit location context patterns first
        location_context_patterns = [
            r'(?:in|at|based in|located in|position in|job in|work in)\s+([a-zA-Z\s]+)',
            r'(?:from|to|near|around)\s+([a-zA-Z\s]+)',
        ]
        
        for pattern in location_context_patterns:
            match = re.search(pattern, message_lower)
            if match:
                location = match.group(1).strip()
                if self._is_likely_location_ai(location):
                    return location.title()
        
        # If it's a very short response (1-3 words), analyze if it's likely a location
        words = message.split()
        if len(words) <= 3 and len(words) >= 1:
            potential_location = message.strip()
            
            # Skip obvious non-location responses
            if self._is_non_location_response(potential_location):
                return None
            
            # Additional check: if it's a very short response (1-2 characters), 
            # it's likely a job title abbreviation, not a location
            if len(potential_location) <= 2:
                return None
            
            # Use AI-based location detection for better accuracy
            if self._is_likely_location_ai(potential_location):
                return potential_location.title()
        
        return None
    
    def _is_non_location_response(self, text: str) -> bool:
        """Check if text is clearly not a location (yes/no responses, job titles, etc.)"""
        text_lower = text.lower().strip()
        
        # Basic non-location responses
        basic_non_locations = [
            'yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great', 
            'thanks', 'thank you', 'please', 'hello', 'hi', 'hey'
        ]
        
        if text_lower in basic_non_locations:
            return True
        
        # Employment type keywords
        employment_types = [
            'full-time', 'fulltime', 'part-time', 'parttime', 'contract', 'internship', 
            'intern', 'freelance', 'permanent', 'temporary', 'seasonal', 'volunteer'
        ]
        
        if text_lower in employment_types:
            return True
        
        # Technical skills/tools
        if text_lower in ['python', 'java', 'javascript', 'react', 'angular', 'node', 'sql', 
                         'database', 'api', 'frontend', 'backend', 'fullstack', 'devops', 
                         'aws', 'azure', 'git', 'docker', 'kubernetes']:
            return True
        
        # Use intelligent AI-based job title detection instead of manual lists
        if self._is_likely_job_title_ai(text):
            return True
        
        # Numbers or experience patterns (likely experience responses)
        import re
        if re.search(r'\d+[-–]?\d*\s*(?:years?|yrs?|months?|experience)', text_lower):
            return True
        
        # Salary patterns (likely salary responses)
        if re.search(r'\d+[-–]?\d*\s*(?:lpa|lakhs?|crores?|k|thousand|million|salary|package|ctc)', text_lower):
            return True
        
        return False
    
    def _is_likely_location(self, text: str) -> bool:
        """Determine if text is likely a geographical location using multiple intelligent criteria"""
        text_lower = text.lower().strip()
        
        # Skip if too long or contains problematic patterns
        if len(text.split()) > 5 or len(text) > 50:
            return False
        
        # Skip if contains numbers (locations typically don't have numbers)
        if any(char.isdigit() for char in text):
            return False
        
        # Skip if starts with action words
        action_starters = ['should', 'must', 'need', 'require', 'want', 'like', 'can', 'will', 'would']
        if any(text_lower.startswith(word) for word in action_starters):
            return False
        
        # Check for job title patterns using intelligent pattern recognition (NOT manual lists)
        import re
        
        # Pattern-based job title detection - these patterns catch most job titles automatically
        job_patterns = [
            # Professional suffixes that indicate job titles
            r'\b\w+(?:er|or|ist|ian|ant|ent)\b$',  # developer, manager, accountant, therapist, etc.
            r'\b\w+(?:man|woman|person)\b$',  # salesman, chairwoman, spokesperson
            # Job title prefixes
            r'\b(?:senior|junior|lead|principal|chief|head|vice|assistant|associate|deputy)\s+\w+',
            # Common job title structures
            r'\b\w+\s+(?:engineer|developer|manager|analyst|designer|specialist|coordinator|assistant|director|officer|representative|agent|advisor|consultant|instructor|technician|operator|supervisor|executive)\b',
            # Medical/healthcare roles
            r'\b(?:doctor|physician|surgeon|nurse|therapist|pharmacist|dentist|veterinarian)\b',
            # Legal roles  
            r'\b(?:lawyer|attorney|judge|paralegal)\b',
            # Service roles
            r'\b(?:teacher|professor|instructor|trainer|coach|tutor)\b',
            # Trade roles
            r'\b(?:electrician|plumber|carpenter|painter|welder|mechanic)\b',
            # Food service
            r'\b(?:chef|cook|waiter|waitress|bartender|barista)\b',
            # Transport/logistics
            r'\b(?:driver|pilot|captain)\b',
            # Finance/business
            r'\b(?:accountant|banker|teller|broker|realtor)\b',
            # General service
            r'\b(?:clerk|secretary|receptionist|cashier|janitor|cleaner|guard)\b'
        ]
        
        for pattern in job_patterns:
            if re.search(pattern, text_lower):
                return False
        
        # Check for location indicators (these suggest it IS a location)
        location_indicators = [
            # Geographic suffixes
            r'\b\w+(?:ville|town|city|burg|ford|field|wood|land|port|bridge|mount|hill|dale|valley|beach|bay|lake|river|creek|falls|springs)\b',
            # Common location patterns
            r'\b(?:new|old|north|south|east|west|upper|lower|greater|little|big|saint|st\.?|mount|mt\.?)\s+\w+',
            # Country/state/region patterns
            r'\b\w+(?:ia|ana|ina|aska|ada|ida|ota|oma|ama|ica|istan|land|shire|sex|folk|wick|ham|ton|don|chester|cester|minster)\b'
        ]
        
        for pattern in location_indicators:
            if re.search(pattern, text_lower):
                return True
        
        # If it passes basic checks and doesn't match job patterns, likely a location
        # This covers simple city names like "Paris", "Tokyo", "Mumbai", etc.
        # But be more conservative - require at least 3 characters for simple names
        if (len(text.strip()) >= 3 and 
            text.isalpha() and 
            not self._is_non_location_response(text) and
            not any(text_lower.endswith(ending) for ending in ['ing', 'ed', 'er', 'ly', 'tion', 'sion', 'ment', 'ness', 'ity', 'ous', 'ful', 'less'])):
            return True
        
        return False
    
    def _is_likely_location_ai(self, text: str) -> bool:
        """Intelligent AI-based location detection - no manual lists required"""
        text_lower = text.lower().strip()
        
        # Skip if too long (likely not a location)
        if len(text.split()) > 5 or len(text) > 50:
            return False
        
        # Skip obvious non-locations
        if text_lower in ['yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great', 'thanks', 'thank you']:
            return False
        
        # Use AI to determine if it's a location
        try:
            ai_prompt = f"""
            Analyze if the following text is likely a geographical location or place name:
            
            Text: "{text}"
            
            Consider:
            - Cities (New York, London, Mumbai, Tokyo, etc.)
            - Countries (USA, India, UK, Canada, etc.)
            - States/Provinces (California, Texas, Ontario, etc.)
            - Regions (Silicon Valley, Bay Area, etc.)
            - Work arrangements (Remote, Hybrid, Onsite, etc.)
            - Office locations (Downtown, Uptown, etc.)
            
            This should NOT be considered a location:
            - Job titles (BA, BSC, Manager, Engineer, etc.)
            - Skills (Python, Java, SQL, etc.)
            - Experience levels (5 years, Senior, etc.)
            - Salary information (50k, 100k, etc.)
            - General words (good, should, etc.)
            
            Respond with ONLY "YES" if it's likely a location, or "NO" if it's not.
            """
            
            response = self.extractor.generate_reply(
                messages=[{"content": ai_prompt, "role": "user"}]
            )
            
            # Check if AI response indicates it's a location
            response_lower = response.lower().strip()
            return "yes" in response_lower and "no" not in response_lower
            
        except Exception as e:
            logger.warning(f"AI location detection failed: {e}, using fallback")
            # Fallback to pattern-based detection
            return self._is_likely_location(text)
    
    def _is_likely_job_title_ai(self, text: str) -> bool:
        """Intelligent AI-based job title detection - no manual lists required"""
        text_lower = text.lower().strip()
        
        # Skip if too long (likely not a job title)
        if len(text.split()) > 5 or len(text) > 50:
            return False
        
        # Skip obvious non-job titles
        if text_lower in ['yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great', 'thanks', 'thank you']:
            return False
        
        # Use AI to determine if it's a job title
        try:
            ai_prompt = f"""
            Analyze if the following text is likely a job title or position name:
            
            Text: "{text}"
            
            Consider:
            - Job titles can be abbreviations (BA, BSC, PM, HR, etc.)
            - Job titles can be full names (Business Analyst, Project Manager, etc.)
            - Job titles can be technical roles (Software Engineer, Data Scientist, etc.)
            - Job titles can be business roles (Manager, Director, Analyst, etc.)
            - Job titles can be creative roles (Designer, Writer, Artist, etc.)
            - Job titles can be service roles (Consultant, Advisor, Specialist, etc.)
            
            Respond with ONLY "YES" if it's likely a job title, or "NO" if it's not.
            """
            
            response = self.extractor.generate_reply(
                messages=[{"content": ai_prompt, "role": "user"}]
            )
            
            # Check if AI response indicates it's a job title
            response_lower = response.lower().strip()
            return "yes" in response_lower and "no" not in response_lower
            
        except Exception as e:
            logger.warning(f"AI job title detection failed: {e}, using fallback")
            # Fallback to pattern-based detection
            return self._is_likely_job_title_pattern(text)
    
    def _is_likely_job_title_pattern(self, text: str) -> bool:
        """Fallback pattern-based job title detection"""
        text_lower = text.lower().strip()
        
        # Pattern-based job title detection
        job_patterns = [
            # Professional suffixes
            r'\b\w+(?:er|or|ist|ian|ant|ent|eer|eer)\b$',
            # Job title structures
            r'\b\w+\s+(?:engineer|developer|manager|analyst|designer|specialist|coordinator|assistant|director|officer|representative|agent|advisor|consultant|instructor|technician|operator|supervisor|executive|architect|scientist|researcher|coordinator|administrator|supervisor|lead|head|chief|principal|senior|junior|associate|deputy|vice)\b',
            # Common abbreviations (but only as fallback)
            r'\b(?:ba|bsc|btech|mca|mba|mtech|phd|ms|ma|bcom|mcom|hr|it|qa|dev|pm|sm|po|ux|ui|seo|smm|dm|am|tl|cto|cfo|ceo|coo|vp|avp|svp|evp|gm|dgm|agm|se|sde|sdet|qe|dba|sre|ml|ai|ds|da|bi|etl|fe|be|fs|devops|infra|sec|pentest|audit|compliance)\b'
        ]
        
        import re
        for pattern in job_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_valid_skills_response(self, message: str) -> bool:
        """Accept ANY skills input from users - no restrictions"""
        message_lower = message.lower().strip()
        
        # Only reject completely empty or very short responses
        if len(message_lower.strip()) < 1:
            return False
        
        # Skip responses that are just "yes", "no", "ok", etc.
        meaningless_responses = ['yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great']
        if message_lower in meaningless_responses:
            return False
        
        # Accept ANY other input as valid skills
        # This includes:
        # - Single skills: "Python"
        # - Multiple skills: "Python, Java, SQL"
        # - Comprehensive lists: "Azure, GCP, Terraform, Docker, Kubernetes..."
        # - Skills with descriptions: "Python programming, Java development"
        # - Any format the user provides
        return True
    
    def _is_valid_employment_type_response(self, message: str) -> bool:
        """Completely automatic employment type validation using AI intelligence - no manual lists"""
        message_lower = message.lower().strip()
        
        # Basic validation: must be reasonable length and not empty
        if len(message_lower.strip()) < 2:
            return False
        
        # Check for employment type patterns using AI-like logic
        employment_indicators = [
            # Common employment type patterns (automatically detected)
            any(pattern in message_lower for pattern in [
                'full', 'part', 'contract', 'intern', 'freelance', 'remote', 'permanent', 
                'temporary', 'seasonal', 'volunteer', 'consultant', 'time', 'employment',
                'job type', 'work type', 'position type', 'role type'
            ]),
            # Time-related indicators
            any(time_word in message_lower for time_word in ['time', 'hour', 'day', 'week', 'month']),
            # Work arrangement indicators
            any(arrangement in message_lower for arrangement in ['remote', 'office', 'hybrid', 'onsite']),
            # Duration indicators
            any(duration in message_lower for duration in ['permanent', 'temporary', 'short', 'long']),
            # Employment status indicators
            any(status in message_lower for status in ['full-time', 'part-time', 'contract', 'internship'])
        ]
        
        # If any employment indicators are present, it's a valid response
        return any(employment_indicators)
    
    def _extract_comprehensive_job_details(self, message: str, full_context: str) -> Dict:
        """Premium extraction method for comprehensive job posting requests"""
        details = {}
        
        # Initialize all fields as NOT_FOUND
        for field in Config.REQUIRED_HIRING_DETAILS:
            details[field] = "NOT_FOUND"
        
        # Check if this is a comprehensive job posting request
        comprehensive_indicators = [
            'looking for', 'hiring for', 'need a', 'require a', 'seeking',
            'position for', 'role for', 'job for', 'opening for',
            'years experience', 'salary', 'location', 'skills', 'requirements',
            'full-time', 'part-time', 'contract', 'remote', 'hybrid'
        ]
        
        message_lower = message.lower()
        is_comprehensive = any(indicator in message_lower for indicator in comprehensive_indicators)
        
        if is_comprehensive or len(message.split()) > 10:
            # This looks like a comprehensive job posting - use AI extraction
            extraction_prompt = f"""
            You are a premium AI hiring assistant. Extract ALL job posting details from this comprehensive request.
            
            User Request: {message}
            
            Extract the following fields with high accuracy:
            - job_title: The specific position/role name (e.g., "Senior Python Developer", "Business Analyst", "Marketing Manager")
            - location: Work location (e.g., "New York", "Remote", "Hybrid", "Pune, India")
            - experience_required: Years of experience (e.g., "3-5 years", "5+ years", "Entry level")
            - salary_range: Salary/compensation (e.g., "$80,000-100,000", "₹8-12 LPA", "Competitive")
            - job_description: Detailed role description and responsibilities
            - required_skills: Key skills and qualifications (e.g., "Python, SQL, AWS", "MBA, 3+ years experience")
            - employment_type: Full-time/Part-time/Contract/Internship
            - deadline: Application deadline if mentioned
            
            PREMIUM EXTRACTION RULES:
            1. Be intelligent and extract information even if not explicitly labeled
            2. Infer context from the request (e.g., if they say "5 years experience", extract that)
            3. If location isn't mentioned, infer from context or mark as "NOT_FOUND"
            4. Extract skills from job descriptions and requirements
            5. Be comprehensive - don't miss any details
            6. If information is implied but not explicit, extract it intelligently
            
            Return ONLY a JSON object with the extracted fields. Use "NOT_FOUND" for missing fields.
            """
            
            try:
                extraction_response = self.extractor.generate_reply(
                    messages=[{"content": extraction_prompt, "role": "user"}]
                )
                
                ai_details = extract_json_from_text(extraction_response) or {}
                logger.info(f"Premium AI extraction response: {ai_details}")
                
                # Merge AI results
                for key, value in ai_details.items():
                    if value and value != "NOT_FOUND" and len(str(value).strip()) > 0:
                        details[key] = str(value).strip()
                
            except Exception as e:
                logger.warning(f"Premium AI extraction failed: {e}, falling back to simple extraction")
                # Fall back to simple extraction
                details = self._quick_extract_details(message)
        
        return details

    def _extract_job_title_intelligently(self, message: str) -> str:
        """Completely automatic job title extraction using AI intelligence - no manual lists"""
        message_lower = message.lower().strip()
        
        # Skip if message is too long (likely a job description)
        if len(message.split()) > 15:
            return None
        
        # If it's a very short response (1-5 words), likely a job title
        words = message.split()
        if len(words) <= 5 and len(words) >= 1:
            potential_title = message.strip()
            
            # Skip obvious non-job title words
            non_title_words = [
                'yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great', 'thanks', 'thank you',
                'full-time', 'part-time', 'contract', 'internship', 'intern', 'freelance', 'remote', 'permanent',
                'temporary', 'seasonal', 'volunteer', 'consultant', 'consulting',
                'speaking', 'injection', 'healthcare', 'medical', 'patient', 'treatment', 'therapy',
                'medicine', 'drugs', 'pharmacy', 'hospital', 'clinic', 'diagnosis', 'symptoms',
                'disease', 'illness', 'health', 'care', 'nursing', 'surgery', 'operation', 'procedure',
                'examination', 'checkup', 'prescription', 'dosage', 'medication', 'vaccination',
                'immunization', 'python', 'java', 'javascript', 'react', 'angular', 'node', 'sql',
                'database', 'api', 'frontend', 'backend', 'fullstack', 'devops', 'aws', 'azure',
                'git', 'docker', 'kubernetes', 'law', 'legal', 'litigation', 'contract', 'corporate',
                'criminal', 'civil', 'family', 'immigration', 'patent', 'trademark', 'intellectual',
                'property', 'compliance', 'regulatory', 'court', 'advocacy', 'mediation', 'arbitration',
                'funny', 'good', 'communication', 'skills', 'customer', 'service', 'hair', 'cutting',
                'styling', 'barber', 'salon', 'grooming', 'trimming', 'shaving', 'beard', 'mustache',
                'circus', 'entertainment', 'performance', 'acting', 'comedy', 'humor', 'joker'
            ]
            
            if potential_title.lower() not in non_title_words and len(potential_title) > 1:
                # Additional validation - check if it looks like a job title
                if (not potential_title.lower().startswith(('should', 'must', 'need', 'require', 'want', 'like')) and
                    not any(char.isdigit() for char in potential_title) and  # No numbers in job titles
                    len(potential_title) >= 2):  # At least 2 characters
                    
                    return potential_title.title()
        
        # Check for job title context patterns - but skip generic job posting requests
        # Skip if this looks like a generic job posting request
        generic_requests = [
            'post a job', 'create job', 'new job', 'job opening', 'add a job', 
            'create posting', 'job posting', 'hire someone', 'post job'
        ]
        
        if any(req in message_lower for req in generic_requests):
            return None  # Don't extract job title from generic requests
        
        title_context_patterns = [
            r'(?:looking for|need|hiring)\s+(?:a\s+)?([a-zA-Z\s]+)',
            r'(?:position|role|job)\s+(?:of\s+)?([a-zA-Z\s]+)',
            r'(?:as|for)\s+([a-zA-Z\s]+)',
        ]
        
        for pattern in title_context_patterns:
            match = re.search(pattern, message_lower)
            if match:
                title = match.group(1).strip()
                # Validate extracted title
                if (len(title) > 1 and len(title) <= 100 and 
                    not any(word in title.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 
                                                             'designer', 'specialist', 'coordinator', 'assistant',
                                                             'director', 'lead', 'principal', 'staff', 'architect',
                                                             'consultant', 'intern', 'trainee', 'skills', 'ability',
                                                             'knowledge', 'experience', 'communication', 'customer',
                                                             'service', 'time', 'management', 'technical', 'mechanical',
                                                             'personal', 'attributes', 'responsibility', 'guidelines',
                                                             'emergency', 'situations', 'polite', 'professional',
                                                             'interaction', 'courteous', 'respectful', 'helpful',
                                                             'attitude', 'toward', 'assist', 'children', 'elderly',
                                                             'special', 'needs', 'schedules', 'timely', 'arrivals',
                                                             'departures', 'punctuality', 'reliability', 'awareness',
                                                             'maintenance', 'troubleshooting', 'detect', 'report',
                                                             'mechanical', 'issues', 'promptly', 'patience', 'stress',
                                                             'stamina', 'hours', 'appearance', 'discipline'])):
                    return title.title()
        
        return None
    
    def _is_valid_job_description_response(self, message: str) -> bool:
        """Completely automatic job description validation - accepts any reasonable response"""
        message_lower = message.lower().strip()
        
        # Basic validation: must be reasonable length and not empty
        if len(message_lower.strip()) < 2:
            return False
        
        # Check for simple responses that are not job descriptions
        simple_responses = ['yes', 'no', 'ok', 'okay', 'sure', 'fine', 'alright', 'good', 'great', 'thanks', 'thank you']
        if message_lower in simple_responses:
            return False
        
        # ACCEPT ANY OTHER REASONABLE RESPONSE - no manual lists needed!
        # This includes "working on python", "developing apps", "managing teams", etc.
        # The AI will automatically understand and process any meaningful description
        return True
    
    def _save_conversation_insights(self, session_id: str, user_id: str, message: str, question_type: str, user_preferences: str):
        """Save conversation insights for learning and personalization"""
        try:
            # Create insights context
            insights_context = {
                'user_id': user_id,
                'session_id': session_id,
                'message_type': question_type,
                'user_preferences': user_preferences,
                'timestamp': datetime.now().isoformat(),
                'message_length': len(message),
                'has_technical_terms': any(term in message.lower() for term in ['python', 'java', 'react', 'aws', 'docker', 'kubernetes']),
                'has_legal_terms': any(term in message.lower() for term in ['law', 'legal', 'litigation', 'contract', 'court']),
                'has_business_terms': any(term in message.lower() for term in ['manager', 'business', 'marketing', 'sales', 'finance']),
                'question_complexity': 'high' if len(message.split()) > 20 else 'medium' if len(message.split()) > 10 else 'low'
            }
            
            # Save to session manager for this conversation
            self.session_manager.save_context(session_id, 'conversation_insights', insights_context)
            
            logger.info(f"Saved conversation insights for user {user_id}: {question_type}")
            
        except Exception as e:
            logger.warning(f"Failed to save conversation insights: {e}")
    
    def _get_conversation_summary(self, session_id: str, user_id: str) -> str:
        """Get a summary of the conversation for context"""
        try:
            insights = self.session_manager.get_latest_context(session_id, 'conversation_insights')
            if insights:
                return f"User has been asking about {insights.get('message_type', 'general topics')} and shows preferences for {insights.get('user_preferences', 'general hiring')}"
            return "New conversation - no previous insights"
        except Exception as e:
            logger.warning(f"Failed to get conversation summary: {e}")
            return "Unable to retrieve conversation summary"
    
    def _build_hiring_context(self, history: List[Dict], current_message: str) -> str:
        """Build context for hiring detail extraction - only include user messages to avoid contamination"""
        messages = []
        for msg in history:
            if msg['sender_type'] == 'user':
                messages.append(f"User: {msg['message_content']}")
            # Don't include assistant messages as they can contaminate extraction
            # (e.g., "How many years of experience..." gets extracted as experience_required)
        messages.append(f"User: {current_message}")
        return "\n".join(messages)
    
    def _reset_hiring_context(self, session_id: str):
        """Reset the hiring context for a fresh start"""
        self.session_manager.save_context(session_id, 'hiring_flow', {})
        logger.info(f"Reset hiring context for session {session_id}")
    
    def _get_conversation_progress(self, session_id: str) -> Dict:
        """Get the current progress of the hiring conversation"""
        hiring_context = self.session_manager.get_latest_context(session_id, 'hiring_flow')
        if not hiring_context:
            return {"status": "not_started", "collected_fields": {}, "missing_fields": Config.REQUIRED_HIRING_DETAILS}
        
        collected_fields = hiring_context.get('collected_fields', {})
        missing_fields = []
        for field in Config.REQUIRED_HIRING_DETAILS:
            if field not in collected_fields or collected_fields.get(field) == "NOT_FOUND":
                missing_fields.append(field)
        
        return {
            "status": "in_progress" if missing_fields else "completed",
            "collected_fields": collected_fields,
            "missing_fields": missing_fields,
            "last_asked_field": hiring_context.get('last_asked_field')
        }
    
    def _analyze_question_type(self, message: str) -> str:
        """Analyze the type of question being asked for better responses"""
        message_lower = message.lower()
        
        # HR and recruitment questions
        if any(word in message_lower for word in ['salary', 'compensation', 'pay', 'wage', 'benefits']):
            return "salary_compensation"
        elif any(word in message_lower for word in ['interview', 'screening', 'candidate', 'resume', 'cv']):
            return "candidate_evaluation"
        elif any(word in message_lower for word in ['hiring', 'recruitment', 'talent', 'acquisition']):
            return "hiring_strategy"
        elif any(word in message_lower for word in ['job posting', 'job description', 'job ad', 'advertisement']):
            return "job_posting"
        elif any(word in message_lower for word in ['skills', 'qualifications', 'requirements', 'experience']):
            return "job_requirements"
        
        # System and technical questions
        elif any(word in message_lower for word in ['how to', 'how do i', 'how does', 'how can']):
            return "how_to_guide"
        elif any(word in message_lower for word in ['what is', 'what are', 'what does', 'explain']):
            return "explanation"
        elif any(word in message_lower for word in ['error', 'problem', 'issue', 'not working', 'broken']):
            return "troubleshooting"
        elif any(word in message_lower for word in ['feature', 'functionality', 'capability', 'option']):
            return "feature_inquiry"
        
        # Process and workflow questions
        elif any(word in message_lower for word in ['process', 'workflow', 'steps', 'procedure']):
            return "process_workflow"
        elif any(word in message_lower for word in ['approval', 'approve', 'pending', 'status']):
            return "approval_process"
        elif any(word in message_lower for word in ['time', 'duration', 'how long', 'when']):
            return "timing_schedule"
        
        # Industry and market questions
        elif any(word in message_lower for word in ['trend', 'market', 'industry', 'benchmark']):
            return "market_insights"
        elif any(word in message_lower for word in ['best practice', 'recommendation', 'advice', 'tip']):
            return "best_practices"
        
        # General questions
        elif any(word in message_lower for word in ['help', 'assistance', 'support']):
            return "help_request"
        elif message_lower.endswith('?') or message_lower.startswith(('what', 'why', 'when', 'where', 'who', 'how')):
            return "general_inquiry"
        else:
            return "general_conversation"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def extract_json_from_text(text: str) -> Optional[Dict]:
    """Extract JSON from text that might contain other content"""
    if not text:
        return None
    
    try:
        # Try direct parsing
        return json.loads(text.strip())
    except:
        # Try to find JSON in the text
        start = text.find('{')
        end = text.rfind('}')
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end+1])
            except:
                pass
    return None

def parse_and_validate_deadline(deadline_str: str) -> Tuple[bool, str, Optional[datetime]]:
    """Parse and validate deadline date string"""
    try:
        # Common date formats
        date_formats = [
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%y',
            '%d/%m/%y',
        ]
        
        parsed_date = None
        deadline_clean = deadline_str.strip()
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(deadline_clean, fmt)
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            return False, "Please provide the deadline in DD-MM-YYYY format.", None
        
        # Check if date is in the future
        if parsed_date <= datetime.now():
            return False, "The deadline must be in the future.", None
        
        # Format the date
        formatted_date = parsed_date.strftime('%d-%m-%Y')
        return True, formatted_date, parsed_date
        
    except Exception as e:
        return False, "Invalid date format. Please use DD-MM-YYYY.", None

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def show_system_status(db_manager: DatabaseManager):
    """Display system status"""
    print("\n" + "="*60)
    print("UNIFIED SYSTEM STATUS")
    print("="*60)
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN source = 'email' THEN 1 ELSE 0 END) as email_tickets,
                    SUM(CASE WHEN source = 'chat' THEN 1 ELSE 0 END) as chat_tickets,
                    SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'terminated' THEN 1 ELSE 0 END) as terminated
                FROM tickets
            """)
            
            stats = cursor.fetchone()
            
            print(f"\nTotal Tickets: {stats['total']}")
            print(f"  - From Email: {stats['email_tickets']}")
            print(f"  - From Chat: {stats['chat_tickets']}")
            print(f"  - Approved: {stats['approved']}")
            print(f"  - Pending: {stats['pending']}")
            print(f"  - Terminated: {stats['terminated']}")
            
            # Show approved jobs
            print("\nApproved Jobs (visible on website):")
            cursor.execute("""
                SELECT t.ticket_id, t.source, td.field_value as job_title
                FROM tickets t
                LEFT JOIN ticket_details td ON t.ticket_id = td.ticket_id 
                    AND td.field_name = 'job_title' AND td.is_initial = TRUE
                WHERE t.approval_status = 'approved'
                ORDER BY t.approved_at DESC
                LIMIT 10
            """)
            
            approved_jobs = cursor.fetchall()
            if approved_jobs:
                for job in approved_jobs:
                    print(f"  - {job['ticket_id']} | {job['job_title'] or 'Unknown'} | Source: {job['source']}")
            else:
                print("  - No approved jobs")
                
    except Exception as e:
        print(f"Error displaying status: {e}")

# ============================================================================
# MAIN ENTRY POINT AND TEST FUNCTIONS
# ============================================================================

def test_chatbot():
    """Test the chatbot with sample conversations"""
    print("\n" + "="*60)
    print("TESTING CHAT BOT WITH LANGUAGE DETECTION")
    print("="*60)
    
    bot = ChatBotHandler()
    
    # Start a new session
    session_data = bot.start_session("test_user_123")
    session_id = session_data['session_id']
    user_id = session_data['user_id']
    
    print(f"\nSession started: {session_id}")
    print(f"Bot: {session_data['message']}")
    
    # Test cases
    test_messages = [
        # Test non-English messages
        "नमस्ते, मुझे एक नौकरी पोस्ट करनी है",  # Hindi
        "Hola, necesito publicar un trabajo",  # Spanish
        "કેમ છો? મારે નોકરી પોસ્ટ કરવી છે",  # Gujarati
        "Bonjour, je veux poster un emploi",  # French
        "你好，我想发布一个职位",  # Chinese
        
        # Test English messages
        "Hello, I want to post a job",
        "Software Engineer",
        "Mumbai",
        "5-7 years",
        "25-30 LPA",
        "Looking for a senior software engineer with Python and Django experience",
        "Python, Django, REST APIs, PostgreSQL",
        "Full-time",
        "31-01-2025",
        
        # Test other features
        "show my tickets",
        "update ticket",  # This will fail without a ticket ID
        "কাজের তালিকা দেখান",  # Bengali - "show job list"
        "help",
        "مرحبا",  # Arabic greeting
    ]
    
    for message in test_messages:
        print(f"\n{'='*40}")
        print(f"User: {message}")
        
        response = bot.process_message(session_id, user_id, message)
        print(f"Bot: {response['message'][:200]}...")  # Show first 200 chars
        
        if response.get('metadata'):
            print(f"Metadata: {response['metadata']}")
        
        import time
        time.sleep(0.5)  # Small delay between messages

def main():
    """Main entry point for the chat bot"""
    print("\n" + "="*60)
    print("AI CHAT BOT WITH LANGUAGE DETECTION")
    print("="*60)
    
    try:
        # Initialize the bot
        bot = ChatBotHandler()
        
        # Show system status
        show_system_status(bot.db_manager)
        
        # Run test
        print("\nRunning test conversation...")
        test_chatbot()
        
        print("\n" + "="*60)
        print("Chat bot is ready for integration!")
        print("="*60)
        
    except Exception as e:
        print(f"\nError initializing chat bot: {e}")
        import traceback
        traceback.print_exc()

# ============================================================================
# EXPORT
# ============================================================================

__all__ = ['ChatBotHandler', 'Config', 'show_system_status', 'main']

if __name__ == "__main__":
    main()