import { motion } from 'framer-motion';
import HeadlineInput from './HeadlineInput';
import { useAnalysisStore } from '../../stores/useAnalysisStore';
import RiskBanner from '../RiskBanner';
import MetricsGrid from '../MetricsGrid';
import Explanation from '../Explanation';

export default function HeadlineAnalyzer() {
  const { analysis } = useAnalysisStore();

  return (
    <section className="max-w-7xl mx-auto">
      {/* INPUT AT TOP */}
      <HeadlineInput />

      {/* RESULTS */}
      {analysis && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-12 space-y-8"
        >
          <RiskBanner />
          <MetricsGrid />
          <Explanation />
        </motion.div>
      )}
    </section>
  );
}
