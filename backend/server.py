import os
import uuid
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import re

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.codelearning_db

# Pydantic models
class AIConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    user_id: str

class RepoAnalysis(BaseModel):
    repo_url: str
    user_id: str

class Flashcard(BaseModel):
    id: str
    front: str
    back: str
    category: str
    difficulty: str
    code_snippet: Optional[str]
    file_path: Optional[str]

class Analysis(BaseModel):
    id: str
    repo_url: str
    user_id: str
    status: str
    created_at: datetime
    flashcards: List[Flashcard]
    total_files: int
    languages: List[str]

# Available AI models
AI_MODELS = {
    "openai": {
        "gpt-4o": "GPT-4o",
        "gpt-4.1": "GPT-4.1", 
        "gpt-4o-mini": "GPT-4o Mini",
        "o3-mini": "O3 Mini"
    },
    "anthropic": {
        "claude-sonnet-4-20250514": "Claude Sonnet 4",
        "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet",
        "claude-3-5-haiku-20241022": "Claude 3.5 Haiku"
    },
    "gemini": {
        "gemini-2.0-flash": "Gemini 2.0 Flash",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gemini-1.5-flash": "Gemini 1.5 Flash"
    }
}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "AI Code Learning System is running"}

@app.get("/api/ai-models")
async def get_available_models():
    """Get all available AI models"""
    return AI_MODELS

@app.post("/api/ai-config")
async def save_ai_config(config: AIConfig):
    """Save AI configuration for a user"""
    try:
        # Validate model exists
        if config.provider not in AI_MODELS or config.model not in AI_MODELS[config.provider]:
            raise HTTPException(status_code=400, detail="Invalid AI model selection")
        
        # Save to database
        config_doc = {
            "user_id": config.user_id,
            "provider": config.provider,
            "model": config.model,
            "api_key": config.api_key,
            "created_at": datetime.now()
        }
        
        await db.ai_configs.replace_one(
            {"user_id": config.user_id}, 
            config_doc, 
            upsert=True
        )
        
        return {"message": "AI configuration saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")

