import { motion, AnimatePresence } from "framer-motion";
import type { ChangeRecord } from "../../types";

interface Props {
  banner: ChangeRecord | null;
}

export function EventBanner({ banner }: Props) {
  return (
    <AnimatePresence>
      {banner && (
        <motion.div
          initial={{ y: -60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -60, opacity: 0 }}
          transition={{ type: "spring", damping: 20 }}
          className="absolute top-0 left-0 right-0 z-30"
        >
          <div className="mx-auto max-w-xl">
            <div className="bg-purple-500/20 border border-purple-500/30 rounded-b-xl px-5 py-3 text-center backdrop-blur-sm">
              <p className="text-xs text-purple-400 uppercase tracking-wider font-semibold mb-0.5">
                Event
              </p>
              <p className="text-sm text-purple-200 font-medium">
                📢 {banner.description}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
