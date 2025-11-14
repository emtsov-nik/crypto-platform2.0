import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { strategyApi } from '../services/api'
import type { Strategy, StrategyCreate } from '../types'

export default function StrategiesPage() {
  const queryClient = useQueryClient()
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null)
  const [createForm, setCreateForm] = useState<StrategyCreate>({
    name: '',
    description: '',
    class_name: 'RSIBBStrategy',
    params: {},
    is_active: true,
  })

  // Fetch user strategies
  const { data: strategiesData, isLoading: strategiesLoading } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => strategyApi.getStrategies(),
  })

  // Fetch available strategy classes
  const { data: availableData, isLoading: availableLoading } = useQuery({
    queryKey: ['available-strategies'],
    queryFn: () => strategyApi.getAvailableStrategies(),
  })

  // Create strategy mutation
  const createMutation = useMutation({
    mutationFn: (data: StrategyCreate) => strategyApi.createStrategy(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      setShowCreateForm(false)
      resetForm()
    },
  })

  // Delete strategy mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => strategyApi.deleteStrategy(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })

  // Toggle active mutation
  const toggleMutation = useMutation({
    mutationFn: (id: number) => strategyApi.toggleStrategyActive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })

  const resetForm = () => {
    setCreateForm({
      name: '',
      description: '',
      class_name: 'RSIBBStrategy',
      params: {},
      is_active: true,
    })
  }

  const handleCreateStrategy = () => {
    // Get default params for selected strategy class
    const strategyClass = availableData?.strategies.find(
      (s) => s.class_name === createForm.class_name
    )

    const strategyData: StrategyCreate = {
      ...createForm,
      params: strategyClass?.default_params || {},
    }

    createMutation.mutate(strategyData)
  }

  const handleDeleteStrategy = (id: number) => {
    if (confirm('Are you sure you want to delete this strategy?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleToggleActive = (id: number) => {
    toggleMutation.mutate(id)
  }

  if (strategiesLoading || availableLoading) {
    return (
      <div className="p-8">
        <div className="text-center">Loading strategies...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Trading Strategies</h1>
        <p className="text-gray-600">
          Manage your trading strategies, test them, and activate for live trading.
        </p>
      </div>

      {/* Available Strategy Classes */}
      <div className="mb-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Available Strategy Classes</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {availableData?.strategies.map((strategy) => (
            <div
              key={strategy.class_name}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition"
            >
              <h3 className="font-semibold text-lg mb-2">{strategy.name}</h3>
              <p className="text-sm text-gray-600 mb-3">
                {strategy.metadata.description || 'No description'}
              </p>
              <div className="space-y-1 text-sm">
                <div>
                  <span className="font-medium">Type:</span>{' '}
                  <span className="text-gray-600">
                    {strategy.metadata.strategy_type || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Risk Level:</span>{' '}
                  <span
                    className={`${
                      strategy.metadata.risk_level === 'high'
                        ? 'text-red-600'
                        : strategy.metadata.risk_level === 'medium'
                        ? 'text-yellow-600'
                        : 'text-green-600'
                    }`}
                  >
                    {strategy.metadata.risk_level || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="font-medium">Indicators:</span>{' '}
                  <span className="text-gray-600">
                    {strategy.metadata.indicators.join(', ')}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Strategy Button */}
      <div className="mb-6">
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
        >
          {showCreateForm ? 'Cancel' : 'Create New Strategy'}
        </button>
      </div>

      {/* Create Strategy Form */}
      {showCreateForm && (
        <div className="mb-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create New Strategy</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Strategy Name</label>
              <input
                type="text"
                value={createForm.name}
                onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="My RSI Strategy"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                value={createForm.description}
                onChange={(e) =>
                  setCreateForm({ ...createForm, description: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Strategy description..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Strategy Class</label>
              <select
                value={createForm.class_name}
                onChange={(e) =>
                  setCreateForm({ ...createForm, class_name: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {availableData?.strategies.map((strategy) => (
                  <option key={strategy.class_name} value={strategy.class_name}>
                    {strategy.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={createForm.is_active}
                onChange={(e) =>
                  setCreateForm({ ...createForm, is_active: e.target.checked })
                }
                className="mr-2"
              />
              <label className="text-sm font-medium">Active</label>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleCreateStrategy}
                disabled={!createForm.name || createMutation.isPending}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition disabled:bg-gray-400"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Strategy'}
              </button>
              <button
                onClick={() => {
                  setShowCreateForm(false)
                  resetForm()
                }}
                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition"
              >
                Cancel
              </button>
            </div>

            {createMutation.isError && (
              <div className="text-red-600 text-sm">
                Error: {(createMutation.error as Error).message}
              </div>
            )}
          </div>
        </div>
      )}

      {/* User Strategies List */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Your Strategies</h2>

        {strategiesData?.strategies.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No strategies yet. Create your first strategy to get started!
          </div>
        ) : (
          <div className="space-y-4">
            {strategiesData?.strategies.map((strategy) => (
              <div
                key={strategy.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-lg">{strategy.name}</h3>
                    <p className="text-sm text-gray-600">{strategy.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 text-xs rounded ${
                        strategy.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {strategy.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                <div className="mb-3 text-sm space-y-1">
                  <div>
                    <span className="font-medium">Class:</span>{' '}
                    <span className="text-gray-600">{strategy.class_name}</span>
                  </div>
                  <div>
                    <span className="font-medium">Created:</span>{' '}
                    <span className="text-gray-600">
                      {new Date(strategy.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div>
                    <span className="font-medium">Parameters:</span>{' '}
                    <span className="text-gray-600 text-xs">
                      {Object.keys(strategy.params).length} params configured
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => handleToggleActive(strategy.id)}
                    disabled={toggleMutation.isPending}
                    className={`px-3 py-1 text-sm rounded transition ${
                      strategy.is_active
                        ? 'bg-yellow-500 hover:bg-yellow-600 text-white'
                        : 'bg-green-500 hover:bg-green-600 text-white'
                    }`}
                  >
                    {strategy.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button
                    onClick={() => setSelectedStrategy(strategy)}
                    className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                  >
                    View Details
                  </button>
                  <button
                    onClick={() => handleDeleteStrategy(strategy.id)}
                    disabled={deleteMutation.isPending}
                    className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Strategy Details Modal */}
      {selectedStrategy && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
          onClick={() => setSelectedStrategy(null)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold">{selectedStrategy.name}</h2>
                <button
                  onClick={() => setSelectedStrategy(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-1">Description</h3>
                  <p className="text-gray-600">
                    {selectedStrategy.description || 'No description'}
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-1">Strategy Class</h3>
                  <p className="text-gray-600">{selectedStrategy.class_name}</p>
                </div>

                <div>
                  <h3 className="font-semibold mb-1">Parameters</h3>
                  <pre className="bg-gray-100 p-3 rounded text-sm overflow-x-auto">
                    {JSON.stringify(selectedStrategy.params, null, 2)}
                  </pre>
                </div>

                <div>
                  <h3 className="font-semibold mb-1">Status</h3>
                  <p className="text-gray-600">
                    {selectedStrategy.is_active ? 'Active' : 'Inactive'}
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold mb-1">Timestamps</h3>
                  <p className="text-sm text-gray-600">
                    Created: {new Date(selectedStrategy.created_at).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    Updated: {new Date(selectedStrategy.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
