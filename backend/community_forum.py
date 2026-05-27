import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class CommunityForum:
    def __init__(self):
        self.posts = []
        self.users = {}
        self.categories = {
            'career_advice': 'Career Development & Advice',
            'skill_development': 'Skill Development & Learning',
            'job_search': 'Job Search & Applications',
            'interview_prep': 'Interview Preparation',
            'workplace': 'Workplace & Professional Life',
            'technology': 'Technology & Industry Trends',
            'mentorship': 'Mentorship & Networking',
            'general': 'General Discussion'
        }
        self.load_forum_data()

    def load_forum_data(self):
        """Load forum data from storage"""
        # In a real implementation, this would load from a database
        # For now, we'll use in-memory storage
        pass

    def create_post(self, user_id: str, title: str, content: str, category: str, tags: List[str] = None) -> Dict:
        """Create a new forum post"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")

        post = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': title,
            'content': content,
            'category': category,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'views': 0,
            'likes': 0,
            'replies': [],
            'is_pinned': False,
            'is_locked': False
        }

        self.posts.append(post)
        return post

    def get_posts(self, category: str = None, limit: int = 20, offset: int = 0,
                  sort_by: str = 'created_at', tags: List[str] = None) -> List[Dict]:
        """Get forum posts with filtering and pagination"""
        filtered_posts = self.posts.copy()

        # Filter by category
        if category:
            filtered_posts = [p for p in filtered_posts if p['category'] == category]

        # Filter by tags
        if tags:
            filtered_posts = [p for p in filtered_posts if any(tag in p['tags'] for tag in tags)]

        # Sort posts
        reverse_sort = sort_by in ['created_at', 'updated_at', 'views', 'likes']
        filtered_posts.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse_sort)

        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        return filtered_posts[start_idx:end_idx]

    def get_post(self, post_id: str) -> Optional[Dict]:
        """Get a specific post by ID"""
        for post in self.posts:
            if post['id'] == post_id:
                # Increment view count
                post['views'] += 1
                return post
        return None

    def update_post(self, post_id: str, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update a post"""
        post = self.get_post(post_id)
        if not post or post['user_id'] != user_id:
            return None

        # Update allowed fields
        allowed_updates = ['title', 'content', 'tags']
        for field in allowed_updates:
            if field in updates:
                post[field] = updates[field]

        post['updated_at'] = datetime.now().isoformat()
        return post

    def delete_post(self, post_id: str, user_id: str) -> bool:
        """Delete a post"""
        for i, post in enumerate(self.posts):
            if post['id'] == post_id and post['user_id'] == user_id:
                del self.posts[i]
                return True
        return False

    def add_reply(self, post_id: str, user_id: str, content: str) -> Optional[Dict]:
        """Add a reply to a post"""
        post = self.get_post(post_id)
        if not post or post.get('is_locked', False):
            return None

        reply = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'content': content,
            'created_at': datetime.now().isoformat(),
            'likes': 0
        }

        post['replies'].append(reply)
        post['updated_at'] = datetime.now().isoformat()
        return reply

    def like_post(self, post_id: str, user_id: str) -> bool:
        """Like or unlike a post"""
        post = self.get_post(post_id)
        if not post:
            return False

        # In a real implementation, track user likes
        post['likes'] += 1
        return True

    def like_reply(self, post_id: str, reply_id: str, user_id: str) -> bool:
        """Like or unlike a reply"""
        post = self.get_post(post_id)
        if not post:
            return False

        for reply in post['replies']:
            if reply['id'] == reply_id:
                reply['likes'] += 1
                return True
        return False

    def search_posts(self, query: str, category: str = None, limit: int = 20) -> List[Dict]:
        """Search posts by content"""
        query_lower = query.lower()
        matching_posts = []

        for post in self.posts:
            if category and post['category'] != category:
                continue

            # Search in title, content, and tags
            searchable_text = f"{post['title']} {post['content']} {' '.join(post['tags'])}".lower()

            if query_lower in searchable_text:
                matching_posts.append(post)

        # Sort by relevance (simple implementation)
        return matching_posts[:limit]

    def get_popular_tags(self, limit: int = 10) -> List[Dict]:
        """Get most popular tags"""
        tag_counts = {}
        for post in self.posts:
            for tag in post['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        popular_tags = [
            {'tag': tag, 'count': count}
            for tag, count in tag_counts.items()
        ]

        return sorted(popular_tags, key=lambda x: x['count'], reverse=True)[:limit]

    def get_forum_stats(self) -> Dict:
        """Get forum statistics"""
        total_posts = len(self.posts)
        total_replies = sum(len(post['replies']) for post in self.posts)
        total_views = sum(post['views'] for post in self.posts)
        total_likes = sum(post['likes'] for post in self.posts)

        category_stats = {}
        for category in self.categories.keys():
            category_posts = [p for p in self.posts if p['category'] == category]
            category_stats[category] = {
                'posts': len(category_posts),
                'replies': sum(len(p['replies']) for p in category_posts)
            }

        return {
            'total_posts': total_posts,
            'total_replies': total_replies,
            'total_views': total_views,
            'total_likes': total_likes,
            'categories': category_stats,
            'active_users': len(set(post['user_id'] for post in self.posts))
        }

    def get_user_posts(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get posts by a specific user"""
        user_posts = [post for post in self.posts if post['user_id'] == user_id]
        return sorted(user_posts, key=lambda x: x['created_at'], reverse=True)[:limit]

    def report_post(self, post_id: str, user_id: str, reason: str) -> bool:
        """Report a post for moderation"""
        post = self.get_post(post_id)
        if not post:
            return False

        # In a real implementation, this would flag the post for moderation
        # For now, just log the report
        print(f"Post {post_id} reported by {user_id} for: {reason}")
        return True

    def pin_post(self, post_id: str, admin_user_id: str) -> bool:
        """Pin or unpin a post (admin function)"""
        post = self.get_post(post_id)
        if not post:
            return False

        # In a real implementation, check if user is admin
        post['is_pinned'] = not post.get('is_pinned', False)
        return True

    def lock_post(self, post_id: str, admin_user_id: str) -> bool:
        """Lock or unlock a post (admin function)"""
        post = self.get_post(post_id)
        if not post:
            return False

        # In a real implementation, check if user is admin
        post['is_locked'] = not post.get('is_locked', False)
        return True

    def get_featured_posts(self, limit: int = 5) -> List[Dict]:
        """Get featured/pinned posts"""
        featured = [post for post in self.posts if post.get('is_pinned', False)]
        return sorted(featured, key=lambda x: x['created_at'], reverse=True)[:limit]

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent forum activity"""
        all_activity = []

        # Add posts
        for post in self.posts:
            all_activity.append({
                'type': 'post',
                'id': post['id'],
                'title': post['title'],
                'user_id': post['user_id'],
                'timestamp': post['created_at'],
                'category': post['category']
            })

            # Add replies
            for reply in post['replies']:
                all_activity.append({
                    'type': 'reply',
                    'post_id': post['id'],
                    'post_title': post['title'],
                    'user_id': reply['user_id'],
                    'timestamp': reply['created_at']
                })

        # Sort by timestamp
        all_activity.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_activity[:limit]

    def get_user_reputation(self, user_id: str) -> Dict:
        """Calculate user reputation based on activity"""
        user_posts = [p for p in self.posts if p['user_id'] == user_id]
        total_replies = sum(len(p['replies']) for p in self.posts if p['user_id'] == user_id)
        total_likes_received = sum(p['likes'] for p in user_posts)

        # Simple reputation calculation
        reputation_score = len(user_posts) * 10 + total_replies * 2 + total_likes_received

        return {
            'score': reputation_score,
            'level': self.get_reputation_level(reputation_score),
            'posts_count': len(user_posts),
            'replies_count': total_replies,
            'likes_received': total_likes_received
        }

    def get_reputation_level(self, score: int) -> str:
        """Get reputation level based on score"""
        if score >= 1000:
            return 'Expert'
        elif score >= 500:
            return 'Advanced'
        elif score >= 200:
            return 'Intermediate'
        elif score >= 50:
            return 'Contributor'
        else:
            return 'Newcomer'