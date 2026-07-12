import './style.css';
import DOMPurify from 'dompurify';

// --- Utility Functions ---
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function scrollToElement(element) {
    element.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start',
        inline: 'nearest'
    });
}

function scrollToHeader(element) {
    // Find the main header element in the document.
    const mainHeader = document.querySelector('.main-header');

    // If the header doesn't exist, log an error and fall back to the old method.
    if (!mainHeader) {
        console.error('Header element with class "main-header" not found.');
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
    }

    // --- Calculation ---
    // 1. Get the height of the header.
    const headerHeight = mainHeader.offsetHeight;

    // 2. Get the position of the element we want to scroll to.
    const elementPosition = element.getBoundingClientRect().top + window.scrollY;

    // 3. Calculate the target scroll position. We want to place the element's top
    const offsetPosition = elementPosition - headerHeight - 15; 

    // --- Action ---
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}


// --- UI Component Classes ---
class AudioPlayer {
    constructor(playerId, audioSrc, title) {
        this.playerId = playerId;
        this.audioSrc = audioSrc;
        this.title = title;
        this.isInitialized = false;
    }

    static createPlayerHTML(audioData) {
        const playerId = `circular-player-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        // Sanitize the dynamic data
        const sanitizedTitle = DOMPurify.sanitize(audioData.title);

        return `
        <div class="audio-player-wrapper">
            <div id="${playerId}" class="circular-audio-player" data-src="${audioData.src}" data-title="${sanitizedTitle}">
                <audio src="${audioData.src}" preload="metadata"></audio>
                <div class="circular-controls">
                    <button class="circular-play-btn" aria-label="Play/Pause">
                        <img class="icon-play" src="play.svg" alt="Play">
                        <img class="icon-pause hidden" src="pause.svg" alt="Pause">
                    </button>
                </div>
            </div>
            <span class="audio-title">${sanitizedTitle}</span>
        </div>
        `;
    }

    initialize() {
        const playerContainer = document.getElementById(this.playerId);
        if (!playerContainer || playerContainer.classList.contains('initialized')) {
            return;
        }

        const audio = playerContainer.querySelector('audio');
        const playBtn = playerContainer.querySelector('.circular-play-btn');
        const playIcon = playBtn.querySelector('.icon-play');
        const pauseIcon = playBtn.querySelector('.icon-pause');

        if (!audio || !playBtn || !playIcon || !pauseIcon) {
            return;
        }

        playerContainer.classList.add('initialized');
        
        let isProcessing = false;
        
        playBtn.addEventListener('click', (e) => {
            if (isProcessing) return;
            isProcessing = true;
            e.preventDefault();

            // Pause all other players
            document.querySelectorAll('.circular-audio-player audio').forEach(otherAudio => {
                if (otherAudio !== audio && !otherAudio.paused) {
                    otherAudio.pause();
                    const otherPlayBtn = otherAudio.closest('.circular-audio-player').querySelector('.circular-play-btn');
                    if (otherPlayBtn) {
                        const otherPlayIcon = otherPlayBtn.querySelector('.icon-play');
                        const otherPauseIcon = otherPlayBtn.querySelector('.icon-pause');
                        if (otherPlayIcon && otherPauseIcon) {
                            otherPlayIcon.classList.remove('hidden');
                            otherPauseIcon.classList.add('hidden');
                        }
                    }
                }
            });

            if (audio.paused) {
                audio.play().then(() => {
                    // --- 3. SHOW PAUSE ICON, HIDE PLAY ICON ---
                    playIcon.classList.add('hidden');
                    pauseIcon.classList.remove('hidden');
                    isProcessing = false;
                }).catch(() => {
                    isProcessing = false; 
                });
            } else {
                audio.pause();
                // --- 4. SHOW PLAY ICON, HIDE PAUSE ICON ---
                playIcon.classList.remove('hidden');
                pauseIcon.classList.add('hidden');
                isProcessing = false;
            }
        });

        audio.addEventListener('timeupdate', () => {
            // Your progress circle logic would go here if you re-add it
        });
        
        audio.addEventListener('ended', () => {
            // --- 5. ON END, RESET TO SHOW THE PLAY ICON ---
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
        });

        audio.addEventListener('error', () => {
            playBtn.disabled = true;
            const titleElement = playerContainer.closest('.audio-player-wrapper').querySelector('.audio-title');
            if (titleElement) {
                titleElement.textContent += ' (Error)';
            }
        });
    }

    static initializeAll(container) {
        const players = container.querySelectorAll('.circular-audio-player:not(.initialized)');
        players.forEach(playerElement => {
            const audioSrc = playerElement.getAttribute('data-src');
            const title = playerElement.getAttribute('data-title');
            const player = new AudioPlayer(playerElement.id, audioSrc, title);
            player.initialize();
        });
    }
}

class WeatherDisplay {
    static getWeatherIconPath(conditionCode) {
        const codeToIconMap = {
            // Sunny / Clear
            1000: 1000,
            // Partly Cloudy
            1003: 1003,
            // Cloudy
            1006: 1006,
            // Overcast / Fog / Light Snow & Sleet
            1009: 1009, // Overcast
            1030: 1009, // Mist
            1135: 1009, // Fog
            1147: 1009, // Freezing fog
            1066: 1009, // Patchy snow possible
            1069: 1009, // Patchy sleet possible
            1072: 1009, // Patchy freezing drizzle possible
            1204: 1009, // Light sleet
            1210: 1009, // Patchy light snow
            1213: 1009, // Light snow
            1216: 1009, // Patchy moderate snow
            1219: 1009, // Moderate snow
            1249: 1009, // Light sleet showers
            1255: 1009, // Light snow showers
            1261: 1009, // Light showers of ice pellets
            // Light & Moderate Rain
            1183: 1183, // Light rain
            1063: 1183, // Patchy rain possible
            1150: 1183, // Patchy light drizzle
            1153: 1183, // Light drizzle
            1168: 1183, // Freezing drizzle
            1171: 1183, // Heavy freezing drizzle
            1180: 1183, // Patchy light rain
            1186: 1183, // Moderate rain at times
            1189: 1183, // Moderate rain
            1198: 1183, // Light freezing rain
            1240: 1183, // Light rain shower
            // Thunder / Heavy Precipitation / Storms
            1276: 1276, // Moderate or heavy rain with thunder
            1087: 1276, // Thundery outbreaks possible
            1114: 1276, // Blowing snow
            1117: 1276, // Blizzard
            1192: 1276, // Heavy rain at times
            1195: 1276, // Heavy rain
            1201: 1276, // Moderate or heavy freezing rain
            1207: 1276, // Moderate or heavy sleet
            1222: 1276, // Patchy heavy snow
            1225: 1276, // Heavy snow
            1237: 1276, // Ice pellets
            1243: 1276, // Moderate or heavy rain shower
            1246: 1276, // Torrential rain shower
            1252: 1276, // Moderate or heavy sleet showers
            1258: 1276, // Moderate or heavy snow showers
            1264: 1276, // Moderate or heavy showers of ice pellets
            1273: 1276, // Patchy light rain with thunder
            1279: 1276, // Patchy light snow with thunder
            1282: 1276, // Moderate or heavy snow with thunder
        };

        const iconFileName = `${codeToIconMap[conditionCode] || '1000'}.svg`; // Fallback to sunny/default
        return `/weather/${iconFileName}`;
    }

    static display(data, responseContainer) {
        if (!data.name || !data.temp_c || !data.condition) {
        return;
        }
        const weatherInfoEl = responseContainer.querySelector('.weather-info');
        const iconEl = responseContainer.querySelector('.weather-icon');
        const tempEl = responseContainer.querySelector('.weather-temp');
        const cityEl = responseContainer.querySelector('.weather-city');

        if (weatherInfoEl && iconEl && tempEl && cityEl) {
            const temp = Math.round(data.temp_c);
            const conditionCode = data.condition.code;
            const locationName = data.name;

            iconEl.src = WeatherDisplay.getWeatherIconPath(conditionCode);
            tempEl.textContent = `${temp}°C`;
            cityEl.textContent = locationName;

            weatherInfoEl.style.display = 'flex';
        }
    }
}


class MapRenderer {
    static MAPBOX_ACCESS_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
    
    static initialize() {
        if (typeof mapboxgl !== 'undefined') {
            mapboxgl.setRTLTextPlugin(
                'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.3.0/mapbox-gl-rtl-text.js',
                null,
                true 
            );
        }
    }

    static render(containerId, locations) {
        if (typeof mapboxgl === 'undefined') {
            console.warn('Mapbox GL JS not loaded');
            return;
        }

        const mapContainer = document.getElementById(containerId);
        if (!mapContainer || !locations || locations.length === 0) return;

        mapContainer.style.display = 'block';
        mapContainer.style.height = '400px';

        mapboxgl.accessToken = MapRenderer.MAPBOX_ACCESS_TOKEN;

        const map = new mapboxgl.Map({
            container: containerId,
            style: 'mapbox://styles/mapbox/streets-v12',
            center: [locations[0].lon, locations[0].lat],
            zoom: 9,
            worldview: 'MA'
        });

        const bounds = new mapboxgl.LngLatBounds();

        locations.forEach(location => {
            const coordinates = [location.lon, location.lat];

            // Create a container for the popup content
            const popupContent = document.createElement('div');
            popupContent.className = 'map-popup-content';

            // Create and safely set the location name
            const locationName = document.createElement('strong');
            locationName.textContent = location.name; // Use textContent to prevent XSS

            // Create the link
            const directionsLink = document.createElement('a');
            directionsLink.href = `https://www.google.com/maps?q=${location.lat},${location.lon}`; // Correct Google Maps URL
            directionsLink.target = '_blank';
            directionsLink.rel = 'noopener noreferrer';
            directionsLink.className = 'directions-btn';
            directionsLink.textContent = 'Open in Google Maps';

            // Append sanitized elements to the container
            popupContent.appendChild(locationName);
            popupContent.appendChild(directionsLink);

            const popup = new mapboxgl.Popup({ 
                offset: 25,
                closeButton: false
            }).setDOMContent(popupContent); // Use setDOMContent with an element

            new mapboxgl.Marker()
                .setLngLat(coordinates)
                .setPopup(popup)
                .addTo(map);

            bounds.extend(coordinates);
        });

        map.fitBounds(bounds, { padding: 60 });
    }
}