@app.get("/api/ai-config/{user_id}")
async def get_ai_config(user_id: str):
    """Get AI configuration for a user"""
    try:
        config = await db.ai_configs.find_one({"user_id": user_id})
        if not config:
            return {"configured": False}
        
        return {
            "configured": True,
            "provider": config["provider"],
            "model": config["model"],
            "model_name": AI_MODELS[config["provider"]][config["model"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

async def fetch_github_repo(repo_url: str) -> Dict:
    """Fetch repository content from GitHub"""
    try:
        # Extract owner and repo name from URL
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url.replace('.git', ''))
        if not match:
            raise ValueError("Invalid GitHub repository URL")
        
        owner, repo = match.groups()
        
        # GitHub API to get repository tree
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise ValueError("Repository not found or not accessible")
                
                tree_data = await response.json()
                
                # Filter for code files
                code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift', '.kt'}
                files = []
                
                for item in tree_data['tree']:
                    if item['type'] == 'blob':
                        ext = os.path.splitext(item['path'])[1].lower()
                        if ext in code_extensions:
                            # Fetch file content
                            content_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{item['path']}"
                            async with session.get(content_url) as file_response:
                                if file_response.status == 200:
                                    file_data = await file_response.json()
                                    if file_data.get('encoding') == 'base64':
                                        import base64
                                        content = base64.b64decode(file_data['content']).decode('utf-8', errors='ignore')
                                        files.append({
                                            'path': item['path'],
                                            'content': content[:5000],  # Limit content size
                                            'language': ext[1:] if ext else 'text'
                                        })
                
                return {
                    'owner': owner,
                    'repo': repo,
                    'files': files[:20],  # Limit to first 20 files for MVP
                    'total_files': len(files)
                }
                
    except Exception as e:
        raise ValueError(f"Failed to fetch repository: {str(e)}")

async def analyze_with_ai(files: List[Dict], config: Dict) -> List[Flashcard]:
    """Analyze code files with AI to generate flashcards"""
    try:
        # This would normally use the emergentintegrations library
        # For now, creating sample flashcards based on file analysis
        flashcards = []
        
        # Group files by language
        languages = {}
        for file in files:
            lang = file['language']
            if lang not in languages:
                languages[lang] = []
            languages[lang].append(file)
        
        # Generate flashcards for each language
        for lang, lang_files in languages.items():
            # Architecture overview flashcard
            flashcards.append(Flashcard(
                id=str(uuid.uuid4()),
                front=f"What is the overall architecture of this {lang.upper()} application?",
                back=f"This application uses {lang.upper()} with {len(lang_files)} files. Key components include: {', '.join([f['path'].split('/')[-1] for f in lang_files[:3]])}",
                category="Architecture",
                difficulty="Medium",
                code_snippet=lang_files[0]['content'][:200] if lang_files else None,
                file_path=lang_files[0]['path'] if lang_files else None
            ))
            
            # File-specific flashcards
            for file in lang_files[:3]:  # Limit to 3 files per language
                file_name = file['path'].split('/')[-1]
                flashcards.append(Flashcard(
                    id=str(uuid.uuid4()),
                    front=f"What is the purpose of {file_name}?",
                    back=f"This file ({file['path']}) contains {lang} code and appears to handle core functionality. It's part of the main application structure.",
                    category=f"{lang.upper()} Files",
                    difficulty="Easy",
                    code_snippet=file['content'][:300],
                    file_path=file['path']
                ))
        
        return flashcards
        
    except Exception as e:
        raise ValueError(f"AI analysis failed: {str(e)}")

async def process_repository_analysis(repo_url: str, user_id: str, analysis_id: str):
    """Background task to process repository analysis"""
    try:
        # Update status to processing
        await db.analyses.update_one(
            {"id": analysis_id},
            {"$set": {"status": "processing"}}
        )
        
        # Get user's AI configuration
        config = await db.ai_configs.find_one({"user_id": user_id})
        if not config:
            raise ValueError("AI configuration not found")
        
        # Fetch repository
        repo_data = await fetch_github_repo(repo_url)
        
        # Analyze with AI and generate flashcards
        flashcards = await analyze_with_ai(repo_data['files'], config)
        
        # Update analysis with results
        await db.analyses.update_one(
            {"id": analysis_id},
            {"$set": {
                "status": "completed",
                "flashcards": [card.dict() for card in flashcards],
                "total_files": repo_data['total_files'],
                "languages": list(set([f['language'] for f in repo_data['files']]))
            }}
        )
        
    except Exception as e:
        await db.analyses.update_one(
            {"id": analysis_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )

@app.post("/api/analyze-repository")
async def analyze_repository(analysis: RepoAnalysis, background_tasks: BackgroundTasks):
    """Start repository analysis"""
    try:
        # Check if user has AI configuration
        config = await db.ai_configs.find_one({"user_id": analysis.user_id})
        if not config:
            raise HTTPException(status_code=400, detail="AI configuration required. Please configure AI model first.")
        
        # Create analysis record
        analysis_id = str(uuid.uuid4())
        analysis_doc = {
            "id": analysis_id,
            "repo_url": analysis.repo_url,
            "user_id": analysis.user_id,
            "status": "queued",
            "created_at": datetime.now(),
            "flashcards": [],
            "total_files": 0,
            "languages": []
        }
        
        await db.analyses.insert_one(analysis_doc)
        
        # Start background processing
        background_tasks.add_task(process_repository_analysis, analysis.repo_url, analysis.user_id, analysis_id)
        
        return {"analysis_id": analysis_id, "status": "queued", "message": "Repository analysis started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis status and results"""
    try:
        analysis = await db.analyses.find_one({"id": analysis_id})
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "id": analysis["id"],
            "repo_url": analysis["repo_url"],
            "status": analysis["status"],
            "created_at": analysis["created_at"],
            "flashcards": analysis.get("flashcards", []),
            "total_files": analysis.get("total_files", 0),
            "languages": analysis.get("languages", []),
            "error": analysis.get("error")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")

@app.get("/api/user-analyses/{user_id}")
async def get_user_analyses(user_id: str):
    """Get all analyses for a user"""
    try:
        analyses = await db.analyses.find(
            {"user_id": user_id}, 
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        
        return {"analyses": analyses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analyses: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)