import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import {
AlertTriangle,
  Award,
  BookOpen,
  Briefcase,
  CheckCircle2,
  Loader2,
  Plus,
  RotateCcw,
  SearchCheck,
  Target,
  Trash2
} from 'lucide-react';

const SKILL_OPTIONS = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'java', label: 'Java' },
  { value: 'sql', label: 'SQL' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
  { value: 'react', label: 'React' },
  { value: 'flutter', label: 'Flutter' },
  { value: 'dart', label: 'Dart' },
  { value: 'android', label: 'Android' },
  { value: 'ios', label: 'iOS' },
  { value: 'mobile_development', label: 'Mobile Development' },
  { value: 'git', label: 'Git' },
  { value: 'machine_learning', label: 'Machine Learning' },
  { value: 'data_analysis', label: 'Data Analysis' },
  { value: 'statistics', label: 'Statistics' },
  { value: 'excel', label: 'Excel' },
  { value: 'communication', label: 'Communication' },
  { value: 'leadership', label: 'Leadership' },
  { value: 'project_management', label: 'Project Management' },
  { value: 'problem_solving', label: 'Problem Solving' },
  { value: 'ui_ux', label: 'UI/UX' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'devops', label: 'DevOps' },
  { value: 'testing', label: 'Testing' }
];

const SKILL_LEVELS = [
  { value: 0, label: 'No Experience' },
  { value: 1, label: 'Beginner' },
  { value: 2, label: 'Intermediate' },
  { value: 3, label: 'Advanced' }
];