class ConversionDisplay {
    static createPillHTML(data) {
        const fromCurrency = DOMPurify.sanitize(data.from_currency);
        const rate = DOMPurify.sanitize(data.rate);
        const toCurrency = DOMPurify.sanitize(data.to_currency);

        return `
            <div class="conversion-container">
                <div class="conversion-pill">
                    <span class="pill-from">1 ${fromCurrency}</span>
                    <span class="pill-equals">≈</span>
                    <span class="pill-to">${rate} ${toCurrency}</span>
                </div>
            </div>
        `;
    }
}

class SuggestionHandler {
    static addHighlights(responseTextDiv, suggestions) {
        const walker = document.createTreeWalker(
            responseTextDiv,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const textNodes = [];
        let node;
        while ((node = walker.nextNode())) {
            textNodes.push(node);
        }

        textNodes.forEach(textNode => {
            const parent = textNode.parentNode;
            if (!parent) return;

            const originalText = textNode.textContent;
            let highlightedHTML = originalText;

            suggestions.forEach(suggestion => {
                const escapedKeyword = SuggestionHandler.escapeRegExp(suggestion.keyword);

                // --- THIS IS THE FINAL CORRECTED LINE ---
                // We now define a "boundary" as any character that is NOT a Unicode letter, number, or mark.
                // This is far more robust than listing specific punctuation.
                const keywordRegex = new RegExp(`(?<=^|[^\\p{L}\\p{N}\\p{M}])${escapedKeyword}(?=[^\\p{L}\\p{N}\\p{M}]|$)`, 'giu');
                // ------------------------------------------

                highlightedHTML = highlightedHTML.replace(keywordRegex,
                    `<span class="highlight clickable-suggestion" data-question="${suggestion.question}">$&</span>`
                );
            });

            if (highlightedHTML !== originalText) {
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = highlightedHTML;

                while (tempDiv.firstChild) {
                    parent.insertBefore(tempDiv.firstChild, textNode);
                }
                parent.removeChild(textNode);
            }
        });
    }

    static escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    static display(data, responseContainer) {
        if (!data || !data.current || !data.location || !responseContainer) {
            return;
        }

        const weatherInfoEl = responseContainer.querySelector('.weather-info');
        weatherInfoEl.style.display = 'flex';
    }

    static removeAll(chatLog) {
        const highlightedElements = chatLog.querySelectorAll('.clickable-suggestion');
        highlightedElements.forEach(element => {
            const textNode = document.createTextNode(element.textContent);
            element.parentNode.replaceChild(textNode, element);
        });

        const responseTexts = chatLog.querySelectorAll('.response-text');
        responseTexts.forEach(responseText => {
            responseText.normalize();
        });
    }
}

class CircuitLinkDisplay {
    static createHTML(data) {
        // Sanitize data for security, though in this case it's from our backend
        const sanitizedTitle = DOMPurify.sanitize(data.title);
        const circuitId = DOMPurify.sanitize(data.id);
        const iconPath = `/icons/${circuitId}.svg`;

        return `
            <div class="circuit-link-wrapper" data-id="${circuitId}" data-title="${sanitizedTitle}" role="button" tabindex="0">
                <div class="circuit-link-icon" style="mask-image: url('${iconPath}'); -webkit-mask-image: url('${iconPath}');"></div>
                <div class="circuit-link-text">
                    <div class="title">${sanitizedTitle}</div>
                    <div class="subtitle">Click to Discover More</div>
                </div>
            </div>
        `;
    }
}

class CircuitHeaderDisplay {
    static createHTML(data) {
        const sanitizedTitle = DOMPurify.sanitize(data.title);
        const circuitId = DOMPurify.sanitize(data.id);
        const iconPath = `/icons/${circuitId}.svg`;

        return `
            <div class="circuit-header">
                <div class="circuit-header-icon" style="mask-image: url('${iconPath}'); -webkit-mask-image: url('${iconPath}');"></div>
                <h2 class="circuit-header-title">${sanitizedTitle}</h2>
            </div>
        `;
    }
}

class TimelineDisplay {
    static start(context) {
        const timelineWrapper = document.createElement('div');
        timelineWrapper.className = 'timeline-wrapper';
        context.responseMainDiv.appendChild(timelineWrapper);
        return timelineWrapper;
    }

