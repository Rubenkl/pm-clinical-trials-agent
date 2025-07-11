# Clinical Trial Management System - Demo Guide

## 🎯 Demo Overview

This system demonstrates AI-powered clinical trial management with realistic test data showcasing three key scenarios:

### **Demo Subject Groups:**
- **"No Issues" Subjects**: CARD003, CARD004, CARD007, CARD008, CARD010, CARD014, CARD015, CARD027 (0 discrepancies)
- **Problem Detection**: CARD001, CARD002, CARD005, CARD006 (12-18 discrepancies each)  
- **Protocol Violations**: CARD010 (age 85), CARD030 (age 17) - age criteria violations

---

## 🚀 **Recommended Demo Flow**

### 1. **Dashboard Overview** (`/dashboard`)
**What to show:**
- Mixed statistics showing both clean and problem subjects
- Critical alerts banner highlighting CARD001, CARD010, CARD030
- 20/50 subjects enrolled (demo subset with realistic mix)
- Real-time metrics showing problem distribution

**Key talking points:**
- "We're using real test data with 60% clean subjects and 40% with issues"
- "3 critical alerts requiring immediate attention"
- "52 total discrepancies across problem subjects (12+13+13+14)"

### 2. **Subject Management** (`/subjects`)  
**What to show:**
- List of 20 demo subjects (mix of clean and problem cases)
- Alert indicators showing which subjects have issues
- Filter by site, status to demonstrate organization

**Demo sequence:**
1. Show overall subject list
2. Point out clean subjects (CARD003, 007, 008, 014) with 0 alerts
3. Highlight problem subjects (CARD001, 002, 005, 006) with alert indicators
4. Click on CARD001 to show subject profile with severe anemia

### 3. **Query Management** (`/queries`)
**What to show:**
- Real queries based on actual discrepancies
- CARD001: Severe anemia (8.5 vs 12.5 g/dL)
- CARD002: Blood pressure discrepancy (145 vs 155 mmHg)

**Demo sequence:**
1. Show query list with realistic clinical scenarios
2. Select "Critical Lab Value: Severe Anemia" for CARD001
3. Click "Analyze with AI" button
4. **Show AI response with full analysis:**
   - Findings: "Hemoglobin level significantly below expected"
   - Severity: Major/Critical
   - Clinical significance explanation
   - Recommended queries
   - Medical assessment

### 4. **Source Data Verification** (`/sdv`)
**What to show:**
- SDV sessions for different subject types
- Verification of clean vs problem subjects
- Real discrepancy patterns

**Demo sequence:**
1. Show SDV session list
2. Select CARD002 blood pressure discrepancy
3. Click "Verify with AI"
4. **Show AI verification results:**
   - Discrepancies found
   - Audit trail
   - Recommendations
   - Confidence score

### 5. **Protocol Compliance** (`/compliance`)
**What to show:**
- Age violation alerts (CARD010: age 85, CARD030: age 17)
- Protocol deviation analysis
- Regulatory risk assessment

**Demo sequence:**
1. Show critical compliance alert for age violations
2. Select age violation deviation
3. Click "Analyze" for AI-powered assessment
4. **Show comprehensive AI analysis:**
   - Deviation severity assessment
   - Regulatory impact analysis
   - Recommended actions

### 6. **Discrepancies Overview** (`/discrepancies`)
**What to show:**
- Side-by-side comparison of clean vs problem subjects
- CARD001: 12 discrepancies, CARD003: 0 discrepancies
- Realistic discrepancy patterns

---

## 💡 **Key Demo Messages**

### **AI Capabilities:**
- "Real clinical data analysis with 4-5 second response times"
- "Comprehensive medical assessment with clinical significance"
- "Automatic severity classification and priority assignment"
- "Detailed recommendations for follow-up actions"

### **Data Quality:**
- "60% of subjects are completely clean (0 discrepancies)"
- "Problem subjects have realistic 12-18 discrepancies each"
- "AI detects both obvious issues (severe anemia) and subtle patterns"

### **Regulatory Compliance:**
- "Automatic protocol violation detection (age criteria)"
- "Risk assessment for regulatory reporting"
- "Audit trail generation for documentation"

---

## 🎨 **Visual Demo Tips**

### **Color Coding:**
- **Green**: Clean subjects (CARD003, 007, 008, 014)
- **Red**: Critical alerts (CARD001 anemia, age violations)
- **Amber**: Moderate discrepancies (CARD002, 005, 006)

### **Navigation Flow:**
1. Start at Dashboard for overview
2. Go to Subjects to show individual cases  
3. Use Query Management for AI analysis demo
4. Show SDV for verification workflows
5. End with Protocol Compliance for regulatory aspects

### **AI Demo Highlights:**
- Always click "Analyze with AI" buttons
- Show the detailed AI responses with:
  - Clinical findings
  - Severity assessment
  - Medical recommendations
  - Execution time (~4 seconds)

---

## 📊 **Expected AI Response Examples**

### **CARD001 Anemia Analysis:**
```
Findings: "Hemoglobin level of 8.5 g/dL is significantly below expected level of 12.5 g/dL"
Severity: Major
Clinical Significance: "Moderate anemia may necessitate intervention"
Recommendations: "Verify hemoglobin level and confirm if any interventions were taken"
```

### **CARD002 BP Discrepancy:**
```
Discrepancies: "Systolic BP 145 mmHg vs 155 mmHg - 10 mmHg difference"
Verification Status: "Completed with findings"
Recommendations: "Confirm source document accuracy for systolic BP"
```

### **CARD010 Age Violation:**
```
Findings: "Subject age 85 exceeds protocol upper limit of 80 years"
Severity: Major
Impact: "Regulatory risk - protocol deviation requires documentation"
```

---

## 🚦 **Demo Success Criteria**

✅ **Technical:**
- All AI analyses complete in 4-5 seconds
- Comprehensive responses with medical reasoning
- Realistic clinical scenarios demonstrated

✅ **Clinical:**
- Show both clean (no issues) and problem workflows
- Demonstrate safety monitoring (severe anemia)
- Protocol compliance monitoring (age violations)

✅ **Regulatory:**
- Audit trail generation
- Risk assessment capabilities
- Documentation for reporting

This demo structure showcases the full clinical trial management workflow with realistic data patterns and comprehensive AI analysis capabilities.