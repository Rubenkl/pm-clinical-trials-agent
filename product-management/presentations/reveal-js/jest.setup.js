// Jest setup for Reveal.js presentation testing
const { toHaveNoViolations } = require('jest-axe');
expect.extend(toHaveNoViolations);

// Mock DOM environment for testing
global.getSlide = (slideNumber) => {
  const slides = document.querySelectorAll('.reveal .slides section');
  return slides[slideNumber - 1]?.innerHTML || '';
};

global.getInteractiveElement = (elementId) => {
  return {
    hasClickableAgents: () => false,
    showsDataFlow: () => false,
    setInput: (input) => {},
    getOutput: () => '',
    getProcessingTime: () => 10000, // Fail initially
    hasAnimatedData: () => false,
    showsGrowthProjection: () => false,
    calculateROI: () => 0,
    filterByCategory: () => {},
    getVisibleCompetitors: () => [],
    setImplementationSize: () => {},
    setTimeframe: () => {},
    setCustomerCount: () => {},
    setAverageContractValue: () => {},
    getAnnualRevenue: () => 0,
    hasClickablePartners: () => false,
    showsIntegrationStatus: () => false,
    highlightsCurrentImplementation: () => false,
    executeCode: () => {},
    showsResponseTime: () => false,
    showsThroughput: () => false,
    showsErrorRate: () => false,
    showsRailwayDeployment: () => false,
    showsScalingOptions: () => false,
    hasFilterableSegments: () => false,
    showsSizeAndGrowth: () => false,
    selectCompetitor: () => {},
    showsComparison: () => false
  };
};

global.measureLoadTime = async () => {
  return 5000; // Fail initially (> 3 seconds)
};

global.measureTransitionFPS = async () => {
  return 30; // Fail initially (< 60 fps)
};

global.measureDemoResponseTime = async () => {
  return 10000; // Fail initially (> 5 seconds)
};

global.runAccessibilityTest = async () => {
  return { critical: ['color contrast violation'] }; // Fail initially
};

global.checkColorContrast = async () => {
  return 3.0; // Fail initially (< 4.5)
};

global.testMobileResponsiveness = async () => {
  return { readability: 70 }; // Fail initially (< 90)
};

global.testTabletResponsiveness = async () => {
  return { readability: 70 }; // Fail initially (< 85)
};

global.testSyntaxHighlighting = async () => {
  return { pythonSupport: false, javascriptSupport: false }; // Fail initially
};

global.measureInteractionResponseTime = async () => {
  return 2000; // Fail initially (> 1000)
};

global.getAllSlides = () => {
  return { toHaveConsistentColorScheme: () => false }; // Fail initially
};

// Enhanced interactivity test functions (should fail initially)
global.measureEnhancedLoadTime = async () => {
  return 6000; // Fail initially (> 4 seconds)
};

global.testConcurrentUsers = async (count) => {
  return { successRate: 60 }; // Fail initially (< 95%)
};

global.testOfflineFunctionality = async () => {
  return { 
    basicFeaturesWork: false, // Fail initially
    interactiveElementsWork: false // Fail initially
  };
};

global.testMobileExperience = async () => {
  return {
    touchNavigation: false, // Fail initially
    readability: 70, // Fail initially (< 95)
    interactivityWorks: false // Fail initially
  };
};

global.testResponsiveDesign = async () => {
  return {
    phoneLayout: 'poor', // Fail initially
    tabletLayout: 'poor', // Fail initially  
    desktopLayout: 'poor' // Fail initially
  };
};

// Update interactive element mock for enhanced features
const originalGetInteractiveElement = global.getInteractiveElement;
global.getInteractiveElement = (elementId) => {
  const base = originalGetInteractiveElement(elementId);
  
  // Enhanced features that should fail initially
  return {
    ...base,
    showsRealTimeData: () => false,
    hasAnimatedCharts: () => false,
    updatesEvery: () => false,
    hasClickableComponents: () => false,
    highlightsActiveAgent: () => false,
    processesMultipleQueries: () => false,
    showsProcessingSteps: () => false,
    comparesBeforeAfter: () => false,
    hasProgressIndicators: () => false,
    calculateTimeSavings: () => 0, // Fail initially
    calculateCostSavings: () => 0, // Fail initially
    hasScenarioComparison: () => false,
    supportsTabNavigation: () => false,
    hasSkipLinks: () => false,
    announcesChanges: () => false,
    hasPlayPauseControls: () => false,
    hasSpeedControls: () => false,
    hasClosedCaptions: () => false,
    setTrialCount: () => {},
    setTrialSize: () => {},
    setQueryCount: () => {}
  };
};