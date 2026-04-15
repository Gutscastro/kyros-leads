import { Zap } from 'lucide-react'

export default function Header() {
  return (
    <header className="border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-md sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo e título */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg
                          flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Zap size={16} className="text-white" fill="white" />
          </div>
          <div>
            <h1 className="font-bold text-slate-100 text-sm leading-none">Kyros Leads</h1>
            <p className="text-xs text-slate-500 leading-none mt-0.5">Painel de Prospecção</p>
          </div>
        </div>

        {/* Indicador de conexão */}
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          Supabase conectado
        </div>
      </div>
    </header>
  )
}
