#!/usr/bin/env node

/**
 * Enhanced Test Runner for Reveal.js Presentations
 * Includes tests for advanced interactive features
 * Following TDD methodology: RED -> GREEN -> REFACTOR
 */

const fs = require('fs');
const path = require('path');

class EnhancedPresentationTester {
    constructor() {
        this.testResults = {
            total: 0,
            passed: 0,
            failed: 0,
            errors: []
        };
    }

    log(message, type = 'info') {
        const colors = {
            info: '\x1b[36m',
            success: '\x1b[32m', 
            error: '\x1b[31m',
            warning: '\x1b[33m',
            reset: '\x1b[0m'
        };
        console.log(`${colors[type]}${message}${colors.reset}`);
    }

    async testEnhancedMVPDemo() {
        this.log('\n🔬 Testing Enhanced MVP Demo Features (NEW TDD CYCLE)', 'info');
        
        const htmlPath = path.join(__dirname, 'mvp-demo-jan-10', 'index.html');
        if (!fs.existsSync(htmlPath)) {
            this.recordFailure('❌ MVP Demo presentation not found');
            return;
        }

        const htmlContent = fs.readFileSync(htmlPath, 'utf8');
        
        // Advanced Interactive Elements Tests
        this.log('  📊 Testing Advanced Interactive Elements...', 'info');
        
        this.assert(
            htmlContent.includes('live-metrics-dashboard') || htmlContent.includes('real-time'),
            'Should have real-time performance metrics dashboard'
        );
        
        this.assert(
            htmlContent.includes('architecture-walkthrough') || htmlContent.includes('clickable'),
            'Should include interactive architecture walkthrough'
        );
        
        this.assert(
            htmlContent.includes('query-simulator') || htmlContent.includes('multiple queries'),
            'Should have enhanced query processing simulator'
        );
        
        this.assert(
            htmlContent.includes('advanced-roi-calculator') || htmlContent.includes('scenario'),
            'Should include ROI calculator with multiple scenarios'
        );
        
        // Accessibility Enhancement Tests
        this.log('  ♿ Testing Enhanced Accessibility...', 'info');
        
        this.assert(
            htmlContent.includes('tabindex') || htmlContent.includes('role='),
            'Should have keyboard navigation for accessibility'
        );
        
        this.assert(
            htmlContent.includes('aria-') && htmlContent.includes('sr-only'),
            'Should include voice narration and screen reader support'
        );
        
        // Performance Tests for Enhanced Features
        this.log('  ⚡ Testing Enhanced Performance...', 'info');
        
        const fileSize = htmlContent.length;
        this.assert(
            fileSize < 150000, // 150KB limit for enhanced version
            `Enhanced HTML should be < 150KB (current: ${Math.round(fileSize/1024)}KB)`
        );
        
        // Enhanced Content Tests
        this.log('  📋 Testing Enhanced Content...', 'info');
        
        this.assert(
            htmlContent.includes('vs Medidata') || htmlContent.includes('vs Veeva'),
            'Should include comparative analysis with competitors'
        );
        
        this.assert(
            htmlContent.includes('API response time') && htmlContent.includes('throughput'),
            'Should show detailed technical metrics'
        );
        
        // Mobile Optimization Tests (simulated)
        this.log('  📱 Testing Mobile Optimization...', 'info');
        
        this.assert(
            htmlContent.includes('viewport') && htmlContent.includes('responsive'),
            'Should work perfectly on mobile devices'
        );
        
        this.assert(
            htmlContent.includes('@media') || htmlContent.includes('grid'),
            'Should adapt layout for different screen sizes'
        );
    }

