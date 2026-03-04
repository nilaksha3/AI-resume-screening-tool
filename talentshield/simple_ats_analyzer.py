# enhanced_ats_analyzer.py
# Enhanced version with AI/ML components

import re
from collections import Counter
import json
import os
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from sklearn.ensemble import RandomForestClassifier

class SimpleATSAnalyzer:
    """
    A simple ATS analyzer that doesn't require NLTK.
    Uses basic keyword matching and pattern recognition to evaluate resumes.
    """
    
    def __init__(self):
        # Load industry-specific keywords
        self.industry_keywords = self._load_industry_keywords()
        
    def _load_industry_keywords(self):
        """Load industry keywords from JSON file or use default set"""
        keywords_file = os.path.join(os.path.dirname(__file__), 'industry_keywords.json')
        
        # Default keywords by industry and role - Expanded with more fields
        default_keywords = {
            "software": {
                "general": ["software", "development", "programming", "code", "developer", "engineer", "architecture", "debugging", "testing", "implementation"],
                "languages": ["python", "java", "javascript", "c++", "c#", "typescript", "go", "ruby", "php", "swift", "kotlin", "rust", "scala", "perl", "r", "dart", "julia", "lua", "matlab", "objective-c", "shell", "sql", "assembly"],
                "frontend": ["react", "angular", "vue", "html", "css", "javascript", "frontend", "ui", "ux", "design", "responsive", "accessibility", "a11y", "webpack", "babel", "sass", "less", "bootstrap", "material-ui", "tailwind", "jquery", "dom", "svg", "canvas", "animation", "mobile-first"],
                "backend": ["api", "rest", "graphql", "server", "database", "sql", "nosql", "node", "django", "flask", "express", "spring", "hibernate", "orm", "jpa", "asp.net", "laravel", "ruby on rails", "endpoints", "microservices", "serverless", "websockets", "oauth", "jwt", "authentication", "authorization", "caching", "rabbitmq", "kafka", "redis", "memcached"],
                "devops": ["docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "jenkins", "terraform", "deployment", "gitlab", "github actions", "travis", "circleci", "ansible", "puppet", "chef", "infrastructure as code", "monitoring", "logging", "elk", "prometheus", "grafana", "load balancing", "auto-scaling", "fault tolerance", "vpc", "security groups", "iam", "cloudformation", "serverless framework"],
                "data": ["analytics", "statistics", "machine learning", "ai", "big data", "data science", "algorithms", "data mining", "etl", "data warehouse", "data lake", "hadoop", "spark", "kafka", "hive", "tableau", "power bi", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "regression", "classification", "clustering", "nlp", "computer vision", "deep learning", "neural networks", "feature engineering", "data preprocessing", "data visualization", "jupyter", "databricks"],
                "mobile": ["android", "ios", "react native", "flutter", "kotlin", "swift", "mobile development", "app store", "google play", "push notifications", "offline support", "geolocation", "camera", "sensors", "mobile ui", "responsive design", "cross-platform", "native modules", "cocoapods", "gradle", "xcode", "android studio", "jetpack compose", "swiftui"],
                "game": ["unity", "unreal engine", "game development", "3d modeling", "animation", "physics", "rendering", "shaders", "level design", "character design", "game mechanics", "multiplayer", "networking", "pathfinding", "ai", "graphics", "directx", "opengl", "vulkan", "collision detection", "game engines", "sprite sheets", "assets", "procedural generation", "game loop"]
            },
            "marketing": {
                "general": ["marketing", "brand", "strategy", "campaign", "promotion", "advertising", "market research", "audience", "customer journey", "positioning", "value proposition", "messaging", "branding", "rebranding", "storytelling", "competitor analysis", "market segmentation", "customer personas", "marketing funnel", "marketing automation", "marketing analytics", "customer acquisition", "customer retention", "loyalty programs", "market penetration"],
                "digital": ["seo", "sem", "digital marketing", "social media", "content marketing", "email marketing", "ppc", "paid search", "google ads", "facebook ads", "instagram ads", "linkedin ads", "tiktok ads", "programmatic advertising", "display advertising", "retargeting", "remarketing", "cpc", "cpm", "ctr", "conversion rate", "landing pages", "a/b testing", "user acquisition", "mobile marketing", "app store optimization", "search console", "analytics", "attribution modeling", "marketing tags", "pixels"],
                "content": ["content creation", "copywriting", "storytelling", "editing", "blog", "article", "white paper", "case study", "ebook", "infographic", "video production", "podcasting", "content calendar", "editorial guidelines", "content strategy", "tone of voice", "thought leadership", "seo writing", "keyword research", "evergreen content", "viral content", "content distribution", "content promotion", "guest posting", "content repurposing", "content audit"],
                "analytics": ["google analytics", "metrics", "kpi", "performance", "conversion", "roi", "reporting", "google tag manager", "data studio", "attribution", "funnel analysis", "cohort analysis", "segmentation", "event tracking", "goal tracking", "ecommerce tracking", "customer lifetime value", "churn rate", "acquisition channels", "user behavior", "heatmaps", "session recording", "bounce rate", "exit rate", "engagement metrics", "data visualization"],
                "pr": ["public relations", "media relations", "press releases", "media coverage", "journalist outreach", "media kits", "crisis management", "reputation management", "brand mentions", "earned media", "media monitoring", "spokesperson training", "press conferences", "media interviews", "influencer relations", "thought leadership", "industry events", "awards", "speaking opportunities", "media pitching"],
                "social": ["social media marketing", "community management", "facebook", "instagram", "twitter", "linkedin", "tiktok", "youtube", "pinterest", "snapchat", "social listening", "social monitoring", "engagement rate", "follower growth", "social media analytics", "hashtag strategy", "user-generated content", "social media calendar", "social ads", "influencer marketing", "social selling", "social crm", "social customer service", "social commerce", "live streaming"]
            },
            "education": {
                "general": ["teaching", "education", "instructor", "curriculum", "lesson", "learning", "pedagogy", "classroom management", "student engagement", "education technology", "assessment", "evaluation", "grading", "feedback", "differentiated instruction", "learning objectives", "lesson planning", "teaching philosophy", "student-centered learning", "project-based learning", "inquiry-based learning", "cooperative learning", "formative assessment", "summative assessment", "rubrics"],
                "skills": ["classroom management", "assessment", "instruction", "differentiation", "pedagogy", "student engagement", "behavior management", "positive reinforcement", "classroom technology", "inclusive teaching", "special education", "iep", "504 plan", "scaffolding", "bloom's taxonomy", "critical thinking", "problem-solving", "collaboration", "communication", "creativity", "digital literacy", "data-driven instruction", "cultural competence", "trauma-informed teaching", "social-emotional learning"],
                "subjects": ["mathematics", "science", "english", "history", "art", "physical education", "language arts", "reading", "writing", "algebra", "geometry", "calculus", "statistics", "biology", "chemistry", "physics", "earth science", "environmental science", "literature", "grammar", "composition", "world history", "u.s. history", "civics", "geography", "economics", "music", "visual arts", "performing arts", "foreign language", "esl", "computer science"],
                "technology": ["educational technology", "e-learning", "digital tools", "interactive", "online learning", "learning management system", "lms", "canvas", "blackboard", "google classroom", "microsoft teams", "zoom", "virtual classroom", "flipped classroom", "blended learning", "digital assessment", "educational apps", "interactive whiteboard", "smart board", "tablets", "chromebooks", "digital literacy", "instructional design", "multimedia", "educational games", "virtual reality", "augmented reality", "adaptive learning"],
                "higher_education": ["professor", "tenure", "research", "publication", "grant writing", "academic advising", "dissertation", "thesis", "graduate studies", "undergraduate studies", "seminar", "lecture", "office hours", "academic freedom", "peer review", "sabbatical", "scholarly activity", "faculty development", "academic departments", "academic governance", "accreditation", "enrollment management", "student affairs", "institutional research", "academic integrity"]
            },
            "healthcare": {
                "general": ["healthcare", "patient", "treatment", "care", "medical", "clinical", "diagnosis", "therapy", "health records", "vitals", "symptoms", "prognosis", "consultation", "examination", "patient-centered care", "evidence-based practice", "preventive care", "acute care", "chronic care", "palliative care", "triage", "referral", "discharge planning", "follow-up care", "health literacy", "telehealth", "telemedicine"],
                "nursing": ["nurse", "rn", "patient care", "medications", "assessment", "documentation", "vital signs", "nursing care plan", "nursing diagnosis", "nursing intervention", "patient monitoring", "medication administration", "iv therapy", "wound care", "patient education", "care coordination", "bedside manner", "nurse practitioner", "triage", "clinical skills", "bls", "acls", "pals", "ekg", "pain management", "infection control"],
                "physician": ["doctor", "md", "diagnosis", "treatment", "examination", "prescription", "patient history", "medical assessment", "differential diagnosis", "physical examination", "medical orders", "treatment plan", "medical consultation", "specialty care", "primary care", "patient rounds", "surgical procedures", "medical ethics", "continuing medical education", "board certification", "residency", "fellowship", "medical research", "clinical trials", "evidence-based medicine"],
                "admin": ["healthcare administration", "medical records", "billing", "coding", "compliance", "hipaa", "healthcare management", "revenue cycle", "medical coding", "icd-10", "cpt codes", "healthcare policy", "quality improvement", "risk management", "patient satisfaction", "healthcare economics", "healthcare operations", "facility management", "credentialing", "utilization review", "case management", "electronic health records", "ehr implementation", "medical staff relations", "regulatory compliance"],
                "mental_health": ["psychiatry", "psychology", "therapy", "counseling", "mental health assessment", "dsm-5", "cognitive behavioral therapy", "psychotherapy", "group therapy", "family therapy", "crisis intervention", "suicide prevention", "substance abuse", "addiction treatment", "behavioral health", "psychiatric medications", "mental status examination", "therapeutic relationship", "trauma-informed care", "mindfulness", "emotional support", "coping strategies", "mental health advocacy", "recovery-oriented care", "psychiatric rehabilitation"],
                "public_health": ["epidemiology", "population health", "health promotion", "disease prevention", "community health", "public health policy", "health education", "environmental health", "health disparities", "social determinants of health", "global health", "infectious disease", "immunization", "health surveillance", "outbreak investigation", "contact tracing", "health statistics", "biostatistics", "public health research", "health impact assessment", "health equity", "public health campaigns", "health regulation", "health planning", "disaster preparedness"]
            },
            "finance": {
                "general": ["finance", "accounting", "budget", "financial", "investment", "banking", "capital", "assets", "liabilities", "equity", "cash flow", "revenue", "expense", "profit", "loss", "balance sheet", "income statement", "financial reporting", "fiscal year", "quarterly", "financial planning", "financial analysis", "financial management", "financial strategy", "corporate finance", "financial markets", "financial instruments", "financial regulations", "financial compliance", "financial controls"],
                "analysis": ["financial analysis", "forecasting", "modeling", "valuation", "risk assessment", "trend analysis", "scenario analysis", "sensitivity analysis", "discounted cash flow", "dcf", "net present value", "npv", "internal rate of return", "irr", "return on investment", "roi", "return on assets", "roa", "return on equity", "roe", "ebitda", "financial ratios", "benchmarking", "variance analysis", "performance metrics", "kpis", "financial statements analysis", "competitive analysis", "industry analysis", "market analysis"],
                "accounting": ["bookkeeping", "audit", "tax", "financial reporting", "gaap", "reconciliation", "accounts payable", "accounts receivable", "general ledger", "journal entries", "trial balance", "accrual accounting", "cash accounting", "asset management", "depreciation", "amortization", "tax planning", "tax preparation", "tax compliance", "internal audit", "external audit", "financial controls", "accounting software", "erp systems", "financial close", "month-end", "year-end", "financial statements", "consolidation", "financial disclosure"],
                "banking": ["loans", "credit", "banking", "portfolio", "wealth management", "client relationship", "retail banking", "commercial banking", "investment banking", "private banking", "mortgage lending", "loan origination", "loan servicing", "underwriting", "credit analysis", "risk management", "compliance", "aml", "kyc", "deposit accounts", "treasury services", "cash management", "payment processing", "foreign exchange", "wire transfers", "correspondent banking", "banking regulations", "basel", "liquidity management", "capital requirements"],
                "investment": ["asset management", "portfolio management", "securities", "stocks", "bonds", "mutual funds", "etfs", "derivatives", "options", "futures", "hedge funds", "private equity", "venture capital", "asset allocation", "diversification", "market analysis", "technical analysis", "fundamental analysis", "investment strategy", "risk management", "portfolio performance", "benchmark", "alpha", "beta", "sharpe ratio", "modern portfolio theory", "capital markets", "investment banking", "mergers and acquisitions", "initial public offerings"],
                "insurance": ["underwriting", "claims", "policy", "premium", "risk assessment", "actuarial", "life insurance", "health insurance", "property insurance", "casualty insurance", "liability insurance", "reinsurance", "insurance regulations", "policy administration", "claims processing", "loss adjustment", "risk management", "insurance portfolio", "insurance products", "customer acquisition", "customer retention", "agency management", "broker relationships", "insurance marketing", "policy renewal", "insurance compliance", "insurance fraud detection", "insurance analytics", "catastrophe modeling", "insurtech"]
            },
            "legal": {
                "general": ["legal", "law", "attorney", "lawyer", "counsel", "litigation", "regulation", "compliance", "contract", "statute", "case law", "legal research", "legal writing", "legal analysis", "jurisprudence", "legal precedent", "legal opinion", "legal advice", "legal representation", "advocacy", "legal strategy", "legal proceedings", "legal documentation", "legal issues", "legal matters", "judiciary", "legal system", "legal framework", "legal principles", "legal standards"],
                "litigation": ["litigation", "trial", "court", "lawsuit", "plaintiff", "defendant", "judge", "jury", "testimony", "witness", "evidence", "discovery", "deposition", "interrogatory", "subpoena", "motion", "brief", "argument", "hearing", "verdict", "judgment", "appeal", "settlement", "mediation", "arbitration", "alternative dispute resolution", "damages", "injunction", "class action", "legal procedure"],
                "corporate": ["corporate law", "business law", "mergers and acquisitions", "due diligence", "securities law", "corporate governance", "board of directors", "shareholders", "fiduciary duty", "corporate compliance", "corporate counsel", "regulatory affairs", "intellectual property", "patents", "trademarks", "copyrights", "licensing", "business contracts", "commercial agreements", "terms and conditions", "privacy policy", "data protection", "corporate structure", "subsidiary", "joint venture", "corporate transactions"],
                "specialties": ["criminal law", "family law", "tax law", "real estate law", "labor law", "employment law", "environmental law", "healthcare law", "immigration law", "international law", "maritime law", "bankruptcy law", "probate law", "trust and estate law", "elder law", "personal injury", "medical malpractice", "product liability", "constitutional law", "administrative law", "entertainment law", "sports law", "education law", "telecommunications law", "energy law", "banking law", "insurance law", "antitrust law", "cyber law", "data privacy law"]
            },
            "engineering": {
                "general": ["engineering", "design", "development", "specification", "testing", "validation", "requirements", "analysis", "problem-solving", "technical documentation", "quality assurance", "quality control", "standards", "codes", "regulations", "engineering management", "project planning", "resource allocation", "technical leadership", "cross-functional collaboration", "risk assessment", "failure analysis", "continuous improvement", "process optimization", "value engineering", "sustainability", "life cycle analysis", "engineering ethics", "professional development", "mentoring"],
                "mechanical": ["mechanical engineering", "mechanical design", "thermodynamics", "fluid mechanics", "heat transfer", "machine design", "mechanical systems", "hvac", "product design", "manufacturing processes", "tooling", "fixtures", "cad", "solidworks", "autocad", "finite element analysis", "fea", "computational fluid dynamics", "cfd", "tolerance analysis", "gd&t", "materials selection", "failure modes and effects analysis", "fmea", "root cause analysis", "prototype development", "3d printing", "additive manufacturing", "design for manufacturing", "dfm", "design for assembly", "dfa"],
                "electrical": ["electrical engineering", "circuit design", "pcb design", "power systems", "power electronics", "analog design", "digital design", "microcontrollers", "fpga", "asic", "embedded systems", "signal processing", "control systems", "motors", "generators", "transformers", "power distribution", "electromagnetic compatibility", "emc", "electronics manufacturing", "electronic components", "schematic capture", "simulation", "prototyping", "testing", "validation", "eagle", "altium", "kicad", "spice", "matlab"],
                "civil": ["civil engineering", "structural engineering", "geotechnical engineering", "transportation engineering", "water resources", "environmental engineering", "construction management", "site development", "infrastructure", "building codes", "structural analysis", "foundation design", "steel design", "concrete design", "highway design", "bridge design", "stormwater management", "hydraulics", "surveying", "gis", "cad", "revit", "autocad civil 3d", "project management", "construction documents", "specifications", "cost estimation", "permitting", "inspection", "quality control"],
                "chemical": ["chemical engineering", "process engineering", "chemical processes", "unit operations", "reaction engineering", "process control", "plant design", "equipment design", "chemical plant operations", "heat exchangers", "distillation", "separation processes", "fluid flow", "thermodynamics", "kinetics", "mass transfer", "heat transfer", "piping design", "instrumentation", "process safety", "hazop", "process hazard analysis", "process optimization", "scale-up", "pilot plant", "laboratory testing", "quality control", "regulatory compliance", "environmental compliance", "sustainability"],
                "aerospace": ["aerospace engineering", "aerodynamics", "propulsion", "aircraft design", "spacecraft design", "structural analysis", "flight mechanics", "control systems", "avionics", "navigation systems", "guidance systems", "aerodynamic testing", "wind tunnel testing", "composite materials", "stress analysis", "fatigue analysis", "aircraft structures", "aircraft systems", "space systems", "mission planning", "trajectory analysis", "orbital mechanics", "rocket design", "thermal protection systems", "aircraft certification", "safety critical systems", "reliability engineering", "systems engineering", "space environment", "flight testing"]
            },
            "design": {
                "general": ["design", "creative", "concept", "aesthetics", "visual", "layout", "composition", "color theory", "typography", "branding", "style guide", "design system", "user-centered design", "design thinking", "ideation", "prototyping", "iteration", "design critique", "design review", "design research", "competitive analysis", "mood boards", "sketching", "wireframing", "mockups", "design documentation", "design principles", "accessibility", "responsive design", "cross-platform design"],
                "graphic": ["graphic design", "print design", "digital design", "layout", "typography", "color theory", "illustration", "logo design", "brand identity", "visual identity", "marketing materials", "advertising design", "packaging design", "editorial design", "publication design", "infographics", "iconography", "vector graphics", "raster graphics", "adobe creative suite", "indesign", "photoshop", "illustrator", "print production", "prepress", "color management", "cmyk", "rgb", "design for print", "design for web"],
                "ui": ["ui design", "user interface", "visual design", "interaction design", "web design", "app design", "responsive design", "mobile design", "desktop design", "design systems", "component library", "wireframing", "prototyping", "mockups", "usability", "accessibility", "color theory", "typography", "navigation", "layout", "visual hierarchy", "micro-interactions", "animation", "iconography", "sketch", "figma", "adobe xd", "invision", "zeplin", "principle"],
                "ux": ["ux design", "user experience", "user research", "usability testing", "information architecture", "user flows", "journey mapping", "personas", "empathy mapping", "card sorting", "tree testing", "a/b testing", "heuristic evaluation", "interaction design", "wireframing", "prototyping", "user-centered design", "accessibility", "inclusive design", "usability", "user needs", "pain points", "user goals", "behavioral design", "cognitive psychology", "analytics", "metrics", "kpis", "design thinking", "service design"],
                "industrial": ["industrial design", "product design", "furniture design", "consumer products", "design for manufacturing", "dfm", "design for assembly", "dfa", "ergonomics", "human factors", "anthropometrics", "form and function", "aesthetic design", "functional design", "prototyping", "model making", "3d printing", "cad", "solidworks", "rhino", "keyshot", "rendering", "materials selection", "finishing", "detailing", "product development", "design for sustainability", "lifecycle assessment", "design research", "market research"],
                "interior": ["interior design", "space planning", "residential design", "commercial design", "hospitality design", "retail design", "office design", "healthcare design", "educational design", "lighting design", "furniture selection", "material specification", "color schemes", "finishes", "fixtures", "fittings", "construction documentation", "floor plans", "elevations", "sections", "renderings", "3d visualization", "building codes", "ada compliance", "environmental psychology", "biophilic design", "sustainable design", "acoustics", "thermal comfort", "indoor air quality"]
            },
            "customer_service": {
                "general": ["customer service", "customer support", "customer experience", "client relations", "customer satisfaction", "customer retention", "customer loyalty", "complaint resolution", "service quality", "service excellence", "customer feedback", "customer needs", "customer communication", "active listening", "empathy", "problem-solving", "conflict resolution", "de-escalation", "service recovery", "customer-centric", "customer journey", "service level agreements", "sla", "quality assurance", "customer service metrics", "first contact resolution", "response time", "customer service training", "service culture", "customer service tools"],
                "support": ["technical support", "help desk", "service desk", "it support", "troubleshooting", "issue resolution", "ticket management", "knowledge base", "faq maintenance", "customer education", "user guides", "training materials", "remote support", "screen sharing", "remote access", "system diagnostics", "bug tracking", "error resolution", "software support", "hardware support", "network support", "application support", "product support", "service escalation", "tier 1 support", "tier 2 support", "tier 3 support", "support documentation", "technical writing", "support metrics"],
                "sales": ["sales support", "account management", "client relationship", "sales assistance", "product knowledge", "solution selling", "consultative sales", "needs assessment", "recommendation", "cross-selling", "upselling", "sales follow-up", "client retention", "customer acquisition", "lead generation", "sales pipeline", "deal closing", "sales negotiations", "sales presentations", "product demonstrations", "competitive positioning", "sales enablement", "sales tools", "crm", "sales reporting", "sales forecasting", "territory management", "channel management", "sales training", "sales coaching"]
            },
            "human_resources": {
                "general": ["human resources", "hr", "personnel", "employee relations", "workforce management", "hr policies", "hr procedures", "hr strategy", "hr operations", "hr information systems", "hris", "hr analytics", "hr metrics", "compliance", "employment law", "labor relations", "employee engagement", "employee experience", "organizational development", "change management", "culture development", "diversity and inclusion", "dei", "employee wellness", "work-life balance", "employee assistance", "hr communication", "hr business partner", "hr consulting", "hr project management"],
                "recruitment": ["recruitment", "talent acquisition", "hiring", "interviewing", "candidate assessment", "candidate screening", "job descriptions", "job posting", "job advertising", "applicant tracking system", "ats", "recruitment marketing", "employer branding", "employee referrals", "campus recruiting", "executive search", "headhunting", "sourcing", "talent sourcing", "talent pipeline", "candidate experience", "candidate relationship management", "selection process", "background checks", "reference checks", "onboarding", "new hire orientation", "recruitment metrics", "time to hire", "cost per hire"],
                "training": ["training", "development", "learning", "instructional design", "training needs analysis", "curriculum development", "training materials", "learning management system", "lms", "e-learning", "virtual training", "instructor-led training", "ilt", "webinars", "workshops", "on-the-job training", "mentoring", "coaching", "professional development", "skill development", "competency development", "leadership development", "management development", "succession planning", "talent management", "career pathing", "learning evaluation", "training effectiveness", "training roi", "certification programs"],
                "compensation": ["compensation", "benefits", "salary", "wages", "pay", "incentives", "bonuses", "commission", "stock options", "equity", "retirement plans", "401k", "pension", "health insurance", "dental insurance", "vision insurance", "life insurance", "disability insurance", "paid time off", "pto", "vacation", "sick leave", "parental leave", "family leave", "compensation structure", "job evaluation", "job grading", "salary surveys", "market data", "compensation benchmarking", "total rewards", "executive compensation", "sales compensation", "variable pay", "merit increases"]
            },
            "general": {
                "skills": ["communication", "teamwork", "leadership", "problem-solving", "critical thinking", 
                          "time management", "organization", "detail-oriented", "collaboration", "adaptability",
                          "project management", "research", "analysis", "planning", "presentation", "writing",
                          "creativity", "innovation", "strategic thinking", "decision making", "negotiation",
                          "conflict resolution", "customer service", "interpersonal skills", "emotional intelligence",
                          "cultural awareness", "multilingual", "public speaking", "facilitation", "mentoring",
                          "coaching", "analytical skills", "quantitative analysis", "qualitative analysis", "data analysis",
                          "business acumen", "financial acumen", "technical aptitude", "digital literacy", "computer skills",
                          "active listening", "written communication", "verbal communication", "persuasion", "influencing",
                          "networking", "relationship building", "stakeholder management", "change management", "resource management"],
                "tools": ["microsoft office", "excel", "word", "powerpoint", "outlook", "google workspace", 
                          "google docs", "google sheets", "google slides", "gmail", "microsoft teams", "zoom",
                          "slack", "trello", "asana", "monday.com", "jira", "confluence", "notion", "airtable",
                          "salesforce", "hubspot", "zoho", "quickbooks", "sap", "oracle", "tableau", "power bi",
                          "google analytics", "adobe creative suite", "photoshop", "illustrator", "indesign",
                          "canva", "figma", "sketch", "adobe xd", "wordpress", "shopify", "wix", "squarespace",
                          "github", "gitlab", "bitbucket", "vs code", "sublime text", "intellij", "eclipse",
                          "android studio", "xcode", "aws", "azure", "gcp", "docker", "kubernetes", "terraform"],
                "achievements": ["increased", "decreased", "improved", "achieved", "launched", "developed", 
                                "managed", "led", "created", "implemented", "reduced", "saved", "generated",
                                "exceeded", "surpassed", "maximized", "minimized", "optimized", "streamlined",
                                "transformed", "revamped", "revolutionized", "pioneered", "spearheaded", "established",
                                "founded", "initiated", "introduced", "innovated", "designed", "architected",
                                "engineered", "programmed", "constructed", "built", "produced", "authored",
                                "published", "presented", "negotiated", "secured", "won", "awarded", "recognized",
                                "certified", "trained", "mentored", "coached", "guided", "resolved", "solved"]
            }
        }
        
        try:
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r') as f:
                    return json.load(f)
            else:
                return default_keywords
        except Exception as e:
            print(f"Error loading keywords: {e}, using defaults")
            return default_keywords
        
    def _get_position_keywords(self, position):
        """Determine relevant keywords for the given position"""
        position_lower = position.lower()
        keywords = set()
        
        # Always include general skills
        for skill in self.industry_keywords["general"]["skills"]:
            keywords.add(skill)
        
        for skill in self.industry_keywords["general"]["tools"]:
            keywords.add(skill)
        
        # Find relevant industry
        if any(word in position_lower for word in ["software", "developer", "engineer", "programming", "coder"]):
            keywords.update(self.industry_keywords["software"]["general"])
            keywords.update(self.industry_keywords["software"]["languages"])
            
            if any(word in position_lower for word in ["frontend", "ui", "ux", "web"]):
                keywords.update(self.industry_keywords["software"]["frontend"])
            
            if any(word in position_lower for word in ["backend", "server", "api"]):
                keywords.update(self.industry_keywords["software"]["backend"])
            
            if any(word in position_lower for word in ["devops", "deployment", "infrastructure"]):
                keywords.update(self.industry_keywords["software"]["devops"])
            
            if any(word in position_lower for word in ["data", "analytics", "science", "machine learning"]):
                keywords.update(self.industry_keywords["software"]["data"])
                
            if any(word in position_lower for word in ["mobile", "android", "ios", "app"]):
                keywords.update(self.industry_keywords["software"]["mobile"])
                
            if any(word in position_lower for word in ["game", "gaming", "unity", "unreal"]):
                keywords.update(self.industry_keywords["software"]["game"])
        
        elif any(word in position_lower for word in ["marketing", "advertis", "brand", "promotion"]):
            keywords.update(self.industry_keywords["marketing"]["general"])
            
            if any(word in position_lower for word in ["digital", "online", "web", "social"]):
                keywords.update(self.industry_keywords["marketing"]["digital"])
            
            if any(word in position_lower for word in ["content", "write", "copy"]):
                keywords.update(self.industry_keywords["marketing"]["content"])
            
            keywords.update(self.industry_keywords["marketing"]["analytics"])
            if any(word in position_lower for word in ["pr", "public relations", "media relations"]):
                keywords.update(self.industry_keywords["marketing"]["pr"])
                
            if any(word in position_lower for word in ["social", "community", "facebook", "instagram", "twitter"]):
                keywords.update(self.industry_keywords["marketing"]["social"])
        
        elif any(word in position_lower for word in ["teach", "education", "instructor", "professor", "tutor"]):
            keywords.update(self.industry_keywords["education"]["general"])
            keywords.update(self.industry_keywords["education"]["skills"])
            
            if "technology" in position_lower or "digital" in position_lower:
                keywords.update(self.industry_keywords["education"]["technology"])
            
            # Look for specific subjects
            for subject in self.industry_keywords["education"]["subjects"]:
                if subject in position_lower:
                    keywords.add(subject)
                    
            if any(word in position_lower for word in ["professor", "university", "college", "academic"]):
                keywords.update(self.industry_keywords["education"]["higher_education"])
        
        elif any(word in position_lower for word in ["healthcare", "medical", "health", "hospital", "clinic", "doctor", "nurse"]):
            keywords.update(self.industry_keywords["healthcare"]["general"])
            
            if any(word in position_lower for word in ["nurse", "nursing", "rn"]):
                keywords.update(self.industry_keywords["healthcare"]["nursing"])
            
            if any(word in position_lower for word in ["doctor", "physician", "md"]):
                keywords.update(self.industry_keywords["healthcare"]["physician"])
            
            if any(word in position_lower for word in ["admin", "administration", "manager"]):
                keywords.update(self.industry_keywords["healthcare"]["admin"])
                
            if any(word in position_lower for word in ["mental", "psychiatric", "psychology", "counseling"]):
                keywords.update(self.industry_keywords["healthcare"]["mental_health"])
                
            if any(word in position_lower for word in ["public health", "epidemiology", "community health"]):
                keywords.update(self.industry_keywords["healthcare"]["public_health"])
        
        elif any(word in position_lower for word in ["finance", "accounting", "accountant", "financial", "banking"]):
            keywords.update(self.industry_keywords["finance"]["general"])
            
            if any(word in position_lower for word in ["analyst", "analysis"]):
                keywords.update(self.industry_keywords["finance"]["analysis"])
            
            if any(word in position_lower for word in ["account", "bookkeep", "audit"]):
                keywords.update(self.industry_keywords["finance"]["accounting"])
            
            if any(word in position_lower for word in ["bank", "loan", "credit", "wealth"]):
                keywords.update(self.industry_keywords["finance"]["banking"])
                
            if any(word in position_lower for word in ["invest", "portfolio", "asset", "wealth"]):
                keywords.update(self.industry_keywords["finance"]["investment"])
                
            if any(word in position_lower for word in ["insurance", "underwriting", "actuar", "claims"]):
                keywords.update(self.industry_keywords["finance"]["insurance"])
                
        elif any(word in position_lower for word in ["legal", "law", "attorney", "lawyer", "counsel", "paralegal"]):
            keywords.update(self.industry_keywords["legal"]["general"])
            
            if any(word in position_lower for word in ["litigation", "trial", "court"]):
                keywords.update(self.industry_keywords["legal"]["litigation"])
                
            if any(word in position_lower for word in ["corporate", "business law", "mergers"]):
                keywords.update(self.industry_keywords["legal"]["corporate"])
                
            # Check for legal specialties
            for specialty in self.industry_keywords["legal"]["specialties"]:
                if specialty in position_lower:
                    keywords.add(specialty)
                    
        elif any(word in position_lower for word in ["engineer", "engineering", "mechanical", "electrical", "civil", "chemical"]):
            keywords.update(self.industry_keywords["engineering"]["general"])
            
            if any(word in position_lower for word in ["mechanical", "machine", "hvac"]):
                keywords.update(self.industry_keywords["engineering"]["mechanical"])
                
            if any(word in position_lower for word in ["electrical", "electronics", "circuit"]):
                keywords.update(self.industry_keywords["engineering"]["electrical"])
                
            if any(word in position_lower for word in ["civil", "structural", "construction"]):
                keywords.update(self.industry_keywords["engineering"]["civil"])
                
            if any(word in position_lower for word in ["chemical", "process"]):
                keywords.update(self.industry_keywords["engineering"]["chemical"])
                
            if any(word in position_lower for word in ["aerospace", "aeronautical", "aircraft"]):
                keywords.update(self.industry_keywords["engineering"]["aerospace"])
                
        elif any(word in position_lower for word in ["design", "designer", "creative", "artist"]):
            keywords.update(self.industry_keywords["design"]["general"])
            
            if any(word in position_lower for word in ["graphic", "print", "visual"]):
                keywords.update(self.industry_keywords["design"]["graphic"])
                
            if any(word in position_lower for word in ["ui", "user interface", "visual design"]):
                keywords.update(self.industry_keywords["design"]["ui"])
                
            if any(word in position_lower for word in ["ux", "user experience", "interaction"]):
                keywords.update(self.industry_keywords["design"]["ux"])
                
            if any(word in position_lower for word in ["industrial", "product design"]):
                keywords.update(self.industry_keywords["design"]["industrial"])
                
            if any(word in position_lower for word in ["interior", "space planning"]):
                keywords.update(self.industry_keywords["design"]["interior"])
                
        elif any(word in position_lower for word in ["customer", "support", "service", "client"]):
            keywords.update(self.industry_keywords["customer_service"]["general"])
            
            if any(word in position_lower for word in ["technical support", "help desk", "it support"]):
                keywords.update(self.industry_keywords["customer_service"]["support"])
                
            if any(word in position_lower for word in ["sales", "account", "client"]):
                keywords.update(self.industry_keywords["customer_service"]["sales"])
                
        elif any(word in position_lower for word in ["hr", "human resources", "talent", "recruiting"]):
            keywords.update(self.industry_keywords["human_resources"]["general"])
            
            if any(word in position_lower for word in ["recruit", "talent acquisition", "hiring"]):
                keywords.update(self.industry_keywords["human_resources"]["recruitment"])
                
            if any(word in position_lower for word in ["training", "learning", "development"]):
                keywords.update(self.industry_keywords["human_resources"]["training"])
                
            if any(word in position_lower for word in ["compensation", "benefits", "salary"]):
                keywords.update(self.industry_keywords["human_resources"]["compensation"])
        
        return list(keywords)
    
    def _check_education(self, resume_text):
        """Check for education details in the resume"""
        education_score = 0
        education_feedback = []
        
        # Check for education section
        edu_pattern = re.compile(r'(?:education|academic|degree|qualification)(?:[\s\:]+)(.*?)(?:experience|skills|work history|employment|projects|references|publications|$)', re.IGNORECASE | re.DOTALL)
        edu_match = edu_pattern.search(resume_text)
        
        if edu_match:
            edu_section = edu_match.group(1)
            
            # Check for degree mentions
            degree_pattern = re.compile(r'(?:bachelor|master|phd|doctorate|mba|bba|bs|ba|ms|ma|b\.tech|m\.tech|b\.e|m\.e)', re.IGNORECASE)
            degree_matches = degree_pattern.findall(edu_section)
            
            if degree_matches:
                education_score += min(len(degree_matches) * 5, 5)  # Changed from 10 to 5 points max
                education_feedback.append(f"Found {len(degree_matches)} degree(s) mentioned")
            else:
                education_feedback.append("No specific degrees detected")
            
            # Check for year mentions (likely graduation years)
            year_pattern = re.compile(r'(?:19|20)\d{2}')
            year_matches = year_pattern.findall(edu_section)
            
            if year_matches:
                education_score += 5
                education_feedback.append("Education dates are included")
            else:
                education_feedback.append("Consider adding graduation dates")
        else:
            education_feedback.append("No clear education section found")
        
        return education_score, education_feedback
    
    def _check_experience(self, resume_text):
        """Check for work experience details in the resume"""
        experience_score = 0
        experience_feedback = []
        
        # Check for experience section
        exp_pattern = re.compile(r'(?:experience|work history|employment|professional|career)(?:[\s\:]+)(.*?)(?:education|skills|certifications|references|projects|publications|$)', re.IGNORECASE | re.DOTALL)
        exp_match = exp_pattern.search(resume_text)
        
        if exp_match:
            exp_section = exp_match.group(1)
            
            # Check for date ranges
            date_ranges = re.findall(r'(?:(?:19|20)\d{2}[\s\-\–\—]+(?:(?:19|20)\d{2}|present|current))', exp_section, re.IGNORECASE)
            
            if date_ranges:
                experience_score += 10
                experience_feedback.append("Work dates clearly formatted")
            else:
                experience_feedback.append("Consider clearly formatting employment dates")
            
            # Check for bullet points
            bullet_pattern = re.compile(r'[\•\-\*\✓]')
            bullet_matches = bullet_pattern.findall(exp_section)
            
            if len(bullet_matches) >= 5:
                experience_score += 10
                experience_feedback.append("Good use of bullet points to highlight experience")
            else:
                experience_feedback.append("Consider using bullet points to highlight achievements")
            
            # Check for achievement keywords
            achievement_verbs = ["achieved", "increased", "decreased", "improved", "managed", "led", "created", "developed", "implemented", "designed", "launched"]
            achievement_count = 0
            for verb in achievement_verbs:
                if verb in exp_section.lower():
                    achievement_count += 1
            
            if achievement_count >= 3:
                experience_score += 10
                experience_feedback.append("Good use of achievement-oriented language")
            else:
                experience_feedback.append("Add more achievement-oriented language with metrics")
        else:
            experience_feedback.append("No clear experience section found")
        
        return experience_score, experience_feedback
    
    def analyze_resume(self, resume_text, position, company=None, job_description=None):
        """
        Analyze a resume for ATS compatibility and provide feedback
        
        Args:
            resume_text (str): The extracted text from the resume
            position (str): The job position title
            company (str, optional): Company name
            job_description (str, optional): Job description text
            
        Returns:
            dict: Analysis results with score, matched/missing keywords, etc.
        """
        # Clean text
        resume_text = resume_text.strip()
        resume_lower = resume_text.lower()
        
        # Get position-specific keywords
        position_keywords = self._get_position_keywords(position)
        
        # Check for keyword matches using simple string matching
        matched_keywords = []
        for keyword in position_keywords:
            if keyword.lower() in resume_lower:
                matched_keywords.append(keyword)
        
        # Identify missing keywords
        missing_keywords = []
        for keyword in position_keywords:
            if keyword.lower() not in resume_lower and keyword not in matched_keywords:
                missing_keywords.append(keyword)
        
        # Limit to top 10 most important missing keywords
        missing_keywords = missing_keywords[:10]
        
        # Check education formatting
        education_score, education_feedback = self._check_education(resume_text)
        
        # Check experience formatting
        experience_score, experience_feedback = self._check_experience(resume_text)
        
        # Calculate keyword score (0-50 points)
        keyword_total = len(position_keywords)
        keyword_matches = len(matched_keywords)
        
        # Modified keyword scoring: 5 points per keyword match, up to 50 max
        if keyword_matches > 0:
            keyword_score = min(keyword_matches * 5, 50)
        else:
            keyword_score = 0
        
        # Calculate overall score (0-100)
        overall_score = keyword_score + education_score + min(experience_score, 30)
        overall_score = min(max(overall_score, 40), 100)  # Ensure score is between 40-100
        
        # Generate feedback
        feedback_points = []
        
        # Keyword feedback
        if keyword_score >= 40:
            feedback_points.append(f"Strong keyword matches for {position} position.")
        elif keyword_score >= 30:
            feedback_points.append(f"Good keyword matches, but could be improved for {position} position.")
        else:
            feedback_points.append(f"Limited keyword matches for {position} position. Consider adding more relevant terms.")
        
        # Add section-specific feedback
        feedback_points.extend(education_feedback)
        feedback_points.extend(experience_feedback)
        
        # Generate overall feedback
        feedback = " ".join(feedback_points)
        
        # Generate improvement suggestions
        if missing_keywords:
            improvement = f"Consider adding these keywords relevant to the {position} position: {', '.join(missing_keywords[:5])}. "
        else:
            improvement = ""
        
        if education_score < 5:  # Changed from 10 to 5
            improvement += "Enhance your education section with more details about degrees, dates, and achievements. "
        
        if experience_score < 20:
            improvement += "Strengthen your experience section with quantifiable achievements and clear date formatting. "
        
        improvement += "Tailor your resume specifically to the job description, emphasizing relevant skills and experiences."
        
        return {
            "score": overall_score,
            "keywordMatches": matched_keywords,
            "missingKeywords": missing_keywords,
            "feedback": feedback,
            "improvedContent": improvement
        }
        class EnhancedATSAnalyzer(SimpleATSAnalyzer):
       
    
          def __init__(self, model_path=None):
              super().__init__()
        
        # Initialize NLP components
        try:
            self.nlp = spacy.load("en_core_web_md")  # Medium-sized model with word vectors
        except:
            print("Warning: Could not load spaCy model. Run 'python -m spacy download en_core_web_md' to install it.")
            try:
                self.nlp = spacy.load("en_core_web_sm")  # Fallback to small model
                print("Using smaller spaCy model without word vectors.")
            except:
                print("Error: spaCy model not available. NLP features will be limited.")
                self.nlp = None
        
        # Initialize TF-IDF vectorizer for document similarity
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        
        # Initialize ML model for scoring (if available)
        self.ml_model = None
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
                print(f"Loaded ML model from {model_path}")
            except Exception as e:
                print(f"Error loading ML model: {e}")
        
    def extract_sections(self, resume_text):
        """
        Use NLP to extract sections from the resume
        More accurate than regex-based approach
        """
        if not self.nlp:
            # Fallback to parent class regex method if NLP not available
            return None
        
        doc = self.nlp(resume_text)
        
        # Split the document into sections using NLP
        sections = {}
        current_section = "header"
        current_text = []
        
        section_headers = ["education", "experience", "skills", "projects", 
                           "certifications", "publications", "awards", "references"]
        
        for para in resume_text.split('\n\n'):
            para = para.strip()
            if not para:
                continue
                
            # Check if paragraph is a section header
            is_header = False
            para_lower = para.lower()
            
            for header in section_headers:
                if header in para_lower and len(para.split()) < 5:  # Short lines with keywords are likely headers
                    current_section = header
                    is_header = True
                    break
            
            if not is_header:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(para)
        
        # Convert lists to strings
        for section in sections:
            sections[section] = '\n'.join(sections[section])
        
        return sections
    
    def extract_skills_with_nlp(self, resume_text):
        """Extract skills using NLP techniques"""
        if not self.nlp:
            return []
            
        # Define common skill indicators
        skill_indicators = ["proficient in", "skilled in", "expertise in", "experience with", 
                           "knowledge of", "familiar with", "specializing in"]
        
        doc = self.nlp(resume_text)
        skills = set()
        
        # Method 1: Look for noun phrases after skill indicators
        for chunk in doc.noun_chunks:
            for indicator in skill_indicators:
                if indicator in chunk.text.lower():
                    # Get the part after the indicator
                    parts = chunk.text.lower().split(indicator)
                    if len(parts) > 1:
                        skills.add(parts[1].strip())
        
        # Method 2: Extract proper nouns that might be technologies/tools
        for token in doc:
            if token.pos_ == "PROPN" and len(token.text) > 1:
                # Check if it's likely a skill (not a person name or place)
                if token.text.lower() not in ["i", "me", "my", "mine", "we", "us", "our"]:
                    skills.add(token.text)
        
        # Method 3: Look for known skills from our keyword lists
        all_keywords = []
        for industry in self.industry_keywords:
            if industry != "general":
                for category in self.industry_keywords[industry]:
                    all_keywords.extend(self.industry_keywords[industry][category])
        
        for keyword in all_keywords:
            if keyword.lower() in resume_text.lower():
                skills.add(keyword)
        
        return list(skills)
    
    def semantic_keyword_match(self, resume_text, position_keywords):
        """
        Use word embeddings to find semantic matches between resume and keywords
        Goes beyond exact string matching to find related terms
        """
        if not self.nlp:
            # Fallback to exact matching if NLP not available
            direct_matches = []
            for keyword in position_keywords:
                if keyword.lower() in resume_text.lower():
                    direct_matches.append(keyword)
            return direct_matches, []
        
        # Direct matches (as in original code)
        direct_matches = []
        for keyword in position_keywords:
            if keyword.lower() in resume_text.lower():
                direct_matches.append(keyword)
        
        # Create doc objects
        resume_doc = self.nlp(resume_text.lower())
        
        # Semantic matches using word vectors
        semantic_matches = []
        for keyword in position_keywords:
            if keyword not in direct_matches:  # Only look for semantic matches if not directly found
                keyword_doc = self.nlp(keyword)
                
                # Look for contextual matches using similarity
                best_similarity = 0
                best_match = None
                
                # Check resumé in chunks to handle large documents
                chunk_size = 200  # characters
                for i in range(0, len(resume_text), chunk_size):
                    chunk = resume_text[i:i+chunk_size]
                    if len(chunk.strip()) > 10:  # Skip empty chunks
                        chunk_doc = self.nlp(chunk)
                        similarity = keyword_doc.similarity(chunk_doc)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = chunk
                
                # If similarity is high enough, consider it a semantic match
                if best_similarity > 0.7:  # Threshold for semantic similarity
                    semantic_matches.append((keyword, round(best_similarity, 2), best_match[:50] + "..."))
        
        return direct_matches, semantic_matches
    
    def calculate_document_similarity(self, resume_text, job_description):
        """
        Calculate similarity between resume and job description using TF-IDF vectors
        This helps measure how well the resume aligns with the specific job
        """
        if not job_description:
            return 0.5  # Default middle value if no job description provided
            
        documents = [resume_text.lower(), job_description.lower()]
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            print("Error calculating document similarity")
            return 0.5
    
    def calculate_section_quality(self, section_text):
        """
        Analyze the quality of a section using NLP
        Checks for diverse vocabulary, sentence complexity, actionable language, etc.
        """
        if not self.nlp or not section_text:
            return 0.5  # Default middle value if NLP not available or no text
        
        doc = self.nlp(section_text)
        
        # Metrics to evaluate section quality
        metrics = {
            "sentence_count": len(list(doc.sents)),
            "avg_sentence_length": sum(len(sent) for sent in doc.sents) / max(len(list(doc.sents)), 1),
            "verb_count": sum(1 for token in doc if token.pos_ == "VERB"),
            "action_verb_ratio": sum(1 for token in doc if token.pos_ == "VERB") / max(len(doc), 1),
            "unique_word_ratio": len(set(token.text.lower() for token in doc)) / max(len(doc), 1)
        }
        
        # Calculate quality score (0-1)
        quality_score = (
            min(metrics["sentence_count"] / 10, 1) * 0.2 +  # Good sections have multiple sentences
            min(metrics["avg_sentence_length"] / 15, 1) * 0.2 +  # Not too short sentences
            min(metrics["action_verb_ratio"] * 5, 1) * 0.4 +  # Using action verbs
            min(metrics["unique_word_ratio"] * 2, 1) * 0.2    # Diverse vocabulary
        )
        
        return quality_score
    
    def generate_features(self, resume_text, position, job_description=None):
        """
        Generate features for ML model from resume text
        These features can be used for more accurate scoring
        """
        # Get basic scores from parent class
        education_score, _ = self._check_education(resume_text)
        experience_score, _ = self._check_experience(resume_text)
        
        # Get keyword matches
        position_keywords = self._get_position_keywords(position)
        direct_matches, semantic_matches = self.semantic_keyword_match(resume_text, position_keywords)
        
        # Extract sections
        sections = self.extract_sections(resume_text)
        if sections is None:
            # Use regex as fallback
            edu_pattern = re.compile(r'(?:education|academic|degree|qualification)(?:[\s\:]+)(.*?)(?:experience|skills|work history|employment|projects|references|publications|$)', re.IGNORECASE | re.DOTALL)
            exp_pattern = re.compile(r'(?:experience|work history|employment|professional|career)(?:[\s\:]+)(.*?)(?:education|skills|certifications|references|projects|publications|$)', re.IGNORECASE | re.DOTALL)
            
            edu_match = edu_pattern.search(resume_text)
            exp_match = exp_pattern.search(resume_text)
            
            education_section = edu_match.group(1) if edu_match else ""
            experience_section = exp_match.group(1) if exp_match else ""
        else:
            education_section = sections.get("education", "")
            experience_section = sections.get("experience", "")
        
        # Calculate section quality scores
        education_quality = self.calculate_section_quality(education_section)
        experience_quality = self.calculate_section_quality(experience_section)
        
        # Document similarity if job description is provided
        if job_description:
            doc_similarity = self.calculate_document_similarity(resume_text, job_description)
        else:
            doc_similarity = 0.5  # Default middle value
        
        # Create feature dictionary
        features = {
            "education_score": education_score / 10,  # Normalize to 0-1 (changed from 15 to 10)
            "experience_score": experience_score / 30,  # Normalize to 0-1
            "keyword_match_ratio": len(direct_matches) / max(len(position_keywords), 1),
            "keyword_match_count": len(direct_matches),  # Added raw count for new scoring
            "semantic_match_count": len(semantic_matches),
            "education_quality": education_quality,
            "experience_quality": experience_quality,
            "document_similarity": doc_similarity,
            "resume_length": len(resume_text) / 5000  # Normalize to around 0-1
        }
        
        return features
    
    def predict_score_with_ml(self, features):
        """
        Use ML model to predict score based on features
        This provides more sophisticated scoring than the rule-based approach
        """
        if self.ml_model:
            try:
                # Convert features to array format expected by model
                feature_array = np.array([[
                    features["education_score"],
                    features["experience_score"],
                    features["keyword_match_ratio"],
                    features["semantic_match_count"] / 10,  # Normalize
                    features["education_quality"],
                    features["experience_quality"],
                    features["document_similarity"],
                    features["resume_length"]
                ]])
                
                # Predict score (0-1)
                predicted_score = self.ml_model.predict(feature_array)[0]
                
                # Scale to 0-100
                return int(predicted_score * 100)
            except Exception as e:
                print(f"Error predicting score with ML model: {e}")
        
        # If ML model not available or error occurred, calculate score manually
        # Modified to use 5 points per keyword match
        weighted_score = (
            features["education_score"] * 10 +  # Changed from 15 to 10
            features["experience_score"] * 30 +
            min(features["keyword_match_count"] * 5, 50) +  # 5 points per keyword up to 50
            features["semantic_match_count"] * 2 +
            features["education_quality"] * 5 +
            features["experience_quality"] * 10 +
            features["document_similarity"] * 10
        )
        
        # Ensure score is between 40-100
        return min(max(int(weighted_score), 40), 100)
    
    def suggest_improvements(self, resume_text, position, job_description=None, missing_keywords=None, section_scores=None):
        """
        Generate detailed improvement suggestions based on analysis
        Uses NLP to provide more specific and helpful recommendations
        """
        suggestions = []
        
        # Keyword suggestions
        if missing_keywords and len(missing_keywords) > 0:
            # Group missing keywords by category
            grouped_keywords = {}
            for keyword in missing_keywords:
                # Find keyword category
                category = "general"
                for industry in self.industry_keywords:
                    for cat in self.industry_keywords[industry]:
                        if keyword in self.industry_keywords[industry][cat]:
                            category = f"{industry}-{cat}"
                            break
                
                if category not in grouped_keywords:
                    grouped_keywords[category] = []
                grouped_keywords[category].append(keyword)
            
            # Generate suggestions by category
            for category, keywords in grouped_keywords.items():
                if len(keywords) > 3:
                    suggestion = f"Add {category.replace('-', ' ')} keywords such as: {', '.join(keywords[:3])}, and others."
                else:
                    suggestion = f"Include these missing {category.replace('-', ' ')} terms: {', '.join(keywords)}."
                suggestions.append(suggestion)
        
        # Education section improvements
        if section_scores and "education" in section_scores and section_scores["education"] < 0.6:
            suggestions.append("Enhance your education section by adding more details about degrees, graduation dates, relevant coursework, and academic achievements.")
        
        # Experience section improvements
        if section_scores and "experience" in section_scores and section_scores["experience"] < 0.6:
            suggestions.append("Strengthen your experience section with more quantifiable achievements, clear date formatting, and action verbs that highlight your specific contributions.")
        
        # Job description alignment
        if job_description and self.calculate_document_similarity(resume_text, job_description) < 0.5:
            suggestions.append("Your resume could be better aligned with the job description. Try to mirror key terms and phrases from the job posting.")
        
        # Check for action verbs
        if self.nlp:
            doc = self.nlp(resume_text)
            action_verbs = [token.text for token in doc if token.pos_ == "VERB" and token.dep_ == "ROOT"]
            if len(action_verbs) < 5:
                suggestions.append("Use more action verbs in your resume to highlight your achievements and responsibilities.")
        
        # Add general advice if no specific suggestions
        if not suggestions:
            suggestions.append("Consider tailoring your resume more specifically to the job you're applying for and highlighting your most relevant achievements with quantifiable metrics.")
        
            return suggestions
    
    def analyze_resume(self, resume_text, position, company=None, job_description=None):
        """
        Enhanced resume analysis using AI/ML techniques
        
        Args:
            resume_text (str): The extracted text from the resume
            position (str): The job position title
            company (str, optional): Company name
            job_description (str, optional): Job description text
            
        Returns:
            dict: Analysis results with score, matched/missing keywords, etc.
        """
        # Get basic analysis from parent class
        basic_analysis = super().analyze_resume(resume_text, position, company, job_description)
        
        # Get position-specific keywords
        position_keywords = self._get_position_keywords(position)
        
        # Enhanced keyword matching using NLP
        direct_matches, semantic_matches = self.semantic_keyword_match(resume_text, position_keywords)
        
        # Get additional skills using NLP
        extracted_skills = self.extract_skills_with_nlp(resume_text)
        
        # Extract sections and calculate quality scores
        sections = self.extract_sections(resume_text)
        section_scores = {}
        
        if sections:
            for section_name, section_text in sections.items():
                section_scores[section_name] = self.calculate_section_quality(section_text)
        else:
            # Use basic scores if section extraction failed
            section_scores = {
                "education": basic_analysis.get("education_score", 0) / 10,
                "experience": basic_analysis.get("experience_score", 0) / 30
            }
        
        # Document similarity if job description is provided
        if job_description:
            doc_similarity = self.calculate_document_similarity(resume_text, job_description)
            doc_similarity_score = int(doc_similarity * 100)
        else:
            doc_similarity = 0.5  # Default middle value
            doc_similarity_score = 50
        
        # Generate ML features
        features = self.generate_features(resume_text, position, job_description)
        
        # Calculate enhanced score using ML or weighted approach
        enhanced_score = self.predict_score_with_ml(features)
        
        # Generate improved suggestions
        missing_keywords = basic_analysis.get("missingKeywords", [])
        detailed_suggestions = self.suggest_improvements(
            resume_text, position, job_description, missing_keywords, section_scores
        )
        
        # Create enhanced analysis result
        enhanced_analysis = basic_analysis.copy()
        enhanced_analysis["score"] = enhanced_score
        enhanced_analysis["semanticMatches"] = [match[0] for match in semantic_matches]
        enhanced_analysis["semanticMatchDetails"] = semantic_matches  # Full details with similarity scores
        enhanced_analysis["extractedSkills"] = extracted_skills
        enhanced_analysis["sectionScores"] = section_scores
        
        if job_description:
            enhanced_analysis["jobDescriptionSimilarity"] = doc_similarity_score
        
        # Enhanced feedback
        additional_feedback = []
        
        if semantic_matches:
            additional_feedback.append(f"Found {len(semantic_matches)} semantic keyword matches that weren't exact matches.")
            
        if extracted_skills:
            additional_feedback.append(f"Identified {len(extracted_skills)} skills in your resume.")
            
        if job_description and doc_similarity_score > 70:
            additional_feedback.append(f"Your resume shows strong alignment with the job description (similarity score: {doc_similarity_score}%).")
        elif job_description:
            additional_feedback.append(f"Consider better aligning your resume with the job description (current similarity: {doc_similarity_score}%).")
        
        # Add section-specific feedback based on quality scores
        for section, score in section_scores.items():
            if score < 0.4:
                additional_feedback.append(f"Your {section} section could be significantly improved.")
            elif score < 0.7:
                additional_feedback.append(f"Your {section} section is good but could be enhanced.")
        
        enhanced_analysis["feedback"] += " " + " ".join(additional_feedback)
        
        # Replace basic improvement suggestions with more detailed ones
        enhanced_analysis["improvedContent"] = " ".join(detailed_suggestions)
        
        # Add visual report data for UI presentation
        enhanced_analysis["visualReport"] = {
            "keywordMatchRate": len(direct_matches) / max(len(position_keywords), 1) * 100,
            "sectionScores": section_scores,
            "overallScore": enhanced_score,
            "jobMatch": doc_similarity_score if job_description else None
        }
        
        return enhanced_analysis