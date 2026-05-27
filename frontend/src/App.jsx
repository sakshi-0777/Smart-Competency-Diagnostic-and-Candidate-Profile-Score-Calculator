import React from 'react'
import Login from './pages/Login'
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import CompetencyQuiz from './pages/CompetencyQuiz'
import SkillGapAnalysis from './pages/SkillGapAnalysis'
import LearningPathways from './pages/LearningPathways'
import ResumeWizard from './pages/ResumeWizard'
import MarketInsights from './pages/MarketInsights'
import CommunityForum from './pages/CommunityForum'
import Certifications from './pages/Certifications'
import Settings from './pages/Settings'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuth } from './context/AuthContext'


const App = () => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;


  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>} >
        <Route index element={<Dashboard />} />
        <Route path="quiz" element={<CompetencyQuiz />} />
        <Route path="skill-analysis" element={<SkillGapAnalysis />} />
        <Route path="learning-paths" element={<LearningPathways />} />
        <Route path="resume-wizard" element={<ResumeWizard />} />
        <Route path="market-insights" element={<MarketInsights />} />
        <Route path="community" element={<CommunityForum />} />
        <Route path="certifications" element={<Certifications />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to={user ? "/" : "/login"} />} />
    </Routes>


  )
}

export default App