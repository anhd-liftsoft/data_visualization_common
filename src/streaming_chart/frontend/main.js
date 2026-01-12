// Streaming Chart Component using Lightweight Charts
// Import msgpack decoder
import { decodeMessage, encodeMessage } from './msgpack.js';

(function () {
    'use strict';

    // Configuration from Streamlit
    const config = window.STREAMING_CHART_CONFIG || {
        websocketUrl: '',
        topic: 'market.data@BTC',
        candleInterval: 60
    };

    // DOM Elements
    const chartContainer = document.getElementById('chart');
    const symbolNameEl = document.getElementById('symbol-name');
    const connectionStatusEl = document.getElementById('connection-status');
    const currentPriceEl = document.getElementById('current-price');
    const priceChangeEl = document.getElementById('price-change');
    const volume24hEl = document.getElementById('volume-24h');
    const lastUpdateEl = document.getElementById('last-update');

    // Chart state
    let chart = null;
    let candlestickSeries = null;
    let volumeSeries = null;
    let ws = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;
    const reconnectDelay = 3000;

    // Price data for calculating change
    let firstPrice = null;
    let lastPrice = null;
    const maxDataPoints = 500; // Keep last 500 candles

    // Candlestick data management
    const candleInterval = config.candleInterval || 60; // Candle interval in seconds
    let currentCandle = null; // Current forming candle
    let candleData = []; // Historical candles

    // Initialize the chart
    function initChart() {
        if (!chartContainer) return;

        chart = LightweightCharts.createChart(chartContainer, {
            layout: {
                background: { type: 'solid', color: '#131722' },
                textColor: '#d1d4dc',
            },
            grid: {
                vertLines: { color: '#1e222d' },
                horzLines: { color: '#1e222d' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#2a2e39',
                scaleMargins: {
                    top: 0.05,
                    bottom: 0.25, // Leave space for volume pane
                },
            },
            timeScale: {
                borderColor: '#2a2e39',
                timeVisible: true,
                secondsVisible: true,
            },
            handleScale: {
                axisPressedMouseMove: true,
            },
            handleScroll: {
                vertTouchDrag: true,
            },
        });

        // Create candlestick series for price (top pane - 75%)
        candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderDownColor: '#ef5350',
            borderUpColor: '#26a69a',
            wickDownColor: '#ef5350',
            wickUpColor: '#26a69a',
            priceFormat: {
                type: 'price',
                precision: 2,
                minMove: 0.01,
            },
        });

        // Create histogram series for volume (bottom pane - 25%)
        volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: 'volume', // Separate price scale for volume
        });

        // Configure volume price scale (bottom pane)
        chart.priceScale('volume').applyOptions({
            scaleMargins: {
                top: 0.8, // Volume pane starts at 80% from top
                bottom: 0,
            },
            borderColor: '#2a2e39',
        });

        // Auto-resize chart
        const resizeObserver = new ResizeObserver(entries => {
            if (chart) {
                const { width, height } = entries[0].contentRect;
                chart.resize(width, height);
            }
        });
        resizeObserver.observe(chartContainer);

        // Initial resize
        chart.resize(chartContainer.clientWidth, chartContainer.clientHeight);
    }

    // Update connection status
    function updateConnectionStatus(status) {
        connectionStatusEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        connectionStatusEl.className = 'status ' + status;
    }

    // Format number with thousands separator
    function formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return '--';
        return num.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    // Format volume
    function formatVolume(vol) {
        if (vol >= 1e9) return (vol / 1e9).toFixed(2) + 'B';
        if (vol >= 1e6) return (vol / 1e6).toFixed(2) + 'M';
        if (vol >= 1e3) return (vol / 1e3).toFixed(2) + 'K';
        return vol.toFixed(2);
    }

    // Format timestamp
    function formatTimestamp(ts) {
        const date = new Date(ts);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    // Update price display with flash animation
    function updatePriceDisplay(price, symbol) {
        // Update symbol name
        if (symbol) {
            symbolNameEl.textContent = symbol;
        }

        // Update price with flash animation
        const oldPrice = lastPrice;
        currentPriceEl.textContent = '$' + formatNumber(price);

        if (oldPrice !== null) {
            currentPriceEl.classList.remove('flash-up', 'flash-down');
            // Force reflow to restart animation
            void currentPriceEl.offsetWidth;

            if (price > oldPrice) {
                currentPriceEl.classList.add('flash-up');
            } else if (price < oldPrice) {
                currentPriceEl.classList.add('flash-down');
            }
        }

        // Calculate and update price change
        if (firstPrice === null) {
            firstPrice = price;
        }

        const change = price - firstPrice;
        const changePercent = (change / firstPrice) * 100;

        priceChangeEl.textContent = `${change >= 0 ? '+' : ''}${formatNumber(change)} (${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%)`;
        priceChangeEl.className = 'change ' + (change >= 0 ? 'positive' : 'negative');

        lastPrice = price;
    }

    // Get the candle time bucket for a given timestamp
    function getCandleTime(timestamp) {
        return Math.floor(timestamp / candleInterval) * candleInterval;
    }

    // Update or create candle with new price data
    function updateCandle(price, timestamp, volume) {
        const candleTime = getCandleTime(timestamp);

        // Check if we need to start a new candle
        if (currentCandle === null || currentCandle.time !== candleTime) {
            // Save the previous candle to history if exists
            if (currentCandle !== null) {
                candleData.push({ ...currentCandle });

                // Limit historical candles
                if (candleData.length > maxDataPoints) {
                    candleData.shift();
                }
            }

            // Create new candle
            currentCandle = {
                time: candleTime,
                open: price,
                high: price,
                low: price,
                close: price,
                volume: volume || 0
            };
        } else {
            // Update existing candle
            currentCandle.high = Math.max(currentCandle.high, price);
            currentCandle.low = Math.min(currentCandle.low, price);
            currentCandle.close = price;
            if (volume) {
                currentCandle.volume = volume;
            }
        }

        // Update chart with current candle
        if (candlestickSeries) {
            candlestickSeries.update({
                time: currentCandle.time,
                open: currentCandle.open,
                high: currentCandle.high,
                low: currentCandle.low,
                close: currentCandle.close
            });
        }

        // Update volume chart
        if (volumeSeries) {
            const isUp = currentCandle.close >= currentCandle.open;
            volumeSeries.update({
                time: currentCandle.time,
                value: currentCandle.volume,
                color: isUp ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
            });
        }
    }

    // Handle incoming WebSocket message (binary msgpack data)
    async function handleMessage(event) {
        try {
            let parsed;

            // Check if data is binary (Blob or ArrayBuffer)
            if (event.data instanceof Blob) {
                // Convert Blob to ArrayBuffer
                const buffer = await event.data.arrayBuffer();
                parsed = decodeMessage(buffer);
            } else if (event.data instanceof ArrayBuffer) {
                parsed = decodeMessage(event.data);
            } else {
                // Fallback to JSON for text messages
                parsed = JSON.parse(event.data);
            }

            console.log('Received message:', parsed);

            // Check if this is market data
            if (parsed && parsed.type === 'market_data' && parsed.data) {
                const data = parsed.data;
                const timestamp = new Date(data.ts).getTime() / 1000; // Convert to Unix timestamp in seconds

                // Update candlestick chart
                updateCandle(data.price, timestamp, data.volume_24h);

                // Update UI elements
                updatePriceDisplay(data.price, data.symbol);
                volume24hEl.textContent = formatVolume(data.volume_24h);
                lastUpdateEl.textContent = 'Last update: ' + formatTimestamp(data.ts);
            }

            // Handle ping message - respond with pong
            if (parsed && parsed.type === 'ping') {
                const pongMessage = encodeMessage({ type: 'pong' });
                ws.send(pongMessage);
            }
        } catch (e) {
            console.error('Error parsing message:', e);
        }
    }

    // Connect to WebSocket
    function connectWebSocket() {
        if (!config.websocketUrl) {
            console.warn('No WebSocket URL configured');
            updateConnectionStatus('disconnected');
            return;
        }

        updateConnectionStatus('connecting');

        try {
            ws = new WebSocket(config.websocketUrl);

            // Set binary type to receive ArrayBuffer
            ws.binaryType = 'arraybuffer';

            ws.onopen = function () {
                console.log('WebSocket connected');
                updateConnectionStatus('connected');
                reconnectAttempts = 0;

                // Subscribe to topic if needed (send as msgpack binary)
                if (config.topic) {
                    const subscribeMessage = encodeMessage({
                        action: 'subscribe',
                        topic: config.topic
                    });
                    ws.send(subscribeMessage);
                }
            };

            ws.onmessage = function (event) {
                handleMessage(event);
            };

            ws.onerror = function (error) {
                console.error('WebSocket error:', error);
                updateConnectionStatus('disconnected');
            };

            ws.onclose = function () {
                console.log('WebSocket closed');
                updateConnectionStatus('disconnected');

                // Attempt to reconnect
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Reconnecting in ${reconnectDelay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                    setTimeout(connectWebSocket, reconnectDelay);
                }
            };
        } catch (e) {
            console.error('Error connecting to WebSocket:', e);
            updateConnectionStatus('disconnected');
        }
    }

    // Initialize everything when DOM is ready
    function init() {
        initChart();
        connectWebSocket();
    }

    // Start initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', function () {
        if (ws) {
            ws.close();
        }
    });
})();
