#!/usr/bin/env node

/**
 * Simple Test Runner for Reveal.js Presentations
 * Following TDD methodology: RED -> GREEN -> REFACTOR
 */

const fs = require('fs');
const path = require('path');

class PresentationTester {
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

    async testPresentation(presentationPath) {
        this.log(`\n🧪 Testing: ${presentationPath}`, 'info');
        
        const indexPath = path.join(presentationPath, 'index.html');
        const testPath = path.join(presentationPath, 'tests');
        
        // Check if presentation exists
        if (!fs.existsSync(indexPath)) {
            this.recordFailure(`❌ Presentation not found: ${indexPath}`);
            return;
        }

        const htmlContent = fs.readFileSync(indexPath, 'utf8');
        
        // Content Tests
        await this.testContent(htmlContent, presentationPath);
        
        // Structure Tests  
        await this.testStructure(htmlContent, presentationPath);
        
        // Performance Tests (simulated)
        await this.testPerformance(htmlContent, presentationPath);
    }

    async testContent(htmlContent, presentationPath) {
        const presentationName = path.basename(presentationPath);
        
        switch(presentationName) {
            case 'mvp-demo-jan-10':
                await this.testMVPContent(htmlContent);
                break;
            case 'executive-overview-jan-17':
                await this.testExecutiveContent(htmlContent);
                break;
            case 'technical-deep-dive-jan-20':
                await this.testTechnicalContent(htmlContent);
                break;
            case 'product-strategy-jan-24':
                await this.testStrategyContent(htmlContent);
                break;
            case 'pm-interview-master-deck':
                await this.testPMInterviewContent(htmlContent);
                break;
        }
    }

    async testMVPContent(htmlContent) {
        this.log('  📊 Testing MVP Demo Content...', 'info');
        
        // Test Phase 1 completion
        this.assert(
            htmlContent.includes('Phase 1 Complete'),
            'Should display Phase 1 completion'
        );
        
        // Test query time reduction
        this.assert(
            htmlContent.includes('96.7%') && htmlContent.includes('3 minutes'),
            'Should show 96.7% time reduction and 3-minute processing'
        );
        
        // Test OpenAI Agents SDK
        this.assert(
            htmlContent.includes('OpenAI Agents SDK'),
            'Should mention OpenAI Agents SDK'
        );
        
        // Test interactive demo
        this.assert(
            htmlContent.includes('query-demo') || htmlContent.includes('processQuery'),
            'Should include interactive query demo'
        );
    }

    async testExecutiveContent(htmlContent) {
        this.log('  💼 Testing Executive Overview Content...', 'info');
        
        // Test market opportunity
        this.assert(
            htmlContent.includes('$3.5B'),
            'Should display $3.5B market opportunity'
        );
        
        // Test efficiency gains
        this.assert(
            htmlContent.includes('8x') || htmlContent.includes('40x'),
            'Should show 8x-40x efficiency gains'
        );
        
        // Test ROI
        this.assert(
            htmlContent.includes('124%') && htmlContent.includes('ROI'),
            'Should include 124% ROI data'
        );
    }

    async testTechnicalContent(htmlContent) {
        this.log('  🔧 Testing Technical Deep Dive Content...', 'info');
        
        // Test architecture details
        this.assert(
            htmlContent.includes('Portfolio Manager') && htmlContent.includes('orchestration'),
            'Should show Portfolio Manager orchestration'
        );
        
        // Test FastAPI implementation
        this.assert(
            htmlContent.includes('FastAPI') && htmlContent.includes('REST'),
            'Should describe FastAPI REST implementation'
        );
        
        // Test TDD results
        this.assert(
            htmlContent.includes('38 tests') && htmlContent.includes('100%'),
            'Should show 38 tests with 100% success rate'
        );
    }

    async testStrategyContent(htmlContent) {
        this.log('  🎯 Testing Product Strategy Content...', 'info');
        
        // Test market positioning
        this.assert(
            htmlContent.includes('$22B') && htmlContent.includes('2030'),
            'Should show $22B market projection by 2030'
        );
        
        // Test pricing strategy
        this.assert(
            htmlContent.includes('$1M-$10M') || htmlContent.includes('Enterprise'),
            'Should include enterprise pricing strategy'
        );
        
        // Test go-to-market
        this.assert(
            htmlContent.includes('Big Pharma') || htmlContent.includes('CRO'),
            'Should identify target customer segments'
        );
    }

