import os
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# Path to the XML file
xml_file = '/home/dioned-campos/projetos/Arquivo-herenio/hereniocombr.WordPress.2026-03-25.xml'
output_dir = '/home/dioned-campos/projetos/Arquivo-herenio/'
posts_dir = os.path.join(output_dir, 'posts')

if not os.path.exists(posts_dir):
    os.makedirs(posts_dir)

# Register namespaces
namespaces = {
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/',
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wfw': 'http://wellformedweb.org/CommentAPI/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'wp': 'http://wordpress.org/export/1.2/'
}

for prefix, uri in namespaces.items():
    ET.register_namespace(prefix, uri)

def parse_date(date_str):
    try:
        # Wed, 14 Aug 2013 01:33:28 +0000
        dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S +0000')
        return dt.strftime('%d/%m/%Y')
    except:
        return date_str

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def generate_post_html(title, date, content, slug):
    template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Arquivo Herênio</title>
    <link rel="stylesheet" href="../styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
</head>
<body>
    <header class="main-header">
        <div class="container">
            <div class="header-top">
                <a href="../index.html" class="back-link">← Voltar ao Arquivo</a>
                <img src="../professor.png" class="profile-avatar sm" alt="Professor Herênio">
            </div>
            <h1>{title}</h1>
            <div class="post-meta">Publicado em {date}</div>
        </div>
    </header>
    <main class="post-content">
        <div class="container">
            <article>
                {content}
            </article>
        </div>
    </main>
    <footer class="main-footer">
        <div class="container">
            <p>&copy; 2026 Arquivo Herênio - Todos os direitos reservados.</p>
        </div>
    </footer>
</body>
</html>
"""
    file_path = os.path.join(posts_dir, f"{slug}.html")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(template)
    return f"posts/{slug}.html"

def convert_videos_to_embeds(content):
    if not content:
        return ""
    
    # YouTube patterns
    # https://www.youtube.com/watch?v=...
    content = re.sub(
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)(?:[^\s<>"]*)',
        r'<div class="video-container"><iframe src="https://www.youtube.com/embed/\1" frameborder="0" allowfullscreen></iframe></div>',
        content
    )
    
    # Vimeo patterns
    # https://vimeo.com/...
    content = re.sub(
        r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)(?:[^\s<>"]*)',
        r'<div class="video-container"><iframe src="https://player.vimeo.com/video/\1" frameborder="0" allowfullscreen></iframe></div>',
        content
    )
    
    return content

def clean_html(content):
    if not content:
        return ""
    
    # Clean up redundant tags and WordPress artifacts
    content = content.replace('<!--more-->', '')
    content = content.replace('<div>', '').replace('</div>', '')
    
    # Handle line breaks - WordPress often lacks p tags and uses newlines
    if '<p' not in content:
        content = '<p>' + content.replace('\n\n', '</p><p>').replace('\n', '<br>') + '</p>'
    
    # Process video links
    content = convert_videos_to_embeds(content)
    
    # Fix redundant p tags around lists and video containers
    content = re.sub(r'<p>\s*<ul>', '<ul>', content)
    content = re.sub(r'</ul>\s*<p>', '</ul>', content)
    content = re.sub(r'<p>\s*<li>', '<li>', content)
    content = re.sub(r'</li>\s*<p>', '</li>', content)
    content = re.sub(r'<p>\s*<div class="video-container">', '<div class="video-container">', content)
    content = re.sub(r'</div>\s*</p>', '</div>', content)
    content = re.sub(r'<p>\s*</p>', '', content)
    
    return content.strip()

def main():
    tree = ET.parse(xml_file)
    root = tree.getroot()
    channel = root.find('channel')
    if channel is None:
        print("Error: Could not find channel in XML.")
        return
    
    posts = []
    
    for item in channel.findall('item'):
        post_type_el = item.find('wp:post_type', namespaces)
        status_el = item.find('wp:status', namespaces)
        
        if post_type_el is None or status_el is None:
            continue

        post_type = post_type_el.text
        status = status_el.text
        
        if post_type == 'post' and status == 'publish':
            title_el = item.find('title')
            title = title_el.text if title_el is not None else "Sem Título"
            
            pub_date_el = item.find('pubDate')
            date = parse_date(pub_date_el.text) if pub_date_el is not None else ""
            
            content_el = item.find('content:encoded', namespaces)
            content = content_el.text if content_el is not None else ""
            
            slug_el = item.find('wp:post_name', namespaces)
            slug = slug_el.text if slug_el is not None and slug_el.text else slugify(title)
            
            content = clean_html(content)
            
            relative_url = generate_post_html(title, date, content, slug)
            posts.append({
                'title': title,
                'date': date,
                'url': relative_url
            })
    
    # Sort posts by date (reverse - newest first)
    posts.sort(key=lambda x: datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)
    
    # Extract unique years for filtering
    unique_years = set()
    for post in posts:
        post_date_raw = post.get('date')
        if post_date_raw and isinstance(post_date_raw, str) and '/' in post_date_raw:
            unique_years.add(post_date_raw.split('/')[-1])
    
    years = sorted(list(unique_years), reverse=True)
    year_options = "\n".join([f'<option value="{year}">{year}</option>' for year in years])
    
    # Generate index.html
    items_html = ""
    for post in posts:
        post_title = str(post.get('title') or "Sem Título")
        post_date_str = str(post.get('date') or "")
        post_year = post_date_str.split('/')[-1] if '/' in post_date_str else ""
        
        items_html += f"""
        <a href="{post['url']}" class="post-card" data-title="{post_title.lower()}" data-year="{post_year}">
            <span class="post-date">{post_date_str}</span>
            <h3>{post_title}</h3>
        </a>
        """
    
    index_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Arquivo Herênio - Blog do Professor Herênio</title>
    <link rel="stylesheet" href="styles.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="main-header">
        <div class="container">
            <div class="branding">
                <img src="professor.png" class="profile-avatar" alt="Professor Herênio">
                <h1>Arquivo Herênio</h1>
                <p>Preservando o conhecimento e as produções acadêmicas do Professor Herênio</p>
            </div>
        </div>
    </header>
    <main class="archive-list">
        <div class="container">
            <div class="search-controls">
                <div class="search-container">
                    <input type="text" id="search-input" placeholder="Buscar por título ou palavra-chave..." aria-label="Buscar posts">
                </div>
                <div class="filter-container">
                    <select id="year-filter" aria-label="Filtrar por ano">
                        <option value="">Todos os anos</option>
                        {year_options}
                    </select>
                </div>
            </div>
            <div class="archive-header">
                <h2>Explorar Publicações</h2>
                <span id="posts-count" class="posts-count">Mostrando {len(posts)} posts</span>
            </div>
            <div class="posts-grid" id="posts-grid">
                {items_html}
            </div>
            <div id="no-results" class="no-results" style="display: none;">
                Nenhum post encontrado para os critérios selecionados.
            </div>
        </div>
    </main>
    <footer class="main-footer">
        <div class="container">
            <p>&copy; 2026 Arquivo Herênio - Preservação Digital</p>
        </div>
    </footer>
    <script src="search.js"></script>
</body>
</html>
"""
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_template)
    
    print(f"Successfully generated index.html and {len(posts)} post pages.")

if __name__ == "__main__":
    main()
