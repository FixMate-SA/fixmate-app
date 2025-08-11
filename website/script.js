// FixMate-SA Website JavaScript - Enhanced 2025

// Enhanced Translations with 5 Languages
const translations = {
    en: {
        // Navigation
        'home': 'Home',
        'features': 'Features',
        'how-it-works': 'How It Works',
        'for-professionals': 'For Professionals',
        'safety': 'Safety',
        'pricing': 'Pricing',
        'contact': 'Contact',
        'get-started': 'Get Started',
        
        // Hero Section
        'hero-title': 'South Africa\'s Premier<br><span class="highlight">Service Platform</span>',
        'hero-subtitle': 'Connect with verified, skilled professionals across South Africa for ANY service you need. From home repairs and beauty services to IT support, tutoring, and business services - find the right expert with real-time tracking, AI-powered matching, and transparent R20 pricing.',
        'verified-professionals': '5,000+ Verified Professionals',
        'real-time-tracking': 'Real-Time Tracking',
        'multi-language': '4 SA Languages Support',
        'ai-powered': 'AI-Powered Matching',
        'find-services': 'Find Services Now',
        'join-professionals': 'Join as Professional',
        'verified-professionals-stat': 'Verified Professionals',
        'services-completed': 'Services Completed',
        'average-rating': 'Average Rating',
        'cities-covered': 'Cities Covered',
        
        // Features
        'features-title': 'Why Choose FixMate-SA?',
        'features-subtitle': 'Advanced technology meets reliable service for the perfect professional service experience across ALL service categories',
        'smart-matching': 'Smart AI Matching',
        'smart-matching-desc': 'AI-powered system matches you with the perfect service professionals based on location, skills, ratings, and availability. Whether you need a plumber, hairdresser, tutor, IT expert, or business consultant - no more endless searching.',
        'real-time-tracking-desc': 'Track your service professional\'s location and progress in real-time. Know exactly when they\'ll arrive and stay updated throughout your appointment - from home repairs to beauty treatments and business consultations.',
        'verification-safety': 'Comprehensive Verification',
        'verification-safety-desc': 'All service professionals undergo rigorous verification including background checks, ID verification, skill assessments, and customer reviews. Whether it\'s a beautician, mechanic, tutor, or business service provider - your safety is guaranteed.',
        'whatsapp-integration': 'WhatsApp Business Integration',
        'whatsapp-integration-desc': 'Request services seamlessly via WhatsApp Business API or SMS. Complete conversation flow optimized for all users, including those without smartphones.',
        'multi-language-support': '4 SA Languages Support',
        'multi-language-support-desc': 'Available in English, Afrikaans, Sepedi, isiZulu, and Xitsonga with complete 100% translation coverage. Use FixMate-SA in your preferred South African language.',
        'transparent-pricing': 'Transparent Pricing',
        'transparent-pricing-desc': 'Simple R20 platform fee per service. No hidden costs, no subscription fees, no surprises. Fair pricing structure for all service categories.',
        'ai-assistant': '24/7 AI Assistant',
        'ai-assistant-desc': 'Multilingual AI assistant available 24/7 for job descriptions, price estimates, technical guidance, and customer support in all supported languages.',
        'dispute-resolution': 'Fair Dispute Resolution',
        'dispute-resolution-desc': 'Comprehensive dispute resolution system with AI-powered mediation ensures fair outcomes for both clients and professionals across all service categories.',
        'enterprise-solution': 'Enterprise B2B Portal',
        'enterprise-solution-desc': 'Advanced B2B portal for businesses needing multiple services. Bulk bookings, business compliance management, analytics, and dedicated enterprise support.',
        
        // How It Works
        'how-it-works-title': 'How FixMate-SA Works',
        'how-it-works-subtitle': 'Simple, fast, and reliable - get any service done in 3 easy steps',
        'for-clients': 'For Clients',
        'step1-client': 'Describe Your Service Need',
        'step1-client-desc': 'Tell us what service you need using voice recording, photos, or text in any of our 5 supported languages. Whether it\'s plumbing, hair styling, tutoring, IT support, business consulting, or any other service - our AI helps create detailed descriptions.',
        'step2-client': 'Get AI-Matched with Professionals',
        'step2-client-desc': 'Our advanced AI instantly finds and matches you with nearby verified professionals based on skills, ratings, and availability. Smart notifications ensure quick responses from qualified service providers.',
        'step3-client': 'Track, Complete & Pay',
        'step3-client-desc': 'Track your professional\'s arrival in real-time with GPS tracking. After service completion, pay securely with our transparent R20 platform fee - whether it\'s a haircut, computer repair, tutoring session, or home maintenance.',
        'step1-professional': 'Complete Professional Verification',
        'step1-professional-desc': 'Upload ID, proof of skills, professional certificates, and complete comprehensive background checks. Join our verified network of trusted professionals across ALL service categories - from traditional trades to modern digital services.',
        'step2-professional': 'Receive Smart Notifications',
        'step2-professional-desc': 'Get AI-powered notifications for nearby service requests matching your skills and availability. Fair opportunity system ensures equal access to jobs across all professions and skill levels.',
        'step3-professional': 'Build Your Professional Reputation',
        'step3-professional-desc': 'Complete services, earn ratings, and advance through our gamification tiers (Bronze, Silver, Gold, Platinum). Higher tiers unlock priority notifications, better rates, and exclusive opportunities regardless of your profession.',
        
        // For Professionals
        'grow-business': 'Grow Your Service Business',
        'grow-business-desc': 'Join over 5,000 successful service professionals earning more with FixMate-SA\'s advanced platform - from hairdressers and tutors to mechanics, IT experts, and business consultants',
        'gamification-system': 'Advanced Gamification System',
        'gamification-desc': 'Earn Bronze, Silver, Gold, and Platinum tiers through performance metrics. Higher tiers receive priority job notifications, better commission rates, and exclusive high-value opportunities.',
        'instant-notifications': 'Smart Job Notifications',
        'notifications-desc': 'AI-powered real-time notifications for nearby jobs matching your skills. Fair opportunity algorithm ensures equitable job distribution across all professionals.',
        'secure-payments': 'Secure Payment System',
        'payments-desc': 'Get paid quickly and securely with multiple payment options. Transparent payment processing with comprehensive dispute protection and earnings analytics.',
        'performance-analytics': 'Performance Analytics Dashboard',
        'analytics-desc': 'Track earnings, ratings, completion rates, customer feedback, and business growth metrics. Advanced analytics to optimize your professional performance.',
        'support-training': 'Professional Development & Support',
        'support-desc': 'Access learning academy, business compliance tools, professional certifications, and dedicated support team available in multiple languages.',
        'verified-network': 'Elite Professional Network',
        'network-desc': 'Join an exclusive community of verified professionals with networking opportunities, reputation management tools, and peer-to-peer learning resources.',
        'join-now': 'Join as Professional Now',
        'avg-weekly-earnings': 'Avg. Weekly Earnings',
        'professional-satisfaction': 'Professional Satisfaction',
        'retention-rate': 'Professional Retention Rate',
        
        // Safety
        'safety-title': 'Safety & Trust First',
        'safety-subtitle': 'Your security and satisfaction are our absolute top priorities across all service categories',
        'id-verification': 'Comprehensive ID Verification',
        'id-verification-desc': 'All professionals must provide valid South African ID documents, proof of residence, and undergo thorough background checks through verified third-party services.',
        'skill-assessment': 'Professional Skill Assessment',
        'skill-assessment-desc': 'Comprehensive skill verification through testing, portfolio review, and practical assessments ensures all professionals are qualified for their registered services.',
        'rating-system': 'Advanced Rating System',
        'rating-system-desc': 'Multi-dimensional rating system with verified customer reviews, photo evidence, and AI-powered fraud detection ensures authentic feedback.',
        'fraud-protection': 'AI-Powered Fraud Protection',
        'fraud-protection-desc': 'Advanced machine learning algorithms monitor all transactions, communications, and user behavior to prevent fraud and ensure platform integrity.',
        'support-24-7': '24/7 Multilingual Support',
        'support-24-7-desc': 'Round-the-clock customer support available in English, Afrikaans, Sepedi, isiZulu, and Xitsonga with emergency assistance protocols.',
        
        // Pricing
        'pricing-title': 'Transparent Pricing',
        'pricing-subtitle': 'Simple, fair, and transparent - no hidden fees, no subscription costs',
        'platform-fee': 'Platform Service Fee',
        'per-job': 'per service',
        'pricing-tagline': 'For unlimited access to all platform features',
        'pricing-feature-1': 'AI-powered professional matching',
        'pricing-feature-2': 'Real-time GPS tracking & updates',
        'pricing-feature-3': 'Secure payment processing',
        'pricing-feature-4': '24/7 multilingual customer support',
        'pricing-feature-5': 'Professional dispute resolution service',
        'pricing-feature-6': 'Complete 4-language support system',
        'pricing-feature-7': 'Business compliance & enterprise tools',
        'pricing-feature-8': 'WhatsApp Business API integration',
        'pricing-note': 'You pay professionals directly for their services. The R20 platform fee covers our advanced technology, comprehensive safety measures, and professional support services.',
        
        // Download
        'download-title': 'Get Started Today',
        'download-subtitle': 'Access via web browser or mobile-optimized interface. Available in English, Afrikaans, Sepedi, isiZulu, and Xitsonga.',
        'web-app': 'Open Web App',
        'professional-portal': 'Professional Portal',
        'multiple-ways': 'Multiple Ways to Access:',
        'web-browser': 'Web Browser',
        'whatsapp': 'WhatsApp Business',
        'sms': 'SMS/USSD',
        'voice-support': 'Voice Assistant',
        
        // Footer
        'footer-description': 'South Africa\'s premier service platform connecting clients with verified, skilled professionals across ALL service categories - from home repair and beauty services to education, technology support, and business consulting.',
        'quick-links': 'Quick Links',
        'services': 'Professional Services',
        'home-repair': 'Home Repair & Maintenance',
        'beauty-wellness': 'Beauty & Wellness Services',
        'education-tutoring': 'Education & Tutoring',
        'it-tech-support': 'IT & Technology Support',
        'cleaning-services': 'Cleaning & Domestic Services',
        'automotive-services': 'Automotive Services',
        'health-fitness': 'Health & Fitness Coaching',
        'business-services': 'Business & Consulting Services',
        'creative-services': 'Creative & Design Services',
        'emergency-services': 'Emergency & Urgent Services',
        'and-much-more': '...and much more!',
        'support': 'Support & Legal',
        'contact-support': 'Contact Support',
        'help-center': 'Help Center',
        'terms-service': 'Terms of Service',
        'privacy-policy': 'Privacy Policy',
        'business-compliance': 'Business Compliance',
        'contact': 'Contact Us',
        'all-rights-reserved': 'All rights reserved.',
        'certified-secure': '🔒 Enterprise Security Certified',
        'sa-compliant': '🇿🇦 SA Labor Law Compliant',
        'verified-platform': '✓ ISO Verified Platform'
    },
    af: {
        // Navigation
        'home': 'Tuis',
        'features': 'Kenmerke',
        'how-it-works': 'Hoe Dit Werk',
        'for-professionals': 'Vir Professionele',
        'safety': 'Veiligheid',
        'pricing': 'Pryse',
        'contact': 'Kontak',
        'get-started': 'Begin Nou',
        
        // Hero Section
        'hero-title': 'Suid-Afrika se Premier<br><span class="highlight">Diens Platform</span>',
        'hero-subtitle': 'Verbind met geverifieerde, bekwame professionele persone regoor Suid-Afrika vir ENIGE diens wat jy nodig het. Van huis herstelwerk en skoonheids dienste tot IT ondersteuning, onderrig, en besigheidsdienste - vind die regte kundige met intydse opsporing, KI-aangedrewe passing, en deursigtige R20 pryse.',
        'verified-professionals': '5,000+ Geverifieerde Professionele',
        'real-time-tracking': 'Intydse Opsporing',
        'multi-language': '4 SA Tale Ondersteuning',
        'ai-powered': 'KI-aangedrewe Passing',
        'find-services': 'Vind Dienste Nou',
        'join-professionals': 'Sluit Aan as Professionele',
        'verified-professionals-stat': 'Geverifieerde Professionele',
        'services-completed': 'Dienste Voltooi',
        'average-rating': 'Gemiddelde Gradering',
        'cities-covered': 'Stede Gedek',
        
        'features-title': 'Hoekom FixMate-SA Kies?',
        'features-subtitle': 'Gevorderde tegnologie ontmoet betroubare diens vir die perfekte professionele diens ervaring regoor ALLE diens kategorieë',
        'grow-business': 'Groei Jou Diensbusiness',
        'pricing-title': 'Deursigtige Pryse',
        'safety-title': 'Veiligheid & Vertroue Eerste',
        'download-title': 'Begin Vandag',
        'footer-description': 'Suid-Afrika se premier diens platform wat kliënte verbind met geverifieerde, bekwame professionele regoor ALLE diens kategorieë.'
    },
    nso: {
        // Navigation
        'home': 'Gae',
        'features': 'Dikarolo',
        'how-it-works': 'Kamoo e Šomago',
        'for-professionals': 'Bakgoni',
        'safety': 'Polokego',
        'pricing': 'Ditheko',
        'contact': 'Ikgokaganye',
        'get-started': 'Thoma Bjale',
        
        // Hero Section  
        'hero-title': 'Sethala sa Pele sa<br><span class="highlight">Ditšhomišo Afrika Borwa</span>',
        'hero-subtitle': 'Kgokagane le bakgoni ba ba netefaditšwego, ba ba nago le bokgoni go ralala Afrika Borwa bakeng sa ENGE tšhomišo yeo o e nyakago. Go tloga go tokofatšo ya ka gae le ditšhomišo tša bohlokwa go ya go thekgo ya IT, thuto, le ditšhomišo tša kgwebo - hwetša mokgoni yo o nepagetšego ka go latela ka nako ya nnete, go swanišanya ga AI, le ditheko tše di pepeneneng tša R20.',
        'verified-professionals': '5,000+ Bakgoni ba ba Netefaditšwego',
        'real-time-tracking': 'Go Latela ka Nako ya Nnete',
        'multi-language': 'Thekgo ya Maleme a 4 a SA',
        'ai-powered': 'Go Swanišanya ga AI',
        'find-services': 'Hwetša Ditšhomišo Bjale',
        'join-professionals': 'Kena Bjalo ka Mokgoni',
        
        'features-title': 'Lebaka la go Kgetha FixMate-SA?',
        'features-subtitle': 'Theknolotši ye e tšwetšego pele e kopana le tšhomišo ye e ka tšeponego bakeng sa maitemogelo a makgonthe a ditšhomišo go ralala dikgoro ka moka tša ditšhomišo',
        'grow-business': 'Godiša Kgwebo ya gago ya Ditšhomišo',
        'pricing-title': 'Ditheko tše di Pepeneneng',
        'safety-title': 'Polokego & Go Tšepa Pele',
        'download-title': 'Thoma Lehono',
        'footer-description': 'Sethala sa pele sa ditšhomišo sa Afrika Borwa seo se kgokaganyago bareki le bakgoni ba ba netefaditšwego, ba ba nago le bokgoni go ralala dikgoro ka moka tša ditšhomišo.'
    },
    zu: {
        // Navigation
        'home': 'Ikhaya',
        'features': 'Izici',
        'how-it-works': 'Indlela Kusebenza Ngayo',
        'for-professionals': 'Ochwepheshe',
        'safety': 'Ukuphepha',
        'pricing': 'Amanani',
        'contact': 'Xhumana',
        'get-started': 'Qala Manje',
        
        // Hero Section
        'hero-title': 'Inkundla Yesevisi<br><span class="highlight">Ehamba Phambili eNingizimu Afrika</span>',
        'hero-subtitle': 'Xhumana nochwepheshe abaqinisekisiwe, abanamakhono kulo lonke iNingizimu Afrika kunoma yisiphi isevisi oyidingayo. Kusuka ekulungiseni amakhaya nezinsizakalo zobuhle kuya ekusekeni kwe-IT, ukufundisa, nezinsizakalo zebhizinisi - thola uchwepheshe olungile ngokulandelwa kwesikhathi sangempela, ukufanisa kwe-AI, nentengo ecacile ye-R20.',
        'verified-professionals': '5,000+ Ochwepheshe Abaqinisekisiwe',
        'real-time-tracking': 'Ukulandelela Kwesikhathi Sangempela',
        'multi-language': 'Ukusekela Izilimi ze-SA ezi-4',
        'ai-powered': 'Ukufanisa Okunamandla kwe-AI',
        'find-services': 'Thola Izinsizakalo Manje',
        'join-professionals': 'Joyina njengoChwepheshe',
        
        'features-title': 'Kungani Ukhethe i-FixMate-SA?',
        'features-subtitle': 'Ubuchwepheshe obuphakeme buhlangana nesevisi ethembekile ukuze kutholakale okuhle kakhulu kwezinsizakalo zobuchwepheshe kuzo zonke izingxenye zezinsizakalo',
        'grow-business': 'Khulisa Ibhizinisi Lakho Lezinsizakalo',
        'pricing-title': 'Amanani Acacile',
        'safety-title': 'Ukuphepha Nokuthembeka Kuqala',
        'download-title': 'Qala Namuhla',
        'footer-description': 'Inkundla yezinsizakalo ehamba phambili yaseNingizimu Afrika exhuma amakhasimende nochwepheshe abaqinisekisiwe, abanamakhono kuzo zonke izingxenye zezinsizakalo.'
    },
    ts: {
        // Navigation
        'home': 'Kaya',
        'features': 'Swiandlakarhi',
        'how-it-works': 'Ndlela leyi Swi Tirhaka ha Yona',
        'for-professionals': 'Vativi',
        'safety': 'Vuhlayiseki',
        'pricing': 'Mitsengo',
        'contact': 'Vulavula',
        'get-started': 'Sungula Sweswi',
        
        // Hero Section
        'hero-title': 'Xifunengeto xa Vukorhokeri<br><span class="highlight">xo Sungula xa Afrika Dzonga</span>',
        'hero-subtitle': 'Hlanganisa na vativi lava tiyisisiweke, lava nga na vuswikoti eka Afrika Dzonga hinkwayo eka vukorhokeri BIHI lebyi u nga byi lavaka. Ku suka eka ku lulamisa ka le kaya na vukorhokeri bya rihlampfu ku ya eka nseketelo wa IT, dyondzo, na vukorhokeri bya bindzu - kuma mutivi loyi a faneleke hi ku landzelerisa hi nkarhi wa xiviri, ku ringanisa ka AI, na mitsengo ya R20 leyi nga erivaleni.',
        'verified-professionals': '5,000+ Vativi lava Tiyisisiweke',
        'real-time-tracking': 'Ku Landzelerisa hi Nkarhi wa Xiviri',
        'multi-language': 'Nseketelo wa Tindzimi ta SA ta 4',
        'ai-powered': 'Ku Ringanisa loku Namaka ka AI',
        'find-services': 'Kuma Vukorhokeri Sweswi',
        'join-professionals': 'Nghena tanihi Mutivi',
        
        'features-title': 'Hikwalaho ka yini u Hlawula FixMate-SA?',
        'features-subtitle': 'Theknoloji yo andziša yi hlangana ni vukorhokeri lebyi tshembekaka ku endla leswaku ku va ni ntokoto wo saseka wa vukorhokeri bya vativi eka swiyenge hinkwaswo swa vukorhokeri',
        'grow-business': 'Andza Bindzu ra Wena ra Vukorhokeri',
        'pricing-title': 'Mitsengo leyi nga Erivaleni',
        'safety-title': 'Vuhlayiseki na Ku tshemba Ku Sungula',
        'download-title': 'Sungula Namuntlha',
        'footer-description': 'Xifunengeto xa vukorhokeri xo sungula xa Afrika Dzonga lexi hlanganisaka vaaki na vativi lava tiyisisiweke, lava nga na vuswikoti eka swiyenge hinkwaswo swa vukorhokeri.'
    }
};

