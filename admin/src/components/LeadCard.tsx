import { Star, MapPin, Tag } from 'lucide-react'
import type { Lead, LeadStatus } from '../types'
import {
  STATUS_CONFIG,
  formatPhoneForWhatsApp,
  buildWhatsAppLink,
  formatNota,
  formatDate,
} from '../utils/helpers'

interface LeadCardProps {
  lead: Lead
  onStatusChange: (id: string, status: LeadStatus) => Promise<void>
}

export default function LeadCard({ lead, onStatusChange }: LeadCardProps) {
  const cfg = STATUS_CONFIG[lead.status]
  const phone = formatPhoneForWhatsApp(lead.telefone)
  const canSend = lead.status === 'gerado' && !!phone && !!lead.texto_proposta

  // Abre WhatsApp e atualiza status para 'enviado'
  const handleSend = async () => {
    if (!phone || !lead.texto_proposta) return
    window.open(buildWhatsAppLink(phone, lead.texto_proposta), '_blank')
    try {
      await onStatusChange(lead.id, 'enviado')
    } catch {
      // Não bloqueia o usuário — o link já abriu
    }
  }

  return (
    <article
      className={`card animate-slide-up flex flex-col gap-4 ${cfg.border}`}
      aria-label={`Card do lead ${lead.nome_empresa}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="font-bold text-slate-100 text-base truncate leading-tight">
            {lead.nome_empresa}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">{formatDate(lead.criado_em)}</p>
        </div>

        {/* Badge de status */}
        <span className={`badge shrink-0 ${cfg.badge}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} animate-pulse`} />
          {cfg.label}
        </span>
      </div>

      {/* Metadados */}
      <div className="flex flex-wrap gap-3 text-xs text-slate-400">
        {lead.cidade && (
          <span className="flex items-center gap-1">
            <MapPin size={12} className="shrink-0" />
            {lead.cidade}
          </span>
        )}
        {lead.categoria && (
          <span className="flex items-center gap-1">
            <Tag size={12} className="shrink-0" />
            {lead.categoria}
          </span>
        )}
        {lead.nota_google !== null && (
          <span className="flex items-center gap-1 text-amber-400">
            <Star size={12} className="shrink-0 fill-amber-400" />
            {formatNota(lead.nota_google)} no Google
          </span>
        )}
      </div>

      {/* Proposta gerada pela IA */}
      {lead.texto_proposta ? (
        <div className="rounded-xl bg-slate-800/60 border border-slate-700/50 p-3">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-2">
            Proposta da IA
          </p>
          <p className="text-sm text-slate-300 leading-relaxed line-clamp-4">
            {lead.texto_proposta}
          </p>
        </div>
      ) : (
        <div className="rounded-xl bg-slate-800/30 border border-dashed border-slate-700 p-3 text-center">
          <p className="text-xs text-slate-600">Proposta ainda não gerada</p>
        </div>
      )}

      {/* Rodapé: telefone + botão de envio */}
      <div className="flex items-center justify-between gap-2 pt-1 border-t border-slate-800">
        <span className="text-xs text-slate-500 font-mono truncate">
          {lead.telefone ?? 'Sem telefone'}
        </span>

        {canSend ? (
          <button
            id={`btn-send-${lead.id}`}
            onClick={handleSend}
            className="btn-primary text-xs py-1.5 px-3 bg-emerald-600 hover:bg-emerald-500 
                       hover:shadow-emerald-500/30"
            aria-label={`Enviar proposta via WhatsApp para ${lead.nome_empresa}`}
          >
            🚀 Enviar Proposta
          </button>
        ) : lead.status === 'enviado' ? (
          <span className="text-xs text-emerald-500 font-semibold flex items-center gap-1">
            ✓ Enviado
          </span>
        ) : (
          <span className="text-xs text-slate-600 italic">
            {!phone ? 'Sem número' : 'Gere a proposta primeiro'}
          </span>
        )}
      </div>
    </article>
  )
}
