import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_BASE_URL } from '../config';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import {
ArrowLeft,
  ArrowRight,
  BarChart3,
  BookOpen,
  CheckCircle2,
  Loader2,
  RotateCcw,
  Send,
  Trophy
} from 'lucide-react';

const CompetencyQuiz = () => {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState(null);

  useEffect(() => {
    if (token) {
      fetchQuestions();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/quiz/questions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) {
        if (response.status === 401 || response.status === 422) {
          navigate('/login', { replace: true });
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setQuestions(Array.isArray(data.questions) ? data.questions : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching questions:', error);
      setQuestions([]);
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/quiz/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          responses: Object.entries(answers).map(([question_id, answer]) => ({
            question_id,
            answer
          }))
        })
      });
      const data = await response.json();
      setResults(data.scores || data);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
    setSubmitting(false);
  };

  if (loading) {
    return (
      <div className="bg-gray-50 flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading quiz questions...</p>
        </div>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!questions.length) {
    return (
      <div className="bg-gray-50 flex items-center justify-center min-h-[50vh]">
        <div className="bg-white p-8 rounded-xl shadow-md text-center">
          <h2 className="text-2xl font-bold mb-4">No quiz questions available</h2>
          <p className="text-gray-600 mb-6">We couldn’t load the competency quiz. Please try again or contact support.</p>
          <button
            onClick={fetchQuestions}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition inline-flex items-center justify-center gap-2"
          >
            <RotateCcw className="h-5 w-5" />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  if (results) {
    return (
      <div className="bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-md p-8">
            <h1 className="text-3xl font-bold text-center mb-8">Quiz Results</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-blue-50 p-6 rounded-lg">
                <BarChart3 className="h-7 w-7 text-blue-600 mb-3" />
                <h3 className="text-xl font-semibold mb-4">Overall Score</h3>
                <div className="text-4xl font-bold text-blue-600">
                  {results.overall_score}%
                </div>
              </div>

              <div className="bg-green-50 p-6 rounded-lg">
                <Trophy className="h-7 w-7 text-green-600 mb-3" />
                <h3 className="text-xl font-semibold mb-4">Competency Level</h3>
                <div className="text-2xl font-bold text-green-600">
                  {results.competency_level}
                </div>
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-4">Skill Breakdown</h3>
              <div className="space-y-4">
                {results.skill_scores.map((skill, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <span className="font-medium">{skill.skill}</span>
                    <div className="flex items-center space-x-4">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${skill.score}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{skill.score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-4">Recommendations</h3>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <ul className="list-disc list-inside space-y-2">
                  {results.recommendations.map((rec, index) => (
                    <li key={index} className="flex items-start gap-2 list-none">
                      <CheckCircle2 className="h-4 w-4 text-yellow-700 mt-1 flex-shrink-0" />
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex space-x-4">
              <Link
                to="/skill-analysis"
                className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition inline-flex items-center gap-2"
              >
                <BarChart3 className="h-5 w-5" />
                <span>View Skill Gap Analysis</span>
              </Link>
              <Link
                to="/learning-paths"
                className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition inline-flex items-center gap-2"
              >
                <BookOpen className="h-5 w-5" />
                <span>Explore Learning Paths</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-2xl font-bold">Competency Quiz</h1>
              <span className="text-sm text-gray-600">
                Question {currentQuestion + 1} of {questions.length}
              </span>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {question && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-6">{question.question}</h2>

              <div className="space-y-3">
                {question.options.map((option, index) => (
                  <label key={index} className="flex items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={option}
                      checked={answers[question.id] === option}
                      onChange={() => handleAnswer(question.id, option)}
                      className="mr-3"
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-400 transition inline-flex items-center gap-2"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Previous</span>
            </button>

            {currentQuestion < questions.length - 1 ? (
              <button
                onClick={handleNext}
                disabled={!answers[question?.id]}
                className="px-6 py-3 bg-blue-500 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-600 transition inline-flex items-center gap-2"
              >
                <span>Next</span>
                <ArrowRight className="h-5 w-5" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!answers[question?.id] || submitting}
                className="px-6 py-3 bg-green-500 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-green-600 transition inline-flex items-center gap-2"
              >
                {submitting ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
                <span>{submitting ? 'Submitting...' : 'Submit Quiz'}</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetencyQuiz;