// Current language - now supports 5 languages
let currentLang = 'en';

// Language options mapping
const languageOptions = {
    'en': 'English',
    'af': 'Afrikaans', 
    'nso': 'Sepedi',
    'zu': 'isiZulu',
    'ts': 'Xitsonga'
};

// DOM elements
const langToggle = document.getElementById('lang-toggle');
const langDropdown = document.getElementById('lang-dropdown');
const currentLangSpan = document.getElementById('current-lang');
const navToggle = document.getElementById('nav-toggle');
const navMenu = document.getElementById('nav-menu');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeLanguage();
    initializeNavigation();
    initializeScrollEffects();
    initializeTabSwitching();
    initializeAnimations();
    initializeScrollProgress();
    initializeEnhancedFeatures();
});

// Enhanced language functionality
function initializeLanguage() {
    // Language toggle
    langToggle.addEventListener('click', function() {
        langDropdown.classList.toggle('show');
    });
    
    // Language options
    document.querySelectorAll('.lang-option').forEach(option => {
        option.addEventListener('click', function() {
            const lang = this.dataset.lang;
            switchLanguage(lang);
            langDropdown.classList.remove('show');
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!langToggle.contains(e.target)) {
            langDropdown.classList.remove('show');
        }
    });
    
    // Load saved language preference
    const savedLang = localStorage.getItem('fixmate-lang');
    if (savedLang && languageOptions[savedLang]) {
        switchLanguage(savedLang);
    }
}

function switchLanguage(lang) {
    if (!languageOptions[lang]) return;
    
    currentLang = lang;
    currentLangSpan.textContent = languageOptions[lang];
    
    // Update all translatable elements
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            if (element.innerHTML.includes('<')) {
                element.innerHTML = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
    
    // Store language preference
    localStorage.setItem('fixmate-lang', lang);
    
    // Track language switch event
    trackEvent('language_switch', 'user_interaction', lang);
}

// Enhanced Navigation functionality
function initializeNavigation() {
    // Mobile menu toggle
    navToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
    });
    
    // Close mobile menu when clicking nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            navMenu.classList.remove('active');
            navToggle.querySelector('i').classList.add('fa-bars');
            navToggle.querySelector('i').classList.remove('fa-times');
        });
    });
    
    // Enhanced smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offsetTop = target.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // Track navigation click
                trackEvent('navigation_click', 'user_interaction', this.getAttribute('href'));
            }
        });
    });
}

