
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const enrollmentData = [
  { month: 'Mar', target: 10, actual: 8, cumulative: 8 },
  { month: 'Apr', target: 20, actual: 12, cumulative: 20 },
  { month: 'May', target: 30, actual: 15, cumulative: 35 },
  { month: 'Jun', target: 40, actual: 12, cumulative: 47 },
  { month: 'Jul', target: 50, actual: 3, cumulative: 50 },
];

export function StudyProgressChart() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">47/50</div>
          <div className="text-sm text-slate-600">Subjects Enrolled</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">94%</div>
          <div className="text-sm text-slate-600">Target Achievement</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-amber-600">3</div>
          <div className="text-sm text-slate-600">Sites Active</div>
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={enrollmentData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="month" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} />
            <Tooltip 
              contentStyle={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '12px'
              }}
            />
            <Legend fontSize={12} />
            <Line 
              type="monotone" 
              dataKey="target" 
              stroke="#94a3b8" 
              strokeDasharray="5 5"
              name="Target Enrollment"
            />
            <Line 
              type="monotone" 
              dataKey="cumulative" 
              stroke="#2563eb" 
              strokeWidth={2}
              name="Actual Enrollment"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