    static end(context) {
        const timelineWrapper = context.responseMainDiv.querySelector('.timeline-wrapper');
        if (timelineWrapper) {
            timelineWrapper.classList.add('timeline-complete');
        }
        // Create a new text element for any content that comes after the timeline
        const newTextElement = document.createElement('div');
        newTextElement.className = 'response-text';
        context.responseMainDiv.appendChild(newTextElement);
        return newTextElement;
    }
}

// --- Chat Manager Class ---
class ChatManager {
    constructor() {
        this.isBotReplying = false;
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.chatForm = document.querySelector('.input-form');
        this.chatInput = document.getElementById('chat-input');
        this.chatLog = document.querySelector('.chat-log');
        this.newConvoButton = document.getElementById('new-convo-btn');
        this.suggestions = document.querySelector('.suggestions-dropdown');
        this.body = document.body;

        this.sendMessageButton = document.getElementById('sendMessageButton-top'); 
        
        // Suggestion buttons
        this.transportBtn = document.getElementById('transport-btn');
        this.attractionsBtn = document.getElementById('attractions-btn');
        this.historyBtn = document.getElementById('history-btn');
        this.emergencyBtn = document.getElementById('emergency-btn');
    }

    async initializeSession() {
        try {
            sessionStorage.setItem('circuitState', 'false');
            await fetch('/api/session/new', {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Failed to initialize a new session on page load:', error);
        }
    }

    bindEvents() {
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitMessage(this.chatInput.value, 'chat_input');
            });
        }

        if (this.sendMessageButton) {
            this.sendMessageButton.addEventListener('click', () => {
                this.submitMessage(this.chatInput.value, 'chat_input');
            });
        }

        if (this.chatLog) {
            this.chatLog.addEventListener('click', (e) => {
                if (this.isBotReplying) return;

                // --- Handler for clickable suggestions ---
                const suggestionEl = e.target.closest('.clickable-suggestion');
                if (suggestionEl) {
                    const question = suggestionEl.dataset.question;
                    if (question) {
                        SuggestionHandler.removeAll(this.chatLog);
                        this.submitMessage(question, 'follow-up-suggestion');
                    }
                    return; // Stop processing after handling the click
                }

                // --- Handler for circuit link clicks (FIXED) ---
                const circuitLinkEl = e.target.closest('.circuit-link-wrapper');
                if (circuitLinkEl) {
                    const title = circuitLinkEl.dataset.title;
                    const circuitId = circuitLinkEl.dataset.id; // Get the circuitId from data-id

                    if (title && circuitId) {
                        // Formulate a user-like message to send to the backend
                        const message = `Tell me more about the ${title}`;
                        
                        // Call submitMessage with the required parameters
                        this.submitMessage(message, 'circuit_link_click', 'circuit', circuitId);
                    }
                    return; // Stop processing after handling the click
                }
            });
        }

        if (this.newConvoButton) {
            this.newConvoButton.addEventListener('click', () => {
                this.startNewConversation();
            });
        }
    }

    toggleChatControls(disabled) {
        if (this.chatForm) this.chatForm.classList.toggle('disabled-form', disabled);
        if (this.transportBtn) this.transportBtn.disabled = disabled;
        if (this.attractionsBtn) this.attractionsBtn.disabled = disabled;
        if (this.historyBtn) this.historyBtn.disabled = disabled;
        if (this.emergencyBtn) this.emergencyBtn.disabled = disabled;
    }

