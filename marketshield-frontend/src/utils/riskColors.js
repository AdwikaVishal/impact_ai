export const riskColors = {
  low: {
    bg: 'bg-success',
    text: 'text-success',
    border: 'border-success',
    gradient: 'from-success/20 via-success/10 to-transparent',
    signalBg: 'bg-success/20',
  },
  medium: {
    bg: 'bg-warning',
    text: 'text-warning',
    border: 'border-warning',
    gradient: 'from-warning/20 via-warning/10 to-transparent',
    signalBg: 'bg-warning/20',
  },
  high: {
    bg: 'bg-danger',
    text: 'text-danger',
    border: 'border-danger',
    gradient: 'from-danger/20 via-danger/10 to-transparent',
    signalBg: 'bg-danger/20',
  },
};

export const getRiskColor = (level) => {
  return riskColors[level?.toLowerCase()] || riskColors.medium;
};
