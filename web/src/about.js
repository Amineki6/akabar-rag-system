class TranslationManager {
    constructor() {
        this.translations = {
            en: {
                'home-page': 'Chat',
                // --- New / Updated Content from HTML ---

                // About Us Section
                'mission-title': 'About Us',
                'mission-text': 'Our mission is to provide every tourist with an instant, accurate, and personalized digital guide, empowering you to explore Morocco with confidence and connect more deeply with its rich culture.',

                // The Problem Section
                'journey-title': 'Redefining the Modern Journey',
                'journey-text': 'We understand that the modern traveler\'s journey begins online. However, planning can be overwhelming, with valuable information often fragmented across countless websites, blogs, and forums. A single question can yield thousands of conflicting and unverified opinions, making it difficult for official, authoritative sources to guide visitors effectively. <br> This digital gap creates uncertainty and friction, from the "Dreaming" phase all the way through to the "Sharing" phase of your journey. Our goal is to eliminate that friction.',

                // The Solution Section
                'solution-title': 'The Solution: A True Digital Concierge',
                'solution-text': 'Akabar is a state-of-the-art digital platform designed to serve as your 24/7 concierge and Morocco\'s single, official source of truth for tourists. We go beyond simple text answers to offer a rich, interactive experience:',
                'solution-li1': '<strong>Instant Answers:</strong> Get clear and helpful responses to a vast range of queries, from cultural etiquette tips to practical questions about transport.',
                'solution-li2': '<strong>Interactive Maps:</strong> Ask for directions or recommendations and receive dynamic maps with pinned locations to help you visualize your plans instantly.',
                'solution-li3': '<strong>Immersive Culture:</strong> Discover Morocco\'s heritage through engaging multimedia, including playable snippets of traditional music like Gnawa.',

                // Trust & Accuracy Section
                'trust-title': 'A Foundation of Trust & Accuracy',
                'trust-text': 'Our platform\'s most important feature is its commitment to accuracy. Akabar is built on a secure "walled garden" architecture. This means its entire universe of knowledge is strictly limited to official, pre-approved data sources provided and reviewed by experts. The AI is architecturally prohibited from accessing the open internet for answers. This is our guarantee that every response is reliable, directly combats online misinformation, and aligns with the highest standards of our nation\'s hospitality.',

                // Contact Section
                'contact-title': 'Contact Us',
                'contact-text': 'We are dedicated to making your journey in Morocco seamless and unforgettable. For inquiries about this project, please contact us:',
                'contact-email': 'kinaamine@gmail.com',
                'english': 'English',
                'french': 'French',
                'spanish': 'Spanish',
                'portuguese': 'Portuguese',
                'arabic': 'Arabic'
            },
            fr: {
                'home-page': 'Chat',
                
                // About Us Section
                'mission-title': 'À Propos',
                'mission-text': 'Notre mission est de fournir à chaque touriste un guide numérique instantané, précis et personnalisé, vous permettant d\'explorer le Maroc en toute confiance et de vous connecter plus profondément avec sa riche culture.',

                // The Problem Section
                'journey-title': 'Redéfinir le Voyage Moderne',
                'journey-text': 'Nous comprenons que le voyage du voyageur moderne commence en ligne. Cependant, la planification peut être écrasante, avec des informations précieuses souvent fragmentées sur d\'innombrables sites web, blogs et forums. Une seule question peut générer des milliers d\'opinions contradictoires et non vérifiées, rendant difficile pour les sources officielles et faisant autorité de guider efficacement les visiteurs. <br> Ce fossé numérique crée de l\'incertitude et des frictions, de la phase de "Rêve" jusqu\'à la phase de "Partage" de votre voyage. Notre objectif est d\'éliminer ces frictions.',

                // The Solution Section
                'solution-title': 'La Solution : Un Véritable Concierge Numérique',
                'solution-text': 'Akabar est une plateforme numérique de pointe conçue pour servir de concierge 24h/24 et 7j/7 et comme source officielle unique de vérité du Maroc pour les touristes. Nous allons au-delà de simples réponses textuelles pour offrir une expérience riche et interactive :',
                'solution-li1': '<strong>Réponses Instantanées :</strong> Obtenez des réponses claires et utiles à une vaste gamme de questions, des conseils d\'étiquette culturelle aux questions pratiques sur les transports.',
                'solution-li2': '<strong>Cartes Interactives :</strong> Demandez des directions ou des recommandations et recevez des cartes dynamiques avec des emplacements épinglés pour vous aider à visualiser vos plans instantanément.',
                'solution-li3': '<strong>Culture Immersive :</strong> Découvrez le patrimoine du Maroc à travers des médias engageants, y compris des extraits jouables de musique traditionnelle comme le Gnawa.',

                // Trust & Accuracy Section
                'trust-title': 'Une Base de Confiance et de Précision',
                'trust-text': 'La caractéristique la plus importante de notre plateforme est son engagement envers la précision. Akabar est construit sur une architecture de "jardin clos" sécurisée. Cela signifie que tout son univers de connaissances est strictement limité aux sources de données officielles pré-approuvées fournies et examinées par des experts. L\'IA est architecturalement interdite d\'accéder à l\'internet ouvert pour les réponses. C\'est notre garantie que chaque réponse est fiable, combat directement la désinformation en ligne, et s\'aligne avec les plus hauts standards de l\'hospitalité de notre nation.',

                // Contact Section
                'contact-title': 'Contactez-nous',
                'contact-text': 'Nous sommes dédiés à rendre votre voyage au Maroc fluide et inoubliable. Pour toute demande concernant ce projet, veuillez nous contacter :',
                'contact-email': 'kinaamine@gmail.com',
                'english': 'Anglais',
                'french': 'Français',
                'spanish': 'Espagnol',
                'portuguese': 'Portugais',
                'arabic': 'Arabe'
            },
            es: {
                'home-page': 'Chat',
                
                // About Us Section
                'mission-title': 'Acerca de Nosotros',
                'mission-text': 'Nuestra misión es proporcionar a cada turista una guía digital instantánea, precisa y personalizada, permitiéndote explorar Marruecos con confianza y conectar más profundamente con su rica cultura.',

                // The Problem Section
                'journey-title': 'Redefiniendo el Viaje Moderno',
                'journey-text': 'Entendemos que el viaje del viajero moderno comienza en línea. Sin embargo, la planificación puede ser abrumadora, con información valiosa a menudo fragmentada en innumerables sitios web, blogs y foros. Una sola pregunta puede generar miles de opiniones contradictorias y no verificadas, haciendo difícil que las fuentes oficiales y autorizadas guíen efectivamente a los visitantes. <br> Esta brecha digital crea incertidumbre y fricción, desde la fase de "Soñar" hasta la fase de "Compartir" de tu viaje. Nuestro objetivo es eliminar esa fricción.',

                // The Solution Section
                'solution-title': 'La Solución: Un Verdadero Conserje Digital',
                'solution-text': 'Akabar es una plataforma digital de vanguardia diseñada para servir como tu conserje 24/7 y la única fuente oficial de información de Marruecos para turistas. Vamos más allá de simples respuestas de texto para ofrecer una experiencia rica e interactiva:',
                'solution-li1': '<strong>Respuestas Instantáneas:</strong> Obtén respuestas claras y útiles a una amplia gama de consultas, desde consejos de etiqueta cultural hasta preguntas prácticas sobre transporte.',
                'solution-li2': '<strong>Mapas Interactivos:</strong> Pide direcciones o recomendaciones y recibe mapas dinámicos con ubicaciones marcadas para ayudarte a visualizar tus planes al instante.',
                'solution-li3': '<strong>Cultura Inmersiva:</strong> Descubre el patrimonio de Marruecos a través de multimedia atractivo, incluyendo fragmentos reproducibles de música tradicional como el Gnawa.',

                // Trust & Accuracy Section
                'trust-title': 'Una Base de Confianza y Precisión',
                'trust-text': 'La característica más importante de nuestra plataforma es su compromiso con la precisión. Akabar está construido sobre una arquitectura de "jardín vallado" segura. Esto significa que todo su universo de conocimiento está estrictamente limitado a fuentes de datos oficiales pre-aprobadas proporcionadas y revisadas por expertos. La IA está arquitectónicamente prohibida de acceder al internet abierto para respuestas. Esta es nuestra garantía de que cada respuesta es confiable, combate directamente la desinformación en línea, y se alinea con los más altos estándares de hospitalidad de nuestra nación.',

                // Contact Section
                'contact-title': 'Contáctanos',
                'contact-text': 'Estamos dedicados a hacer tu viaje en Marruecos fluido e inolvidable. Para consultas sobre este proyecto, por favor contáctanos:',
                'contact-email': 'kinaamine@gmail.com',
                'english': 'Inglés',
                'french': 'Francés',
                'spanish': 'Español',
                'portuguese': 'Portugués',
                'arabic': 'Árabe'
            },
            pt: {
                'home-page': 'Chat',
                
                // About Us Section
                'mission-title': 'Sobre Nós',
                'mission-text': 'Nossa missão é fornecer a cada turista um guia digital instantâneo, preciso e personalizado, capacitando você a explorar o Marrocos com confiança e se conectar mais profundamente com sua rica cultura.',

                // The Problem Section
                'journey-title': 'Redefinindo a Jornada Moderna',
                'journey-text': 'Entendemos que a jornada do viajante moderno começa online. No entanto, o planejamento pode ser avassalador, com informações valiosas frequentemente fragmentadas em incontáveis sites, blogs e fóruns. Uma única pergunta pode gerar milhares de opiniões conflitantes e não verificadas, tornando difícil para fontes oficiais e autoritativas orientar os visitantes efetivamente. <br> Esta lacuna digital cria incerteza e atrito, desde a fase de "Sonhar" até a fase de "Compartilhar" da sua jornada. Nosso objetivo é eliminar esse atrito.',

                // The Solution Section
                'solution-title': 'A Solução: Um Verdadeiro Concierge Digital',
                'solution-text': 'Akabar é uma plataforma digital de última geração projetada para servir como seu concierge 24/7 e a única fonte oficial de informação do Marrocos para turistas. Vamos além de simples respostas em texto para oferecer uma experiência rica e interativa:',
                'solution-li1': '<strong>Respostas Instantâneas:</strong> Obtenha respostas claras e úteis para uma vasta gama de consultas, desde dicas de etiqueta cultural até questões práticas sobre transporte.',
                'solution-li2': '<strong>Mapas Interativos:</strong> Peça direções ou recomendações e receba mapas dinâmicos com localizações marcadas para ajudar você a visualizar seus planos instantaneamente.',
                'solution-li3': '<strong>Cultura Imersiva:</strong> Descubra o patrimônio do Marrocos através de multimídia envolvente, incluindo trechos reproduzíveis de música tradicional como Gnawa.',

                // Trust & Accuracy Section
                'trust-title': 'Uma Base de Confiança e Precisão',
                'trust-text': 'A característica mais importante da nossa plataforma é seu compromisso com a precisão. Akabar é construído sobre uma arquitetura de "jardim murado" segura. Isso significa que todo seu universo de conhecimento é estritamente limitado a fontes de dados oficiais pré-aprovadas fornecidas e revisadas por especialistas. A IA é arquiteturalmente proibida de acessar a internet aberta para respostas. Esta é nossa garantia de que cada resposta é confiável, combate diretamente a desinformação online, e se alinha com os mais altos padrões de hospitalidade da nossa nação.',

                // Contact Section
                'contact-title': 'Contate-nos',
                'contact-text': 'Estamos dedicados a tornar sua jornada no Marrocos perfeita e inesquecível. Para consultas sobre este projeto, por favor nos contate:',
                'contact-email': 'kinaamine@gmail.com',
                'english': 'Inglês',
                'french': 'Francês',
                'spanish': 'Espanhol',
                'portuguese': 'Português',
                'arabic': 'Árabe'
            },
            ar: {
                'home-page': 'المحادثة',
                
                // About Us Section
                'mission-title': 'من نحن',
                'mission-text': 'مهمتنا هي تقديم دليل رقمي فوري ودقيق وشخصي لكل سائح، مما يمكنك من استكشاف المغرب بثقة والتواصل بشكل أعمق مع ثقافته الغنية.',

                // The Problem Section
                'journey-title': 'إعادة تعريف الرحلة الحديثة',
                'journey-text': 'نحن ندرك أن رحلة المسافر الحديث تبدأ عبر الإنترنت. ومع ذلك، يمكن أن يكون التخطيط مرهقاً، حيث تكون المعلومات القيمة مجزأة في كثير من الأحيان عبر مواقع ومدونات ومنتديات لا حصر لها. يمكن أن ينتج عن سؤال واحد آلاف الآراء المتضاربة وغير المتحقق منها، مما يجعل من الصعب على المصادر الرسمية والموثوقة توجيه الزوار بفعالية. <br> هذه الفجوة الرقمية تخلق عدم يقين واحتكاك، من مرحلة "الحلم" وصولاً إلى مرحلة "المشاركة" في رحلتك. هدفنا هو القضاء على هذا الاحتكاك.',

                // The Solution Section
                'solution-title': 'الحل: مرشدك الرقمي الشخصي',
                'solution-text': 'Akabar هي منصة رقمية متطورة مصممة لتعمل كمرشد شخصي على مدار الساعة طوال أيام الأسبوع ومصدر المغرب الرسمي الوحيد للمعلومات للسياح. نذهب إلى ما هو أبعد من الإجابات النصية البسيطة لنقدم تجربة غنية وتفاعلية:',
                'solution-li1': '<strong>إجابات فورية:</strong> احصل على ردود واضحة ومفيدة لمجموعة واسعة من الاستفسارات، من نصائح آداب الثقافة إلى الأسئلة العملية حول النقل.',
                'solution-li2': '<strong>خرائط تفاعلية:</strong> اطلب الاتجاهات أو التوصيات واحصل على خرائط ديناميكية مع مواقع مثبتة لمساعدتك في تصور خططك فوراً.',
                'solution-li3': '<strong>ثقافة غامرة:</strong> اكتشف تراث المغرب من خلال الوسائط المتعددة الجذابة، بما في ذلك مقاطع قابلة للتشغيل من الموسيقى التقليدية مثل كناوة.',

                // Trust & Accuracy Section
                'trust-title': 'أساس من الثقة والدقة',
                'trust-text': ' Akabar مبني على هيكلية "حديقة مسورة" آمنة. هذا يعني أن عالم معرفتها بأكمله مقتصر بصرامة على مصادر البيانات الرسمية المعتمدة مسبقاً والمقدمة والمراجعة من قبل الخبراء. الذكاء الاصطناعي محظور معمارياً من الوصول إلى الإنترنت المفتوح للحصول على إجابات. هذا ضمان منا أن كل إجابة موثوقة، وتحارب بشكل مباشر المعلومات المضللة عبر الإنترنت، وتتماشى مع أعلى معايير ضيافة بلدنا.',

                // Contact Section
                'contact-title': 'اتصل بنا',
                'contact-text': 'نحن مكرسون لجعل رحلتك في المغرب سلسة ولا تُنسى. للاستفسارات حول هذا المشروع، يرجى الاتصال بنا:',
                'contact-email': 'kinaamine@gmail.com',
                'english': 'الإنجليزية',
                'french': 'الفرنسية',
                'spanish': 'الإسبانية',
                'portuguese': 'البرتغالية',
                'arabic': 'العربية'
            }
        };
        this.bindEvents();
    }

    applyTranslations(lang) {
        // Translate all elements with a data-translate attribute
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (this.translations[lang] && this.translations[lang][key]) {
                element.innerHTML = this.translations[lang][key];
            }
        });

        // Specifically translate the language names in the dropdown menu
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

        // Set page direction for Arabic
        document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
        localStorage.setItem('selectedLanguage', lang);
    }

    loadSavedLanguage() {
        const savedLang = localStorage.getItem('selectedLanguage') || 'en';
        this.applyTranslations(savedLang);
    }

    bindEvents() {
        const languageToggleButton = document.getElementById('language-toggle-btn');
        const languageDropdownMenu = document.getElementById('language-dropdown-menu');

        if (languageToggleButton && languageDropdownMenu) {
            languageToggleButton.addEventListener('click', (event) => {
                event.stopPropagation();
                languageDropdownMenu.classList.toggle('show');
                const isExpanded = languageDropdownMenu.classList.contains('show');
                languageToggleButton.setAttribute('aria-expanded', isExpanded);
            });

            languageDropdownMenu.querySelectorAll('[data-lang]').forEach(button => {
                button.addEventListener('click', () => {
                    const selectedLang = button.getAttribute('data-lang');
                    this.applyTranslations(selectedLang);
                    languageDropdownMenu.classList.remove('show');
                    languageToggleButton.setAttribute('aria-expanded', 'false');
                });
            });
        }

        window.addEventListener('click', (event) => {
            if (languageDropdownMenu && languageDropdownMenu.classList.contains('show')) {
                if (!languageToggleButton.contains(event.target) && !languageDropdownMenu.contains(event.target)) {
                    languageDropdownMenu.classList.remove('show');
                    languageToggleButton.setAttribute('aria-expanded', 'false');
                }
            }
        });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // --- Theme Toggle Logic ---
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    const frontPageImage = document.getElementById('front-page-image');
    const audioPlayerImage = document.getElementById('audio-player-image');
    const whiteLogo = document.getElementById('white-logo');
    const blackLogo = document.getElementById('black-logo');
    const body = document.body;
    const sunIconSrc = '/sun-o.svg';
    const moonIconSrc = '/moon-o.svg';
    const darkImageSrc = '/front_page_black.jpg';
    const lightImageSrc = '/front_page.jpg';
    const darkAudioImageSrc = '/audio-player_black.jpg';
    const lightAudioImageSrc = '/audio-player.jpg';
    

    const applyTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
            themeIcon.src = sunIconSrc;
            // Add this line to set the image on page load
            if (frontPageImage) frontPageImage.src = darkImageSrc;
            if (audioPlayerImage) audioPlayerImage.src = darkAudioImageSrc;
            blackLogo.classList.add('hidden');
            whiteLogo.classList.remove('hidden');
        } else {
            body.classList.remove('dark-mode');
            themeIcon.src = moonIconSrc;
            blackLogo.classList.remove('hidden');
            whiteLogo.classList.add('hidden');
            // Add this line to ensure the light image is set
            if (frontPageImage) frontPageImage.src = lightImageSrc;
            if (audioPlayerImage) audioPlayerImage.src = lightAudioImageSrc;
        }
    };

    const toggleTheme = () => {
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            themeIcon.src = sunIconSrc;
            blackLogo.classList.add('hidden');
            whiteLogo.classList.remove('hidden');
            // Add this line to switch to the dark image
            if (frontPageImage) frontPageImage.src = darkImageSrc;
            if (audioPlayerImage) audioPlayerImage.src = darkAudioImageSrc;

            localStorage.setItem('theme', 'dark');
        } else {
            themeIcon.src = moonIconSrc;
            // Add this line to switch back to the light image
            blackLogo.classList.remove('hidden');
            whiteLogo.classList.add('hidden');
            if (frontPageImage) frontPageImage.src = lightImageSrc;
            if (audioPlayerImage) audioPlayerImage.src = lightAudioImageSrc;
            localStorage.setItem('theme', 'light');
        }
    };

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', toggleTheme);
    }

    // Run this function when the script loads to apply the saved theme
    applyTheme();

    // --- Initialize and load translations ---
    const translationManager = new TranslationManager();
    translationManager.loadSavedLanguage();

    // --- ADDED: Language Button Text Sync ---
    // This block fixes the glitch by updating the main language button's text.
    // It assumes your main button's text is inside an element with id="selected-language-text".
    const selectedLanguageText = document.getElementById('selected-language-text');
    const languageDropdownMenu = document.getElementById('language-dropdown-menu');

    if (selectedLanguageText && languageDropdownMenu) {
        // 1. Set the initial text when the page loads
        const savedLang = localStorage.getItem('selectedLanguage') || 'en';
        const initialButton = languageDropdownMenu.querySelector(`[data-lang="${savedLang}"]`);
        if (initialButton) {
            selectedLanguageText.textContent = initialButton.textContent.trim();
        }

        // 2. Add a listener to update the text whenever a language is clicked
        languageDropdownMenu.addEventListener('click', (event) => {
            const button = event.target.closest('[data-lang]');
            if (button) {
                selectedLanguageText.textContent = button.textContent.trim();
            }
        });
    }
    // --- END OF ADDED CODE ---

    // --- Dynamic Question Card Logic ---
    const questionCards = document.querySelectorAll('.question-card');
    questionCards.forEach(card => {
        const askBtn = card.querySelector('.ask-btn');
        const titleElement = card.querySelector('h3[data-translate]');

        if (askBtn && titleElement) {
            askBtn.addEventListener('click', () => {
                const currentLang = localStorage.getItem('selectedLanguage') || 'en';
                const titleKey = titleElement.getAttribute('data-translate');
                const questionKey = `${titleKey.replace('-title', '')}-question`;

                const questionText = (translationManager.translations[currentLang] && translationManager.translations[currentLang][questionKey]) ||
                    (translationManager.translations['en'] && translationManager.translations['en'][questionKey]) ||
                    translationManager.translations[currentLang][titleKey] ||
                    translationManager.translations['en'][titleKey];

                const encodedQuestion = encodeURIComponent(questionText);
                window.location.href = `/?question=${encodedQuestion}`;
            });
        }
    });

    // --- Navigation Button Logic ---
    const navigationButton = document.querySelector('button[href]');
    if (navigationButton) {
        navigationButton.addEventListener('click', () => {
            const destination = navigationButton.getAttribute('href');
            if (destination) {
                window.location.href = destination;
            }
        });
    }
});