from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

import models, database
from database import engine, get_db
from pipeline import fetch_raw_news, process_with_llm

# Initialize Database - this creates the sqlite file if it doesn't exist
models.Base.metadata.create_all(bind=engine)

async def sync_news_job():
    db = database.SessionLocal()
    try:
        print("\n--- Starting Background News Sync ---")
        raw_news = fetch_raw_news()
        
        # Check what we already have in the database to avoid duplicates
        existing_titles = {a.title for a in db.query(models.Article.title).all()}
        new_articles = [a for a in raw_news if a["title"] not in existing_titles]
        
        if new_articles:
            print(f"Processing {len(new_articles)} new articles with AI...")
            processed = process_with_llm(new_articles)
            
            for item in processed:
                article_obj = models.Article(
                    title=item.get("title", "Unknown Title"),
                    url=item.get("url", ""),
                    source=item.get("source", "Unknown"),
                    summary=item.get("summary", ""),
                    topic=item.get("topic", "Unclustered"),
                    sentiment=item.get("sentiment", "Neutral")
                )
                db.add(article_obj)
            db.commit()
            print(f"Successfully saved {len(processed)} articles to database.")
        else:
            print("No new articles to process. Everything is up to date.")
    except Exception as e:
        print(f"Error in background sync: {e}")
    finally:
        db.close()
        print("--- Sync Complete ---\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    scheduler = AsyncIOScheduler()
    scheduler.add_job(sync_news_job, 'interval', minutes=30) # Runs every 30 mins
    scheduler.start()
    
    # Run the job once immediately so you have data right away
    await sync_news_job() 
    
    yield
    
    # This runs when the server stops
    scheduler.shutdown()

# Create the FastAPI app
app = FastAPI(
    title="Multi-Source News Digest API", 
    description="API for clustered and summarized news digests.",
    lifespan=lifespan
)

# Allow the frontend to communicate with this backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you'd lock this down to your frontend's URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.get("/digest")
def get_digest(db: Session = Depends(get_db)):
    articles = db.query(models.Article).all()
    
    # Group the articles by their AI-assigned topic
    digest = {}
    for a in articles:
        if a.topic not in digest:
            digest[a.topic] = []
        digest[a.topic].append({
            "title": a.title,
            "url": a.url,
            "source": a.source,
            "summary": a.summary,
            "sentiment": a.sentiment
        })
    return digest

@app.get("/topic/{name}")
def get_by_topic(name: str, db: Session = Depends(get_db)):
    # Fetch articles filtered by a specific topic
    return db.query(models.Article).filter(models.Article.topic.ilike(f"%{name}%")).all()