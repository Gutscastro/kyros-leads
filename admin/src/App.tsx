import Header from './components/Header'
import StatsBar from './components/StatsBar'
import FilterBar from './components/FilterBar'
import LeadCard from './components/LeadCard'
import { useLeads } from './hooks/useLeads'
import { Loader2, SearchX } from 'lucide-react'

function App() {
  const { 
    leads, 
    loading, 
    error, 
    filterStatus, 
    setFilterStatus, 
    refetch, 
    updateStatus 
  } = useLeads()

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Sumário de Estatísticas */}
        <StatsBar leads={leads} />

        {/* Filtros e Ações */}
        <FilterBar 
          active={filterStatus} 
          onChange={setFilterStatus} 
          onRefresh={refetch}
          loading={loading}
        />

        {/* Tratamento de Erro */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl text-center text-sm">
            ❌ {error}
          </div>
        )}

        {/* Grid de Leads */}
        <div className="relative min-h-[400px]">
          {loading && leads.length === 0 ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-slate-500">
              <Loader2 className="animate-spin" size={32} />
              <p className="text-sm font-medium">Carregando leads do Supabase...</p>
            </div>
          ) : leads.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {leads.map(lead => (
                <LeadCard 
                  key={lead.id} 
                  lead={lead} 
                  onStatusChange={updateStatus} 
                />
              ))}
            </div>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 text-slate-600">
              <div className="bg-slate-900 p-4 rounded-full">
                <SearchX size={48} />
              </div>
              <div className="text-center">
                <p className="text-lg font-bold text-slate-400">Nenhum lead encontrado</p>
                <p className="text-sm">Tente mudar o filtro ou rodar o scanner_leads.py</p>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="py-8 border-t border-slate-900 text-center text-xs text-slate-600">
        <p>© 2026 Kyros Digital — Sistema de Prospecção Proativa</p>
      </footer>
    </div>
  )
}

export default App
