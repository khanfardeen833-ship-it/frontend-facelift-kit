# Resume Filtering System with LLM-Powered Job Analysis
# LLM used ONLY for job analysis - candidate data processed 100% locally
# Works for ANY job worldwide - zero hardcoding

import os
import json
import PyPDF2
from docx import Document
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from datetime import datetime
import pandas as pd
from pathlib import Path
import re
import hashlib
import time
from difflib import SequenceMatcher
from collections import defaultdict
from fuzzywuzzy import fuzz
import jellyfish
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

class ResumeExtractor:
    """Extract text from various resume formats"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            return ""
    
    @staticmethod
    def extract_text(file_path: Path) -> str:
        """Extract text from resume file"""
        file_path_str = str(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            return ResumeExtractor.extract_text_from_pdf(file_path_str)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return ResumeExtractor.extract_text_from_docx(file_path_str)
        elif file_path.suffix.lower() == '.txt':
            with open(file_path_str, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return ""


class DuplicateCandidateDetector:
    """Advanced duplicate candidate detection system"""
    
    def __init__(self):
        self.candidates_db = {}
        self.email_to_id = {}
        self.phone_to_id = {}
        self.name_variations = defaultdict(set)
        
    def extract_candidate_identifiers(self, resume_text: str, filename: str) -> Dict:
        """Extract all possible identifiers from resume"""
        identifiers = {
            'filename': filename,
            'emails': self._extract_emails(resume_text),
            'phones': self._extract_phones(resume_text),
            'names': self._extract_names(resume_text),
            'github': self._extract_github(resume_text),
            'linkedin': self._extract_linkedin(resume_text),
            'content_hash': self._generate_content_hash(resume_text),
            'education_hash': self._generate_education_hash(resume_text),
            'experience_hash': self._generate_experience_hash(resume_text)
        }
        return identifiers
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract and validate email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        valid_emails = []
        for email in emails:
            email_lower = email.lower()
            if not any(invalid in email_lower for invalid in ['example.com', 'test.com', '@gmail.co']):
                valid_emails.append(email_lower)
                
        return list(set(valid_emails))
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extract and normalize phone numbers"""
        phone_patterns = [
            r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})',
            r'\+?(\d{1,3})[\s.-]?(\d{3,4})[\s.-]?(\d{3,4})[\s.-]?(\d{3,4})',
            r'\b(\d{10})\b',
            r'\+91[\s.-]?(\d{10})',
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    phone = ''.join(match)
                else:
                    phone = match
                
                phone_digits = re.sub(r'\D', '', phone)
                
                if len(phone_digits) >= 10:
                    normalized = phone_digits[-10:]
                    phones.append(normalized)
        
        return list(set(phones))
    
    def _extract_names(self, text: str) -> List[str]:
        """Extract potential names from resume"""
        names = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            
            if not line or any(keyword in line.lower() for keyword in 
                             ['resume', 'curriculum', 'cv', 'objective', 'summary']):
                continue
            
            words = line.split()
            if 2 <= len(words) <= 4:
                if all(word[0].isupper() for word in words if word):
                    names.append(line)
        
        name_pattern = r'(?:Name|NAME|name)\s*[:|-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        name_matches = re.findall(name_pattern, text)
        names.extend(name_matches)
        
        return list(set(names))
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub username"""
        github_patterns = [
            r'github\.com/([a-zA-Z0-9-]+)',
            r'github\s*:\s*([a-zA-Z0-9-]+)',
            r'@([a-zA-Z0-9-]+)\s*\(github\)',
        ]
        
        for pattern in github_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return None
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile ID"""
        linkedin_patterns = [
            r'linkedin\.com/in/([a-zA-Z0-9-]+)',
            r'linkedin\s*:\s*([a-zA-Z0-9-]+)',
        ]
        
        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return None
    
    def _generate_content_hash(self, text: str) -> str:
        """Generate hash of key content"""
        lines = text.split('\n')
        content_lines = lines[5:] if len(lines) > 5 else lines
        
        content = '\n'.join(content_lines)
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        content = re.sub(r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})', '', content)
        
        content = ' '.join(content.split())
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_education_hash(self, text: str) -> str:
        """Generate hash based on education details"""
        education_section = self._extract_section(text, ['education', 'academic', 'qualification'])
        
        degree_patterns = [
            r'(B\.?S\.?|B\.?Sc\.?|Bachelor|B\.?Tech|B\.?E\.?)',
            r'(M\.?S\.?|M\.?Sc\.?|Master|M\.?Tech|MBA|M\.?E\.?)',
            r'(Ph\.?D\.?|Doctorate)',
        ]
        
        degrees = []
        for pattern in degree_patterns:
            matches = re.findall(pattern, education_section, re.IGNORECASE)
            degrees.extend(matches)
        
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', education_section)
        
        edu_string = ' '.join(sorted(degrees + years))
        return hashlib.md5(edu_string.encode()).hexdigest()[:16]
    
    def _generate_experience_hash(self, text: str) -> str:
        """Generate hash based on work experience"""
        experience_section = self._extract_section(text, ['experience', 'employment', 'work history'])
        
        companies = re.findall(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b', experience_section)
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', experience_section)
        
        tech_keywords = ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'kubernetes']
        techs_found = [tech for tech in tech_keywords if tech in experience_section.lower()]
        
        exp_string = ' '.join(sorted(companies[:5] + years + techs_found))
        return hashlib.md5(exp_string.encode()).hexdigest()[:16]
    
    def _extract_section(self, text: str, section_keywords: List[str]) -> str:
        """Extract a section from resume based on keywords"""
        lines = text.split('\n')
        section_start = -1
        section_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in section_keywords):
                section_start = i
                continue
            
            if section_start >= 0:
                if any(keyword in line_lower for keyword in 
                      ['experience', 'education', 'skills', 'projects', 'summary', 'objective']):
                    if not any(keyword in line_lower for keyword in section_keywords):
                        break
                
                section_lines.append(line)
        
        return '\n'.join(section_lines)
    
    def calculate_similarity_score(self, id1: Dict, id2: Dict) -> Dict[str, float]:
        """Calculate similarity scores between two candidates"""
        scores = {
            'email_match': 0.0,
            'phone_match': 0.0,
            'name_similarity': 0.0,
            'github_match': 0.0,
            'linkedin_match': 0.0,
            'content_similarity': 0.0,
            'education_match': 0.0,
            'experience_match': 0.0
        }
        
        if id1['emails'] and id2['emails']:
            if set(id1['emails']) & set(id2['emails']):
                scores['email_match'] = 1.0
        
        if id1['phones'] and id2['phones']:
            if set(id1['phones']) & set(id2['phones']):
                scores['phone_match'] = 1.0
        
        if id1['names'] and id2['names']:
            max_similarity = 0.0
            for name1 in id1['names']:
                for name2 in id2['names']:
                    # Check if names are completely different (different first names)
                    name1_parts = name1.lower().split()
                    name2_parts = name2.lower().split()
                    
                    # If first names are completely different, reduce similarity significantly
                    if name1_parts and name2_parts:
                        first_name1 = name1_parts[0]
                        first_name2 = name2_parts[0]
                        
                        # If first names are completely different, this is likely a different person
                        if first_name1 != first_name2:
                            # Check if they're at least somewhat similar (nicknames, variations)
                            fuzzy_score = fuzz.token_sort_ratio(name1.lower(), name2.lower()) / 100.0
                            
                            # Only consider high similarity if names are very close
                            if fuzzy_score < 0.7:
                                # Different first names with low similarity - likely different people
                                similarity = fuzzy_score * 0.3  # Reduce similarity significantly
                            else:
                                similarity = fuzzy_score
                        else:
                            # Same first name, calculate normal similarity
                            fuzzy_score = fuzz.token_sort_ratio(name1.lower(), name2.lower()) / 100.0
                            similarity = fuzzy_score
                    else:
                        # Fallback to original logic
                        fuzzy_score = fuzz.token_sort_ratio(name1.lower(), name2.lower()) / 100.0
                        similarity = fuzzy_score
                    
                    try:
                        phonetic_score = 1.0 if jellyfish.soundex(name1) == jellyfish.soundex(name2) else 0.0
                        # Only use phonetic score if names are already somewhat similar
                        if similarity > 0.5:
                            similarity = max(similarity, phonetic_score)
                    except:
                        pass
                    
                    # Be more conservative with contains_score for different names
                    if similarity < 0.6:  # Only if names are already quite different
                        contains_score = 0.4 if (name1.lower() in name2.lower() or 
                                               name2.lower() in name1.lower()) else 0.0
                        similarity = max(similarity, contains_score)
                    
                    max_similarity = max(max_similarity, similarity)
            
            scores['name_similarity'] = max_similarity
        
        if id1['github'] and id2['github']:
            scores['github_match'] = 1.0 if id1['github'] == id2['github'] else 0.0
        
        if id1['linkedin'] and id2['linkedin']:
            scores['linkedin_match'] = 1.0 if id1['linkedin'] == id2['linkedin'] else 0.0
        
        if id1['content_hash'] == id2['content_hash']:
            scores['content_similarity'] = 1.0
        
        if id1['education_hash'] == id2['education_hash']:
            scores['education_match'] = 0.8
        
        if id1['experience_hash'] == id2['experience_hash']:
            scores['experience_match'] = 0.8
        
        return scores
    
    def is_duplicate(self, scores: Dict[str, float]) -> Tuple[bool, float, str]:
        """Determine if two candidates are duplicates based on scores"""
        
        # Strong indicators of same person
        if scores['email_match'] == 1.0:
            return True, 1.0, "Same email address"
        
        if scores['phone_match'] == 1.0:
            # Phone number matching is unreliable for different people
            # Only consider phone match if we have VERY strong evidence it's the same person
            # This prevents false positives when different people share phone numbers
            
            # Check if this is likely a false positive (different people)
            if scores['name_similarity'] < 0.5:  # Very different names
                return False, scores['phone_match'], "Same phone number but very different names - likely different people"
            
            # Even with similar names, require multiple strong indicators
            strong_indicators = 0
            
            if scores['name_similarity'] > 0.8:
                strong_indicators += 1
            if scores['content_similarity'] > 0.9:
                strong_indicators += 1
            if scores['github_match'] == 1.0:
                strong_indicators += 1
            if scores['linkedin_match'] == 1.0:
                strong_indicators += 1
            if scores['education_match'] > 0.8:
                strong_indicators += 1
            if scores['experience_match'] > 0.8:
                strong_indicators += 1
            
            # Require at least 3 strong indicators for phone match to be considered duplicate
            # This is very conservative to avoid false positives
            if strong_indicators >= 3:
                return True, 0.95, f"Same phone number with {strong_indicators} strong indicators"
            else:
                return False, scores['phone_match'], f"Same phone number but only {strong_indicators} strong indicators - likely different people"
        
        if scores['github_match'] == 1.0:
            return True, 0.95, "Same GitHub account"
        
        if scores['linkedin_match'] == 1.0:
            return True, 0.95, "Same LinkedIn profile"
        
        if scores['content_similarity'] == 1.0:
            return True, 0.9, "Identical resume content"
        
        weighted_score = (
            scores['name_similarity'] * 0.3 +
            scores['education_match'] * 0.25 +
            scores['experience_match'] * 0.25 +
            scores['content_similarity'] * 0.2
        )
        
        # More stringent requirements for considering as duplicate
        if (scores['name_similarity'] > 0.8 and 
            scores['education_match'] > 0.8 and 
            scores['experience_match'] > 0.8):
            return True, weighted_score, "Very high similarity in name, education, and experience"
        
        if weighted_score > 0.9:  # Increased threshold from 0.85 to 0.9
            return True, weighted_score, "Very high overall similarity"
        
        return False, weighted_score, "Not duplicate"
    
    def is_different_person(self, id1: Dict, id2: Dict) -> bool:
        """Check if two candidates are clearly different people"""
        # If they have different names and different emails, they're likely different people
        # even if they share other characteristics like phone numbers
        
        # Check if names are completely different
        if id1['names'] and id2['names']:
            name1_parts = id1['names'][0].lower().split()
            name2_parts = id2['names'][0].lower().split()
            
            if name1_parts and name2_parts:
                first_name1 = name1_parts[0]
                first_name2 = name2_parts[0]
                
                # If first names are completely different, they're likely different people
                if first_name1 != first_name2:
                    # Check if emails are also different
                    if id1['emails'] and id2['emails']:
                        email1 = id1['emails'][0].lower()
                        email2 = id2['emails'][0].lower()
                        
                        # If both names and emails are different, they're definitely different people
                        if email1 != email2:
                            return True
        
        return False
    
    def add_candidate(self, resume_text: str, filename: str) -> Tuple[str, List[Dict]]:
        """Add candidate and check for duplicates"""
        identifiers = self.extract_candidate_identifiers(resume_text, filename)
        
        duplicates = []
        
        # Check for duplicates before adding to database
        for email in identifiers['emails']:
            if email in self.email_to_id:
                existing_id = self.email_to_id[email]
                existing = self.candidates_db[existing_id]
                scores = self.calculate_similarity_score(identifiers, existing)
                is_dup, confidence, reason = self.is_duplicate(scores)
                if is_dup:
                    duplicates.append({
                        'candidate_id': existing_id,
                        'filename': existing['filename'],
                        'confidence': confidence,
                        'reason': reason,
                        'matched_by': 'email'
                    })
        
        for phone in identifiers['phones']:
            if phone in self.phone_to_id:
                existing_id = self.phone_to_id[phone]
                if not any(d['candidate_id'] == existing_id for d in duplicates):
                    existing = self.candidates_db[existing_id]
                    scores = self.calculate_similarity_score(identifiers, existing)
                    
                    # Check if these are clearly different people
                    if self.is_different_person(identifiers, existing):
                        # These are clearly different people, don't mark as duplicate
                        continue
                    
                    is_dup, confidence, reason = self.is_duplicate(scores)
                    if is_dup:
                        duplicates.append({
                            'candidate_id': existing_id,
                            'filename': existing['filename'],
                            'confidence': confidence,
                            'reason': reason,
                            'matched_by': 'phone'
                        })
        
        if not duplicates:
            for cand_id, candidate in self.candidates_db.items():
                scores = self.calculate_similarity_score(identifiers, candidate)
                is_dup, confidence, reason = self.is_duplicate(scores)
                if is_dup:
                    duplicates.append({
                        'candidate_id': cand_id,
                        'filename': candidate['filename'],
                        'confidence': confidence,
                        'reason': reason,
                        'matched_by': 'similarity'
                    })
        
        # Generate candidate ID
        candidate_id = hashlib.md5(f"{filename}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Add to database
        self.candidates_db[candidate_id] = identifiers
        
        # Only store identifiers if this is a truly unique candidate
        # or if we're confident it's not a duplicate
        if not duplicates:
            # This is a unique candidate, safe to store all identifiers
            for email in identifiers['emails']:
                self.email_to_id[email] = candidate_id
            
            for phone in identifiers['phones']:
                self.phone_to_id[phone] = candidate_id
            
            for name in identifiers['names']:
                self.name_variations[name.lower()].add(candidate_id)
        else:
            # This candidate has duplicates, be more careful about storing identifiers
            # Only store email if it's unique (no other candidate has it)
            for email in identifiers['emails']:
                if email not in self.email_to_id:
                    self.email_to_id[email] = candidate_id
            
            # Be very conservative with phone numbers for candidates with duplicates
            # Only store if we're confident it's not a false positive
            for phone in identifiers['phones']:
                if phone not in self.phone_to_id:
                    # Check if this phone number is truly unique
                    phone_is_unique = True
                    for dup in duplicates:
                        if dup.get('matched_by') == 'phone':
                            # This phone number caused a duplicate detection
                            # Don't store it to avoid future false positives
                            phone_is_unique = False
                            break
                    
                    if phone_is_unique:
                        self.phone_to_id[phone] = candidate_id
            
            # Store names for duplicate candidates
            for name in identifiers['names']:
                self.name_variations[name.lower()].add(candidate_id)
        
        return candidate_id, duplicates
    
    def get_duplicate_groups(self) -> List[List[Dict]]:
        """Get groups of duplicate candidates with details"""
        groups = []
        processed = set()
        
        for cand_id in self.candidates_db:
            if cand_id in processed:
                continue
            
            group = [{'candidate_id': cand_id, 'filename': self.candidates_db[cand_id]['filename']}]
            processed.add(cand_id)
            
            candidate = self.candidates_db[cand_id]
            
            for email in candidate['emails']:
                for other_id in self.candidates_db:
                    if other_id != cand_id and other_id not in processed:
                        if email in self.candidates_db[other_id]['emails']:
                            group.append({
                                'candidate_id': other_id,
                                'filename': self.candidates_db[other_id]['filename']
                            })
                            processed.add(other_id)
            
            for phone in candidate['phones']:
                for other_id in self.candidates_db:
                    if other_id != cand_id and other_id not in processed:
                        if phone in self.candidates_db[other_id]['phones']:
                            group.append({
                                'candidate_id': other_id,
                                'filename': self.candidates_db[other_id]['filename']
                            })
                            processed.add(other_id)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups


class DuplicateHandlingStrategy:
    """Strategies for handling duplicate candidates"""
    
    @staticmethod
    def merge_scores(candidates: List[Dict]) -> Dict:
        """Merge scores from duplicate candidates, taking the best scores"""
        if not candidates:
            return {}
        
        merged = candidates[0].copy()
        
        all_filenames = [c['filename'] for c in candidates]
        merged['all_filenames'] = all_filenames
        merged['duplicate_count'] = len(candidates)
        
        for candidate in candidates[1:]:
            if candidate.get('final_score', 0) > merged.get('final_score', 0):
                merged['final_score'] = candidate['final_score']
            
            if candidate.get('skill_score', 0) > merged.get('skill_score', 0):
                merged['skill_score'] = candidate['skill_score']
                merged['matched_skills'] = candidate.get('matched_skills', [])
            
            if candidate.get('experience_score', 0) > merged.get('experience_score', 0):
                merged['experience_score'] = candidate['experience_score']
                merged['detected_experience_years'] = candidate.get('detected_experience_years', 0)
            
            if candidate.get('professional_development_score', 0) > merged.get('professional_development_score', 0):
                merged['professional_development_score'] = candidate['professional_development_score']
                merged['professional_development'] = candidate.get('professional_development', {})
        
        merged['has_duplicates'] = True
        merged['duplicate_info'] = {
            'count': len(candidates),
            'filenames': all_filenames,
            'selected_filename': merged['filename']
        }
        
        return merged


class EnhancedJobTicket:
    """Enhanced JobTicket class that reads latest updates from JSON structure"""
    
    def __init__(self, ticket_folder: str):
        self.ticket_folder = Path(ticket_folder)
        self.ticket_id = self.ticket_folder.name
        self.raw_data = self._load_raw_data()
        self.job_details = self._merge_with_updates()
        self._print_loaded_details()
    
    def _load_raw_data(self) -> Dict:
        """Load the raw JSON data from the ticket folder"""
        priority_files = ['job_details.json', 'job-data.json', 'job.json']
        json_file = None
        
        for filename in priority_files:
            file_path = self.ticket_folder / filename
            if file_path.exists():
                json_file = file_path
                break
        
        if not json_file:
            json_files = [f for f in self.ticket_folder.glob("*.json") 
                         if f.name not in ['metadata.json', 'applications.json']]
            if json_files:
                json_file = json_files[0]
        
        if not json_file:
            app_file = self.ticket_folder / 'applications.json'
            if app_file.exists():
                json_file = app_file
            else:
                raise FileNotFoundError(f"No JSON file found in {self.ticket_folder}")
        
        print(f"Loading job details from: {json_file.name}")
        
        job_desc_file = self.ticket_folder / 'job-description.txt'
        job_description_text = ""
        if job_desc_file.exists():
            print(f"📝 Loading job description from: job-description.txt")
            with open(job_desc_file, 'r', encoding='utf-8') as f:
                job_description_text = f.read()
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if job_description_text and isinstance(data, dict):
                if 'job_description' not in data:
                    data['job_description'] = job_description_text
                if 'job_details' in data and 'job_description' not in data['job_details']:
                    data['job_details']['job_description'] = job_description_text
            
            return data
        except Exception as e:
            print(f"ERROR: Error loading JSON: {e}")
            raise
    
    def _merge_with_updates(self) -> Dict:
        """Merge initial details with latest updates"""
        if isinstance(self.raw_data, list):
            print("📝 Detected applications list format, creating job structure...")
            merged_details = {
                'ticket_id': self.ticket_id,
                'applications': self.raw_data,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'job_title': 'Software Developer',
                'position': 'Software Developer',
                'experience_required': '2+ years',
                'location': 'Remote',
                'salary_range': 'Competitive',
                'required_skills': 'Python, JavaScript, SQL',
                'job_description': 'We are looking for a talented developer',
                'deadline': 'Open until filled'
            }
            return merged_details
        
        if 'ticket_info' in self.raw_data and 'job_details' in self.raw_data:
            merged_details = self.raw_data['job_details'].copy()
            merged_details['ticket_id'] = self.raw_data['ticket_info'].get('ticket_id', self.ticket_id)
            merged_details['status'] = self.raw_data['ticket_info'].get('status', 'active')
            merged_details['created_at'] = self.raw_data['ticket_info'].get('created_at', '')
            merged_details['last_updated'] = self.raw_data.get('saved_at', '')
            return merged_details
        
        if 'initial_details' in self.raw_data:
            merged_details = self.raw_data['initial_details'].copy()
        else:
            merged_details = self.raw_data.copy()
        
        merged_details['ticket_id'] = self.raw_data.get('ticket_id', self.ticket_id)
        merged_details['status'] = self.raw_data.get('status', 'unknown')
        merged_details['created_at'] = self.raw_data.get('created_at', '')
        merged_details['last_updated'] = self.raw_data.get('last_updated', '')
        
        if 'updates' in self.raw_data and self.raw_data['updates']:
            print(f"📝 Found {len(self.raw_data['updates'])} update(s)")
            
            sorted_updates = sorted(
                self.raw_data['updates'], 
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            
            latest_update = sorted_updates[0]
            print(f"SUCCESS: Applying latest update from: {latest_update.get('timestamp', 'unknown')}")
            
            if 'details' in latest_update:
                for key, value in latest_update['details'].items():
                    if value:
                        merged_details[key] = value
                        print(f"   Updated {key}: {value}")
        
        return merged_details
    
    def _print_loaded_details(self):
        """Print the loaded job details for verification"""
        print("\n" + "="*60)
        print("📋 LOADED JOB REQUIREMENTS")
        print("="*60)
        print(f"Position: {self.position}")
        print(f"Experience: {self.experience_required}")
        print(f"Location: {self.location}")
        print(f"Salary: {self.salary_range}")
        print(f"Skills: {', '.join(self.tech_stack)}")
        print(f"Deadline: {self.deadline}")
        print(f"Last Updated: {self.job_details.get('last_updated', 'Unknown')}")
        print("="*60 + "\n")
    
    def _parse_skills(self, skills_str: str) -> List[str]:
        """Parse skills from string format to list"""
        if isinstance(skills_str, list):
            return skills_str
        
        if not skills_str:
            return []
        
        skills = re.split(r'[,;|]\s*', skills_str)
        expanded_skills = []
        
        for skill in skills:
            if '(' in skill and ')' in skill:
                main_skill = skill[:skill.index('(')].strip()
                variations = skill[skill.index('(')+1:skill.index(')')].strip()
                expanded_skills.append(main_skill)
                if '/' in variations:
                    expanded_skills.extend([v.strip() for v in variations.split('/')])
                else:
                    expanded_skills.append(variations)
            else:
                expanded_skills.append(skill.strip())
        
        return list(set([s for s in expanded_skills if s]))
    
    @property
    def position(self) -> str:
        return (self.job_details.get('job_title') or 
                self.job_details.get('position') or 
                self.job_details.get('title', 'Unknown Position'))
    
    @property
    def experience_required(self) -> str:
        return (self.job_details.get('experience_required') or 
                self.job_details.get('experience') or 
                self.job_details.get('years_of_experience', '0+ years'))
    
    @property
    def location(self) -> str:
        return self.job_details.get('location', 'Not specified')
    
    @property
    def salary_range(self) -> str:
        salary = self.job_details.get('salary_range', '')
        if isinstance(salary, dict):
            min_sal = salary.get('min', '')
            max_sal = salary.get('max', '')
            currency = salary.get('currency', 'INR')
            return f"{currency} {min_sal}-{max_sal}"
        return salary or 'Not specified'
    
    @property
    def deadline(self) -> str:
        return self.job_details.get('deadline', 'Not specified')
    
    @property
    def tech_stack(self) -> List[str]:
        skills = self.job_details.get('required_skills') or self.job_details.get('tech_stack', '')
        return self._parse_skills(skills)
    
    @property
    def requirements(self) -> List[str]:
        requirements = []
        
        if self.job_details.get('job_description'):
            requirements.append(self.job_details['job_description'])
        
        req_field = self.job_details.get('requirements', [])
        if isinstance(req_field, str):
            requirements.extend([r.strip() for r in req_field.split('\n') if r.strip()])
        elif isinstance(req_field, list):
            requirements.extend(req_field)
        
        return requirements
    
    @property
    def description(self) -> str:
        return (self.job_details.get('job_description') or 
                self.job_details.get('description') or 
                self.job_details.get('summary', ''))
    
    @property
    def employment_type(self) -> str:
        return self.job_details.get('employment_type', 'Full-time')
    
    @property
    def nice_to_have(self) -> List[str]:
        nice = (self.job_details.get('nice_to_have') or 
                self.job_details.get('preferred_skills') or 
                self.job_details.get('bonus_skills', []))
        
        if isinstance(nice, str):
            return [n.strip() for n in nice.split('\n') if n.strip()]
        elif isinstance(nice, list):
            return nice
        return []
    
    def get_resumes(self) -> List[Path]:
        """Get all resume files from the ticket folder"""
        resume_extensions = ['.pdf', '.docx', '.doc', '.txt']
        resumes = []
        
        for ext in resume_extensions:
            resumes.extend(self.ticket_folder.glob(f"*{ext}"))
        
        excluded_keywords = ['job_description', 'job-description', 'requirements', 'jd', 'job_posting', 'job-posting']
        filtered_resumes = []
        
        for resume in resumes:
            if not any(keyword in resume.name.lower().replace('_', '-') for keyword in excluded_keywords):
                filtered_resumes.append(resume)
            else:
                print(f"   ℹ️ Excluding non-resume file: {resume.name}")
        
        return filtered_resumes


class LLMJobAnalyzer:
    """
    🤖 Uses LLM to analyze ANY job in the world
    🔒 NEVER sends candidate resumes to LLM - only job descriptions
    🌍 Works for: Bus Driver, Chef, Doctor, Software Engineer, Astronaut, etc.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key and self.openai_api_key != 'your_openai_api_key_here':
            openai.api_key = self.openai_api_key
            self.llm_available = True
            print("✓ LLM-powered universal job analysis enabled")
            print("🔒 Privacy Mode: Candidate resumes NEVER sent to LLM")
        else:
            self.llm_available = False
            print("⚠ LLM not available - using basic fallback mode")
            print("   To enable LLM: Add your OpenAI API key to config.env")
    
    def analyze_any_job_worldwide(self, job_title: str, job_description: str, 
                                   provided_skills: List[str] = None) -> Dict[str, Any]:
        """
        Analyze ANY job anywhere in the world using LLM
        Works for: Any industry, any country, any role
        
        Returns comprehensive job analysis without ANY hardcoding
        """
        
        if not self.llm_available:
            return self._basic_fallback(job_title, provided_skills or [])
        
        try:
            print(f"\n🤖 Analyzing job with AI: {job_title}")
            
            skills_str = ', '.join(provided_skills) if provided_skills else 'Not specified in job posting'
            
            prompt = f"""You are an expert global HR analyst with deep knowledge of ALL industries and job types worldwide.

Analyze this job posting for ANY role in ANY industry in ANY country:

**Job Title:** {job_title}

**Job Description:**
{job_description}

**Skills Listed in Job Posting:**
{skills_str}

Your task: Provide a COMPLETE analysis that will help match candidates to this job.

Return a JSON object with these fields:

1. **job_category**: Main industry (e.g., "Transportation", "Healthcare", "Technology", "Hospitality", "Construction", "Education", "Manufacturing", "Agriculture", "Creative Arts", "Public Service", "Sports", etc.)

2. **job_subcategory**: Specific role type (e.g., "Bus Driver", "Heart Surgeon", "Full Stack Developer", "Pastry Chef")

3. **country_region**: Where this job is located (if mentioned, otherwise "Global")

4. **all_required_skills**: COMPREHENSIVE list of ALL skills needed (extract from description + add implied skills):
   - Technical skills (tools, software, equipment)
   - Certifications/Licenses (CDL, Medical License, Teaching Certificate, etc.)
   - Soft skills (communication, leadership, time management)
   - Physical requirements (if any - lifting, standing, driving)
   - Language skills (if mentioned)
   - Domain knowledge
   Include EVERYTHING a candidate needs to succeed in this role.

5. **skill_variations_map**: For EACH skill, provide ALL possible ways it might appear in a resume:
   Example for Bus Driver:
   {{
     "Commercial Driver's License": ["CDL", "commercial driver license", "commercial driving license", "class B license", "class A CDL", "CDL Class B", "commercial vehicle license"],
     "Route Planning": ["route planning", "route navigation", "route management", "trip planning", "route optimization"],
     "Passenger Safety": ["passenger safety", "safety procedures", "safe driving", "defensive driving", "safety compliance"]
   }}
   
   Example for Software Engineer:
   {{
     "Python": ["python", "py", "python3", "python programming", "python developer"],
     "React": ["react", "reactjs", "react.js", "react framework", "react library"]
   }}

6. **required_certifications**: List ALL certifications, licenses, or credentials needed or preferred:
   - For Bus Driver: ["Commercial Driver's License (CDL)", "Clean Driving Record", "DOT Physical"]
   - For Doctor: ["Medical Degree (MD/DO)", "Board Certification", "State Medical License"]
   - For Teacher: ["Teaching Credential", "Bachelor's in Education", "Subject Certification"]

7. **scoring_weights**: How important is each criterion for THIS specific job? (must sum to 1.0)
   Consider:
   - Technical roles: Higher skills weight
   - Regulated professions: Higher certification weight
   - Senior roles: Higher experience weight
   - Location-dependent roles (bus driver, teacher): Higher location weight
   - Remote roles: Lower location weight
   {{
     "skills": 0.0-1.0,
     "experience": 0.0-1.0,
     "location": 0.0-1.0,
     "certifications": 0.0-1.0,
     "education": 0.0-1.0
   }}

8. **experience_requirements**: 
   {{
     "minimum_years": <number>,
     "preferred_years": <number>,
     "importance": "critical|high|moderate|low",
     "type": "years driving|years teaching|years programming|years managing|etc."
   }}

9. **location_requirements**:
   {{
     "importance": "critical|high|moderate|low|not_important",
     "can_be_remote": true/false,
     "must_be_local": true/false,
     "travel_required": true/false
   }}

10. **education_requirements**:
    {{
      "minimum_level": "none|high_school|certification|associates|bachelors|masters|phd|professional_degree",
      "preferred_fields": ["specific majors or fields"],
      "strict_requirement": true/false,
      "alternatives_accepted": true/false
    }}

11. **key_evaluation_criteria**: Top 5-7 most important things to look for:
    Example for Bus Driver: ["Valid CDL", "5+ years driving experience", "Clean driving record", "Customer service skills", "Knowledge of local routes", "Safety-first mindset"]

12. **industry_keywords**: Words/phrases that indicate domain expertise:
    Example for Healthcare: ["patient care", "HIPAA", "EMR", "clinical"]
    Example for Transportation: ["DOT regulations", "vehicle inspection", "route management"]

13. **experience_indicators**: Phrases in resumes that show relevant experience:
    Example for Bus Driver: ["drove bus", "operated commercial vehicle", "transported passengers", "maintained safety record"]
    Example for Chef: ["prepared dishes", "managed kitchen", "created menu", "supervised cooks"]

14. **disqualifying_factors**: What would disqualify a candidate?
    Example: ["DUI conviction (for driver)", "No medical license (for doctor)", "Less than required experience"]

15. **bonus_qualifications**: Nice-to-have extras:
    Example: ["Bilingual", "First Aid Certified", "Customer service training", "Additional endorsements"]

16. **physical_requirements**: If this job has physical demands, list them:
    Example: ["Ability to lift 50 lbs", "Standing for 8 hours", "Good vision", "Physical stamina"]

Return ONLY valid JSON. No markdown, no explanations."""

            response = openai.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a world-class HR expert and job analyst with comprehensive knowledge of:
- ALL industries worldwide (tech, healthcare, transportation, hospitality, construction, education, manufacturing, agriculture, arts, sports, government, non-profit, etc.)
- ALL job types (entry-level to executive, blue-collar to white-collar)
- ALL countries and regions (understand cultural and regional job differences)
- Global certification and licensing requirements
- Skills taxonomies across all fields

You analyze job postings and extract complete, actionable hiring criteria.
You NEVER see candidate data - only job requirements."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Validate and normalize weights
            weights = analysis.get('scoring_weights', {})
            total = sum(weights.values())
            if total > 0:
                analysis['scoring_weights'] = {k: v/total for k, v in weights.items()}
            else:
                # Fallback weights
                analysis['scoring_weights'] = {
                    'skills': 0.35,
                    'experience': 0.30,
                    'location': 0.15,
                    'certifications': 0.10,
                    'education': 0.10
                }
            
            # Print analysis summary
            print(f"\n✅ AI Analysis Complete:")
            print(f"   📂 Category: {analysis.get('job_category', 'Unknown')}")
            print(f"   🎯 Role: {analysis.get('job_subcategory', 'Unknown')}")
            print(f"   🌍 Region: {analysis.get('country_region', 'Global')}")
            print(f"   💡 Skills Identified: {len(analysis.get('all_required_skills', []))}")
            print(f"   📜 Certifications: {len(analysis.get('required_certifications', []))}")
            print(f"   ⚖️  Weights: Skills={weights.get('skills', 0):.0%}, Exp={weights.get('experience', 0):.0%}, Loc={weights.get('location', 0):.0%}")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}")
            print(f"   Falling back to basic mode...")
            return self._basic_fallback(job_title, provided_skills or [])
    
    def _basic_fallback(self, job_title: str, provided_skills: List[str]) -> Dict[str, Any]:
        """Minimal fallback when LLM is unavailable"""
        return {
            "job_category": "General",
            "job_subcategory": job_title,
            "country_region": "Global",
            "all_required_skills": provided_skills,
            "skill_variations_map": {skill: [skill.lower()] for skill in provided_skills},
            "required_certifications": [],
            "scoring_weights": {
                "skills": 0.35,
                "experience": 0.30,
                "location": 0.15,
                "certifications": 0.10,
                "education": 0.10
            },
            "experience_requirements": {
                "minimum_years": 0,
                "preferred_years": 2,
                "importance": "moderate",
                "type": "general work experience"
            },
            "location_requirements": {
                "importance": "moderate",
                "can_be_remote": False,
                "must_be_local": False,
                "travel_required": False
            },
            "education_requirements": {
                "minimum_level": "high_school",
                "preferred_fields": [],
                "strict_requirement": False,
                "alternatives_accepted": True
            },
            "key_evaluation_criteria": ["Relevant skills", "Work experience"],
            "industry_keywords": [],
            "experience_indicators": [],
            "disqualifying_factors": [],
            "bonus_qualifications": [],
            "physical_requirements": []
        }


class ZeroHardcodingSkillMatcher:
    """
    🔒 100% LOCAL skill matching using LLM-generated variations
    ✅ Privacy-Safe: NO candidate data sent to external services
    🌍 Universal: Works for ANY skill from ANY industry
    """
    
    def __init__(self, skill_variations_map: Dict[str, List[str]]):
        """
        skill_variations_map: Generated by LLM from job analysis
        Example: {"CDL": ["cdl", "commercial driver license", "class b license"], ...}
        """
        self.skill_variations_map = skill_variations_map
    
    def match_skill_in_resume(self, resume_text: str, skill: str) -> Tuple[bool, List[str]]:
        """
        Match a skill in resume using LLM-generated variations
        100% LOCAL processing - no API calls
        """
        resume_lower = resume_text.lower()
        
        # Get variations for this skill (from LLM job analysis)
        variations = self.skill_variations_map.get(skill, [skill.lower()])
        
        matched_variations = []
        for variation in variations:
            if variation.lower() in resume_lower:
                matched_variations.append(variation)
        
        if matched_variations:
            return True, matched_variations
        
        # Fuzzy matching as backup
        if ' ' in skill and len(skill.split()) <= 4:
            words = skill.split()
            if all(word.lower() in resume_lower for word in words):
                return True, [skill.lower()]
        
        return False, []
    
    def calculate_skill_match_score(self, resume_text: str, 
                                   required_skills: List[str]) -> Tuple[float, List[str], Dict]:
        """Calculate skill matching score - 100% LOCAL"""
        matched_skills = []
        detailed_matches = {}
        
        for skill in required_skills:
            is_matched, variations = self.match_skill_in_resume(resume_text, skill)
            if is_matched:
                matched_skills.append(skill)
                detailed_matches[skill] = variations
        
        score = len(matched_skills) / len(required_skills) if required_skills else 0
        return score, matched_skills, detailed_matches


class UniversalResumeFilter:
    """
    🌍 TRULY UNIVERSAL Resume Filter - ZERO Hardcoding
    
    ✅ Works for: Bus Driver, Chef, Doctor, Teacher, Engineer, Astronaut, etc.
    ✅ Uses LLM: ONLY for job analysis (not candidate data)
    ✅ Privacy: 100% local candidate processing
    ✅ Global: Any job, any industry, any country
    """
    
    def __init__(self):
        self.llm_analyzer = LLMJobAnalyzer()
        self.job_analysis = None
        self.skill_matcher = None
        self.pd_scorer = None  # Will be initialized later
    
    def initialize_for_job(self, job_ticket):
        """
        Analyze job with LLM - NO candidate data involved
        This runs ONCE per job, not per candidate
        """
        print(f"\n{'='*70}")
        print(f"🤖 AI-Powered Job Analysis")
        print(f"{'='*70}")
        print(f"Position: {job_ticket.position}")
        print(f"Analyzing with LLM to support ANY job type worldwide...")
        
        # LLM analyzes ONLY the job (never sees candidates)
        self.job_analysis = self.llm_analyzer.analyze_any_job_worldwide(
            job_title=job_ticket.position,
            job_description=job_ticket.description,
            provided_skills=job_ticket.tech_stack
        )
        
        # Initialize LOCAL skill matcher with LLM-generated variations
        skill_variations = self.job_analysis.get('skill_variations_map', {})
        self.skill_matcher = ZeroHardcodingSkillMatcher(skill_variations)
        
        # Initialize professional development scorer
        if self.pd_scorer is None:
            self.pd_scorer = ProfessionalDevelopmentScorer()
        
        print(f"\n✅ Job Analysis Complete - Ready for LOCAL candidate screening")
        print(f"   All candidate data will be processed 100% locally")
        print(f"   No candidate resumes will be sent to any external service")
        print(f"{'='*70}\n")
    
    def parse_experience_range(self, experience_str: str) -> Tuple[int, int]:
        """Parse experience requirement"""
        numbers = re.findall(r'\d+', experience_str)
        
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            if '+' in experience_str:
                return int(numbers[0]), int(numbers[0]) + 5
            else:
                return int(numbers[0]), int(numbers[0])
        else:
            # Use LLM-analyzed requirements
            min_years = self.job_analysis.get('experience_requirements', {}).get('minimum_years', 0)
            return min_years, min_years + 5
    
    def calculate_experience_match(self, resume_text: str, required_experience: str) -> Tuple[float, int]:
        """100% LOCAL experience calculation"""
        min_req, max_req = self.parse_experience_range(required_experience)
        
        # Get experience indicators from LLM analysis
        experience_indicators = self.job_analysis.get('experience_indicators', [])
        
        # Standard patterns
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?(?:experience|exp)',
            r'experience\s*[:–-]\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?',
            r'(\d{4})\s*[-–]\s*(?:present|current|now|(\d{4}))',
        ]
        
        # Add job-specific patterns from LLM
        exp_type = self.job_analysis.get('experience_requirements', {}).get('type', '')
        if exp_type:
            patterns.append(rf'(\d+)\+?\s*years?\s*{re.escape(exp_type)}')
        
        years_found = []
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text.lower())
            for match in matches:
                if isinstance(match, tuple) and match:
                    if match[0].isdigit():
                        if len(match[0]) == 4:  # Year
                            start_year = int(match[0])
                            if 1970 < start_year <= datetime.now().year:
                                end_year = int(match[1]) if len(match) > 1 and match[1] and match[1].isdigit() else datetime.now().year
                                years_found.append(end_year - start_year)
                        else:
                            years_found.append(int(match[0]))
                elif match and match.isdigit():
                    years_found.append(int(match))
        
        if years_found:
            candidate_years = max([y for y in years_found if 0 < y < 60])
            
            if min_req <= candidate_years <= max_req:
                return 1.0, candidate_years
            elif candidate_years > max_req:
                return 0.9, candidate_years
            elif candidate_years >= min_req - 1:
                return 0.8, candidate_years
            else:
                return candidate_years / min_req if min_req > 0 else 0, candidate_years
        
        return 0.0, 0
    
    def score_certifications(self, resume_text: str) -> Tuple[float, List[str]]:
        """Score certifications/licenses - 100% LOCAL"""
        required_certs = self.job_analysis.get('required_certifications', [])
        
        if not required_certs:
            return 0.5, []  # Neutral if no certs required
        
        resume_lower = resume_text.lower()
        matched_certs = []
        
        for cert in required_certs:
            # Check main cert name
            if cert.lower() in resume_lower:
                matched_certs.append(cert)
                continue
            
            # Check variations (extract from parentheses/abbreviations)
            cert_variations = [cert.lower()]
            
            # Extract abbreviations from cert name
            if '(' in cert and ')' in cert:
                abbrev = cert[cert.index('(')+1:cert.index(')')].lower()
                cert_variations.append(abbrev)
            
            # Check variations
            if any(var in resume_lower for var in cert_variations):
                matched_certs.append(cert)
        
        score = len(matched_certs) / len(required_certs)
        return score, matched_certs
    
    def _score_education(self, resume_text: str) -> float:
        """Score education based on LLM-analyzed requirements"""
        edu_reqs = self.job_analysis.get('education_requirements', {})
        required_level = edu_reqs.get('minimum_level', 'high_school')
        
        education_levels = {
            'none': 0,
            'high_school': 1,
            'certification': 1.5,
            'associates': 2,
            'bachelors': 3,
            'masters': 4,
            'phd': 5,
            'professional_degree': 5
        }
        
        resume_lower = resume_text.lower()
        
        # Detect education level in resume
        detected_level = 0
        detection_keywords = {
            'phd': 5, 'ph.d': 5, 'doctorate': 5,
            'md': 5, 'jd': 5, 'dds': 5,
            'masters': 4, 'master': 4, 'mba': 4, 'ms': 4, 'ma': 4,
            'bachelors': 3, 'bachelor': 3, 'bs': 3, 'ba': 3, 'btech': 3,
            'associates': 2, 'associate degree': 2,
            'certification': 1.5, 'certified': 1.5,
            'high school': 1, 'diploma': 1
        }
        
        for keyword, level in detection_keywords.items():
            if keyword in resume_lower:
                detected_level = max(detected_level, level)
        
        required_score = education_levels.get(required_level, 1)
        
        if edu_reqs.get('strict_requirement', False):
            # Strict: must meet or exceed
            if detected_level >= required_score:
                return 1.0
            else:
                return detected_level / required_score if required_score > 0 else 0.5
        else:
            # Flexible: close is good enough
            if detected_level >= required_score:
                return 1.0
            elif detected_level >= required_score - 1:
                return 0.8
            else:
                return max(detected_level / required_score if required_score > 0 else 0.5, 0.3)
    
    def score_resume(self, resume_text: str, job_ticket) -> Dict[str, Any]:
        """
        🔒 100% LOCAL resume scoring
        This function processes candidate data ENTIRELY on your server
        NO external API calls - complete privacy
        """
        
        # Get all required skills from LLM analysis
        all_skills = self.job_analysis.get('all_required_skills', job_ticket.tech_stack)
        
        # Skills matching (100% local)
        skill_score, matched_skills, detailed_matches = self.skill_matcher.calculate_skill_match_score(
            resume_text, all_skills
        )
        
        # Experience matching (100% local)
        exp_score, detected_years = self.calculate_experience_match(
            resume_text, job_ticket.experience_required
        )
        
        # Location matching (100% local)
        location_score = 0.0
        location_importance = self.job_analysis.get('location_requirements', {}).get('importance', 'moderate')
        
        if job_ticket.location.lower() in resume_text.lower():
            location_score = 1.0
        elif "remote" in job_ticket.location.lower() or "remote" in resume_text.lower():
            location_score = 0.8
        elif location_importance == 'not_important':
            location_score = 1.0  # Don't penalize if location doesn't matter
        
        # Certification matching (100% local)
        cert_score, matched_certs = self.score_certifications(resume_text)
        
        # Education matching (100% local)
        education_score = self._score_education(resume_text)
        
        # Professional development (100% local)
        pd_results = self.pd_scorer.calculate_professional_development_score(resume_text)
        
        # Get LLM-optimized weights (from job analysis, NOT candidate data)
        weights = self.job_analysis.get('scoring_weights', {
            'skills': 0.35,
            'experience': 0.30,
            'location': 0.15,
            'certifications': 0.10,
            'education': 0.10
        })
        
        # Calculate final score
        final_score = (
            weights.get('skills', 0.35) * skill_score +
            weights.get('experience', 0.30) * exp_score +
            weights.get('location', 0.15) * location_score +
            weights.get('certifications', 0.10) * cert_score +
            weights.get('education', 0.10) * education_score
        )
        
        # Bonus for professional development
        if pd_results['professional_development_score'] > 0.7:
            final_score = min(final_score * 1.05, 1.0)
        
        return {
            'final_score': final_score,
            'skill_score': skill_score,
            'experience_score': exp_score,
            'location_score': location_score,
            'certification_score': cert_score,
            'education_score': education_score,
            'professional_development_score': pd_results['professional_development_score'],
            'matched_skills': matched_skills,
            'matched_certifications': matched_certs,
            'detailed_skill_matches': detailed_matches,
            'detected_experience_years': detected_years,
            'professional_development': pd_results,
            'scoring_weights': weights,
            'job_category': self.job_analysis.get('job_category', 'Unknown'),
            'job_subcategory': self.job_analysis.get('job_subcategory', 'Unknown'),
            'privacy_mode': 'ENABLED - All candidate data processed locally',
            'job_requirements': {
                'position': job_ticket.position,
                'required_skills': all_skills,
                'required_certifications': self.job_analysis.get('required_certifications', []),
                'required_experience': job_ticket.experience_required,
                'location': job_ticket.location
            }
        }


class ProfessionalDevelopmentScorer:
    """Score candidates based on continuous learning and professional development"""
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        
        self.certifications_db = {
            'cloud': {
                'aws': {
                    'patterns': [
                        'aws certified solutions architect', 'aws certified developer',
                        'aws certified sysops', 'aws certified devops', 'aws certified security',
                        'aws certified database', 'aws certified machine learning',
                        'aws certified data analytics', 'aws solutions architect',
                        'amazon web services certified', 'aws certification'
                    ],
                    'weight': 1.0,
                    'recency_important': True
                },
                'azure': {
                    'patterns': [
                        'azure certified', 'azure fundamentals', 'azure administrator',
                        'azure developer', 'azure solutions architect', 'azure devops',
                        'azure data engineer', 'azure ai engineer', 'microsoft certified azure',
                        'az-900', 'az-104', 'az-204', 'az-303', 'az-304', 'az-400'
                    ],
                    'weight': 1.0,
                    'recency_important': True
                },
                'gcp': {
                    'patterns': [
                        'google cloud certified', 'gcp certified', 'google cloud professional',
                        'cloud architect google', 'cloud engineer google', 'data engineer google',
                        'google cloud developer', 'google cloud network engineer'
                    ],
                    'weight': 1.0,
                    'recency_important': True
                }
            },
            'data': {
                'general': {
                    'patterns': [
                        'databricks certified', 'cloudera certified', 'hortonworks certified',
                        'mongodb certified', 'cassandra certified', 'elastic certified',
                        'confluent certified', 'snowflake certified', 'tableau certified',
                        'power bi certified', 'qlik certified'
                    ],
                    'weight': 0.9,
                    'recency_important': True
                }
            },
            'programming': {
                'general': {
                    'patterns': [
                        'oracle certified java', 'microsoft certified c#', 'python institute certified',
                        'javascript certified', 'golang certified', 'rust certified',
                        'scala certified', 'kotlin certified'
                    ],
                    'weight': 0.8,
                    'recency_important': True
                }
            },
            'devops': {
                'general': {
                    'patterns': [
                        'docker certified', 'kubernetes certified', 'cka', 'ckad', 'cks',
                        'jenkins certified', 'ansible certified', 'terraform certified',
                        'gitlab certified', 'github actions certified'
                    ],
                    'weight': 0.9,
                    'recency_important': True
                }
            },
            'security': {
                'general': {
                    'patterns': [
                        'cissp', 'ceh', 'certified ethical hacker', 'comptia security+',
                        'comptia pentest+', 'gsec', 'gcih', 'oscp', 'security certified'
                    ],
                    'weight': 0.85,
                    'recency_important': True
                }
            },
            'agile': {
                'general': {
                    'patterns': [
                        'certified scrum master', 'csm', 'psm', 'safe certified',
                        'pmp', 'prince2', 'agile certified', 'kanban certified',
                        'product owner certified', 'cspo'
                    ],
                    'weight': 0.7,
                    'recency_important': False
                }
            },
            'ai_ml': {
                'general': {
                    'patterns': [
                        'tensorflow certified', 'pytorch certified', 'deep learning certified',
                        'machine learning certified', 'ai certified', 'coursera deep learning',
                        'fast.ai certified', 'nvidia certified'
                    ],
                    'weight': 0.95,
                    'recency_important': True
                }
            }
        }
        
        self.learning_platforms = {
            'premium': {
                'patterns': ['coursera', 'udacity', 'edx', 'pluralsight', 'linkedin learning', 
                           'datacamp', 'udemy business', 'o\'reilly', 'safari books'],
                'weight': 0.8
            },
            'standard': {
                'patterns': ['udemy', 'skillshare', 'khan academy', 'codecademy', 
                           'freecodecamp', 'w3schools'],
                'weight': 0.6
            },
            'specialized': {
                'patterns': ['fast.ai', 'deeplearning.ai', 'kaggle learn', 'qwiklabs',
                           'linux academy', 'cloud academy', 'acloud.guru'],
                'weight': 0.9
            }
        }
        
        self.conference_patterns = {
            'speaking': {
                'patterns': [
                    'speaker at', 'presented at', 'talk at', 'keynote', 'panelist',
                    'conference speaker', 'tech talk', 'lightning talk', 'workshop facilitator'
                ],
                'weight': 1.0
            },
            'attendance': {
                'patterns': [
                    'attended', 'participant', 'conference attendee', 'summit participant',
                    'bootcamp', 'workshop attended', 'training attended'
                ],
                'weight': 0.5
            },
            'major_conferences': {
                'patterns': [
                    're:invent', 'google i/o', 'microsoft build', 'kubecon', 'pycon',
                    'jsconf', 'defcon', 'black hat', 'rsa conference', 'strata',
                    'spark summit', 'kafka summit', 'dockercon', 'hashiconf'
                ],
                'weight': 0.8
            }
        }
        
        self.content_creation = {
            'blog': {
                'patterns': [
                    'blog', 'medium.com', 'dev.to', 'hashnode', 'technical blog',
                    'tech blogger', 'write about', 'published articles', 'technical writing'
                ],
                'weight': 0.8
            },
            'video': {
                'patterns': [
                    'youtube channel', 'video tutorials', 'screencast', 'tech videos',
                    'online instructor', 'course creator'
                ],
                'weight': 0.9
            },
            'open_source': {
                'patterns': [
                    'github.com', 'gitlab.com', 'bitbucket', 'open source contributor',
                    'maintainer', 'pull requests', 'github stars', 'npm package',
                    'pypi package', 'maven package'
                ],
                'weight': 1.0
            },
            'community': {
                'patterns': [
                    'stack overflow', 'stackoverflow reputation', 'forum moderator',
                    'discord community', 'slack community', 'reddit moderator',
                    'community leader', 'meetup organizer'
                ],
                'weight': 0.7
            }
        }
    
    def extract_years_from_text(self, text: str, keyword: str, look_ahead: int = 50) -> List[int]:
        """Extract years mentioned near a keyword"""
        years_found = []
        keyword_indices = [m.start() for m in re.finditer(keyword, text.lower())]
        
        for idx in keyword_indices:
            start = max(0, idx - 30)
            end = min(len(text), idx + len(keyword) + look_ahead)
            snippet = text[start:end]
            
            year_pattern = r'\b(20[1-2][0-9])\b'
            years = re.findall(year_pattern, snippet)
            years_found.extend([int(y) for y in years if 2010 <= int(y) <= self.current_year + 1])
        
        return years_found
    
    def calculate_recency_score(self, years: List[int]) -> float:
        """Calculate how recent the certifications/courses are"""
        if not years:
            return 0.5
        
        most_recent = max(years)
        years_ago = self.current_year - most_recent
        
        if years_ago == 0:
            return 1.0
        elif years_ago == 1:
            return 0.9
        elif years_ago == 2:
            return 0.8
        elif years_ago == 3:
            return 0.6
        elif years_ago <= 5:
            return 0.4
        else:
            return 0.2
    
    def score_certifications(self, resume_text: str) -> Dict[str, Any]:
        """Score professional certifications"""
        resume_lower = resume_text.lower()
        
        results = {
            'certification_score': 0.0,
            'certification_count': 0,
            'recent_certification_score': 0.0,
            'certifications_found': [],
            'certification_categories': {},
            'years_detected': []
        }
        
        found_certs = set()
        category_scores = {}
        all_years = []
        
        for category, cert_types in self.certifications_db.items():
            category_scores[category] = 0.0
            category_certs = []
            
            for cert_type, cert_info in cert_types.items():
                for pattern in cert_info['patterns']:
                    if pattern in resume_lower and pattern not in found_certs:
                        found_certs.add(pattern)
                        results['certification_count'] += 1
                        category_certs.append(pattern)
                        
                        years = self.extract_years_from_text(resume_text, pattern)
                        all_years.extend(years)
                        
                        category_scores[category] += cert_info['weight']
            
            if category_certs:
                results['certification_categories'][category] = category_certs
        
        if results['certification_count'] > 0:
            base_score = min(results['certification_count'] * 0.15, 0.6)
            
            category_diversity = len(results['certification_categories']) / len(self.certifications_db)
            diversity_bonus = category_diversity * 0.2
            
            high_value_bonus = 0.0
            if any(cat in results['certification_categories'] for cat in ['cloud', 'ai_ml', 'data']):
                high_value_bonus = 0.2
            
            results['certification_score'] = min(base_score + diversity_bonus + high_value_bonus, 1.0)
        
        if all_years:
            results['years_detected'] = sorted(list(set(all_years)), reverse=True)
            results['recent_certification_score'] = self.calculate_recency_score(all_years)
        
        results['certifications_found'] = list(found_certs)
        
        return results
    
    def score_online_learning(self, resume_text: str) -> Dict[str, Any]:
        """Score online course completions"""
        resume_lower = resume_text.lower()
        
        results = {
            'online_learning_score': 0.0,
            'platforms_found': [],
            'course_count_estimate': 0,
            'recent_learning_score': 0.0,
            'specializations_mentioned': False
        }
        
        platforms_detected = set()
        platform_weights = []
        
        for tier, platform_info in self.learning_platforms.items():
            for platform in platform_info['patterns']:
                if platform in resume_lower:
                    platforms_detected.add(platform)
                    platform_weights.append(platform_info['weight'])
        
        results['platforms_found'] = list(platforms_detected)
        
        course_indicators = [
            r'completed?\s+\d+\s+courses?',
            r'\d+\s+courses?\s+completed',
            r'certification?\s+in',
            r'specialization\s+in',
            r'nanodegree',
            r'micromasters',
            r'professional certificate'
        ]
        
        course_count = 0
        for pattern in course_indicators:
            matches = re.findall(pattern, resume_lower)
            course_count += len(matches)
        
        if any(term in resume_lower for term in ['specialization', 'nanodegree', 'micromasters']):
            results['specializations_mentioned'] = True
            course_count += 2
        
        results['course_count_estimate'] = course_count
        
        if platforms_detected:
            platform_score = sum(platform_weights) / len(platform_weights) if platform_weights else 0
            course_bonus = min(course_count * 0.1, 0.3)
            spec_bonus = 0.2 if results['specializations_mentioned'] else 0
            
            results['online_learning_score'] = min(platform_score * 0.5 + course_bonus + spec_bonus, 1.0)
        
        recent_years = []
        for platform in platforms_detected:
            years = self.extract_years_from_text(resume_text, platform)
            recent_years.extend(years)
        
        if recent_years:
            results['recent_learning_score'] = self.calculate_recency_score(recent_years)
        
        return results
    
    def score_conference_participation(self, resume_text: str) -> Dict[str, Any]:
        """Score conference attendance and speaking"""
        resume_lower = resume_text.lower()
        
        results = {
            'conference_score': 0.0,
            'speaking_score': 0.0,
            'attendance_score': 0.0,
            'events_found': [],
            'speaker_events': [],
            'major_conferences': []
        }
        
        for pattern in self.conference_patterns['speaking']['patterns']:
            if pattern in resume_lower:
                results['speaker_events'].append(pattern)
                event_matches = re.findall(f'{pattern}[^.]*(?:conference|summit|meetup|workshop)', resume_lower)
                results['events_found'].extend(event_matches)
        
        for pattern in self.conference_patterns['attendance']['patterns']:
            if pattern in resume_lower:
                results['events_found'].append(pattern)
        
        for conference in self.conference_patterns['major_conferences']['patterns']:
            if conference in resume_lower:
                results['major_conferences'].append(conference)
        
        if results['speaker_events']:
            results['speaking_score'] = min(len(results['speaker_events']) * 0.3, 1.0)
        
        if results['events_found'] or results['major_conferences']:
            attendance_count = len(results['events_found']) + len(results['major_conferences'])
            results['attendance_score'] = min(attendance_count * 0.15, 0.6)
        
        results['conference_score'] = min(
            results['speaking_score'] * 0.7 + results['attendance_score'] * 0.3,
            1.0
        )
        
        return results
    
    def score_content_creation(self, resume_text: str) -> Dict[str, Any]:
        """Score technical content creation and community involvement"""
        resume_lower = resume_text.lower()
        
        results = {
            'content_creation_score': 0.0,
            'blog_writing': False,
            'video_content': False,
            'open_source': False,
            'community_involvement': False,
            'content_platforms': [],
            'github_activity': None
        }
        
        content_scores = []
        
        for content_type, content_info in self.content_creation.items():
            for pattern in content_info['patterns']:
                if pattern in resume_lower:
                    results[f'{content_type}_activity'] = True
                    results['content_platforms'].append(pattern)
                    content_scores.append(content_info['weight'])
                    
                    if 'github' in pattern:
                        stats_patterns = [
                            r'(\d+)\+?\s*stars',
                            r'(\d+)\+?\s*followers',
                            r'(\d+)\+?\s*repositories',
                            r'(\d+)\+?\s*contributions'
                        ]
                        github_stats = {}
                        for stat_pattern in stats_patterns:
                            match = re.search(stat_pattern, resume_lower)
                            if match:
                                github_stats[stat_pattern] = int(match.group(1))
                        if github_stats:
                            results['github_activity'] = github_stats
        
        if content_scores:
            base_score = sum(content_scores) / len(content_scores)
            variety_bonus = min(len(content_scores) * 0.1, 0.3)
            results['content_creation_score'] = min(base_score + variety_bonus, 1.0)
        
        return results
    
    def calculate_professional_development_score(self, resume_text: str) -> Dict[str, Any]:
        """Calculate comprehensive professional development score"""
        
        cert_results = self.score_certifications(resume_text)
        learning_results = self.score_online_learning(resume_text)
        conference_results = self.score_conference_participation(resume_text)
        content_results = self.score_content_creation(resume_text)
        
        weights = {
            'certifications': 0.35,
            'online_learning': 0.25,
            'conferences': 0.20,
            'content_creation': 0.20
        }
        
        weighted_score = (
            weights['certifications'] * cert_results['certification_score'] +
            weights['online_learning'] * learning_results['online_learning_score'] +
            weights['conferences'] * conference_results['conference_score'] +
            weights['content_creation'] * content_results['content_creation_score']
        )
        
        recency_scores = [
            cert_results.get('recent_certification_score', 0),
            learning_results.get('recent_learning_score', 0)
        ]
        recency_bonus = max(recency_scores) * 0.1 if recency_scores else 0
        
        final_score = min(weighted_score + recency_bonus, 1.0)
        
        pd_level = self._determine_pd_level(final_score, cert_results, learning_results, 
                                           conference_results, content_results)
        
        return {
            'professional_development_score': final_score,
            'professional_development_level': pd_level,
            'component_scores': {
                'certifications': cert_results,
                'online_learning': learning_results,
                'conferences': conference_results,
                'content_creation': content_results
            },
            'weights_used': weights,
            'summary': self._generate_pd_summary(cert_results, learning_results, 
                                                conference_results, content_results)
        }
    
    def _determine_pd_level(self, score: float, cert_results: Dict, learning_results: Dict,
                           conference_results: Dict, content_results: Dict) -> str:
        """Determine professional development level"""
        
        if score >= 0.8:
            return "Exceptional - Continuous learner with strong industry presence"
        elif score >= 0.6:
            return "Strong - Active in professional development"
        elif score >= 0.4:
            return "Moderate - Some professional development activities"
        elif score >= 0.2:
            return "Basic - Limited professional development shown"
        else:
            return "Minimal - Little evidence of continuous learning"
    
    def _generate_pd_summary(self, cert_results: Dict, learning_results: Dict,
                            conference_results: Dict, content_results: Dict) -> Dict[str, Any]:
        """Generate summary of professional development findings"""
        
        summary = {
            'total_certifications': cert_results['certification_count'],
            'certification_categories': list(cert_results['certification_categories'].keys()),
            'recent_certifications': cert_results['recent_certification_score'] > 0.7,
            'learning_platforms_used': len(learning_results['platforms_found']),
            'estimated_courses_completed': learning_results['course_count_estimate'],
            'conference_speaker': len(conference_results['speaker_events']) > 0,
            'conferences_attended': len(conference_results['events_found']),
            'content_creator': content_results['content_creation_score'] > 0.5,
            'content_types': [k.replace('_activity', '') for k, v in content_results.items() 
                            if k.endswith('_activity') and v],
            'continuous_learner': (
                cert_results['recent_certification_score'] > 0.7 or 
                learning_results['recent_learning_score'] > 0.7
            )
        }
        
        highlights = []
        if summary['total_certifications'] >= 3:
            highlights.append(f"Has {summary['total_certifications']} professional certifications")
        if summary['conference_speaker']:
            highlights.append("Conference speaker")
        if summary['content_creator']:
            highlights.append("Active content creator")
        if summary['continuous_learner']:
            highlights.append("Recent learning activities (within 2 years)")
        if 'cloud' in summary['certification_categories']:
            highlights.append("Cloud certified professional")
        
        summary['key_highlights'] = highlights
        
        return summary


class UpdateAwareResumeFilter:
    """Legacy resume filter - kept for backward compatibility"""
    
    def __init__(self):
        self.skill_variations = self._build_skill_variations()
        self.pd_scorer = ProfessionalDevelopmentScorer()
        print("⚠️  Using legacy filter mode (limited to predefined skills)")
        print("   For universal support of ANY job type, LLM mode is recommended")
    
    def _build_skill_variations(self) -> Dict[str, List[str]]:
        """Build comprehensive skill variations dictionary"""
        return {
            "python": ["python", "py", "python3", "python2", "python 3", "python 2"],
            "javascript": ["javascript", "js", "node.js", "nodejs", "node", "ecmascript", "es6", "es5"],
            "java": ["java", "jvm", "j2ee", "java8", "java11", "java17"],
            "c++": ["c++", "cpp", "cplusplus", "c plus plus"],
            "c#": ["c#", "csharp", "c sharp", ".net", "dotnet"],
            "html": ["html", "html5", "html 5"],
            "css": ["css", "css3", "css 3", "styles", "styling"],
            "html/css": ["html/css", "html css", "html, css", "html and css", "html & css"],
            "sql": ["sql", "structured query language", "tsql", "t-sql", "plsql", "pl/sql"],
            "mongodb": ["mongodb", "mongo", "mongod", "nosql mongodb"],
            "redis": ["redis", "redis cache", "redis db", "redis database"],
            "postgresql": ["postgresql", "postgres", "pgsql", "postgre"],
            "mysql": ["mysql", "my sql", "mariadb"],
            "react": ["react", "reactjs", "react.js", "react js", "react native"],
            "angular": ["angular", "angularjs", "angular.js", "angular js"],
            "django": ["django", "django rest", "drf", "django framework"],
            "spring": ["spring", "spring boot", "springboot", "spring framework"],
            "flask": ["flask", "flask api", "flask framework"],
            "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "amazon aws"],
            "gcp": ["gcp", "google cloud", "google cloud platform", "gcloud"],
            "azure": ["azure", "microsoft azure", "ms azure", "windows azure"],
            "cloud platforms": ["cloud platforms", "cloud services", "cloud computing", "cloud infrastructure"],
            "spark": ["spark", "apache spark", "pyspark", "spark sql"],
            "hadoop": ["hadoop", "hdfs", "mapreduce", "apache hadoop"],
            "kafka": ["kafka", "apache kafka", "kafka streams"],
            "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn", "ml models"],
            "deep learning": ["deep learning", "dl", "neural networks", "nn", "dnn"],
            "tensorflow": ["tensorflow", "tf", "tf2", "tensorflow 2"],
            "pytorch": ["pytorch", "torch", "py torch"],
            "docker": ["docker", "containers", "containerization", "dockerfile"],
            "kubernetes": ["kubernetes", "k8s", "kubectl", "k8", "container orchestration"],
            "graphql": ["graphql", "graph ql", "apollo", "graphql api"],
            "rest": ["rest", "restful", "rest api", "restful api", "rest services"],
            "rest apis": ["rest apis", "restful apis", "rest api", "restful api", "api development"],
            "git": ["git", "github", "gitlab", "bitbucket", "version control", "vcs"],
            "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment", "jenkins", "travis", "circle ci"],
            "agile": ["agile", "scrum", "kanban", "sprint", "agile methodology"],
            "etl": ["etl", "elt", "extract transform load", "data pipeline", "data pipelines"],
            "data warehouse": ["data warehouse", "data warehousing", "dwh", "datawarehouse"],
            "apache spark": ["apache spark", "spark", "pyspark", "spark sql", "spark streaming"],
            "sql/nosql databases": ["sql/nosql", "sql nosql", "sql and nosql", "relational and non-relational", 
                                   "sql", "nosql", "mysql", "postgresql", "mongodb", "cassandra", "redis",
                                   "database", "databases", "rdbms", "nosql databases"],
        }
    
    def calculate_skill_match_score(self, resume_text: str, required_skills: List[str]) -> tuple[float, List[str], Dict[str, List[str]]]:
        """Calculate skill matching score with variations"""
        resume_lower = resume_text.lower()
        matched_skills = []
        detailed_matches = {}
        
        for skill in required_skills:
            skill_lower = skill.lower().strip()
            skill_matched = False
            
            if skill_lower in resume_lower:
                matched_skills.append(skill)
                detailed_matches[skill] = [skill_lower]
                skill_matched = True
                continue
            
            skill_key = None
            for key in self.skill_variations:
                if skill_lower in self.skill_variations[key] or key in skill_lower:
                    skill_key = key
                    break
            
            if skill_key and skill_key in self.skill_variations:
                variations_found = []
                for variation in self.skill_variations[skill_key]:
                    if variation in resume_lower:
                        variations_found.append(variation)
                        skill_matched = True
                
                if variations_found:
                    matched_skills.append(skill)
                    detailed_matches[skill] = variations_found
            
            if not skill_matched and ' ' in skill:
                parts = skill.split()
                if all(part.lower() in resume_lower for part in parts):
                    matched_skills.append(skill)
                    detailed_matches[skill] = [skill_lower]
        
        score = len(matched_skills) / len(required_skills) if required_skills else 0
        return score, matched_skills, detailed_matches
    
    def parse_experience_range(self, experience_str: str) -> tuple[int, int]:
        """Parse experience range like '5-8 years' to (5, 8)"""
        numbers = re.findall(r'\d+', experience_str)
        
        if len(numbers) >= 2:
            return int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            if '+' in experience_str:
                return int(numbers[0]), int(numbers[0]) + 5
            else:
                return int(numbers[0]), int(numbers[0])
        else:
            return 0, 100
    
    def calculate_experience_match(self, resume_text: str, required_experience: str) -> tuple[float, int]:
        """Calculate experience matching score"""
        min_req, max_req = self.parse_experience_range(required_experience)
        
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:professional\s*)?experience',
            r'experience\s*[:–-]\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|data|engineering|development)',
            r'total\s*experience\s*[:–-]\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s*exp',
            r'(\d{4})\s*[-–]\s*(?:present|current|now|(\d{4}))',
        ]
        
        date_patterns = [
            r'from\s+(?:january|february|march|april|may|june|july|august|september|october|november|december),?\s*(\d{4})\s*[-–]\s*(?:present|current|now)',
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december),?\s*(\d{4})\s*[-–]\s*(?:january|february|march|april|may|june|july|august|september|october|november|december),?\s*(\d{4})',
            r'(\d{4})\s*(?:to|-|–)\s*(\d{4})',
            r'since\s+(?:january|february|march|april|may|june|july|august|september|october|november|december),?\s*(\d{4})',
        ]
        
        month_year_patterns = [
            r'(?:january|february|march|april|may|june|july|august|september|october|november|december),?\s*(\d{4})\s*[-–]\s*(?:present|current|now)',
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*,?\s*(\d{4})\s*[-–]\s*(?:present|current|now)',
        ]
        
        years_found = []
        experience_periods = []
        
        education_keywords = ['education', 'academic', 'degree', 'bachelor', 'master', 'phd', 'university', 'college', 'school']
        
        for pattern in patterns:
            matches = re.findall(pattern, resume_text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    if match[0].isdigit() and len(match[0]) == 4:
                        start_year = int(match[0])
                        if match[1] and match[1].isdigit():
                            end_year = int(match[1])
                        else:
                            end_year = datetime.now().year
                        
                        match_context = resume_text.lower()[max(0, resume_text.lower().find(match[0])-100):resume_text.lower().find(match[0])+100]
                        if not any(edu_keyword in match_context for edu_keyword in education_keywords):
                            if 1990 < start_year <= datetime.now().year:
                                years_found.append(end_year - start_year)
                else:
                    if match.isdigit():
                        years_found.append(int(match))
        
        experience_keywords = ['experience', 'work', 'employed', 'position', 'role', 'job', 'company', 'engineer at', 'developer at']
        
        for pattern in month_year_patterns:
            for match in re.finditer(pattern, resume_text.lower()):
                match_text = match.group(1) if match.groups() else match.group(0)
                if match_text.isdigit():
                    start_year = int(match_text)
                    
                    match_context = resume_text.lower()[max(0, match.start()-200):match.end()+50]
                    if any(exp_keyword in match_context for exp_keyword in experience_keywords):
                        if 1990 < start_year <= datetime.now().year:
                            current_year = datetime.now().year
                            current_month = datetime.now().month
                            
                            month_str = resume_text.lower()[max(0, match.start()-20):match.start()].strip()
                            
                            month_map = {
                                'january': 1, 'february': 2, 'march': 3, 'april': 4,
                                'may': 5, 'june': 6, 'july': 7, 'august': 8,
                                'september': 9, 'october': 10, 'november': 11, 'december': 12
                            }
                            
                            start_month = 1
                            for month_name, month_num in month_map.items():
                                if month_name in month_str:
                                    start_month = month_num
                                    break
                            
                            if start_year == current_year:
                                years = (current_month - start_month) / 12.0
                            elif start_year == current_year - 1:
                                years = 1 + ((current_month - start_month) / 12.0)
                            else:
                                years = current_year - start_year + ((current_month - start_month) / 12.0)
                            
                            experience_periods.append(max(0.5, years))
        
        for pattern in date_patterns:
            matches = re.findall(pattern, resume_text.lower())
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) >= 1:
                        start_year = int(match[0])
                        if len(match) > 1 and match[1] and match[1].isdigit():
                            end_year = int(match[1])
                        else:
                            end_year = datetime.now().year
                        
                        match_context = resume_text.lower()[max(0, resume_text.lower().find(str(start_year))-100):resume_text.lower().find(str(start_year))+100]
                        if any(exp_keyword in match_context for exp_keyword in experience_keywords) and \
                           not any(edu_keyword in match_context for edu_keyword in education_keywords):
                            if 1990 < start_year <= datetime.now().year and end_year - start_year < 10:
                                experience_periods.append(end_year - start_year)
                elif match and match.isdigit():
                    start_year = int(match)
                    if 1990 < start_year <= datetime.now().year:
                        experience_periods.append(datetime.now().year - start_year)
        
        all_years = years_found + experience_periods
        
        if all_years:
            realistic_years = [y for y in all_years if 0 < y < 15]
            
            if realistic_years:
                candidate_years = max(realistic_years)
                if candidate_years < 1:
                    candidate_years = 1
                else:
                    candidate_years = int(round(candidate_years))
            else:
                candidate_years = int(round(max(all_years)))
            
            if min_req <= candidate_years <= max_req:
                return 1.0, candidate_years
            elif candidate_years > max_req:
                return 0.9, candidate_years
            elif candidate_years >= min_req - 1:
                return 0.8, candidate_years
            else:
                return candidate_years / min_req if min_req > 0 else 0, candidate_years
        
        return 0.0, 0
    
    def score_resume(self, resume_text: str, job_ticket: EnhancedJobTicket) -> Dict[str, Any]:
        """Enhanced score_resume method with professional development"""
        
        skill_score, matched_skills, detailed_matches = self.calculate_skill_match_score(
            resume_text, job_ticket.tech_stack
        )
        
        exp_score, detected_years = self.calculate_experience_match(
            resume_text, job_ticket.experience_required
        )
        
        location_score = 0.0
        if job_ticket.location.lower() in resume_text.lower():
            location_score = 1.0
        elif "remote" in job_ticket.location.lower() or "remote" in resume_text.lower():
            location_score = 0.8
        
        pd_results = self.pd_scorer.calculate_professional_development_score(resume_text)
        
        weights = {
            'skills': 0.40,
            'experience': 0.30,
            'location': 0.10,
            'professional_dev': 0.20
        }
        
        final_score = (
            weights['skills'] * skill_score +
            weights['experience'] * exp_score +
            weights['location'] * location_score +
            weights['professional_dev'] * pd_results['professional_development_score']
        )
        
        return {
            'final_score': final_score,
            'skill_score': skill_score,
            'experience_score': exp_score,
            'location_score': location_score,
            'professional_development_score': pd_results['professional_development_score'],
            'matched_skills': matched_skills,
            'detailed_skill_matches': detailed_matches,
            'detected_experience_years': detected_years,
            'professional_development': pd_results,
            'scoring_weights': weights,
            'job_requirements': {
                'position': job_ticket.position,
                'required_skills': job_ticket.tech_stack,
                'required_experience': job_ticket.experience_required,
                'location': job_ticket.location
            }
        }


class UpdateAwareBasicFilter:
    """Enhanced basic filter with LLM-powered universal job support"""
    
    def __init__(self, use_llm: bool = True):
        # Use LLM-powered universal filter by default
        if use_llm:
            self.resume_filter = UniversalResumeFilter()
            self.llm_mode = True
        else:
            self.resume_filter = UpdateAwareResumeFilter()
            self.llm_mode = False
        
        self.duplicate_detector = DuplicateCandidateDetector()
        self.duplicate_handler = DuplicateHandlingStrategy()
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def initialize_for_job(self, job_ticket):
        """Initialize filter for specific job (LLM analysis happens here)"""
        if self.llm_mode and hasattr(self.resume_filter, 'initialize_for_job'):
            self.resume_filter.initialize_for_job(job_ticket)
    
    def score_resume_comprehensive(self, resume_text: str, resume_path: Path, job_ticket) -> Dict:
        """Comprehensive scoring using multiple methods"""
        base_scores = self.resume_filter.score_resume(resume_text, job_ticket)
        
        similarity_score = 0.0
        if job_ticket.description:
            try:
                tfidf_matrix = self.vectorizer.fit_transform([job_ticket.description, resume_text])
                similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            except:
                similarity_score = 0.0
        
        additional_features = self._extract_additional_features(resume_text)
        
        result = {
            "file_path": str(resume_path),
            "filename": resume_path.name,
            "final_score": base_scores['final_score'],
            "skill_score": base_scores['skill_score'],
            "experience_score": base_scores['experience_score'],
            "location_score": base_scores['location_score'],
            "professional_development_score": base_scores['professional_development_score'],
            "certification_score": base_scores.get('certification_score', 0),
            "education_score": base_scores.get('education_score', 0),
            "similarity_score": similarity_score,
            "matched_skills": base_scores['matched_skills'],
            "matched_certifications": base_scores.get('matched_certifications', []),
            "detailed_skill_matches": base_scores['detailed_skill_matches'],
            "detected_experience_years": base_scores['detected_experience_years'],
            "professional_development": base_scores['professional_development'],
            "additional_features": additional_features,
            "scoring_weights": base_scores['scoring_weights'],
            "job_category": base_scores.get('job_category', 'Unknown'),
            "job_subcategory": base_scores.get('job_subcategory', 'Unknown'),
            "privacy_mode": base_scores.get('privacy_mode', 'ENABLED'),
            "job_requirements_used": base_scores['job_requirements']
        }
        
        return result
    
    def _extract_additional_features(self, resume_text: str) -> Dict:
        """Extract additional features from resume"""
        features = {}
        
        education_keywords = {
            'phd': 4, 'doctorate': 4,
            'master': 3, 'mba': 3, 'ms': 3, 'mtech': 3,
            'bachelor': 2, 'btech': 2, 'bs': 2, 'be': 2,
            'diploma': 1
        }
        
        resume_lower = resume_text.lower()
        education_score = 0
        for keyword, score in education_keywords.items():
            if keyword in resume_lower:
                education_score = max(education_score, score)
        
        features['education_level'] = education_score
        
        cert_keywords = ['certified', 'certification', 'certificate', 'aws certified', 'google certified', 'microsoft certified']
        features['has_certifications'] = any(cert in resume_lower for cert in cert_keywords)
        
        leadership_keywords = ['lead', 'manager', 'head', 'director', 'principal', 'senior', 'architect']
        features['leadership_experience'] = sum(1 for keyword in leadership_keywords if keyword in resume_lower)
        
        return features


class UpdatedResumeFilteringSystem:
    """
    🌍 ZERO-HARDCODING Universal Resume Filter
    🤖 Uses LLM ONLY for job analysis (not candidates)
    🔒 100% privacy-safe candidate processing
    ✅ Works for: Bus Driver, Chef, Astronaut, ANY job worldwide
    """
    
    def __init__(self, ticket_folder: str, use_llm: bool = True):
        self.ticket_folder = Path(ticket_folder)
        self.job_ticket = EnhancedJobTicket(ticket_folder)
        self.basic_filter = UpdateAwareBasicFilter(use_llm=use_llm)
        
        # Initialize filter for this specific job (LLM analysis happens here)
        self.basic_filter.initialize_for_job(self.job_ticket)
        
        self.output_folder = self.ticket_folder / "filtering_results"
        self.output_folder.mkdir(exist_ok=True)
        
        # Track processed resumes for incremental filtering
        self.processed_resumes_file = self.output_folder / "processed_resumes.json"
        self.processed_resumes = self._load_processed_resumes()
    
    def _load_processed_resumes(self) -> Dict:
        """Load the list of previously processed resumes"""
        if self.processed_resumes_file.exists():
            try:
                with open(self.processed_resumes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load processed resumes file: {e}")
                return {}
        return {}
    
    def _save_processed_resumes(self):
        """Save the list of processed resumes"""
        try:
            with open(self.processed_resumes_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_resumes, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save processed resumes file: {e}")
    
    def _get_resume_hash(self, resume_path: Path) -> str:
        """Generate a hash for a resume file based on filename and modification time"""
        import hashlib
        # Use filename and modification time to create a unique identifier
        file_info = f"{resume_path.name}_{resume_path.stat().st_mtime}"
        return hashlib.md5(file_info.encode()).hexdigest()
    
    def _get_new_resumes(self, all_resumes: List[Path]) -> List[Path]:
        """Identify which resumes are new and need processing"""
        new_resumes = []
        
        for resume in all_resumes:
            resume_hash = self._get_resume_hash(resume)
            if resume_hash not in self.processed_resumes:
                new_resumes.append(resume)
                print(f"  🆕 New resume detected: {resume.name}")
            else:
                print(f"  ✅ Already processed: {resume.name}")
        
        return new_resumes
    
    def _load_existing_results(self) -> Dict:
        """Load existing filtering results"""
        final_results_file = self.output_folder / "final_results.json"
        if final_results_file.exists():
            try:
                with open(final_results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing results: {e}")
        return None
    
    def _merge_initial_results(self, existing: Dict, new: Dict) -> Dict:
        """Merge new initial results with existing ones"""
        merged = existing.copy()
        
        # Handle both old and new structures
        existing_candidates = merged.get('all_ranked_candidates', merged.get('top_10', []))
        new_candidates = new.get('all_ranked_candidates', [])
        
        # Combine and deduplicate based on file_path
        existing_paths = {item.get('file_path') for item in existing_candidates}
        for item in new_candidates:
            if item.get('file_path') not in existing_paths:
                existing_candidates.append(item)
        
        # Re-sort by final_score
        existing_candidates.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        merged['all_ranked_candidates'] = existing_candidates
        
        # Remove old structure if it exists
        if 'top_10' in merged:
            del merged['top_10']
        
        # Update counts
        merged['total_processed'] = len(existing_candidates)
        merged['new_processed'] = len(new.get('all_ranked_candidates', []))
        
        return merged
    
    def _merge_final_results(self, existing: Dict, new: Dict) -> Dict:
        """Merge new final results with existing ones"""
        merged = existing.copy()
        
        # Handle both old and new structures
        existing_candidates = merged.get('all_ranked_candidates', merged.get('top_5_candidates', []))
        new_candidates = new.get('all_ranked_candidates', [])
        
        # Combine and deduplicate based on file_path
        existing_paths = {item.get('file_path') for item in existing_candidates}
        for item in new_candidates:
            if item.get('file_path') not in existing_paths:
                existing_candidates.append(item)
        
        # Re-rank the combined list by adjusted_score (final ranking)
        existing_candidates.sort(key=lambda x: x.get('adjusted_score', x.get('final_score', 0)), reverse=True)
        merged['all_ranked_candidates'] = existing_candidates
        
        # Remove old structure if it exists
        if 'top_5_candidates' in merged:
            del merged['top_5_candidates']
        
        # Update summary
        if 'summary' in merged:
            merged['summary']['final_selected'] = len(merged['all_ranked_candidates'])
            merged['summary']['new_candidates_added'] = len(new.get('all_ranked_candidates', []))
        
        return merged
    
    def filter_resumes(self, incremental: bool = True) -> Dict:
        """Main filtering method with incremental processing support"""
        print(f"\n{'='*70}")
        print(f"🚀 UNIVERSAL RESUME FILTERING SYSTEM")
        print(f"{'='*70}")
        print(f"Job Ticket: {self.job_ticket.ticket_id}")
        print(f"Position: {self.job_ticket.position}")
        print(f"Mode: {'INCREMENTAL' if incremental else 'FULL RE-PROCESSING'}")
        
        # Show LLM status
        if hasattr(self.basic_filter.resume_filter, 'llm_analyzer'):
            if self.basic_filter.resume_filter.llm_analyzer.llm_available:
                print(f"🤖 AI Mode: ENABLED - Works for ANY job worldwide")
            else:
                print(f"⚠️  AI Mode: DISABLED - Using basic mode (limited skills)")
        
        print(f"\n📋 JOB REQUIREMENTS:")
        print(f"  • Experience: {self.job_ticket.experience_required}")
        print(f"  • Skills: {', '.join(self.job_ticket.tech_stack)}")
        print(f"  • Location: {self.job_ticket.location}")
        print(f"  • Salary: {self.job_ticket.salary_range}")
        print(f"  • Deadline: {self.job_ticket.deadline}")
        print(f"{'='*70}\n")
        
        all_resumes = self.job_ticket.get_resumes()
        print(f"Found {len(all_resumes)} total resumes in folder")
        
        if not all_resumes:
            return {
                "error": "No resumes found in the ticket folder",
                "ticket_id": self.job_ticket.ticket_id
            }
        
        # Determine which resumes to process
        if incremental:
            resumes_to_process = self._get_new_resumes(all_resumes)
            print(f"\n🔄 INCREMENTAL MODE: Processing {len(resumes_to_process)} new resumes")
            
            if not resumes_to_process:
                print("✅ No new resumes to process. All resumes are up to date.")
                existing = self._load_existing_results()
                if existing:
                    return existing
                # If no existing results, fall through to process all resumes
                print("   No previous results found. Processing all resumes...")
                resumes_to_process = all_resumes
        else:
            resumes_to_process = all_resumes
            print(f"\n🔄 FULL RE-PROCESSING MODE: Processing all {len(resumes_to_process)} resumes")
        
        # Load existing results for merging
        existing_results = self._load_existing_results() if incremental else None
        
        print(f"\nStage 1: Algorithmic Filtering with Duplicate Detection...")
        initial_results = self._basic_filtering_with_duplicates(resumes_to_process)
        
        # Merge with existing results if in incremental mode
        if incremental and existing_results:
            initial_results = self._merge_initial_results(existing_results, initial_results)
        
        with open(self.output_folder / "stage1_results.json", 'w', encoding='utf-8') as f:
            json.dump(initial_results, f, indent=2, default=str)
        
        print(f"\nStage 2: Advanced Scoring and Ranking...")
        final_results = self._advanced_scoring(initial_results)
        
        # Merge with existing results if in incremental mode
        if incremental and existing_results:
            final_results = self._merge_final_results(existing_results, final_results)
        
        with open(self.output_folder / "final_results.json", 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, default=str)
        
        # Calculate duplicate statistics for banner
        duplicate_groups_count = initial_results.get('duplicate_groups_count', 0)
        duplicate_banner_message = ""
        if duplicate_groups_count > 0:
            duplicate_banner_message = f"⚠️ DUPLICATE RESUME DETECTED: {duplicate_groups_count} duplicate group(s) found! Duplicate candidates have been assigned the same rank."
        
        final_output = {
            "ticket_id": self.job_ticket.ticket_id,
            "position": self.job_ticket.position,
            "timestamp": datetime.now().isoformat(),
            "job_status": self.job_ticket.job_details.get('status', 'unknown'),
            "requirements_last_updated": self.job_ticket.job_details.get('last_updated', ''),
            "latest_requirements": {
                "experience": self.job_ticket.experience_required,
                "tech_stack": self.job_ticket.tech_stack,
                "location": self.job_ticket.location,
                "salary": self.job_ticket.salary_range,
                "deadline": self.job_ticket.deadline
            },
            "summary": {
                "total_resumes": len(initial_results.get("all_ranked_candidates", [])),
                "unique_candidates": initial_results.get('unique_candidates', 0),
                "duplicate_groups_found": duplicate_groups_count,
                "stage1_selected": len(initial_results.get("all_ranked_candidates", [])),
                "final_selected": len(final_results.get("all_ranked_candidates", [])),
                "duplicate_banner_message": duplicate_banner_message,
            },
            "duplicate_detection": initial_results.get('duplicate_summary', {}),
            "stage1_results": initial_results,
            "final_results": final_results,
            "all_ranked_candidates": final_results.get("all_ranked_candidates", []),
        }
        
        output_file = self.output_folder / f"final_results_{self.job_ticket.ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, default=str)
        
        self._create_enhanced_summary_report(final_output)
        
        # Update processed resumes tracking
        if incremental and resumes_to_process:
            for resume in resumes_to_process:
                resume_hash = self._get_resume_hash(resume)
                self.processed_resumes[resume_hash] = {
                    'filename': resume.name,
                    'processed_at': datetime.now().isoformat(),
                    'file_path': str(resume)
                }
            self._save_processed_resumes()
            print(f"✅ Updated processed resumes tracking for {len(resumes_to_process)} new resumes")
        
        print(f"\nSUCCESS: Filtering complete! Results saved to: {output_file}")
        
        return final_output
    
    def _basic_filtering_with_duplicates(self, resumes: List[Path]) -> Dict:
        """Stage 1 with duplicate detection and handling"""
        
        print("\nDetecting duplicate candidates...")
        
        duplicate_map = {}
        
        for resume_path in resumes:
            resume_text = ResumeExtractor.extract_text(resume_path)
            if not resume_text:
                continue
            
            candidate_id, duplicates = self.basic_filter.duplicate_detector.add_candidate(
                resume_text, resume_path.name
            )
            
            duplicate_map[resume_path.name] = {
                'candidate_id': candidate_id,
                'duplicates': [dup['filename'] for dup in duplicates] if duplicates else []
            }
            
            if duplicates:
                print(f"  WARNING: {resume_path.name} has {len(duplicates)} duplicate(s):")
                for dup in duplicates:
                    print(f"     - {dup['filename']} (confidence: {dup['confidence']:.1%}, reason: {dup['reason']})")
        
        dup_groups = self.basic_filter.duplicate_detector.get_duplicate_groups()
        
        print("\nScoring resumes...")
        scored_resumes = []
        processed_candidates = set()
        
        for i, resume_path in enumerate(resumes):
            print(f"  Processing {i+1}/{len(resumes)}: {resume_path.name}")
            
            resume_text = ResumeExtractor.extract_text(resume_path)
            if not resume_text:
                print(f"    WARNING: Failed to extract text from {resume_path.name}")
                continue
            
            candidate_info = duplicate_map.get(resume_path.name, {})
            candidate_id = candidate_info.get('candidate_id')
            
            score_result = self.basic_filter.score_resume_comprehensive(
                resume_text, 
                resume_path,
                self.job_ticket
            )
            
            score_result['candidate_id'] = candidate_id
            
            if candidate_info.get('duplicates'):
                score_result['has_duplicates'] = True
                score_result['duplicate_count'] = len(candidate_info['duplicates'])
                score_result['duplicates'] = candidate_info['duplicates']
            else:
                score_result['has_duplicates'] = False
                score_result['duplicate_count'] = 0
                score_result['duplicates'] = []
            
            scored_resumes.append(score_result)
        
        final_scored_resumes = scored_resumes
        
        # Mark all candidates in duplicate groups
        for group in dup_groups:
            if len(group) > 1:  # Only process groups with multiple candidates
                primary_candidate = None
                duplicate_filenames = []
                
                for candidate in final_scored_resumes:
                    if candidate['filename'] in [item['filename'] for item in group]:
                        if primary_candidate is None:
                            # First candidate becomes the primary
                            
                            primary_candidate = candidate
                            candidate['has_duplicates'] = True
                            candidate['duplicate_count'] = len(group) - 1
                            candidate['duplicates'] = []
                        else:
                            # Mark as duplicate of primarython 
                            candidate['has_duplicates'] = False
                            candidate['duplicate_count'] = 0
                            candidate['duplicates'] = []
                            candidate['duplicate_of'] = primary_candidate['filename']
                            duplicate_filenames.append(candidate['filename'])
                
                # Set the duplicate filenames for the primary candidate
                if primary_candidate:
                    primary_candidate['duplicates'] = duplicate_filenames
        
        # Note: Duplicate separation logic removed as it was interfering with duplicate ranking
        
        final_scored_resumes.sort(key=lambda x: x["final_score"], reverse=True)
        # Rank ALL candidates instead of just top 10
        all_ranked_candidates = final_scored_resumes
        
        print("\nAll Ranked Candidates (after duplicate handling):")
        for i, candidate in enumerate(all_ranked_candidates):
            print(f"  {i+1}. {candidate['filename']} - Score: {candidate['final_score']:.2%}")
            print(f"      Skills: {len(candidate['matched_skills'])}/{len(self.job_ticket.tech_stack)} matched")
            print(f"      Experience: {candidate['detected_experience_years']} years")
            print(f"      Prof. Development: {candidate['professional_development_score']:.2%}")
            if candidate.get('has_duplicates'):
                print(f"      WARNING: Best of {candidate.get('duplicate_count', 1) + 1} submissions")
        
        duplicate_summary = {
            "total_resumes_submitted": len(resumes),
            "unique_candidates": len(final_scored_resumes),
            "duplicate_groups_found": len(dup_groups),
            "duplicate_groups": [
                {
                    "group_size": len(group),
                    "filenames": [item['filename'] for item in group]
                }
                for group in dup_groups
            ]
        }
        
        print(f"\nDuplicate Detection Summary:")
        print(f"  Total resumes submitted: {duplicate_summary['total_resumes_submitted']}")
        print(f"  Unique candidates: {duplicate_summary['unique_candidates']}")
        print(f"  Duplicate groups found: {duplicate_summary['duplicate_groups_found']}")
        
        return {
            "all_resumes": final_scored_resumes,
            "all_ranked_candidates": all_ranked_candidates,
            "scoring_criteria": {
                "skills_required": self.job_ticket.tech_stack,
                "experience_range": self.job_ticket.experience_required,
                "location": self.job_ticket.location
            },
            "duplicate_summary": duplicate_summary,
            "unique_candidates": len(final_scored_resumes),
            "duplicate_groups_count": len(dup_groups)
        }
    
    def _merge_duplicate_scores(self, scored_resumes: List[Dict], dup_groups: List[List[Dict]]) -> List[Dict]:
        """Merge scores for duplicate candidates and select the best one"""
        if not dup_groups:
            return scored_resumes
        
        # Create a mapping of duplicate groups
        duplicate_map = {}
        for group in dup_groups:
            for candidate in group:
                duplicate_map[candidate['filename']] = {
                    'candidate_id': candidate['candidate_id'],
                    'duplicates': [c['filename'] for c in group if c['filename'] != candidate['filename']],
                    'duplicate_count': len(group) - 1
                }
        
        # Process each resume and add duplicate information
        for resume in scored_resumes:
            filename = resume['filename']
            if filename in duplicate_map:
                resume.update(duplicate_map[filename])
                resume['has_duplicates'] = True
            else:
                resume['has_duplicates'] = False
                resume['duplicate_count'] = 0
                resume['duplicates'] = []
        
        # Sort by score and return
        scored_resumes.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_resumes
    
    def _force_separate_candidates(self, scored_resumes: List[Dict]) -> List[Dict]:
        """Force separation of candidates that were incorrectly detected as duplicates"""
        # This is a workaround for cases where different people are incorrectly grouped as duplicates
        
        # Check if we have candidates with different names and emails that were marked as duplicates
        for i, resume in enumerate(scored_resumes):
            if resume.get('has_duplicates') and resume.get('duplicate_count', 0) > 0:
                # Check if the duplicates are actually different people
                duplicates = resume.get('duplicates', [])
                
                for dup_filename in duplicates:
                    # Find the duplicate resume
                    dup_resume = next((r for r in scored_resumes if r['filename'] == dup_filename), None)
                    
                    if dup_resume:
                        # Check if they have different names and emails
                        current_name = resume.get('applicant_name', resume['filename'])
                        dup_name = dup_resume.get('applicant_name', dup_filename)
                        
                        # If names are clearly different, separate them
                        if current_name != dup_name:
                            # Remove duplicate marking
                            resume['has_duplicates'] = False
                            resume['duplicate_count'] = 0
                            resume['duplicates'] = []
                            
                            # Also remove duplicate marking from the other resume
                            dup_resume['has_duplicates'] = False
                            dup_resume['duplicate_count'] = 0
                            dup_resume['duplicates'] = []
        
        return scored_resumes
    
    def _advanced_scoring(self, initial_results: Dict) -> Dict:
        """Stage 2: Advanced algorithmic scoring without LLM"""
        all_candidates = initial_results["all_ranked_candidates"]
        
        # Apply additional scoring criteria to ALL candidates
        for candidate in all_candidates:
            # Bonus for exact skill matches
            exact_matches = sum(1 for skill in self.job_ticket.tech_stack 
                              if skill.lower() in candidate['filename'].lower())
            candidate['exact_skill_bonus'] = exact_matches * 0.05
            
            # Bonus for certifications
            if candidate.get('additional_features', {}).get('has_certifications'):
                candidate['certification_bonus'] = 0.1
            else:
                candidate['certification_bonus'] = 0
            
            # Bonus for leadership experience
            leadership_score = candidate.get('additional_features', {}).get('leadership_experience', 0)
            candidate['leadership_bonus'] = min(leadership_score * 0.02, 0.1)
            
            # Recalculate final score with bonuses
            candidate['adjusted_score'] = min(
                candidate['final_score'] + 
                candidate['exact_skill_bonus'] + 
                candidate['certification_bonus'] + 
                candidate['leadership_bonus'],
                1.0
            )
        
        # Re-sort by adjusted score
        all_candidates.sort(key=lambda x: x['adjusted_score'], reverse=True)
        
        # Rank ALL candidates with duplicate-aware ranking
        all_ranked_candidates = []
        current_rank = 1
        processed_candidates = set()
        
        for i, candidate in enumerate(all_candidates):
            # Skip if already processed as part of a duplicate group
            if candidate['filename'] in processed_candidates:
                continue
                
            # Check if this candidate has duplicates
            if candidate.get('has_duplicates') and candidate.get('duplicate_count', 0) > 0:
                # This is the primary candidate in a duplicate group
                candidate['final_rank'] = current_rank
                candidate['is_duplicate_group'] = True
                candidate['duplicate_group_rank'] = current_rank
                candidate['selection_reason'] = self._generate_selection_reason(candidate)
                all_ranked_candidates.append(candidate)
                processed_candidates.add(candidate['filename'])
                
                # Find and mark all duplicate candidates with the same rank
                duplicates = candidate.get('duplicates', [])
                for dup_filename in duplicates:
                    # Find the duplicate resume in the list
                    for j, other_candidate in enumerate(all_candidates):
                        if other_candidate['filename'] == dup_filename and other_candidate['filename'] not in processed_candidates:
                            other_candidate['final_rank'] = current_rank
                            other_candidate['is_duplicate_group'] = True
                            other_candidate['duplicate_group_rank'] = current_rank
                            other_candidate['duplicate_of'] = candidate['filename']
                            other_candidate['selection_reason'] = self._generate_selection_reason(other_candidate)
                            all_ranked_candidates.append(other_candidate)
                            processed_candidates.add(other_candidate['filename'])
                            break
                
                # Only increment rank after processing the entire duplicate group
                current_rank += 1
            else:
                # Regular candidate without duplicates
                candidate['final_rank'] = current_rank
                candidate['is_duplicate_group'] = False
                candidate['selection_reason'] = self._generate_selection_reason(candidate)
                all_ranked_candidates.append(candidate)
                processed_candidates.add(candidate['filename'])
                current_rank += 1
        
        return {
            "all_ranked_candidates": all_ranked_candidates,
            "selection_criteria": "Algorithmic scoring based on skills, experience, professional development, and additional features",
            "scoring_method": "Pure algorithmic approach without LLM"
        }
    
    def _generate_selection_reason(self, candidate: Dict) -> str:
        """Generate selection reason based on scores"""
        reasons = []
        
        if candidate['skill_score'] >= 0.8:
            reasons.append("Excellent skill match")
        elif candidate['skill_score'] >= 0.6:
            reasons.append("Good skill match")
        else:
            reasons.append("Moderate skill match")
        
        if candidate['experience_score'] >= 0.9:
            reasons.append("perfect experience fit")
        elif candidate['experience_score'] >= 0.7:
            reasons.append("good experience level")
        
        if candidate['professional_development_score'] >= 0.6:
            reasons.append("strong professional development")
        
        if candidate.get('certification_bonus', 0) > 0:
            reasons.append("has relevant certifications")
        
        if candidate.get('leadership_bonus', 0) > 0:
            reasons.append("leadership experience")
        
        return "; ".join(reasons).capitalize()
    
    def _create_enhanced_summary_report(self, results: Dict):
        """Create detailed summary report"""
        report_path = self.output_folder / f"summary_report_{self.job_ticket.ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"RESUME FILTERING SUMMARY REPORT (NO LLM)\n")
            f.write(f"{'='*70}\n\n")
            f.write(f"Job Ticket ID: {results['ticket_id']}\n")
            f.write(f"Position: {results['position']}\n")
            f.write(f"Report Generated: {results['timestamp']}\n")
            
            f.write(f"\n{'='*70}\n")
            f.write(f"JOB REQUIREMENTS:\n")
            f.write(f"{'='*70}\n")
            f.write(f"Experience: {results['latest_requirements']['experience']}\n")
            f.write(f"Skills: {', '.join(results['latest_requirements']['tech_stack'])}\n")
            f.write(f"Location: {results['latest_requirements']['location']}\n")
            f.write(f"Salary: {results['latest_requirements']['salary']}\n")
            f.write(f"Deadline: {results['latest_requirements']['deadline']}\n")
            
            f.write(f"\n{'='*70}\n")
            f.write(f"FILTERING SUMMARY:\n")
            f.write(f"{'='*70}\n")
            f.write(f"Total Resumes Submitted: {results['summary']['total_resumes']}\n")
            f.write(f"Unique Candidates: {results['summary']['unique_candidates']}\n")
            f.write(f"Duplicate Groups Found: {results['summary']['duplicate_groups_found']}\n")
            f.write(f"Final Selected: {results['summary']['final_selected']}\n")
            
            # Add duplicate banner information
            if results['summary']['duplicate_groups_found'] > 0:
                f.write(f"\n⚠️  DUPLICATE RESUME DETECTED: {results['summary']['duplicate_groups_found']} duplicate group(s) found!\n")
                f.write(f"   Duplicate candidates have been assigned the same rank.\n")
                f.write(f"   Please review duplicate submissions carefully.\n")
            
            if results.get('duplicate_detection') and results['duplicate_detection'].get('duplicate_groups'):
                f.write(f"\n{'='*70}\n")
                f.write(f"DUPLICATE CANDIDATES DETECTED:\n")
                f.write(f"{'='*70}\n")
                for i, group in enumerate(results['duplicate_detection']['duplicate_groups'], 1):
                    f.write(f"\nGroup {i} ({group['group_size']} submissions):\n")
                    for filename in group['filenames']:
                        f.write(f"  - {filename}\n")
            
            f.write(f"\n{'='*70}\n")
            f.write(f"TOP CANDIDATES (RANKED):\n")
            f.write(f"{'='*70}\n\n")
            
            for i, candidate in enumerate(results.get('all_ranked_candidates', [])):
                # Show rank with duplicate information
                rank_display = f"{candidate.get('final_rank', i+1)}"
                if candidate.get('is_duplicate_group'):
                    rank_display += f" (DUPLICATE GROUP)"
                
                f.write(f"{rank_display}. {candidate['filename']}\n")
                f.write(f"   Overall Score: {candidate.get('adjusted_score', candidate['final_score']):.1%}\n")
                f.write(f"   Skill Match: {candidate['skill_score']:.1%} ({len(candidate['matched_skills'])}/{len(results['latest_requirements']['tech_stack'])} skills)\n")
                f.write(f"   Matched Skills: {', '.join(candidate['matched_skills'])}\n")
                f.write(f"   Experience: {candidate['detected_experience_years']} years (Score: {candidate['experience_score']:.1%})\n")
                f.write(f"   Location Match: {'Yes' if candidate['location_score'] > 0 else 'No'}\n")
                f.write(f"   Professional Development Score: {candidate['professional_development_score']:.1%}\n")
                f.write(f"   Selection Reason: {candidate.get('selection_reason', 'N/A')}\n")
                
                if candidate.get('has_duplicates'):
                    f.write(f"   ⚠️  DUPLICATE RESUME: Best of {candidate.get('duplicate_count', 1) + 1} submissions\n")
                    f.write(f"   Duplicate files: {', '.join(candidate.get('duplicates', []))}\n")
                elif candidate.get('duplicate_of'):
                    f.write(f"   ⚠️  DUPLICATE OF: {candidate['duplicate_of']}\n")
                
                f.write(f"\n")
        
        print(f"\nSummary report created: {report_path}")


def main():
    """Main function for running the resume filter"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='🌍 Universal Resume Filtering System - Works for ANY job worldwide')
    parser.add_argument('ticket_folder', help='Path to the ticket folder containing resumes and job details')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM mode (uses basic predefined skills only)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.ticket_folder):
        print(f"ERROR: Folder '{args.ticket_folder}' not found")
        return
    
    try:
        use_llm = not args.no_llm
        
        if use_llm:
            print("🌍 Initializing UNIVERSAL Resume Filtering System...")
            print("🤖 LLM Mode: Analyzing job to support ANY role worldwide")
            print("🔒 Privacy: Candidate resumes processed 100% locally")
            print("\n💡 To enable: Add your OpenAI API key to Backend/config.env")
            print("   OPENAI_API_KEY=your_api_key_here")
        else:
            print("Initializing Resume Filtering System (Basic Mode)...")
            print("⚠️  Limited to predefined tech skills only")
            print("💡 Remove --no-llm flag to enable universal job support")
        
        filter_system = UpdatedResumeFilteringSystem(args.ticket_folder, use_llm=use_llm)
        
        results = filter_system.filter_resumes()
        
        if "error" not in results:
            print(f"\n{'='*70}")
            print(f"✅ SUCCESS: FILTERING COMPLETE - FINAL SUMMARY")
            print(f"{'='*70}")
            
            # Show job category if available
            if results.get('all_ranked_candidates') and len(results['all_ranked_candidates']) > 0:
                first_candidate = results['all_ranked_candidates'][0]
                if first_candidate.get('job_category'):
                    print(f"Job Category: {first_candidate.get('job_category', 'Unknown')}")
                    print(f"Job Type: {first_candidate.get('job_subcategory', 'Unknown')}")
            
            # Handle both old and new result formats
            total_resumes = results.get('summary', {}).get('total_resumes', len(results.get('all_ranked_candidates', [])))
            unique_candidates = results.get('summary', {}).get('unique_candidates', len(results.get('all_ranked_candidates', [])))
            duplicate_groups = results.get('summary', {}).get('duplicate_groups_found', 0)
            
            print(f"Total resumes processed: {total_resumes}")
            print(f"Unique candidates identified: {unique_candidates}")
            print(f"Duplicate groups found: {duplicate_groups}")
            print(f"\nTop candidates:")
            for i, candidate in enumerate(results.get('all_ranked_candidates', [])[:10]):  # Show top 10
                print(f"  {i+1}. {candidate['filename']}")
                print(f"      Score: {candidate.get('adjusted_score', candidate['final_score']):.1%}")
                print(f"      Skills: {len(candidate['matched_skills'])}/{len(candidate.get('matched_skills', []) + candidate.get('job_requirements_used', {}).get('required_skills', []))} matched")
                print(f"      Experience: {candidate['detected_experience_years']} years")
                
                # Show certifications if matched
                if candidate.get('matched_certifications'):
                    print(f"      Certifications: {', '.join(candidate['matched_certifications'][:3])}")
                
                if candidate.get('has_duplicates'):
                    print(f"      ⚠️  WARNING: Best of {candidate.get('duplicate_count', 1) + 1} submissions")
            
            if len(results.get('all_ranked_candidates', [])) > 10:
                print(f"\n   ... and {len(results['all_ranked_candidates']) - 10} more candidates")
            
            print(f"\nResults saved in: {filter_system.output_folder}")
        else:
            print(f"\nERROR: {results['error']}")
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()