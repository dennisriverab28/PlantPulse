import { motion } from 'framer-motion'
import { Construction } from 'lucide-react'

export default function ComingSoon({ title, slice, blurb }: { title: string; slice: number; blurb: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="mx-auto mt-16 max-w-md rounded-xl border border-zinc-800 bg-zinc-950 p-8 text-center"
    >
      <Construction className="mx-auto mb-4 h-8 w-8 text-amber-400" />
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-sm text-zinc-400">{blurb}</p>
      <p className="mt-4 text-xs uppercase tracking-widest text-zinc-600">arriving in slice {slice}</p>
    </motion.div>
  )
}