// Enhanced scroll effects
function initializeScrollEffects() {
    const navbar = document.getElementById('navbar');
    let ticking = false;
    
    function updateNavbar() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    });
}

// Enhanced tab switching functionality
function initializeTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.process-tab');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Remove active class from all buttons and tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Add active class to clicked button and corresponding tab
            this.classList.add('active');
            const targetTabId = targetTab + '-process';
            const targetElement = document.getElementById(targetTabId);
            if (targetElement) {
                targetElement.classList.add('active');
            }
            
            // Track tab switch
            trackEvent('tab_switch', 'user_interaction', targetTab);
        });
    });
}

// Enhanced scroll animations
function initializeAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '-10% 0px -10% 0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.feature-card, .safety-feature, .step, .benefit').forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
    
    // Specific animations for different sections
    document.querySelectorAll('.hero-text').forEach(el => {
        el.classList.add('slide-in-left');
        observer.observe(el);
    });
    
    document.querySelectorAll('.hero-image, .fixers-image').forEach(el => {
        el.classList.add('slide-in-right');
        observer.observe(el);
    });
}

// Enhanced scroll progress indicator
function initializeScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);
    
    let ticking = false;
    
    function updateProgress() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateProgress);
            ticking = true;
        }
    });
}

// New enhanced features
function initializeEnhancedFeatures() {
    // Initialize lazy loading for images
    initializeLazyLoading();
    
    // Initialize form interactions
    initializeFormInteractions();
    
    // Initialize CTA button tracking
    initializeCTATracking();
    
    // Initialize performance monitoring
    initializePerformanceMonitoring();
}

