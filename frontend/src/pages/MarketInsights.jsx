import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from "../config";
import {
  Bell,
  Building2,
  Calendar,
  DollarSign,
  Lightbulb,
  Loader2,
  MapPin,
  Target,
  TrendingUp
} from 'lucide-react';

const MarketInsights = () => {
  const { token } = useAuth();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');

  useEffect(() => {
    fetchInsights();
  }, [selectedCategory, selectedLocation]);

  const fetchInsights = async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      if (selectedCategory !== 'all') params.append('category', selectedCategory);
      if (selectedLocation !== 'all') params.append('location', selectedLocation);

      const response = await fetch(`${API_BASE_URL}/market-insights?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to load market insights');
      }

      setInsights(data.insights || data);
    } catch (error) {
      console.error('Error fetching insights:', error);
      setError(error.message || 'Unable to load market insights');
      setInsights(null);
    }
    setLoading(false);
  };

  const trendingJobs = insights?.trending_jobs || [];
  const salaryInsights = insights?.salary_insights || [];
  const demandSkills = insights?.demand_skills || [];
  const industryTrends = insights?.industry_trends || [];
  const recommendations = insights?.personalized_recommendations || [];
  const jobAlerts = insights?.job_alerts || [];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading market insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-bold mb-8">Market Insights</h1>

          {error && (
            <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Filters */}
          <div className="mb-8 flex flex-wrap gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Categories</option>
                <option value="technology">Technology</option>
                <option value="finance">Finance</option>
                <option value="healthcare">Healthcare</option>
                <option value="education">Education</option>
                <option value="marketing">Marketing</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Locations</option>
                <option value="remote">Remote</option>
                <option value="new-york">New York</option>
                <option value="san-francisco">San Francisco</option>
                <option value="london">London</option>
                <option value="bangalore">Bangalore</option>
              </select>
            </div>
          </div>

          {insights && (
            <div className="space-y-8">
              {/* Trending Jobs */}
              <div>
                <h2 className="text-2xl font-semibold mb-6">Trending Jobs</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {trendingJobs.map((job, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition">
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="text-lg font-semibold">{job.title}</h3>
                        <span className="text-green-600 font-medium text-sm inline-flex items-center gap-1">
                          <TrendingUp className="h-4 w-4" />
                          <span>+{job.growth}%</span>
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-3">{job.company}</p>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span className="inline-flex items-center gap-1"><MapPin className="h-4 w-4" /> {job.location}</span>
                        <span className="inline-flex items-center gap-1"><DollarSign className="h-4 w-4" /> {job.salary_range}</span>
                      </div>
                      <div className="mt-3">
                        <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          {job.category}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Salary Insights */}
              <div>
                <h2 className="text-2xl font-semibold mb-6">Salary Insights</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {salaryInsights.map((insight, index) => (
                    <div key={index} className="bg-gray-50 rounded-lg p-6">
                      <h3 className="text-lg font-semibold mb-3">{insight.role}</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Entry Level</span>
                          <span className="font-medium">${insight.entry_level}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Mid Level</span>
                          <span className="font-medium">${insight.mid_level}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Senior Level</span>
                          <span className="font-medium">${insight.senior_level}</span>
                        </div>
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-gray-600">Demand</span>
                          <span className={`font-medium ${
                            insight.demand === 'High' ? 'text-green-600' :
                            insight.demand === 'Medium' ? 'text-yellow-600' :
                            'text-red-600'
                          }`}>
                            {insight.demand}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Skills in Demand */}
              <div>
                <h2 className="text-2xl font-semibold mb-6">Skills in Demand</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {demandSkills.map((skill, index) => (
                    <div key={index} className="bg-blue-50 rounded-lg p-4 text-center">
                      <Target className="h-7 w-7 text-blue-600 mx-auto mb-2" />
                      <h3 className="font-semibold mb-1">{skill.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{skill.description}</p>
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {skill.growth} growth
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Industry Trends */}
              <div>
                <h2 className="text-2xl font-semibold mb-6">Industry Trends</h2>
                <div className="space-y-4">
                  {industryTrends.map((trend, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="text-lg font-semibold">{trend.title}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          trend.impact === 'High' ? 'bg-red-100 text-red-800' :
                          trend.impact === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {trend.impact} Impact
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">{trend.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="inline-flex items-center gap-1"><Calendar className="h-4 w-4" /> {trend.timeline}</span>
                        <span className="inline-flex items-center gap-1"><Building2 className="h-4 w-4" /> {trend.industry}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Personalized Recommendations */}
              <div>
                <h2 className="text-2xl font-semibold mb-6">Personalized Recommendations</h2>
                <div className="bg-green-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Based on your profile and quiz results:</h3>
                  <div className="space-y-3">
                    {recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start">
                        <span className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3 flex-shrink-0">
                          <Lightbulb className="h-4 w-4" />
                        </span>
                        <div>
                          <p className="font-medium">{rec.title}</p>
                          <p className="text-sm text-gray-600">{rec.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Job Alerts */}
              <div>
                <h2 className="text-2xl font-semibold mb-6">Job Alerts</h2>
                <div className="bg-yellow-50 rounded-lg p-6">
                  <p className="text-gray-700 mb-4">
                    Get notified when jobs matching your skills become available.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {jobAlerts.map((alert, index) => (
                      <span key={index} className="bg-yellow-200 text-yellow-800 text-sm px-3 py-1 rounded-full">
                        {alert}
                      </span>
                    ))}
                  </div>
                  <button className="mt-4 bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition inline-flex items-center gap-2">
                    <Bell className="h-4 w-4" />
                    <span>Set up Job Alerts</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {!insights && !error && (
            <div className="text-center text-gray-600 bg-gray-50 rounded-lg p-8">
              No market insights are available yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarketInsights;
