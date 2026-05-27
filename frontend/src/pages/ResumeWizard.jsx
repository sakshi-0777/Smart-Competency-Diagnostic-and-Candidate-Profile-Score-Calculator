import React, { useState, useEffect, useMemo } from 'react';
import { useAuth } from '../context/AuthContext';
import {
Download,
  FilePlus2,
  Loader2,
  Plus,
  RotateCcw,
  Trash2,
  X
} from 'lucide-react';

const ResumeWizard = () => {
  const { token, user } = useAuth();
  const fallbackTemplates = useMemo(() => ([
    { id: 'modern', name: 'Modern Professional', description: 'Clean resume with summary, skills, education, and projects.' },
    { id: 'technical', name: 'Technical Focus', description: 'Highlights technical skills and project work.' },
    { id: 'creative', name: 'Creative Portfolio', description: 'Showcases portfolio-style project experience.' }
  ]), []);
  const [templates, setTemplates] = useState(fallbackTemplates);
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: '',
    location: '',
    summary: '',
    experience: [{ company: '', position: '', duration: '', description: '' }],
    education: [{ institution: '', degree: '', year: '' }],
    skills: [''],
    projects: [{ name: '', description: '', technologies: '' }]
  });
  const [generating, setGenerating] = useState(false);
  const [resumeText, setResumeText] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      fetchTemplates();
    }
  }, [token]);

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/resume/templates`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      if (response.ok && Array.isArray(data.templates) && data.templates.length > 0) {
        setTemplates(data.templates);
        setSelectedTemplate(data.templates[0].id);
      }
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayChange = (field, index, subfield, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) =>
        i === index ? { ...item, [subfield]: value } : item
      )
    }));
  };

  const addArrayItem = (field, defaultItem) => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], defaultItem]
    }));
  };

  const removeArrayItem = (field, index) => {
    setFormData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }));
  };

  const handleSkillChange = (index, value) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.map((skill, i) => i === index ? value : skill)
    }));
  };

  const addSkill = () => {
    setFormData(prev => ({
      ...prev,
      skills: [...prev.skills, '']
    }));
  };

  const removeSkill = (index) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter((_, i) => i !== index)
    }));
  };

  const buildUserProfile = () => {
    const skillScores = formData.skills
      .map(skill => skill.trim())
      .filter(Boolean)
      .reduce((scores, skill) => ({ ...scores, [skill.toLowerCase()]: 2 }), {});

    return {
      name: formData.name,
      email: formData.email,
      phone: formData.phone,
      location: formData.location,
      summary: formData.summary,
      skill_scores: skillScores,
      experience: formData.experience
        .filter(exp => exp.company || exp.position || exp.description)
        .map(exp => ({
          company: exp.company,
          position: exp.position,
          start_date: exp.duration,
          end_date: '',
          responsibilities: exp.description
            .split('\n')
            .map(line => line.trim())
            .filter(Boolean)
        })),
      education: formData.education
        .filter(edu => edu.institution || edu.degree || edu.year)
        .map(edu => ({
          institution: edu.institution,
          degree: edu.degree,
          graduation_year: edu.year
        })),
      projects: formData.projects
        .filter(project => project.name || project.description || project.technologies)
        .map(project => ({
          name: project.name,
          description: project.description,
          technologies: project.technologies
            .split(',')
            .map(technology => technology.trim())
            .filter(Boolean)
        }))
    };
  };

  const formatGeneratedResume = (resume) => {
    const sections = resume?.sections || {};
    const header = sections.header || {};
    const summary = sections.summary || {};
    const skills = sections.skills || {};
    const education = sections.education || [];
    const projects = sections.projects || [];

    const lines = [
      header.name,
      header.title,
      [header.email, header.phone, header.location].filter(Boolean).join(' | '),
      ''
    ];

    if (summary.content) {
      lines.push('PROFESSIONAL SUMMARY', summary.content, '');
    }

    if (Object.keys(skills).length) {
      lines.push('SKILLS');
      Object.entries(skills).forEach(([category, items]) => {
        lines.push(`${category}: ${items.map(item => item.name).join(', ')}`);
      });
      lines.push('');
    }

    if (education.length) {
      lines.push('EDUCATION');
      education.forEach(edu => {
        lines.push([edu.degree, edu.institution, edu.graduation_year].filter(Boolean).join(' - '));
      });
      lines.push('');
    }

    if (projects.length) {
      lines.push('PROJECTS');
      projects.forEach(project => {
        lines.push(project.name);
        if (project.description) lines.push(project.description);
        if (project.technologies?.length) lines.push(`Technologies: ${project.technologies.join(', ')}`);
        lines.push('');
      });
    }

    return lines.filter((line, index) => line || lines[index - 1]).join('\n').trim();
  };

  const downloadResume = () => {
    const blob = new Blob([resumeText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${formData.name || 'resume'}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE_URL}/resume/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          template: selectedTemplate,
          user_profile: buildUserProfile()
        })
      });
      const data = await response.json();
      if (!response.ok || data.status === 'error') {
        throw new Error(data.message || data.error || 'Failed to generate resume');
      }
      setResumeText(formatGeneratedResume(data.resume));
    } catch (error) {
      console.error('Error generating resume:', error);
      setError(error.message || 'Failed to generate resume');
    }
    setGenerating(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-md p-8">
          <h1 className="text-3xl font-bold mb-8">Resume Wizard</h1>

          {resumeText ? (
            <div className="text-center">
              <h2 className="text-2xl font-semibold mb-4">Resume Generated Successfully!</h2>
              <pre className="mb-6 whitespace-pre-wrap rounded-lg border border-gray-200 bg-gray-50 p-5 text-left text-sm leading-6 text-gray-800">
                {resumeText}
              </pre>
              <div className="mb-6 flex justify-center">
                <button
                  onClick={downloadResume}
                  className="inline-flex items-center gap-2 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition"
                >
                  <Download className="h-5 w-5" />
                  <span>Download Resume</span>
                </button>
              </div>
              <button
                onClick={() => setResumeText('')}
                className="text-blue-500 hover:text-blue-700 inline-flex items-center gap-2"
              >
                <RotateCcw className="h-5 w-5" />
                <span>Create Another Resume</span>
              </button>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Template Selection */}
              <div>
                <h2 className="text-xl font-semibold mb-4">Choose a Template</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {templates.map((template) => (
                    <div
                      key={template.id}
                      onClick={() => setSelectedTemplate(template.id)}
                      className={`border-2 rounded-lg p-4 cursor-pointer transition ${
                        selectedTemplate === template.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <h3 className="font-medium mb-2">{template.name}</h3>
                      <p className="text-sm text-gray-600">{template.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Personal Information */}
              <div>
                <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Full Name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="tel"
                    placeholder="Phone"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Location"
                    value={formData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <textarea
                  placeholder="Professional Summary"
                  value={formData.summary}
                  onChange={(e) => handleInputChange('summary', e.target.value)}
                  rows={3}
                  className="w-full mt-4 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Experience */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Work Experience</h2>
                  <button
                    onClick={() => addArrayItem('experience', { company: '', position: '', duration: '', description: '' })}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition text-sm inline-flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add Experience</span>
                  </button>
                </div>
                {formData.experience.map((exp, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <input
                        type="text"
                        placeholder="Company"
                        value={exp.company}
                        onChange={(e) => handleArrayChange('experience', index, 'company', e.target.value)}
                        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder="Position"
                        value={exp.position}
                        onChange={(e) => handleArrayChange('experience', index, 'position', e.target.value)}
                        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder="Duration (e.g., 2020-2023)"
                        value={exp.duration}
                        onChange={(e) => handleArrayChange('experience', index, 'duration', e.target.value)}
                        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <textarea
                      placeholder="Job Description"
                      value={exp.description}
                      onChange={(e) => handleArrayChange('experience', index, 'description', e.target.value)}
                      rows={3}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    {formData.experience.length > 1 && (
                      <button
                        onClick={() => removeArrayItem('experience', index)}
                        className="mt-2 text-red-500 hover:text-red-700 text-sm inline-flex items-center gap-1"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Remove</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* Education */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Education</h2>
                  <button
                    onClick={() => addArrayItem('education', { institution: '', degree: '', year: '' })}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition text-sm inline-flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add Education</span>
                  </button>
                </div>
                {formData.education.map((edu, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <input
                        type="text"
                        placeholder="Institution"
                        value={edu.institution}
                        onChange={(e) => handleArrayChange('education', index, 'institution', e.target.value)}
                        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder="Degree"
                        value={edu.degree}
                        onChange={(e) => handleArrayChange('education', index, 'degree', e.target.value)}
                        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      <input
                        type="text"
                        placeholder="Year"
                        value={edu.year}
                        onChange={(e) => handleArrayChange('education', index, 'year', e.target.value)}
                        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    {formData.education.length > 1 && (
                      <button
                        onClick={() => removeArrayItem('education', index)}
                        className="mt-2 text-red-500 hover:text-red-700 text-sm inline-flex items-center gap-1"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Remove</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* Skills */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Skills</h2>
                  <button
                    onClick={addSkill}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition text-sm inline-flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add Skill</span>
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {formData.skills.map((skill, index) => (
                    <div key={index} className="flex space-x-2">
                      <input
                        type="text"
                        placeholder="Skill"
                        value={skill}
                        onChange={(e) => handleSkillChange(index, e.target.value)}
                        className="flex-1 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                      {formData.skills.length > 1 && (
                        <button
                          onClick={() => removeSkill(index)}
                          className="text-red-500 hover:text-red-700 px-2"
                          aria-label="Remove skill"
                          title="Remove skill"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Projects */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Projects</h2>
                  <button
                    onClick={() => addArrayItem('projects', { name: '', description: '', technologies: '' })}
                    className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition text-sm inline-flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add Project</span>
                  </button>
                </div>
                {formData.projects.map((project, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <input
                      type="text"
                      placeholder="Project Name"
                      value={project.name}
                      onChange={(e) => handleArrayChange('projects', index, 'name', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded mb-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <textarea
                      placeholder="Project Description"
                      value={project.description}
                      onChange={(e) => handleArrayChange('projects', index, 'description', e.target.value)}
                      rows={3}
                      className="w-full p-2 border border-gray-300 rounded mb-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <input
                      type="text"
                      placeholder="Technologies Used (comma-separated)"
                      value={project.technologies}
                      onChange={(e) => handleArrayChange('projects', index, 'technologies', e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    {formData.projects.length > 1 && (
                      <button
                        onClick={() => removeArrayItem('projects', index)}
                        className="mt-2 text-red-500 hover:text-red-700 text-sm inline-flex items-center gap-1"
                      >
                        <Trash2 className="h-4 w-4" />
                        <span>Remove</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>

              {/* Generate Button */}
              <div className="text-center">
                {error && (
                  <p className="mb-4 text-sm font-medium text-red-600">{error}</p>
                )}
                <button
                  onClick={handleGenerate}
                  disabled={!selectedTemplate || generating}
                  className="bg-blue-500 text-white px-8 py-4 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition text-lg font-medium inline-flex items-center gap-2"
                >
                  {generating ? <Loader2 className="h-5 w-5 animate-spin" /> : <FilePlus2 className="h-5 w-5" />}
                  <span>{generating ? 'Generating Resume...' : 'Generate Resume'}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumeWizard;
