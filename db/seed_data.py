"""Contenu initial du portfolio d'Alhassane Barry, inséré au premier démarrage dans une base vide.

Chaque section est validée par son schéma Pydantic lors de l'initialisation.
"""

from schemas.sections import SectionKey

SECTIONS: dict[SectionKey, dict] = {
    SectionKey.SITE: {
        "first_name": "Alhassane",
        "last_name": "Barry",
        "tagline": "Développeur Full-stack",
        "location": "Timbi Madina",
        "phone": "+224 626 01 45 52",
        "email": "barryalhassane476@gmail.com",
        "whatsapp_number": "224626014552",
        "senegal_location": "Dakar, Guédiawaye",
        "senegal_phone": "+221 77 487 40 73",
        "senegal_whatsapp_number": "221774874073",
        "footer_description": (
            "Ingénieur informatique passionné par le développement web et mobile. "
            "Créateur de solutions innovantes et performantes."
        ),
        "footer_tagline": "Développé avec passion",
    },
    SectionKey.THEME: {
        "accent_color": "#f59e0b",
        "default_mode": "light",
        "heading_font": "Inter",
        "body_font": "Inter",
    },
    SectionKey.HERO: {
        "layout": "classic",
        "greeting": "Bonjour, je suis",
        "first_name": "Alhassane",
        "last_name": "Barry",
        "role": "Développeur Full-stack",
        "description": (
            "Passionné par le développement web et mobile, je transforme vos idées en solutions numériques "
            "performantes. Spécialisé en React, TypeScript et architectures modernes."
        ),
        "image": "barry.png",
        "image_alt": "Alhassane Barry",
        "cta_label": "Découvrir mes projets",
        "cta_href": "#projets",
        "availability_badge": "Disponible pour nouveaux projets",
        "tech_logos": [
            "github",
            "docker",
            "django",
            "laravel",
            "react",
            "tailwindcss",
            "nestjs",
            "postgresql",
        ],
    },
    SectionKey.ABOUT: {
        "eyebrow": "À propos",
        "title": "Créateur de solutions digitales innovantes",
        "image": "barry.jpeg",
        "image_alt": "Alhassane Barry",
        "paragraphs": [
            (
                "Développeur full-stack. Je me spécialise dans la création d'applications performantes, "
                "scalables et centrées sur l'utilisateur. Mon approche combine expertise technique et "
                "compréhension des besoins métier pour livrer des solutions qui font la différence."
            ),
            (
                "Passionné par les technologies modernes, je reste constamment à jour avec les dernières "
                "tendances et meilleures pratiques du développement logiciel."
            ),
        ],
        "cta_label": "Prendre contact",
        "cta_href": "#contact",
    },
    SectionKey.SERVICES: {
        "eyebrow": "Services",
        "title": "Ce que je peux faire pour vous",
        "description": "Des solutions sur mesure pour transformer vos idées en réalité digitale",
    },
    SectionKey.SKILLS: {
        "eyebrow": "Compétences",
        "title": "Technologies maîtrisées",
        "description": "Un éventail de compétences pour répondre à tous vos besoins",
    },
    SectionKey.STATS: {
        "eyebrow": "Réalisations",
        "title": "En quelques chiffres",
        "items": [
            {
                "value": 10,
                "suffix": "+",
                "label": "Projets réalisés",
                "icon": "projects",
                "color": "from-blue-500 to-blue-600",
            },
            {
                "value": 10,
                "suffix": "+",
                "label": "Clients satisfaits",
                "icon": "users",
                "color": "from-green-500 to-green-600",
            },
            {
                "value": 2,
                "suffix": "+",
                "label": "Années d'expérience",
                "icon": "award",
                "color": "from-amber-500 to-amber-600",
            },
        ],
    },
    SectionKey.PARCOURS: {
        "eyebrow": "Expérience",
        "title": "Mon parcours professionnel",
        "description": "Des années d'expérience au service de l'innovation",
    },
    SectionKey.FORMATION: {
        "eyebrow": "Formation",
        "title": "Parcours académique",
        "description": "Une formation solide pour une expertise reconnue",
    },
    SectionKey.PROCESS: {
        "eyebrow": "Processus",
        "title": "Comment je travaille",
        "description": "Une méthodologie éprouvée pour transformer vos idées en succès",
        "steps": [
            {
                "number": "01",
                "title": "Analyse & Conception",
                "description": (
                    "Je commence par comprendre vos besoins, analyser votre marché et concevoir "
                    "une solution adaptée."
                ),
                "icon": "search",
            },
            {
                "number": "02",
                "title": "Planification",
                "description": (
                    "Élaboration d'un plan détaillé avec des jalons clairs et un calendrier réaliste "
                    "pour le projet."
                ),
                "icon": "lightbulb",
            },
            {
                "number": "03",
                "title": "Développement",
                "description": (
                    "Création de la solution avec un code propre, maintenable et suivant les "
                    "meilleures pratiques."
                ),
                "icon": "code",
            },
            {
                "number": "04",
                "title": "Tests & Déploiement",
                "description": (
                    "Tests approfondis, optimisation des performances et déploiement sur les "
                    "plateformes cibles."
                ),
                "icon": "rocket",
            },
            {
                "number": "05",
                "title": "Support & Maintenance",
                "description": (
                    "Accompagnement continu, maintenance et améliorations pour garantir la pérennité "
                    "de votre projet."
                ),
                "icon": "check",
            },
        ],
    },
    SectionKey.PROJECTS: {
        "eyebrow": "Portfolio",
        "title": "Mes réalisations",
        "description": "Des projets qui témoignent de mon expertise et de ma créativité",
    },
    SectionKey.TESTIMONIALS: {
        "eyebrow": "Témoignages",
        "title": "Ce que disent mes clients",
        "description": "La satisfaction client au cœur de mon approche",
    },
    SectionKey.CONTACT: {
        "eyebrow": "Contact",
        "title": "Travaillons ensemble",
        "description": "Discutons de votre projet et créons quelque chose d'extraordinaire",
        "email": "barryalhassane476@gmail.com",
        "phone": "+224 626 01 45 52",
        "location": "Timbi Madina",
        "cta_label": "Envoyer le message",
    },
    SectionKey.CTA: {
        "title": "Prêt à démarrer votre projet ?",
        "highlight_word": "projet",
        "description": "Discutons de votre projet et créons ensemble quelque chose d'extraordinaire",
        "primary_cta_label": "Me contacter",
        "primary_cta_href": "#contact",
        "secondary_cta_label": "Appeler maintenant",
        "secondary_cta_href": "tel:+224626014552",
        "footnote": "Réponse garantie sous 24h • Consultation gratuite • Devis sans engagement",
    },
}

SERVICES: list[dict] = [
    {
        "title": "Développement Web",
        "description": "Applications web modernes et responsives avec React, Next.js et TypeScript",
        "icon": "web",
    },
    {
        "title": "Développement Mobile",
        "description": "Applications natives et cross-platform avec React Native et Flutter",
        "icon": "mobile",
    },
    {
        "title": "Architecture & API",
        "description": "Conception d'architectures scalables et développement d'APIs RESTful",
        "icon": "api",
    },
    {
        "title": "Consulting Tech",
        "description": "Accompagnement stratégique et optimisation de vos projets numériques",
        "icon": "consulting",
    },
]

SKILL_CATEGORIES: list[dict] = [
    {
        "name": "Frontend",
        "icon": "code",
        "skills": [
            {"name": "React", "level": 95},
            {"name": "TypeScript", "level": 90},
            {"name": "Tailwind CSS", "level": 92},
            {"name": "HTML | CSS", "level": 95},
        ],
    },
    {
        "name": "Backend",
        "icon": "database",
        "skills": [
            {"name": "Express", "level": 30},
            {"name": "NestJS", "level": 85},
            {"name": "MySQL", "level": 82},
            {"name": "Django + DRF", "level": 50},
            {"name": "REST API", "level": 93},
            {"name": "PHP", "level": 70},
        ],
    },
    {
        "name": "Mobile",
        "icon": "mobile",
        "skills": [
            {"name": "React Native", "level": 87},
            {"name": "Flutter", "level": 75},
        ],
    },
    {
        "name": "Cloud & DevOps",
        "icon": "cloud",
        "skills": [
            {"name": "Docker", "level": 85},
            {"name": "Git et GitHub", "level": 95},
        ],
    },
    {
        "name": "Outils",
        "icon": "tools",
        "skills": [
            {"name": "Figma", "level": 88},
            {"name": "VS Code", "level": 95},
            {"name": "Postman", "level": 90},
            {"name": "Trello", "level": 80},
            {"name": "VMware Workstation", "level": 80},
            {"name": "Photoshop", "level": 60},
            {"name": "Illustrator", "level": 60},
        ],
    },
]

EXPERIENCES: list[dict] = [
    {
        "title": "Stagiaire maintenance et développement web",
        "company": "Tout en Génie Informatique (TGI)",
        "period": "Mars 2024 - Avril 2024",
        "description": (
            "Développement d'applications avec HTML, CSS, JavaScript et WordPress. "
            "Programmation et maintenance du matériel informatique."
        ),
        "technologies": ["HTML", "CSS", "JavaScript", "WordPress"],
    },
    {
        "title": "Stagiaire en réseau informatique et multimédia",
        "company": "Tout en Génie Informatique (TGI)",
        "period": "Mai 2025 - Juin 2025",
        "description": (
            "Mise en place de serveur DHCP, Windows Server, et déploiement d'un réseau d'entreprise."
        ),
        "technologies": ["Rufus", "DHCP", "VMware Workstation 17"],
    },
    {
        "title": "Stagiaire en développement full-stack",
        "company": "Aiglix Lab",
        "period": "Février 2026 - Juin 2026",
        "description": (
            "Conception et développement d'une application intelligente de suivi et d'optimisation "
            "de la consommation électrique basée sur l'Internet des Objets (IoT) : cas d'EcoSystem."
        ),
        "technologies": ["React Native", "Django", "IoT", "MQTT"],
    },
]

EDUCATIONS: list[dict] = [
    {
        "degree": "Licence en Génie Informatique (en cours)",
        "institution": "Univers Professionnel de Dakar (Unipro)",
        "period": "2024 - 2026",
        "description": (
            "Formation complète en informatique avec focus sur la programmation, "
            "les systèmes d'information et les réseaux informatiques."
        ),
        "achievements": ["Mention Excellente"],
    },
    {
        "degree": "Baccalauréat Scientifique",
        "institution": "Groupe Scolaire Tely Diallo",
        "period": "2022 - 2023",
        "description": "Baccalauréat scientifique en Sciences expérimentales.",
        "achievements": ["Mention Assez Bien"],
    },
]

PROJECTS: list[dict] = [
    {
        "slug": "application-immobilier",
        "title": "Application Immobilier",
        "description": (
            "Application web pour la gestion d'une agence immobilière avec accès locataires "
            "pour paiement en ligne et suivi des factures."
        ),
        "main_image": "classiqueImmo/banner.jpeg",
        "images": [
            "classiqueImmo/1.jpeg",
            "classiqueImmo/2.jpeg",
        ],
        "type": "web",
        "category": "Web Development",
        "technologies": ["PHP", "MySQL", "TailwindCSS", "Prometheus", "Grafana"],
        "live_url": None,
        "demo_url": None,
        "github_url": None,
    },
    {
        "slug": "leydi-agriculteurs-consommateurs",
        "title": "Application mise en relation agriculteurs consommateurs",
        "description": (
            "Application pour optimiser les rendements agricoles en Guinée, gestion des parcelles, "
            "transport, stockage et conseils experts."
        ),
        "main_image": "leydi/realisation-1 cpie.png",
        "images": [
            "leydi/ba.png",
            "leydi/Sans titre-1-Récupéré.png",
            "leydi/c.png",
        ],
        "type": "mobile",
        "category": "Mobile Application",
        "technologies": ["Django", "React Native", "PostgreSQL"],
        "live_url": None,
        "demo_url": None,
        "github_url": None,
    },
    {
        "slug": "plateforme-web-de-revision",
        "title": "Plateforme web de révision",
        "description": (
            "Application web pour faciliter la révision des élèves avec des exercices, corrigés "
            "et anciens sujets d'examen (bac, brevet et entrée en 7ème)."
        ),
        "main_image": "Tely/image.png",
        "images": [
            "Tely/im1.png",
            "Tely/im2.png",
        ],
        "type": "web",
        "category": "Web Development",
        "technologies": ["React", "NestJS", "PostgreSQL", "TypeScript", "TailwindCSS"],
        "live_url": None,
        "demo_url": None,
        "github_url": None,
    },
    {
        "slug": "gestion-de-bibliotheque-desktop",
        "title": "Application Desktop Gestion de Bibliothèque",
        "description": (
            "Logiciel desktop pour gérer les livres, emprunts, retours et membres d'une bibliothèque."
        ),
        "main_image": "afrilib/banner.png",
        "images": [
            "afrilib/1.png",
            "afrilib/2.png",
        ],
        "type": "desktop",
        "category": "Desktop Application",
        "technologies": ["Java", "JavaSwing", "MySQL"],
        "live_url": None,
        "demo_url": None,
        "github_url": None,
    },
    {
        "slug": "guesthub-reservation-restaurant-hotel",
        "title": "Application Mobile Réservation Restaurant & Hôtel",
        "description": (
            "Application mobile pour réserver des restaurants et hôtels avec paiement en ligne."
        ),
        "main_image": "guesthub/banner.png",
        "images": [],
        "type": "mobile",
        "category": "Mobile Application",
        "technologies": ["React Native", "Laravel"],
        "live_url": None,
        "demo_url": None,
        "github_url": None,
    },
    {
        "slug": "teranga-palace",
        "title": "Teranga Palace",
        "description": (
            "Site web vitrine pour l'hôtel Teranga Palace avec informations sur les chambres "
            "et réservation en ligne."
        ),
        "main_image": "teranga/terangaBanner.png",
        "images": [
            "teranga/1.png",
            "teranga/2.png",
            "teranga/3.png",
        ],
        "type": "web",
        "category": "Web Development",
        "technologies": ["TailwindCSS", "React", "Vercel"],
        "live_url": "https://dakar-dreams.vercel.app/",
        "demo_url": None,
        "github_url": None,
    },
]

TESTIMONIALS: list[dict] = [
    {
        "name": "Marie Dubois",
        "role": "CEO",
        "company": "TechStart Inc.",
        "image": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
        "rating": 5,
        "text": (
            "Travail exceptionnel ! Barry a su transformer notre vision en réalité. Son professionnalisme "
            "et sa créativité ont dépassé nos attentes. Je recommande vivement ses services."
        ),
    },
    {
        "name": "Jean Martin",
        "role": "Directeur Technique",
        "company": "Digital Solutions",
        "image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
        "rating": 5,
        "text": (
            "Un développeur talentueux et fiable. Les projets sont toujours livrés dans les temps avec "
            "un code de qualité. Collaboration excellente et communication claire."
        ),
    },
    {
        "name": "Sophie Laurent",
        "role": "Product Manager",
        "company": "InnovateLab",
        "image": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150",
        "rating": 5,
        "text": (
            "Barry comprend rapidement les besoins et propose des solutions innovantes. Son expertise "
            "technique et son approche méthodique font de lui un partenaire idéal."
        ),
    },
    {
        "name": "Pierre Moreau",
        "role": "Fondateur",
        "company": "StartupXYZ",
        "image": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
        "rating": 5,
        "text": (
            "Excellent développeur full-stack. Il a su créer une application robuste et scalable. "
            "Très satisfait du résultat final et de l'accompagnement tout au long du projet."
        ),
    },
]

SOCIAL_LINKS: list[dict] = [
    {
        "label": "GitHub",
        "url": "https://github.com",
        "icon": "github",
    },
    {
        "label": "LinkedIn",
        "url": "https://www.linkedin.com/in/alhassane-barry-71116728b",
        "icon": "linkedin",
    },
    {
        "label": "Twitter / X",
        "url": "https://twitter.com",
        "icon": "twitter",
    },
]
