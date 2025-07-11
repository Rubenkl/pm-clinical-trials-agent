
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { VitalSigns } from '@/services';

interface ClinicalVitalsChartProps {
  data: VitalSigns[];
}

export function ClinicalVitalsChart({ data }: ClinicalVitalsChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        No vital signs data available
      </div>
    );
  }

  const chartData = data.map(vital => ({
    visit: vital.visit,
    systolic: vital.systolic_bp,
    diastolic: vital.diastolic_bp,
    heartRate: vital.heart_rate,
    weight: vital.weight,
    date: vital.date
  }));

  return (
    <div className="space-y-6">
      {/* Blood Pressure Chart */}
      <div>
        <h3 className="text-lg font-medium mb-4">Blood Pressure Trends</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="visit" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} domain={[60, 180]} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '12px'
                }}
                formatter={(value, name) => [
                  `${value} mmHg`,
                  name === 'systolic' ? 'Systolic BP' : 'Diastolic BP'
                ]}
              />
              <Legend fontSize={12} />
              {/* Normal BP reference lines */}
              <Line type="monotone" dataKey={120} stroke="#94a3b8" strokeDasharray="5 5" dot={false} name="Normal Systolic (120)" />
              <Line type="monotone" dataKey={80} stroke="#94a3b8" strokeDasharray="3 3" dot={false} name="Normal Diastolic (80)" />
              
              {/* Actual data */}
              <Line 
                type="monotone" 
                dataKey="systolic" 
                stroke="#dc2626" 
                strokeWidth={2}
                name="Systolic BP"
              />
              <Line 
                type="monotone" 
                dataKey="diastolic" 
                stroke="#2563eb" 
                strokeWidth={2}
                name="Diastolic BP"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Clinical Interpretation */}
        <div className="mt-4 p-3 bg-slate-50 rounded-lg">
          <h4 className="font-medium text-slate-900 mb-2">Clinical Interpretation</h4>
          {(() => {
            const latest = chartData[chartData.length - 1];
            if (!latest) return null;
            
            let interpretation = "";
            let severity = "normal";
            
            if (latest.systolic >= 180 || latest.diastolic >= 110) {
              interpretation = "Hypertensive Crisis - Immediate medical attention required";
              severity = "critical";
            } else if (latest.systolic >= 160 || latest.diastolic >= 100) {
              interpretation = "Stage 2 Hypertension - Antihypertensive therapy recommended";
              severity = "major";
            } else if (latest.systolic >= 140 || latest.diastolic >= 90) {
              interpretation = "Stage 1 Hypertension - Consider antihypertensive therapy";
              severity = "minor";
            } else if (latest.systolic >= 120 || latest.diastolic >= 80) {
              interpretation = "Elevated BP - Lifestyle modifications recommended";
              severity = "elevated";
            } else {
              interpretation = "Normal blood pressure";
              severity = "normal";
            }
            
            return (
              <p className={`text-sm ${
                severity === 'critical' ? 'text-red-700' :
                severity === 'major' ? 'text-red-600' :
                severity === 'minor' ? 'text-amber-600' :
                severity === 'elevated' ? 'text-yellow-600' :
                'text-green-600'
              }`}>
                <strong>Latest Reading ({latest.visit}):</strong> {latest.systolic}/{latest.diastolic} mmHg - {interpretation}
              </p>
            );
          })()}
        </div>
      </div>

      {/* Heart Rate and Weight */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-4">Heart Rate</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="visit" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} domain={[50, 120]} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '12px'
                  }}
                  formatter={(value) => [`${value} bpm`, 'Heart Rate']}
                />
                <Line 
                  type="monotone" 
                  dataKey="heartRate" 
                  stroke="#059669" 
                  strokeWidth={2}
                  name="Heart Rate"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-4">Weight</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="visit" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '12px'
                  }}
                  formatter={(value) => [`${value} kg`, 'Weight']}
                />
                <Line 
                  type="monotone" 
                  dataKey="weight" 
                  stroke="#7c3aed" 
                  strokeWidth={2}
                  name="Weight"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
