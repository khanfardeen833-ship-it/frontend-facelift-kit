# 🌍 Universal Resume Filtering System

## Zero Hardcoding - Works for ANY Job Worldwide

This system uses AI to analyze job requirements and match candidates, supporting **ANY job type in ANY industry in ANY country**.

### ✅ Supported Jobs

- **Transportation**: Bus Driver, Truck Driver, Taxi Driver, Delivery Driver
- **Healthcare**: Doctor, Nurse, Surgeon, Pharmacist, Therapist
- **Technology**: Software Engineer, Data Scientist, DevOps, Frontend/Backend
- **Hospitality**: Chef, Cook, Hotel Manager, Bartender, Restaurant Manager
- **Construction**: Electrician, Plumber, Carpenter, Builder, Contractor
- **Education**: Teacher, Professor, Tutor, Instructor, Trainer
- **And literally ANY other job!**

---

## 🔒 Privacy First

- **LLM analyzes**: Only job descriptions (NOT candidate data)
- **Candidate resumes**: Processed 100% locally on your server
- **No data sharing**: Resumes never sent to external APIs
- **GDPR compliant**: Complete data privacy

---

## 🚀 Quick Start

### 1. Get OpenAI API Key

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy your key

### 2. Configure

Edit `Backend/config.env`:

```env
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Run

```bash
# For ANY job (with LLM)
python Backend/resume_filter5.py "Backend/approved_tickets/your-job-folder"

# Examples:
python Backend/resume_filter5.py "Backend/approved_tickets/bus-driver"
python Backend/resume_filter5.py "Backend/approved_tickets/chef-position"
python Backend/resume_filter5.py "Backend/approved_tickets/software-engineer"

# Without LLM (basic mode - tech jobs only)
python Backend/resume_filter5.py "Backend/approved_tickets/your-job-folder" --no-llm
```

---

## 🎯 How It Works

```
┌────────────────────────────────────────┐
│  Step 1: Job Analysis (LLM - Once)     │
│  ✓ Reads job description              │
│  ✓ Extracts ALL required skills       │
│  ✓ Generates skill variations         │
│  ✓ Determines optimal scoring weights │
│  ✓ Identifies certifications needed   │
│  ✓ NO candidate data involved         │
└────────────────────────────────────────┘
              ↓ (Results cached)
┌────────────────────────────────────────┐
│  Step 2: Candidate Matching (Local)    │
│  ✓ For each resume (100% local):      │
│    - Match skills using AI variations │
│    - Calculate experience             │
│    - Check certifications             │
│    - Score education                  │
│    - Detect duplicates                │
│  ✓ NO external API calls              │
│  ✓ Complete privacy                   │
└────────────────────────────────────────┘
              ↓
┌────────────────────────────────────────┐
│  Step 3: Results                       │
│  ✓ Ranked candidates                  │
│  ✓ Detailed scoring breakdown         │
│  ✓ Duplicate detection                │
│  ✓ Summary reports                    │
└────────────────────────────────────────┘
```

---

## 📊 Example Output

### Bus Driver Position
```
🤖 Analyzing job with AI: Bus Driver

✅ AI Analysis Complete:
   📂 Category: Transportation
   🎯 Role: Bus Driver
   🌍 Region: United States
   💡 Skills Identified: 12
   📜 Certifications: ["Commercial Driver's License (CDL)", "Clean Driving Record", "DOT Physical"]
   ⚖️  Weights: Skills=25%, Exp=40%, Loc=20%

Top candidates:
  1. john_doe_resume.pdf
      Score: 87.5%
      Skills: 10/12 matched
      Experience: 8 years
      Certifications: CDL Class B, Clean Record
```

### Chef Position
```
🤖 Analyzing job with AI: Head Chef

✅ AI Analysis Complete:
   📂 Category: Hospitality
   🎯 Role: Head Chef
   🌍 Region: Global
   💡 Skills Identified: 15
   📜 Certifications: ["Food Safety Certification", "Culinary Degree"]
   ⚖️  Weights: Skills=30%, Exp=35%, Loc=20%

Top candidates:
  1. maria_chef.pdf
      Score: 92.3%
      Skills: 14/15 matched
      Experience: 10 years
      Certifications: ServSafe, Culinary Institute Diploma
```

---

## 💰 Cost Estimation

- **Model**: gpt-4o-mini (recommended)
- **Cost per job**: ~$0.01-0.03 per job analysis
- **Cost per candidate**: $0 (processed locally)

**Example**: Filtering 100 candidates for 1 job = **$0.02 total**

To use more accurate model:
```env
OPENAI_MODEL=gpt-4o  # More accurate, $0.10-0.20 per job
```

---

## 🔧 Advanced Usage

### Incremental Processing

The system automatically tracks processed resumes:

```bash
# First run: processes all resumes
python Backend/resume_filter5.py "Backend/approved_tickets/job-folder"

# Second run: only processes NEW resumes
python Backend/resume_filter5.py "Backend/approved_tickets/job-folder"
```

### Disable LLM (Basic Mode)

If you don't have an OpenAI API key:

```bash
python Backend/resume_filter5.py "Backend/approved_tickets/job-folder" --no-llm
```

⚠️ **Note**: Basic mode only works for tech jobs with predefined skills.

---

## 📁 Output Files

After filtering, you'll find in `job-folder/filtering_results/`:

- `final_results.json` - Complete results with all data
- `summary_report_*.txt` - Human-readable summary
- `stage1_results.json` - Initial filtering results
- `processed_resumes.json` - Tracking for incremental processing

---

## 🆘 Troubleshooting

### "LLM not available - using basic fallback mode"

**Solution**: Add your OpenAI API key to `Backend/config.env`

### "API key invalid"

**Solution**: 
1. Check your key is correct in `config.env`
2. Ensure you have billing set up at https://platform.openai.com/account/billing

### "Works for tech jobs but not bus driver"

**Solution**: Make sure LLM mode is enabled (don't use `--no-llm` flag)

---

## 🌟 Key Features

✅ **Zero Hardcoding**: No predefined skills or job types
✅ **Universal**: Works for ANY job worldwide
✅ **Privacy-Safe**: Candidate data never leaves your server
✅ **Smart Matching**: AI-powered skill variations
✅ **Duplicate Detection**: Identifies same candidates with multiple submissions
✅ **Incremental**: Only processes new resumes
✅ **Cost-Effective**: ~$0.02 per job analysis
✅ **Fast**: Local processing = no API latency for candidates

---

## 📞 Support

For issues or questions, check:
1. Your OpenAI API key is valid
2. You have sufficient OpenAI credits
3. Job description is detailed enough

---

**Made with ❤️ for universal hiring**
