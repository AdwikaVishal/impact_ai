import { useEffect, useRef } from 'react';

export default function TradingViewChart({ symbol = 'NSE:NIFTY' }) {
  const containerRef = useRef();
  const widgetRef = useRef(null);

  useEffect(() => {
    // Clean up previous widget
    if (widgetRef.current) {
      try {
        widgetRef.current.remove();
      } catch (e) {
        console.log('Widget cleanup:', e);
      }
      widgetRef.current = null;
    }

    // Load TradingView script
    const loadWidget = () => {
      if (window.TradingView && containerRef.current) {
        const containerId = `tradingview_${Math.random().toString(36).substr(2, 9)}`;
        containerRef.current.id = containerId;

        widgetRef.current = new window.TradingView.widget({
          autosize: true,
          symbol: symbol,
          interval: 'D',
          timezone: 'Asia/Kolkata',
          theme: 'dark',
          style: '1',
          locale: 'en',
          toolbar_bg: '#1e293b',
          enable_publishing: false,
          hide_top_toolbar: false,
          hide_legend: false,
          save_image: false,
          container_id: containerId,
          hide_side_toolbar: false,
          allow_symbol_change: true,
          studies: [],
          show_popup_button: false,
          popup_width: '1000',
          popup_height: '650',
        });
      }
    };

    if (window.TradingView) {
      loadWidget();
    } else {
      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/tv.js';
      script.async = true;
      script.onload = loadWidget;
      document.head.appendChild(script);
    }

    return () => {
      if (widgetRef.current) {
        try {
          widgetRef.current.remove();
        } catch (e) {
          console.log('Cleanup error:', e);
        }
        widgetRef.current = null;
      }
    };
  }, [symbol]);

  return (
    <div 
      ref={containerRef}
      className="w-full h-full"
      style={{ position: 'relative', minHeight: '400px' }}
    />
  );
}
