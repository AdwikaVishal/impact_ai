import { motion, AnimatePresence } from 'framer-motion';
import HeadlineInput from './HeadlineInput';
import { useAnalysisStore } from '../../stores/useAnalysisStore';
import RiskBanner from '../RiskBanner';
import MetricsGrid from '../MetricsGrid';
import Explanation from '../Explanation';

export default function HeadlineAnalyzer() {
  const { analysis } = useAnalysisStore();

  return (
    <div className="space-y-6">
      <HeadlineInput />

      <AnimatePresence>
        {analysis && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-5"
          >
            <RiskBanner />
            <MetricsGrid />
            <Explanation />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
