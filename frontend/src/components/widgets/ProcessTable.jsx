// src/components/widgets/ProcessTable.jsx
export default function ProcessTable({ processes = [] }) {
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">Top Processes by CPU</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 border-b border-gray-800">
              <th className="text-left pb-2 font-medium">PID</th>
              <th className="text-left pb-2 font-medium">Name</th>
              <th className="text-right pb-2 font-medium">CPU %</th>
              <th className="text-right pb-2 font-medium">MEM %</th>
              <th className="text-right pb-2 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {processes.map((p, i) => (
              <tr key={p.pid} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                <td className="py-2 text-gray-500">{p.pid}</td>
                <td className="py-2 text-gray-200 font-mono text-xs">{p.name}</td>
                <td className="py-2 text-right">
                  <span className={`font-medium ${
                    (p.cpu_percent || 0) > 50 ? 'text-red-400' :
                    (p.cpu_percent || 0) > 20 ? 'text-yellow-400' : 'text-green-400'
                  }`}>
                    {(p.cpu_percent || 0).toFixed(1)}%
                  </span>
                </td>
                <td className="py-2 text-right text-gray-300">{p.memory_percent.toFixed(1)}%</td>
                <td className="py-2 text-right">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    p.status === 'running' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
                  }`}>
                    {p.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}