    async submitMessage(rawmessage, source = 'unknown', mode = 'default', circuit = null) {
        const message = rawmessage.trim();
        const maxLength = 2000;

        if (this.isBotReplying || !message.trim()) return;

        if (message.length > maxLength) {
            alert(`Message is too long. Please limit your message to ${maxLength} characters.`);
            return; 
        }

        this.isBotReplying = true;
        this.toggleChatControls(true);

        if (!this.body.classList.contains('chat-active')) {
            this.body.classList.add('chat-active');
        }

        const lastChatTurn = this.chatLog.querySelector('.chat-turn:last-child');

        // If it exists, add a class to finalize its height.
        if (lastChatTurn) {
            lastChatTurn.classList.add('chat-turn-finalized');
        }

        // Create a single container for the new conversational turn
        const chatTurn = document.createElement('div');
        chatTurn.className = 'chat-turn';

        // Add user message to the new turn container
        const userMessageHTML = `<div class="user-message"><div class="user-query-pill" dir="auto">${message}</div></div>`;
        chatTurn.insertAdjacentHTML('beforeend', userMessageHTML);

        // Append the entire turn container to the chat log
        this.chatLog.appendChild(chatTurn);

        // Perform standard UI updates

        this.chatInput.value = '';
        this.chatInput.dir = 'ltr';
        this.newConvoButton.classList.add('visible');
        if (this.suggestions) {
            this.suggestions.classList.remove('display');
        }

        // Scroll the new turn container into view
        setTimeout(() => scrollToHeader(chatTurn), 100);

        // Create the model's wrapper, which will initially hold the loading indicator
        const modelWrapper = document.createElement('div');
        modelWrapper.className = 'model-wrapper';

        // Note: I removed the id="loading-indicator" to prevent duplicate IDs in the DOM.
        const loadingHTML = `
            <div class="model-response loading">
                <div class="logo-loader-container">
                    <img class="response-logo" src="/icon-logo.png" alt="Response Orb">
                    <div class="loader"></div>
                </div>
                <span data-translate="thinking">Hmmm</span>
            </div>`;
        modelWrapper.innerHTML = loadingHTML;

        // Append the model's wrapper to the same turn container
        chatTurn.appendChild(modelWrapper);
        
        // Scroll again to ensure the bottom of the new turn is visible
        setTimeout(() => scrollToHeader(chatTurn), 100);

        try {
            // Pass the modelWrapper to streamResponse so it knows where to render the reply.
            await this.streamResponse(message, source, modelWrapper, mode, circuit);
        } catch (error) {
            // You might also want to pass modelWrapper to your error handler.
            this.handleError(error, modelWrapper);
        } finally {
            this.isBotReplying = false;
            this.toggleChatControls(false);
        }
    }

