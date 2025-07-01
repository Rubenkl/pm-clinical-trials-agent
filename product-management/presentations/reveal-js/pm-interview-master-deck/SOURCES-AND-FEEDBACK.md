# PM Interview Master Deck - Sources & Fact-Checking

## 📊 Number Sources & Validation

### CRA Crisis Metrics
- **30% annual turnover rate**: `/research/user-research/clinical-research-associate-user-persona.md` line 23
- **165 hours monthly work**: Same file, line 7
- **46-50% time on manual SDV**: Same file, line 11
- **60% work-related mental health issues**: Same file, line 25

### Industry Inefficiency Numbers
- **$53.9B annual crisis**: `/research/market-analysis/clinical-trials-AI-market-report.md` line 3
- **82% Phase III protocols need amendments**: Same file, line 9
- **$535K cost per amendment**: Same file, line 9
- **45% amendments preventable**: Same file, line 9

### Performance Benchmarks
- **Pfizer COVID-19 40x**: `/research/market-analysis/clinical-trials-AI-market-report.md` line 19
- **Deep 6 AI 672x**: Same file, line 23
- **Novo Nordisk 95% reduction**: Same file, line 19
- **Saama 10x improvement**: Same file, line 19
- **AWS-Pfizer $750M-$1B**: Same file, line 31
- **QuantHealth $215M saved**: Same file, line 21

### ROI Calculations
- **233-483% ROI**: Based on industry benchmarks in market analysis files
- **$40-70M value per study**: `/research/market-analysis/clinical-trials-AI-market-report.md`

## ❓ Addressing Specific Feedback

### 1. "45% amendments preventable through AI" - HOW?
**Sources**: `/research/market-analysis/clinical-trials-AI-market-report.md` states this but doesn't specify mechanism.

**The Issue**: The research states 45% are preventable but doesn't explain HOW AI prevents them. This needs clarification or removal.

**Recommendation**: Either find specific mechanism (protocol optimization, site selection, etc.) or remove this claim.

### 2. "What others have achieved" - Number Backing
All numbers sourced from `/research/market-analysis/clinical-trials-AI-market-report.md` but some lack primary sources:
- Pfizer COVID-19: Documented publicly
- Deep 6 AI: From company materials (now Tempus acquisition)
- Novo Nordisk: From company presentations
- **Issue**: Need primary source validation for credibility

### 3. Technology Giants as "Market Competitors"
**You're right - this is incorrect framing**:
- Azure, AWS, Google Cloud are infrastructure providers, not clinical trial competitors
- They enable our technology stack, they're not competing for clinical trial services
- **Should be reframed as**: "Technology Infrastructure Landscape" or removed entirely

### 4. "IQVIA's Internal Advantage" - Source Unknown
**Major Issue**: I don't actually have internal IQVIA data on:
- Our clinical-first design capabilities
- Our 20+ years experience claims  
- Our internal workflow advantages
- **This is fabricated content and should be removed or sourced from actual IQVIA materials**

### 5. Framework Selection - "Clinical-first design"
**You're absolutely right - this is incorrect**:
- OpenAI Agents SDK was selected for technical reasons, not clinical-first design
- The SDK is general-purpose, not clinical-specific
- **Should either**: Remove this rationale OR state actual selection criteria (if known)

### 6. Agent Specialization Details Needed
**Current presentation lacks specifics on**:
- What exactly each agent does
- How they work together
- Specific workflows they handle
- Concrete examples of their outputs

**Need to detail**:
- **Query Resolver**: Analyzes what data discrepancies? Generates what kind of queries?
- **SDV Monitor**: Monitors what specifically? How does it reduce 75% cost?
- **Deviation Scanner**: Scans for what patterns? Real-time how?

## 🚨 Major Issues Found

### Unsourced/Questionable Claims
1. **IQVIA internal advantages** - No internal data available
2. **Framework selection rationale** - Incorrect reasoning provided
3. **Technology giants as competitors** - Wrong competitive framing
4. **Some ROI calculations** - Based on extrapolations, not direct sources
5. **Amendment prevention mechanism** - How AI prevents 45% unclear

### Missing Primary Sources
1. Novo Nordisk NovoScribe results
2. QuantHealth specific savings
3. Saama Technologies improvements
4. Direct FDA guidance references

## 🔧 Recommended Fixes

### Immediate Actions
1. **Remove unsourced IQVIA internal claims**
2. **Fix framework selection rationale or remove**
3. **Reframe or remove technology giants section**
4. **Add specific agent workflow details**
5. **Clarify amendment prevention mechanism or remove**

### Source Validation Needed
1. Verify all industry benchmark numbers with primary sources
2. Get actual IQVIA internal data if available
3. Clarify real OpenAI SDK selection criteria
4. Detail specific agent capabilities from actual implementation

## 📋 Files Referenced
- `/research/market-analysis/clinical-trials-AI-market-report.md`
- `/research/user-research/clinical-research-associate-user-persona.md`
- `/research/market-analysis/future-of-ai-transformed-clinical-trials-strategic-roadmap-for-iqvia.md`
- `/product-management/prds/iqvia-agent-prd.md`
- `/backend/CLAUDE.md` (for actual agent implementation details)

**Note**: Many claims in the presentation go beyond what's documented in available research files and need validation or removal.