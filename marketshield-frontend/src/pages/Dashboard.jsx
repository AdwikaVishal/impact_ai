import { motion } from 'framer-motion';
import HeroChart from '../components/dashboard/HeroChart';

export default function Dashboard() {
  return (
    <div className="max-w-[1400px] mx-auto px-8 lg:px-16">
      {/* HERO CHART - COMPACT SPACING */}
      <div className="mb-16">
        <HeroChart />
      </div>
    </div>
  );
}
