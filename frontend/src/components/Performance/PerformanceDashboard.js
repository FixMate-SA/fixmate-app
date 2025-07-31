import React, { useState, useEffect, memo } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';

// Performance metrics collection
const usePerformanceMetrics = () => {
  const [metrics, setMetrics] = useState({
    loadTime: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    firstInputDelay: 0,
    cumulativeLayoutShift: 0,
    bundleSize: 0,
    cacheHitRate: 0,
    apiResponseTime: 0,
    memoryUsage: 0,
    networkInfo: null
  });

  useEffect(() => {
    // Get performance metrics
    const collectMetrics = () => {
      // Navigation timing
      if (performance.getEntriesByType) {
        const navigation = performance.getEntriesByType('navigation')[0];
        if (navigation) {
          setMetrics(prev => ({
            ...prev,
            loadTime: navigation.loadEventEnd - navigation.loadEventStart
          }));
        }

        // Paint timing
        const paintEntries = performance.getEntriesByType('paint');
        paintEntries.forEach(entry => {
          if (entry.name === 'first-contentful-paint') {
            setMetrics(prev => ({
              ...prev,
              firstContentfulPaint: entry.startTime
            }));
          }
        });

        // Largest Contentful Paint
        if ('PerformanceObserver' in window) {
          try {
            const lcpObserver = new PerformanceObserver((list) => {
              const entries = list.getEntries();
              const lastEntry = entries[entries.length - 1];
              setMetrics(prev => ({
                ...prev,
                largestContentfulPaint: lastEntry.startTime
              }));
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

            // First Input Delay
            const fidObserver = new PerformanceObserver((list) => {
              const entries = list.getEntries();
              entries.forEach(entry => {
                if (entry.processingStart) {
                  setMetrics(prev => ({
                    ...prev,
                    firstInputDelay: entry.processingStart - entry.startTime
                  }));
                }
              });
            });
            fidObserver.observe({ entryTypes: ['first-input'] });

            // Cumulative Layout Shift
            const clsObserver = new PerformanceObserver((list) => {
              let clsValue = 0;
              list.getEntries().forEach(entry => {
                if (!entry.hadRecentInput) {
                  clsValue += entry.value;
                }
              });
              setMetrics(prev => ({
                ...prev,
                cumulativeLayoutShift: clsValue
              }));
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
          } catch (error) {
            console.warn('Performance Observer not fully supported:', error);
          }
        }
      }

      // Memory usage
      if (performance.memory) {
        setMetrics(prev => ({
          ...prev,
          memoryUsage: {
            used: performance.memory.usedJSHeapSize,
            total: performance.memory.totalJSHeapSize,
            limit: performance.memory.jsHeapSizeLimit
          }
        }));
      }

      // Network information
      if (navigator.connection) {
        setMetrics(prev => ({
          ...prev,
          networkInfo: {
            effectiveType: navigator.connection.effectiveType,
            downlink: navigator.connection.downlink,
            rtt: navigator.connection.rtt,
            saveData: navigator.connection.saveData
          }
        }));
      }

      // Bundle size estimation
      const scripts = document.querySelectorAll('script[src]');
      let totalSize = 0;
      scripts.forEach(script => {
        // This is an approximation - in real app you'd get actual sizes
        totalSize += script.src.length * 100; // Rough estimation
      });
      
      setMetrics(prev => ({
        ...prev,
        bundleSize: totalSize
      }));
    };

    // Collect metrics after page load
    if (document.readyState === 'complete') {
      collectMetrics();
    } else {
      window.addEventListener('load', collectMetrics);
    }

    return () => {
      window.removeEventListener('load', collectMetrics);
    };
  }, []);

  return metrics;
};

// Performance score calculator
const calculatePerformanceScore = (metrics) => {
  let score = 100;
  
  // Deduct points based on Core Web Vitals
  if (metrics.largestContentfulPaint > 2500) score -= 20;
  else if (metrics.largestContentfulPaint > 1500) score -= 10;
  
  if (metrics.firstInputDelay > 100) score -= 20;
  else if (metrics.firstInputDelay > 50) score -= 10;
  
  if (metrics.cumulativeLayoutShift > 0.25) score -= 20;
  else if (metrics.cumulativeLayoutShift > 0.1) score -= 10;
  
  if (metrics.firstContentfulPaint > 3000) score -= 15;
  else if (metrics.firstContentfulPaint > 1500) score -= 8;
  
  return Math.max(0, Math.round(score));
};

// Performance metric card component
const MetricCard = memo(({ title, value, unit, threshold, icon, description }) => {
  const getStatusColor = () => {
    if (threshold) {
      if (value <= threshold.good) return 'text-green-600 bg-green-50 border-green-200';
      if (value <= threshold.needs_improvement) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      return 'text-red-600 bg-red-50 border-red-200';
    }
    return 'text-blue-600 bg-blue-50 border-blue-200';
  };

  const formatValue = () => {
    if (typeof value === 'number') {
      if (unit === 'ms') return `${Math.round(value)}${unit}`;
      if (unit === 'MB') return `${(value / 1024 / 1024).toFixed(1)}${unit}`;
      if (unit === '%') return `${Math.round(value * 100)}${unit}`;
      return `${value}${unit || ''}`;
    }
    return value;
  };

  return (
    <div className={`p-4 rounded-lg border ${getStatusColor()}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center">
          <span className="text-2xl mr-2">{icon}</span>
          <h3 className="font-medium text-sm">{title}</h3>
        </div>
        <div className="text-2xl font-bold">
          {formatValue()}
        </div>
      </div>
      {description && (
        <p className="text-xs opacity-75">{description}</p>
      )}
    </div>
  );
});

MetricCard.displayName = 'MetricCard';

// Main Performance Dashboard Component
const PerformanceDashboard = () => {
  const { language, translations } = useLanguage();
  const metrics = usePerformanceMetrics();
  const [refreshKey, setRefreshKey] = useState(0);
  
  const performanceScore = calculatePerformanceScore(metrics);
  
  const refreshMetrics = () => {
    setRefreshKey(prev => prev + 1);
    window.location.reload();
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const coreWebVitals = [
    {
      title: 'Largest Contentful Paint',
      value: metrics.largestContentfulPaint,
      unit: 'ms',
      icon: '🎨',
      threshold: { good: 2500, needs_improvement: 4000 },
      description: 'Time to render the largest content element'
    },
    {
      title: 'First Input Delay',
      value: metrics.firstInputDelay,
      unit: 'ms',
      icon: '⚡',
      threshold: { good: 100, needs_improvement: 300 },
      description: 'Time from first user input to browser response'
    },
    {
      title: 'Cumulative Layout Shift',
      value: metrics.cumulativeLayoutShift,
      unit: '',
      icon: '📐',
      threshold: { good: 0.1, needs_improvement: 0.25 },
      description: 'Visual stability of page elements'
    }
  ];

  const additionalMetrics = [
    {
      title: 'First Contentful Paint',
      value: metrics.firstContentfulPaint,
      unit: 'ms',
      icon: '🏁',
      description: 'Time to first content render'
    },
    {
      title: 'Page Load Time',
      value: metrics.loadTime,
      unit: 'ms',
      icon: '⏱️',
      description: 'Total page load duration'
    },
    {
      title: 'Bundle Size (Est.)',
      value: metrics.bundleSize,
      unit: 'KB',
      icon: '📦',
      description: 'Estimated JavaScript bundle size'
    },
    {
      title: 'Memory Usage',
      value: metrics.memoryUsage?.used || 0,
      unit: 'MB',
      icon: '🧠',
      description: 'JavaScript heap memory usage'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              ⚡ {translations.performance_dashboard || 'Performance Dashboard'}
            </h1>
            <p className="text-gray-600 mt-1">
              {translations.performance_description || 'Monitor Core Web Vitals and app performance metrics'}
            </p>
          </div>
          <button
            onClick={refreshMetrics}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center"
          >
            <span className="mr-2">🔄</span>
            Refresh
          </button>
        </div>

        {/* Performance Score */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="text-center">
            <div className={`text-6xl font-bold mb-2 ${getScoreColor(performanceScore)}`}>
              {performanceScore}
            </div>
            <div className="text-gray-600 text-lg">
              {translations.performance_score || 'Performance Score'}
            </div>
            <div className="text-sm text-gray-500 mt-2">
              {performanceScore >= 90 && '🎉 Excellent performance!'}
              {performanceScore >= 50 && performanceScore < 90 && '⚡ Good performance with room for improvement'}
              {performanceScore < 50 && '🐌 Performance needs optimization'}
            </div>
          </div>
        </div>
      </div>

      {/* Core Web Vitals */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          🎯 Core Web Vitals
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {coreWebVitals.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>
      </div>

      {/* Additional Performance Metrics */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          📊 Additional Metrics
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {additionalMetrics.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>
      </div>

      {/* Network Information */}
      {metrics.networkInfo && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            🌐 Network Information
          </h2>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {metrics.networkInfo.effectiveType}
                </div>
                <div className="text-sm text-blue-700">Connection Type</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {metrics.networkInfo.downlink} Mbps
                </div>
                <div className="text-sm text-green-700">Downlink Speed</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {metrics.networkInfo.rtt}ms
                </div>
                <div className="text-sm text-purple-700">Round Trip Time</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {metrics.networkInfo.saveData ? 'ON' : 'OFF'}
                </div>
                <div className="text-sm text-orange-700">Data Saver</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Performance Recommendations */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          💡 Performance Recommendations
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-800 mb-2">Optimization Tips</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Enable PWA installation for better caching</li>
              <li>• Use optimized images with lazy loading</li>
              <li>• Minimize JavaScript bundle size</li>
              <li>• Enable service worker for offline capability</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-gray-800 mb-2">Phase 4B Features</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Code splitting and lazy loading implemented</li>
              <li>• React Query for API response caching</li>
              <li>• Image optimization with WebP support</li>
              <li>• Performance monitoring and metrics</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default memo(PerformanceDashboard);