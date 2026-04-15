import { useEffect, useState, useCallback } from 'react'
import { supabase } from '../lib/supabase'
import type { Lead, LeadStatus } from '../types'

interface UseLeadsReturn {
  leads: Lead[]
  loading: boolean
  error: string | null
  filterStatus: LeadStatus | 'todos'
  setFilterStatus: (s: LeadStatus | 'todos') => void
  refetch: () => Promise<void>
  updateStatus: (id: string, status: LeadStatus) => Promise<void>
}

// Hook customizado que encapsula toda a lógica de dados
export function useLeads(): UseLeadsReturn {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filterStatus, setFilterStatus] = useState<LeadStatus | 'todos'>('todos')

  const fetchLeads = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      let query = supabase
        .from('leads_prospeccao')
        .select('*')
        .order('criado_em', { ascending: false })

      if (filterStatus !== 'todos') {
        query = query.eq('status', filterStatus)
      }

      const { data, error: sbError } = await query

      if (sbError) throw sbError
      setLeads((data as Lead[]) ?? [])
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Erro desconhecido ao buscar leads.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [filterStatus])

  // Atualiza status de um lead individualmente
  const updateStatus = useCallback(async (id: string, status: LeadStatus) => {
    const { error: sbError } = await supabase
      .from('leads_prospeccao')
      .update({ status })
      .eq('id', id)

    if (sbError) throw sbError

    // Atualiza local sem re-fetch completo para UX imediata
    setLeads(prev => prev.map(l => (l.id === id ? { ...l, status } : l)))
  }, [])

  useEffect(() => {
    fetchLeads()
  }, [fetchLeads])

  return { leads, loading, error, filterStatus, setFilterStatus, refetch: fetchLeads, updateStatus }
}
