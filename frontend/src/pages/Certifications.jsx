import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Award,
  BadgeCheck,
  BriefcaseBusiness,
  CheckCircle2,
  Download,
  Loader2,
  Medal,
  RefreshCcw,
  Send,
  TrendingUp,
  X
} from 'lucide-react';

const Certifications = () => {
  const { token } = useAuth();
  const [certifications, setCertifications] = useState([]);
  const [userCertifications, setUserCertifications] = useState([]);
  const [selectedCertification, setSelectedCertification] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [takingQuiz, setTakingQuiz] = useState(false);
  const [quizResults, setQuizResults] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchCertifications();
      fetchUserCertifications();
    }
  }, [token]);

  const fetchCertifications = async () => {
    try {
      setError('');
      const response = await fetch('http://localhost:5000/certifications', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to load certifications');
      }
      setCertifications(Array.isArray(data.certifications) ? data.certifications : []);
    } catch (error) {
      console.error('Error fetching certifications:', error);
      setError(error.message || 'Unable to load certifications');
    }
  };

  const fetchUserCertifications = async () => {
    try {
      const response = await fetch('http://localhost:5000/certifications/user', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to load your certifications');
      }
      setUserCertifications(Array.isArray(data.certifications) ? data.certifications : []);
    } catch (error) {
      console.error('Error fetching user certifications:', error);
      setError(error.message || 'Unable to load your certifications');
    }
    setLoading(false);
  };

  const handleStartQuiz = async (certificationId) => {
    try {
      const response = await fetch(`http://localhost:5000/certifications/${certificationId}/quiz`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to load certification quiz');
      }
      setQuiz(data.quiz);
      setSelectedCertification(certifications.find(c => c.id === certificationId));
      setTakingQuiz(true);
      setAnswers({});
      setQuizResults(null);
    } catch (error) {
      console.error('Error fetching quiz:', error);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmitQuiz = async () => {
    try {
      const response = await fetch(`http://localhost:5000/certifications/${selectedCertification.id}/quiz/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ answers })
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Failed to submit quiz');
      }
      setQuizResults(data);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  const handleDownloadCertificate = async (certificationId) => {
    try {
      const response = await fetch(`http://localhost:5000/certifications/${certificationId}/download`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      // In a real app, this would trigger a download
      alert(`Certificate download link: ${data.download_url}`);
    } catch (error) {
      console.error('Error downloading certificate:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 text-blue-500 animate-spin mx-auto" />
          <p className="mt-4 text-gray-600">Loading certifications...</p>
        </div>
      </div>
    );
  }

  if (takingQuiz && quiz) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-md p-8">
            <div className="flex items-center justify-between mb-6">
              <h1 className="text-2xl font-bold">{selectedCertification.title} - Certification Quiz</h1>
              <button
                onClick={() => {
                  setTakingQuiz(false);
                  setQuiz(null);
                  setSelectedCertification(null);
                }}
                className="text-gray-500 hover:text-gray-700"
                aria-label="Close quiz"
                title="Close quiz"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {quizResults ? (
              <div className="text-center">
                <h2 className="text-3xl font-bold mb-4">
                  <span className="inline-flex items-center justify-center gap-3">
                    {quizResults.passed ? <BadgeCheck className="h-8 w-8 text-green-600" /> : <RefreshCcw className="h-8 w-8 text-blue-600" />}
                    <span>{quizResults.passed ? 'Congratulations!' : 'Keep Learning'}</span>
                  </span>
                </h2>

                <div className="mb-6">
                  <div className="text-6xl font-bold mb-2">
                    {quizResults.score}%
                  </div>
                  <p className="text-gray-600">Your Score</p>
                </div>

                {quizResults.passed ? (
                  <div className="bg-green-50 p-6 rounded-lg mb-6">
                    <h3 className="text-xl font-semibold text-green-800 mb-2">
                      You Passed! Certificate Earned
                    </h3>
                    <p className="text-green-700 mb-4">
                      You have successfully earned the {selectedCertification.title} certification.
                    </p>
                    <button
                      onClick={() => handleDownloadCertificate(selectedCertification.id)}
                      className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition inline-flex items-center gap-2"
                    >
                      <Download className="h-5 w-5" />
                      <span>Download Certificate</span>
                    </button>
                  </div>
                ) : (
                  <div className="bg-red-50 p-6 rounded-lg mb-6">
                    <h3 className="text-xl font-semibold text-red-800 mb-2">
                      Certificate Not Earned
                    </h3>
                    <p className="text-red-700 mb-4">
                      You need at least {quizResults.passing_score}% to earn this certification.
                      Review the material and try again.
                    </p>
                    <button
                      onClick={() => handleStartQuiz(selectedCertification.id)}
                      className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition inline-flex items-center gap-2"
                    >
                      <RefreshCcw className="h-5 w-5" />
                      <span>Retake Quiz</span>
                    </button>
                  </div>
                )}

                <div className="text-left bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold mb-4">Detailed Results</h3>
                  <div className="space-y-3">
                    {quizResults.details.map((detail, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-white rounded">
                        <span className="font-medium">{detail.question}</span>
                        <span className={`px-2 py-1 rounded text-sm ${
                          detail.correct ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {detail.correct ? 'Correct' : 'Incorrect'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div>
                <div className="mb-6">
                  <div className="flex justify-between items-center text-sm text-gray-600 mb-4">
                    <span>Question {Object.keys(answers).length + 1} of {quiz.questions.length}</span>
                    <span>{Math.round((Object.keys(answers).length / quiz.questions.length) * 100)}% Complete</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(Object.keys(answers).length / quiz.questions.length) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="space-y-6">
                  {quiz.questions.map((question, index) => (
                    <div key={question.id} className="border border-gray-200 rounded-lg p-6">
                      <h3 className="text-lg font-semibold mb-4">
                        {index + 1}. {question.question}
                      </h3>

                      <div className="space-y-3">
                        {question.options.map((option, optionIndex) => (
                          <label key={optionIndex} className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
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
                  ))}
                </div>

                <div className="mt-8 text-center">
                  <button
                    onClick={handleSubmitQuiz}
                    disabled={Object.keys(answers).length !== quiz.questions.length}
                    className="bg-green-500 text-white px-8 py-3 rounded-lg hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition text-lg inline-flex items-center gap-2"
                  >
                    <Send className="h-5 w-5" />
                    <span>Submit Quiz</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-bold mb-8">Skill Certifications</h1>

          {error && (
            <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* User's Certifications */}
          {userCertifications.length > 0 && (
            <div className="mb-12">
              <h2 className="text-2xl font-semibold mb-6">Your Certifications</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {userCertifications.map((cert) => (
                  <div key={cert.id} className="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg p-6 text-white">
                    <h3 className="text-xl font-bold mb-2">{cert.title}</h3>
                    <p className="text-yellow-100 mb-3">{cert.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Earned: {new Date(cert.earned_date).toLocaleDateString()}</span>
                      <button
                        onClick={() => handleDownloadCertificate(cert.id)}
                        className="bg-white text-yellow-600 px-3 py-1 rounded text-sm hover:bg-gray-100 transition inline-flex items-center gap-1"
                      >
                        <Download className="h-4 w-4" />
                        <span>Download</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Available Certifications */}
          <div>
            <h2 className="text-2xl font-semibold mb-6">Available Certifications</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {certifications.map((cert) => {
                const isEarned = userCertifications.some(uc => uc.id === cert.id);

                return (
                  <div key={cert.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold mb-2">{cert.title}</h3>
                        <p className="text-gray-600 text-sm mb-3">{cert.description}</p>
                      </div>
                      {isEarned && (
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-medium">
                          Earned
                        </span>
                      )}
                    </div>

                    <div className="mb-4">
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span>Difficulty</span>
                        <span className={`font-medium ${
                          cert.difficulty === 'Beginner' ? 'text-green-600' :
                          cert.difficulty === 'Intermediate' ? 'text-yellow-600' :
                          'text-red-600'
                        }`}>
                          {cert.difficulty}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                        <span>Duration</span>
                        <span className="font-medium">{cert.duration}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>Prerequisites</span>
                        <span className="font-medium">{cert.prerequisites || 'None'}</span>
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="font-medium mb-2">Skills Covered:</h4>
                      <div className="flex flex-wrap gap-1">
                        {(cert.skills || []).map((skill, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>

                    {isEarned ? (
                      <div className="text-center">
                        <span className="text-green-600 font-medium inline-flex items-center justify-center gap-2">
                          <CheckCircle2 className="h-5 w-5" />
                          <span>Certification Earned</span>
                        </span>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleStartQuiz(cert.id)}
                        className="w-full bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 transition inline-flex items-center justify-center gap-2"
                      >
                        <Award className="h-5 w-5" />
                        <span>Take Certification Quiz</span>
                      </button>
                    )}
                  </div>
                );
              })}
            </div>

            {!certifications.length && !error && (
              <div className="text-center text-gray-600 bg-gray-50 rounded-lg p-8">
                No certifications are available yet.
              </div>
            )}
          </div>

          {/* Certification Benefits */}
          <div className="mt-12 bg-gray-50 rounded-lg p-8">
            <h2 className="text-2xl font-semibold mb-6">Why Get Certified?</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center">
                <BriefcaseBusiness className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Career Advancement</h3>
                <p className="text-sm text-gray-600">Stand out to employers with verified skills</p>
              </div>
              <div className="text-center">
                <BadgeCheck className="h-8 w-8 text-green-600 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Skill Validation</h3>
                <p className="text-sm text-gray-600">Prove your expertise with recognized certifications</p>
              </div>
              <div className="text-center">
                <TrendingUp className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Higher Salary</h3>
                <p className="text-sm text-gray-600">Certified professionals earn 10-20% more</p>
              </div>
              <div className="text-center">
                <Medal className="h-8 w-8 text-yellow-600 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">Recognition</h3>
                <p className="text-sm text-gray-600">Get badges and certificates to showcase achievements</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Certifications;
