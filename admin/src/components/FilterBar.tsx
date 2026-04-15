import { RefreshCw } from 'lucide-react'
import type { LeadStatus } from '../types'
import { STATUS_CONFIG } from '../utils/helpers'

const FILTERS: Array<{ value: LeadStatus | 'todos'; label: string }> = [
  { value: 'todos',   label: 'Todos' },
  { value: 'novo',    label: 'Novos' },
  { value: 'gerado',  label: 'Gerados' },
  { value: 'enviado', label: 'Enviados' },
  { value: 'fechado', label: 'Fechados' },
]

interface FilterBarProps {
  active: LeadStatus | 'todos'
  onChange: (s: LeadStatus | 'todos') => void
  onRefresh: () => void
  loading: boolean
}

export default function FilterBar({ active, onChange, onRefresh, loading }: FilterBarProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      {/* Filtros de status */}
      <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar leads por status">
        {FILTERS.map(({ value, label }) => {
          const isActive = active === value
          const cfg = value !== 'todos' ? STATUS_CONFIG[value as LeadStatus] : null

          return (
            <button
              key={value}
              id={`filter-${value}`}
              onClick={() => onChange(value)}
              aria-pressed={isActive}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
                border transition-all duration-200
                ${isActive
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/20'
                  : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
                }
              `}
            >
              {cfg && (
                <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
              )}
              {label}
            </button>
          )
        })}
      </div>

      {/* Botão de atualizar */}
      <button
        id="btn-refresh"
        onClick={onRefresh}
        disabled={loading}
        className="btn-ghost"
        aria-label="Recarregar lista de leads"
      >
        <RefreshCw
          size={14}
          className={loading ? 'animate-spin' : ''}
        />
        Atualizar
      </button>
    </div>
  )
}
