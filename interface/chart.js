// Obtenemos del objeto global
const { createChart, CandlestickSeries, HistogramSeries, CrosshairMode } = LightweightCharts;

(async () => {
  const chart = createChart(document.getElementById('chart'), {
    layout: {
      background: { type: 'solid', color: '#000' },
      textColor: '#DDD',
    },
    grid: {
      vertLines: { color: '#222' },
      horzLines: { color: '#222' },
    },
    crosshair: { mode: CrosshairMode.Normal },
    timeScale: { timeVisible: true, secondsVisible: false, borderColor: '#555' },
    priceScale: { borderColor: '#555' },
  });

  // Velas
  const candleSeries = chart.addSeries(CandlestickSeries, {
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
  });

  // Volumen
  const volumeSeries = chart.addSeries(HistogramSeries, {
    priceFormat: { type: 'Volume' },
    priceScaleId: '',  // overlay para que quede abajo
    scaleMargins: { top: 0.8, bottom: 0 },
  });

    // ① Traigo el CSV como texto
    const res = await fetch('static/ohlcv_data.csv');
    const csvText = await res.text();

    // ② Parseo con PapaParse (header: true, convierte tipos)
    const { data: raw } = Papa.parse(csvText, {
    header: true,
    dynamicTyping: true
    });

    // ③ Mapeo a formato candles
    candles = raw.map(d => ({
    time: d.timestamp ?? d.time,  // ajustá si tu columna se llama "timestamp" o "time"
    open:   d.Open,
    high:   d.High,
    low:    d.Low,
    close:  d.Close,
    volume: d.Volume
    }));

    console.log('Candles parsed:', candles);
    candles = raw.map(d => ({
    // parsea "2025-07-16 10:17:00" y lo convierte a segundos
    time: Math.floor(Date.parse(d.time) / 1000),
    open:  +d.Open,
    high:  +d.High,
    low:   +d.Low,
    close: +d.Close,
    volume:+d.Volume
    }));
    console.log('Final candles:', candles.slice(0,5));
  const marks = await fetch('static/marks.json');
  candleSeries.setData(candles);
  volumeSeries.setData(candles.map(c => ({
    time: c.time,
    value: c.volume,
    color: c.close > c.open ? '#26a69a' : '#ef5350',
  })));

  // Para incluir flechitas, usamos createSeriesMarkers
  const { createSeriesMarkers } = LightweightCharts;
  const markers = createSeriesMarkers(candleSeries, marks);

  chart.timeScale().fitContent();
})();