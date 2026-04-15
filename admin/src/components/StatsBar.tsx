import { Users, Sparkles, Send, TrendingUp } from 'lucide-react'
import type { Lead } from '../types'

interface StatsBarProps {
  leads: Lead[]
}

export default function StatsBar({ leads }: StatsBarProps) {
  const total    = leads.length
  const novos    = leads.filter(l => l.status === 'novo').length
  const gerados  = leads.filter(l => l.status === 'gerado').length
  const enviados = leads.filter(l => l.status === 'enviado').length
  const taxa     = total > 0 ? Math.round((enviados / total) * 100) : 0

  const stats = [
    { icon: Users,    label: 'Total de Leads',    value: total,    color: 'text-indigo-400',  bg: 'bg-indigo-500/10' },
    { icon: TrendingUp, label: 'Novos',           value: novos,    color: 'text-blue-400',    bg: 'bg-blue-500/10' },
    { icon: Sparkles, label: 'Propostas Geradas', value: gerados,  color: 'text-amber-400',   bg: 'bg-amber-500/10' },
    { icon: Send,     label: 'Enviados',          value: enviados, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map(({ icon: Icon, label, value, color, bg }) => (
        <div key={label} className="stat-card">
          <div className={`${bg} ${color} p-3 rounded-xl shrink-0`}>
            <Icon size={20} />
          </div>
          <div>
            <p className="text-2xl font-bold text-slate-100">{value}</p>
            <p className="text-xs text-slate-500">{label}</p>
          </div>
        </div>
      ))}

      {/* Barra de progresso da taxa de envio */}
      {total > 0 && (
        <div className="col-span-2 lg:col-span-4 card !py-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-400">Taxa de Conversão (enviados / total)</span>
            <span className="text-xs font-bold text-emerald-400">{taxa}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5">
            <div
              className="bg-gradient-to-r from-indigo-500 to-emerald-500 h-1.5 rounded-full transition-all duration-700"
              style={{ width: `${taxa}%` }}
              role="progressbar"
              aria-valuenow={taxa}
              aria-valuemin={0}
              aria-valuemax={100}
            />
          </div>
        </div>
      )}
    </div>
  )
}
