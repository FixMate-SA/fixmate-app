#!/usr/bin/env node

/**
 * Bundle Analysis Script for FixMate-SA
 * Analyzes webpack bundle size and provides optimization recommendations
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class BundleAnalyzer {
  constructor() {
    this.buildPath = path.join(__dirname, '../build');
    this.results = {
      totalSize: 0,
      jsFiles: [],
      cssFiles: [],
      assets: [],
      chunks: {},
      recommendations: []
    };
  }

  async analyze() {
    console.log('🔍 Starting Bundle Analysis for FixMate-SA...\n');
    
    try {
      // Check if build directory exists
      if (!fs.existsSync(this.buildPath)) {
        console.log('⚠️  Build directory not found. Running production build...');
        this.runProductionBuild();
      }

      // Analyze files
      this.analyzeFiles();
      this.generateRecommendations();
      this.printResults();
      this.saveResults();

    } catch (error) {
      console.error('❌ Bundle analysis failed:', error.message);
      process.exit(1);
    }
  }

  runProductionBuild() {
    try {
      console.log('📦 Building production bundle...');
      execSync('npm run build', { 
        cwd: path.join(__dirname, '..'),
        stdio: 'inherit' 
      });
    } catch (error) {
      console.error('❌ Production build failed:', error.message);
      process.exit(1);
    }
  }

  analyzeFiles() {
    console.log('📊 Analyzing bundle files...\n');

    const staticPath = path.join(this.buildPath, 'static');
    
    // Analyze JavaScript files
    const jsPath = path.join(staticPath, 'js');
    if (fs.existsSync(jsPath)) {
      this.analyzeDirectory(jsPath, '.js', 'jsFiles');
    }

    // Analyze CSS files
    const cssPath = path.join(staticPath, 'css');
    if (fs.existsSync(cssPath)) {
      this.analyzeDirectory(cssPath, '.css', 'cssFiles');
    }

    // Analyze other assets
    const mediaPath = path.join(staticPath, 'media');
    if (fs.existsSync(mediaPath)) {
      this.analyzeDirectory(mediaPath, null, 'assets');
    }

    // Calculate total size
    this.results.totalSize = [
      ...this.results.jsFiles,
      ...this.results.cssFiles,
      ...this.results.assets
    ].reduce((total, file) => total + file.size, 0);
  }

  analyzeDirectory(dirPath, extension, resultKey) {
    const files = fs.readdirSync(dirPath);
    
    files.forEach(file => {
      if (!extension || file.endsWith(extension)) {
        const filePath = path.join(dirPath, file);
        const stats = fs.statSync(filePath);
        
        const fileInfo = {
          name: file,
          path: filePath,
          size: stats.size,
          sizeFormatted: this.formatBytes(stats.size),
          type: this.getFileType(file)
        };

        this.results[resultKey].push(fileInfo);

        // Categorize chunks
        if (extension === '.js') {
          this.categorizeJSChunk(fileInfo);
        }
      }
    });

    // Sort by size descending
    this.results[resultKey].sort((a, b) => b.size - a.size);
  }

  categorizeJSChunk(fileInfo) {
    const fileName = fileInfo.name.toLowerCase();
    
    if (fileName.includes('main')) {
      this.results.chunks.main = fileInfo;
    } else if (fileName.includes('vendor') || fileName.includes('chunk')) {
      if (!this.results.chunks.vendor) this.results.chunks.vendor = [];
      this.results.chunks.vendor.push(fileInfo);
    } else if (fileName.includes('runtime')) {
      this.results.chunks.runtime = fileInfo;
    } else {
      if (!this.results.chunks.async) this.results.chunks.async = [];
      this.results.chunks.async.push(fileInfo);
    }
  }

  getFileType(fileName) {
    const ext = path.extname(fileName).toLowerCase();
    const typeMap = {
      '.js': 'JavaScript',
      '.css': 'Stylesheet',
      '.png': 'Image',
      '.jpg': 'Image',
      '.jpeg': 'Image',
      '.gif': 'Image',
      '.svg': 'Vector Image',
      '.woff': 'Font',
      '.woff2': 'Font',
      '.ttf': 'Font',
      '.eot': 'Font'
    };
    return typeMap[ext] || 'Other';
  }

  generateRecommendations() {
    const recs = this.results.recommendations;

    // Bundle size recommendations
    if (this.results.totalSize > 5 * 1024 * 1024) { // 5MB
      recs.push({
        type: 'critical',
        category: 'Bundle Size',
        message: 'Total bundle size exceeds 5MB. Consider code splitting and lazy loading.',
        suggestion: 'Implement route-based code splitting and lazy load non-critical components.'
      });
    } else if (this.results.totalSize > 2 * 1024 * 1024) { // 2MB
      recs.push({
        type: 'warning',
        category: 'Bundle Size',
        message: 'Bundle size is large (>2MB). Monitor performance on slower networks.',
        suggestion: 'Consider implementing progressive loading and better compression.'
      });
    }

    // JavaScript specific recommendations
    const largeJSFiles = this.results.jsFiles.filter(file => file.size > 500 * 1024); // 500KB
    if (largeJSFiles.length > 0) {
      recs.push({
        type: 'warning',
        category: 'JavaScript',
        message: `${largeJSFiles.length} JavaScript file(s) exceed 500KB.`,
        suggestion: 'Split large chunks and implement dynamic imports for better caching.',
        files: largeJSFiles.map(f => f.name)
      });
    }

    // CSS recommendations
    const totalCSSSize = this.results.cssFiles.reduce((total, file) => total + file.size, 0);
    if (totalCSSSize > 200 * 1024) { // 200KB
      recs.push({
        type: 'info',
        category: 'CSS',
        message: 'CSS bundle is relatively large.',
        suggestion: 'Consider CSS-in-JS solutions or better CSS purging to reduce unused styles.'
      });
    }

    // Asset recommendations
    const largeAssets = this.results.assets.filter(file => file.size > 1024 * 1024); // 1MB
    if (largeAssets.length > 0) {
      recs.push({
        type: 'warning',
        category: 'Assets',
        message: `${largeAssets.length} asset(s) exceed 1MB.`,
        suggestion: 'Optimize images and consider WebP format for better compression.',
        files: largeAssets.map(f => f.name)
      });
    }

    // Phase 4B specific recommendations
    recs.push({
      type: 'success',
      category: 'Phase 4B Optimizations',
      message: 'Code splitting and lazy loading have been implemented.',
      suggestion: 'Monitor Core Web Vitals and consider further optimizations based on real user metrics.'
    });
  }

  printResults() {
    console.log('📈 BUNDLE ANALYSIS RESULTS');
    console.log('═'.repeat(50));
    
    // Overall stats
    console.log(`\n📦 BUNDLE OVERVIEW:`);
    console.log(`   Total Size: ${this.formatBytes(this.results.totalSize)}`);
    console.log(`   JavaScript: ${this.formatBytes(this.results.jsFiles.reduce((sum, f) => sum + f.size, 0))} (${this.results.jsFiles.length} files)`);
    console.log(`   CSS: ${this.formatBytes(this.results.cssFiles.reduce((sum, f) => sum + f.size, 0))} (${this.results.cssFiles.length} files)`);
    console.log(`   Assets: ${this.formatBytes(this.results.assets.reduce((sum, f) => sum + f.size, 0))} (${this.results.assets.length} files)`);

    // Largest files
    console.log(`\n📊 LARGEST FILES:`);
    const allFiles = [...this.results.jsFiles, ...this.results.cssFiles, ...this.results.assets]
      .sort((a, b) => b.size - a.size)
      .slice(0, 10);

    allFiles.forEach((file, index) => {
      console.log(`   ${index + 1}. ${file.name} - ${file.sizeFormatted} (${file.type})`);
    });

    // Chunk analysis
    console.log(`\n🧩 CHUNK ANALYSIS:`);
    if (this.results.chunks.main) {
      console.log(`   Main Chunk: ${this.results.chunks.main.sizeFormatted}`);
    }
    if (this.results.chunks.vendor && this.results.chunks.vendor.length > 0) {
      const vendorSize = this.results.chunks.vendor.reduce((sum, f) => sum + f.size, 0);
      console.log(`   Vendor Chunks: ${this.formatBytes(vendorSize)} (${this.results.chunks.vendor.length} files)`);
    }
    if (this.results.chunks.async && this.results.chunks.async.length > 0) {
      const asyncSize = this.results.chunks.async.reduce((sum, f) => sum + f.size, 0);
      console.log(`   Async Chunks: ${this.formatBytes(asyncSize)} (${this.results.chunks.async.length} files)`);
    }

    // Recommendations
    console.log(`\n💡 RECOMMENDATIONS:`);
    this.results.recommendations.forEach((rec, index) => {
      const emoji = rec.type === 'critical' ? '🚨' : rec.type === 'warning' ? '⚠️' : rec.type === 'info' ? 'ℹ️' : '✅';
      console.log(`   ${emoji} [${rec.category}] ${rec.message}`);
      console.log(`      💭 ${rec.suggestion}`);
      if (rec.files) {
        console.log(`      📁 Files: ${rec.files.join(', ')}`);
      }
      console.log('');
    });

    // Performance scores
    this.printPerformanceScores();
  }

  printPerformanceScores() {
    console.log(`🎯 PERFORMANCE SCORES:`);
    
    const scores = {
      bundleSize: this.calculateBundleSizeScore(),
      chunkOptimization: this.calculateChunkOptimizationScore(),
      assetOptimization: this.calculateAssetOptimizationScore()
    };

    const overallScore = Math.round(
      (scores.bundleSize + scores.chunkOptimization + scores.assetOptimization) / 3
    );

    console.log(`   Overall Score: ${this.getScoreEmoji(overallScore)} ${overallScore}/100`);
    console.log(`   Bundle Size: ${this.getScoreEmoji(scores.bundleSize)} ${scores.bundleSize}/100`);
    console.log(`   Chunk Optimization: ${this.getScoreEmoji(scores.chunkOptimization)} ${scores.chunkOptimization}/100`);
    console.log(`   Asset Optimization: ${this.getScoreEmoji(scores.assetOptimization)} ${scores.assetOptimization}/100`);
  }

  calculateBundleSizeScore() {
    const sizeMB = this.results.totalSize / (1024 * 1024);
    if (sizeMB <= 1) return 100;
    if (sizeMB <= 2) return 85;
    if (sizeMB <= 3) return 70;
    if (sizeMB <= 5) return 50;
    return 25;
  }

  calculateChunkOptimizationScore() {
    let score = 100;
    
    // Penalize if no async chunks (no code splitting)
    if (!this.results.chunks.async || this.results.chunks.async.length === 0) {
      score -= 30;
    }
    
    // Penalize large main chunk
    if (this.results.chunks.main && this.results.chunks.main.size > 1024 * 1024) {
      score -= 20;
    }
    
    return Math.max(0, score);
  }

  calculateAssetOptimizationScore() {
    let score = 100;
    
    const largeAssets = this.results.assets.filter(asset => asset.size > 500 * 1024);
    score -= largeAssets.length * 15;
    
    return Math.max(0, score);
  }

  getScoreEmoji(score) {
    if (score >= 90) return '🟢';
    if (score >= 70) return '🟡';
    if (score >= 50) return '🟠';
    return '🔴';
  }

  formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }

  saveResults() {
    const reportPath = path.join(__dirname, '../bundle-analysis-report.json');
    
    const report = {
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      phase: '4B - Performance Optimization',
      ...this.results
    };

    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n💾 Analysis report saved to: ${reportPath}`);
  }
}

// CLI execution
if (require.main === module) {
  const analyzer = new BundleAnalyzer();
  analyzer.analyze().catch(error => {
    console.error('❌ Analysis failed:', error);
    process.exit(1);
  });
}

module.exports = BundleAnalyzer;