    async testPresentationAssets() {
        this.log('\n📁 Testing Presentation Asset Library', 'info');
        
        // Check for asset directories
        const assetDirs = [
            path.join(__dirname, 'assets'),
            path.join(__dirname, 'templates')
        ];
        
        for (const dir of assetDirs) {
            this.assert(
                fs.existsSync(dir),
                `Should have ${path.basename(dir)} directory`
            );
        }
        
        // Check for template files
        const templatePath = path.join(__dirname, 'templates', 'base-template.html');
        this.assert(
            fs.existsSync(templatePath),
            'Should have reusable presentation template'
        );
    }

    async testContinuousIntegration() {
        this.log('\n🔄 Testing CI/CD Integration', 'info');
        
        // Check for CI configuration
        const ciFiles = [
            path.join(__dirname, '..', '..', '..', '.github', 'workflows', 'presentations.yml'),
            path.join(__dirname, 'package.json')
        ];
        
        for (const file of ciFiles) {
            this.assert(
                fs.existsSync(file),
                `Should have CI configuration: ${path.basename(file)}`
            );
        }
        
        // Check for test scripts
        const packagePath = path.join(__dirname, 'package.json');
        if (fs.existsSync(packagePath)) {
            const packageContent = fs.readFileSync(packagePath, 'utf8');
            this.assert(
                packageContent.includes('test:all'),
                'Should have comprehensive test script'
            );
        }
    }

    assert(condition, message) {
        this.testResults.total++;
        
        if (condition) {
            this.testResults.passed++;
            this.log(`    ✅ ${message}`, 'success');
        } else {
            this.testResults.failed++;
            this.testResults.errors.push(message);
            this.log(`    ❌ ${message}`, 'error');
        }
    }

    recordFailure(message) {
        this.testResults.total++;
        this.testResults.failed++;
        this.testResults.errors.push(message);
        this.log(`  ${message}`, 'error');
    }

    async runEnhancedTests() {
        this.log('🚀 Starting Enhanced TDD Test Suite\n', 'info');
        this.log('🔴 RED PHASE: Testing new requirements (expecting failures)\n', 'warning');
        
        await this.testEnhancedMVPDemo();
        await this.testPresentationAssets();
        await this.testContinuousIntegration();
        
        this.printEnhancedSummary();
    }

    printEnhancedSummary() {
        this.log('\n📊 Enhanced Test Results Summary', 'info');
        this.log('=' .repeat(50), 'info');
        
        const passRate = Math.round((this.testResults.passed / this.testResults.total) * 100);
        
        this.log(`Total Tests: ${this.testResults.total}`, 'info');
        this.log(`Passed: ${this.testResults.passed}`, 'success');
        this.log(`Failed: ${this.testResults.failed}`, 'error');
        this.log(`Pass Rate: ${passRate}%`, passRate >= 80 ? 'success' : 'error');
        
        if (this.testResults.failed > 0) {
            this.log('\n❌ Failed Tests (Expected in RED phase):', 'error');
            this.testResults.errors.forEach((error, index) => {
                this.log(`  ${index + 1}. ${error}`, 'error');
            });
            
            this.log('\n🔧 Next Steps (Enter GREEN phase):', 'warning');
            this.log('  1. Implement enhanced interactive elements', 'warning');
            this.log('  2. Add real-time metrics dashboard', 'warning'); 
            this.log('  3. Create presentation asset library', 'warning');
            this.log('  4. Set up CI/CD pipeline', 'warning');
            this.log('  5. Run tests again to verify fixes', 'warning');
        } else {
            this.log('\n🎉 All enhanced tests passed! Ready for next TDD cycle.', 'success');
        }
        
        // TDD Process status
        if (passRate < 100) {
            this.log('\n🔴 TDD STATUS: RED - New requirements failing as expected', 'error');
            this.log('This is CORRECT for TDD! Now implement features to make tests pass.', 'warning');
        } else {
            this.log('\n🟢 TDD STATUS: GREEN - All enhanced tests passing', 'success');
            this.log('Ready for REFACTOR phase or next feature cycle', 'info');
        }
    }
}

// Run enhanced tests
const tester = new EnhancedPresentationTester();
tester.runEnhancedTests().catch(console.error);