// Performance optimization: Enhanced lazy loading
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Enhanced form interactions
function initializeFormInteractions() {
    // Handle newsletter signup (if added)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Handle form submission logic here
            console.log('Form submitted:', new FormData(form));
            trackEvent('form_submit', 'user_interaction', form.id || 'unknown_form');
        });
    });
}

// CTA button tracking
function initializeCTATracking() {
    const ctaButtons = document.querySelectorAll('.btn-primary, .btn-secondary');
    ctaButtons.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.textContent.trim();
            const href = this.href || 'no_href';
            trackEvent('cta_click', 'user_interaction', action + '|' + href);
        });
    });
}

// Performance monitoring
function initializePerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', function() {
        if ('performance' in window) {
            const navigation = performance.getEntriesByType('navigation')[0];
            const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
            console.log('Page load time:', loadTime + 'ms');
            
            // Track performance metrics
            trackEvent('performance', 'page_load_time', Math.round(loadTime));
        }
    });
    
    // Monitor scroll performance
    let scrollCount = 0;
    window.addEventListener('scroll', debounce(function() {
        scrollCount++;
        if (scrollCount % 10 === 0) {
            trackEvent('engagement', 'scroll_depth', scrollCount * 10);
        }
    }, 100));
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Enhanced error handling
window.addEventListener('error', function(e) {
    console.error('Website error:', e.error);
    trackEvent('error', 'javascript_error', e.message || 'unknown_error');
});

// Enhanced analytics tracking
function trackEvent(action, category, label) {
    // Enhanced analytics tracking with more context
    const eventData = {
        action: action,
        category: category,
        label: label,
        language: currentLang,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent
    };
    
    console.log('Track event:', eventData);
    
    // Here you would send to your analytics service
    // Example: gtag('event', action, { event_category: category, event_label: label });
}

// Enhanced accessibility features
function initializeAccessibility() {
    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });
    
    document.addEventListener('mousedown', function() {
        document.body.classList.remove('keyboard-navigation');
    });
    
    // High contrast mode detection
    if (window.matchMedia('(prefers-contrast: high)').matches) {
        document.body.classList.add('high-contrast');
    }
    
    // Reduced motion detection
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.body.classList.add('reduced-motion');
    }
}

// Export functions for external use
window.FixMateSA = {
    switchLanguage,
    trackEvent,
    currentLang: () => currentLang,
    translations: translations,
    languageOptions: languageOptions
};

// Initialize accessibility features
document.addEventListener('DOMContentLoaded', initializeAccessibility);

// Service worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('ServiceWorker registration failed: ', registrationError);
            });
    });
}