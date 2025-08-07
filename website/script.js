// FixMate-SA Website JavaScript

// Translations
const translations = {
    en: {
        // Navigation
        'home': 'Home',
        'features': 'Features',
        'how-it-works': 'How It Works',
        'for-fixers': 'For Fixers',
        'safety': 'Safety',
        'pricing': 'Pricing',
        'contact': 'Contact',
        'get-started': 'Get Started',
        
        // Hero Section
        'hero-title': 'South Africa\'s Premier<br><span class="highlight">Service Platform</span>',
        'hero-subtitle': 'Connect with verified, skilled professionals across South Africa for ANY service you need. From home repairs and beauty services to IT support and tutoring - find the right expert with real-time tracking, AI-powered matching, and transparent R20 pricing.',
        'verified-professionals': 'Verified Professionals',
        'real-time-tracking': 'Real-Time Tracking',
        'multi-language': 'Multi-Language Support',
        'ai-powered': 'AI-Powered Matching',
        'find-services': 'Find Services Now',
        'join-professionals': 'Join as Professional',
        'verified-professionals': 'Verified Professionals',
        'jobs-completed': 'Services Completed',
        'average-rating': 'Average Rating',
        
        // Features
        'features-title': 'Why Choose FixMate-SA?',
        'features-subtitle': 'Advanced technology meets reliable service for the perfect professional service experience',
        'smart-matching': 'Smart Matching',
        'smart-matching-desc': 'AI-powered system matches you with the perfect service professionals based on location, skills, ratings, and availability. Whether you need a plumber, hairdresser, tutor, or IT expert - no more endless searching.',
        'real-time-tracking-desc': 'Track your service professional\'s location and progress in real-time. Know exactly when they\'ll arrive and stay updated throughout your appointment - from home repairs to beauty treatments.',
        'verification-safety': 'Verification & Safety',
        'verification-safety-desc': 'All service professionals are verified with background checks, ID verification, and skill assessments. Whether it\'s a beautician, mechanic, or tutor - your safety is our priority.',
        'whatsapp-integration': 'WhatsApp Integration',
        'whatsapp-integration-desc': 'No smartphone? No problem! Request services via WhatsApp or SMS. Full conversation flow for all users.',
        'multi-language-support': 'Multi-Language Support',
        'multi-language-support-desc': 'Available in English and Afrikaans with more South African languages coming soon. Use in your preferred language.',
        'transparent-pricing': 'Transparent Pricing',
        'transparent-pricing-desc': 'Simple R20 platform fee per job. No hidden costs, no surprises. Fair pricing for quality service.',
        'ai-assistant': 'AI Assistant',
        'ai-assistant-desc': '24/7 multilingual AI assistant helps with job descriptions, price estimates, and technical guidance.',
        'dispute-resolution': 'Dispute Resolution',
        'dispute-resolution-desc': 'Fair and fast dispute resolution system ensures satisfaction for both clients and fixers.',
        'enterprise-solution': 'Enterprise Solutions',
        'enterprise-solution-desc': 'B2B portal for businesses needing multiple services. Bulk bookings, compliance management, and dedicated support.',
        
        // How It Works
        'how-it-works-title': 'How FixMate-SA Works',
        'how-it-works-subtitle': 'Simple, fast, and reliable - get any service done in 3 easy steps',
        'for-clients': 'For Clients',
        'for-professionals': 'For Professionals',
        'step1-client': 'Describe Your Service Need',
        'step1-client-desc': 'Tell us what service you need using voice recording, photos, or text. Whether it\'s plumbing, hair styling, tutoring, IT support, or any other service - our AI helps create detailed descriptions.',
        'step2-client': 'Get Matched',
        'step2-client-desc': 'Our AI instantly finds nearby verified professionals. First-come-first-serve notifications ensure quick responses from qualified service providers.',
        'step3-client': 'Track & Pay',
        'step3-client-desc': 'Track your professional\'s arrival in real-time. Pay securely after service completion with our transparent R20 platform fee - whether it\'s a haircut, computer repair, or home maintenance.',
        'step1-professional': 'Complete Verification',
        'step1-professional-desc': 'Upload ID, proof of skills, and complete background checks. Join our verified network of trusted professionals across all service categories.',
        'step2-professional': 'Receive Service Requests',
        'step2-professional-desc': 'Get notified of nearby service requests matching your skills. First-come-first-serve system ensures fair opportunities across all professions.',
        'step3-professional': 'Build Your Reputation',
        'step3-professional-desc': 'Complete services, earn ratings, and climb our gamification tiers. Higher tiers = more opportunities and better earnings, regardless of your profession.',
        
        // For Professionals
        'grow-business': 'Grow Your Service Business',
        'grow-business-desc': 'Join thousands of successful service professionals earning more with FixMate-SA\'s advanced platform - from hairdressers and tutors to mechanics and cleaners',
        'gamification-system': 'Gamification System',
        'gamification-desc': 'Earn Bronze, Silver, Gold, and Platinum tiers. Higher tiers get priority job notifications and better rates.',
        'instant-notifications': 'Instant Job Notifications',
        'notifications-desc': 'Real-time notifications for nearby jobs. First-come-first-serve system ensures fair opportunities.',
        'secure-payments': 'Secure Payments',
        'payments-desc': 'Get paid quickly and securely. Transparent payment system with dispute protection.',
        'performance-analytics': 'Performance Analytics',
        'analytics-desc': 'Track your earnings, ratings, completion rates, and optimize your business performance.',
        'support-training': 'Support & Training',
        'support-desc': 'Access learning resources, business compliance tools, and dedicated fixer support team.',
        'verified-network': 'Verified Professional Network',
        'network-desc': 'Join a trusted community of verified professionals with reputation management tools.',
        'join-now': 'Join as Professional Now',
        'avg-weekly-earnings': 'Avg. Weekly Earnings',
        'fixer-satisfaction': 'Fixer Satisfaction',
        
        // Safety
        'safety-title': 'Safety & Trust First',
        'safety-subtitle': 'Your security and satisfaction are our top priorities',
        'id-verification': 'ID Verification',
        'id-verification-desc': 'All fixers must provide valid South African ID documents and undergo thorough background checks.',
        'skill-assessment': 'Skill Assessment',
        'skill-assessment-desc': 'Comprehensive skill verification ensures fixers are qualified for the services they offer.',
        'rating-system': 'Rating System',
        'rating-system-desc': 'Transparent rating and review system helps you choose the best fixers based on real customer feedback.',
        'fraud-protection': 'AI Fraud Protection',
        'fraud-protection-desc': 'Advanced AI monitors all transactions and interactions to prevent fraud and ensure platform integrity.',
        'support-24-7': '24/7 Support',
        'support-24-7-desc': 'Round-the-clock customer support and emergency assistance whenever you need help.',
        
        // Pricing
        'pricing-title': 'Transparent Pricing',
        'pricing-subtitle': 'Simple, fair, and transparent - no hidden fees',
        'platform-fee': 'Platform Fee',
        'per-job': 'per job',
        'pricing-feature-1': 'AI-powered fixer matching',
        'pricing-feature-2': 'Real-time job tracking',
        'pricing-feature-3': 'Secure payment processing',
        'pricing-feature-4': '24/7 customer support',
        'pricing-feature-5': 'Dispute resolution service',
        'pricing-feature-6': 'Multi-language support',
        'pricing-note': 'You pay the fixer directly for their work. The R20 platform fee covers our technology, safety, and support services.',
        
        // Download
        'download-title': 'Get Started Today',
        'download-subtitle': 'Download the app or access via web browser. Available in English and Afrikaans.',
        'web-app': 'Open Web App',
        'fixer-portal': 'Fixer Portal',
        'multiple-ways': 'Multiple Ways to Access:',
        'web-browser': 'Web Browser',
        'whatsapp': 'WhatsApp',
        'sms': 'SMS/USSD',
        'voice-support': 'Voice Support',
        
        // Footer
        'footer-description': 'South Africa\'s premier service platform connecting clients with verified, reliable fixers across the country.',
        'quick-links': 'Quick Links',
        'services': 'Services',
        'plumbing': 'Plumbing',
        'electrical': 'Electrical',
        'carpentry': 'Carpentry',
        'painting': 'Painting',
        'appliance-repair': 'Appliance Repair',
        'emergency-services': 'Emergency Services',
        'support': 'Support',
        'contact-support': 'Contact Support',
        'help-center': 'Help Center',
        'terms-service': 'Terms of Service',
        'privacy-policy': 'Privacy Policy',
        'business-compliance': 'Business Compliance',
        'all-rights-reserved': 'All rights reserved.',
        'certified-secure': '🔒 Certified Secure',
        'sa-compliant': '🇿🇦 SA Compliant',
        'verified-platform': '✓ Verified Platform'
    },
    af: {
        // Navigation
        'home': 'Tuis',
        'features': 'Kenmerke',
        'how-it-works': 'Hoe Dit Werk',
        'for-fixers': 'Vir Herstellers',
        'safety': 'Veiligheid',
        'pricing': 'Pryse',
        'contact': 'Kontak',
        'get-started': 'Begin Nou',
        
        // Hero Section
        'hero-title': 'Suid-Afrika se Premier<br><span class="highlight">Diens Platform</span>',
        'hero-subtitle': 'Verbind met geverifieerde, betroubare herstellers regoor Suid-Afrika. Van loodgieterynoodeisies tot elektriese herstelwerk, vind die regte professionele persoon met intydse opsporing, KI-aangedrewe passing, en deursigtige R20 pryse.',
        'verified-fixers': 'Geverifieerde Herstellers',
        'real-time-tracking': 'Intydse Opsporing',
        'multi-language': 'Multi-taal Ondersteuning',
        'ai-powered': 'KI-aangedrewe Passing',
        'find-fixers': 'Vind Herstellers Nou',
        'join-fixers': 'Sluit Aan as Hersteller',
        'verified-professionals': 'Geverifieerde Professionele',
        'jobs-completed': 'Werk Voltooi',
        'average-rating': 'Gemiddelde Gradering',
        
        // Features
        'features-title': 'Hoekom FixMate-SA Kies?',
        'features-subtitle': 'Gevorderde tegnologie ontmoet betroubare diens vir die perfekte huis herstel ervaring',
        'smart-matching': 'Slim Passing',
        'smart-matching-desc': 'KI-aangedrewe stelsel pas jou by die mees geskikte herstellers gebaseer op ligging, vaardighede, graderings, en beskikbaarheid. Geen eindelose soektog meer nie.',
        'real-time-tracking-desc': 'Spoor jou hersteller se ligging en werk vordering in intyd. Weet presies wanneer hulle sal aankom en bly opgedateer gedurende die diens.',
        'verification-safety': 'Verifikasie & Veiligheid',
        'verification-safety-desc': 'Alle herstellers word geverifieer met agtergrond kontroles, ID verifikasie, en vaardigheids assesserings. Jou veiligheid is ons prioriteit.',
        'whatsapp-integration': 'WhatsApp Integrasie',
        'whatsapp-integration-desc': 'Geen slimfoon nie? Geen probleem! Versoek dienste via WhatsApp of SMS. Volledige gespreksvloei vir alle gebruikers.',
        'multi-language-support': 'Multi-taal Ondersteuning',
        'multi-language-support-desc': 'Beskikbaar in Engels en Afrikaans met meer Suid-Afrikaanse tale wat binnekort kom. Gebruik in jou voorkeur taal.',
        'transparent-pricing': 'Deursigtige Pryse',
        'transparent-pricing-desc': 'Eenvoudige R20 platform fooi per werk. Geen versteekte kostes, geen verrassings. Billike pryse vir kwaliteit diens.',
        'ai-assistant': 'KI Assistent',
        'ai-assistant-desc': '24/7 meertalige KI assistent help met werk beskrywings, prys beramings, en tegniese leiding.',
        'dispute-resolution': 'Geskil Oplossing',
        'dispute-resolution-desc': 'Billike en vinnige geskil oplossing stelsel verseker tevredenheid vir beide kliënte en herstellers.',
        'enterprise-solution': 'Onderneming Oplossings',
        'enterprise-solution-desc': 'B2B portaal vir besighede wat veelvuldige dienste benodig. Bulk besprekings, nakoming bestuur, en toegewyde ondersteuning.',
        
        // How It Works
        'how-it-works-title': 'Hoe FixMate-SA Werk',
        'how-it-works-subtitle': 'Eenvoudig, vinnig, en betroubaar - kry jou herstelwerk gedoen in 3 maklike stappe',
        'for-clients': 'Vir Kliënte',
        'step1-client': 'Beskryf Jou Werk',
        'step1-client-desc': 'Vertel ons wat herstel moet word deur stem opname, fotos, of teks te gebruik. Ons KI help om gedetailleerde werk beskrywings te skep.',
        'step2-client': 'Kry Gepas',
        'step2-client-desc': 'Ons KI vind onmiddellik nabygeleë geverifieerde herstellers. Eerste-kom-eerste-bedien kennisgewings verseker vinnige response.',
        'step3-client': 'Spoor & Betaal',
        'step3-client-desc': 'Spoor jou hersteller se aankoms in intyd. Betaal veilig na werk voltooiing met ons deursigtige R20 platform fooi.',
        'step1-fixer': 'Voltooi Verifikasie',
        'step1-fixer-desc': 'Laai ID op, bewys van vaardighede, en voltooi agtergrond kontroles. Sluit aan by ons geverifieerde netwerk van vertroude professionele.',
        'step2-fixer': 'Ontvang Werk Kennisgewings',
        'step2-fixer-desc': 'Kry kennis van nabygeleë werk wat jou vaardighede pas. Eerste-kom-eerste-bedien stelsel verseker billike geleenthede.',
        'step3-fixer': 'Bou Jou Reputasie',
        'step3-fixer-desc': 'Voltooi werk, verdien graderings, en klim ons gamifikasie vlakke. Hoër vlakke = meer werk geleenthede en beter verdienste.',
        
        // For Fixers
        'grow-business': 'Groei Jou Besigheid',
        'grow-business-desc': 'Sluit aan by duisende suksesvolle herstellers wat meer verdien met FixMate-SA se gevorderde platform',
        'gamification-system': 'Gamifikasie Stelsel',
        'gamification-desc': 'Verdien Brons, Silwer, Goud, en Platina vlakke. Hoër vlakke kry voorrang werk kennisgewings en beter tariewe.',
        'instant-notifications': 'Onmiddellike Werk Kennisgewings',
        'notifications-desc': 'Intydse kennisgewings vir nabygeleë werk. Eerste-kom-eerste-bedien stelsel verseker billike geleenthede.',
        'secure-payments': 'Veilige Betalings',
        'payments-desc': 'Kry betaal vinnig en veilig. Deursigtige betaling stelsel met geskil beskerming.',
        'performance-analytics': 'Prestasie Analise',
        'analytics-desc': 'Spoor jou verdienste, graderings, voltooiing tariewe, en optimaliseer jou besigheid prestasie.',
        'support-training': 'Ondersteuning & Opleiding',
        'support-desc': 'Toegang tot leer hulpbronne, besigheid nakoming tools, en toegewyde hersteller ondersteuning span.',
        'verified-network': 'Geverifieerde Professionele Netwerk',
        'network-desc': 'Sluit aan by \'n vertroude gemeenskap van geverifieerde professionele met reputasie bestuur tools.',
        'join-now': 'Sluit Nou Aan as Hersteller',
        'avg-weekly-earnings': 'Gem. Weeklikse Verdienste',
        'fixer-satisfaction': 'Hersteller Tevredenheid',
        
        // Safety
        'safety-title': 'Veiligheid & Vertroue Eerste',
        'safety-subtitle': 'Jou sekuriteit en tevredenheid is ons top prioriteite',
        'id-verification': 'ID Verifikasie',
        'id-verification-desc': 'Alle herstellers moet geldige Suid-Afrikaanse ID dokumente verskaf en deeglike agtergrond kontroles ondergaan.',
        'skill-assessment': 'Vaardigheid Assessering',
        'skill-assessment-desc': 'Omvattende vaardigheid verifikasie verseker herstellers is gekwalifiseer vir die dienste wat hulle bied.',
        'rating-system': 'Gradering Stelsel',
        'rating-system-desc': 'Deursigtige gradering en resensie stelsel help jou om die beste herstellers te kies gebaseer op werklike kliënt terugvoer.',
        'fraud-protection': 'KI Bedrog Beskerming',
        'fraud-protection-desc': 'Gevorderde KI monitor alle transaksies en interaksies om bedrog te voorkom en platform integriteit te verseker.',
        'support-24-7': '24/7 Ondersteuning',
        'support-24-7-desc': 'Rondom-die-klok kliënt ondersteuning en noodgeval bystand wanneer jy hulp nodig het.',
        
        // Pricing
        'pricing-title': 'Deursigtige Pryse',
        'pricing-subtitle': 'Eenvoudig, billik, en deursigtig - geen versteekte fooie',
        'platform-fee': 'Platform Fooi',
        'per-job': 'per werk',
        'pricing-feature-1': 'KI-aangedrewe hersteller passing',
        'pricing-feature-2': 'Intydse werk opsporing',
        'pricing-feature-3': 'Veilige betaling verwerking',
        'pricing-feature-4': '24/7 kliënt ondersteuning',
        'pricing-feature-5': 'Geskil oplossing diens',
        'pricing-feature-6': 'Multi-taal ondersteuning',
        'pricing-note': 'Jy betaal die hersteller direk vir hulle werk. Die R20 platform fooi dek ons tegnologie, veiligheid, en ondersteuning dienste.',
        
        // Download
        'download-title': 'Begin Vandag',
        'download-subtitle': 'Laai die app af of toegang via web blaaier. Beskikbaar in Engels en Afrikaans.',
        'web-app': 'Open Web App',
        'fixer-portal': 'Hersteller Portaal',
        'multiple-ways': 'Veelvuldige Maniere om Toegang te kry:',
        'web-browser': 'Web Blaaier',
        'whatsapp': 'WhatsApp',
        'sms': 'SMS/USSD',
        'voice-support': 'Stem Ondersteuning',
        
        // Footer
        'footer-description': 'Suid-Afrika se premier diens platform wat kliënte verbind met geverifieerde, betroubare herstellers regoor die land.',
        'quick-links': 'Vinnige Skakels',
        'services': 'Dienste',
        'plumbing': 'Loodgieter',
        'electrical': 'Elektries',
        'carpentry': 'Skrynwerk',
        'painting': 'Verf',
        'appliance-repair': 'Toestel Herstel',
        'emergency-services': 'Noodgeval Dienste',
        'support': 'Ondersteuning',
        'contact-support': 'Kontak Ondersteuning',
        'help-center': 'Help Sentrum',
        'terms-service': 'Diensvoorwaardes',
        'privacy-policy': 'Privaatheid Beleid',
        'business-compliance': 'Besigheid Nakoming',
        'all-rights-reserved': 'Alle regte voorbehou.',
        'certified-secure': '🔒 Gesertifiseerd Veilig',
        'sa-compliant': '🇿🇦 SA Voldoende',
        'verified-platform': '✓ Geverifieerde Platform'
    }
};

