"""
Controlled skill taxonomy for resume and JD analysis.
Organized by category for structured extraction and matching.
"""

SKILL_TAXONOMY = {
    # ── Programming Languages ─────────────────────────────────
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
        "r", "matlab", "perl", "haskell", "lua", "dart", "objective-c",
        "shell", "bash", "powershell", "groovy", "elixir", "clojure",
        "assembly", "fortran", "cobol", "visual basic", "vb.net",
    ],

    # ── Web Frontend ──────────────────────────────────────────
    "web_frontend": [
        "html", "html5", "css", "css3", "sass", "scss", "less",
        "react", "react.js", "reactjs", "next.js", "nextjs",
        "angular", "angularjs", "vue", "vue.js", "vuejs", "nuxt", "nuxt.js",
        "svelte", "sveltekit", "gatsby", "remix",
        "tailwind", "tailwindcss", "tailwind css", "bootstrap", "material ui",
        "mui", "chakra ui", "ant design", "styled-components",
        "webpack", "vite", "parcel", "rollup", "esbuild",
        "jquery", "redux", "mobx", "zustand", "recoil", "pinia",
        "three.js", "d3.js", "chart.js", "recharts",
    ],

    # ── Web Backend ───────────────────────────────────────────
    "web_backend": [
        "node.js", "nodejs", "express", "express.js", "nestjs", "nest.js",
        "fastapi", "flask", "django", "tornado", "aiohttp",
        "spring", "spring boot", "spring mvc", "hibernate",
        "asp.net", ".net", ".net core", "entity framework",
        "ruby on rails", "rails", "sinatra",
        "laravel", "symfony", "codeigniter",
        "gin", "fiber", "echo",
        "graphql", "rest", "restful", "grpc", "soap", "websocket",
    ],

    # ── Databases ─────────────────────────────────────────────
    "databases": [
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mariadb",
        "oracle", "microsoft sql server", "mssql", "sql server",
        "mongodb", "dynamodb", "cassandra", "couchdb", "couchbase",
        "redis", "memcached", "elasticsearch",
        "neo4j", "arangodb", "firebase", "firestore",
        "supabase", "prisma", "sequelize", "sqlalchemy", "typeorm",
        "mongoose", "knex", "drizzle",
    ],

    # ── Cloud & DevOps ────────────────────────────────────────
    "cloud_devops": [
        "aws", "amazon web services", "ec2", "s3", "lambda", "rds",
        "cloudformation", "cloudwatch", "sqs", "sns", "ecs", "eks",
        "azure", "microsoft azure", "azure devops",
        "gcp", "google cloud", "google cloud platform", "bigquery",
        "docker", "kubernetes", "k8s", "helm", "istio",
        "terraform", "ansible", "puppet", "chef", "vagrant",
        "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
        "ci/cd", "continuous integration", "continuous deployment",
        "nginx", "apache", "caddy", "traefik",
        "linux", "ubuntu", "centos", "debian", "red hat",
        "heroku", "vercel", "netlify", "render", "railway",
        "digitalocean", "linode",
    ],

    # ── Data Science & ML ─────────────────────────────────────
    "data_science_ml": [
        "machine learning", "deep learning", "artificial intelligence", "ai",
        "neural networks", "cnn", "rnn", "lstm", "transformer",
        "nlp", "natural language processing", "computer vision",
        "tensorflow", "keras", "pytorch", "scikit-learn", "sklearn",
        "xgboost", "lightgbm", "catboost", "random forest",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "jupyter", "jupyter notebook", "colab",
        "opencv", "spacy", "nltk", "hugging face", "huggingface",
        "bert", "gpt", "llm", "large language model",
        "data mining", "feature engineering", "model training",
        "regression", "classification", "clustering",
        "reinforcement learning", "generative ai", "rag",
        "langchain", "llamaindex", "vector database",
        "mlflow", "wandb", "kubeflow",
    ],

    # ── Data Engineering ──────────────────────────────────────
    "data_engineering": [
        "etl", "data pipeline", "data warehouse", "data lake",
        "apache spark", "spark", "pyspark", "hadoop", "hive",
        "kafka", "apache kafka", "airflow", "apache airflow",
        "dbt", "snowflake", "databricks", "redshift",
        "data modeling", "data governance",
    ],

    # ── Mobile Development ────────────────────────────────────
    "mobile_development": [
        "android", "ios", "react native", "flutter",
        "swift", "swiftui", "objective-c", "kotlin",
        "xamarin", "ionic", "cordova", "capacitor",
        "mobile development", "responsive design",
    ],

    # ── Testing & QA ──────────────────────────────────────────
    "testing_qa": [
        "unit testing", "integration testing", "e2e testing",
        "jest", "mocha", "chai", "jasmine", "cypress", "playwright",
        "selenium", "puppeteer", "pytest", "unittest",
        "jmeter", "postman", "swagger",
        "tdd", "bdd", "test driven development",
        "qa", "quality assurance", "manual testing", "automation testing",
    ],

    # ── Tools & Practices ────────────────────────────────────
    "tools_practices": [
        "git", "github", "gitlab", "bitbucket", "svn",
        "jira", "confluence", "trello", "asana", "notion",
        "agile", "scrum", "kanban", "waterfall",
        "figma", "sketch", "adobe xd", "invision",
        "vs code", "visual studio", "intellij", "eclipse",
        "microservices", "monolith", "serverless",
        "design patterns", "solid", "clean architecture",
        "api design", "system design", "architecture",
    ],

    # ── Security ──────────────────────────────────────────────
    "security": [
        "cybersecurity", "information security", "network security",
        "penetration testing", "ethical hacking", "owasp",
        "encryption", "ssl", "tls", "https",
        "oauth", "oauth2", "jwt", "saml", "sso",
        "firewall", "vpn", "ids", "ips",
        "soc", "siem", "vulnerability assessment",
    ],

    # ── Soft Skills ───────────────────────────────────────────
    "soft_skills": [
        "leadership", "communication", "teamwork", "collaboration",
        "problem solving", "critical thinking", "analytical",
        "project management", "time management", "organizational",
        "presentation", "public speaking", "mentoring",
        "adaptability", "creativity", "innovation",
        "attention to detail", "self-motivated", "proactive",
    ],
}

# Flatten all skills into a single set for fast lookup
ALL_SKILLS = set()
for category_skills in SKILL_TAXONOMY.values():
    ALL_SKILLS.update(category_skills)

# Build a reverse mapping: skill -> category
SKILL_TO_CATEGORY = {}
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        SKILL_TO_CATEGORY[skill] = category


def get_skill_category(skill: str) -> str:
    """Return the category for a given skill, or 'other' if not found."""
    return SKILL_TO_CATEGORY.get(skill.lower().strip(), "other")


def find_matching_skills(text: str) -> list:
    """
    Find all taxonomy skills mentioned in a text.
    Uses lowercased matching to handle case variations.
    Returns a list of (skill, category) tuples.
    """
    text_lower = text.lower()
    found = []
    # Sort by length descending so longer multi-word skills match first
    sorted_skills = sorted(ALL_SKILLS, key=len, reverse=True)
    matched_positions = set()

    for skill in sorted_skills:
        # Check for word-boundary-like matching
        idx = text_lower.find(skill)
        while idx != -1:
            end_idx = idx + len(skill)
            # Ensure we're not matching a substring of a larger word
            before_ok = (idx == 0) or not text_lower[idx - 1].isalnum()
            after_ok = (end_idx == len(text_lower)) or not text_lower[end_idx].isalnum()

            if before_ok and after_ok:
                # Check if this position range overlaps with an already-matched skill
                position_range = set(range(idx, end_idx))
                if not position_range & matched_positions:
                    found.append((skill, get_skill_category(skill)))
                    matched_positions.update(position_range)
                    break  # Only match each skill once

            idx = text_lower.find(skill, idx + 1)

    return found
