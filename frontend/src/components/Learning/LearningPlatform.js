import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const LearningPlatform = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');

  const categories = [
    { id: 'all', name: 'All Categories', icon: '📚' },
    { id: 'electrical', name: 'Electrical', icon: '⚡' },
    { id: 'plumbing', name: 'Plumbing', icon: '🔧' },
    { id: 'carpentry', name: 'Carpentry', icon: '🔨' },
    { id: 'painting', name: 'Painting', icon: '🎨' },
    { id: 'general', name: 'General Handyman', icon: '🛠️' },
    { id: 'business', name: 'Business Skills', icon: '💼' },
    { id: 'safety', name: 'Safety & Compliance', icon: '🦺' },
    { id: 'technology', name: 'Technology', icon: '💻' },
    { id: 'project-management', name: 'Project Management', icon: '📋' },
    { id: 'communication', name: 'Communication', icon: '🗣️' },
    { id: 'finance', name: 'Finance', icon: '💰' },
    { id: 'marketing', name: 'Marketing', icon: '📢' },
    { id: 'personal-development', name: 'Personal Development', icon: '🌟' },
  ];

  const levels = [
    { id: 'all', name: 'All Levels' },
    { id: 'beginner', name: 'Beginner' },
    { id: 'intermediate', name: 'Intermediate' },
    { id: 'advanced', name: 'Advanced' },
  ];

  // Real free courses with certificates from major platforms
  const realFreeCourses = [
    // Google Courses
    {
      id: 'google-digital-marketing',
      title: 'Google Digital Marketing & E-commerce Certificate',
      description: 'Learn digital marketing fundamentals and grow your business online. Get job-ready skills for high-growth fields.',
      category: 'marketing',
      difficulty_level: 'beginner',
      duration_minutes: 1800, // 30 hours
      instructor_name: 'Google',
      thumbnail_url: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400',
      is_featured: true,
      enrollment_count: 125000,
      rating: 4.7,
      certificate_available: true,
      platform: 'Coursera',
      course_url: 'https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce',
      skills: ['Digital Marketing', 'E-commerce', 'Google Analytics', 'Google Ads'],
      certificate_type: 'Professional Certificate'
    },
    {
      id: 'google-project-management',
      title: 'Google Project Management Certificate',
      description: 'Learn project management fundamentals and methodologies. Perfect for fixers managing multiple jobs.',
      category: 'project-management',
      difficulty_level: 'beginner',
      duration_minutes: 1440, // 24 hours
      instructor_name: 'Google',
      thumbnail_url: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400',
      is_featured: true,
      enrollment_count: 180000,
      rating: 4.8,
      certificate_available: true,
      platform: 'Coursera',
      course_url: 'https://www.coursera.org/professional-certificates/google-project-management',
      skills: ['Project Management', 'Agile', 'Scrum', 'Risk Management'],
      certificate_type: 'Professional Certificate'
    },
    {
      id: 'google-data-analytics',
      title: 'Google Data Analytics Certificate',
      description: 'Learn data analysis to make better business decisions. Analyze customer data and business metrics.',
      category: 'technology',
      difficulty_level: 'beginner',
      duration_minutes: 1200, // 20 hours
      instructor_name: 'Google',
      thumbnail_url: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400',
      is_featured: true,
      enrollment_count: 95000,
      rating: 4.6,
      certificate_available: true,
      platform: 'Coursera',
      course_url: 'https://www.coursera.org/professional-certificates/google-data-analytics',
      skills: ['Data Analysis', 'SQL', 'R Programming', 'Tableau'],
      certificate_type: 'Professional Certificate'
    },

    // Microsoft Learn Courses
    {
      id: 'microsoft-azure-fundamentals',
      title: 'Microsoft Azure Fundamentals',
      description: 'Learn cloud computing basics and Microsoft Azure services. Essential for modern business operations.',
      category: 'technology',
      difficulty_level: 'beginner',
      duration_minutes: 480, // 8 hours
      instructor_name: 'Microsoft',
      thumbnail_url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400',
      is_featured: false,
      enrollment_count: 75000,
      rating: 4.5,
      certificate_available: true,
      platform: 'Microsoft Learn',
      course_url: 'https://docs.microsoft.com/en-us/learn/certifications/azure-fundamentals/',
      skills: ['Cloud Computing', 'Azure', 'IT Infrastructure'],
      certificate_type: 'Microsoft Certification'
    },
    {
      id: 'microsoft-power-platform',
      title: 'Microsoft Power Platform Fundamentals',
      description: 'Build business applications and automate processes. Perfect for managing fixer operations.',
      category: 'business',
      difficulty_level: 'beginner',
      duration_minutes: 360, // 6 hours
      instructor_name: 'Microsoft',
      thumbnail_url: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400',
      is_featured: false,
      enrollment_count: 45000,
      rating: 4.4,
      certificate_available: true,
      platform: 'Microsoft Learn',
      course_url: 'https://docs.microsoft.com/en-us/learn/certifications/power-platform-fundamentals/',
      skills: ['Business Automation', 'Power Apps', 'Power BI', 'Process Improvement'],
      certificate_type: 'Microsoft Certification'
    },

    // edX Courses
    {
      id: 'mit-introduction-computer-science',
      title: 'Introduction to Computer Science and Programming',
      description: 'Learn programming fundamentals. Useful for fixers wanting to understand smart home technology.',
      category: 'technology',
      difficulty_level: 'beginner',
      duration_minutes: 540, // 9 hours
      instructor_name: 'MIT',
      thumbnail_url: 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400',
      is_featured: false,
      enrollment_count: 67000,
      rating: 4.7,
      certificate_available: true,
      platform: 'edX',
      course_url: 'https://www.edx.org/course/introduction-to-computer-science-and-programming-7',
      skills: ['Python Programming', 'Problem Solving', 'Computational Thinking'],
      certificate_type: 'Verified Certificate'
    },
    {
      id: 'harvard-business-fundamentals',
      title: 'Introduction to Business',
      description: 'Learn business fundamentals including finance, marketing, and operations for your fixer business.',
      category: 'business',
      difficulty_level: 'beginner',
      duration_minutes: 480, // 8 hours
      instructor_name: 'Harvard Business School',
      thumbnail_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400',
      is_featured: true,
      enrollment_count: 89000,
      rating: 4.6,
      certificate_available: true,
      platform: 'edX',
      course_url: 'https://www.edx.org/course/introduction-to-business',
      skills: ['Business Strategy', 'Financial Management', 'Marketing', 'Operations'],
      certificate_type: 'Verified Certificate'
    },

    // LinkedIn Learning Free Courses
    {
      id: 'linkedin-communication-skills',
      title: 'Effective Communication Skills',
      description: 'Improve client communication and build stronger relationships. Essential for service providers.',
      category: 'communication',
      difficulty_level: 'beginner',
      duration_minutes: 180, // 3 hours
      instructor_name: 'LinkedIn Learning',
      thumbnail_url: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400',
      is_featured: true,
      enrollment_count: 156000,
      rating: 4.5,
      certificate_available: true,
      platform: 'LinkedIn Learning',
      course_url: 'https://www.linkedin.com/learning/effective-listening',
      skills: ['Communication', 'Active Listening', 'Client Relations', 'Presentation Skills'],
      certificate_type: 'LinkedIn Certificate'
    },
    {
      id: 'linkedin-time-management',
      title: 'Time Management Fundamentals',
      description: 'Learn to manage multiple jobs efficiently and improve productivity as a fixer.',
      category: 'personal-development',
      difficulty_level: 'beginner',
      duration_minutes: 120, // 2 hours
      instructor_name: 'LinkedIn Learning',
      thumbnail_url: 'https://images.unsplash.com/photo-1506784693919-ef06d93c28be?w=400',
      is_featured: false,
      enrollment_count: 98000,
      rating: 4.4,
      certificate_available: true,
      platform: 'LinkedIn Learning',
      course_url: 'https://www.linkedin.com/learning/time-management-fundamentals',
      skills: ['Time Management', 'Productivity', 'Task Prioritization', 'Work-Life Balance'],
      certificate_type: 'LinkedIn Certificate'
    },

    // FreeCodeCamp Courses
    {
      id: 'freecodecamp-web-development',
      title: 'Responsive Web Design',
      description: 'Learn to build websites. Useful for fixers wanting to create their own business websites.',
      category: 'technology',
      difficulty_level: 'beginner',
      duration_minutes: 1800, // 30 hours
      instructor_name: 'freeCodeCamp',
      thumbnail_url: 'https://images.unsplash.com/photo-1467232004584-a241de8bcf5d?w=400',
      is_featured: false,
      enrollment_count: 234000,
      rating: 4.8,
      certificate_available: true,
      platform: 'freeCodeCamp',
      course_url: 'https://www.freecodecamp.org/learn/responsive-web-design/',
      skills: ['HTML', 'CSS', 'Web Design', 'Responsive Design'],
      certificate_type: 'freeCodeCamp Certificate'
    },

    // Coursera Free Courses
    {
      id: 'yale-financial-markets',
      title: 'Financial Markets',
      description: 'Understand financial markets and investment principles. Manage your fixer business finances better.',
      category: 'finance',
      difficulty_level: 'intermediate',
      duration_minutes: 1980, // 33 hours
      instructor_name: 'Yale University',
      thumbnail_url: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400',
      is_featured: false,
      enrollment_count: 145000,
      rating: 4.6,
      certificate_available: true,
      platform: 'Coursera',
      course_url: 'https://www.coursera.org/learn/financial-markets-global',
      skills: ['Financial Planning', 'Investment', 'Risk Management', 'Economics'],
      certificate_type: 'Course Certificate'
    },
    {
      id: 'stanford-entrepreneurship',
      title: 'Entrepreneurship: Launching an Innovative Business',
      description: 'Learn to start and grow your fixer business. From idea validation to scaling operations.',
      category: 'business',
      difficulty_level: 'intermediate',
      duration_minutes: 720, // 12 hours
      instructor_name: 'Stanford University',
      thumbnail_url: 'https://images.unsplash.com/photo-1553484771-cc0d9b8c2b33?w=400',
      is_featured: true,
      enrollment_count: 78000,
      rating: 4.7,
      certificate_available: true,
      platform: 'Coursera',
      course_url: 'https://www.coursera.org/learn/launching-innovative-business',
      skills: ['Entrepreneurship', 'Business Planning', 'Innovation', 'Marketing Strategy'],
      certificate_type: 'Course Certificate'
    },

    // SANS Cyber Aces (Cybersecurity)
    {
      id: 'cybersecurity-basics',
      title: 'Cybersecurity Fundamentals',
      description: 'Learn basic cybersecurity principles. Important for fixers working with smart home devices.',
      category: 'technology',
      difficulty_level: 'beginner',
      duration_minutes: 300, // 5 hours
      instructor_name: 'SANS Institute',
      thumbnail_url: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=400',
      is_featured: false,
      enrollment_count: 34000,
      rating: 4.5,
      certificate_available: true,
      platform: 'SANS Cyber Aces',
      course_url: 'https://www.cyberaces.org/',
      skills: ['Cybersecurity', 'Network Security', 'Privacy Protection', 'Risk Assessment'],
      certificate_type: 'SANS Certificate'
    },

    // Trade-Specific Courses
    {
      id: 'electrical-safety-osha',
      title: 'Electrical Safety Standards and Compliance',
      description: 'Learn OSHA electrical safety standards and South African electrical compliance requirements.',
      category: 'electrical',
      difficulty_level: 'beginner',
      duration_minutes: 240, // 4 hours
      instructor_name: 'OSHA Training Institute',
      thumbnail_url: 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=400',
      is_featured: true,
      enrollment_count: 67000,
      rating: 4.8,
      certificate_available: true,
      platform: 'OSHA Training',
      course_url: 'https://www.osha.gov/training/outreach',
      skills: ['Electrical Safety', 'OSHA Compliance', 'Risk Assessment', 'Safety Protocols'],
      certificate_type: 'OSHA Certificate'
    },
    {
      id: 'green-building-fundamentals',
      title: 'Green Building and Sustainable Construction',
      description: 'Learn sustainable building practices and green construction techniques for modern projects.',
      category: 'general',
      difficulty_level: 'intermediate',
      duration_minutes: 420, // 7 hours
      instructor_name: 'U.S. Green Building Council',
      thumbnail_url: 'https://images.unsplash.com/photo-1518005020951-eccb494ad742?w=400',
      is_featured: false,
      enrollment_count: 45000,
      rating: 4.6,
      certificate_available: true,
      platform: 'USGBC',
      course_url: 'https://www.usgbc.org/education',
      skills: ['Sustainable Construction', 'Energy Efficiency', 'Green Materials', 'Environmental Compliance'],
      certificate_type: 'USGBC Certificate'
    },

    // Customer Service & Soft Skills
    {
      id: 'customer-service-excellence',
      title: 'Customer Service Excellence',
      description: 'Master customer service skills to build a successful fixer business with repeat clients.',
      category: 'communication',
      difficulty_level: 'beginner',
      duration_minutes: 180, // 3 hours
      instructor_name: 'Customer Service Institute',
      thumbnail_url: 'https://images.unsplash.com/photo-1573496527892-904f897eb744?w=400',
      is_featured: true,
      enrollment_count: 123000,
      rating: 4.7,
      certificate_available: true,
      platform: 'Alison',
      course_url: 'https://alison.com/course/customer-service-training',
      skills: ['Customer Service', 'Conflict Resolution', 'Communication', 'Problem Solving'],
      certificate_type: 'Alison Certificate'
    }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setCourses(realFreeCourses);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredCourses = courses.filter(course => {
    const categoryMatch = selectedCategory === 'all' || course.category === selectedCategory;
    const levelMatch = selectedLevel === 'all' || course.difficulty_level === selectedLevel;
    return categoryMatch && levelMatch;
  });

  const getDifficultyColor = (level) => {
    switch (level) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${remainingMinutes}m`;
    }
    return `${remainingMinutes}m`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">FixMate Learning Academy</h1>
        <p className="text-blue-100">
          Enhance your skills with free courses from our partner institutions. 
          Learn new techniques, improve your craft, and grow your business.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-full">
              <span className="text-2xl">📚</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Total Courses</p>
              <p className="text-xl font-semibold">{courses.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-full">
              <span className="text-2xl">🏆</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-xl font-semibold">0</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-full">
              <span className="text-2xl">⏱️</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Learning Hours</p>
              <p className="text-xl font-semibold">0h</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-full">
              <span className="text-2xl">🎓</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Certificates</p>
              <p className="text-xl font-semibold">0</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.icon} {category.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty Level</label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {levels.map(level => (
                <option key={level.id} value={level.id}>
                  {level.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Featured Courses */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Featured Courses with Certificates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.filter(course => course.is_featured).map(course => (
            <div key={course.id} className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
              <div className="relative">
                <img 
                  src={course.thumbnail_url} 
                  alt={course.title}
                  className="w-full h-32 object-cover rounded-md mb-3"
                />
                <span className="absolute top-2 right-2 bg-yellow-400 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">
                  ⭐ Featured
                </span>
                {course.certificate_available && (
                  <span className="absolute top-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                    🎓 Certificate
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{course.title}</h3>
              <p className="text-sm text-gray-600 mb-3">{course.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                <span>👨‍🏫 {course.instructor_name}</span>
                <span>⏱️ {formatDuration(course.duration_minutes)}</span>
              </div>
              <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                  📚 {course.platform}
                </span>
                <span className="text-green-600 font-medium">
                  {course.certificate_type}
                </span>
              </div>
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyColor(course.difficulty_level)}`}>
                  {course.difficulty_level}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-yellow-500">⭐</span>
                  <span className="text-sm">{course.rating}</span>
                  <span className="text-sm text-gray-500">({course.enrollment_count.toLocaleString()})</span>
                </div>
              </div>
              <div className="mb-3">
                <p className="text-xs text-gray-600 mb-1">Skills you'll learn:</p>
                <div className="flex flex-wrap gap-1">
                  {course.skills.slice(0, 3).map((skill, index) => (
                    <span key={index} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                      {skill}
                    </span>
                  ))}
                  {course.skills.length > 3 && (
                    <span className="text-xs text-gray-500">+{course.skills.length - 3} more</span>
                  )}
                </div>
              </div>
              <a 
                href={course.course_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors block text-center"
              >
                Start Learning Free
              </a>
            </div>
          ))}
        </div>
      </div>

      {/* All Courses */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">All Free Courses with Certificates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map(course => (
            <div key={course.id} className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div className="relative">
                <img 
                  src={course.thumbnail_url} 
                  alt={course.title}
                  className="w-full h-32 object-cover rounded-t-lg"
                />
                {course.certificate_available && (
                  <span className="absolute top-2 right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full font-medium">
                    🎓 Certificate
                  </span>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-2">{course.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{course.description}</p>
                <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
                  <span>👨‍🏫 {course.instructor_name}</span>
                  <span>⏱️ {formatDuration(course.duration_minutes)}</span>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                  <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    📚 {course.platform}
                  </span>
                  <span className="text-green-600 font-medium text-xs">
                    {course.certificate_type}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyColor(course.difficulty_level)}`}>
                    {course.difficulty_level}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-yellow-500">⭐</span>
                    <span className="text-sm">{course.rating}</span>
                    <span className="text-sm text-gray-500">({course.enrollment_count.toLocaleString()})</span>
                  </div>
                </div>
                <div className="mb-3">
                  <p className="text-xs text-gray-600 mb-1">Skills:</p>
                  <div className="flex flex-wrap gap-1">
                    {course.skills.slice(0, 2).map((skill, index) => (
                      <span key={index} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                        {skill}
                      </span>
                    ))}
                    {course.skills.length > 2 && (
                      <span className="text-xs text-gray-500">+{course.skills.length - 2}</span>
                    )}
                  </div>
                </div>
                <a 
                  href={course.course_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors block text-center"
                >
                  Enroll Free
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Partner Learning Platforms */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Our Learning Partners</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
            <div className="text-3xl mb-2">🎓</div>
            <p className="text-sm font-medium">Google</p>
            <p className="text-xs text-gray-600">Professional Certificates</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
            <div className="text-3xl mb-2">💼</div>
            <p className="text-sm font-medium">Microsoft</p>
            <p className="text-xs text-gray-600">Azure & Office Certifications</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
            <div className="text-3xl mb-2">🏛️</div>
            <p className="text-sm font-medium">Coursera</p>
            <p className="text-xs text-gray-600">University Courses</p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
            <div className="text-3xl mb-2">📚</div>
            <p className="text-sm font-medium">edX</p>
            <p className="text-xs text-gray-600">MIT, Harvard & More</p>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors">
            <div className="text-3xl mb-2">💻</div>
            <p className="text-sm font-medium">freeCodeCamp</p>
            <p className="text-xs text-gray-600">Programming & Web Dev</p>
          </div>
          <div className="text-center p-4 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
            <div className="text-3xl mb-2">🔗</div>
            <p className="text-sm font-medium">LinkedIn</p>
            <p className="text-xs text-gray-600">Professional Skills</p>
          </div>
        </div>
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 mb-4">
            All courses are completely free to audit. Certificates are available for a fee or through financial aid on most platforms.
          </p>
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">💡 Pro Tip for Fixers & Clients</h3>
            <p className="text-sm text-blue-800">
              Many platforms offer financial aid for certificates. Apply through the course page to get certified for free! 
              These certificates can help you build credibility with clients and advance your career.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningPlatform;