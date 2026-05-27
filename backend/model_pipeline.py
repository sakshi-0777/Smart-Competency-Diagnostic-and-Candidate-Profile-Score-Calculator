import pandas as pd
import numpy as np
import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import re

from pathlib import Path

# -------------------------------
# 🔹 LOAD MODEL (ONCE)
# -------------------------------
EMBED_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


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
        print("❌ PDF Extraction Error:", e)
        return ""


# -------------------------------
# 🔹 BUILD JOB INDEX
# -------------------------------
def build_job_index(
    job_df,
    batch_size=64,
    cache_path="data/job_embs.npy",
    progress_callback=None
):
    cache_path = os.path.abspath(cache_path)
    try:
        job_df.columns = [c.strip().lower() for c in job_df.columns]

        # Handle different column naming conventions
        if "job_title" in job_df.columns:
            title_col = "job_title"
        elif "job title" in job_df.columns:
            title_col = "job title"
        else:
            # Skip the first column if it's unnamed/index
            title_col = job_df.columns[1] if job_df.columns[0].startswith("unnamed") else job_df.columns[0]

        if "job_description" in job_df.columns:
            desc_col = "job_description"
        elif "job description" in job_df.columns:
            desc_col = "job description"
        else:
            desc_col = job_df.columns[2] if len(job_df.columns) > 2 and job_df.columns[0].startswith("unnamed") else job_df.columns[1]

        texts = (
            job_df[title_col].fillna("").astype(str) +
            ". " +
            job_df[desc_col].fillna("").astype(str)
        ).tolist()

        # ---------------- CACHE ---------------- #
        if os.path.exists(cache_path):
            embs = np.load(cache_path)
            print(" Loaded cached embeddings")

            if progress_callback:
                progress_callback(len(texts), len(texts))

        else:
            print(f"Encoding {len(texts)} jobs...")
            all_embs = []

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                batch_embs = EMBED_MODEL.encode(
                    batch,
                    convert_to_numpy=True,
                    show_progress_bar=False
                )

                all_embs.append(batch_embs)

                if progress_callback:
                    progress_callback(i + len(batch), len(texts))

            embs = np.vstack(all_embs)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            np.save(cache_path, embs)

        # ---------------- FAISS ---------------- #
        faiss.normalize_L2(embs)
        index = faiss.IndexFlatIP(embs.shape[1])
        index.add(embs)

        return index, embs

    except Exception as e:
        print("Job Index Error:", e)
        raise e


# -------------------------------
# 🔹 JOB MATCHING
# -------------------------------
def find_similar_jobs(resume_text, job_df, index, job_embs, topk=5):
    try:
        resume_text = clean_text(resume_text)

        if not resume_text or index is None:
            return []

        q = EMBED_MODEL.encode([resume_text], convert_to_numpy=True)
        faiss.normalize_L2(q)

        D, I = index.search(q, topk)

        results = []

        for score, idx in zip(D[0], I[0]):
            row = job_df.iloc[idx]

            job_title = str(
                row.get("job_title") or row.get("job title") or row.get("job_title") or row.get("Job_Title") or "N/A"
            )
            job_desc = str(
                row.get("job_description") or row.get("job description") or row.get("Job_Description") or ""
            )

            #  keyword boost
            keyword_overlap = sum(
                1 for word in resume_text.split()
                if word in job_desc.lower()
            )

            final_score = float(score) + 0.01 * keyword_overlap

            results.append({
                "title": job_title,
                "description": (job_desc[:200] + "...") if len(job_desc) > 200 else job_desc,
                "score": round(final_score, 3)
            })

        return sorted(results, key=lambda x: -x["score"])

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


# -------------------------------
# 🔹 COURSE RECOMMENDATION
# -------------------------------
def recommend_courses(keywords, courses_df):
    try:
        if not keywords:
            return []

        keyword_list = [k["keyword"] for k in keywords]

        courses_df = courses_df.copy()
        courses_df.columns = [c.strip().lower() for c in courses_df.columns]

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

        cache_path = os.path.abspath("data/course_embs.npy")

        if os.path.exists(cache_path):
            course_embs = np.load(cache_path)
            print("Loaded cached course embeddings")
        else:
            course_embs = EMBED_MODEL.encode(texts, convert_to_numpy=True)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            np.save(cache_path, course_embs)

        query = EMBED_MODEL.encode(
            [" ".join(keyword_list)],
            convert_to_numpy=True
        )

        scores = cosine_similarity(query, course_embs)[0]

        courses_df["score"] = scores

        results = courses_df.sort_values("score", ascending=False).head(10)

        return [
            {
                "title": row[course_name_col],
                "platform": row[platform_col] if platform_col else "Unknown",
                "url": row[course_url_col] if course_url_col else "",
                "score": round(float(row["score"]), 3)
            }
            for _, row in results.iterrows()
        ]

    except Exception as e:
        print("Course Recommendation Error:", e)
        return []