    async streamResponse(message, source, modelWrapper, mode, circuit) {
        const response = await fetch(`/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message, 
                source: source,
                mode: mode,
                circuit: circuit
            }),
            credentials: 'include'
        });

        if (!response.ok) {
            // 1. Log the specific, technical error for developers
            console.error(`Network error: ${response.status} ${response.statusText}`);

            // 2. Throw a generic error for the application to handle
            throw new Error("Sorry, something went wrong while communicating with the server.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        let isFirstToken = true;
        let modelResponseContainer = null;
        let responseMainDiv = null; // We'll target the main container
        let currentTextElement = null; // This will be the active text segment
        let currentText = ''; 
        let mapContainerId = null;
        let requestId = null;
        let isNewSegment = false;
        let languageChecked = false;
        let isRTL = false;

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            let newlineIndex;
            while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
                const line = buffer.slice(0, newlineIndex).trim();
                buffer = buffer.slice(newlineIndex + 1);

                if (!line) continue;

                try {
                    const event = JSON.parse(line);
                    //console.log("Received event:", event);
                    if (event.type === 'processed_token' && isFirstToken) {
                        isFirstToken = false;

                        // Find the loader element *within* the specific modelWrapper for this turn.
                        const loader = modelWrapper.querySelector('.model-response.loading');

                        // Proceed only if the loader is found in the current context.
                        if (loader) {
                            const responseUUID = generateUUID();
                            mapContainerId = `map-${responseUUID}`;
                            
                            // This HTML represents the full content that will live inside the modelWrapper.
                            // It replaces the loader element entirely.
                            const modelResponseContentHTML = `
                                <div class="model-response">
                                    <div class="header-spacer">
                                        <img class="response-logo" src="/icon-logo.png" alt="Response Orb">
                                        <div class="spacer-right">
                                            <div class="weather-info" style="display: none;">
                                                <img src="" alt="Weather" class="weather-icon" />
                                                <span class="weather-temp"></span>
                                                <span class="weather-city"></span>
                                            </div>
                                            <div aria-label="Report Response" id="report-response-icon" class="action-btn">
                                                <span class="copy-response-icon-mask" style="--icon-url: url('/more-vertical-circle.svg');"></span>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="response-main">
                                        <div class="response-text"></div>
                                    </div>
                                </div>
                                <div id="${mapContainerId}" class="map-container" style="display: none;"></div>
                            `;
                            
                            // Use outerHTML to replace the loader with the new response structure.
                            loader.outerHTML = modelResponseContentHTML;

                            // Get references to the new elements, scoped to the current modelWrapper.
                            responseMainDiv = modelWrapper.querySelector('.response-main');
                            currentTextElement = modelWrapper.querySelector('.response-text');
                        }
                    }

                    // This part remains the same, but now it only ever handles clean text tokens
                    if (event.type === 'processed_token' && currentTextElement) {
                        let token = event.data || ''; 

                        if (isNewSegment) {
                            // Trim leading whitespace, newlines, and periods from the token.
                            token = token.replace(/^[\s.\r\n]+/, '');

                            // If the token is now empty (e.g., it was just ".\\n\\n"),
                            if (!token) continue;

                            // As soon as we get a valid token, turn the flag off.
                            isNewSegment = false;
                        }

                        currentText += token;

                        if (!languageChecked && currentText.length > 3) {
                            const arabicRegex = /[\u0600-\u06FF]/;
                            if (arabicRegex.test(currentText)) {
                                // 1. Set the flag for the entire response stream
                                isRTL = true;
                                // 2. Apply RTL to the current text element
                                currentTextElement.setAttribute('dir', 'rtl');
                                responseMainDiv.setAttribute('dir', 'rtl');
                            }
                            languageChecked = true;
                        }
                        const rawHTML = marked.parse(currentText);
                        currentTextElement.innerHTML = DOMPurify.sanitize(rawHTML);
                    }

                    // Pass event and context to the streamlined handler
                    const newTextElement = await this.handleStreamEvent(event, {
                        modelResponseContainer: modelWrapper,
                        responseMainDiv,
                        currentTextElement,
                        mapContainerId,
                        requestId,
                    });

                    if (newTextElement) {
                        currentTextElement = newTextElement;
                        currentText = ''; 
                        isNewSegment = true; 

                        if (isRTL) {
                            currentTextElement.setAttribute('dir', 'rtl');
                        }
                    }

                } catch (e) {
                    console.error("Failed to parse stream event:", line, e);
                }
            }
        }
    }

    async handleStreamEvent(event, context) {
        let newTextElement = null;

        switch (event.type) {
            case 'context':
                if (context.modelResponseContainer) {
                    context.modelResponseContainer.dataset.requestId = event.data.original_request_id;
                }
                break;

            case 'weather':
                if (context.modelResponseContainer) {
                    WeatherDisplay.display(event.data, context.modelResponseContainer);
                }
                break;

            case 'audio_data':
                if (context.responseMainDiv && context.currentTextElement && event.data) {
                    // Use the current text element as the initial insertion point.
                    let insertionPoint = context.currentTextElement;

                    // Insert each player sequentially.
                    event.data.forEach(audio => {
                        const playerHTML = AudioPlayer.createPlayerHTML(audio);
                        insertionPoint.insertAdjacentHTML('afterend', playerHTML);
                        // Move the insertion point to the element we just created.
                        insertionPoint = insertionPoint.nextElementSibling;
                    });
                    
                    // Initialize all the players we just added.
                    AudioPlayer.initializeAll(context.responseMainDiv);

                    // Create the new text segment for subsequent text.
                    newTextElement = document.createElement('div');
                    newTextElement.className = 'response-text';
                    // Insert the new text segment after the last widget we added.
                    insertionPoint.insertAdjacentElement('afterend', newTextElement);
                }
                break;

            case 'conversions':
                if (context.responseMainDiv && context.currentTextElement && event.data) {
                    const insertionPoint = context.currentTextElement;

                    const pillContainer = document.createElement('div');
                    pillContainer.className = 'conversion-pills';
                    
                    event.data.forEach(conversion => {
                        const pillHTML = ConversionDisplay.createPillHTML(conversion);
                        pillContainer.insertAdjacentHTML('beforeend', pillHTML);
                    });

                    // Insert the container after the current text block.
                    insertionPoint.insertAdjacentElement('afterend', pillContainer);
                }
                break;

            case 'map_data':
                if (event.data && event.data.locations && context.mapContainerId) {
                    MapRenderer.render(context.mapContainerId, event.data.locations);
                }
                break;

            case 'suggestions':
                if (context.currentTextElement && event.data && event.data.suggestions) {
                    SuggestionHandler.addHighlights(context.currentTextElement, event.data.suggestions);
                }
                break;
            
            case 'circuit_link':
                if (context.responseMainDiv && context.currentTextElement && event.data) {
                    const insertionPoint = context.currentTextElement;
                    
                    // 1. Create the HTML for the link widget
                    const linkHTML = CircuitLinkDisplay.createHTML(event.data);
                    insertionPoint.insertAdjacentHTML('afterend', linkHTML);

                    // 2. Create a new, empty text container for any subsequent text
                    newTextElement = document.createElement('div');
                    newTextElement.className = 'response-text';
                    
                    // 3. Insert the new text container after the widget we just added
                    insertionPoint.nextElementSibling.insertAdjacentElement('afterend', newTextElement);
                }
                break;
            
            case 'circuit_header':
                if (context.responseMainDiv && event.data) {
                    const headerHTML = CircuitHeaderDisplay.createHTML(event.data);
                    context.responseMainDiv.insertAdjacentHTML('afterbegin', headerHTML);
                    newTextElement = context.responseMainDiv.querySelector('.response-text');
                }
                break;

            case 'timeline_start':
                newTextElement = TimelineDisplay.start(context);
                break;

            case 'timeline_end':
                newTextElement = TimelineDisplay.end(context);
                break;
            case 'error':
                throw new Error(event.data);
        }
        return newTextElement;
    }

    handleError(error, modelWrapper) { 
        const errorHTML = `<p class="error-text">Sorry, something went wrong. Please try again.</p>`;

        const loader = modelWrapper ? modelWrapper.querySelector('.model-response.loading') : document.getElementById('loading-indicator');

        if (loader) {
            loader.innerHTML = errorHTML;
            loader.classList.remove('loading');
        }
    }

    async startNewConversation() {
        this.body.classList.remove('chat-active');
        if (this.suggestions) {
            this.suggestions.classList.add('display');
        }
        this.chatLog.innerHTML = '';
        this.newConvoButton.classList.remove('visible');
        try {
            sessionStorage.setItem('circuitState', 'false');
            await fetch('/api/session/new', {
                method: 'POST',
                credentials: 'include' // Required to handle cookies
            });
        } catch (error) {
            console.error('Failed to create a new session:', error);
        }
    }
}

// --- Translation System ---
class TranslationManager {
    constructor() {
        this.translations = {
            en: { 
                'chat-bot-ui': 'Chat Bot UI', 
                'new-chat': 'New Chat', 
                'ask-anything': 'Ask anything about Morocco...', 
                'transport': 'Afcon Matches', 
                'attractions': 'Attractions', 
                'history': 'History', 
                'emergency': 'Emergency', 
                'english': 'English', 
                'french': 'French', 
                'spanish': 'Spanish', 
                'portuguese': 'Portuguese', 
                'arabic': 'Arabic',
                'transport-q': 'Tell me about Morocco’s AFCON matches.',
                'attractions-q': 'What are the must-see attractions in Morocco?',
                'history-q': 'Can you tell me about the history of Morocco?',
                'emergency-q': 'What are the emergency numbers in Morocco?',
                'thinking': 'Thinking...',
                'copy': 'Copy',
                'report': 'Report'
            },
            fr: { 
                'chat-bot-ui': 'Interface de Chatbot', 
                'new-chat': 'Nouveau Chat', 
                'ask-anything': 'Demandez n\'importe quoi sur le Maroc...', 
                'transport': 'Matches de la CAN', 
                'attractions': 'Attractions', 
                'history': 'Histoire', 
                'emergency': 'Urgence', 
                'english': 'Anglais', 
                'french': 'Français', 
                'spanish': 'Espagnol', 
                'portuguese': 'Portugais', 
                'arabic': 'Arabe',
                'transport-q': 'Parlez-moi des matchs de la CAN au Maroc.',
                'attractions-q': 'Quelles sont les attractions incontournables au Maroc ?',
                'history-q': 'Pouvez-vous me parler de l\'histoire du Maroc ?',
                'emergency-q': 'Quels sont les numéros d\'urgence au Maroc ?',
                'thinking': 'Réflexion en cours...',
                'copy': 'Copier',
                'report': 'Signaler'
            },
            es: { 
                'chat-bot-ui': 'Interfaz de Chatbot', 
                'new-chat': 'Nuevo Chat', 
                'ask-anything': 'Pregunta cualquier cosa sobre Marruecos...', 
                'transport': 'Partidos de la CAN', 
                'attractions': 'Atracciones', 
                'history': 'Historia', 
                'emergency': 'Emergencia', 
                'english': 'Inglés', 
                'french': 'Francés', 
                'spanish': 'Español', 
                'portuguese': 'Portugués', 
                'arabic': 'Árabe',
                'transport-q': '¿Cuáles son los partidos de la CAN en Marruecos?',
                'attractions-q': '¿Cuáles son las atracciones imperdibles en Marruecos?',
                'history-q': '¿Puedes contarme sobre la historia de Marruecos?',
                'emergency-q': '¿Cuáles son los números de emergencia en Marruecos?',
                'thinking': 'Pensando...',
                'copy': 'Copiar',
                'report': 'Informar'
            },
            pt: { 
                'chat-bot-ui': 'Interface de Chatbot', 
                'new-chat': 'Novo Chat', 
                'ask-anything': 'Pergunte qualquer coisa sobre Marrocos...', 
                'transport': 'Partidos de la CAN', 
                'attractions': 'Atrações', 
                'history': 'História', 
                'emergency': 'Emergência', 
                'english': 'Inglês', 
                'french': 'Francês', 
                'spanish': 'Espanhol', 
                'portuguese': 'Português', 
                'arabic': 'Árabe',
                'transport-q': 'Quais são os partidos da CAN em Marrocos?',
                'attractions-q': 'Quais são as atrações imperdíveis em Marrocos?',
                'history-q': 'Você pode me contar sobre a história de Marrocos?',
                'emergency-q': 'Quais são os números de emergência em Marrocos?',
                'thinking': 'Pensando...',
                'copy': 'Copiar',
                'report': 'Relatar'
            },
            ar: { 
                'chat-bot-ui': 'واجهة روبوت الدردشة', 
                'new-chat': 'دردشة جديدة', 
                'ask-anything': 'اسأل أي شيء عن المغرب...', 
                'transport': 'مباريات كأس الأمم الأفريقية', 
                'attractions': 'مناطق الجذب السياحي', 
                'history': 'التاريخ', 
                'emergency': 'حالة طوارئ', 
                'english': 'الإنجليزية', 
                'french': 'الفرنسية', 
                'spanish': 'الإسبانية', 
                'portuguese': 'البرتغالية', 
                'arabic': 'العربية',
                'transport-q': 'ما هي مباريات كأس الأمم الأفريقية في المغرب؟',
                'attractions-q': 'ما هي المعالم السياحية التي يجب مشاهدتها في المغرب؟',
                'history-q': 'هل يمكنك أن تخبرني عن تاريخ المغرب؟',
                'emergency-q': 'ما هي أرقام الطوارئ في المغرب؟',
                'thinking': '...جاري التفكير',
                'copy': 'نسخ',
                'report': 'إبلاغ'
            }
        };
        
        this.bindEvents();
    }

    applyTranslations(lang) {
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (this.translations[lang] && this.translations[lang][key]) {
                if (element.tagName === 'INPUT' && element.hasAttribute('placeholder')) {
                    element.placeholder = this.translations[lang][key];
                } else {
                    element.textContent = this.translations[lang][key];
                }
            }
        });

        const translationKeyMap = {
            en: 'english',
            fr: 'french',
            es: 'spanish',
            pt: 'portuguese',
            ar: 'arabic'
        };

        document.querySelectorAll('[data-lang]').forEach(button => {
            const langKey = button.getAttribute('data-lang');
            const translationKey = translationKeyMap[langKey];
            if (translationKey && this.translations[lang] && this.translations[lang][translationKey]) {
                button.textContent = this.translations[lang][translationKey];
            }
        });

        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        localStorage.setItem('selectedLanguage', lang);
    }

    loadSavedLanguage() {
        const savedLang = localStorage.getItem('selectedLanguage') || 'en';
        this.applyTranslations(savedLang);
    }

    bindEvents() {
        const languageToggleButton = document.getElementById('language-toggle-btn');
        // --- CHANGED --- Using 'language-dropdown-menu' to match your setup
        const languageDropdownMenu = document.getElementById('language-dropdown-menu');

        if (languageToggleButton && languageDropdownMenu) {
            languageToggleButton.addEventListener('click', (event) => {
                event.stopPropagation();
                // --- CHANGED --- Using 'show' class to match your CSS
                languageDropdownMenu.classList.toggle('show');
                const isExpanded = languageDropdownMenu.classList.contains('show');
                languageToggleButton.setAttribute('aria-expanded', isExpanded);
            });

            languageDropdownMenu.querySelectorAll('[data-lang]').forEach(button => {
                button.addEventListener('click', () => {
                    const selectedLang = button.getAttribute('data-lang');
                    this.applyTranslations(selectedLang);
                    // --- CHANGED --- Using 'show' class
                    languageDropdownMenu.classList.remove('show');
                    languageToggleButton.setAttribute('aria-expanded', 'false');
                });
            });
        }

        window.addEventListener('click', (event) => {
            if (languageDropdownMenu && languageDropdownMenu.classList.contains('show')) {
                // Close if the click is outside the toggle button and the menu
                if (!languageToggleButton.contains(event.target) && !languageDropdownMenu.contains(event.target)) {
                    // --- CHANGED --- Using 'show' class
                    languageDropdownMenu.classList.remove('show');
                    languageToggleButton.setAttribute('aria-expanded', 'false');
                }
            }
        });
    }

    setupSuggestionButtons(chatManager) {
        const suggestionsRef = {
            'transport-btn': 'transport-q',
            'attractions-btn': 'attractions-q',
            'history-btn': 'history-q',
            'emergency-btn': 'emergency-q',
            'transport-btn-mobile': 'transport-q',
            'attractions-btn-mobile': 'attractions-q',
            'history-btn-mobile': 'history-q',
            'emergency-btn-mobile': 'emergency-q'
        };

        for (const [btnId, questionKey] of Object.entries(suggestionsRef)) {
            const button = document.getElementById(btnId);
            if (button) {
                button.addEventListener('click', () => {
                    const currentLang = localStorage.getItem('selectedLanguage');
                    const question = this.translations[currentLang][questionKey] || this.translations['en'][questionKey];
                    chatManager.submitMessage(question, 'suggestion_button');
                });
            }
        }
    }
}

async function sendReport(reason, requestId) {
    // If there's no requestId passed to the function, we can't file a report.
    if (!requestId) {
        console.error("Cannot send report: No requestId was provided.");
        throw new Error("Missing report context.");
    }

    const reportData = {
        reason: reason,
        requestId: requestId, // Use the requestId passed as an argument
        timestamp: new Date().toISOString()
    };

    const minDelayPromise = new Promise(resolve => setTimeout(resolve, 800));

    try {
        const fetchPromise = fetch('/api/report', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(reportData),
            credentials: 'include' 
        });

        const [response] = await Promise.all([fetchPromise, minDelayPromise]);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        throw error;
    }
}

// --- Initialize Application ---
document.addEventListener('DOMContentLoaded', () => {
    const translationManager = new TranslationManager();
    
    // --- 1. Define translations for the welcome popup --- 
    const translations = {
        'en': {
            message: 'Welcome on Akabar',
            submessage: 'Please select a display language',
            button: 'Continue'
        },
        'fr': {
            message: 'Bienvenue sur Akabar',
            submessage: 'Veuillez sélectionner une langue d\'affichage',
            button: 'Continuer'
        },
        'es': {
            message: 'Bienvenido a Akabar',
            submessage: 'Por favor seleccione un idioma',
            button: 'Continuar'
        },
        'pt': {
            message: 'Bem-vindo ao Akabar',
            submessage: 'Selecione um idioma de exibição',
            button: 'Continuar'
        },
        'ar': {
            message: 'مرحبا بك في أكبار',
            submessage: 'الرجاء تحديد لغة الموقع',
            button: 'متابعة'
        }
    };

    // --- Select all necessary elements ---
    const languageSelect = document.getElementById('language-select-dropdown');
    const confirmBtn = document.getElementById('confirm-language-btn');
    const welcomeOverlay = document.getElementById('welcome-overlay');
    const welcomeMessage = document.querySelector('.welcome-message');
    const welcomeSubmessage = document.querySelector('.welcome-submessage');
    
    const languageKey = 'selectedLanguage';

    // --- 2. Create a function to apply translations ---
    const translatePopup = (lang) => {
        if (translations[lang]) {
            welcomeMessage.textContent = translations[lang].message;
            welcomeSubmessage.textContent = translations[lang].submessage;
            confirmBtn.textContent = translations[lang].button;
        }
    };

    // --- 3. Add a 'change' event listener to the dropdown ---
    languageSelect.addEventListener('change', () => {
        const selectedLanguage = languageSelect.value;
        translatePopup(selectedLanguage);
    });

    // --- Existing Logic (with a small improvement) ---
    const savedLanguage = localStorage.getItem(languageKey);

    if (savedLanguage) {
        welcomeOverlay.style.display = 'none';
        // Improvement: Set the dropdown to the saved language for consistency
        languageSelect.value = savedLanguage;
        translationManager.applyTranslations(savedLanguage);
    } else {
        welcomeOverlay.style.display = 'flex';
    }

    confirmBtn.addEventListener('click', () => {
        const selectedLanguage = languageSelect.value;
        try {
            localStorage.setItem(languageKey, selectedLanguage);
            translationManager.applyTranslations(selectedLanguage);
        } catch (e) {
            console.error('Failed to save language to localStorage.', e);
        }
        welcomeOverlay.style.display = 'none';
    });

    // Initialize map renderer
    MapRenderer.initialize();

    // --- Theme Toggle Setup ---
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const whiteLogo = document.getElementById('white-logo');
    const blackLogo = document.getElementById('black-logo');
    const body = document.body;
    const sunIconSrc = '/sun-o.svg';
    const moonIconSrc = '/moon-o.svg';
    const hiddenGemsOverlay = document.getElementById('hidden-gems-overlay');

    const discoverCircuitsBtn = document.getElementById('discover-circuits-btn');
    if (discoverCircuitsBtn) {
        discoverCircuitsBtn.addEventListener('click', () => {
            // 1. Define the message to be sent
            const message = 'Tell me about the best circuits in Morocco for an unforgettable experience!';
            sessionStorage.setItem('circuitState', 'true');
            // 2. Call submitMessage with the message, a source, and the 'circuit' mode
            chatManager.submitMessage(message, 'circuit_start', 'circuit');

            // 3. Close the modal
            closeHiddenGemsModal();
        });
    }

    const applyTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
            blackLogo.classList.add('hidden');
            whiteLogo.classList.remove('hidden');
            themeIcon.src = sunIconSrc;
        } else {
            body.classList.remove('dark-mode');
            blackLogo.classList.remove('hidden');
            whiteLogo.classList.add('hidden');
            themeIcon.src = moonIconSrc;
        }
    };

    const toggleTheme = () => {
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            themeIcon.src = sunIconSrc;
            blackLogo.classList.add('hidden');
            whiteLogo.classList.remove('hidden');
            localStorage.setItem('theme', 'dark');
        } else {
            themeIcon.src = moonIconSrc;
            blackLogo.classList.remove('hidden');
            whiteLogo.classList.add('hidden');
            localStorage.setItem('theme', 'light');
        }
    };

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }
    applyTheme();

    // --- About Section Setup ---
    const aboutButton = document.getElementById('about-btn');
    const closeButton = document.getElementById('close-btn');
    const fullscreenContent = document.getElementById('fullscreen-content');

    if (aboutButton) {
        aboutButton.addEventListener('click', () => {
            fullscreenContent.classList.add('is-visible');
        });
    }
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            fullscreenContent.classList.remove('is-visible');
        });
    }

    // --- Initialize Main Application Components ---
    const chatManager = new ChatManager();
    chatManager.initializeSession();
    

    // Load saved language and setup suggestion buttons using the manager
    translationManager.loadSavedLanguage();
    translationManager.setupSuggestionButtons(chatManager);


    // --- Language Button Text Update ---
    // This part remains to keep the main button's text in sync.
    const selectedLanguageText = document.getElementById('selected-language-text');
    const languageDropdownMenu = document.getElementById('language-dropdown-menu');

    if (languageDropdownMenu && selectedLanguageText) {
        // Set initial button text based on saved language on page load
        const savedLang = localStorage.getItem('selectedLanguage');
        const initialButton = languageDropdownMenu.querySelector(`[data-lang="${savedLang}"]`);
        if (initialButton) {
            selectedLanguageText.textContent = initialButton.textContent.trim();
        }

        // Update button text when a new language is selected
        languageDropdownMenu.addEventListener('click', (event) => {
            const button = event.target.closest('[data-lang]');
            if (button) {
                selectedLanguageText.textContent = button.textContent.trim();
            }
        });
    }

    const chatInput = document.getElementById('chat-input');
    // This regex tests for any character in the Arabic Unicode block.
    const arabicRegex = /[\u0600-\u06FF]/;

    chatInput.addEventListener('input', function() {
        // Check if the input value contains any Arabic characters
        if (arabicRegex.test(this.value)) {
            // If it does, set direction for Arabic. The browser will handle alignment.
            this.dir = 'rtl';
        } else {
            // Otherwise, set it back for LTR languages.
            this.dir = 'ltr';
        }
    });


    // Get elements that we know will exist
    const modalOverlay = document.getElementById('modal-overlay');
    const reportForm = document.getElementById('report-form');
    const reportReasonTextarea = document.getElementById('report-reason');

    // --- Functions to control the modal ---
    const openModal = () => {
        modalOverlay.classList.add('active');
    };

    const closeModal = () => {
        modalOverlay.classList.remove('active');
    };

    const openHiddenGemsModal = () => {
        if (sessionStorage.getItem('circuitState') === 'true') {
            return; 
        }
        hiddenGemsOverlay.classList.add('active');
    };

    const closeHiddenGemsModal = () => {
        hiddenGemsOverlay.classList.remove('active');
    };

    // --- Event Listeners ---

    // 1. Listen for all clicks on the document
    document.addEventListener('click', (event) => {
        // Use .closest() to see if the clicked element (or its parent) is a button we care about
        const clickedElement = event.target;

        // If the report button (or something inside it) was clicked
        const reportButton = clickedElement.closest('#report-response-icon');
        if (reportButton) {
            // Find the parent container that holds our data-request-id
            const messageContainer = reportButton.closest('.model-wrapper');
            if (messageContainer && messageContainer.dataset.requestId) {
                const requestId = messageContainer.dataset.requestId;
                // Temporarily attach the ID to the modal for the form to use
                modalOverlay.dataset.currentRequestId = requestId;
                openModal();
            } else {
                console.error("Could not find a request ID for this message.");
                // Optionally alert the user that reporting is not available for this message
            }
        }

        // If the close button was clicked
        if (clickedElement.closest('#close-btn')) {
            closeModal();
        }

        // If the modal overlay itself was clicked (but not its content)
        if (clickedElement === modalOverlay) {
            closeModal();
        }

        if (clickedElement.closest('#explore-hidden')) {
            openHiddenGemsModal();
        }

        // If the 'hidden gems' modal's close button was clicked
        if (clickedElement.closest('#hidden-gems-close-btn')) {
            closeHiddenGemsModal();
        }

        // If the 'hidden gems' overlay itself was clicked
        if (clickedElement === hiddenGemsOverlay) {
            closeHiddenGemsModal();
        }
    });

    // 2. Listen for the form submission separately
    reportForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const reason = reportReasonTextarea.value.trim();
        const sendButton = event.target.querySelector('.send-report-btn');

        // Retrieve the ID from the modal's dataset
        const requestId = modalOverlay.dataset.currentRequestId;

        if (!reason || !requestId) {
            console.error("Report reason or request ID is missing.");
            return;
        }

        const originalButtonText = sendButton.textContent;
        sendButton.disabled = true;
        sendButton.textContent = 'Sending...';

        try {
            // Pass both the reason and the specific requestId to the function
            const responseData = await sendReport(reason, requestId);
            
            // Clear the form and close the modal on success
            reportReasonTextarea.value = '';
            closeModal();
            // Clean up the stored ID
            delete modalOverlay.dataset.currentRequestId; 

        } finally {
            sendButton.disabled = false;
            sendButton.textContent = originalButtonText;
        }
    });

    const langModalOverlay = document.getElementById('language-modal-overlay');
    const langForm = document.getElementById('language-form');
    const langSelect = document.getElementById('language-select');

    // --- Functions to control the language modal ---
    const openLanguageModal = () => {
        // Optional: You could set the dropdown to the currently active language
        // const currentLang = document.documentElement.lang || 'en';
        // langSelect.value = currentLang;
        langModalOverlay.classList.add('active');
    };

    const closeLanguageModal = () => {
        langModalOverlay.classList.remove('active');
    };

    // --- Event Listeners for the language modal ---

    // 1. Listen for clicks on the document to open/close the modal
    // This can be merged with your existing click listener
    document.addEventListener('click', (event) => {
        const clickedElement = event.target;

        // Assumes you have a button or icon with this ID to open the modal
        if (clickedElement.closest('#pick-language-but')) {
            openLanguageModal();
        }

        // If the language modal's close button was clicked
        if (clickedElement.closest('#lang-close-btn')) {
            closeLanguageModal();
        }

        // If the language modal overlay itself was clicked
        if (clickedElement === langModalOverlay) {
            closeLanguageModal();
        }
    });

    // 2. Listen for the language form submission
    langForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent the form from reloading the page
        const selectedLang = langSelect.value;

        if (selectedLang) {
            translationManager.applyTranslations(selectedLang);
            closeLanguageModal();
        }
    });

});