    async testPMInterviewContent(htmlContent) {
        this.log('  🎯 Testing PM Interview Master Deck Content...', 'info');
        
        // Test strategic thinking - market opportunity
        this.assert(
            htmlContent.includes('$53.9B'),
            'Should display $53.9B addressable market crisis'
        );
        
        // Test user research integration
        this.assert(
            htmlContent.includes('30%') && htmlContent.includes('CRA Turnover'),
            'Should include CRA user persona with crisis metrics'
        );
        
        // Test execution details - framework selection
        this.assert(
            htmlContent.includes('OpenAI Agents SDK') && htmlContent.includes('LangChain'),
            'Should justify OpenAI Agents SDK selection with trade-offs'
        );
        
        // Test technical depth - confidence routing
        this.assert(
            htmlContent.includes('95-100%') && htmlContent.includes('Fully Automated'),
            'Should show confidence-based routing architecture'
        );
        
        // Test business results
        this.assert(
            htmlContent.includes('233-483%') && htmlContent.includes('ROI'),
            'Should display ROI calculations per Phase III study'
        );
        
        // Test regulatory strategy
        this.assert(
            htmlContent.includes('FDA 2025') && htmlContent.includes('PCCP'),
            'Should include FDA 2025 compliance strategy'
        );
        
        // Test competitive positioning
        this.assert(
            htmlContent.includes('Microsoft') && htmlContent.includes('AWS'),
            'Should include competitive positioning vs tech giants'
        );
        
        // Test risk assessment
        this.assert(
            htmlContent.includes('Risk') && htmlContent.includes('Mitigation'),
            'Should include risk assessment and mitigation'
        );
    }

    async testStructure(htmlContent, presentationPath) {
        this.log('  🏗️ Testing Presentation Structure...', 'info');
        
        // Test Reveal.js structure
        this.assert(
            htmlContent.includes('class="reveal"') && htmlContent.includes('class="slides"'),
            'Should have proper Reveal.js structure'
        );
        
        // Test multiple slides
        const slideCount = (htmlContent.match(/<section/g) || []).length;
        this.assert(
            slideCount >= 5,
            `Should have at least 5 slides (found ${slideCount})`
        );
        
        // Test title slide
        this.assert(
            htmlContent.includes('title-slide') || htmlContent.includes('PM Clinical Trials Agent'),
            'Should have proper title slide'
        );
    }

    async testPerformance(htmlContent, presentationPath) {
        this.log('  ⚡ Testing Performance Characteristics...', 'info');
        
        // Test file size (simulated)
        const fileSize = htmlContent.length;
        this.assert(
            fileSize < 100000, // 100KB limit
            `HTML file should be < 100KB (current: ${Math.round(fileSize/1024)}KB)`
        );
        
        // Test external dependencies
        const externalScripts = (htmlContent.match(/src="https:\/\//g) || []).length;
        this.assert(
            externalScripts <= 5,
            `Should minimize external dependencies (found ${externalScripts})`
        );
        
        // Test CSS optimization
        this.assert(
            htmlContent.includes('<style>'),
            'Should include embedded CSS for performance'
        );
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

    async runAllTests() {
        this.log('🚀 Starting TDD Test Suite for Reveal.js Presentations\n', 'info');
        
        const presentationsDir = __dirname;
        const presentations = [
            'mvp-demo-jan-10',
            'executive-overview-jan-17', 
            'technical-deep-dive-jan-20',
            'product-strategy-jan-24',
            'pm-interview-master-deck'
        ];

        for (const presentation of presentations) {
            const presentationPath = path.join(presentationsDir, presentation);
            if (fs.existsSync(presentationPath)) {
                await this.testPresentation(presentationPath);
            } else {
                this.recordFailure(`❌ Presentation directory not found: ${presentation}`);
            }
        }

        this.printSummary();
    }

    printSummary() {
        this.log('\n📊 Test Results Summary', 'info');
        this.log('=' .repeat(50), 'info');
        
        const passRate = Math.round((this.testResults.passed / this.testResults.total) * 100);
        
        this.log(`Total Tests: ${this.testResults.total}`, 'info');
        this.log(`Passed: ${this.testResults.passed}`, 'success');
        this.log(`Failed: ${this.testResults.failed}`, 'error');
        this.log(`Pass Rate: ${passRate}%`, passRate >= 80 ? 'success' : 'error');
        
        if (this.testResults.failed > 0) {
            this.log('\n❌ Failed Tests:', 'error');
            this.testResults.errors.forEach(error => {
                this.log(`  • ${error}`, 'error');
            });
            
            this.log('\n🔧 Next Steps (TDD GREEN phase):', 'warning');
            this.log('  1. Fix failing tests by updating presentations', 'warning');
            this.log('  2. Run tests again to verify fixes', 'warning'); 
            this.log('  3. Refactor for better code quality', 'warning');
            this.log('  4. Repeat until all tests pass', 'warning');
        } else {
            this.log('\n🎉 All tests passed! Ready for REFACTOR phase.', 'success');
        }
        
        // TDD Process status
        if (passRate < 100) {
            this.log('\n🔴 TDD STATUS: RED - Tests are failing as expected', 'error');
            this.log('Next: Enter GREEN phase to make tests pass', 'warning');
        } else {
            this.log('\n🟢 TDD STATUS: GREEN - All tests passing', 'success');
            this.log('Next: Enter REFACTOR phase to improve quality', 'info');
        }
    }
}

// Run tests
const tester = new PresentationTester();
tester.runAllTests().catch(console.error);