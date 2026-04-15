// Tipagem centralizada da tabela leads_prospeccao
export type LeadStatus = 'novo' | 'gerado' | 'enviado' | 'fechado'

export interface Lead {
  id: string
  nome_empresa: string
  telefone: string | null
  categoria: string | null
  cidade: string | null
  nota_google: number | null
  texto_proposta: string | null
  status: LeadStatus
  criado_em: string
}
