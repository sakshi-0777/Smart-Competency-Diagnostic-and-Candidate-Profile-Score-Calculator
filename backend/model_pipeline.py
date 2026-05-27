import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re

from pathlib import Path

# Memory-optimized: No FAISS, no sentence-transformers
# Using lightweight TF-IDF + cosine similarity instead


# -------------------------------
# 🔹 TEXT CLEANING
# -------------------------------
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    return text.strip()


# -------------------------------
# 🔹 PDF TEXT EXTRACTION
# -------------------------------
def extract_text_from_pdf(file_stream):
    try:
        reader = PdfReader(file_stream)
        text = []

        for page in reader.pages:
            content = page.extract_text()
            if content:
                text.append(content)

        return clean_text("\n".join(text))

    except Exception as e:
        print("PDF Extraction Error:", e)
        return ""


# Memory-optimized job index using TF-IDF
def build_job_index(
    job_df,
    batch_size=64,
    cache_path="data/job_embs.npy",
    progress_callback=None
):
    """Build lightweight TF-IDF index for job matching (replaces FAISS)"""
    try:
        job_df.columns = [c.strip().lower() for c in job_df.columns]

        # Handle different column naming conventions
        if "job_title" in job_df.columns:
            title_col = "job_title"
        elif "job title" in job_df.columns:
            title_col = "job title"
        else:
            title_col = job_df.columns[1] if job_df.columns[0].startswith("unnamed") else job_df.columns[0]

        if "job_description" in job_df.columns:
            desc_col = "job_description"
        elif "job description" in job_df.columns:
            desc_col = "job description"
        else:
            desc_col = job_df.columns[2] if len(job_df.columns) > 2 and job_df.columns[0].startswith("unnamed") else job_df.columns[1]

        # Limit to first 1000 jobs to save memory on Render
        if len(job_df) > 1000:
            job_df = job_df.head(1000)
            print(f"Limited jobs to 1000 for memory efficiency")

        texts = (
            job_df[title_col].fillna("").astype(str) +
            ". " +
            job_df[desc_col].fillna("").astype(str)
        ).tolist()

        print(f"Building TF-IDF index for {len(texts)} jobs...")
        
        # Create lightweight TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=100,  # Limited features for memory
            stop_words="english",
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=1
        )
        
        # Fit and transform
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        if progress_callback:
            progress_callback(len(texts), len(texts))

        # Return as tuple: (vectorizer, tfidf_matrix, job_df indices)
        # This replaces (index, embs) from FAISS approach
        return vectorizer, tfidf_matrix, job_df.reset_index(drop=True)

    except Exception as e:
        print("Job Index Error:", e)
        raise e


# Memory-optimized job matching using TF-IDF
def find_similar_jobs(resume_text, job_df, index, job_embs, topk=5):
    """Find similar jobs using TF-IDF similarity (memory-efficient)"""
    try:
        resume_text = clean_text(resume_text)

        if not resume_text:
            return []

        # index is now the TfidfVectorizer
        # job_embs is now the TF-IDF sparse matrix
        # job_df is the actual dataframe
        
        vectorizer = index
        tfidf_matrix = job_embs
        
        # Transform resume to same TF-IDF space
        resume_tfidf = vectorizer.transform([resume_text])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(resume_tfidf, tfidf_matrix)[0]
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-topk:][::-1]
        
        results = []
        
        for idx in top_indices:
            score = float(similarities[idx])
            
            if score < 0.01:  # Skip very low scores
                continue
                
            row = job_df.iloc[idx]
            
            job_title = str(
                row.get("job_title") or row.get("job title") or "N/A"
            )
            job_desc = str(
                row.get("job_description") or row.get("job description") or ""
            )
            
            results.append({
                "title": job_title,
                "description": (job_desc[:200] + "...") if len(job_desc) > 200 else job_desc,
                "score": round(score * 100, 2)  # Convert to percentage
            })
        
        return results

    except Exception as e:
        print("Job Matching Error:", e)
        return []


# -------------------------------
# 🔹 KEYWORD EXTRACTION
# -------------------------------
def extract_keywords_from_text(text, top_k=10):
    try:
        text = clean_text(text)

        if not text:
            return []

        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform([text])

        scores = zip(vectorizer.get_feature_names_out(), X.toarray()[0])
        sorted_words = sorted(scores, key=lambda x: x[1], reverse=True)

        return [{"keyword": w, "score": round(float(s), 3)} for w, s in sorted_words[:top_k]]

    except Exception as e:
        print("Keyword Extraction Error:", e)
        return []


# Memory-optimized course recommendation using TF-IDF
def recommend_courses(keywords, courses_df):
    """Recommend courses based on keywords (memory-efficient)"""
    try:
        if not keywords or courses_df is None or len(courses_df) == 0:
            return []

        keyword_list = [k["keyword"] for k in keywords]
        
        if not keyword_list:
            return []

        courses_df = courses_df.copy()
        courses_df.columns = [c.strip().lower() for c in courses_df.columns]

        # Limit to first 500 courses for memory efficiency
        if len(courses_df) > 500:
            courses_df = courses_df.head(500)

        course_name_col = next((c for c in courses_df.columns if c in ["course name", "course_name"]), None)
        course_desc_col = next((c for c in courses_df.columns if c in ["course description", "course_description"]), None)
        course_url_col = next((c for c in courses_df.columns if c in ["course url", "course_url"]), None)
        platform_col = next((c for c in courses_df.columns if c in ["university", "provider", "platform"]), None)

        if course_name_col is None or course_desc_col is None:
            return []

        texts = (
            courses_df[course_name_col].fillna("").astype(str) +
            " " +
            courses_df[course_desc_col].fillna("").astype(str)
        ).tolist()

        # Create lightweight TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=50,  # Limited for memory
            stop_words="english",
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=1
        )
        
        # Fit and transform course texts
        course_tfidf = vectorizer.fit_transform(texts)
        
        # Transform keywords query
        query_text = " ".join(keyword_list)
        query_tfidf = vectorizer.transform([query_text])
        
        # Calculate similarity scores
        scores = cosine_similarity(query_tfidf, course_tfidf)[0]
        
        courses_df["score"] = scores
        
        results = courses_df.sort_values("score", ascending=False).head(10)

        return [
            {
                "title": row[course_name_col],
                "platform": row[platform_col] if platform_col else "Unknown",
                "url": row[course_url_col] if course_url_col else "",
                "score": round(float(row["score"]) * 100, 2)
            }
            for _, row in results.iterrows()
            if row["score"] > 0
        ]

    except Exception as e:
        print("Course Recommendation Error:", e)
        return []