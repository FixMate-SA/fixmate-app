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
  ];

  const levels = [
    { id: 'all', name: 'All Levels' },
    { id: 'beginner', name: 'Beginner' },
    { id: 'intermediate', name: 'Intermediate' },
    { id: 'advanced', name: 'Advanced' },
  ];

  // Sample course data (replace with API call)
  const sampleCourses = [
    {
      id: '1',
      title: 'Electrical Safety Fundamentals',
      description: 'Learn essential electrical safety practices and regulations for South African homes.',
      category: 'electrical',
      difficulty_level: 'beginner',
      duration_minutes: 120,
      instructor_name: 'John Smith',
      thumbnail_url: 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?w=400',
      is_featured: true,
      enrollment_count: 234,
      rating: 4.8,
    },
    {
      id: '2',
      title: 'Plumbing Basics for Beginners',
      description: 'Master basic plumbing repairs and installations with hands-on techniques.',
      category: 'plumbing',
      difficulty_level: 'beginner',
      duration_minutes: 90,
      instructor_name: 'Sarah Johnson',
      thumbnail_url: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
      is_featured: true,
      enrollment_count: 189,
      rating: 4.7,
    },
    {
      id: '3',
      title: 'Advanced Carpentry Techniques',
      description: 'Take your woodworking skills to the next level with advanced joinery and finishing.',
      category: 'carpentry',
      difficulty_level: 'advanced',
      duration_minutes: 180,
      instructor_name: 'Michael Brown',
      thumbnail_url: 'https://images.unsplash.com/photo-1504148455328-d24b4c77c093?w=400',
      is_featured: false,
      enrollment_count: 156,
      rating: 4.9,
    },
    {
      id: '4',
      title: 'Running Your Fixer Business',
      description: 'Learn how to price jobs, manage clients, and grow your service business.',
      category: 'business',
      difficulty_level: 'intermediate',
      duration_minutes: 150,
      instructor_name: 'Lisa Davis',
      thumbnail_url: 'https://images.unsplash.com/photo-1553484771-371a605b060b?w=400',
      is_featured: true,
      enrollment_count: 298,
      rating: 4.6,
    },
    {
      id: '5',
      title: 'Paint Application & Color Theory',
      description: 'Professional painting techniques and color selection for interior and exterior work.',
      category: 'painting',
      difficulty_level: 'intermediate',
      duration_minutes: 135,
      instructor_name: 'David Wilson',
      thumbnail_url: 'https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400',
      is_featured: false,
      enrollment_count: 167,
      rating: 4.5,
    },
    {
      id: '6',
      title: 'Workplace Safety & Compliance',
      description: 'Essential safety practices and South African compliance requirements for fixers.',
      category: 'safety',
      difficulty_level: 'beginner',
      duration_minutes: 75,
      instructor_name: 'Emma Thompson',
      thumbnail_url: 'https://images.unsplash.com/photo-1585121071761-2e33c4bc4b91?w=400',
      is_featured: true,
      enrollment_count: 345,
      rating: 4.8,
    },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setCourses(sampleCourses);
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
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Featured Courses</h2>
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
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{course.title}</h3>
              <p className="text-sm text-gray-600 mb-3">{course.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                <span>👨‍🏫 {course.instructor_name}</span>
                <span>⏱️ {formatDuration(course.duration_minutes)}</span>
              </div>
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyColor(course.difficulty_level)}`}>
                  {course.difficulty_level}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-yellow-500">⭐</span>
                  <span className="text-sm">{course.rating}</span>
                  <span className="text-sm text-gray-500">({course.enrollment_count})</span>
                </div>
              </div>
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
                Start Learning
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* All Courses */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">All Courses</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map(course => (
            <div key={course.id} className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <img 
                src={course.thumbnail_url} 
                alt={course.title}
                className="w-full h-32 object-cover rounded-t-lg"
              />
              <div className="p-4">
                <h3 className="font-semibold text-gray-900 mb-2">{course.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{course.description}</p>
                <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
                  <span>👨‍🏫 {course.instructor_name}</span>
                  <span>⏱️ {formatDuration(course.duration_minutes)}</span>
                </div>
                <div className="flex items-center justify-between mb-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${getDifficultyColor(course.difficulty_level)}`}>
                    {course.difficulty_level}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-yellow-500">⭐</span>
                    <span className="text-sm">{course.rating}</span>
                    <span className="text-sm text-gray-500">({course.enrollment_count})</span>
                  </div>
                </div>
                <button className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors">
                  Enroll Now
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Partner Institutions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Our Partner Institutions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl mb-2">🏛️</div>
            <p className="text-sm font-medium">University of Cape Town</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl mb-2">🎓</div>
            <p className="text-sm font-medium">Wits University</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl mb-2">🏫</div>
            <p className="text-sm font-medium">TVET Colleges</p>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-3xl mb-2">🔧</div>
            <p className="text-sm font-medium">Trade Associations</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningPlatform;