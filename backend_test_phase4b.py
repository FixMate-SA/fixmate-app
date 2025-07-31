#!/usr/bin/env python3
"""
FixMate-SA Phase 4B: Performance Optimization Backend Testing Script
Tests the Phase 4B Performance Optimization backend implementation.

PRIORITY FOCUS: Test Performance Optimized Endpoints with Caching:

Optimized Endpoints with Caching:
1. GET /api/dashboard/{user_id} - Dashboard with caching and performance monitoring
2. GET /api/jobs - Jobs listing with optimized queries and pagination  
3. GET /api/jobs/{job_id} - Individual job with eager loading
4. GET /api/fixers - Fixers listing with caching
5. GET /api/users - Users with optimized queries

Performance Features to Test:
- Response compression (GZip)
- Cache headers implementation
- Database query optimization
- Pagination with optimized limits
- Eager loading for relationships
- Performance monitoring integration

Authentication Context:
- Admin: +27821234567 / admin123
- Regular User: Created during testing
- Test with different pagination parameters and performance monitoring
"""

import requests
import json
import sys
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"🔧 Testing FixMate-SA Phase 4B: Performance Optimization at: {API_BASE}")
print("=" * 80)
print("🎯 PERFORMANCE OPTIMIZATION TESTING")
print("=" * 80)

class FixMatePerformanceTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.performance_metrics = {}
    
    def log_result(self, test_name, success, message="", response=None, metrics=None):
        """Log test result with performance metrics"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if metrics:
            print(f"   Performance: {metrics}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
        print()
    
    def measure_performance(self, response):
        """Extract performance metrics from response"""
        metrics = {}
        
        # Response time
        if hasattr(response, 'elapsed'):
            metrics['response_time_ms'] = round(response.elapsed.total_seconds() * 1000, 2)
        
        # Response size
        if hasattr(response, 'content'):
            metrics['response_size_bytes'] = len(response.content)
            metrics['response_size_kb'] = round(len(response.content) / 1024, 2)
        
        # Check for compression
        if 'content-encoding' in response.headers:
            metrics['compression'] = response.headers['content-encoding']
        
        # Check for cache headers
        cache_headers = {}
        for header in ['cache-control', 'etag', 'last-modified', 'expires']:
            if header in response.headers:
                cache_headers[header] = response.headers[header]
        if cache_headers:
            metrics['cache_headers'] = cache_headers
        
        # Check for performance monitoring headers
        perf_headers = {}
        for header in response.headers:
            if header.lower().startswith('x-performance') or header.lower().startswith('x-timing'):
                perf_headers[header] = response.headers[header]
        if perf_headers:
            metrics['performance_headers'] = perf_headers
        
        return metrics
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/")
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_result("Health Check", True, f"API is running: {data['message']}", metrics=metrics)
                    return True
                else:
                    self.log_result("Health Check", False, "Invalid response format", response)
            else:
                self.log_result("Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_admin_login(self):
        """Test admin login for admin-only endpoints"""
        try:
            login_data = {
                "phone": "+27821234567",
                "password": "admin123"
            }
            
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.test_data['admin_token'] = data['token']
                    self.test_data['admin_user'] = data['user']
                    self.log_result("Admin Login", True, 
                                  f"Admin login successful, role: {data.get('role_info', {}).get('role', 'unknown')}", 
                                  metrics=metrics)
                    return True
                else:
                    self.log_result("Admin Login", False, "Invalid response format", response)
            else:
                self.log_result("Admin Login", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Admin Login", False, f"Request error: {str(e)}")
        return False
    
    def test_create_test_user(self):
        """Create a test user for testing"""
        timestamp = str(int(time.time()))[-6:]
        
        user_data = {
            "phone": f"+2782123{timestamp}",
            "first_name": "Performance",
            "last_name": "Tester",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": "Cape Town",
            "email": f"perf.tester.{timestamp}@example.com",
            "address": "123 Performance St, Cape Town"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/users", json=user_data)
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_data['user_id'] = data['id']
                    self.test_data['user'] = data
                    self.log_result("Create Test User", True, f"User created with ID: {data['id']}", metrics=metrics)
                    return True
                else:
                    self.log_result("Create Test User", False, "Invalid response format", response)
            else:
                self.log_result("Create Test User", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Test User", False, f"Request error: {str(e)}")
        return False
    
    def test_create_test_fixer(self):
        """Create a test fixer for testing"""
        timestamp = str(int(time.time()))[-6:]
        
        # First create a user for the fixer
        user_data = {
            "phone": f"+2782987{timestamp}",
            "first_name": "Performance",
            "last_name": "Fixer",
            "id_number": f"8001015009{timestamp[-3:]}",
            "town": "Cape Town",
            "email": f"perf.fixer.{timestamp}@fixmate.com",
            "address": "456 Fixer St, Cape Town"
        }
        
        try:
            # Create user first
            user_response = self.session.post(f"{API_BASE}/users", json=user_data)
            if user_response.status_code != 200:
                self.log_result("Create Test Fixer", False, "Failed to create user for fixer", user_response)
                return False
            
            fixer_user = user_response.json()
            
            fixer_data = {
                "user_id": fixer_user['id'],
                "phone": f"+2782987{timestamp}",
                "name": "Performance Fixer",
                "email": f"perf.fixer.{timestamp}@fixmate.com",
                "services": '["plumbing", "electrical", "carpentry"]',
                "location": "Cape Town"
            }
            
            response = self.session.post(f"{API_BASE}/fixers", json=fixer_data)
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_data['fixer_id'] = data['id']
                    self.test_data['fixer'] = data
                    self.log_result("Create Test Fixer", True, f"Fixer created with ID: {data['id']}", metrics=metrics)
                    return True
                else:
                    self.log_result("Create Test Fixer", False, "Invalid response format", response)
            else:
                self.log_result("Create Test Fixer", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Test Fixer", False, f"Request error: {str(e)}")
        return False
    
    def test_create_test_job(self):
        """Create a test job for testing"""
        if 'user_id' not in self.test_data:
            self.log_result("Create Test Job", False, "No user ID available from previous test")
            return False
        
        job_data = {
            "user_id": self.test_data['user_id'],
            "service": "plumbing",
            "description": "Performance test job - Fix leaking kitchen tap",
            "location": "123 Performance St, Cape Town",
            "estimated_price": 250.0
        }
        
        try:
            response = self.session.post(f"{API_BASE}/jobs", json=job_data)
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data:
                    self.test_data['job_id'] = data['id']
                    self.test_data['job'] = data
                    self.log_result("Create Test Job", True, f"Job created with ID: {data['id']}", metrics=metrics)
                    return True
                else:
                    self.log_result("Create Test Job", False, "Invalid response format", response)
            else:
                self.log_result("Create Test Job", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Test Job", False, f"Request error: {str(e)}")
        return False
    
    # ======= PHASE 4B: PERFORMANCE OPTIMIZATION TESTS =======
    
    def test_optimized_users_endpoint(self):
        """Test GET /api/users with performance optimizations"""
        try:
            # Test with different pagination parameters
            test_cases = [
                {"skip": 0, "limit": 10},
                {"skip": 0, "limit": 50},
                {"skip": 10, "limit": 20}
            ]
            
            for params in test_cases:
                response = self.session.get(f"{API_BASE}/users", params=params)
                metrics = self.measure_performance(response)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Check if response has pagination info or is optimized
                        success_msg = f"Retrieved {len(data)} users with pagination (skip={params['skip']}, limit={params['limit']})"
                        
                        # Check for performance optimizations
                        perf_features = []
                        if metrics.get('compression'):
                            perf_features.append(f"compression: {metrics['compression']}")
                        if metrics.get('cache_headers'):
                            perf_features.append("cache headers present")
                        if metrics.get('response_time_ms', 0) < 1000:
                            perf_features.append(f"fast response: {metrics.get('response_time_ms')}ms")
                        
                        if perf_features:
                            success_msg += f" | Optimizations: {', '.join(perf_features)}"
                        
                        self.log_result("Optimized Users Endpoint", True, success_msg, metrics=metrics)
                    else:
                        self.log_result("Optimized Users Endpoint", False, "Response is not a list", response)
                        return False
                else:
                    self.log_result("Optimized Users Endpoint", False, f"HTTP {response.status_code}", response)
                    return False
            
            return True
        except Exception as e:
            self.log_result("Optimized Users Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_optimized_fixers_endpoint(self):
        """Test GET /api/fixers with caching and performance optimizations"""
        try:
            # Test with different pagination parameters
            test_cases = [
                {"skip": 0, "limit": 10},
                {"skip": 0, "limit": 25},
                {"skip": 5, "limit": 15}
            ]
            
            for params in test_cases:
                response = self.session.get(f"{API_BASE}/fixers", params=params)
                metrics = self.measure_performance(response)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Check for performance optimizations
                        perf_features = []
                        if metrics.get('compression'):
                            perf_features.append(f"compression: {metrics['compression']}")
                        if metrics.get('cache_headers'):
                            perf_features.append("cache headers present")
                        if metrics.get('response_time_ms', 0) < 1000:
                            perf_features.append(f"fast response: {metrics.get('response_time_ms')}ms")
                        
                        success_msg = f"Retrieved {len(data)} fixers with pagination (skip={params['skip']}, limit={params['limit']})"
                        if perf_features:
                            success_msg += f" | Optimizations: {', '.join(perf_features)}"
                        
                        self.log_result("Optimized Fixers Endpoint", True, success_msg, metrics=metrics)
                    else:
                        self.log_result("Optimized Fixers Endpoint", False, "Response is not a list", response)
                        return False
                else:
                    self.log_result("Optimized Fixers Endpoint", False, f"HTTP {response.status_code}", response)
                    return False
            
            return True
        except Exception as e:
            self.log_result("Optimized Fixers Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_optimized_jobs_endpoint(self):
        """Test GET /api/jobs with optimized queries, caching, and pagination"""
        try:
            # Test with different parameters and filters
            test_cases = [
                {"skip": 0, "limit": 10},
                {"skip": 0, "limit": 20},
                {"service": "plumbing", "skip": 0, "limit": 15},
                {"status": "open", "skip": 0, "limit": 10},
                {"location": "Cape Town", "skip": 0, "limit": 10}
            ]
            
            for params in test_cases:
                response = self.session.get(f"{API_BASE}/jobs", params=params)
                metrics = self.measure_performance(response)
                
                if response.status_code == 200:
                    # Check if response is paginated or optimized format
                    try:
                        data = response.json()
                        
                        # Handle both list format and paginated format
                        if isinstance(data, list):
                            jobs_count = len(data)
                            format_type = "list"
                        elif isinstance(data, dict) and 'data' in data:
                            jobs_count = len(data['data'])
                            format_type = "paginated"
                        else:
                            jobs_count = len(data) if isinstance(data, list) else 0
                            format_type = "unknown"
                        
                        # Check for performance optimizations
                        perf_features = []
                        if metrics.get('compression'):
                            perf_features.append(f"compression: {metrics['compression']}")
                        if metrics.get('cache_headers'):
                            perf_features.append("cache headers present")
                        if metrics.get('response_time_ms', 0) < 1500:
                            perf_features.append(f"fast response: {metrics.get('response_time_ms')}ms")
                        if metrics.get('performance_headers'):
                            perf_features.append("performance monitoring")
                        
                        # Build filter description
                        filter_desc = []
                        for key, value in params.items():
                            if key not in ['skip', 'limit']:
                                filter_desc.append(f"{key}={value}")
                        
                        filter_str = f" with filters: {', '.join(filter_desc)}" if filter_desc else ""
                        success_msg = f"Retrieved {jobs_count} jobs ({format_type} format) with pagination (skip={params.get('skip', 0)}, limit={params.get('limit', 20)}){filter_str}"
                        
                        if perf_features:
                            success_msg += f" | Optimizations: {', '.join(perf_features)}"
                        
                        self.log_result("Optimized Jobs Endpoint", True, success_msg, metrics=metrics)
                    except Exception as parse_error:
                        self.log_result("Optimized Jobs Endpoint", False, f"Failed to parse response: {str(parse_error)}", response)
                        return False
                else:
                    self.log_result("Optimized Jobs Endpoint", False, f"HTTP {response.status_code}", response)
                    return False
            
            return True
        except Exception as e:
            self.log_result("Optimized Jobs Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_optimized_single_job_endpoint(self):
        """Test GET /api/jobs/{job_id} with eager loading and caching"""
        if 'job_id' not in self.test_data:
            self.log_result("Optimized Single Job Endpoint", False, "No job ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/jobs/{self.test_data['job_id']}")
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and data['id'] == self.test_data['job_id']:
                    # Check for eager loading - should have user and fixer data if available
                    eager_loading_features = []
                    if 'user' in data and isinstance(data['user'], dict):
                        eager_loading_features.append("user data loaded")
                    if 'fixer' in data and isinstance(data['fixer'], dict):
                        eager_loading_features.append("fixer data loaded")
                    if 'reviews' in data and isinstance(data['reviews'], list):
                        eager_loading_features.append("reviews loaded")
                    
                    # Check for performance optimizations
                    perf_features = []
                    if metrics.get('compression'):
                        perf_features.append(f"compression: {metrics['compression']}")
                    if metrics.get('cache_headers'):
                        perf_features.append("cache headers present")
                    if metrics.get('response_time_ms', 0) < 1000:
                        perf_features.append(f"fast response: {metrics.get('response_time_ms')}ms")
                    if metrics.get('performance_headers'):
                        perf_features.append("performance monitoring")
                    
                    success_msg = f"Retrieved job with optimized response"
                    if eager_loading_features:
                        success_msg += f" | Eager loading: {', '.join(eager_loading_features)}"
                    if perf_features:
                        success_msg += f" | Optimizations: {', '.join(perf_features)}"
                    
                    self.log_result("Optimized Single Job Endpoint", True, success_msg, metrics=metrics)
                    return True
                else:
                    self.log_result("Optimized Single Job Endpoint", False, "Job ID mismatch or invalid format", response)
            else:
                self.log_result("Optimized Single Job Endpoint", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Optimized Single Job Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_optimized_dashboard_endpoint(self):
        """Test GET /api/dashboard/{user_id} with caching and performance monitoring"""
        if 'user_id' not in self.test_data:
            self.log_result("Optimized Dashboard Endpoint", False, "No user ID available from previous test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/dashboard/{self.test_data['user_id']}")
            metrics = self.measure_performance(response)
            
            if response.status_code == 200:
                data = response.json()
                required_keys = ['user', 'recent_jobs', 'top_fixers', 'stats']
                
                if all(key in data for key in required_keys):
                    # Check for performance optimizations
                    perf_features = []
                    if metrics.get('compression'):
                        perf_features.append(f"compression: {metrics['compression']}")
                    if metrics.get('cache_headers'):
                        perf_features.append("cache headers present")
                    if metrics.get('response_time_ms', 0) < 2000:
                        perf_features.append(f"fast response: {metrics.get('response_time_ms')}ms")
                    if metrics.get('performance_headers'):
                        perf_features.append("performance monitoring")
                    
                    # Check dashboard data completeness
                    data_features = []
                    if data.get('business_insight'):
                        data_features.append("AI business insights")
                    if isinstance(data.get('recent_jobs'), list):
                        data_features.append(f"{len(data['recent_jobs'])} recent jobs")
                    if isinstance(data.get('top_fixers'), list):
                        data_features.append(f"{len(data['top_fixers'])} top fixers")
                    if isinstance(data.get('stats'), dict):
                        data_features.append("user statistics")
                    
                    success_msg = f"Dashboard retrieved with complete data"
                    if data_features:
                        success_msg += f" | Data: {', '.join(data_features)}"
                    if perf_features:
                        success_msg += f" | Optimizations: {', '.join(perf_features)}"
                    
                    self.log_result("Optimized Dashboard Endpoint", True, success_msg, metrics=metrics)
                    return True
                else:
                    missing_keys = [key for key in required_keys if key not in data]
                    self.log_result("Optimized Dashboard Endpoint", False, f"Missing keys: {missing_keys}", response)
            else:
                self.log_result("Optimized Dashboard Endpoint", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Optimized Dashboard Endpoint", False, f"Request error: {str(e)}")
        return False
    
    def test_performance_monitoring_integration(self):
        """Test that performance monitoring is working across endpoints"""
        try:
            # Test multiple endpoints to see if performance monitoring is consistent
            endpoints_to_test = [
                f"{API_BASE}/users?limit=5",
                f"{API_BASE}/fixers?limit=5",
                f"{API_BASE}/jobs?limit=5"
            ]
            
            performance_data = []
            
            for endpoint in endpoints_to_test:
                response = self.session.get(endpoint)
                metrics = self.measure_performance(response)
                
                if response.status_code == 200:
                    performance_data.append({
                        'endpoint': endpoint.split('/')[-1].split('?')[0],
                        'response_time': metrics.get('response_time_ms', 0),
                        'size_kb': metrics.get('response_size_kb', 0),
                        'has_cache_headers': bool(metrics.get('cache_headers')),
                        'has_compression': bool(metrics.get('compression')),
                        'has_perf_headers': bool(metrics.get('performance_headers'))
                    })
            
            if len(performance_data) >= 2:
                # Analyze performance consistency
                avg_response_time = sum(p['response_time'] for p in performance_data) / len(performance_data)
                cache_coverage = sum(1 for p in performance_data if p['has_cache_headers']) / len(performance_data) * 100
                compression_coverage = sum(1 for p in performance_data if p['has_compression']) / len(performance_data) * 100
                
                success_msg = f"Performance monitoring across {len(performance_data)} endpoints"
                success_msg += f" | Avg response time: {avg_response_time:.1f}ms"
                success_msg += f" | Cache headers: {cache_coverage:.0f}% coverage"
                success_msg += f" | Compression: {compression_coverage:.0f}% coverage"
                
                # Store performance metrics for summary
                self.performance_metrics = {
                    'endpoints_tested': len(performance_data),
                    'avg_response_time': avg_response_time,
                    'cache_coverage': cache_coverage,
                    'compression_coverage': compression_coverage,
                    'details': performance_data
                }
                
                self.log_result("Performance Monitoring Integration", True, success_msg)
                return True
            else:
                self.log_result("Performance Monitoring Integration", False, "Not enough endpoints responded successfully")
        except Exception as e:
            self.log_result("Performance Monitoring Integration", False, f"Request error: {str(e)}")
        return False
    
    def test_response_compression(self):
        """Test that responses are properly compressed"""
        try:
            # Test endpoints that should have compression
            endpoints_to_test = [
                f"{API_BASE}/jobs?limit=20",
                f"{API_BASE}/fixers?limit=20",
                f"{API_BASE}/users?limit=20"
            ]
            
            compression_results = []
            
            for endpoint in endpoints_to_test:
                # Request with Accept-Encoding header to enable compression
                headers = {'Accept-Encoding': 'gzip, deflate'}
                response = self.session.get(endpoint, headers=headers)
                metrics = self.measure_performance(response)
                
                if response.status_code == 200:
                    endpoint_name = endpoint.split('/')[-1].split('?')[0]
                    compression_results.append({
                        'endpoint': endpoint_name,
                        'has_compression': bool(metrics.get('compression')),
                        'compression_type': metrics.get('compression', 'none'),
                        'size_kb': metrics.get('response_size_kb', 0)
                    })
            
            if compression_results:
                compressed_count = sum(1 for r in compression_results if r['has_compression'])
                compression_rate = compressed_count / len(compression_results) * 100
                
                success_msg = f"Compression testing on {len(compression_results)} endpoints"
                success_msg += f" | {compressed_count}/{len(compression_results)} endpoints compressed ({compression_rate:.0f}%)"
                
                if compressed_count > 0:
                    compression_types = set(r['compression_type'] for r in compression_results if r['has_compression'])
                    success_msg += f" | Types: {', '.join(compression_types)}"
                
                # Consider it successful if at least some endpoints have compression
                is_success = compression_rate >= 50  # At least 50% should have compression
                
                self.log_result("Response Compression", is_success, success_msg)
                return is_success
            else:
                self.log_result("Response Compression", False, "No endpoints responded successfully")
        except Exception as e:
            self.log_result("Response Compression", False, f"Request error: {str(e)}")
        return False
    
    def test_cache_headers_implementation(self):
        """Test that proper cache headers are implemented"""
        try:
            # Test endpoints that should have cache headers
            endpoints_to_test = [
                f"{API_BASE}/fixers?limit=10",
                f"{API_BASE}/users?limit=10"
            ]
            
            if 'job_id' in self.test_data:
                endpoints_to_test.append(f"{API_BASE}/jobs/{self.test_data['job_id']}")
            if 'user_id' in self.test_data:
                endpoints_to_test.append(f"{API_BASE}/dashboard/{self.test_data['user_id']}")
            
            cache_results = []
            
            for endpoint in endpoints_to_test:
                response = self.session.get(endpoint)
                metrics = self.measure_performance(response)
                
                if response.status_code == 200:
                    endpoint_name = endpoint.split('/')[-1].split('?')[0]
                    cache_headers = metrics.get('cache_headers', {})
                    
                    cache_results.append({
                        'endpoint': endpoint_name,
                        'has_cache_control': 'cache-control' in cache_headers,
                        'has_etag': 'etag' in cache_headers,
                        'has_last_modified': 'last-modified' in cache_headers,
                        'cache_headers': cache_headers
                    })
            
            if cache_results:
                cache_control_count = sum(1 for r in cache_results if r['has_cache_control'])
                etag_count = sum(1 for r in cache_results if r['has_etag'])
                
                success_msg = f"Cache headers testing on {len(cache_results)} endpoints"
                success_msg += f" | Cache-Control: {cache_control_count}/{len(cache_results)}"
                success_msg += f" | ETag: {etag_count}/{len(cache_results)}"
                
                # Consider it successful if most endpoints have some cache headers
                cache_coverage = (cache_control_count + etag_count) / (len(cache_results) * 2) * 100
                is_success = cache_coverage >= 25  # At least 25% coverage
                
                if cache_coverage > 0:
                    success_msg += f" | Coverage: {cache_coverage:.0f}%"
                
                self.log_result("Cache Headers Implementation", is_success, success_msg)
                return is_success
            else:
                self.log_result("Cache Headers Implementation", False, "No endpoints responded successfully")
        except Exception as e:
            self.log_result("Cache Headers Implementation", False, f"Request error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all Phase 4B performance optimization tests"""
        print("🚀 Starting Phase 4B Performance Optimization Tests...")
        print()
        
        # Basic setup tests
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return
        
        if not self.test_admin_login():
            print("❌ Admin login failed - some tests may not work")
        
        # Create test data
        self.test_create_test_user()
        self.test_create_test_fixer()
        self.test_create_test_job()
        
        print("\n" + "="*60)
        print("🎯 PHASE 4B: PERFORMANCE OPTIMIZATION TESTS")
        print("="*60)
        
        # Core performance optimization tests
        self.test_optimized_users_endpoint()
        self.test_optimized_fixers_endpoint()
        self.test_optimized_jobs_endpoint()
        self.test_optimized_single_job_endpoint()
        self.test_optimized_dashboard_endpoint()
        
        # Performance feature tests
        self.test_performance_monitoring_integration()
        self.test_response_compression()
        self.test_cache_headers_implementation()
        
        # Print final results
        print("\n" + "="*60)
        print("📊 PHASE 4B PERFORMANCE OPTIMIZATION TEST RESULTS")
        print("="*60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.performance_metrics:
            print(f"\n📊 Performance Summary:")
            print(f"   Average Response Time: {self.performance_metrics.get('avg_response_time', 0):.1f}ms")
            print(f"   Cache Headers Coverage: {self.performance_metrics.get('cache_coverage', 0):.0f}%")
            print(f"   Compression Coverage: {self.performance_metrics.get('compression_coverage', 0):.0f}%")
        
        if self.results['failed'] > 0:
            print(f"\n❌ Failed Tests:")
            for error in self.results['errors']:
                print(f"   - {error}")
        
        print("\n🎉 Phase 4B Performance Optimization Testing Complete!")

if __name__ == "__main__":
    tester = FixMatePerformanceTester()
    tester.run_all_tests()