const SkillGapAnalysis = () => {
  const { token } = useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState('');
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState('');
  const [mySkills, setMySkills] = useState([
    { skill: 'python', level: 1 },
    { skill: 'communication', level: 1 }
  ]);

  const matchingSkills = analysis?.matching_skills || [];
  const fullyMatchedSkills = analysis?.fully_matched_skills || [];
  const partialSkills = analysis?.partial_skills || [];
  const skillGaps = analysis?.skill_gaps || [];
  const skillDetails = analysis?.skill_details || [];
  const learningPath = analysis?.learning_path || [];

  useEffect(() => {
    let isMounted = true;

    fetch(`${API_BASE_URL}/skill-analysis/jobs`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(response => response.json())
      .then(data => {
        if (isMounted) {
          if (data.status === 'error' || data.error) {
            setError(data.message || data.error || 'Unable to load job titles.');
          } else {
            setJobs(data.jobs || []);
          }
          setLoading(false);
        }
      })
      .catch(error => {
        console.error('Error fetching jobs:', error);
        if (isMounted) {
          setError('Unable to load job titles. Please try again.');
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [token]);

  const handleAnalyze = async () => {
    if (!selectedJob) return;

    const userSkills = mySkills.reduce((skills, item) => {
      if (item.skill) {
        skills[item.skill] = Number(item.level);
      }
      return skills;
    }, {});

    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/skill-analysis/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          job_title: selectedJob,
          user_skills: userSkills
        })
      });
      const data = await response.json();
      if (!response.ok || data.status === 'error' || data.error) {
        throw new Error(data.message || data.error || 'Skill analysis failed');
      }
      setAnalysis(data);
    } catch (error) {
      console.error('Error analyzing skills:', error);
      setError(error.message || 'Error analyzing skills.');
    }
    setLoading(false);
  };

  const updateSkill = (index, field, value) => {
    setMySkills(prev =>
      prev.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item
      )
    );
  };

  const addSkill = () => {
    const usedSkills = new Set(mySkills.map(item => item.skill));
    const nextSkill = SKILL_OPTIONS.find(option => !usedSkills.has(option.value));

    if (nextSkill) {
      setMySkills(prev => [...prev, { skill: nextSkill.value, level: 1 }]);
    }
  };

  const removeSkill = (index) => {
    setMySkills(prev => prev.filter((_, itemIndex) => itemIndex !== index));
  };

  if (loading && !analysis) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading skill analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-bold mb-8">Skill Gap Analysis</h1>
          {error && (
            <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          {!analysis ? (
            <div className="mb-8">
              <p className="text-gray-600 mb-6">
                Select a job title to analyze your skill gaps and get personalized recommendations.
              </p>

              <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)] gap-8">
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <Briefcase className="h-4 w-4 text-gray-500" />
                    <span>Job Title</span>
                  </label>
                  <select
                    value={selectedJob}
                    onChange={(e) => setSelectedJob(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a job title...</option>
                    {jobs.map((job, index) => (
                      <option key={index} value={job}>{job}</option>
                    ))}
                  </select>

                  <button
                    onClick={handleAnalyze}
                    disabled={!selectedJob}
                    className="w-full mt-4 bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition inline-flex items-center justify-center gap-2"
                  >
                    <SearchCheck className="h-5 w-5" />
                    <span>Analyze My Skills</span>
                  </button>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                      <Target className="h-4 w-4 text-gray-500" />
                      <span>My Skills</span>
                    </label>
                    <button
                      type="button"
                      onClick={addSkill}
                      disabled={mySkills.length >= SKILL_OPTIONS.length}
                      className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 disabled:text-gray-400"
                    >
                      <Plus className="h-4 w-4" />
                      <span>Add Skill</span>
                    </button>
                  </div>

                  <div className="space-y-3">
                    {mySkills.map((item, index) => (
                      <div key={`${item.skill}-${index}`} className="grid grid-cols-1 sm:grid-cols-[minmax(0,1fr)_160px_auto] gap-3 items-center">
                        <select
                          value={item.skill}
                          onChange={(e) => updateSkill(index, 'skill', e.target.value)}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          {SKILL_OPTIONS.map((skill) => (
                            <option key={skill.value} value={skill.value}>
                              {skill.label}
                            </option>
                          ))}
                        </select>

                        <select
                          value={item.level}
                          onChange={(e) => updateSkill(index, 'level', e.target.value)}
                          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          {SKILL_LEVELS.map((level) => (
                            <option key={level.value} value={level.value}>
                              {level.label}
                            </option>
                          ))}
                        </select>

                        <button
                          type="button"
                          onClick={() => removeSkill(index)}
                          disabled={mySkills.length === 1}
                          className="px-3 py-3 text-sm text-red-600 hover:text-red-700 disabled:text-gray-400 inline-flex items-center justify-center gap-1"
                          aria-label="Remove skill"
                          title="Remove skill"
                        >
                          <Trash2 className="h-4 w-4" />
                          <span className="sm:hidden">Remove</span>
                        </button>
                      </div>
                    ))}
                  </div>

                  <p className="text-sm text-gray-500 mt-3">
                    Levels are compared with job requirements from the job description dataset.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              <div className="text-center">
                <h2 className="text-2xl font-semibold mb-2">Analysis for: {analysis.job_title}</h2>
                <p className="text-gray-600">Based on your selected skills and job requirements</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-green-50 p-6 rounded-lg text-center">
                  <CheckCircle2 className="h-7 w-7 text-green-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    {fullyMatchedSkills.length}
                  </div>
                  <p className="text-green-700 font-medium">Fully Matched</p>
                </div>

                <div className="bg-red-50 p-6 rounded-lg text-center">
                  <AlertTriangle className="h-7 w-7 text-red-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-red-600 mb-2">
                    {skillGaps.length}
                  </div>
                  <p className="text-red-700 font-medium">Skill Gaps</p>
                </div>

                <div className="bg-blue-50 p-6 rounded-lg text-center">
                  <Target className="h-7 w-7 text-blue-600 mx-auto mb-3" />
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    {analysis.match_percentage || 0}%
                  </div>
                  <p className="text-blue-700 font-medium">Match Percentage</p>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-semibold mb-4 text-green-700">Skills Found in Your Profile</h3>
                  <div className="space-y-3">
                    {matchingSkills.map((skill, index) => (
                      <div key={index} className="flex items-center p-3 bg-green-50 rounded-lg">
                        <CheckCircle2 className="h-4 w-4 text-green-600 mr-3 flex-shrink-0" />
                        <span>{skill}</span>
                        {partialSkills.includes(skill) && (
                          <span className="ml-auto rounded-full bg-yellow-100 px-2 py-1 text-xs font-medium text-yellow-700">
                            Needs improvement
                          </span>
                        )}
                      </div>
                    ))}
                    {matchingSkills.length === 0 && (
                      <div className="p-3 bg-gray-50 rounded-lg text-gray-600">
                        No matching skills yet. Add more skills or increase skill levels and analyze again.
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-4 text-red-700">Skill Gaps to Address</h3>
                  <div className="space-y-3">
                    {skillGaps.map((skill, index) => (
                      <div key={index} className="flex items-center p-3 bg-red-50 rounded-lg">
                        <AlertTriangle className="h-4 w-4 text-red-600 mr-3 flex-shrink-0" />
                        <span>{skill}</span>
                      </div>
                    ))}
                    {skillGaps.length === 0 && (
                      <div className="p-3 bg-green-50 rounded-lg text-green-700">
                        No major skill gaps found for your selected skills.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {skillDetails.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold mb-4">Required Skill Details</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {skillDetails.map((detail) => (
                      <div key={detail.skill} className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <h4 className="font-semibold text-gray-900">{detail.skill}</h4>
                            <p className="text-sm text-gray-600">
                              Level {detail.current_level} of {detail.required_level}
                            </p>
                          </div>
                          <span className={`rounded-full px-2 py-1 text-xs font-semibold ${
                            detail.status === 'matched'
                              ? 'bg-green-100 text-green-700'
                              : detail.status === 'partial'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-red-100 text-red-700'
                          }`}>
                            {detail.status}
                          </span>
                        </div>
                        <div className="mt-3 h-2 overflow-hidden rounded-full bg-gray-200">
                          <div
                            className={`h-full rounded-full ${
                              detail.status === 'matched'
                                ? 'bg-green-500'
                                : detail.status === 'partial'
                                  ? 'bg-yellow-500'
                                  : 'bg-red-500'
                            }`}
                            style={{ width: `${detail.completion}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-xl font-semibold mb-4">Recommended Learning Path</h3>
                <div className="bg-blue-50 p-6 rounded-lg">
                  <div className="space-y-4">
                    {learningPath.map((step, index) => (
                      <div key={index} className="flex items-start">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium mr-4">
                          <BookOpen className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="font-medium">{step.skill}</h4>
                          <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                          <div className="flex items-center mt-2 space-x-4">
                            <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                              {step.duration}
                            </span>
                            <span className="text-xs bg-yellow-200 px-2 py-1 rounded">
                              {step.difficulty}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                    {learningPath.length === 0 && (
                      <p className="text-gray-600">You are already meeting the detected requirements for this role.</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={() => setAnalysis(null)}
                  className="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600 transition inline-flex items-center gap-2"
                >
                  <RotateCcw className="h-5 w-5" />
                  <span>Analyze Different Job</span>
                </button>
                <Link
                  to="/learning-paths"
                  className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition inline-flex items-center gap-2"
                >
                  <BookOpen className="h-5 w-5" />
                  <span>Start Learning Path</span>
                </Link>
                <Link
                  to="/certifications"
                  className="bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 transition inline-flex items-center gap-2"
                >
                  <Award className="h-5 w-5" />
                  <span>Get Certified</span>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkillGapAnalysis;
