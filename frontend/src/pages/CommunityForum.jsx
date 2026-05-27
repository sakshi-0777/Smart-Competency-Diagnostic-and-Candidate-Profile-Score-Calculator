import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  ArrowLeft,
  ArrowRight,
  Heart,
  Loader2,
  MessageCircle,
  Plus,
  Send,
  X
} from 'lucide-react';

const CommunityForum = () => {
  const { token } = useAuth();
  const [posts, setPosts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPost, setSelectedPost] = useState(null);
  const [newPost, setNewPost] = useState({ title: '', content: '', category: '' });
  const [newReply, setNewReply] = useState('');
  const [loading, setLoading] = useState(true);
  const [showNewPostForm, setShowNewPostForm] = useState(false);

  const loadPosts = async (category = selectedCategory) => {
    setLoading(true);
    try {
      const url = category === 'all'
        ? 'http://localhost:5000/forum/posts'
        : `http://localhost:5000/forum/posts?category=${category}`;

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setPosts(data.posts);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    let isMounted = true;

    fetch('http://localhost:5000/forum/categories', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(response => response.json())
      .then(data => {
        if (isMounted) {
          setCategories(data.categories || []);
        }
      })
      .catch(error => console.error('Error fetching categories:', error));

    const url = selectedCategory === 'all'
      ? 'http://localhost:5000/forum/posts'
      : `http://localhost:5000/forum/posts?category=${selectedCategory}`;

    fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
    })
      .then(response => response.json())
      .then(data => {
        if (isMounted) {
          setPosts(data.posts || []);
          setLoading(false);
        }
      })
      .catch(error => {
        console.error('Error fetching posts:', error);
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [selectedCategory, token]);

  const handleCreatePost = async () => {
    try {
      const response = await fetch('http://localhost:5000/forum/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newPost)
      });
      const data = await response.json();
      if (data.success) {
        setNewPost({ title: '', content: '', category: '' });
        setShowNewPostForm(false);
        loadPosts();
      }
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };

  const handleCreateReply = async (postId) => {
    if (!newReply.trim()) return;

    try {
      const response = await fetch(`http://localhost:5000/forum/posts/${postId}/replies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ content: newReply })
      });
      const data = await response.json();
      if (data.success) {
        setNewReply('');
        loadPosts();
        if (selectedPost) {
          setSelectedPost(prev => ({
            ...prev,
            replies: data.replies
          }));
        }
      }
    } catch (error) {
      console.error('Error creating reply:', error);
    }
  };

  const handleLikePost = async (postId) => {
    try {
      const response = await fetch(`http://localhost:5000/forum/posts/${postId}/like`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        loadPosts();
      }
    } catch (error) {
      console.error('Error liking post:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading community forum...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold">Community Forum</h1>
            <button
              onClick={() => setShowNewPostForm(!showNewPostForm)}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition inline-flex items-center gap-2"
            >
              {showNewPostForm ? <X className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
              <span>{showNewPostForm ? 'Cancel' : 'New Post'}</span>
            </button>
          </div>

          {/* Category Filter */}
          <div className="mb-6">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-4 py-2 rounded-lg transition ${
                  selectedCategory === 'all'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                All Posts
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`px-4 py-2 rounded-lg transition ${
                    selectedCategory === category.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>

          {/* New Post Form */}
          {showNewPostForm && (
            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Create New Post</h2>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Post Title"
                  value={newPost.title}
                  onChange={(e) => setNewPost(prev => ({ ...prev, title: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <select
                  value={newPost.category}
                  onChange={(e) => setNewPost(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select Category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>{category.name}</option>
                  ))}
                </select>
                <textarea
                  placeholder="Post Content"
                  value={newPost.content}
                  onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
                  rows={6}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="flex space-x-4">
                  <button
                    onClick={handleCreatePost}
                    disabled={!newPost.title || !newPost.content || !newPost.category}
                    className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition inline-flex items-center gap-2"
                  >
                    <Send className="h-4 w-4" />
                    <span>Create Post</span>
                  </button>
                  <button
                    onClick={() => setShowNewPostForm(false)}
                    className="bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition inline-flex items-center gap-2"
                  >
                    <X className="h-4 w-4" />
                    <span>Cancel</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Posts List */}
          {!selectedPost ? (
            <div className="space-y-4">
              {posts.map((post) => (
                <div key={post.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition cursor-pointer">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1" onClick={() => setSelectedPost(post)}>
                      <h3 className="text-xl font-semibold mb-2 hover:text-blue-600">{post.title}</h3>
                      <p className="text-gray-600 mb-3 line-clamp-2">{post.content}</p>
                    </div>
                    <div className="flex items-center space-x-4 ml-4">
                      <button
                        onClick={() => handleLikePost(post.id)}
                        className={`flex items-center space-x-1 px-3 py-1 rounded transition ${
                          post.user_liked ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        <Heart className="h-4 w-4" />
                        <span>{post.likes}</span>
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-4">
                      <span>By {post.author}</span>
                      <span>{formatDate(post.created_at)}</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {post.category_name}
                      </span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="inline-flex items-center gap-1"><MessageCircle className="h-4 w-4" /> {post.replies_count} replies</span>
                      <button
                        onClick={() => setSelectedPost(post)}
                        className="text-blue-500 hover:text-blue-700 inline-flex items-center gap-1"
                      >
                        <span>View Discussion</span>
                        <ArrowRight className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {posts.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-gray-500 text-lg">No posts found in this category.</p>
                  <button
                  onClick={() => setShowNewPostForm(true)}
                    className="mt-4 text-blue-500 hover:text-blue-700 inline-flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Be the first to post!</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* Post Detail View */
            <div>
              <div className="flex items-center justify-between mb-6">
                <button
                  onClick={() => setSelectedPost(null)}
                  className="text-blue-500 hover:text-blue-700 font-medium inline-flex items-center gap-2"
                >
                  <ArrowLeft className="h-5 w-5" />
                  <span>Back to Posts</span>
                </button>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => handleLikePost(selectedPost.id)}
                    className={`flex items-center space-x-1 px-3 py-1 rounded transition ${
                      selectedPost.user_liked ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    <Heart className="h-4 w-4" />
                    <span>{selectedPost.likes}</span>
                  </button>
                </div>
              </div>

              {/* Original Post */}
              <div className="bg-gray-50 rounded-lg p-6 mb-8">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold mb-2">{selectedPost.title}</h2>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>By {selectedPost.author}</span>
                      <span>{formatDate(selectedPost.created_at)}</span>
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {selectedPost.category_name}
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-gray-700 leading-relaxed">{selectedPost.content}</p>
              </div>

              {/* Replies */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold mb-4">Replies ({selectedPost.replies?.length || 0})</h3>
                <div className="space-y-4">
                  {selectedPost.replies?.map((reply) => (
                    <div key={reply.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{reply.author}</span>
                          <span className="text-sm text-gray-500">{formatDate(reply.created_at)}</span>
                        </div>
                      </div>
                      <p className="text-gray-700">{reply.content}</p>
                    </div>
                  ))}

                  {(!selectedPost.replies || selectedPost.replies.length === 0) && (
                    <div className="text-center py-8 text-gray-500">
                      No replies yet. Be the first to reply!
                    </div>
                  )}
                </div>
              </div>

              {/* Reply Form */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Add a Reply</h3>
                <textarea
                  placeholder="Write your reply..."
                  value={newReply}
                  onChange={(e) => setNewReply(e.target.value)}
                  rows={4}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
                />
                <button
                  onClick={() => handleCreateReply(selectedPost.id)}
                  disabled={!newReply.trim()}
                  className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition inline-flex items-center gap-2"
                >
                  <Send className="h-4 w-4" />
                  <span>Post Reply</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommunityForum;