// Current language
let currentLang = 'en';

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
});

// Language functionality
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
}

function switchLanguage(lang) {
    currentLang = lang;
    currentLangSpan.textContent = lang === 'en' ? 'English' : 'Afrikaans';
    
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
}

// Navigation functionality
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
    
    // Smooth scrolling for navigation links
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
            }
        });
    });
}

// Scroll effects
function initializeScrollEffects() {
    const navbar = document.getElementById('navbar');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

// Tab switching functionality
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
            document.getElementById(targetTab + '-process').classList.add('active');
        });
    });
}

// Scroll animations
function initializeAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
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

// Scroll progress indicator
function initializeScrollProgress() {
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    });
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

// Handle form submissions (if needed)
function handleFormSubmit(form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        // Handle form submission logic here
        console.log('Form submitted:', new FormData(form));
    });
}

// Load saved language preference
window.addEventListener('load', function() {
    const savedLang = localStorage.getItem('fixmate-lang');
    if (savedLang && savedLang !== currentLang) {
        switchLanguage(savedLang);
    }
});

// Performance optimization: Lazy load images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Website error:', e.error);
    // Could send error reports to analytics service
});

// Analytics tracking (placeholder)
function trackEvent(action, category, label) {
    // Implement analytics tracking
    console.log('Track event:', { action, category, label });
}

// Export functions for external use
window.FixMateSA = {
    switchLanguage,
    trackEvent,
    currentLang: () => currentLang
};