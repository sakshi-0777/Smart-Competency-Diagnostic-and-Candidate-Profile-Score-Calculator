import React from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const Charts = ({analytics}) => {
  const chartData = (analytics.keywords || []).map((item) => {
    if (!item) return { keyword: "", score: 0 };
    const keyword = typeof item === "string" ? item : item.keyword || item.text || item.name || "";
    const score = typeof item === "object" ? item.score || item.value || 1 : 1;
    return { keyword, score };
  });

  return (
    <div className="bg-gray-50 p-4 rounded-lg shadow-sm">
      <h3 className="font-semibold mb-2 text-gray-700">Keyword Frequency</h3>
      <div style={{ width: "100%", height: 250 }}>
        <ResponsiveContainer>
          <BarChart data={chartData}>
            <XAxis dataKey="keyword" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="score" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default Charts