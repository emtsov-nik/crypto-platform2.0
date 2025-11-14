export default function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">
          Welcome to Crypto Trading Platform!
        </p>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded">
            <h3 className="font-semibold text-blue-900">Strategies</h3>
            <p className="text-sm text-blue-700">Manage your trading strategies</p>
          </div>
          <div className="p-4 bg-green-50 rounded">
            <h3 className="font-semibold text-green-900">Backtesting</h3>
            <p className="text-sm text-green-700">Test strategies on historical data</p>
          </div>
          <div className="p-4 bg-purple-50 rounded">
            <h3 className="font-semibold text-purple-900">Live Trading</h3>
            <p className="text-sm text-purple-700">Run bots with real money</p>
          </div>
        </div>
      </div>
    </div>
  )
}
