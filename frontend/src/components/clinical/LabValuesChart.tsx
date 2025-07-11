
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { LabValues } from '@/services';

interface LabValuesChartProps {
  data: LabValues[];
}

export function LabValuesChart({ data }: LabValuesChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        No laboratory data available
      </div>
    );
  }

  const chartData = data.map(lab => ({
    visit: lab.visit,
    bnp: lab.bnp,
    creatinine: lab.creatinine,
    troponin: lab.troponin,
    date: lab.date
  }));

  return (
    <div className="space-y-6">
      {/* BNP Chart */}
      <div>
        <h3 className="text-lg font-medium mb-4">B-type Natriuretic Peptide (BNP)</h3>
        <div className="h-64">
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
                formatter={(value) => [`${Number(value).toFixed(1)} pg/mL`, 'BNP']}
              />
              {/* Normal BNP reference line */}
              <Line type="monotone" dataKey={100} stroke="#94a3b8" strokeDasharray="5 5" dot={false} name="Normal Limit (100)" />
              
              <Line 
                type="monotone" 
                dataKey="bnp" 
                stroke="#dc2626" 
                strokeWidth={2}
                name="BNP"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 p-3 bg-slate-50 rounded-lg">
          <h4 className="font-medium text-slate-900 mb-2">Clinical Significance</h4>
          {(() => {
            const latest = chartData[chartData.length - 1];
            if (!latest) return null;
            
            let interpretation = "";
            let severity = "normal";
            
            if (latest.bnp > 400) {
              interpretation = "Severely elevated - Likely heart failure, cardiology consultation urgent";
              severity = "critical";
            } else if (latest.bnp > 300) {
              interpretation = "Moderately elevated - Possible heart failure, cardiology evaluation recommended";
              severity = "major";
            } else if (latest.bnp > 100) {
              interpretation = "Mildly elevated - Consider cardiac assessment";
              severity = "minor";
            } else {
              interpretation = "Normal - Low likelihood of heart failure";
              severity = "normal";
            }
            
            return (
              <p className={`text-sm ${
                severity === 'critical' ? 'text-red-700' :
                severity === 'major' ? 'text-red-600' :
                severity === 'minor' ? 'text-amber-600' :
                'text-green-600'
              }`}>
                <strong>Latest Value ({latest.visit}):</strong> {latest.bnp.toFixed(1)} pg/mL - {interpretation}
              </p>
            );
          })()}
        </div>
      </div>

      {/* Creatinine and Troponin */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-4">Creatinine</h3>
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
                  formatter={(value) => [`${value} mg/dL`, 'Creatinine']}
                />
                {/* Normal creatinine reference line */}
                <Line type="monotone" dataKey={1.2} stroke="#94a3b8" strokeDasharray="5 5" dot={false} name="Upper Normal (1.2)" />
                
                <Line 
                  type="monotone" 
                  dataKey="creatinine" 
                  stroke="#ea580c" 
                  strokeWidth={2}
                  name="Creatinine"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4 p-3 bg-orange-50 rounded-lg">
            {(() => {
              const latest = chartData[chartData.length - 1];
              if (!latest) return null;
              
              let interpretation = "";
              let severity = "normal";
              
              if (latest.creatinine > 2.0) {
                interpretation = "Significantly elevated - Nephrology consultation required";
                severity = "critical";
              } else if (latest.creatinine > 1.5) {
                interpretation = "Moderately elevated - Monitor kidney function closely";
                severity = "major";
              } else if (latest.creatinine > 1.2) {
                interpretation = "Mildly elevated - Consider renal assessment";
                severity = "minor";
              } else {
                interpretation = "Normal kidney function";
                severity = "normal";
              }
              
              return (
                <p className={`text-sm ${
                  severity === 'critical' ? 'text-red-700' :
                  severity === 'major' ? 'text-red-600' :
                  severity === 'minor' ? 'text-amber-600' :
                  'text-green-600'
                }`}>
                  <strong>Latest:</strong> {latest.creatinine} mg/dL - {interpretation}
                </p>
              );
            })()}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium mb-4">Troponin</h3>
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
                  formatter={(value) => [`${Number(value).toFixed(3)} ng/mL`, 'Troponin']}
                />
                {/* Normal troponin reference line */}
                <Line type="monotone" dataKey={0.04} stroke="#94a3b8" strokeDasharray="5 5" dot={false} name="Upper Normal (0.04)" />
                
                <Line 
                  type="monotone" 
                  dataKey="troponin" 
                  stroke="#7c3aed" 
                  strokeWidth={2}
                  name="Troponin"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <div className="mt-4 p-3 bg-purple-50 rounded-lg">
            {(() => {
              const latest = chartData[chartData.length - 1];
              if (!latest) return null;
              
              let interpretation = "";
              let severity = "normal";
              
              if (latest.troponin > 0.4) {
                interpretation = "Significantly elevated - Acute MI likely, immediate cardiology consult";
                severity = "critical";
              } else if (latest.troponin > 0.04) {
                interpretation = "Elevated - Possible cardiac injury, monitor closely";
                severity = "major";
              } else {
                interpretation = "Normal - No evidence of cardiac injury";
                severity = "normal";
              }
              
              return (
                <p className={`text-sm ${
                  severity === 'critical' ? 'text-red-700' :
                  severity === 'major' ? 'text-red-600' :
                  'text-green-600'
                }`}>
                  <strong>Latest:</strong> {latest.troponin.toFixed(3)} ng/mL - {interpretation}
                </p>
              );
            })()}
          </div>
        </div>
      </div>

      {/* Combined Values Table */}
      <div>
        <h3 className="text-lg font-medium mb-4">Laboratory Values Summary</h3>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border border-slate-200">
            <thead>
              <tr className="bg-slate-50">
                <th className="border border-slate-200 px-4 py-2 text-left">Visit</th>
                <th className="border border-slate-200 px-4 py-2 text-left">BNP (pg/mL)</th>
                <th className="border border-slate-200 px-4 py-2 text-left">Creatinine (mg/dL)</th>
                <th className="border border-slate-200 px-4 py-2 text-left">Troponin (ng/mL)</th>
                <th className="border border-slate-200 px-4 py-2 text-left">Date</th>
              </tr>
            </thead>
            <tbody>
              {data.map((lab, index) => (
                <tr key={index} className="hover:bg-slate-50">
                  <td className="border border-slate-200 px-4 py-2 font-medium">{lab.visit}</td>
                  <td className={`border border-slate-200 px-4 py-2 ${
                    lab.bnp > 300 ? 'text-red-600 font-medium' : 
                    lab.bnp > 100 ? 'text-amber-600' : 
                    'text-green-600'
                  }`}>
                    {lab.bnp.toFixed(1)}
                    {lab.bnp > 100 && <span className="ml-1 text-xs">↑</span>}
                  </td>
                  <td className={`border border-slate-200 px-4 py-2 ${
                    lab.creatinine > 1.5 ? 'text-red-600 font-medium' : 
                    lab.creatinine > 1.2 ? 'text-amber-600' : 
                    'text-green-600'
                  }`}>
                    {lab.creatinine}
                    {lab.creatinine > 1.2 && <span className="ml-1 text-xs">↑</span>}
                  </td>
                  <td className={`border border-slate-200 px-4 py-2 ${
                    lab.troponin > 0.04 ? 'text-red-600 font-medium' : 'text-green-600'
                  }`}>
                    {lab.troponin.toFixed(3)}
                    {lab.troponin > 0.04 && <span className="ml-1 text-xs">↑</span>}
                  </td>
                  <td className="border border-slate-200 px-4 py-2 text-sm text-slate-600">
                    {new Date(lab.date).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
