import { useState } from 'react'
import { UserPlus, Check, AlertCircle, Mail, User, Lock, Briefcase } from 'lucide-react'
import { toast } from 'sonner'

const ROLES = [
  { value: 'STUDENT', label: 'Étudiant' },
  { value: 'PROFESSOR', label: 'Professeur' },
  { value: 'STAFF', label: 'Personnel DIT' },
]

const MOCK_MEMBERS = [
  { id: '1', name: 'Mamadou Diallo', email: 'mdiallo@dit.sn', role: 'STUDENT' },
  { id: '2', name: 'Admin DIT', email: 'admin@dit.sn', role: 'STAFF' },
  { id: '3', name: 'Fatou Sow', email: 'fsow@dit.sn', role: 'PROFESSOR' },
  { id: '4', name: 'Ibrahima Ba', email: 'iba@dit.sn', role: 'STUDENT' },
]

const ROLE_STYLE: Record<string, { bg: string; text: string }> = {
  STUDENT:   { bg: 'bg-blue-50',   text: 'text-blue-600' },
  PROFESSOR: { bg: 'bg-purple-50', text: 'text-purple-600' },
  STAFF:     { bg: 'bg-teal-50',   text: 'text-[#004455]' },
}

type Form = { firstName: string; lastName: string; email: string; role: string; password: string }
const EMPTY: Form = { firstName: '', lastName: '', email: '', role: 'STUDENT', password: '' }

export function AdminUsersTab() {
  const [members, setMembers] = useState(MOCK_MEMBERS)
  const [form, setForm] = useState<Form>(EMPTY)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const set = (key: keyof Form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const USERS_API = import.meta.env.VITE_USERS_API_URL ?? 'http://localhost:8002'
      const res = await fetch(`${USERS_API}/api/users/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          first_name: form.firstName,
          last_name: form.lastName,
          role: form.role,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        const msg = Object.values(data).flat().join(' ')
        throw new Error(msg || 'Erreur lors de la création')
      }
      setMembers([
        { id: data.id, name: `${form.firstName} ${form.lastName}`, email: form.email, role: form.role },
        ...members,
      ])
      setForm(EMPTY)
      toast.success(`${form.firstName} ${form.lastName} ajouté·e`)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-5 space-y-6">
      {/* Members list */}
      <div>
        <h2 className="font-bold text-gray-900 text-sm mb-3">Membres ({members.length})</h2>
        <div className="space-y-2">
          {members.map((m) => {
            const style = ROLE_STYLE[m.role] ?? ROLE_STYLE.STUDENT
            return (
              <div key={m.id} className="flex items-center gap-3 bg-white rounded-2xl border border-gray-100 p-3 shadow-sm">
                <div
                  className="w-9 h-9 rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                  style={{ backgroundColor: '#004455' }}
                >
                  {m.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 text-sm line-clamp-1">{m.name}</p>
                  <p className="text-gray-400 text-xs line-clamp-1">{m.email}</p>
                </div>
                <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${style.bg} ${style.text}`}>
                  {ROLES.find((r) => r.value === m.role)?.label ?? m.role}
                </span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Invite form */}
      <div className="relative overflow-hidden rounded-3xl border border-border/70 bg-card p-5 shadow-sm">
        <div className="pointer-events-none absolute -right-10 -top-10 w-40 h-40 rounded-full bg-primary/8 blur-2xl" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ backgroundColor: '#00445512' }}>
              <UserPlus className="w-4 h-4" style={{ color: '#004455' }} />
            </div>
            <h2 className="font-bold text-gray-900 text-sm">Inviter un utilisateur</h2>
          </div>

          <form onSubmit={handleInvite} className="space-y-3">
            {error && (
              <div className="flex items-center gap-2 text-xs text-destructive bg-destructive/10 rounded-xl px-3 py-2">
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                {error}
              </div>
            )}

            <div className="grid grid-cols-2 gap-2">
              {[
                { label: 'Prénom', key: 'firstName' as const, Icon: User },
                { label: 'Nom', key: 'lastName' as const, Icon: User },
              ].map(({ label, key, Icon }) => (
                <div key={key}>
                  <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{label}</label>
                  <div className="relative mt-1">
                    <Icon className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                    <input
                      value={form[key]}
                      onChange={set(key)}
                      required
                      className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                    />
                  </div>
                </div>
              ))}
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Email</label>
              <div className="relative mt-1">
                <Mail className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  type="email"
                  value={form.email}
                  onChange={set('email')}
                  required
                  placeholder="prenom.nom@dit.sn"
                  className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Mot de passe provisoire</label>
              <div className="relative mt-1">
                <Lock className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <input
                  type="password"
                  value={form.password}
                  onChange={set('password')}
                  required
                  minLength={8}
                  placeholder="min. 8 caractères"
                  className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Rôle</label>
              <div className="relative mt-1">
                <Briefcase className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                <select
                  value={form.role}
                  onChange={set('role')}
                  className="w-full pl-8 pr-3 py-2 rounded-xl border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 appearance-none"
                >
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 rounded-full bg-primary py-2.5 text-sm font-medium text-primary-foreground shadow-sm hover:opacity-90 transition-opacity disabled:opacity-50 mt-1"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              {loading ? 'Création...' : 'Créer le compte'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
