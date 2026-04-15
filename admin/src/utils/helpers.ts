import type { LeadStatus } from '../types'

// Paleta de cores por status — usada no badge e no card border
export const STATUS_CONFIG: Record<
  LeadStatus,
  { label: string; badge: string; dot: string; border: string }
> = {
  novo: {
    label: 'Novo',
    badge: 'bg-blue-500/15 text-blue-400 ring-1 ring-blue-500/30',
    dot:   'bg-blue-400',
    border: 'hover:border-blue-500/40',
  },
  gerado: {
    label: 'Gerado',
    badge: 'bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/30',
    dot:   'bg-amber-400',
    border: 'hover:border-amber-500/40',
  },
  enviado: {
    label: 'Enviado',
    badge: 'bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/30',
    dot:   'bg-emerald-400',
    border: 'hover:border-emerald-500/40',
  },
  fechado: {
    label: 'Fechado',
    badge: 'bg-slate-500/15 text-slate-400 ring-1 ring-slate-500/30',
    dot:   'bg-slate-400',
    border: 'hover:border-slate-500/40',
  },
}

// Formata número de telefone para envio ao WhatsApp
export function formatPhoneForWhatsApp(phone: string | null): string | null {
  if (!phone) return null
  const digits = phone.replace(/\D/g, '')
  if (!digits) return null
  return digits.startsWith('55') && digits.length >= 12 ? digits : `55${digits}`
}

// Monta o link de abertura do WhatsApp com a proposta codificada
export function buildWhatsAppLink(phone: string, text: string): string {
  return `https://api.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(text)}`
}

// Formata a nota do Google com 1 casa decimal
export function formatNota(nota: number | null): string {
  if (nota === null || nota === undefined) return '—'
  return nota.toFixed(1)
}

// Formata data para pt-BR curto
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('pt-BR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
  })
}
