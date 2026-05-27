import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from "../config";
import {
  ArrowLeft,
  BookOpen,
  Check,
  Clock,
  ExternalLink,
  Loader2,
  Lock,
  Play,
  Route,
  UserPlus
} from 'lucide-react';

const LearningPathways = () => {
  const { token } = useAuth();
  const [pathways, setPathways] = useState([]);
  const [selectedPathway, setSelectedPathway] = useState(null);
  const [progress, setProgress] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (token) {
      fetchPathways();
    }
  }, [token]);

  const fetchPathways = async () => {
    try {
      setError("");
      const response = await fetch(`${API_BASE_URL}/learning-pathways`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to load learning pathways');
      }

      setPathways(Array.isArray(data.pathways) ? data.pathways : []);
      setProgress(data.progress || {});
      setLoading(false);
    } catch (error) {
      console.error('Error fetching pathways:', error);
      setError(error.message || 'Unable to load learning pathways');
      setLoading(false);
    }
  };

  const handleEnroll = async (pathwayId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/learning-pathways/${pathwayId}/enroll`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.success) {
        setProgress(data.progress || {});
      }
    } catch (error) {
      console.error('Error enrolling in pathway:', error);
    }
  };

  const handleCompleteStep = async (pathwayId, stepId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/learning-pathways/${pathwayId}/complete/${stepId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (data.success) {
        setProgress(data.progress || {});
      }
    } catch (error) {
      console.error('Error completing step:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading learning pathways...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-bold mb-8">Learning Pathways</h1>

          {error && (
            <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {!selectedPathway ? (
            <div>
              <p className="text-gray-600 mb-6">
                Choose from our personalized learning pathways to develop your skills.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pathways.map((pathway) => (
                  <div key={pathway.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold mb-2">{pathway.title}</h3>
                        <p className="text-gray-600 text-sm mb-3">{pathway.description}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        pathway.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                        pathway.difficulty === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {pathway.difficulty}
                      </span>
                    </div>

                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span>Progress</span>
                        <span>{progress[pathway.id]?.completed || 0}/{pathway.steps.length} steps</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{
                            width: `${((progress[pathway.id]?.completed || 0) / pathway.steps.length) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">{pathway.duration}</span>
                        <span className="mx-2">•</span>
                        <span>{pathway.steps.length} steps</span>
                      </div>

                      {progress[pathway.id]?.enrolled ? (
                        <button
                          onClick={() => setSelectedPathway(pathway)}
                          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition text-sm inline-flex items-center gap-2"
                        >
                          <Play className="h-4 w-4" />
                          <span>Continue</span>
                        </button>
                      ) : (
                        <button
                          onClick={() => handleEnroll(pathway.id)}
                          className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition text-sm inline-flex items-center gap-2"
                        >
                          <UserPlus className="h-4 w-4" />
                          <span>Enroll</span>
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {!pathways.length && !error && (
                <div className="text-center text-gray-600 bg-gray-50 rounded-lg p-8">
                  No learning pathways are available yet.
                </div>
              )}
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-6">
                <button
                  onClick={() => setSelectedPathway(null)}
                  className="text-blue-500 hover:text-blue-700 font-medium inline-flex items-center gap-2"
                >
                  <ArrowLeft className="h-5 w-5" />
                  <span>Back to Pathways</span>
                </button>
                <h2 className="text-2xl font-bold">{selectedPathway.title}</h2>
              </div>

              <div className="mb-6">
                <p className="text-gray-600">{selectedPathway.description}</p>
              </div>

              <div className="space-y-4">
                {selectedPathway.steps.map((step, index) => {
                  const isCompleted = progress[selectedPathway.id]?.completed_steps?.includes(step.id);
                  const isCurrent = !isCompleted && (index === 0 || progress[selectedPathway.id]?.completed_steps?.includes(selectedPathway.steps[index - 1]?.id));

                  return (
                    <div key={step.id} className={`border rounded-lg p-6 ${
                      isCompleted ? 'bg-green-50 border-green-200' :
                      isCurrent ? 'bg-blue-50 border-blue-200' :
                      'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4">
                          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                            isCompleted ? 'bg-green-500 text-white' :
                            isCurrent ? 'bg-blue-500 text-white' :
                            'bg-gray-300 text-gray-600'
                          }`}>
                            {isCompleted ? <Check className="h-4 w-4" /> : <Route className="h-4 w-4" />}
                          </div>

                          <div className="flex-1">
                            <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                            <p className="text-gray-600 mb-3">{step.description}</p>

                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                              <span className="inline-flex items-center gap-1"><BookOpen className="h-4 w-4" /> {step.type}</span>
                              <span className="inline-flex items-center gap-1"><Clock className="h-4 w-4" /> {step.duration}</span>
                              {step.resources && <span className="inline-flex items-center gap-1"><ExternalLink className="h-4 w-4" /> {step.resources.length} resources</span>}
                            </div>
                          </div>
                        </div>

                        <div className="flex-shrink-0">
                          {isCompleted ? (
                            <span className="text-green-600 font-medium inline-flex items-center gap-2">
                              <Check className="h-4 w-4" />
                              <span>Completed</span>
                            </span>
                          ) : isCurrent ? (
                            <button
                              onClick={() => handleCompleteStep(selectedPathway.id, step.id)}
                              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition text-sm inline-flex items-center gap-2"
                            >
                              <Check className="h-4 w-4" />
                              <span>Mark Complete</span>
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm inline-flex items-center gap-1">
                              <Lock className="h-4 w-4" />
                              <span>Locked</span>
                            </span>
                          )}
                        </div>
                      </div>

                      {step.resources && step.resources.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <h4 className="font-medium mb-2">Resources:</h4>
                          <div className="space-y-2">
                            {step.resources.map((resource, idx) => (
                              <a
                                key={idx}
                                href={resource.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 text-blue-500 hover:text-blue-700 text-sm"
                              >
                                <ExternalLink className="h-4 w-4" />
                                <span>{resource.title}</span>
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className="mt-8 p-6 bg-gray-50 rounded-lg">
                <h3 className="text-lg font-semibold mb-4">Pathway Progress</h3>
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Overall Completion</span>
                  <span>{progress[selectedPathway.id]?.completed || 0} of {selectedPathway.steps.length} steps</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{
                      width: `${((progress[selectedPathway.id]?.completed || 0) / selectedPathway.steps.length) * 100}%`
                    }}
                  ></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LearningPathways;
